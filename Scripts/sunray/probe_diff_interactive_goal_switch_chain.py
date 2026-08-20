#!/usr/bin/env python3
"""Probe Diff-Planner interactive goal switching through the RViz goal path.

This probe publishes normal RViz-style goals to /move_base_simple/goal, then
uses the actual forwarded /goal_with_id target as the acceptance target. That
keeps the audit aligned with the Goal4 click/2D-nav goal adapter: if the
adapter clamps or stages a far request, the flight is judged against the target
that was really handed to Diff-Planner, not against the raw mouse request.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import rospy
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from quadrotor_msgs.msg import PositionCommand
from rosgraph_msgs.msg import Clock
from std_msgs.msg import Bool


def parse_goals(value: str) -> list[tuple[float, float, float]]:
    goals: list[tuple[float, float, float]] = []
    for item in value.split(";"):
        item = item.strip()
        if not item:
            continue
        parts = [part.strip() for part in item.split(",")]
        if len(parts) != 3:
            raise ValueError(f"goal must be x,y,z: {item!r}")
        goals.append((float(parts[0]), float(parts[1]), float(parts[2])))
    if not goals:
        raise ValueError("no goals parsed")
    return goals


def load_goals(args: argparse.Namespace) -> list[tuple[float, float, float]]:
    if args.goals_file:
        path = Path(args.goals_file)
        packet = json.loads(path.read_text(encoding="utf-8"))
        raw_goals = packet.get("waypoints")
        if not isinstance(raw_goals, list):
            raise ValueError(f"goals file has no waypoints list: {path}")
        goals = []
        for item in raw_goals:
            if not isinstance(item, list) or len(item) < 3:
                raise ValueError(f"invalid waypoint in {path}: {item!r}")
            goals.append((float(item[0]), float(item[1]), float(item[2])))
    else:
        goals = parse_goals(args.goals)
    if not goals:
        raise ValueError("no goals loaded")
    return goals


def yaw_from_quat(x: float, y: float, z: float, w: float) -> float:
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


def rpy_from_quat(x: float, y: float, z: float, w: float) -> tuple[float, float, float]:
    roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
    pitch = math.asin(max(-1.0, min(1.0, 2.0 * (w * y - z * x))))
    return roll, pitch, yaw_from_quat(x, y, z, w)


def finite_time(value: object) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def build_goal_stage_rtf_report(report: dict, clock_topic: str) -> dict:
    """Summarize actual planner-goal to arrival timing from one live probe."""

    goals = []
    blockers = []
    for item in report.get("goals", []):
        timing = item.get("goal_stage_timing")
        if not isinstance(timing, dict):
            timing = {
                "status": "blocked",
                "reason_code": "goal_stage_timing_missing",
            }
        goal = {
            "index": item.get("index"),
            "route_index": item.get("route_index"),
            "requested": item.get("requested"),
            "accepted": item.get("accepted"),
            "reached": bool(item.get("reached")),
            "timing": timing,
        }
        goals.append(goal)
        if timing.get("status") != "measured":
            blockers.append(
                f"goal_{item.get('index', 'unknown')}:{timing.get('reason_code', 'goal_stage_timing_missing')}"
            )

    if report.get("status") != "passed":
        blockers.append("interactive_goal_probe_not_passed")
    if not goals:
        blockers.append("no_executed_goals")

    return {
        "schema": "mosim.sunray_ros1.diff_interactive_goal_stage_rtf.v1",
        "status": "passed" if not blockers else "blocked",
        "source": "live_ros1_clock_and_goal_switch_probe",
        "clock_topic": clock_topic,
        "task_boundary": {
            "start": "actual /goal_with_id forwarding to Diff-Planner",
            "end": "stable arrival-hold confirmation",
            "excludes": ["Gazebo/PX4 cold start", "post-arrival final hover", "cleanup"],
        },
        "goals": goals,
        "blockers": blockers,
        "claim_boundary": (
            "This reports only the live goal-stage sim/wall factor for the actual "
            "forwarded Diff-Planner target. It does not replace raw-cloud pacing, "
            "controller-quality, collision, or broader mission acceptance evidence."
        ),
    }


class InteractiveGoalSwitchProbe:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.request_pub = rospy.Publisher(args.request_goal_topic, PoseStamped, queue_size=3, latch=True)

        self.odom: dict | None = None
        self.truth: dict | None = None
        self.raw_cmd: dict | None = None
        self.cmd: dict | None = None
        self.forwarded_goal: dict | None = None
        self.forwarded_goal_seq = 0
        self.mission_ready = not bool(args.require_mission_ready)
        self.last_mission_ready_wall: float | None = None
        self.latest_clock_sim_s: float | None = None
        self.latest_clock_wall_s: float | None = None
        self.clock_message_count = 0
        self.goal_index = 0
        self.goal_start_wall = 0.0
        self.last_record_wall: dict[str, float] = {}
        self.rows: dict[str, list[dict]] = {
            "odom": [],
            "truth": [],
            "raw_cmd": [],
            "cmd": [],
            "forwarded_goal": [],
        }
        self.last_record_wall = {key: -1e9 for key in self.rows}

        self.forwarded_goal_sub = rospy.Subscriber(
            args.forwarded_goal_topic,
            PoseStamped,
            self.on_forwarded_goal,
            queue_size=30,
        )
        rospy.Subscriber(args.clock_topic, Clock, self.on_clock, queue_size=100)
        rospy.Subscriber(args.odom_topic, Odometry, self.on_odom, queue_size=100)
        rospy.Subscriber(args.truth_topic, ModelStates, self.on_truth, queue_size=50)
        rospy.Subscriber(args.raw_cmd_topic, PositionCommand, self.on_raw_cmd, queue_size=200)
        rospy.Subscriber(args.cmd_topic, PositionCommand, self.on_cmd, queue_size=200)
        rospy.Subscriber(args.mission_ready_topic, Bool, self.on_mission_ready, queue_size=10)

    def write_partial_report(self, report: dict) -> None:
        if not self.args.partial_output_json:
            return
        output = Path(self.args.partial_output_json)
        if not output.is_absolute():
            output = Path(self.args.result_dir) / output
        output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    def now(self) -> float:
        if self.latest_clock_sim_s is not None:
            return self.latest_clock_sim_s
        stamp = rospy.Time.now().to_sec()
        return float(stamp) if stamp > 0 else time.time()

    def time_fields(self) -> dict:
        wall = time.time()
        clock_age = None
        if self.latest_clock_wall_s is not None:
            clock_age = max(0.0, wall - self.latest_clock_wall_s)
        return {
            "wall": wall,
            "sim_time_s": self.latest_clock_sim_s,
            "clock_age_wall_s": clock_age,
            "time_basis": "ros_sim_time",
        }

    def clock_summary(self) -> dict:
        return {
            "topic": self.args.clock_topic,
            "messages_observed": self.clock_message_count,
            "latest_sim_time_s": self.latest_clock_sim_s,
            "latest_clock_wall_s": self.latest_clock_wall_s,
        }

    def current_position_row(self) -> dict | None:
        return self.truth or self.odom

    def choose_rejoin_index(
        self,
        goals: list[tuple[float, float, float]],
        next_index: int,
        last_item: dict,
    ) -> tuple[int, dict | None]:
        if not self.args.enable_route_rejoin:
            return next_index, None
        if next_index >= len(goals):
            return next_index, None
        should_rejoin = bool(last_item.get("runtime_skipped_goal") or last_item.get("route_rejoin_recovered_goal"))
        if self.args.route_rejoin_after_soft_waypoint and last_item.get("coverage_soft_waypoint"):
            should_rejoin = True
        if not should_rejoin:
            return next_index, None

        pose = self.current_position_row()
        if pose is None:
            return next_index, {
                "from_route_index": next_index + 1,
                "to_route_index": next_index + 1,
                "reason": "route_rejoin_no_current_pose",
                "applied": False,
            }
        px = float(pose["x"])
        py = float(pose["y"])
        scan_end = min(len(goals), next_index + max(1, self.args.route_rejoin_search_count))
        candidates: list[tuple[float, int, tuple[float, float, float]]] = []
        for idx in range(next_index, scan_end):
            goal = goals[idx]
            dist = math.hypot(goal[0] - px, goal[1] - py)
            candidates.append((dist, idx, goal))
        if not candidates:
            return next_index, None

        original_dist = math.hypot(goals[next_index][0] - px, goals[next_index][1] - py)
        best_dist, best_index, best_goal = min(candidates, key=lambda item: (item[0], item[1]))
        event = {
            "from_route_index": next_index + 1,
            "from_requested": list(goals[next_index]),
            "from_xy_distance_m": original_dist,
            "to_route_index": best_index + 1,
            "to_requested": list(best_goal),
            "to_xy_distance_m": best_dist,
            "current_pose": {"x": px, "y": py, "z": float(pose.get("z", 0.0))},
            "search_count": scan_end - next_index,
            "local_horizon_m": self.args.route_rejoin_local_horizon_m,
            "applied": False,
        }
        if best_index == next_index:
            event["reason"] = "route_rejoin_original_goal_is_nearest"
            return next_index, event
        if best_dist > self.args.route_rejoin_local_horizon_m:
            event["reason"] = "route_rejoin_no_future_goal_inside_local_horizon"
            return next_index, event
        if original_dist <= self.args.route_rejoin_local_horizon_m and (
            original_dist - best_dist < self.args.route_rejoin_min_improvement_m
        ):
            event["reason"] = "route_rejoin_improvement_below_gate"
            return next_index, event
        event["reason"] = "route_rejoin_to_nearest_remaining_goal_after_runtime_skip"
        event["applied"] = True
        event["skipped_route_indices"] = list(range(next_index + 1, best_index + 1))
        return best_index, event

    def recover_stable_failure_for_rejoin(
        self,
        goals: list[tuple[float, float, float]],
        next_index: int,
        item: dict,
    ) -> dict | None:
        def reject(reason: str, **details: object) -> None:
            item["route_rejoin_recovery_reject_reason"] = reason
            if details:
                item["route_rejoin_recovery_reject_details"] = details

        blockers = list(item.get("blockers") or [])
        if not blockers:
            return None
        if not self.args.allow_route_rejoin_on_stable_failure:
            reject("stable_failure_recovery_disabled")
            return None
        if blockers != ["accepted_goal_stable_hold_not_reached"]:
            reject("blockers_not_stable_hold_only", blockers=blockers)
            return None
        if item.get("safety_violation"):
            reject("safety_violation_present", safety_violation=item.get("safety_violation"))
            return None
        if next_index >= len(goals):
            reject("no_future_route_goal", next_index=next_index, goal_count=len(goals))
            return None
        end = item.get("end_truth") or item.get("end_odom")
        if not isinstance(end, dict):
            reject("missing_end_state")
            return None
        if float(end.get("err_xy_m", 1e9)) > self.args.route_rejoin_stable_failure_max_xy_error_m:
            reject(
                "xy_error_above_rejoin_gate",
                err_xy_m=end.get("err_xy_m"),
                max_xy_error_m=self.args.route_rejoin_stable_failure_max_xy_error_m,
            )
            return None
        if abs(float(end.get("err_z_m", 1e9))) > self.args.runtime_skip_max_z_error_m:
            reject(
                "z_error_above_rejoin_gate",
                err_z_m=end.get("err_z_m"),
                max_z_error_m=self.args.runtime_skip_max_z_error_m,
            )
            return None
        if float(end.get("speed_mps", 1e9)) > self.args.route_rejoin_stable_failure_max_speed_mps:
            reject(
                "speed_above_rejoin_gate",
                speed_mps=end.get("speed_mps"),
                max_speed_mps=self.args.route_rejoin_stable_failure_max_speed_mps,
            )
            return None
        if float(end.get("abs_vz_mps", 1e9)) > self.args.runtime_skip_max_vz_mps:
            reject(
                "vz_above_rejoin_gate",
                abs_vz_mps=end.get("abs_vz_mps"),
                max_vz_mps=self.args.runtime_skip_max_vz_mps,
            )
            return None
        if float(end.get("abs_roll_pitch_deg", 1e9)) > self.args.route_rejoin_stable_failure_max_roll_pitch_deg:
            reject(
                "roll_pitch_above_rejoin_gate",
                abs_roll_pitch_deg=end.get("abs_roll_pitch_deg"),
                max_roll_pitch_deg=self.args.route_rejoin_stable_failure_max_roll_pitch_deg,
            )
            return None

        px = float(end["x"])
        py = float(end["y"])
        scan_end = min(len(goals), next_index + max(1, self.args.route_rejoin_search_count))
        candidates: list[tuple[float, int, tuple[float, float, float]]] = []
        for idx in range(next_index, scan_end):
            goal = goals[idx]
            candidates.append((math.hypot(goal[0] - px, goal[1] - py), idx, goal))
        if not candidates:
            reject("no_rejoin_candidates", next_index=next_index, scan_end=scan_end)
            return None
        best_dist, best_index, best_goal = min(candidates, key=lambda candidate: (candidate[0], candidate[1]))
        if best_dist > self.args.route_rejoin_local_horizon_m:
            reject(
                "nearest_future_goal_outside_local_horizon",
                nearest_future_route_index=best_index + 1,
                nearest_future_xy_distance_m=best_dist,
                local_horizon_m=self.args.route_rejoin_local_horizon_m,
                scan_start_route_index=next_index + 1,
                scan_end_route_index=scan_end,
            )
            return None

        recovery = {
            "reason": "stable_failure_recovered_by_near_future_route_goal",
            "failed_route_index": item.get("route_index", item.get("index")),
            "next_route_index": next_index + 1,
            "nearest_future_route_index": best_index + 1,
            "nearest_future_goal": list(best_goal),
            "nearest_future_xy_distance_m": best_dist,
            "scan_start_route_index": next_index + 1,
            "scan_end_route_index": scan_end,
            "end_xy_error_m": end.get("err_xy_m"),
            "end_speed_mps": end.get("speed_mps"),
            "end_z": end.get("z"),
        }
        item["route_rejoin_recovered_goal"] = True
        item["route_rejoin_recovery"] = recovery
        item.pop("route_rejoin_recovery_reject_reason", None)
        item.pop("route_rejoin_recovery_reject_details", None)
        item["blockers"] = []
        item.setdefault("warnings", []).append(
            "route_rejoin_recovered_goal:"
            f"{recovery['failed_route_index']}->{recovery['nearest_future_route_index']}"
        )
        return recovery

    def should_record(self, key: str) -> bool:
        wall = time.time()
        if wall - self.last_record_wall[key] < 1.0 / max(1e-6, self.args.record_hz):
            return False
        self.last_record_wall[key] = wall
        return True

    def record(self, key: str, row: dict) -> None:
        if not self.should_record(key):
            return
        row["goal_index"] = self.goal_index
        row["wall_since_goal_s"] = time.time() - self.goal_start_wall
        self.rows[key].append(row)

    def on_mission_ready(self, msg: Bool) -> None:
        self.mission_ready = bool(msg.data)
        self.last_mission_ready_wall = time.time()

    def on_clock(self, msg: Clock) -> None:
        sim_time_s = finite_time(msg.clock.to_sec())
        if sim_time_s is None or sim_time_s < 0.0:
            return
        self.latest_clock_sim_s = sim_time_s
        self.latest_clock_wall_s = time.time()
        self.clock_message_count += 1

    def on_forwarded_goal(self, msg: PoseStamped) -> None:
        p = msg.pose.position
        self.forwarded_goal_seq += 1
        row = {
            "t": self.now(),
            **self.time_fields(),
            "seq": self.forwarded_goal_seq,
            "x": float(p.x),
            "y": float(p.y),
            "z": float(p.z),
            "frame_id": msg.header.frame_id,
        }
        self.forwarded_goal = row
        self.record("forwarded_goal", row.copy())

    def on_odom(self, msg: Odometry) -> None:
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        v = msg.twist.twist.linear
        roll, pitch, yaw = rpy_from_quat(q.x, q.y, q.z, q.w)
        row = {
            "t": self.now(),
            **self.time_fields(),
            "x": float(p.x),
            "y": float(p.y),
            "z": float(p.z),
            "vx": float(v.x),
            "vy": float(v.y),
            "vz": float(v.z),
            "roll": roll,
            "pitch": pitch,
            "yaw": yaw,
        }
        self.odom = row
        self.record("odom", row.copy())

    def on_truth(self, msg: ModelStates) -> None:
        try:
            idx = list(msg.name).index(self.args.truth_model_name)
        except ValueError:
            return
        pose = msg.pose[idx]
        twist = msg.twist[idx]
        q = pose.orientation
        roll, pitch, yaw = rpy_from_quat(q.x, q.y, q.z, q.w)
        row = {
            "t": self.now(),
            **self.time_fields(),
            "x": float(pose.position.x),
            "y": float(pose.position.y),
            "z": float(pose.position.z),
            "vx": float(twist.linear.x),
            "vy": float(twist.linear.y),
            "vz": float(twist.linear.z),
            "roll": roll,
            "pitch": pitch,
            "yaw": yaw,
        }
        self.truth = row
        self.record("truth", row.copy())

    def cmd_row(self, msg: PositionCommand) -> dict:
        return {
            "t": self.now(),
            **self.time_fields(),
            "x": float(msg.position.x),
            "y": float(msg.position.y),
            "z": float(msg.position.z),
            "vx": float(msg.velocity.x),
            "vy": float(msg.velocity.y),
            "vz": float(msg.velocity.z),
            "ax": float(msg.acceleration.x),
            "ay": float(msg.acceleration.y),
            "az": float(msg.acceleration.z),
            "yaw": float(msg.yaw),
        }

    def on_raw_cmd(self, msg: PositionCommand) -> None:
        row = self.cmd_row(msg)
        self.raw_cmd = row
        self.record("raw_cmd", row.copy())

    def on_cmd(self, msg: PositionCommand) -> None:
        row = self.cmd_row(msg)
        self.cmd = row
        self.record("cmd", row.copy())

    def wait_ready(self) -> bool:
        start = time.time()
        while time.time() - start < self.args.ready_timeout_s and not rospy.is_shutdown():
            if self.odom is not None and self.truth is not None:
                return True
            time.sleep(0.05)
        return False

    def wait_stable_before_goal(self) -> dict:
        if not self.args.wait_stable_before_goal:
            return {"required": False, "ok": True, "reasons": []}
        stable_since = None
        last_snapshot = None
        start = time.time()
        while time.time() - start < self.args.pre_goal_stable_timeout_s and not rospy.is_shutdown():
            snapshot = self.stability_snapshot()
            last_snapshot = snapshot
            if snapshot["ok"]:
                if stable_since is None:
                    stable_since = time.time()
                duration = time.time() - stable_since
                snapshot["stable_duration_s"] = duration
                if duration >= self.args.pre_goal_stable_s:
                    return {"required": True, "ok": True, "snapshot": snapshot, "reasons": []}
            else:
                stable_since = None
            time.sleep(0.05)
        return {
            "required": True,
            "ok": False,
            "snapshot": last_snapshot,
            "reasons": ["pre_goal_stability_timeout"],
        }

    def stability_snapshot(self) -> dict:
        if self.odom is None:
            return {"ok": False, "reasons": ["odom_missing"]}
        target_z = self.args.pre_goal_target_z
        row = self.odom
        speed = math.sqrt(row["vx"] ** 2 + row["vy"] ** 2 + row["vz"] ** 2)
        abs_vz = abs(row["vz"])
        abs_roll_pitch_deg = math.degrees(max(abs(row["roll"]), abs(row["pitch"])))
        reasons: list[str] = []
        if self.args.require_mission_ready and not self.mission_ready:
            reasons.append("mission_not_ready")
        if row["z"] < self.args.pre_goal_min_z_m:
            reasons.append("z_below_min")
        if abs(row["z"] - target_z) > self.args.pre_goal_z_tol_m:
            reasons.append("z_outside_target_tolerance")
        if speed > self.args.pre_goal_max_speed_mps:
            reasons.append("speed_above_gate")
        if abs_vz > self.args.pre_goal_max_vz_mps:
            reasons.append("vz_above_gate")
        if abs_roll_pitch_deg > self.args.pre_goal_max_roll_pitch_deg:
            reasons.append("attitude_above_gate")
        return {
            "ok": not reasons,
            "reasons": reasons,
            "target_z": target_z,
            "x": row["x"],
            "y": row["y"],
            "z": row["z"],
            "speed_mps": speed,
            "abs_vz_mps": abs_vz,
            "abs_roll_pitch_deg": abs_roll_pitch_deg,
            "mission_ready": self.mission_ready,
            "require_mission_ready": self.args.require_mission_ready,
            "mission_ready_topic": self.args.mission_ready_topic,
            "last_mission_ready_age_s": (
                None if self.last_mission_ready_wall is None else time.time() - self.last_mission_ready_wall
            ),
            "stable_duration_s": 0.0,
        }

    def publish_requested_goal(self, goal: tuple[float, float, float]) -> None:
        msg = PoseStamped()
        msg.header.frame_id = self.args.frame_id
        msg.pose.position.x, msg.pose.position.y, msg.pose.position.z = goal
        msg.pose.orientation.w = 1.0
        wait_start = time.time()
        while (
            self.request_pub.get_num_connections() < self.args.min_request_goal_connections
            and time.time() - wait_start < self.args.request_connection_timeout_s
            and not rospy.is_shutdown()
        ):
            time.sleep(0.05)
        for _ in range(self.args.publish_repeats):
            msg.header.stamp = rospy.Time.now()
            self.request_pub.publish(msg)
            time.sleep(self.args.publish_period_s)

    def wait_forwarded_goal_connection(self) -> bool:
        start = time.time()
        while time.time() - start < self.args.forwarded_connection_timeout_s and not rospy.is_shutdown():
            if self.forwarded_goal_sub.get_num_connections() >= self.args.min_forwarded_goal_connections:
                return True
            time.sleep(0.05)
        return False

    def wait_forwarded_goal(self, old_seq: int, publish_wall: float) -> dict | None:
        start = time.time()
        while time.time() - start < self.args.forwarded_goal_timeout_s and not rospy.is_shutdown():
            if (
                self.forwarded_goal is not None
                and self.forwarded_goal_seq > old_seq
                and float(self.forwarded_goal.get("wall", 0.0)) >= publish_wall - 0.10
            ):
                return self.forwarded_goal.copy()
            time.sleep(0.05)
        return None

    @staticmethod
    def state_snapshot(row: dict | None, target: tuple[float, float, float]) -> dict | None:
        if row is None:
            return None
        out = row.copy()
        out["err_xyz_m"] = math.dist((row["x"], row["y"], row["z"]), target)
        out["err_xy_m"] = math.dist((row["x"], row["y"]), target[:2])
        out["err_z_m"] = row["z"] - target[2]
        out["speed_mps"] = math.sqrt(row["vx"] ** 2 + row["vy"] ** 2 + row["vz"] ** 2)
        out["abs_vz_mps"] = abs(row["vz"])
        if "roll" in row and "pitch" in row:
            out["abs_roll_pitch_deg"] = math.degrees(max(abs(row["roll"]), abs(row["pitch"])))
        return out

    @staticmethod
    def summarize_rows(rows: list[dict], goal_index: int, target: tuple[float, float, float]) -> dict:
        subset = [row for row in rows if row.get("goal_index") == goal_index]
        if not subset:
            return {"samples": 0}
        zs = [float(row["z"]) for row in subset]
        xyz_err = [math.dist((float(row["x"]), float(row["y"]), float(row["z"])), target) for row in subset]
        xy_err = [math.dist((float(row["x"]), float(row["y"])), target[:2]) for row in subset]
        vz_values = [abs(float(row.get("vz", 0.0))) for row in subset]
        speed_values = [
            math.sqrt(float(row.get("vx", 0.0)) ** 2 + float(row.get("vy", 0.0)) ** 2 + float(row.get("vz", 0.0)) ** 2)
            for row in subset
        ]
        rp_values = [
            math.degrees(max(abs(float(row.get("roll", 0.0))), abs(float(row.get("pitch", 0.0)))))
            for row in subset
        ]
        return {
            "samples": len(subset),
            "start_xyz": [subset[0]["x"], subset[0]["y"], subset[0]["z"]],
            "end_xyz": [subset[-1]["x"], subset[-1]["y"], subset[-1]["z"]],
            "min_z_m": min(zs),
            "max_z_m": max(zs),
            "end_z_error_m": subset[-1]["z"] - target[2],
            "min_xyz_error_m": min(xyz_err),
            "end_xyz_error_m": xyz_err[-1],
            "min_xy_error_m": min(xy_err),
            "end_xy_error_m": xy_err[-1],
            "max_abs_vz_mps": max(vz_values),
            "max_speed_mps": max(speed_values),
            "max_abs_roll_pitch_deg": max(rp_values),
        }

    @staticmethod
    def goal_stage_timing(forwarded: dict, arrival: dict | None) -> dict:
        start_wall_s = finite_time(forwarded.get("wall"))
        start_sim_s = finite_time(forwarded.get("sim_time_s"))
        if arrival is None:
            return {
                "status": "blocked",
                "reason_code": "stable_arrival_hold_not_confirmed",
                "start": {"wall_s": start_wall_s, "sim_time_s": start_sim_s},
                "arrival": None,
            }

        end_wall_s = finite_time(arrival.get("wall"))
        end_sim_s = finite_time(arrival.get("sim_time_s"))
        timing = {
            "start": {"wall_s": start_wall_s, "sim_time_s": start_sim_s},
            "arrival": {
                "wall_s": end_wall_s,
                "sim_time_s": end_sim_s,
                "clock_age_wall_s": finite_time(arrival.get("clock_age_wall_s")),
            },
        }
        if None in (start_wall_s, start_sim_s, end_wall_s, end_sim_s):
            timing.update({"status": "blocked", "reason_code": "goal_stage_clock_boundary_missing"})
            return timing

        wall_elapsed_s = end_wall_s - start_wall_s
        sim_elapsed_s = end_sim_s - start_sim_s
        timing.update({"wall_elapsed_s": wall_elapsed_s, "sim_elapsed_s": sim_elapsed_s})
        if wall_elapsed_s <= 0.0 or sim_elapsed_s < 0.0:
            timing.update({"status": "blocked", "reason_code": "goal_stage_clock_regressed"})
            return timing

        timing.update(
            {
                "status": "measured",
                "reason_code": "goal_stage_sim_wall_rtf_measured",
                "sim_wall_rtf": sim_elapsed_s / wall_elapsed_s,
            }
        )
        return timing

    def run_goal(self, index: int, requested: tuple[float, float, float]) -> dict:
        self.goal_index = index
        self.goal_start_wall = time.time()
        old_seq = self.forwarded_goal_seq
        pre_goal_stability = self.wait_stable_before_goal()
        start_odom = self.odom.copy() if self.odom else None
        start_truth = self.truth.copy() if self.truth else None
        if not pre_goal_stability.get("ok", False):
            return {
                "index": index,
                "requested": list(requested),
                "accepted": None,
                "pre_goal_stability": pre_goal_stability,
                "start_odom": start_odom,
                "start_truth": start_truth,
                "reached": False,
                "blockers": list(pre_goal_stability.get("reasons", ["pre_goal_stability_failed"])),
            }
        if not self.wait_forwarded_goal_connection():
            return {
                "index": index,
                "requested": list(requested),
                "accepted": None,
                "pre_goal_stability": pre_goal_stability,
                "start_odom": start_odom,
                "start_truth": start_truth,
                "reached": False,
                "blockers": ["forwarded_goal_publisher_connection_timeout"],
            }
        publish_wall = time.time()
        self.publish_requested_goal(requested)
        forwarded = self.wait_forwarded_goal(old_seq, publish_wall)
        if forwarded is None:
            if not self.args.allow_requested_goal_on_forwarded_timeout:
                return {
                    "index": index,
                    "requested": list(requested),
                    "accepted": None,
                    "pre_goal_stability": pre_goal_stability,
                    "start_odom": start_odom,
                    "start_truth": start_truth,
                    "reached": False,
                    "blockers": ["forwarded_goal_timeout"],
                }
            forwarded = {
                "t": self.now(),
                "wall": time.time(),
                "seq": old_seq,
                "x": requested[0],
                "y": requested[1],
                "z": requested[2],
                "frame_id": self.args.frame_id,
                "fallback_reason": "forwarded_goal_timeout_using_requested_goal",
            }
        forwarded_timeout_fallback = bool(forwarded.get("fallback_reason"))

        accepted = (float(forwarded["x"]), float(forwarded["y"]), float(forwarded["z"]))
        request_to_accepted_xy = math.dist(requested[:2], accepted[:2])
        clamped_or_staged = request_to_accepted_xy > self.args.accepted_goal_epsilon_m
        best = None
        reached_since = None
        stable_since_sim = None
        reached_hold_duration_s = 0.0
        reached_hold_ok = False
        reached_hold_start_t = None
        reached_hold_end_t = None
        reached_hold_start_timepoint = None
        reached_hold_end_timepoint = None
        runtime_skip_candidate = False
        runtime_skip_since = None
        runtime_skip_end_t = None
        coverage_soft_candidate = False
        coverage_soft_since = None
        coverage_soft_end_t = None
        safety_violation = None
        attitude_stuck_violation = None
        attitude_stuck_since = None
        start = time.time()
        while time.time() - start < self.args.goal_timeout_s and not rospy.is_shutdown():
            snap = self.state_snapshot(self.odom, accepted)
            truth = self.state_snapshot(self.truth, accepted)
            if snap is not None:
                if best is None or snap["err_xyz_m"] < best["err_xyz_m"]:
                    best = snap
                if snap["z"] < self.args.min_safe_z_m:
                    safety_violation = {"kind": "odom_z_below_min_safe", "snapshot": snap}
                    break
                if snap["abs_roll_pitch_deg"] > self.args.max_safe_roll_pitch_deg:
                    safety_violation = {"kind": "odom_attitude_over_limit", "snapshot": snap}
                    break
                if truth is not None and truth.get("abs_roll_pitch_deg", 0.0) > self.args.max_safe_roll_pitch_deg:
                    safety_violation = {"kind": "truth_attitude_over_limit", "snapshot": truth}
                    break
                stuck_snapshot = truth if truth is not None else snap
                if (
                    self.args.attitude_stuck_gate
                    and time.time() - start >= self.args.attitude_stuck_min_elapsed_s
                    and stuck_snapshot["err_xy_m"] >= self.args.attitude_stuck_min_xy_error_m
                    and stuck_snapshot["speed_mps"] <= self.args.attitude_stuck_max_speed_mps
                    and stuck_snapshot["abs_vz_mps"] <= self.args.attitude_stuck_max_vz_mps
                    and stuck_snapshot.get("abs_roll_pitch_deg", 0.0) >= self.args.attitude_stuck_min_roll_pitch_deg
                ):
                    if attitude_stuck_since is None:
                        attitude_stuck_since = time.time()
                    if time.time() - attitude_stuck_since >= self.args.attitude_stuck_hold_s:
                        attitude_stuck_violation = {
                            "kind": "attitude_stuck_while_far_from_goal",
                            "snapshot": stuck_snapshot,
                            "hold_s": time.time() - attitude_stuck_since,
                            "source": "truth" if truth is not None else "odom",
                        }
                        break
                else:
                    attitude_stuck_since = None
                if (
                    snap["err_xy_m"] <= self.args.reach_xy_radius_m
                    and abs(snap["err_z_m"]) <= self.args.reach_z_tol_m
                    and snap["speed_mps"] <= self.args.reach_max_speed_mps
                    and snap["abs_vz_mps"] <= self.args.reach_max_vz_mps
                ):
                    if reached_since is None:
                        stable_since_sim = self.now()
                        reached_since = stable_since_sim
                        reached_hold_start_t = snap["t"]
                        reached_hold_start_timepoint = self.time_fields()
                    if self.now() - stable_since_sim >= self.args.reach_hold_s:
                        reached_hold_duration_s = self.now() - stable_since_sim
                        reached_hold_end_t = snap["t"]
                        reached_hold_end_timepoint = self.time_fields()
                        reached_hold_ok = True
                        break
                else:
                    reached_since = None
                    stable_since_sim = None
                    reached_hold_start_t = None
                    reached_hold_start_timepoint = None
                    reached_hold_duration_s = 0.0
                    if (
                        self.args.allow_coverage_soft_waypoints
                        and time.time() - start >= self.args.coverage_soft_min_elapsed_s
                        and snap["err_xy_m"] <= self.args.coverage_soft_xy_radius_m
                        and abs(snap["err_z_m"]) <= self.args.coverage_soft_z_tol_m
                        and snap["speed_mps"] <= self.args.coverage_soft_max_speed_mps
                        and snap["abs_vz_mps"] <= self.args.coverage_soft_max_vz_mps
                        and snap.get("abs_roll_pitch_deg", 0.0) <= self.args.coverage_soft_max_roll_pitch_deg
                    ):
                        if coverage_soft_since is None:
                            coverage_soft_since = time.time()
                        if time.time() - coverage_soft_since >= self.args.coverage_soft_hold_s:
                            coverage_soft_candidate = True
                            coverage_soft_end_t = snap["t"]
                            break
                    else:
                        coverage_soft_since = None
                    if (
                        self.args.allow_runtime_skipped_goals
                        and time.time() - start >= self.args.runtime_skip_min_elapsed_s
                        and snap["err_xy_m"] <= self.args.runtime_skip_max_xy_error_m
                        and abs(snap["err_z_m"]) <= self.args.runtime_skip_max_z_error_m
                        and snap["speed_mps"] <= self.args.runtime_skip_max_speed_mps
                        and snap["abs_vz_mps"] <= self.args.runtime_skip_max_vz_mps
                        and snap.get("abs_roll_pitch_deg", 0.0) <= self.args.runtime_skip_max_roll_pitch_deg
                    ):
                        if runtime_skip_since is None:
                            runtime_skip_since = time.time()
                        if time.time() - runtime_skip_since >= self.args.runtime_skip_stable_away_s:
                            runtime_skip_candidate = True
                            runtime_skip_end_t = snap["t"]
                            break
                    else:
                        runtime_skip_since = None
            if truth is not None and truth["z"] < self.args.min_safe_z_m:
                safety_violation = {"kind": "truth_z_below_min_safe", "snapshot": truth}
                break
            if truth is not None and truth.get("abs_roll_pitch_deg", 0.0) > self.args.max_safe_roll_pitch_deg:
                safety_violation = {"kind": "truth_attitude_over_limit", "snapshot": truth}
                break
            time.sleep(0.05)

        end_odom = self.state_snapshot(self.odom, accepted)
        end_truth = self.state_snapshot(self.truth, accepted)
        position_inside_gate = bool(
            end_odom is not None
            and end_odom["err_xy_m"] <= self.args.reach_xy_radius_m
            and abs(end_odom["err_z_m"]) <= self.args.reach_z_tol_m
        )
        reached = reached_hold_ok
        summaries = {key: self.summarize_rows(rows, index, accepted) for key, rows in self.rows.items() if key != "forwarded_goal"}
        blockers: list[str] = []
        warnings: list[str] = []
        if not reached:
            blockers.append("accepted_goal_stable_hold_not_reached")
        if safety_violation:
            blockers.append(safety_violation["kind"])
        if attitude_stuck_violation:
            blockers.append(attitude_stuck_violation["kind"])
        if clamped_or_staged and self.args.fail_on_goal_clamp:
            blockers.append("requested_goal_was_clamped_or_staged")
        elif clamped_or_staged:
            warnings.append("requested_goal_was_clamped_or_staged")
        if forwarded_timeout_fallback:
            warnings.append(str(forwarded["fallback_reason"]))
        for name in ("raw_cmd", "cmd"):
            summary = summaries.get(name, {})
            if summary.get("samples", 0) < self.args.min_cmd_samples:
                cmd_summary = summaries.get("cmd", {})
                if (
                    name == "raw_cmd"
                    and (coverage_soft_candidate or runtime_skip_candidate or reached_hold_ok)
                    and cmd_summary.get("samples", 0) >= self.args.min_cmd_samples
                ):
                    warnings.append(f"{name}_sample_count_below_gate_for_fast_coverage_waypoint")
                    continue
                blockers.append(f"{name}_sample_count_below_gate")
                continue
            z_gate_findings: list[str] = []
            if summary["min_z_m"] < self.args.min_cmd_z_m:
                z_gate_findings.append(f"{name}_z_below_gate")
            if summary["max_z_m"] > self.args.max_cmd_z_m:
                z_gate_findings.append(f"{name}_z_above_gate")
            if abs(summary["end_z_error_m"]) > self.args.cmd_end_z_tol_m:
                z_gate_findings.append(f"{name}_end_z_error_over_gate")
            if name == "raw_cmd" and self.args.raw_cmd_z_warnings_only:
                warnings.extend(z_gate_findings)
            elif (
                name == "cmd"
                and self.args.allow_initial_cmd_z_below_gate
                and z_gate_findings == ["cmd_z_below_gate"]
                and abs(summary["end_z_error_m"]) <= self.args.cmd_end_z_tol_m
                and summary["max_z_m"] <= self.args.max_cmd_z_m
            ):
                warnings.extend(z_gate_findings)
            else:
                blockers.extend(z_gate_findings)
        runtime_skipped_goal = False
        runtime_skip_reason = None
        coverage_soft_waypoint = False
        coverage_soft_reason = None
        if (
            self.args.allow_runtime_skipped_goals
            and not reached
            and (
                runtime_skip_candidate
                or (
                    end_odom is not None
                    and end_odom["err_xy_m"] <= self.args.runtime_skip_max_xy_error_m
                    and abs(end_odom["err_z_m"]) <= self.args.runtime_skip_max_z_error_m
                    and end_odom["speed_mps"] <= self.args.runtime_skip_max_speed_mps
                    and end_odom["abs_vz_mps"] <= self.args.runtime_skip_max_vz_mps
                    and end_odom.get("abs_roll_pitch_deg", 0.0) <= self.args.runtime_skip_max_roll_pitch_deg
                )
            )
            and safety_violation is None
            and end_odom is not None
            and end_odom["err_xy_m"] <= self.args.runtime_skip_max_xy_error_m
            and abs(end_odom["err_z_m"]) <= self.args.runtime_skip_max_z_error_m
            and end_odom["speed_mps"] <= self.args.runtime_skip_max_speed_mps
            and end_odom["abs_vz_mps"] <= self.args.runtime_skip_max_vz_mps
            and end_odom.get("abs_roll_pitch_deg", 0.0) <= self.args.runtime_skip_max_roll_pitch_deg
        ):
            runtime_skipped_goal = True
            runtime_skip_reason = "stable_away_from_accepted_goal_after_runtime_replan_or_collision_clamp"
            blockers = [blocker for blocker in blockers if blocker != "accepted_goal_stable_hold_not_reached"]
            warnings.append(f"runtime_skipped_goal:{runtime_skip_reason}")
        if (
            self.args.allow_coverage_soft_waypoints
            and not reached
            and not runtime_skipped_goal
            and coverage_soft_candidate
            and safety_violation is None
            and end_odom is not None
            and end_odom["err_xy_m"] <= self.args.coverage_soft_xy_radius_m
            and abs(end_odom["err_z_m"]) <= self.args.coverage_soft_z_tol_m
            and end_odom["speed_mps"] <= self.args.coverage_soft_max_speed_mps
            and end_odom["abs_vz_mps"] <= self.args.coverage_soft_max_vz_mps
            and end_odom.get("abs_roll_pitch_deg", 0.0) <= self.args.coverage_soft_max_roll_pitch_deg
        ):
            coverage_soft_waypoint = True
            coverage_soft_reason = "coverage_route_point_reached_within_sensor_footprint_without_stable_hover"
            blockers = [blocker for blocker in blockers if blocker != "accepted_goal_stable_hold_not_reached"]
            warnings.append(f"coverage_soft_waypoint:{coverage_soft_reason}")
        goal_stage_timing = self.goal_stage_timing(forwarded, reached_hold_end_timepoint)
        return {
            "index": index,
            "requested": list(requested),
            "accepted": list(accepted),
            "forwarded_goal": forwarded,
            "pre_goal_stability": pre_goal_stability,
            "request_to_accepted_xy_m": request_to_accepted_xy,
            "clamped_or_staged": clamped_or_staged,
            "start_odom": self.state_snapshot(start_odom, accepted) if start_odom else None,
            "start_truth": self.state_snapshot(start_truth, accepted) if start_truth else None,
            "end_odom": end_odom,
            "end_truth": end_truth,
            "best_odom": best,
            "reached": reached,
            "runtime_skipped_goal": runtime_skipped_goal,
            "runtime_skip_reason": runtime_skip_reason,
            "runtime_skip_candidate": runtime_skip_candidate,
            "runtime_skip_end_t": runtime_skip_end_t,
            "coverage_soft_waypoint": coverage_soft_waypoint,
            "coverage_soft_reason": coverage_soft_reason,
            "coverage_soft_candidate": coverage_soft_candidate,
            "coverage_soft_end_t": coverage_soft_end_t,
            "position_inside_gate_at_end": position_inside_gate,
            "stable_hold": {
                "required_s": self.args.reach_hold_s,
                "duration_s": reached_hold_duration_s,
                "ok": reached_hold_ok,
                "start_t": reached_hold_start_t,
                "end_t": reached_hold_end_t,
                "start_timepoint": reached_hold_start_timepoint,
                "end_timepoint": reached_hold_end_timepoint,
            },
            "goal_stage_timing": goal_stage_timing,
            "safety_violation": safety_violation,
            "attitude_stuck_violation": attitude_stuck_violation,
            "summaries": summaries,
            "warnings": warnings,
            "blockers": blockers,
        }

    def run(self) -> dict:
        report = {
            "schema": "mosim.sunray_ros1.diff_interactive_goal_switch_chain_probe.v1",
            "goal_source": self.args.goals_file or "inline",
            "request_goal_topic": self.args.request_goal_topic,
            "forwarded_goal_topic": self.args.forwarded_goal_topic,
            "mission_ready_topic": self.args.mission_ready_topic,
            "require_mission_ready": self.args.require_mission_ready,
            "odom_topic": self.args.odom_topic,
            "truth_topic": self.args.truth_topic,
            "raw_cmd_topic": self.args.raw_cmd_topic,
            "cmd_topic": self.args.cmd_topic,
            "route_rejoin": {
                "enabled": bool(self.args.enable_route_rejoin),
                "after_soft_waypoint": bool(self.args.route_rejoin_after_soft_waypoint),
                "stable_failure_recovery": bool(self.args.allow_route_rejoin_on_stable_failure),
                "local_horizon_m": self.args.route_rejoin_local_horizon_m,
                "search_count": self.args.route_rejoin_search_count,
                "min_improvement_m": self.args.route_rejoin_min_improvement_m,
                "stable_failure_max_xy_error_m": self.args.route_rejoin_stable_failure_max_xy_error_m,
                "stable_failure_max_speed_mps": self.args.route_rejoin_stable_failure_max_speed_mps,
                "stable_failure_max_roll_pitch_deg": self.args.route_rejoin_stable_failure_max_roll_pitch_deg,
            },
            "goals": [],
            "route_rejoin_events": [],
            "route_rejoin_recoveries": [],
            "status": "running",
        }
        if not self.wait_ready():
            report["status"] = "blocked"
            report["blockers"] = ["ready_timeout_no_odom_or_truth"]
            report["clock"] = self.clock_summary()
            return report
        goals = load_goals(self.args)
        report["loaded_route_goal_count"] = len(goals)
        report["max_executed_goal_count"] = self.args.max_goals
        route_index = 0
        executed_goal_count = 0
        while route_index < len(goals):
            if self.args.max_goals > 0 and executed_goal_count >= self.args.max_goals:
                report["stop_reason"] = "max_executed_goal_count_reached"
                break
            requested = goals[route_index]
            executed_goal_count += 1
            item = self.run_goal(executed_goal_count, requested)
            item["route_index"] = route_index + 1
            report["goals"].append(item)
            report["status"] = "running"
            report["completed_goal_count"] = len(report["goals"])
            self.write_partial_report(report)
            next_route_index = route_index + 1
            recovery = self.recover_stable_failure_for_rejoin(goals, next_route_index, item)
            if recovery is not None:
                report.setdefault("route_rejoin_recoveries", []).append(recovery)
                self.write_partial_report(report)
            if item["blockers"] and self.args.stop_on_first_failure:
                report["status"] = "blocked"
                report["blockers"] = [
                    f"goal_{executed_goal_count}/route_{route_index + 1}:{blocker}"
                    for blocker in item["blockers"]
                ]
                report["runtime_skipped_goal_count"] = sum(
                    1 for recorded in report["goals"] if recorded.get("runtime_skipped_goal")
                )
                report["coverage_soft_waypoint_count"] = sum(
                    1 for recorded in report["goals"] if recorded.get("coverage_soft_waypoint")
                )
                report["route_rejoin_applied_count"] = sum(
                    1 for event in report.get("route_rejoin_events", []) if event.get("applied")
                )
                report["route_rejoin_recovered_goal_count"] = sum(
                    1 for recorded in report["goals"] if recorded.get("route_rejoin_recovered_goal")
                )
                report["clock"] = self.clock_summary()
                self.write_partial_report(report)
                return report
            rejoin_index, rejoin_event = self.choose_rejoin_index(goals, next_route_index, item)
            if rejoin_event is not None:
                rejoin_event["after_goal_index"] = executed_goal_count
                rejoin_event["after_route_index"] = route_index + 1
                report["route_rejoin_events"].append(rejoin_event)
                if rejoin_event.get("applied"):
                    item.setdefault("warnings", []).append(
                        "route_rejoin:"
                        f"{rejoin_event['from_route_index']}->{rejoin_event['to_route_index']}"
                    )
            route_index = rejoin_index
        blockers = [
            f"goal_{item['index']}/route_{item.get('route_index', item['index'])}:{blocker}"
            for item in report["goals"]
            for blocker in item.get("blockers", [])
        ]
        warnings = [
            f"goal_{item['index']}/route_{item.get('route_index', item['index'])}:{warning}"
            for item in report["goals"]
            for warning in item.get("warnings", [])
        ]
        report["runtime_skipped_goal_count"] = sum(1 for item in report["goals"] if item.get("runtime_skipped_goal"))
        report["coverage_soft_waypoint_count"] = sum(
            1 for item in report["goals"] if item.get("coverage_soft_waypoint")
        )
        report["route_rejoin_applied_count"] = sum(
            1 for event in report.get("route_rejoin_events", []) if event.get("applied")
        )
        report["route_rejoin_recovered_goal_count"] = sum(
            1 for item in report["goals"] if item.get("route_rejoin_recovered_goal")
        )
        report["status"] = "blocked" if blockers else "passed"
        report["blockers"] = blockers
        report["warnings"] = warnings
        report["clock"] = self.clock_summary()
        return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--output-json", default="DIFF_INTERACTIVE_GOAL_SWITCH_CHAIN_PROBE.json")
    parser.add_argument("--partial-output-json", default="")
    parser.add_argument("--goal-stage-rtf-output", default="DIFF_INTERACTIVE_GOAL_STAGE_RTF.json")
    parser.add_argument("--clock-topic", default="/clock")
    parser.add_argument("--request-goal-topic", default="/move_base_simple/goal")
    parser.add_argument("--forwarded-goal-topic", default="/goal_with_id")
    parser.add_argument("--mission-ready-topic", default="/mosim/goal4/interactive_goal_ready")
    parser.add_argument("--require-mission-ready", action="store_true", default=True)
    parser.add_argument("--no-require-mission-ready", dest="require_mission_ready", action="store_false")
    parser.add_argument("--odom-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--truth-topic", default="/gazebo/model_states")
    parser.add_argument("--truth-model-name", default="uav1")
    parser.add_argument("--raw-cmd-topic", default="/diff_planner/position_cmd_raw")
    parser.add_argument("--cmd-topic", default="/position_cmd")
    parser.add_argument("--frame-id", default="world")
    parser.add_argument("--goals", default="2.0,0.0,1.0;3.0,0.5,1.0;4.0,1.0,1.0")
    parser.add_argument("--goals-file", default="")
    parser.add_argument("--max-goals", type=int, default=0)
    parser.add_argument("--ready-timeout-s", type=float, default=12.0)
    parser.add_argument("--forwarded-goal-timeout-s", type=float, default=5.0)
    parser.add_argument("--allow-requested-goal-on-forwarded-timeout", action="store_true")
    parser.add_argument("--goal-timeout-s", type=float, default=45.0)
    parser.add_argument("--wait-stable-before-goal", action="store_true", default=True)
    parser.add_argument("--no-wait-stable-before-goal", dest="wait_stable_before_goal", action="store_false")
    parser.add_argument("--pre-goal-stable-timeout-s", type=float, default=80.0)
    parser.add_argument("--pre-goal-stable-s", type=float, default=1.0)
    parser.add_argument("--pre-goal-target-z", type=float, default=1.0)
    parser.add_argument("--pre-goal-min-z-m", type=float, default=0.85)
    parser.add_argument("--pre-goal-z-tol-m", type=float, default=0.15)
    parser.add_argument("--pre-goal-max-speed-mps", type=float, default=0.35)
    parser.add_argument("--pre-goal-max-vz-mps", type=float, default=0.20)
    parser.add_argument("--pre-goal-max-roll-pitch-deg", type=float, default=12.0)
    parser.add_argument("--publish-repeats", type=int, default=3)
    parser.add_argument("--publish-period-s", type=float, default=0.12)
    parser.add_argument("--min-request-goal-connections", type=int, default=1)
    parser.add_argument("--request-connection-timeout-s", type=float, default=5.0)
    parser.add_argument("--min-forwarded-goal-connections", type=int, default=1)
    parser.add_argument("--forwarded-connection-timeout-s", type=float, default=10.0)
    parser.add_argument("--record-hz", type=float, default=30.0)
    parser.add_argument("--reach-xy-radius-m", type=float, default=0.35)
    parser.add_argument("--reach-z-tol-m", type=float, default=0.12)
    parser.add_argument("--reach-max-speed-mps", type=float, default=0.45)
    parser.add_argument("--reach-max-vz-mps", type=float, default=0.25)
    parser.add_argument("--reach-hold-s", type=float, default=1.0)
    parser.add_argument("--min-safe-z-m", type=float, default=0.50)
    parser.add_argument("--max-safe-roll-pitch-deg", type=float, default=45.0)
    parser.add_argument("--attitude-stuck-gate", action="store_true")
    parser.add_argument("--attitude-stuck-min-elapsed-s", type=float, default=8.0)
    parser.add_argument("--attitude-stuck-hold-s", type=float, default=2.0)
    parser.add_argument("--attitude-stuck-min-xy-error-m", type=float, default=2.0)
    parser.add_argument("--attitude-stuck-max-speed-mps", type=float, default=0.08)
    parser.add_argument("--attitude-stuck-max-vz-mps", type=float, default=0.05)
    parser.add_argument("--attitude-stuck-min-roll-pitch-deg", type=float, default=18.0)
    parser.add_argument("--min-cmd-samples", type=int, default=5)
    parser.add_argument("--min-cmd-z-m", type=float, default=0.80)
    parser.add_argument("--max-cmd-z-m", type=float, default=1.45)
    parser.add_argument("--cmd-end-z-tol-m", type=float, default=0.15)
    parser.add_argument("--raw-cmd-z-warnings-only", action="store_true")
    parser.add_argument("--allow-initial-cmd-z-below-gate", action="store_true")
    parser.add_argument("--accepted-goal-epsilon-m", type=float, default=0.05)
    parser.add_argument("--fail-on-goal-clamp", action="store_true")
    parser.add_argument("--allow-runtime-skipped-goals", action="store_true")
    parser.add_argument("--runtime-skip-max-xy-error-m", type=float, default=2.50)
    parser.add_argument("--runtime-skip-max-z-error-m", type=float, default=0.25)
    parser.add_argument("--runtime-skip-max-speed-mps", type=float, default=0.08)
    parser.add_argument("--runtime-skip-max-vz-mps", type=float, default=0.05)
    parser.add_argument("--runtime-skip-max-roll-pitch-deg", type=float, default=8.0)
    parser.add_argument("--runtime-skip-min-elapsed-s", type=float, default=8.0)
    parser.add_argument("--runtime-skip-stable-away-s", type=float, default=3.0)
    parser.add_argument("--allow-coverage-soft-waypoints", action="store_true")
    parser.add_argument("--coverage-soft-xy-radius-m", type=float, default=1.25)
    parser.add_argument("--coverage-soft-z-tol-m", type=float, default=0.25)
    parser.add_argument("--coverage-soft-max-speed-mps", type=float, default=0.80)
    parser.add_argument("--coverage-soft-max-vz-mps", type=float, default=0.25)
    parser.add_argument("--coverage-soft-max-roll-pitch-deg", type=float, default=10.0)
    parser.add_argument("--coverage-soft-min-elapsed-s", type=float, default=2.0)
    parser.add_argument("--coverage-soft-hold-s", type=float, default=0.25)
    parser.add_argument("--enable-route-rejoin", action="store_true")
    parser.add_argument("--route-rejoin-after-soft-waypoint", action="store_true")
    parser.add_argument("--allow-route-rejoin-on-stable-failure", action="store_true")
    parser.add_argument("--route-rejoin-local-horizon-m", type=float, default=5.0)
    parser.add_argument("--route-rejoin-search-count", type=int, default=80)
    parser.add_argument("--route-rejoin-min-improvement-m", type=float, default=0.50)
    parser.add_argument("--route-rejoin-stable-failure-max-xy-error-m", type=float, default=5.25)
    parser.add_argument("--route-rejoin-stable-failure-max-speed-mps", type=float, default=0.08)
    parser.add_argument("--route-rejoin-stable-failure-max-roll-pitch-deg", type=float, default=8.0)
    parser.add_argument("--stop-on-first-failure", action="store_true")
    args = parser.parse_args()

    rospy.init_node("mosim_diff_interactive_goal_switch_chain_probe", anonymous=True)
    result_dir = Path(args.result_dir)
    result_dir.mkdir(parents=True, exist_ok=True)
    output_json = Path(args.output_json)
    if not output_json.is_absolute():
        output_json = result_dir / output_json

    probe = InteractiveGoalSwitchProbe(args)
    report = probe.run()
    output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    rtf_output = Path(args.goal_stage_rtf_output)
    if not rtf_output.is_absolute():
        rtf_output = result_dir / rtf_output
    rtf_output.write_text(
        json.dumps(build_goal_stage_rtf_report(report, args.clock_topic), indent=2) + "\n",
        encoding="utf-8",
    )
    print(output_json)
    return 0 if report.get("status") == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
