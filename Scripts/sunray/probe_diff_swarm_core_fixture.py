#!/usr/bin/env python3
"""Exercise the three-UAV Diff-Swarm planner ROS interface without a simulator."""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from dataclasses import dataclass
from pathlib import Path

import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from quadrotor_msgs.msg import PositionCommand
from sensor_msgs import point_cloud2
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Empty
from traj_utils.msg import MINCOTraj, PolyTraj


@dataclass(frozen=True)
class DroneFixture:
    uid: int
    drone_id: int
    start_x: float
    start_y: float
    start_z: float
    target_x: float
    target_y: float
    target_z: float
    odom_topic: str
    cloud_topic: str
    goal_topic: str
    heartbeat_topic: str
    trajectory_topic: str
    position_cmd_topic: str


class Counter:
    def __init__(self, topic: str) -> None:
        self.topic = topic
        self.count = 0
        self.last_summary: dict[str, object] = {}

    def observe(self, summary: dict[str, object] | None = None) -> None:
        self.count += 1
        if summary is not None:
            self.last_summary = summary


class DiffSwarmCoreFixture:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.drones = self._build_drones(args)
        self.odom_pubs: dict[int, rospy.Publisher] = {}
        self.cloud_pubs: dict[int, rospy.Publisher] = {}
        self.goal_pubs: dict[int, rospy.Publisher] = {}
        self.input_counts = {drone.uid: {"odom": 0, "cloud": 0, "goal": 0} for drone in self.drones}
        self.heartbeat = {drone.uid: Counter(drone.heartbeat_topic) for drone in self.drones}
        self.trajectory = {drone.uid: Counter(drone.trajectory_topic) for drone in self.drones}
        self.position_cmd = {drone.uid: Counter(drone.position_cmd_topic) for drone in self.drones}
        self.broadcast_from = Counter("/broadcast_traj_from_planner")
        self.broadcast_to = Counter("/broadcast_traj_to_planner")
        self.broadcast_relay_count = 0
        self.broadcast_pub = rospy.Publisher("/broadcast_traj_to_planner", MINCOTraj, queue_size=100)

        for drone in self.drones:
            self.odom_pubs[drone.uid] = rospy.Publisher(drone.odom_topic, Odometry, queue_size=20)
            self.cloud_pubs[drone.uid] = rospy.Publisher(drone.cloud_topic, PointCloud2, queue_size=20)
            self.goal_pubs[drone.uid] = rospy.Publisher(drone.goal_topic, PoseStamped, queue_size=3)
            rospy.Subscriber(
                drone.heartbeat_topic,
                Empty,
                lambda _msg, uid=drone.uid: self.heartbeat[uid].observe(),
                queue_size=50,
            )
            rospy.Subscriber(
                drone.trajectory_topic,
                PolyTraj,
                lambda msg, uid=drone.uid: self.trajectory[uid].observe(self._poly_summary(msg)),
                queue_size=50,
            )
            rospy.Subscriber(
                drone.position_cmd_topic,
                PositionCommand,
                lambda msg, uid=drone.uid: self.position_cmd[uid].observe(self._cmd_summary(msg)),
                queue_size=100,
            )

        rospy.Subscriber("/broadcast_traj_from_planner", MINCOTraj, self._broadcast_from_cb, queue_size=100)
        rospy.Subscriber(
            "/broadcast_traj_to_planner",
            MINCOTraj,
            lambda msg: self.broadcast_to.observe(self._minco_summary(msg)),
            queue_size=100,
        )

    @staticmethod
    def _build_drones(args: argparse.Namespace) -> list[DroneFixture]:
        starts = [
            (args.start1_x, args.start1_y, args.start_z),
            (args.start2_x, args.start2_y, args.start_z),
            (args.start3_x, args.start3_y, args.start_z),
        ]
        targets = [
            (args.target1_x, args.target1_y, args.target_z),
            (args.target2_x, args.target2_y, args.target_z),
            (args.target3_x, args.target3_y, args.target_z),
        ]
        drones = []
        for index, ((sx, sy, sz), (tx, ty, tz)) in enumerate(zip(starts, targets), start=1):
            drone_id = index - 1
            drones.append(
                DroneFixture(
                    uid=index,
                    drone_id=drone_id,
                    start_x=sx,
                    start_y=sy,
                    start_z=sz,
                    target_x=tx,
                    target_y=ty,
                    target_z=tz,
                    odom_topic=args.odom_topic_template.format(uid=index, drone_id=drone_id),
                    cloud_topic=args.cloud_topic_template.format(uid=index, drone_id=drone_id),
                    goal_topic=args.goal_topic_template.format(uid=index, drone_id=drone_id),
                    heartbeat_topic=f"/drone_{drone_id}_traj_server/heartbeat",
                    trajectory_topic=f"/drone_{drone_id}_planning/trajectory",
                    position_cmd_topic=args.position_cmd_topic_template.format(uid=index, drone_id=drone_id),
                )
            )
        return drones

    @staticmethod
    def _poly_summary(msg: PolyTraj) -> dict[str, object]:
        return {
            "drone_id": int(msg.drone_id),
            "traj_id": int(msg.traj_id),
            "order": int(msg.order),
            "duration_count": len(msg.duration),
            "duration_sum_s": float(sum(msg.duration)) if msg.duration else 0.0,
            "start_time_s": msg.start_time.to_sec(),
        }

    @staticmethod
    def _minco_summary(msg: MINCOTraj) -> dict[str, object]:
        return {
            "drone_id": int(msg.drone_id),
            "traj_id": int(msg.traj_id),
            "order": int(msg.order),
            "des_clearance_m": float(msg.des_clearance),
            "duration_count": len(msg.duration),
            "duration_sum_s": float(sum(msg.duration)) if msg.duration else 0.0,
            "start_time_s": msg.start_time.to_sec(),
            "start_p": [float(value) for value in msg.start_p],
            "end_p": [float(value) for value in msg.end_p],
        }

    @staticmethod
    def _cmd_summary(msg: PositionCommand) -> dict[str, object]:
        return {
            "trajectory_id": int(msg.trajectory_id),
            "trajectory_flag": int(msg.trajectory_flag),
            "position": [float(msg.position.x), float(msg.position.y), float(msg.position.z)],
            "velocity": [float(msg.velocity.x), float(msg.velocity.y), float(msg.velocity.z)],
            "acceleration": [float(msg.acceleration.x), float(msg.acceleration.y), float(msg.acceleration.z)],
            "yaw": float(msg.yaw),
        }

    @staticmethod
    def _clone_minco(msg: MINCOTraj) -> MINCOTraj:
        out = MINCOTraj()
        out.drone_id = msg.drone_id
        out.traj_id = msg.traj_id
        out.start_time = msg.start_time
        out.des_clearance = msg.des_clearance
        out.order = msg.order
        out.start_p = list(msg.start_p)
        out.start_v = list(msg.start_v)
        out.start_a = list(msg.start_a)
        out.end_p = list(msg.end_p)
        out.end_v = list(msg.end_v)
        out.end_a = list(msg.end_a)
        out.inner_x = list(msg.inner_x)
        out.inner_y = list(msg.inner_y)
        out.inner_z = list(msg.inner_z)
        out.duration = list(msg.duration)
        return out

    def _broadcast_from_cb(self, msg: MINCOTraj) -> None:
        self.broadcast_from.observe(self._minco_summary(msg))
        self.broadcast_pub.publish(self._clone_minco(msg))
        self.broadcast_relay_count += 1

    def _odom_msg(self, drone: DroneFixture, stamp: rospy.Time) -> Odometry:
        msg = Odometry()
        msg.header.stamp = stamp
        msg.header.frame_id = self.args.frame_id
        msg.child_frame_id = f"uav{drone.uid}/base_link"
        msg.pose.pose.position.x = drone.start_x
        msg.pose.pose.position.y = drone.start_y
        msg.pose.pose.position.z = drone.start_z
        msg.pose.pose.orientation.w = 1.0
        return msg

    def _cloud_msg(self, drone: DroneFixture, stamp: rospy.Time) -> PointCloud2:
        header = self._odom_msg(drone, stamp).header
        point = (drone.start_x, drone.start_y + self.args.fixture_cloud_offset_y, drone.start_z)
        return point_cloud2.create_cloud_xyz32(header, [point])

    def _goal_msg(self, drone: DroneFixture, stamp: rospy.Time) -> PoseStamped:
        msg = PoseStamped()
        msg.header.stamp = stamp
        msg.header.frame_id = self.args.frame_id
        msg.pose.position.x = drone.target_x
        msg.pose.position.y = drone.target_y
        msg.pose.position.z = drone.target_z
        msg.pose.orientation.w = 1.0
        return msg

    def publish_inputs(self) -> None:
        stamp = rospy.Time.now()
        for drone in self.drones:
            self.odom_pubs[drone.uid].publish(self._odom_msg(drone, stamp))
            self.cloud_pubs[drone.uid].publish(self._cloud_msg(drone, stamp))
            self.input_counts[drone.uid]["odom"] += 1
            self.input_counts[drone.uid]["cloud"] += 1

    def publish_goals(self) -> None:
        stamp = rospy.Time.now()
        for drone in self.drones:
            self.goal_pubs[drone.uid].publish(self._goal_msg(drone, stamp))
            self.input_counts[drone.uid]["goal"] += 1

    def inputs_connected(self) -> bool:
        return all(
            self.odom_pubs[drone.uid].get_num_connections() >= 1
            and self.cloud_pubs[drone.uid].get_num_connections() >= 1
            and self.goal_pubs[drone.uid].get_num_connections() >= 1
            for drone in self.drones
        )

    def outputs_ready(self) -> bool:
        return all(
            self.heartbeat[drone.uid].count > 0
            and self.trajectory[drone.uid].count > 0
            and self.position_cmd[drone.uid].count > 0
            for drone in self.drones
        )

    def run(self) -> dict[str, object]:
        deadline = time.monotonic() + self.args.timeout_s
        connected = False
        while not rospy.is_shutdown() and time.monotonic() < deadline:
            self.publish_inputs()
            if self.inputs_connected():
                connected = True
                break
            rospy.sleep(0.05)

        for _ in range(self.args.goal_publish_repeats):
            self.publish_inputs()
            self.publish_goals()
            rospy.sleep(self.args.goal_publish_period_s)

        while not rospy.is_shutdown() and time.monotonic() < deadline:
            self.publish_inputs()
            if self.outputs_ready() and self.broadcast_from.count > 0 and self.broadcast_relay_count > 0:
                break
            rospy.sleep(0.05)

        blockers: list[str] = []
        if not connected:
            blockers.append("planner_input_subscribers_not_connected")
        if self.broadcast_from.count == 0:
            blockers.append("planner_broadcast_from_missing")
        if self.broadcast_relay_count == 0:
            blockers.append("planner_broadcast_relay_missing")

        per_uav = {}
        for drone in self.drones:
            uid_key = f"uav{drone.uid}"
            if self.heartbeat[drone.uid].count == 0:
                blockers.append(f"{uid_key}_planner_heartbeat_missing")
            if self.trajectory[drone.uid].count == 0:
                blockers.append(f"{uid_key}_planner_trajectory_missing")
            if self.position_cmd[drone.uid].count == 0:
                blockers.append(f"{uid_key}_traj_server_position_cmd_missing")
            per_uav[uid_key] = {
                "drone_id": drone.drone_id,
                "start_world_xyz_m": [drone.start_x, drone.start_y, drone.start_z],
                "target_world_xyz_m": [drone.target_x, drone.target_y, drone.target_z],
                "input_topics": {
                    "odom": drone.odom_topic,
                    "cloud": drone.cloud_topic,
                    "goal": drone.goal_topic,
                },
                "output_topics": {
                    "heartbeat": drone.heartbeat_topic,
                    "trajectory": drone.trajectory_topic,
                    "position_cmd": drone.position_cmd_topic,
                },
                "input_publish_counts": self.input_counts[drone.uid],
                "heartbeat": vars(self.heartbeat[drone.uid]),
                "trajectory": vars(self.trajectory[drone.uid]),
                "position_cmd": vars(self.position_cmd[drone.uid]),
            }

        return {
            "schema": "mosim.sunray_ros1.diff_swarm_core_fixture.v1",
            "status": "passed" if not blockers else "blocked",
            "ros_master_uri": os.environ.get("ROS_MASTER_URI", ""),
            "frame_contract": {
                "planner_input_frame": self.args.frame_id,
                "planner_goal_frame": self.args.frame_id,
                "planner_position_cmd_frame": self.args.frame_id,
                "runtime_bridge_required_for_px4": (
                    "C99 runtime must bridge MAVROS-local odom, local point clouds, and mission-local "
                    "goals into this common planner frame, then bridge planner PositionCommand back to PX4 local."
                ),
            },
            "per_uav": per_uav,
            "broadcast": {
                "from_planner": vars(self.broadcast_from),
                "to_planner": vars(self.broadcast_to),
                "relay_count": self.broadcast_relay_count,
                "relay_mode": "transparent_single_ros_master_common_world",
            },
            "blockers": blockers,
            "claim_boundary": (
                "This fixture proves only the source-local three-UAV Diff-Swarm ROS interface "
                "in a common planner frame: per-UAV odom/cloud/goal input, transparent trajectory "
                "broadcast relay, trajectory publication, and traj_server PositionCommand output. "
                "It does not prove FAST-LIO, MID360, occupancy quality, obstacle avoidance, "
                "px4ctrl, vehicle dynamics, inter-UAV clearance, or flight."
            ),
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--frame-id", default="world")
    parser.add_argument("--odom-topic-template", default="/uav{uid}/mosim/diff_swarm/planner_odom_world")
    parser.add_argument(
        "--cloud-topic-template",
        default="/uav{uid}/mosim/diff_swarm/planner_cloud_world",
    )
    parser.add_argument("--goal-topic-template", default="/uav{uid}/mosim/diff_swarm/planner_goal_world")
    parser.add_argument(
        "--position-cmd-topic-template",
        default="/uav{uid}/mosim/diff_swarm/planner_position_cmd_world",
    )
    parser.add_argument("--start1-x", type=float, default=0.0)
    parser.add_argument("--start1-y", type=float, default=-1.0)
    parser.add_argument("--start2-x", type=float, default=0.0)
    parser.add_argument("--start2-y", type=float, default=1.0)
    parser.add_argument("--start3-x", type=float, default=-1.5)
    parser.add_argument("--start3-y", type=float, default=0.0)
    parser.add_argument("--start-z", type=float, default=1.0)
    parser.add_argument("--target1-x", type=float, default=2.0)
    parser.add_argument("--target1-y", type=float, default=-1.0)
    parser.add_argument("--target2-x", type=float, default=2.0)
    parser.add_argument("--target2-y", type=float, default=1.0)
    parser.add_argument("--target3-x", type=float, default=0.5)
    parser.add_argument("--target3-y", type=float, default=0.0)
    parser.add_argument("--target-z", type=float, default=1.0)
    parser.add_argument("--fixture-cloud-offset-y", type=float, default=4.0)
    parser.add_argument("--timeout-s", type=float, default=25.0)
    parser.add_argument("--goal-publish-repeats", type=int, default=3)
    parser.add_argument("--goal-publish-period-s", type=float, default=0.20)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    for value in (
        args.start1_x,
        args.start1_y,
        args.start2_x,
        args.start2_y,
        args.start3_x,
        args.start3_y,
        args.start_z,
        args.target1_x,
        args.target1_y,
        args.target2_x,
        args.target2_y,
        args.target3_x,
        args.target3_y,
        args.target_z,
    ):
        if not math.isfinite(value):
            raise SystemExit("fixture coordinates must be finite")
    rospy.init_node("mosim_diff_swarm_core_fixture", anonymous=True)
    report = DiffSwarmCoreFixture(args).run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
