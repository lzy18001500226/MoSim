#!/usr/bin/env python3
"""Bridge MoSim ROS1 odom/cloud topics into FALCON input topics.

This node is intentionally small: it republishes vehicle odometry to
``/odom_world``, derives the FALCON sensor-pose TransformStamped from odometry,
and forwards a LiDAR point cloud to ``/voxel_mapping/pointcloud``.
"""

from __future__ import annotations

import argparse
import json
import time

import rospy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import PointCloud2


class FalconMosimTopicBridge:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.start_wall = time.time()
        self.counts = {"odom_in": 0, "cloud_in": 0, "odom_out": 0, "sensor_pose_out": 0, "cloud_out": 0}
        self.last_stamp = {}

        self.odom_pub = rospy.Publisher(args.odom_out, Odometry, queue_size=20)
        self.sensor_pose_pub = rospy.Publisher(args.sensor_pose_out, TransformStamped, queue_size=100)
        self.cloud_pub = rospy.Publisher(args.cloud_out, PointCloud2, queue_size=5)

        rospy.Subscriber(args.odom_in, Odometry, self._odom_cb, queue_size=50)
        rospy.Subscriber(args.cloud_in, PointCloud2, self._cloud_cb, queue_size=5)

    def _record(self, key: str, stamp: rospy.Time) -> None:
        self.counts[key] += 1
        self.last_stamp[key] = stamp.to_sec() if stamp else 0.0

    def _stamp(self, source_stamp: rospy.Time) -> rospy.Time:
        if self.args.restamp in {"now", "ros_now", "wall_now"}:
            return rospy.Time.now()
        return source_stamp

    def _odom_cb(self, msg: Odometry) -> None:
        self._record("odom_in", msg.header.stamp)
        out = Odometry()
        out.header = msg.header
        out.header.stamp = self._stamp(msg.header.stamp)
        out.header.frame_id = self.args.world_frame
        out.child_frame_id = msg.child_frame_id or self.args.body_frame
        out.pose = msg.pose
        out.twist = msg.twist
        self.odom_pub.publish(out)
        self._record("odom_out", out.header.stamp)

        tf_msg = TransformStamped()
        tf_msg.header.stamp = out.header.stamp
        tf_msg.header.frame_id = self.args.world_frame
        tf_msg.child_frame_id = self.args.sensor_frame
        tf_msg.transform.translation.x = msg.pose.pose.position.x + self.args.sensor_offset_x
        tf_msg.transform.translation.y = msg.pose.pose.position.y + self.args.sensor_offset_y
        tf_msg.transform.translation.z = msg.pose.pose.position.z + self.args.sensor_offset_z
        tf_msg.transform.rotation = msg.pose.pose.orientation
        self.sensor_pose_pub.publish(tf_msg)
        self._record("sensor_pose_out", tf_msg.header.stamp)

    def _cloud_cb(self, msg: PointCloud2) -> None:
        self._record("cloud_in", msg.header.stamp)
        out = PointCloud2()
        out.header = msg.header
        out.header.stamp = self._stamp(msg.header.stamp)
        out.height = msg.height
        out.width = msg.width
        out.fields = msg.fields
        out.is_bigendian = msg.is_bigendian
        out.point_step = msg.point_step
        out.row_step = msg.row_step
        out.data = msg.data
        out.is_dense = msg.is_dense
        self.cloud_pub.publish(out)
        self._record("cloud_out", out.header.stamp)

    def spin(self) -> None:
        rate = rospy.Rate(self.args.status_hz)
        try:
            while not rospy.is_shutdown():
                rate.sleep()
        except rospy.exceptions.ROSInterruptException:
            pass
        if self.args.summary_json:
            payload = {
                "schema": "mosim.falcon_topic_bridge_summary.v1",
                "duration_wall_s": round(time.time() - self.start_wall, 3),
                "counts": self.counts,
                "last_stamp": self.last_stamp,
                "topics": {
                    "odom_in": self.args.odom_in,
                    "cloud_in": self.args.cloud_in,
                    "odom_out": self.args.odom_out,
                    "sensor_pose_out": self.args.sensor_pose_out,
                    "cloud_out": self.args.cloud_out,
                    "restamp": self.args.restamp,
                },
            }
            with open(self.args.summary_json, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--odom-in", default="/mosim/falcon/odom_in")
    parser.add_argument("--cloud-in", default="/mosim/falcon/cloud_in")
    parser.add_argument("--odom-out", default="/odom_world")
    parser.add_argument("--sensor-pose-out", default="/transformer/sensor_pose_topic")
    parser.add_argument("--cloud-out", default="/voxel_mapping/pointcloud")
    parser.add_argument("--world-frame", default="world")
    parser.add_argument("--body-frame", default="base_link")
    parser.add_argument("--sensor-frame", default="mid360")
    parser.add_argument("--sensor-offset-x", type=float, default=0.0)
    parser.add_argument("--sensor-offset-y", type=float, default=0.0)
    parser.add_argument("--sensor-offset-z", type=float, default=0.0)
    parser.add_argument("--restamp", choices=["input", "now", "ros_now", "wall_now"], default="input")
    parser.add_argument("--status-hz", type=float, default=1.0)
    parser.add_argument("--summary-json", default="")
    return parser.parse_args(rospy.myargv()[1:])


def main() -> None:
    args = parse_args()
    rospy.init_node("falcon_mosim_topic_bridge", anonymous=False)
    FalconMosimTopicBridge(args).spin()


if __name__ == "__main__":
    main()
