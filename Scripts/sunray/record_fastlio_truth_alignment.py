#!/usr/bin/env python3
"""Record ROS1 FAST-LIO odometry against Sunray Gazebo truth.

This is localization-only evidence. It does not publish setpoints or feed the
estimator into PX4.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Optional

import rospy
from nav_msgs.msg import Odometry

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from fastlio_frame_transform import Pose3, livox_pose_to_base_pose, quat_from_rpy  # noqa: E402


class Recorder:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.mount_pose = Pose3(args.mount_xyz, quat_from_rpy(*args.mount_rpy))
        self.latest_fastlio: Optional[Odometry] = None
        self.latest_truth: Optional[Odometry] = None
        self.rows: list[dict] = []
        self.start_wall = time.time()
        rospy.Subscriber(args.fastlio_topic, Odometry, self.on_fastlio, queue_size=50)
        rospy.Subscriber(args.truth_topic, Odometry, self.on_truth, queue_size=50)

    def now(self) -> float:
        t = rospy.Time.now().to_sec()
        if t > 0:
            return float(t)
        return time.time() - self.start_wall

    @staticmethod
    def pose_from_odom(msg: Odometry) -> Pose3:
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        return Pose3((float(p.x), float(p.y), float(p.z)), (float(q.x), float(q.y), float(q.z), float(q.w)))

    def fastlio_base_pose(self, msg: Odometry) -> Pose3:
        pose = self.pose_from_odom(msg)
        if self.args.fastlio_pose_frame == "livox":
            return livox_pose_to_base_pose(pose, self.mount_pose)
        return pose

    def on_fastlio(self, msg: Odometry) -> None:
        self.latest_fastlio = msg

    def on_truth(self, msg: Odometry) -> None:
        self.latest_truth = msg

    @staticmethod
    def dist(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    @staticmethod
    def rmse(values: list[float]) -> float | None:
        if not values:
            return None
        return math.sqrt(sum(v * v for v in values) / len(values))

    def snapshot(self) -> None:
        if self.latest_fastlio is None or self.latest_truth is None:
            return
        fast = self.fastlio_base_pose(self.latest_fastlio)
        truth = self.pose_from_odom(self.latest_truth)
        row = {
            "t": self.now(),
            "fastlio_frame_id": self.latest_fastlio.header.frame_id,
            "fastlio_child_frame_id": self.latest_fastlio.child_frame_id,
            "truth_frame_id": self.latest_truth.header.frame_id,
            "truth_child_frame_id": self.latest_truth.child_frame_id,
            "fastlio_base_position_m": list(fast.p),
            "truth_base_position_m": list(truth.p),
            "direct_error_m": self.dist(fast.p, truth.p),
        }
        self.rows.append(row)

    def summarize(self) -> dict:
        direct = [float(row["direct_error_m"]) for row in self.rows]
        origin_aligned: list[float] = []
        first_offset = None
        if self.rows:
            first_fast = self.rows[0]["fastlio_base_position_m"]
            first_truth = self.rows[0]["truth_base_position_m"]
            first_offset = [float(first_fast[i]) - float(first_truth[i]) for i in range(3)]
            for row in self.rows:
                fast = row["fastlio_base_position_m"]
                truth = row["truth_base_position_m"]
                shifted = tuple(float(fast[i]) - first_offset[i] for i in range(3))
                origin_aligned.append(self.dist(shifted, tuple(float(v) for v in truth)))
        return {
            "schema": "mosim.sunray_ros1.fastlio_truth_alignment.v1",
            "status": "recorded",
            "claim": "FAST-LIO localization comparison only; no controller state-source switch",
            "fastlio_topic": self.args.fastlio_topic,
            "truth_topic": self.args.truth_topic,
            "fastlio_pose_frame": self.args.fastlio_pose_frame,
            "samples": len(self.rows),
            "first_direct_offset_m": first_offset,
            "direct_rmse_m": self.rmse(direct),
            "direct_max_m": max(direct) if direct else None,
            "origin_aligned_rmse_m": self.rmse(origin_aligned),
            "origin_aligned_max_m": max(origin_aligned) if origin_aligned else None,
            "first_row": self.rows[0] if self.rows else None,
            "last_row": self.rows[-1] if self.rows else None,
        }

    def run(self) -> None:
        out_dir = Path(self.args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        deadline = time.time() + self.args.duration_s
        rate = rospy.Rate(self.args.sample_rate_hz)
        while not rospy.is_shutdown() and time.time() < deadline:
            self.snapshot()
            rate.sleep()
        (out_dir / "fastlio_truth_alignment_samples.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in self.rows),
            encoding="utf-8",
        )
        summary = self.summarize()
        (out_dir / "FASTLIO_TRUTH_ALIGNMENT.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(summary, ensure_ascii=False, indent=2))


def parse_vec3(text: str) -> tuple[float, float, float]:
    parts = [p for p in text.replace(",", " ").split() if p]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(f"expected 3 floats, got {text!r}")
    return float(parts[0]), float(parts[1]), float(parts[2])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--duration-s", type=float, default=60.0)
    parser.add_argument("--sample-rate-hz", type=float, default=20.0)
    parser.add_argument("--fastlio-topic", default="/Odometry")
    parser.add_argument("--truth-topic", default="/uav1/sunray/gazebo_pose")
    parser.add_argument("--fastlio-pose-frame", choices=["base", "livox"], default="livox")
    parser.add_argument("--mount-xyz", type=parse_vec3, default=(-0.000005, 0.032295, 0.050167))
    parser.add_argument("--mount-rpy", type=parse_vec3, default=(0.0, 0.0, 4.712389))
    args = parser.parse_args()
    rospy.init_node("mosim_fastlio_truth_alignment_recorder", anonymous=True, disable_signals=True)
    Recorder(args).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
