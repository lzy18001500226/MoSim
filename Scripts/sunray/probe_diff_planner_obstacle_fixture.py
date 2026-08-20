#!/usr/bin/env python3
"""Exercise Diff Planner against a deterministic world-frame obstacle wall."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from sensor_msgs import point_cloud2
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Empty, Header
from traj_utils.msg import PolyTraj


class ObstacleFixture:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.heartbeats = 0
        self.trajectories: list[dict[str, object]] = []
        self.odom_pub = rospy.Publisher(args.odom_topic, Odometry, queue_size=10)
        self.cloud_pub = rospy.Publisher(args.cloud_topic, PointCloud2, queue_size=2)
        self.goal_pub = rospy.Publisher(args.goal_topic, PoseStamped, queue_size=2)
        rospy.Subscriber(args.heartbeat_topic, Empty, self._heartbeat, queue_size=50)
        rospy.Subscriber(args.trajectory_topic, PolyTraj, self._trajectory, queue_size=20)

    def _heartbeat(self, _msg: Empty) -> None:
        self.heartbeats += 1

    def _trajectory(self, msg: PolyTraj) -> None:
        if msg.order != 5 or not msg.duration:
            return
        piece_count = len(msg.duration)
        expected = piece_count * (msg.order + 1)
        if len(msg.coef_x) != expected or len(msg.coef_y) != expected or len(msg.coef_z) != expected:
            return
        samples: list[tuple[float, float, float]] = []
        for piece, duration in enumerate(msg.duration):
            if duration <= 0.0:
                continue
            offset = piece * 6
            for sample in range(self.args.samples_per_piece + 1):
                t = float(duration) * sample / self.args.samples_per_piece
                samples.append(
                    (
                        self._evaluate(msg.coef_x[offset : offset + 6], t),
                        self._evaluate(msg.coef_y[offset : offset + 6], t),
                        self._evaluate(msg.coef_z[offset : offset + 6], t),
                    )
                )
        violations = [point for point in samples if self._inside_inflated_box(point)]
        max_abs_y_detour = max((abs(point[1]) for point in samples), default=0.0)
        self.trajectories.append(
            {
                "traj_id": int(msg.traj_id),
                "duration_s": float(sum(msg.duration)),
                "sample_count": len(samples),
                "collision_sample_count": len(violations),
                "min_abs_y_to_detour": min((abs(point[1]) for point in samples), default=math.inf),
                "max_abs_y_detour": max_abs_y_detour,
                "start_xyz": list(samples[0]) if samples else None,
                "end_xyz": list(samples[-1]) if samples else None,
                "coefficients_head": {
                    "x": [float(value) for value in msg.coef_x[:6]],
                    "y": [float(value) for value in msg.coef_y[:6]],
                    "z": [float(value) for value in msg.coef_z[:6]],
                },
                "durations": [float(value) for value in msg.duration],
            }
        )

    @staticmethod
    def _evaluate(coefficients: list[float], t: float) -> float:
        value = 0.0
        # PolyTraj stores c0..c5, while the native evaluator applies c5 first.
        for coefficient in coefficients:
            value = value * t + float(coefficient)
        return value

    def _inside_inflated_box(self, point: tuple[float, float, float]) -> bool:
        x, y, z = point
        return (
            self.args.obstacle_min_x - self.args.inflation <= x <= self.args.obstacle_max_x + self.args.inflation
            and self.args.obstacle_min_y - self.args.inflation <= y <= self.args.obstacle_max_y + self.args.inflation
            and self.args.obstacle_min_z - self.args.inflation <= z <= self.args.obstacle_max_z + self.args.inflation
        )

    def _publish_odom(self, stamp: rospy.Time) -> None:
        msg = Odometry()
        msg.header.stamp = stamp
        msg.header.frame_id = self.args.frame_id
        msg.child_frame_id = "base_link"
        msg.pose.pose.orientation.w = 1.0
        msg.pose.pose.position.z = self.args.odom_z
        self.odom_pub.publish(msg)

    def _wall_points(self) -> list[tuple[float, float, float]]:
        points = []
        for ix in range(self.args.wall_x_samples):
            x = self.args.obstacle_min_x + (self.args.obstacle_max_x - self.args.obstacle_min_x) * ix / max(1, self.args.wall_x_samples - 1)
            for iy in range(self.args.wall_y_samples):
                y = self.args.obstacle_min_y + (self.args.obstacle_max_y - self.args.obstacle_min_y) * iy / max(1, self.args.wall_y_samples - 1)
                for iz in range(self.args.wall_z_samples):
                    z = self.args.obstacle_min_z + (self.args.obstacle_max_z - self.args.obstacle_min_z) * iz / max(1, self.args.wall_z_samples - 1)
                    points.append((x, y, z))
        return points

    def _publish_cloud(self, stamp: rospy.Time, points: list[tuple[float, float, float]]) -> None:
        self.cloud_pub.publish(point_cloud2.create_cloud_xyz32(Header(stamp=stamp, frame_id=self.args.frame_id), points))

    def _publish_goal(self) -> None:
        msg = PoseStamped()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.args.frame_id
        msg.pose.position.x = self.args.goal_x
        msg.pose.position.y = self.args.goal_y
        msg.pose.position.z = self.args.goal_z
        msg.pose.orientation.w = 1.0
        self.goal_pub.publish(msg)

    def run(self) -> dict[str, object]:
        wall = self._wall_points()
        deadline = time.monotonic() + self.args.timeout_s
        while not rospy.is_shutdown() and time.monotonic() < deadline and (
            self.odom_pub.get_num_connections() < 1
            or self.cloud_pub.get_num_connections() < 1
        ):
            stamp = rospy.Time.now()
            self._publish_odom(stamp)
            self._publish_cloud(stamp, wall)
            rospy.sleep(0.05)
        warmup_deadline = time.monotonic() + self.args.warmup_s
        while not rospy.is_shutdown() and time.monotonic() < warmup_deadline:
            stamp = rospy.Time.now()
            self._publish_odom(stamp)
            self._publish_cloud(stamp, wall)
            rospy.sleep(0.05)
        for _ in range(self.args.goal_repeats):
            goal_deadline = time.monotonic() + 2.0
            while not rospy.is_shutdown() and time.monotonic() < goal_deadline and self.goal_pub.get_num_connections() < 1:
                rospy.sleep(0.05)
            self._publish_goal()
            rospy.sleep(0.2)
        while not rospy.is_shutdown() and time.monotonic() < deadline:
            stamp = rospy.Time.now()
            self._publish_odom(stamp)
            self._publish_cloud(stamp, wall)
            if self.trajectories and self.heartbeats > 0:
                break
            rospy.sleep(0.05)

        latest = self.trajectories[-1] if self.trajectories else None
        blockers: list[str] = []
        if self.cloud_pub.get_num_connections() < 1:
            blockers.append("planner_cloud_subscriber_not_connected")
        if self.heartbeats == 0:
            blockers.append("planner_heartbeat_missing")
        if latest is None:
            blockers.append("planner_trajectory_missing")
        elif int(latest["collision_sample_count"]) > 0:
            blockers.append("planned_trajectory_enters_inflated_obstacle")
        elif float(latest["max_abs_y_detour"]) <= max(
            abs(self.args.obstacle_min_y), abs(self.args.obstacle_max_y)
        ) + self.args.inflation:
            blockers.append("planned_trajectory_does_not_detour_around_obstacle")
        elif latest["start_xyz"] is None or math.dist(latest["start_xyz"], (0.0, 0.0, self.args.odom_z)) > 0.5:
            blockers.append("planned_trajectory_start_does_not_match_odom")
        elif latest["end_xyz"] is None or math.dist(latest["end_xyz"], (self.args.goal_x, self.args.goal_y, self.args.goal_z)) > 0.5:
            blockers.append("planned_trajectory_end_does_not_match_goal")
        return {
            "schema": "mosim.sunray_ros1.diff_planner_obstacle_fixture.v1",
            "status": "passed" if not blockers else "blocked",
            "obstacle_box_xyz_m": {
                "min": [self.args.obstacle_min_x, self.args.obstacle_min_y, self.args.obstacle_min_z],
                "max": [self.args.obstacle_max_x, self.args.obstacle_max_y, self.args.obstacle_max_z],
                "inflation_m": self.args.inflation,
            },
            "goal_xyz_m": [self.args.goal_x, self.args.goal_y, self.args.goal_z],
            "heartbeat_count": self.heartbeats,
            "trajectory_count": len(self.trajectories),
            "latest_trajectory": latest,
            "blockers": blockers,
            "claim_boundary": "This fixture proves only that the source-local Diff Planner PolyTraj avoids the deterministic world-frame inflated obstacle in a frozen-input ROS interface. It does not prove point-cloud fidelity, localization, px4ctrl, vehicle dynamics, or flight.",
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
    parser.add_argument("--odom-z", type=float, default=1.0)
    parser.add_argument("--goal-x", type=float, default=2.0)
    parser.add_argument("--goal-y", type=float, default=0.0)
    parser.add_argument("--goal-z", type=float, default=1.0)
    parser.add_argument("--obstacle-min-x", type=float, default=0.8)
    parser.add_argument("--obstacle-max-x", type=float, default=1.2)
    parser.add_argument("--obstacle-min-y", type=float, default=-0.9)
    parser.add_argument("--obstacle-max-y", type=float, default=0.9)
    parser.add_argument("--obstacle-min-z", type=float, default=0.5)
    parser.add_argument("--obstacle-max-z", type=float, default=1.5)
    parser.add_argument("--inflation", type=float, default=0.2)
    parser.add_argument("--wall-x-samples", type=int, default=4)
    parser.add_argument("--wall-y-samples", type=int, default=17)
    parser.add_argument("--wall-z-samples", type=int, default=9)
    parser.add_argument("--samples-per-piece", type=int, default=80)
    parser.add_argument("--warmup-s", type=float, default=2.0)
    parser.add_argument("--goal-repeats", type=int, default=1)
    parser.add_argument("--timeout-s", type=float, default=20.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rospy.init_node("mosim_diff_planner_obstacle_fixture", anonymous=True)
    fixture = ObstacleFixture(args)
    report = fixture.run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
