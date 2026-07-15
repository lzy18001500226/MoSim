#!/usr/bin/env python3
"""Publish PoseStamped from Odometry while preserving the source header."""

from __future__ import annotations

import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry


class OdomToPoseStamped:
    def __init__(self) -> None:
        input_topic = rospy.get_param("~input_topic", "/uav1/sunray/gazebo_pose")
        output_topic = rospy.get_param("~output_topic", "/mosim/fuel/cloud_source_pose")
        self.offset_x = float(rospy.get_param("~offset_x", 0.0))
        self.offset_y = float(rospy.get_param("~offset_y", 0.0))
        self.offset_z = float(rospy.get_param("~offset_z", 0.0))
        self.publisher = rospy.Publisher(output_topic, PoseStamped, queue_size=50)
        rospy.Subscriber(input_topic, Odometry, self.on_odom, queue_size=50)

    def on_odom(self, msg: Odometry) -> None:
        out = PoseStamped()
        out.header = msg.header
        out.pose = msg.pose.pose
        out.pose.position.x -= self.offset_x
        out.pose.position.y -= self.offset_y
        out.pose.position.z -= self.offset_z
        self.publisher.publish(out)


def main() -> None:
    rospy.init_node("mosim_odom_to_pose_stamped", anonymous=False)
    OdomToPoseStamped()
    rospy.spin()


if __name__ == "__main__":
    main()
