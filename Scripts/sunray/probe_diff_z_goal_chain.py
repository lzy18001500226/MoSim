#!/usr/bin/env python3
"""Probe Diff-Planner 3D goal handling and Z command/execution chain."""

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


def yaw_from_quat(x: float, y: float, z: float, w: float) -> float:
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


def rpy_from_quat(x: float, y: float, z: float, w: float) -> tuple[float, float, float]:
    roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
    pitch = math.asin(max(-1.0, min(1.0, 2.0 * (w * y - z * x))))
    yaw = yaw_from_quat(x, y, z, w)
    return roll, pitch, yaw


class ChainProbe:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.goal_pub = rospy.Publisher(args.goal_topic, PoseStamped, queue_size=3, latch=True)
        self.odom: dict | None = None
        self.truth: dict | None = None
        self.raw_cmd: dict | None = None
        self.cmd: dict | None = None
        self.goal_start_wall = 0.0
        self.goal_index = 0
        self.rows: dict[str, list[dict]] = {
            "odom": [],
            "truth": [],
            "raw_cmd": [],
            "cmd": [],
        }
        self.last_record_wall = {key: -1e9 for key in self.rows}
        rospy.Subscriber(args.odom_topic, Odometry, self.on_odom, queue_size=100)
        rospy.Subscriber(args.truth_topic, ModelStates, self.on_truth, queue_size=50)
        rospy.Subscriber(args.raw_cmd_topic, PositionCommand, self.on_raw_cmd, queue_size=200)
        rospy.Subscriber(args.cmd_topic, PositionCommand, self.on_cmd, queue_size=200)

    def now(self) -> float:
        stamp = rospy.Time.now().to_sec()
        return float(stamp) if stamp > 0 else time.time()

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

    def on_odom(self, msg: Odometry) -> None:
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        v = msg.twist.twist.linear
        roll, pitch, yaw = rpy_from_quat(q.x, q.y, q.z, q.w)
        row = {
            "t": self.now(),
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

    @staticmethod
    def cmd_row(msg: PositionCommand, t: float) -> dict:
        return {
            "t": t,
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
        row = self.cmd_row(msg, self.now())
        self.raw_cmd = row
        self.record("raw_cmd", row.copy())

    def on_cmd(self, msg: PositionCommand) -> None:
        row = self.cmd_row(msg, self.now())
        self.cmd = row
        self.record("cmd", row.copy())

    def wait_ready(self) -> bool:
        start = time.time()
        while time.time() - start < self.args.ready_timeout_s and not rospy.is_shutdown():
            if self.odom is not None and self.truth is not None:
                return True
            time.sleep(0.05)
        return False

    def publish_goal(self, goal: tuple[float, float, float]) -> None:
        msg = PoseStamped()
        msg.header.frame_id = self.args.frame_id
        msg.pose.position.x, msg.pose.position.y, msg.pose.position.z = goal
        msg.pose.orientation.w = 1.0
        for _ in range(self.args.publish_repeats):
            msg.header.stamp = rospy.Time.now()
            self.goal_pub.publish(msg)
            time.sleep(self.args.publish_period_s)

    @staticmethod
    def state_snapshot(row: dict | None, goal: tuple[float, float, float]) -> dict | None:
        if row is None:
            return None
        out = row.copy()
        out["err_xyz_m"] = math.dist((row["x"], row["y"], row["z"]), goal)
        out["err_xy_m"] = math.dist((row["x"], row["y"]), goal[:2])
        out["err_z_m"] = row["z"] - goal[2]
        out["speed_mps"] = math.sqrt(row["vx"] ** 2 + row["vy"] ** 2 + row["vz"] ** 2)
        out["abs_vz_mps"] = abs(row["vz"])
        if "roll" in row and "pitch" in row:
            out["abs_roll_pitch_deg"] = math.degrees(max(abs(row["roll"]), abs(row["pitch"])))
        return out

    @staticmethod
    def summarize_rows(rows: list[dict], goal_index: int, goal: tuple[float, float, float]) -> dict:
        subset = [row for row in rows if row.get("goal_index") == goal_index]
        if not subset:
            return {"samples": 0}
        zs = [float(row["z"]) for row in subset]
        xyz_err = [math.dist((float(row["x"]), float(row["y"]), float(row["z"])), goal) for row in subset]
        xy_err = [math.dist((float(row["x"]), float(row["y"])), goal[:2]) for row in subset]
        vz_values = [abs(float(row.get("vz", 0.0))) for row in subset]
        return {
            "samples": len(subset),
            "start_xyz": [subset[0]["x"], subset[0]["y"], subset[0]["z"]],
            "end_xyz": [subset[-1]["x"], subset[-1]["y"], subset[-1]["z"]],
            "min_z_m": min(zs),
            "max_z_m": max(zs),
            "end_z_error_m": subset[-1]["z"] - goal[2],
            "min_xyz_error_m": min(xyz_err),
            "end_xyz_error_m": xyz_err[-1],
            "min_xy_error_m": min(xy_err),
            "end_xy_error_m": xy_err[-1],
            "max_abs_vz_mps": max(vz_values),
        }

    def run_goal(self, index: int, goal: tuple[float, float, float]) -> dict:
        self.goal_index = index
        self.goal_start_wall = time.time()
        start_counts = {key: len(value) for key, value in self.rows.items()}
        start_odom = self.state_snapshot(self.odom, goal)
        start_truth = self.state_snapshot(self.truth, goal)
        self.publish_goal(goal)
        best = None
        reached_since = None
        safety_violation = None
        start = time.time()
        while time.time() - start < self.args.goal_timeout_s and not rospy.is_shutdown():
            snap = self.state_snapshot(self.odom, goal)
            truth = self.state_snapshot(self.truth, goal)
            if snap is not None:
                if best is None or snap["err_xyz_m"] < best["err_xyz_m"]:
                    best = snap
                if snap["z"] < self.args.min_safe_z_m:
                    safety_violation = {"kind": "odom_z_below_min_safe", "snapshot": snap}
                    break
                if abs(snap["roll"]) > math.radians(self.args.max_safe_roll_pitch_deg) or abs(snap["pitch"]) > math.radians(self.args.max_safe_roll_pitch_deg):
                    safety_violation = {"kind": "odom_attitude_over_limit", "snapshot": snap}
                    break
                if (
                    snap["err_xy_m"] <= self.args.reach_xy_radius_m
                    and abs(snap["err_z_m"]) <= self.args.reach_z_tol_m
                    and snap["speed_mps"] <= self.args.reach_max_speed_mps
                    and snap["abs_vz_mps"] <= self.args.reach_max_vz_mps
                ):
                    if reached_since is None:
                        reached_since = time.time()
                    if time.time() - reached_since >= self.args.reach_hold_s:
                        break
                else:
                    reached_since = None
            if truth is not None and truth["z"] < self.args.min_safe_z_m:
                safety_violation = {"kind": "truth_z_below_min_safe", "snapshot": truth}
                break
            time.sleep(0.05)
        end_odom = self.state_snapshot(self.odom, goal)
        end_truth = self.state_snapshot(self.truth, goal)
        reached = bool(
            end_odom is not None
            and end_odom["err_xy_m"] <= self.args.reach_xy_radius_m
            and abs(end_odom["err_z_m"]) <= self.args.reach_z_tol_m
        )
        summaries = {
            key: self.summarize_rows(rows, index, goal)
            for key, rows in self.rows.items()
        }
        blockers: list[str] = []
        if not reached:
            blockers.append("goal_not_reached")
        if safety_violation:
            blockers.append(safety_violation["kind"])
        raw_summary = summaries.get("raw_cmd", {})
        cmd_summary = summaries.get("cmd", {})
        for name, summary in (("raw_cmd", raw_summary), ("cmd", cmd_summary)):
            if summary.get("samples", 0) < self.args.min_cmd_samples:
                blockers.append(f"{name}_sample_count_below_gate")
                continue
            if summary["min_z_m"] < self.args.min_cmd_z_m:
                blockers.append(f"{name}_z_below_gate")
            if summary["max_z_m"] > self.args.max_cmd_z_m:
                blockers.append(f"{name}_z_above_gate")
            if abs(summary["end_z_error_m"]) > self.args.cmd_end_z_tol_m:
                blockers.append(f"{name}_end_z_error_over_gate")
        return {
            "index": index,
            "target": list(goal),
            "start_counts": start_counts,
            "end_counts": {key: len(value) for key, value in self.rows.items()},
            "start_odom": start_odom,
            "start_truth": start_truth,
            "end_odom": end_odom,
            "end_truth": end_truth,
            "best_odom": best,
            "reached": reached,
            "safety_violation": safety_violation,
            "summaries": summaries,
            "blockers": blockers,
        }

    def run(self) -> dict:
        report = {
            "schema": "mosim.sunray_ros1.diff_z_goal_chain_probe.v1",
            "goal_topic": self.args.goal_topic,
            "odom_topic": self.args.odom_topic,
            "truth_topic": self.args.truth_topic,
            "raw_cmd_topic": self.args.raw_cmd_topic,
            "cmd_topic": self.args.cmd_topic,
            "goals": [],
            "status": "running",
        }
        if not self.wait_ready():
            report["status"] = "blocked"
            report["blockers"] = ["ready_timeout_no_odom_or_truth"]
            return report
        for index, goal in enumerate(parse_goals(self.args.goals), start=1):
            item = self.run_goal(index, goal)
            report["goals"].append(item)
            if item["blockers"] and self.args.stop_on_first_failure:
                report["status"] = "blocked"
                report["blockers"] = [f"goal_{index}:{blocker}" for blocker in item["blockers"]]
                return report
        blockers = [
            f"goal_{item['index']}:{blocker}"
            for item in report["goals"]
            for blocker in item.get("blockers", [])
        ]
        report["status"] = "blocked" if blockers else "passed"
        report["blockers"] = blockers
        return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--output-json", default="DIFF_Z_GOAL_CHAIN_PROBE.json")
    parser.add_argument("--goal-topic", default="/goal_with_id")
    parser.add_argument("--odom-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--truth-topic", default="/gazebo/model_states")
    parser.add_argument("--truth-model-name", default="uav1")
    parser.add_argument("--raw-cmd-topic", default="/diff_planner/position_cmd_raw")
    parser.add_argument("--cmd-topic", default="/position_cmd")
    parser.add_argument("--frame-id", default="world")
    parser.add_argument("--goals", default="1.0,0.0,1.0;2.0,0.0,1.2;3.0,0.5,0.9;4.0,1.0,1.0")
    parser.add_argument("--ready-timeout-s", type=float, default=8.0)
    parser.add_argument("--goal-timeout-s", type=float, default=45.0)
    parser.add_argument("--publish-repeats", type=int, default=3)
    parser.add_argument("--publish-period-s", type=float, default=0.12)
    parser.add_argument("--record-hz", type=float, default=30.0)
    parser.add_argument("--reach-xy-radius-m", type=float, default=0.35)
    parser.add_argument("--reach-z-tol-m", type=float, default=0.12)
    parser.add_argument("--reach-max-speed-mps", type=float, default=0.45)
    parser.add_argument("--reach-max-vz-mps", type=float, default=0.25)
    parser.add_argument("--reach-hold-s", type=float, default=1.0)
    parser.add_argument("--min-safe-z-m", type=float, default=0.50)
    parser.add_argument("--max-safe-roll-pitch-deg", type=float, default=45.0)
    parser.add_argument("--min-cmd-samples", type=int, default=5)
    parser.add_argument("--min-cmd-z-m", type=float, default=0.80)
    parser.add_argument("--max-cmd-z-m", type=float, default=1.45)
    parser.add_argument("--cmd-end-z-tol-m", type=float, default=0.15)
    parser.add_argument("--stop-on-first-failure", action="store_true")
    args = parser.parse_args()

    rospy.init_node("mosim_diff_z_goal_chain_probe", anonymous=True)
    result_dir = Path(args.result_dir)
    result_dir.mkdir(parents=True, exist_ok=True)
    output_json = Path(args.output_json)
    if not output_json.is_absolute():
        output_json = result_dir / output_json

    probe = ChainProbe(args)
    report = probe.run()
    output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(output_json)
    return 0 if report.get("status") == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
