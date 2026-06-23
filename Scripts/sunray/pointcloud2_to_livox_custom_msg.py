#!/usr/bin/env python3
"""Bridge Sunray MID360 PointCloud2 to FAST-LIO Livox CustomMsg.

Sunray's Gazebo Classic Livox plugin publishes a dense PointCloud2 on
``/uav1/livox/lidar`` for RViz/planner review. The message has x/y/z fields but
does not declare the per-point Livox fields that FAST-LIO's Livox path expects.
This bridge keeps the original PointCloud2 topic unchanged and publishes a
FAST-LIO-only Livox CustomMsg with monotonic stamps, line ids, reflectivity, and
offset_time.
"""

from __future__ import annotations

import argparse
import math
import struct

import rospy
import sensor_msgs.point_cloud2 as pc2
from sensor_msgs.msg import Imu
from sensor_msgs.msg import PointCloud2

from livox_ros_driver.msg import CustomMsg, CustomPoint


class Bridge:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.pub = rospy.Publisher(args.output_topic, CustomMsg, queue_size=5)
        self.seq = 0
        self.last_stamp = rospy.Time(0)
        self.latest_imu_stamp = rospy.Time(0)
        self.period_ns = int(1_000_000_000.0 / max(args.scan_rate_hz, 0.1))
        rospy.Subscriber(args.input_topic, PointCloud2, self.on_cloud, queue_size=3)
        if args.imu_topic:
            rospy.Subscriber(args.imu_topic, Imu, self.on_imu, queue_size=20)

    def on_imu(self, msg: Imu) -> None:
        if msg.header.stamp.to_sec() > 0:
            self.latest_imu_stamp = msg.header.stamp

    def source_stamp(self, msg: PointCloud2) -> rospy.Time:
        if self.args.stamp_source == "imu" and self.latest_imu_stamp.to_sec() > 0:
            return self.latest_imu_stamp
        if self.args.stamp_source == "now":
            return rospy.Time.now()
        if msg.header.stamp.to_sec() > 0:
            return msg.header.stamp
        if self.latest_imu_stamp.to_sec() > 0:
            return self.latest_imu_stamp
        return rospy.Time.now()

    def monotonic_stamp(self, stamp: rospy.Time) -> rospy.Time:
        if stamp.to_sec() > 0 and self.last_stamp.to_sec() > 0 and stamp + rospy.Duration.from_sec(10.0) < self.last_stamp:
            rospy.logwarn(
                "resetting bridge timestamp base from %.6f to %.6f",
                self.last_stamp.to_sec(),
                stamp.to_sec(),
            )
            self.last_stamp = rospy.Time(0)
        if stamp <= self.last_stamp:
            stamp = self.last_stamp + rospy.Duration.from_sec(1.0 / max(self.args.scan_rate_hz, 0.1))
        self.last_stamp = stamp
        return stamp

    def on_cloud(self, msg: PointCloud2) -> None:
        if self.args.stamp_source == "imu" and self.latest_imu_stamp.to_sec() <= 0:
            rospy.logwarn_throttle(5.0, "waiting for first IMU stamp before publishing FAST-LIO Livox CustomMsg")
            return
        stamp = self.monotonic_stamp(self.source_stamp(msg))
        out = CustomMsg()
        out.header.seq = self.seq
        out.header.stamp = stamp
        out.header.frame_id = self.args.frame_id or msg.header.frame_id
        out.timebase = stamp.to_nsec()
        out.lidar_id = self.args.lidar_id

        points = []
        stride = max(self.args.stride, 1)
        kept = 0
        for idx, point in enumerate(pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)):
            if idx % stride != 0:
                continue
            x, y, z = point
            if x * x + y * y + z * z < self.args.blind * self.args.blind:
                continue
            pt = CustomPoint()
            pt.offset_time = int((kept % max(self.args.points_per_scan_hint, 1)) * self.period_ns / max(self.args.points_per_scan_hint, 1))
            pt.x = float(x)
            pt.y = float(y)
            pt.z = float(z)
            pt.reflectivity = self.args.reflectivity
            pt.tag = 0x10
            pt.line = int(self.estimate_line(float(x), float(y), float(z)))
            points.append(pt)
            kept += 1
            if self.args.max_points > 0 and kept >= self.args.max_points:
                break

        out.point_num = len(points)
        out.points = points
        self.pub.publish(out)
        self.seq += 1

    def estimate_line(self, x: float, y: float, z: float) -> int:
        horizontal = math.atan2(y, x)
        bucket = int((horizontal + math.pi) / (2.0 * math.pi) * self.args.scan_lines)
        return max(0, min(self.args.scan_lines - 1, bucket))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-topic", default="/uav1/livox/lidar")
    parser.add_argument("--output-topic", default="/mosim/fastlio/livox/lidar")
    parser.add_argument("--imu-topic", default="/uav1/livox/imu")
    parser.add_argument(
        "--stamp-source",
        choices=("imu", "cloud", "now"),
        default="imu",
        help="Timestamp source for FAST-LIO CustomMsg. Sunray's LiDAR header can be wall time while IMU is Gazebo time.",
    )
    parser.add_argument("--frame-id", default="uav1/base_link")
    parser.add_argument("--scan-rate-hz", type=float, default=10.0)
    parser.add_argument("--scan-lines", type=int, default=4)
    parser.add_argument("--blind", type=float, default=0.4)
    parser.add_argument("--stride", type=int, default=1)
    parser.add_argument("--max-points", type=int, default=0)
    parser.add_argument("--points-per-scan-hint", type=int, default=20000)
    parser.add_argument("--reflectivity", type=int, default=100)
    parser.add_argument("--lidar-id", type=int, default=1)
    args = parser.parse_args(rospy.myargv()[1:])

    rospy.init_node("mosim_pointcloud2_to_livox_custom_msg", anonymous=False)
    Bridge(args)
    rospy.loginfo(
        "bridging %s -> %s as livox_ros_driver/CustomMsg",
        args.input_topic,
        args.output_topic,
    )
    rospy.spin()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
