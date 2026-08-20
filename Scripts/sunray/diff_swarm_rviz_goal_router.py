#!/usr/bin/env python3
"""Route RViz manual formation waypoints to the Diff-Planner swarm.

RViz selects a formation center in the reviewed common-world frame. The router
expands each center into fixed per-UAV targets, publishes one PoseStamped to
each planner input, and holds later clicks until every UAV reaches the active
batch. It is a planning-input adapter only: it does not publish PX4/MAVROS
commands, perform collision-aware replanning, or replace planner occupancy
checks.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
import time
from pathlib import Path

import rospy
from geometry_msgs.msg import Pose, PoseArray, PoseStamped
from nav_msgs.msg import Odometry, Path as RosPath
from std_msgs.msg import Bool, String

# The launcher executes this file by absolute path from a WSL shell. Python
# then puts Scripts/sunray, rather than the project root, on sys.path.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Scripts.sunray.diff_swarm_goal_geometry import (
    default_formation_offsets,
    minimum_pairwise_distance,
    parse_vector_list,
    route_center_goal,
)


SCHEMA = "mosim.rviz_diff_swarm_goal_router.v2"


def normalize_frame(value: object) -> str:
    return str(value or "").strip().lstrip("/")


class DiffSwarmRvizGoalRouter:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.uav_ids = tuple(range(1, args.uav_num + 1))
        self.formation_offsets = (
            parse_vector_list(args.formation_offsets, expected_count=args.uav_num, field="formation_offsets")
            if args.formation_offsets
            else default_formation_offsets(args.uav_num)
        )
        self.world_to_local_offsets = (
            parse_vector_list(
                args.world_to_local_offsets,
                expected_count=args.uav_num,
                field="world_to_local_offsets",
            )
            if args.world_to_local_offsets
            else tuple((0.0, 0.0, 0.0) for _ in self.uav_ids)
        )
        self.input_frame = normalize_frame(args.input_frame)
        self.output_frame = normalize_frame(args.output_frame)
        if not self.input_frame or not self.output_frame:
            raise ValueError("input and output frames are required")
        if args.min_target_separation_m < 0.0 or not math.isfinite(args.min_target_separation_m):
            raise ValueError("min_target_separation_m must be finite and nonnegative")

        self.ready = False
        self.pending_centers: list[tuple[float, float, float]] = []
        self.active_batch: dict | None = None
        self.progress_odom: dict[int, Odometry | None] = {uid: None for uid in self.uav_ids}
        self.progress_stable_since_wall: float | None = None
        self.goal_count = 0
        self.forwarded_batch_count = 0
        self.completed_waypoint_count = 0
        self.rejected_goal_count = 0
        self.last_status = "starting"
        self.last_rejection: str | None = None
        self.last_batch: dict | None = None
        self.last_progress_snapshot: dict | None = None
        self.diagnostics_path = Path(args.diagnostics_path) if args.diagnostics_path else None

        self.output_pubs = {
            uid: rospy.Publisher(
                args.goal_topic_template.format(uid=uid, drone_id=uid - 1),
                PoseStamped,
                queue_size=5,
                latch=False,
            )
            for uid in self.uav_ids
        }
        self.target_preview_pub = rospy.Publisher(args.target_preview_topic, PoseArray, queue_size=1, latch=False)
        self.route_preview_pub = rospy.Publisher(args.route_preview_topic, RosPath, queue_size=1, latch=False)
        self.status_pub = rospy.Publisher(args.status_topic, String, queue_size=5, latch=False)
        self.ready_sub = rospy.Subscriber(args.mission_ready_topic, Bool, self.on_mission_ready, queue_size=5)
        self.goal_sub = rospy.Subscriber(args.goal_input_topic, PoseStamped, self.on_rviz_goal, queue_size=10)
        self.progress_subs = {
            uid: rospy.Subscriber(
                args.progress_odom_topic_template.format(uid=uid, drone_id=uid - 1),
                Odometry,
                self.on_progress_odom,
                callback_args=uid,
                queue_size=20,
            )
            for uid in self.uav_ids
            if args.progress_odom_topic_template
        }
        self.timer = rospy.Timer(rospy.Duration(0.1), self.on_timer)
        self.publish_status("waiting_for_mission_ready")
        self.write_diagnostics()

    def on_mission_ready(self, msg: Bool) -> None:
        self.ready = bool(msg.data)
        self.last_status = "mission_ready" if self.ready else "waiting_for_mission_ready"
        self.publish_status(self.last_status)
        self.try_dispatch()

    def on_rviz_goal(self, msg: PoseStamped) -> None:
        self.goal_count += 1
        frame = normalize_frame(msg.header.frame_id) or self.input_frame
        center = (float(msg.pose.position.x), float(msg.pose.position.y), float(self.args.target_z))
        if frame != self.input_frame:
            self.reject(f"goal_frame_mismatch:{frame}:{self.input_frame}")
            return
        if not all(math.isfinite(value) for value in center):
            self.reject("goal_not_finite")
            return
        try:
            world_targets = route_center_goal(center, self.formation_offsets)
            if minimum_pairwise_distance(world_targets) < self.args.min_target_separation_m - 1.0e-9:
                self.reject("formation_target_separation_below_gate")
                return
        except ValueError as exc:
            self.reject(str(exc))
            return
        if len(self.pending_centers) + (1 if self.active_batch is not None else 0) >= self.args.max_waypoints:
            self.reject("waypoint_queue_full")
            return
        self.pending_centers.append(center)
        self.progress_stable_since_wall = None
        self.last_status = "waypoint_queued_until_current_batch_reaches"
        self.last_rejection = None
        self.publish_status(self.last_status)
        self.publish_route_preview()
        self.write_diagnostics()
        self.try_dispatch()

    def on_progress_odom(self, msg: Odometry, uid: int) -> None:
        self.progress_odom[int(uid)] = msg
        self.try_dispatch()

    def on_timer(self, _event: object) -> None:
        self.try_dispatch()

    def try_dispatch(self) -> None:
        if self.active_batch is not None:
            if not self.active_batch_reached():
                return
            self.completed_waypoint_count += 1
            self.active_batch = None
            self.progress_stable_since_wall = None
            self.last_status = "current_waypoint_reached"
            self.publish_status(self.last_status)
            self.publish_route_preview()
        if not self.pending_centers:
            self.write_diagnostics()
            return
        if not self.ready:
            self.last_status = "waiting_for_mission_ready"
            self.publish_status(self.last_status)
            return
        missing = [
            str(uid)
            for uid, pub in self.output_pubs.items()
            if pub.get_num_connections() < self.args.min_subscribers
        ]
        if missing:
            self.last_status = "waiting_for_uav_goal_subscribers:" + ",".join(missing)
            self.publish_status(self.last_status)
            self.write_diagnostics()
            return

        center = self.pending_centers.pop(0)
        try:
            local_targets = route_center_goal(
                center,
                self.formation_offsets,
                world_to_local_offsets=self.world_to_local_offsets,
            )
        except ValueError as exc:
            self.reject(str(exc))
            return

        stamp = rospy.Time.now()
        batch_id = f"{self.args.run_id or 'ros'}-{self.forwarded_batch_count + 1:04d}"
        for uid, target in zip(self.uav_ids, local_targets):
            msg = PoseStamped()
            msg.header.stamp = stamp
            msg.header.frame_id = self.output_frame
            msg.pose.position.x, msg.pose.position.y, msg.pose.position.z = target
            msg.pose.orientation.w = 1.0
            self.output_pubs[uid].publish(msg)

        display_targets = route_center_goal(center, self.formation_offsets)
        preview = PoseArray()
        preview.header.stamp = stamp
        preview.header.frame_id = self.input_frame
        for target in display_targets:
            pose = Pose()
            pose.position.x, pose.position.y, pose.position.z = target
            pose.orientation.w = 1.0
            preview.poses.append(pose)
        self.target_preview_pub.publish(preview)

        self.forwarded_batch_count += 1
        self.active_batch = {
            "batch_id": batch_id,
            "waypoint_index": self.completed_waypoint_count + 1,
            "center_world": list(center),
            "planner_targets": [list(target) for target in local_targets],
            "display_targets": [list(target) for target in display_targets],
            "dispatched_wall": time.time(),
            "reached_wall": None,
        }
        self.last_batch = dict(self.active_batch)
        self.last_status = "forwarded_goal_batch"
        self.last_rejection = None
        self.publish_status(self.last_status)
        self.publish_route_preview()
        self.write_diagnostics()

    def progress_position_world(self, uid: int) -> tuple[float, float, float] | None:
        msg = self.progress_odom.get(uid)
        if msg is None:
            return None
        p = msg.pose.pose.position
        values = [float(p.x), float(p.y), float(p.z)]
        if not all(math.isfinite(value) for value in values):
            return None
        if self.args.progress_odom_frame == "local":
            offset = self.world_to_local_offsets[uid - 1]
            values = [values[index] + offset[index] for index in range(3)]
        return tuple(values)  # type: ignore[return-value]

    def active_batch_reached(self) -> bool:
        if self.active_batch is None or not self.args.auto_advance:
            return False
        targets = self.active_batch.get("display_targets") or []
        positions: dict[str, dict] = {}
        blockers: list[str] = []
        now_wall = time.time()
        now_ros = rospy.Time.now().to_sec()
        for uid, target in zip(self.uav_ids, targets):
            msg = self.progress_odom.get(uid)
            if msg is None:
                blockers.append(f"uav{uid}:odom_missing")
                continue
            stamp = msg.header.stamp.to_sec()
            if stamp > 0.0 and now_ros > 0.0 and now_ros - stamp > self.args.progress_odom_timeout_s:
                blockers.append(f"uav{uid}:odom_stale")
                continue
            position = self.progress_position_world(uid)
            if position is None:
                blockers.append(f"uav{uid}:odom_invalid")
                continue
            distance_xy = math.hypot(position[0] - float(target[0]), position[1] - float(target[1]))
            distance_z = abs(position[2] - float(target[2]))
            reached = (
                distance_xy <= self.args.waypoint_reach_radius_m
                and distance_z <= self.args.waypoint_reach_z_tolerance_m
            )
            positions[str(uid)] = {
                "position_world": list(position),
                "distance_xy_m": distance_xy,
                "distance_z_m": distance_z,
                "reached": reached,
            }
            if not reached:
                blockers.append(f"uav{uid}:outside_reach_gate")

        self.last_progress_snapshot = {
            "status": "reached_candidate" if not blockers else "waiting",
            "active_batch_id": self.active_batch.get("batch_id"),
            "positions": positions,
            "blockers": blockers,
            "reach_radius_m": self.args.waypoint_reach_radius_m,
            "reach_z_tolerance_m": self.args.waypoint_reach_z_tolerance_m,
            "required_stable_s": self.args.waypoint_reach_stable_s,
        }
        if blockers:
            self.progress_stable_since_wall = None
            self.last_status = "waiting_for_waypoint_reach"
            self.publish_status(self.last_status)
            return False
        if self.progress_stable_since_wall is None:
            self.progress_stable_since_wall = now_wall
            self.last_status = "waypoint_reached_stabilizing"
            self.publish_status(self.last_status)
            return False
        stable_s = now_wall - self.progress_stable_since_wall
        self.last_progress_snapshot["stable_duration_s"] = stable_s
        if stable_s < self.args.waypoint_reach_stable_s:
            return False
        self.active_batch["reached_wall"] = now_wall
        return True

    def publish_route_preview(self) -> None:
        path = RosPath()
        path.header.stamp = rospy.Time.now()
        path.header.frame_id = self.input_frame
        centers: list[tuple[float, float, float]] = []
        if self.active_batch is not None:
            center = self.active_batch.get("center_world")
            if isinstance(center, list) and len(center) == 3:
                centers.append(tuple(float(value) for value in center))
        centers.extend(self.pending_centers)
        for center in centers:
            pose = PoseStamped()
            pose.header = path.header
            pose.pose.position.x, pose.pose.position.y, pose.pose.position.z = center
            pose.pose.orientation.w = 1.0
            path.poses.append(pose)
        self.route_preview_pub.publish(path)

    def reject(self, reason: str) -> None:
        self.rejected_goal_count += 1
        self.last_rejection = reason
        self.last_status = "rejected:" + reason
        self.publish_status(self.last_status)
        self.write_diagnostics()
        rospy.logwarn("Diff-Swarm RViz goal rejected: %s", reason)

    def publish_status(self, value: str) -> None:
        self.status_pub.publish(String(data=value))

    def write_diagnostics(self) -> None:
        if self.diagnostics_path is None:
            return
        payload = {
            "schema": SCHEMA,
            "run_id": self.args.run_id,
            "status": self.last_status,
            "goal_input_topic": self.args.goal_input_topic,
            "goal_topic_template": self.args.goal_topic_template,
            "mission_ready_topic": self.args.mission_ready_topic,
            "target_preview_topic": self.args.target_preview_topic,
            "route_preview_topic": self.args.route_preview_topic,
            "status_topic": self.args.status_topic,
            "input_frame": self.input_frame,
            "output_frame": self.output_frame,
            "uav_num": self.args.uav_num,
            "formation_offsets": [list(item) for item in self.formation_offsets],
            "world_to_local_offsets": [list(item) for item in self.world_to_local_offsets],
            "min_target_separation_m": self.args.min_target_separation_m,
            "mission_ready": self.ready,
            "goal_count": self.goal_count,
            "forwarded_batch_count": self.forwarded_batch_count,
            "completed_waypoint_count": self.completed_waypoint_count,
            "rejected_goal_count": self.rejected_goal_count,
            "pending_centers_world": [list(center) for center in self.pending_centers],
            "active_batch": self.active_batch,
            "progress_odom_topic_template": self.args.progress_odom_topic_template,
            "progress_odom_frame": self.args.progress_odom_frame,
            "progress_odom_timeout_s": self.args.progress_odom_timeout_s,
            "last_progress_snapshot": self.last_progress_snapshot,
            "last_rejection": self.last_rejection,
            "last_batch": self.last_batch,
            "claim_boundary": (
                "RViz input routing, per-UAV fixed-offset expansion, and waypoint queueing only. "
                "This does not prove planner acceptance, collision-aware swarm planning, "
                "controller success, flight, or closed-loop acceptance."
            ),
        }
        self.diagnostics_path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=self.diagnostics_path.name + ".", dir=self.diagnostics_path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=True, indent=2)
                handle.write("\n")
            os.replace(temp_name, self.diagnostics_path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--uav-num", type=int, choices=(2, 3), default=3)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--goal-input-topic", default="/move_base_simple/goal")
    parser.add_argument("--goal-topic-template", default="/uav{uid}/goal_with_id")
    parser.add_argument("--mission-ready-topic", default="/mosim/diff_swarm/interactive_goal_ready")
    parser.add_argument("--target-preview-topic", default="/mosim/diff_swarm/manual_targets")
    parser.add_argument("--route-preview-topic", default="/mosim/diff_swarm/manual_waypoint_path")
    parser.add_argument("--status-topic", default="/mosim/diff_swarm/manual_goal_status")
    parser.add_argument("--input-frame", default="world")
    parser.add_argument("--output-frame", default="local")
    parser.add_argument("--target-z", type=float, default=1.0)
    parser.add_argument("--formation-offsets", default="")
    parser.add_argument("--world-to-local-offsets", default="")
    parser.add_argument("--min-target-separation-m", type=float, default=0.80)
    parser.add_argument("--min-subscribers", type=int, default=1)
    parser.add_argument("--max-waypoints", type=int, default=32)
    parser.add_argument("--auto-advance", dest="auto_advance", action="store_true", default=True)
    parser.add_argument("--no-auto-advance", dest="auto_advance", action="store_false")
    parser.add_argument("--progress-odom-topic-template", default="/uav{uid}/mavros/local_position/odom")
    parser.add_argument("--progress-odom-frame", choices=("local", "world"), default="local")
    parser.add_argument("--progress-odom-timeout-s", type=float, default=1.0)
    parser.add_argument("--waypoint-reach-radius-m", type=float, default=0.40)
    parser.add_argument("--waypoint-reach-z-tolerance-m", type=float, default=0.20)
    parser.add_argument("--waypoint-reach-stable-s", type=float, default=0.80)
    parser.add_argument("--diagnostics-path", default="")
    args = parser.parse_args()
    if args.target_z <= 0.0 or not math.isfinite(args.target_z):
        parser.error("target-z must be finite and positive")
    if args.min_subscribers < 1 or args.max_waypoints < 1:
        parser.error("min-subscribers and max-waypoints must be positive")
    for name in (
        "progress_odom_timeout_s",
        "waypoint_reach_radius_m",
        "waypoint_reach_z_tolerance_m",
        "waypoint_reach_stable_s",
    ):
        value = getattr(args, name)
        if value < 0.0 or not math.isfinite(value):
            parser.error(f"{name.replace('_', '-')} must be finite and nonnegative")
    return args


def main() -> int:
    args = parse_args()
    rospy.init_node("mosim_diff_swarm_rviz_goal_router", anonymous=False)
    DiffSwarmRvizGoalRouter(args)
    rospy.spin()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
