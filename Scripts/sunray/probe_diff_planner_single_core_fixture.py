#!/usr/bin/env python3
"""Exercise the Diff-Planner single-vehicle ROS interface without a simulator."""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from pathlib import Path

import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from quadrotor_msgs.msg import PositionCommand
from sensor_msgs import point_cloud2
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Empty
from traj_utils.msg import PolyTraj


class SingleCoreFixture:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.heartbeat_count = 0
        self.trajectory_count = 0
        self.position_cmd_count = 0
        self.odom_publications = 0
        self.cloud_publications = 0
        self.last_trajectory_id: int | None = None
        self.last_position_cmd_z: float | None = None
        self.odom_publisher = rospy.Publisher(args.odom_topic, Odometry, queue_size=10)
        self.cloud_publisher = rospy.Publisher(args.cloud_topic, PointCloud2, queue_size=10)
        self.goal_publisher = rospy.Publisher(args.goal_topic, PoseStamped, queue_size=3)
        rospy.Subscriber(args.heartbeat_topic, Empty, self.on_heartbeat, queue_size=50)
        rospy.Subscriber(args.trajectory_topic, PolyTraj, self.on_trajectory, queue_size=10)
        rospy.Subscriber(args.position_cmd_topic, PositionCommand, self.on_position_cmd, queue_size=50)

    def on_heartbeat(self, _message: Empty) -> None:
        self.heartbeat_count += 1

    def on_trajectory(self, message: PolyTraj) -> None:
        self.trajectory_count += 1
        self.last_trajectory_id = int(message.traj_id)

    def on_position_cmd(self, message: PositionCommand) -> None:
        self.position_cmd_count += 1
        self.last_position_cmd_z = float(message.position.z)

    def publish_inputs(self) -> None:
        now = rospy.Time.now()
        odom = Odometry()
        odom.header.stamp = now
        odom.header.frame_id = self.args.frame_id
        odom.child_frame_id = "base_link"
        odom.pose.pose.position.z = self.args.odom_z
        odom.pose.pose.orientation.w = 1.0
        self.odom_publisher.publish(odom)
        self.odom_publications += 1

        cloud_header = odom.header
        cloud = point_cloud2.create_cloud_xyz32(
            cloud_header, [(self.args.fixture_cloud_x, self.args.fixture_cloud_y, self.args.odom_z)]
        )
        self.cloud_publisher.publish(cloud)
        self.cloud_publications += 1

    def publish_goal(self) -> None:
        goal = PoseStamped()
        goal.header.stamp = rospy.Time.now()
        goal.header.frame_id = self.args.frame_id
        goal.pose.position.x = self.args.goal_x
        goal.pose.position.y = self.args.goal_y
        goal.pose.position.z = self.args.goal_z
        goal.pose.orientation.w = 1.0
        self.goal_publisher.publish(goal)

    def wait_for_connections(self, deadline: float) -> bool:
        while not rospy.is_shutdown() and time.monotonic() < deadline:
            self.publish_inputs()
            if (
                self.odom_publisher.get_num_connections() >= 1
                and self.cloud_publisher.get_num_connections() >= 1
                and self.goal_publisher.get_num_connections() >= 1
            ):
                return True
            rospy.sleep(0.05)
        return False

    def run(self) -> dict[str, object]:
        deadline = time.monotonic() + self.args.timeout_s
        inputs_connected = self.wait_for_connections(deadline)
        for _ in range(self.args.goal_publish_repeats):
            self.publish_inputs()
            self.publish_goal()
            rospy.sleep(self.args.goal_publish_period_s)

        while not rospy.is_shutdown() and time.monotonic() < deadline:
            self.publish_inputs()
            if self.heartbeat_count > 0 and self.trajectory_count > 0 and self.position_cmd_count > 0:
                break
            rospy.sleep(0.05)

        blockers: list[str] = []
        if not inputs_connected:
            blockers.append("planner_input_subscribers_not_connected")
        if self.heartbeat_count == 0:
            blockers.append("planner_heartbeat_missing")
        if self.trajectory_count == 0:
            blockers.append("planner_trajectory_missing")
        if self.position_cmd_count == 0:
            blockers.append("traj_server_position_cmd_missing")
        return {
            "schema": "mosim.sunray_ros1.diff_planner_single_core_fixture.v1",
            "status": "passed" if not blockers else "blocked",
            "ros_master_uri": os.environ.get("ROS_MASTER_URI", ""),
            "inputs": {
                "odom_topic": self.args.odom_topic,
                "cloud_topic": self.args.cloud_topic,
                "goal_topic": self.args.goal_topic,
                "fixture_cloud_xyz_m": [self.args.fixture_cloud_x, self.args.fixture_cloud_y, self.args.odom_z],
                "goal_xyz_m": [self.args.goal_x, self.args.goal_y, self.args.goal_z],
            },
            "outputs": {
                "heartbeat_topic": self.args.heartbeat_topic,
                "trajectory_topic": self.args.trajectory_topic,
                "position_cmd_topic": self.args.position_cmd_topic,
                "heartbeat_count": self.heartbeat_count,
                "trajectory_count": self.trajectory_count,
                "position_cmd_count": self.position_cmd_count,
                "last_trajectory_id": self.last_trajectory_id,
                "last_position_cmd_z_m": self.last_position_cmd_z,
            },
            "fixture_publications": {
                "odom": self.odom_publications,
                "cloud": self.cloud_publications,
                "goal_repeats": self.args.goal_publish_repeats,
            },
            "blockers": blockers,
            "claim_boundary": (
                "This fixture proves only the source-local single Diff-Planner ROS interface: "
                "odom and nonempty PointCloud2 input, manual target acceptance, trajectory publication, "
                "and traj_server position-command publication. It does not prove FAST-LIO, MID360, "
                "occupancy quality, obstacle avoidance, px4ctrl, vehicle dynamics, or flight."
            ),
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--frame-id", default="world")
    parser.add_argument("--odom-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--cloud-topic", default="/uav1/livox_world")
    parser.add_argument("--goal-topic", default="/goal_with_id")
    parser.add_argument("--heartbeat-topic", default="/drone_0_traj_server/heartbeat")
    parser.add_argument("--trajectory-topic", default="/drone_0_planning/trajectory")
    parser.add_argument("--position-cmd-topic", default="/position_cmd")
    parser.add_argument("--odom-z", type=float, default=1.0)
    parser.add_argument("--fixture-cloud-x", type=float, default=0.0)
    parser.add_argument("--fixture-cloud-y", type=float, default=4.0)
    parser.add_argument("--goal-x", type=float, default=2.0)
    parser.add_argument("--goal-y", type=float, default=0.0)
    parser.add_argument("--goal-z", type=float, default=1.0)
    parser.add_argument("--timeout-s", type=float, default=20.0)
    parser.add_argument("--goal-publish-repeats", type=int, default=3)
    parser.add_argument("--goal-publish-period-s", type=float, default=0.20)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not math.isfinite(args.odom_z) or not math.isfinite(args.goal_z):
        raise SystemExit("odom and goal heights must be finite")
    rospy.init_node("mosim_diff_planner_single_core_fixture", anonymous=True)
    fixture = SingleCoreFixture(args)
    report = fixture.run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
