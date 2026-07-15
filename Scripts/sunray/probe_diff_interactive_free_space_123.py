#!/usr/bin/env python3
"""Probe Goal4 Diff interactive target handling with known free-space goals."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry


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


class Probe:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.odom: tuple[float, float, float, float, float, float, float] | None = None
        self.pub = rospy.Publisher(args.goal_topic, PoseStamped, queue_size=3, latch=True)
        rospy.Subscriber(args.odom_topic, Odometry, self.on_odom, queue_size=30)

    def on_odom(self, msg: Odometry) -> None:
        p = msg.pose.pose.position
        v = msg.twist.twist.linear
        self.odom = (
            float(p.x),
            float(p.y),
            float(p.z),
            float(v.x),
            float(v.y),
            float(v.z),
            rospy.Time.now().to_sec(),
        )

    def wait_for_odom(self) -> bool:
        start = time.time()
        while self.odom is None and time.time() - start < self.args.odom_timeout_s and not rospy.is_shutdown():
            time.sleep(0.05)
        return self.odom is not None

    def publish_goal(self, goal: tuple[float, float, float]) -> None:
        msg = PoseStamped()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.args.frame_id
        msg.pose.position.x, msg.pose.position.y, msg.pose.position.z = goal
        msg.pose.orientation.w = 1.0
        for _ in range(self.args.publish_repeats):
            self.pub.publish(msg)
            time.sleep(self.args.publish_period_s)

    def current_snapshot(self, goal: tuple[float, float, float]) -> dict | None:
        if self.odom is None:
            return None
        x, y, z, vx, vy, vz, t = self.odom
        return {
            "t": t,
            "x": x,
            "y": y,
            "z": z,
            "err": math.dist((x, y, z), goal),
            "xy_err": math.dist((x, y), goal[:2]),
            "z_error": z - goal[2],
            "speed": math.sqrt(vx * vx + vy * vy + vz * vz),
            "vz": vz,
        }

    def run_goal(self, index: int, goal: tuple[float, float, float]) -> dict:
        self.publish_goal(goal)
        best = None
        samples: list[dict] = []
        reached_since = None
        start = time.time()
        while time.time() - start < self.args.goal_timeout_s and not rospy.is_shutdown():
            snap = self.current_snapshot(goal)
            if snap is None:
                time.sleep(0.05)
                continue
            if best is None or snap["err"] < best["err"]:
                best = snap
            if len(samples) < 5 or time.time() - start > len(samples) * self.args.sample_period_s:
                samples.append(snap)
            if (
                snap["err"] <= self.args.reach_radius_m
                and snap["speed"] <= self.args.reach_max_speed_mps
                and abs(snap["vz"]) <= self.args.reach_max_vz_mps
            ):
                if reached_since is None:
                    reached_since = time.time()
                if time.time() - reached_since >= self.args.reach_hold_s:
                    break
            else:
                reached_since = None
            time.sleep(0.05)
        last = self.current_snapshot(goal)
        reached = bool(last is not None and last["err"] <= self.args.reach_radius_m)
        return {
            "index": index,
            "target": list(goal),
            "reached": reached,
            "best": best,
            "last": last,
            "samples": samples,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--output-json", default="FREE_SPACE_INTERACTIVE_123_PROBE.json")
    parser.add_argument("--goal-topic", default="/move_base_simple/goal")
    parser.add_argument("--odom-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--frame-id", default="world")
    parser.add_argument("--goals", default="1.0,0.0,1.0;2.0,0.0,1.0;3.0,0.5,1.0")
    parser.add_argument("--odom-timeout-s", type=float, default=8.0)
    parser.add_argument("--goal-timeout-s", type=float, default=35.0)
    parser.add_argument("--publish-repeats", type=int, default=3)
    parser.add_argument("--publish-period-s", type=float, default=0.12)
    parser.add_argument("--reach-radius-m", type=float, default=0.35)
    parser.add_argument("--reach-max-speed-mps", type=float, default=0.45)
    parser.add_argument("--reach-max-vz-mps", type=float, default=0.25)
    parser.add_argument("--reach-hold-s", type=float, default=1.0)
    parser.add_argument("--sample-period-s", type=float, default=2.0)
    args = parser.parse_args()

    rospy.init_node("mosim_diff_interactive_free_space_123_probe", anonymous=True)
    result_dir = Path(args.result_dir)
    result_dir.mkdir(parents=True, exist_ok=True)
    output_json = Path(args.output_json)
    if not output_json.is_absolute():
        output_json = result_dir / output_json

    probe = Probe(args)
    goals = parse_goals(args.goals)
    report = {
        "schema": "mosim.sunray_ros1.diff_free_space_interactive_probe.v1",
        "goal_topic": args.goal_topic,
        "odom_topic": args.odom_topic,
        "goals": [],
        "status": "running",
    }
    if not probe.wait_for_odom():
        report["status"] = "blocked"
        report["blocker"] = "no_odom"
        output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(output_json)
        return 2
    report["start_odom"] = list(probe.odom) if probe.odom is not None else None

    for index, goal in enumerate(goals, start=1):
        item = probe.run_goal(index, goal)
        report["goals"].append(item)
        output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
        if not item["reached"]:
            report["status"] = "blocked"
            report["blocker"] = f"goal_{index}_not_reached"
            output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
            print(output_json)
            return 1

    report["status"] = "passed"
    report["end_odom"] = list(probe.odom) if probe.odom is not None else None
    output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
