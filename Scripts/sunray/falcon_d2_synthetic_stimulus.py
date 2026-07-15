#!/usr/bin/env python3
"""Synthetic dry-run for the MoSim -> FALCON topic bridge."""

from __future__ import annotations

import argparse
import json
import math
import time
from typing import Dict, List, Tuple

import rospy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from sensor_msgs import point_cloud2
from sensor_msgs.msg import PointCloud2


Point = Tuple[float, float, float]


class Counter:
    def __init__(self) -> None:
        self.count = 0
        self.last_stamp = 0.0

    def observe(self, stamp: rospy.Time) -> None:
        self.count += 1
        self.last_stamp = stamp.to_sec() if stamp else 0.0


def make_cloud_points() -> List[Point]:
    points: List[Point] = []
    for angle_deg in range(0, 360, 10):
        angle = math.radians(angle_deg)
        for radius in (1.5, 2.5, 3.5):
            points.append((radius * math.cos(angle), radius * math.sin(angle), 0.0))
    for z_i in range(0, 24):
        z = 0.2 + z_i * 0.08
        for angle_deg in range(0, 360, 20):
            angle = math.radians(angle_deg)
            points.append((3.0 + 0.3 * math.cos(angle), 0.8 + 0.3 * math.sin(angle), z))
    return points


class FalconD2SyntheticStimulus:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.start_wall = time.time()
        self.points = make_cloud_points()
        self.odom_pub = rospy.Publisher(args.odom_in, Odometry, queue_size=10)
        self.cloud_pub = rospy.Publisher(args.cloud_in, PointCloud2, queue_size=10)
        self.outputs: Dict[str, Counter] = {
            args.odom_out: Counter(),
            args.sensor_pose_out: Counter(),
            args.cloud_out: Counter(),
        }
        rospy.Subscriber(args.odom_out, Odometry, self._odom_cb, queue_size=20)
        rospy.Subscriber(args.sensor_pose_out, TransformStamped, self._sensor_pose_cb, queue_size=50)
        rospy.Subscriber(args.cloud_out, PointCloud2, self._cloud_cb, queue_size=10)
        self.input_counts = {"odom": 0, "cloud": 0}

    def _odom_cb(self, msg: Odometry) -> None:
        self.outputs[self.args.odom_out].observe(msg.header.stamp)

    def _sensor_pose_cb(self, msg: TransformStamped) -> None:
        self.outputs[self.args.sensor_pose_out].observe(msg.header.stamp)

    def _cloud_cb(self, msg: PointCloud2) -> None:
        self.outputs[self.args.cloud_out].observe(msg.header.stamp)

    def _odom_msg(self, stamp: rospy.Time, elapsed: float) -> Odometry:
        msg = Odometry()
        msg.header.stamp = stamp
        msg.header.frame_id = "world"
        msg.child_frame_id = "uav1/base_link"
        msg.pose.pose.position.x = -10.575025 + 0.2 * elapsed
        msg.pose.pose.position.y = -19.36313
        msg.pose.pose.position.z = 1.2
        msg.pose.pose.orientation.w = 1.0
        return msg

    def _cloud_msg(self, stamp: rospy.Time) -> PointCloud2:
        header = rospy.Header()
        header.stamp = stamp
        header.frame_id = "mid360"
        return point_cloud2.create_cloud_xyz32(header, self.points)

    def run(self) -> int:
        rate = rospy.Rate(self.args.rate_hz)
        deadline = time.time() + self.args.duration_s
        while not rospy.is_shutdown() and time.time() < deadline:
            stamp = rospy.Time.now()
            elapsed = time.time() - self.start_wall
            self.odom_pub.publish(self._odom_msg(stamp, elapsed))
            self.cloud_pub.publish(self._cloud_msg(stamp))
            self.input_counts["odom"] += 1
            self.input_counts["cloud"] += 1
            rate.sleep()

        rospy.sleep(0.5)
        payload = {
            "schema": "mosim.falcon_d2_synthetic_stimulus.v1",
            "status": "passed" if self._passed() else "failed",
            "duration_s": self.args.duration_s,
            "input_counts": self.input_counts,
            "output_counts": {
                topic: {"count": counter.count, "last_stamp": counter.last_stamp}
                for topic, counter in self.outputs.items()
            },
            "claim_boundary": "Adapter dry-run only; not Gazebo/PX4/MAVROS/RViz or exploration success evidence.",
        }
        with open(self.args.summary_json, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(json.dumps(payload, ensure_ascii=False))
        return 0 if payload["status"] == "passed" else 1

    def _passed(self) -> bool:
        return all(counter.count > 0 for counter in self.outputs.values())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--odom-in", default="/mosim/falcon/odom_in")
    parser.add_argument("--cloud-in", default="/mosim/falcon/cloud_in")
    parser.add_argument("--odom-out", default="/odom_world")
    parser.add_argument("--sensor-pose-out", default="/transformer/sensor_pose_topic")
    parser.add_argument("--cloud-out", default="/voxel_mapping/pointcloud")
    parser.add_argument("--duration-s", type=float, default=5.0)
    parser.add_argument("--rate-hz", type=float, default=10.0)
    parser.add_argument("--summary-json", required=True)
    return parser.parse_args(rospy.myargv()[1:])


def main() -> None:
    args = parse_args()
    rospy.init_node("falcon_d2_synthetic_stimulus", anonymous=False)
    raise SystemExit(FalconD2SyntheticStimulus(args).run())


if __name__ == "__main__":
    main()
