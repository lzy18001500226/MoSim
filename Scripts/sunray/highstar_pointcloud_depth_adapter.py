#!/usr/bin/env python3
"""Project a MoSim PointCloud2 stream into a HighStar-style depth image.

This is an adapter for bounded HighStar dry-runs. It does not replace the
robotics evidence path and it does not publish control commands.
"""

import array
import math
from typing import Iterable, Tuple

import rospy
import sensor_msgs.point_cloud2 as pc2
from sensor_msgs.msg import CameraInfo, Image, PointCloud2


class HighStarDepthAdapter:
    def __init__(self) -> None:
        self.cloud_topic = rospy.get_param("~cloud_topic", "/uav1/livox/lidar")
        self.depth_topic = rospy.get_param("~depth_topic", "/mosim/highstar/depth")
        self.camera_info_topic = rospy.get_param("~camera_info_topic", "/mosim/highstar/camera_info")
        self.frame_id = rospy.get_param("~frame_id", "uav1_livox_depth")
        self.axes_mode = rospy.get_param("~axes_mode", "lidar_x_forward")
        self.width = int(rospy.get_param("~width", 160))
        self.height = int(rospy.get_param("~height", 90))
        self.hfov_rad = float(rospy.get_param("~hfov_rad", 1.9))
        self.vfov_rad = float(rospy.get_param("~vfov_rad", 1.046))
        self.min_range_m = float(rospy.get_param("~min_range_m", 0.2))
        self.max_range_m = float(rospy.get_param("~max_range_m", 8.0))
        self.point_stride = max(1, int(rospy.get_param("~point_stride", 1)))
        self.min_points_to_publish = int(rospy.get_param("~min_points_to_publish", 20))
        self.info_hz = float(rospy.get_param("~camera_info_hz", 5.0))

        self.fx = (self.width * 0.5) / math.tan(self.hfov_rad * 0.5)
        self.fy = (self.height * 0.5) / math.tan(self.vfov_rad * 0.5)
        self.cx = (self.width - 1) * 0.5
        self.cy = (self.height - 1) * 0.5
        self.last_info = CameraInfo()

        self.depth_pub = rospy.Publisher(self.depth_topic, Image, queue_size=3)
        self.info_pub = rospy.Publisher(self.camera_info_topic, CameraInfo, queue_size=3, latch=True)
        self.sub = rospy.Subscriber(self.cloud_topic, PointCloud2, self.on_cloud, queue_size=1, buff_size=8 * 1024 * 1024)
        self.info_timer = rospy.Timer(rospy.Duration(1.0 / max(0.1, self.info_hz)), self.on_info_timer)

        rospy.loginfo(
            "HighStar depth adapter: %s -> %s, camera_info=%s, size=%dx%d, fov=(%.3f, %.3f), axes=%s",
            self.cloud_topic,
            self.depth_topic,
            self.camera_info_topic,
            self.width,
            self.height,
            self.hfov_rad,
            self.vfov_rad,
            self.axes_mode,
        )

    def convert_axes(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        if self.axes_mode == "camera":
            return x, y, z
        if self.axes_mode == "lidar_x_forward":
            return -y, -z, x
        if self.axes_mode == "lidar_y_forward":
            return x, -z, y
        raise ValueError(f"unsupported axes_mode={self.axes_mode}")

    def make_camera_info(self, stamp: rospy.Time) -> CameraInfo:
        msg = CameraInfo()
        msg.header.stamp = stamp
        msg.header.frame_id = self.frame_id
        msg.width = self.width
        msg.height = self.height
        msg.distortion_model = "plumb_bob"
        msg.D = [0.0, 0.0, 0.0, 0.0, 0.0]
        msg.K = [
            self.fx, 0.0, self.cx,
            0.0, self.fy, self.cy,
            0.0, 0.0, 1.0,
        ]
        msg.R = [
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
        ]
        msg.P = [
            self.fx, 0.0, self.cx, 0.0,
            0.0, self.fy, self.cy, 0.0,
            0.0, 0.0, 1.0, 0.0,
        ]
        return msg

    def iter_points(self, msg: PointCloud2) -> Iterable[Tuple[float, float, float]]:
        index = 0
        for point in pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True):
            if index % self.point_stride == 0:
                yield float(point[0]), float(point[1]), float(point[2])
            index += 1

    def on_cloud(self, msg: PointCloud2) -> None:
        depth_mm = array.array("H", [0]) * (self.width * self.height)
        projected = 0
        used = 0
        max_depth_mm = int(self.max_range_m * 1000.0)

        for raw_x, raw_y, raw_z in self.iter_points(msg):
            x, y, z = self.convert_axes(raw_x, raw_y, raw_z)
            if z < self.min_range_m or z > self.max_range_m:
                continue
            u = int(self.fx * x / z + self.cx)
            v = int(self.fy * y / z + self.cy)
            if u < 0 or u >= self.width or v < 0 or v >= self.height:
                continue
            projected += 1
            depth = max(1, min(max_depth_mm, int(z * 1000.0)))
            idx = v * self.width + u
            if depth_mm[idx] == 0 or depth < depth_mm[idx]:
                depth_mm[idx] = depth
                used += 1

        if used < self.min_points_to_publish:
            rospy.logwarn_throttle(
                2.0,
                "HighStar depth adapter sparse frame: projected=%d used_pixels=%d threshold=%d",
                projected,
                used,
                self.min_points_to_publish,
            )
            return

        stamp = msg.header.stamp if msg.header.stamp != rospy.Time() else rospy.Time.now()
        info = self.make_camera_info(stamp)
        depth = Image()
        depth.header.stamp = stamp
        depth.header.frame_id = self.frame_id
        depth.height = self.height
        depth.width = self.width
        depth.encoding = "16UC1"
        depth.is_bigendian = 0
        depth.step = self.width * 2
        depth.data = depth_mm.tobytes()
        self.last_info = info
        self.info_pub.publish(info)
        self.depth_pub.publish(depth)
        rospy.loginfo_throttle(
            5.0,
            "HighStar depth adapter published depth: projected=%d used_pixels=%d stamp=%.3f",
            projected,
            used,
            stamp.to_sec(),
        )

    def on_info_timer(self, _event) -> None:
        if self.last_info.width == 0:
            self.last_info = self.make_camera_info(rospy.Time.now())
        self.info_pub.publish(self.last_info)


def main() -> None:
    rospy.init_node("mosim_highstar_pointcloud_depth_adapter", anonymous=False)
    HighStarDepthAdapter()
    rospy.spin()


if __name__ == "__main__":
    main()
