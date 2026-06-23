#!/usr/bin/env python3
"""Record Goal 3 FAST-LIO external-vision/PX4-EKF fusion evidence.

This recorder is passive. It does not arm, publish setpoints, or command a
mission. It is expected to run while a separate takeoff-hover-land gate is
active.
"""

from __future__ import annotations

import argparse
import json
import math
import signal
import time
from pathlib import Path
from typing import Any

import rospy
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import State
from nav_msgs.msg import Odometry
from sunray_msgs.msg import PX4State


def stamp_to_sec(stamp: Any) -> float | None:
    try:
        return float(stamp.secs) + float(stamp.nsecs) * 1e-9
    except Exception:
        return None


def yaw_from_quat(q: Any) -> float:
    x, y, z, w = float(q.x), float(q.y), float(q.z), float(q.w)
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


def angle_diff(a: float, b: float) -> float:
    return math.atan2(math.sin(a - b), math.cos(a - b))


def pos_tuple(p: Any) -> tuple[float, float, float]:
    return float(p.x), float(p.y), float(p.z)


def dist(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def gap_stats(values: list[float]) -> dict[str, Any]:
    if len(values) < 2:
        return {"count": len(values)}
    gaps = [b - a for a, b in zip(values, values[1:])]
    negative_gaps = [gap for gap in gaps if gap < -1e-6]
    elapsed = values[-1] - values[0]
    return {
        "count": len(values),
        "avg_hz": (len(values) - 1) / elapsed if elapsed > 0 else None,
        "min_gap_s": min(gaps),
        "max_gap_s": max(gaps),
        "negative_gap_count": len(negative_gaps),
        "max_negative_gap_s": min(negative_gaps) if negative_gaps else 0.0,
        "first": values[0],
        "last": values[-1],
    }


def scalar_stats(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0}
    values_sorted = sorted(values)
    p95_idx = min(len(values_sorted) - 1, int(math.ceil(0.95 * len(values_sorted))) - 1)
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": sum(values) / len(values),
        "p95": values_sorted[p95_idx],
    }


class TopicStats:
    def __init__(self) -> None:
        self.wall: list[float] = []
        self.header: list[float] = []
        self.frames: set[str] = set()
        self.children: set[str] = set()

    def add(self, stamp: float | None = None, frame: str = "", child: str = "") -> None:
        self.wall.append(time.time())
        if stamp is not None:
            self.header.append(stamp)
        if frame:
            self.frames.add(frame)
        if child:
            self.children.add(child)

    def summary(self) -> dict[str, Any]:
        return {
            "wall_stats": gap_stats(self.wall),
            "header_stats": gap_stats(self.header),
            "unique_frame_ids": sorted(self.frames),
            "unique_child_frame_ids": sorted(self.children),
        }


class Goal3FusionRecorder:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.stop_requested = False
        self.topic_stats: dict[str, TopicStats] = {}
        self.latest_aligned: Odometry | None = None
        self.latest_local: Odometry | None = None
        self.latest_vision: PoseStamped | None = None
        self.latest_truth: Odometry | None = None
        self.latest_px4_state: PX4State | None = None
        self.latest_mavros_state: State | None = None
        self.fusion_success: list[bool] = []
        self.odom_valid: list[bool] = []
        self.armed: list[bool] = []
        self.aligned_vs_vision_pos: list[float] = []
        self.aligned_vs_local_pos: list[float] = []
        self.vision_vs_local_pos: list[float] = []
        self.aligned_vs_truth_pos: list[float] = []
        self.local_vs_truth_pos: list[float] = []
        self.aligned_vs_local_yaw: list[float] = []
        self.vision_vs_local_yaw: list[float] = []

    def ts(self, name: str) -> TopicStats:
        return self.topic_stats.setdefault(name, TopicStats())

    def add_odom_stat(self, name: str, msg: Odometry) -> None:
        self.ts(name).add(stamp_to_sec(msg.header.stamp), msg.header.frame_id, msg.child_frame_id)

    def add_pose_stat(self, name: str, msg: PoseStamped) -> None:
        self.ts(name).add(stamp_to_sec(msg.header.stamp), msg.header.frame_id, "")

    def on_aligned(self, msg: Odometry) -> None:
        self.latest_aligned = msg
        self.add_odom_stat("fastlio_aligned_odom", msg)
        self.compare_latest()

    def on_local(self, msg: Odometry) -> None:
        self.latest_local = msg
        self.add_odom_stat("mavros_local_odom", msg)
        self.compare_latest()

    def on_vision(self, msg: PoseStamped) -> None:
        self.latest_vision = msg
        self.add_pose_stat("mavros_vision_pose", msg)
        self.compare_latest()

    def on_truth(self, msg: Odometry) -> None:
        self.latest_truth = msg
        self.add_odom_stat("sunray_gazebo_truth", msg)
        self.compare_latest()

    def on_px4_state(self, msg: PX4State) -> None:
        self.latest_px4_state = msg
        self.ts("sunray_px4_state").add(stamp_to_sec(msg.header.stamp), "", "")
        self.fusion_success.append(bool(msg.external_odom.fusion_success))
        self.odom_valid.append(bool(msg.external_odom.odom_valid))
        self.armed.append(bool(msg.armed))

    def on_mavros_state(self, msg: State) -> None:
        self.latest_mavros_state = msg
        self.ts("mavros_state").add(None, "", "")
        self.armed.append(bool(msg.armed))

    def compare_latest(self) -> None:
        aligned = self.latest_aligned
        local = self.latest_local
        vision = self.latest_vision
        truth = self.latest_truth
        if aligned is not None and vision is not None:
            self.aligned_vs_vision_pos.append(dist(pos_tuple(aligned.pose.pose.position), pos_tuple(vision.pose.position)))
        if aligned is not None and local is not None:
            self.aligned_vs_local_pos.append(dist(pos_tuple(aligned.pose.pose.position), pos_tuple(local.pose.pose.position)))
            self.aligned_vs_local_yaw.append(
                abs(angle_diff(yaw_from_quat(aligned.pose.pose.orientation), yaw_from_quat(local.pose.pose.orientation)))
            )
        if vision is not None and local is not None:
            self.vision_vs_local_pos.append(dist(pos_tuple(vision.pose.position), pos_tuple(local.pose.pose.position)))
            self.vision_vs_local_yaw.append(
                abs(angle_diff(yaw_from_quat(vision.pose.orientation), yaw_from_quat(local.pose.pose.orientation)))
            )
        if aligned is not None and truth is not None:
            self.aligned_vs_truth_pos.append(dist(pos_tuple(aligned.pose.pose.position), pos_tuple(truth.pose.pose.position)))
        if local is not None and truth is not None:
            self.local_vs_truth_pos.append(dist(pos_tuple(local.pose.pose.position), pos_tuple(truth.pose.pose.position)))

    def request_stop(self, _signum: int, _frame: Any) -> None:
        self.stop_requested = True

    def run(self) -> dict[str, Any]:
        rospy.init_node("mosim_fastlio_ekf_fusion_goal3_recorder", anonymous=True, disable_signals=True)
        signal.signal(signal.SIGTERM, self.request_stop)
        signal.signal(signal.SIGINT, self.request_stop)
        subscribers = [
            rospy.Subscriber(self.args.aligned_odom_topic, Odometry, self.on_aligned, queue_size=100),
            rospy.Subscriber(self.args.local_odom_topic, Odometry, self.on_local, queue_size=100),
            rospy.Subscriber(self.args.vision_pose_topic, PoseStamped, self.on_vision, queue_size=100),
            rospy.Subscriber(self.args.truth_topic, Odometry, self.on_truth, queue_size=100),
            rospy.Subscriber(self.args.px4_state_topic, PX4State, self.on_px4_state, queue_size=100),
            rospy.Subscriber(self.args.mavros_state_topic, State, self.on_mavros_state, queue_size=50),
        ]
        start = time.time()
        while not self.stop_requested and not rospy.is_shutdown() and time.time() - start < self.args.duration_s:
            time.sleep(0.05)
        for subscriber in subscribers:
            subscriber.unregister()
        return self.summary(time.time() - start, interrupted=self.stop_requested)

    def summary(self, duration_wall_s: float, interrupted: bool = False) -> dict[str, Any]:
        topics = {name: stats.summary() for name, stats in self.topic_stats.items()}
        negative_header_gaps = {
            name: data.get("header_stats", {}).get("negative_gap_count", 0)
            for name, data in topics.items()
        }
        comparisons = {
            "aligned_vs_vision_position_m": scalar_stats(self.aligned_vs_vision_pos),
            "aligned_vs_local_position_m": scalar_stats(self.aligned_vs_local_pos),
            "vision_vs_local_position_m": scalar_stats(self.vision_vs_local_pos),
            "aligned_vs_truth_position_m": scalar_stats(self.aligned_vs_truth_pos),
            "local_vs_truth_position_m": scalar_stats(self.local_vs_truth_pos),
            "aligned_vs_local_yaw_rad": scalar_stats(self.aligned_vs_local_yaw),
            "vision_vs_local_yaw_rad": scalar_stats(self.vision_vs_local_yaw),
        }
        checks = {
            "aligned_odom_present": topics.get("fastlio_aligned_odom", {}).get("wall_stats", {}).get("count", 0) > 0,
            "vision_pose_present": topics.get("mavros_vision_pose", {}).get("wall_stats", {}).get("count", 0) > 0,
            "px4_state_present": topics.get("sunray_px4_state", {}).get("wall_stats", {}).get("count", 0) > 0,
            "local_odom_present": topics.get("mavros_local_odom", {}).get("wall_stats", {}).get("count", 0) > 0,
            "truth_present": topics.get("sunray_gazebo_truth", {}).get("wall_stats", {}).get("count", 0) > 0,
            "aligned_frame_world": "world" in topics.get("fastlio_aligned_odom", {}).get("unique_frame_ids", []),
            "aligned_child_base_link": "base_link" in topics.get("fastlio_aligned_odom", {}).get("unique_child_frame_ids", []),
            "external_odom_valid_seen": any(self.odom_valid),
            "external_odom_valid_last": self.odom_valid[-1] if self.odom_valid else False,
            "fusion_success_seen": any(self.fusion_success),
            "fusion_success_ratio": (sum(1 for v in self.fusion_success if v) / len(self.fusion_success)) if self.fusion_success else None,
            "fusion_success_last": self.fusion_success[-1] if self.fusion_success else False,
            "armed_seen": any(self.armed),
            "negative_header_gaps": negative_header_gaps,
        }
        gate_pass = (
            checks["aligned_odom_present"]
            and checks["vision_pose_present"]
            and checks["px4_state_present"]
            and checks["local_odom_present"]
            and checks["truth_present"]
            and checks["aligned_frame_world"]
            and checks["aligned_child_base_link"]
            and checks["external_odom_valid_seen"]
            and checks["fusion_success_seen"]
            and all(count == 0 for count in negative_header_gaps.values())
        )
        return {
            "schema": "mosim.sunray_ros1.fastlio_ekf_fusion_goal3.v1",
            "status": "passed" if gate_pass else "blocked",
            "duration_requested_s": self.args.duration_s,
            "duration_wall_s": duration_wall_s,
            "interrupted": interrupted,
            "topics": topics,
            "comparisons": comparisons,
            "checks": checks,
            "gate_pass": gate_pass,
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-s", type=float, default=120.0)
    parser.add_argument("--out", required=True)
    parser.add_argument("--aligned-odom-topic", default="/mosim/fastlio/odom_aligned")
    parser.add_argument("--local-odom-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--vision-pose-topic", default="/uav1/mavros/vision_pose/pose")
    parser.add_argument("--truth-topic", default="/uav1/sunray/gazebo_pose")
    parser.add_argument("--px4-state-topic", default="/uav1/sunray/px4_state")
    parser.add_argument("--mavros-state-topic", default="/uav1/mavros/state")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = Goal3FusionRecorder(args).run()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["gate_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
