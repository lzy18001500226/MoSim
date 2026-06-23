#!/usr/bin/env python3
"""Record a ROS2 PoseArray truth topic as MoSim Gazebo truth JSONL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import rclpy
from geometry_msgs.msg import PoseArray
from rclpy.node import Node


ROOT = Path(__file__).resolve().parents[2]


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


class PoseArrayRecorder(Node):
    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__("mosim_pose_array_truth_recorder")
        self.args = args
        self.samples: list[dict[str, Any]] = []
        self.messages = 0
        self.subscription = self.create_subscription(PoseArray, args.topic, self.on_pose_array, 10)
        self.timer = self.create_timer(0.05, self.on_timer)
        self.start_time = self.get_clock().now()

    def on_pose_array(self, msg: PoseArray) -> None:
        self.messages += 1
        if not msg.poses:
            return
        pose = msg.poses[0]
        stamp = msg.header.stamp
        time_s = float(stamp.sec) + float(stamp.nanosec) * 1e-9
        if time_s == 0.0:
            time_s = len(self.samples) * 1e-6
            time_source = "synthetic_order"
        else:
            time_source = "header_stamp"
        self.samples.append(
            {
                "schema": "mosim.gazebo_pose_truth_sample.v1",
                "seq": len(self.samples),
                "time": round(time_s, 6),
                "time_source": time_source,
                "frame_id": self.args.frame_id or msg.header.frame_id or "world",
                "source_topic": self.args.topic,
                "model_name": self.args.model_name,
                "position_m": [
                    round(float(pose.position.x), 6),
                    round(float(pose.position.y), 6),
                    round(float(pose.position.z), 6),
                ],
                "orientation_xyzw": [
                    round(float(pose.orientation.x), 9),
                    round(float(pose.orientation.y), 9),
                    round(float(pose.orientation.z), 9),
                    round(float(pose.orientation.w), 9),
                ],
            }
        )

    def on_timer(self) -> None:
        elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
        if len(self.samples) >= self.args.target_samples or elapsed >= self.args.timeout_seconds:
            self.write_outputs()
            rclpy.shutdown()

    def write_outputs(self) -> None:
        output_jsonl = project_path(self.args.output_jsonl)
        summary_json = project_path(self.args.summary_json)
        output_jsonl.parent.mkdir(parents=True, exist_ok=True)
        summary_json.parent.mkdir(parents=True, exist_ok=True)
        with output_jsonl.open("w", encoding="utf-8", newline="\n") as handle:
            for index, sample in enumerate(self.samples):
                sample = dict(sample)
                sample["seq"] = index
                handle.write(json.dumps(sample, ensure_ascii=False, separators=(",", ":")) + "\n")
        summary = {
            "schema": "mosim.gazebo_pose_truth_recording.v1",
            "status": "recorded" if self.samples else "blocked_no_samples",
            "topic": self.args.topic,
            "model_name": self.args.model_name,
            "frame_id": self.args.frame_id,
            "count": len(self.samples),
            "messages_seen": self.messages,
            "capture_method": "ros2_pose_array_bridge",
            "timeout_seconds": self.args.timeout_seconds,
            "target_samples": self.args.target_samples,
            "time_sources": {
                "header_stamp": len([sample for sample in self.samples if sample.get("time_source") == "header_stamp"]),
                "synthetic_order": len([sample for sample in self.samples if sample.get("time_source") == "synthetic_order"]),
            },
            "outputs": {
                "truth_pose_jsonl": rel(output_jsonl),
            },
            "claim_boundary": [
                "ROS2 PoseArray truth bridged from Gazebo pose transport.",
                "This file is intended for same-run comparison and controller pre-acceptance only.",
            ],
        }
        summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-jsonl", required=True, type=Path)
    parser.add_argument("--summary-json", required=True, type=Path)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--model-name", default="sunray150_assembled")
    parser.add_argument("--frame-id", default="world")
    parser.add_argument("--timeout-seconds", type=float, default=15.0)
    parser.add_argument("--target-samples", type=int, default=50)
    args = parser.parse_args()

    rclpy.init()
    node = PoseArrayRecorder(args)
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        node.write_outputs()
    finally:
        node.destroy_node()
    return 0 if project_path(args.summary_json).exists() else 3


if __name__ == "__main__":
    raise SystemExit(main())
