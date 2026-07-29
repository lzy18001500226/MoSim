#!/usr/bin/env python3
"""Publish a persistent review cloud from the real Sunray MID360 scan topic.

This node is display-only. It subscribes to the real Gazebo/Sunray
``/uav1/livox/lidar`` PointCloud2 and Gazebo truth odometry, transforms a
bounded sample of points into the map frame, and republishes a latched
accumulated cloud for RViz review.
"""

from __future__ import annotations

import argparse
import math
import struct
import time
from pathlib import Path

import rospy
from nav_msgs.msg import Odometry
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header


class PointcloudReviewNode:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.result_dir = Path(args.result_dir)
        self.result_dir.mkdir(parents=True, exist_ok=True)
        self.pose = None
        self.cloud_count = 0
        self.last_publish_t = -1.0
        self.points: list[tuple[float, float, float, int]] = []
        self.pub = rospy.Publisher(args.output_topic, PointCloud2, queue_size=1, latch=True)
        rospy.Subscriber(args.odom_topic, Odometry, self.on_odom, queue_size=20)
        rospy.Subscriber(args.input_topic, PointCloud2, self.on_cloud, queue_size=2)

    @staticmethod
    def yaw_from_quat(x: float, y: float, z: float, w: float) -> float:
        return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))

    def on_odom(self, msg: Odometry) -> None:
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        self.pose = (
            float(p.x),
            float(p.y),
            float(p.z),
            self.yaw_from_quat(float(q.x), float(q.y), float(q.z), float(q.w)),
        )

    def on_cloud(self, msg: PointCloud2) -> None:
        self.cloud_count += 1
        if self.pose is None or msg.point_step < 12 or not msg.data:
            return
        x0, y0, z0, yaw = self.pose
        cy = math.cos(yaw)
        sy = math.sin(yaw)
        data = msg.data
        point_count = min(msg.width * max(1, msg.height), len(data) // msg.point_step)
        stride = max(1, int(self.args.sample_stride))
        added = 0
        for idx in range(0, point_count, stride):
            if added >= self.args.max_points_per_cloud:
                break
            offset = idx * msg.point_step
            try:
                lx, ly, lz = struct.unpack_from("<fff", data, offset)
            except struct.error:
                break
            if not (math.isfinite(lx) and math.isfinite(ly) and math.isfinite(lz)):
                continue
            if lx * lx + ly * ly + lz * lz < self.args.min_range_m * self.args.min_range_m:
                continue
            wx = x0 + cy * lx - sy * ly
            wy = y0 + sy * lx + cy * ly
            wz = z0 + lz
            color = self.color_from_z(wz)
            self.points.append((wx, wy, wz, color))
            added += 1
        if len(self.points) > self.args.max_accumulated_points:
            self.points = self.points[-self.args.max_accumulated_points :]
        now = time.time()
        if now - self.last_publish_t >= 1.0 / max(0.1, self.args.publish_rate_hz):
            self.publish()
            self.last_publish_t = now

    @staticmethod
    def color_from_z(z: float) -> int:
        # Packed RGB: low points blue/green, high points red/yellow.
        t = max(0.0, min(1.0, (z + 0.2) / 2.2))
        r = int(40 + 215 * t)
        g = int(80 + 120 * (1.0 - abs(2.0 * t - 1.0)))
        b = int(230 * (1.0 - t))
        return (r << 16) | (g << 8) | b

    def publish(self) -> None:
        if not self.points:
            return
        msg = PointCloud2()
        msg.header = Header(frame_id=self.args.frame_id, stamp=rospy.Time.now())
        msg.height = 1
        msg.width = len(self.points)
        msg.fields = [
            PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name="rgb", offset=12, datatype=PointField.UINT32, count=1),
        ]
        msg.is_bigendian = False
        msg.point_step = 16
        msg.row_step = msg.point_step * msg.width
        msg.is_dense = False
        msg.data = b"".join(struct.pack("<fffI", *point) for point in self.points)
        self.pub.publish(msg)

    def spin(self) -> None:
        rospy.spin()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--node-name", default="mosim_px4ctrl_pointcloud_review")
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--input-topic", default="/uav1/livox/lidar")
    parser.add_argument("--odom-topic", default="/uav1/sunray/gazebo_pose")
    parser.add_argument("--output-topic", default="/mosim/sunray/lidar_points_map_accumulated")
    parser.add_argument("--frame-id", default="map")
    parser.add_argument("--sample-stride", type=int, default=8)
    parser.add_argument("--max-points-per-cloud", type=int, default=2500)
    parser.add_argument("--max-accumulated-points", type=int, default=120000)
    parser.add_argument("--publish-rate-hz", type=float, default=2.0)
    parser.add_argument("--min-range-m", type=float, default=0.35)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rospy.init_node(args.node_name, anonymous=False)
    PointcloudReviewNode(args).spin()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
