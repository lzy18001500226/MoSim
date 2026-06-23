#!/usr/bin/env python3
"""Bridge MAVROS local pose and velocity topics into nav_msgs/Odometry.

Fast-Drone-250 px4ctrl consumes a single Odometry topic. The current Sunray
ROS1 lane exposes MAVROS local pose and local velocity as separate topics.
This node only repackages those measured states; it does not implement or
replace any controller.
"""

from __future__ import annotations

import argparse

import rospy
from geometry_msgs.msg import PoseStamped, TwistStamped
from nav_msgs.msg import Odometry


class PoseVelocityToOdomBridge:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.last_pose: PoseStamped | None = None
        self.last_velocity: TwistStamped | None = None
        self.last_published_stamp = rospy.Time(0)
        self.pub = rospy.Publisher(args.output_topic, Odometry, queue_size=20)
        rospy.Subscriber(args.pose_topic, PoseStamped, self.on_pose, queue_size=50)
        rospy.Subscriber(args.velocity_topic, TwistStamped, self.on_velocity, queue_size=50)

    def on_pose(self, msg: PoseStamped) -> None:
        self.last_pose = msg
        self.publish_if_ready()

    def on_velocity(self, msg: TwistStamped) -> None:
        self.last_velocity = msg
        self.publish_if_ready()

    def publish_if_ready(self) -> None:
        if rospy.is_shutdown():
            return
        if self.last_pose is None or self.last_velocity is None:
            return
        msg = Odometry()
        msg.header = self.last_pose.header
        stamps = [
            stamp
            for stamp in (self.last_pose.header.stamp, self.last_velocity.header.stamp)
            if stamp.to_sec() > 0
        ]
        msg.header.stamp = max(stamps) if stamps else rospy.Time.now()
        if msg.header.stamp <= self.last_published_stamp:
            return
        self.last_published_stamp = msg.header.stamp
        if not msg.header.frame_id:
            msg.header.frame_id = self.args.frame_id
        msg.child_frame_id = self.args.child_frame_id
        msg.pose.pose = self.last_pose.pose
        msg.twist.twist = self.last_velocity.twist
        try:
            self.pub.publish(msg)
        except rospy.ROSException:
            if not rospy.is_shutdown():
                raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pose-topic", default="/uav1/mavros/local_position/pose")
    parser.add_argument("--velocity-topic", default="/uav1/mavros/local_position/velocity_local")
    parser.add_argument("--output-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--frame-id", default="map")
    parser.add_argument("--child-frame-id", default="uav1/base_link")
    return parser.parse_args()


def main() -> int:
    rospy.init_node("mosim_mavros_pose_velocity_to_odom_bridge", anonymous=True)
    PoseVelocityToOdomBridge(parse_args())
    rospy.spin()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
