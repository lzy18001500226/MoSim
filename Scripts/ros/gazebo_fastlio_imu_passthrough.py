#!/usr/bin/env python3
"""Lightweight IMU passthrough for FAST-LIO/planner input gates.

The point-cloud side of the Gazebo FAST-LIO/planner adapter performs heavier
PointCloud2 conversion work. This node keeps the high-rate IMU path in a
separate process so the 200 Hz IMU stream is not gated by LiDAR callback cost.
It does not launch FAST-LIO, publish setpoints, command motors, or claim
closed-loop behavior.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROS_LOG_DIR = ROOT / "Results" / "tmp" / "ros_logs"


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def ensure_ros_log_dir() -> None:
    log_dir = Path(os.environ.get("ROS_LOG_DIR", str(DEFAULT_ROS_LOG_DIR)))
    resolved = project_path(log_dir)
    resolved.mkdir(parents=True, exist_ok=True)
    os.environ["ROS_LOG_DIR"] = str(resolved)


def repo_path(value: str | Path | None) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def write_json(path: str | Path | None, payload: dict[str, Any]) -> None:
    output = repo_path(path)
    if output is None:
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: str | Path | None, payload: dict[str, Any]) -> None:
    output = repo_path(path)
    if output is None:
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def clone_imu_with_frame(source: Any, output_frame: str | None = None) -> Any:
    from sensor_msgs.msg import Imu

    output = Imu()
    output.header = source.header
    if output_frame:
        output.header.frame_id = output_frame
    output.orientation = source.orientation
    output.orientation_covariance = source.orientation_covariance
    output.angular_velocity = source.angular_velocity
    output.angular_velocity_covariance = source.angular_velocity_covariance
    output.linear_acceleration = source.linear_acceleration
    output.linear_acceleration_covariance = source.linear_acceleration_covariance
    return output


@dataclass
class RateTracker:
    count: int = 0
    first_at: float | None = None
    last_at: float | None = None

    def mark(self, now: float) -> None:
        if self.first_at is None:
            self.first_at = now
        self.last_at = now
        self.count += 1

    def average_hz(self) -> float | None:
        if self.first_at is None or self.last_at is None or self.count < 2:
            return None
        duration = self.last_at - self.first_at
        if duration <= 0.0:
            return None
        return (self.count - 1) / duration


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--imu-input-topic", default="/mosim/gazebo/imu")
    parser.add_argument("--fastlio-imu-topic", default="/mosim/fastlio/livox/imu")
    parser.add_argument("--sunray-imu-topic", default="/uav1/livox/imu")
    parser.add_argument("--imu-frame", default="sunray150_assembled/base_link/forward_imu")
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--trace-jsonl", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def claim_boundary() -> list[str]:
    return [
        "High-rate IMU passthrough only; no FAST-LIO node is launched",
        "IMU topic visibility and rate do not prove FAST-LIO localization success",
        "No planner_ready, setpoint publication, command authority, actuator command, or closed_loop claim",
        "This process is split from PointCloud2 conversion so IMU cadence is not LiDAR-gated",
    ]


def dry_run(args: argparse.Namespace) -> int:
    report = {
        "schema": "mosim.fastlio_imu_passthrough.dryrun.v1",
        "status": "dry_run_ready",
        "inputs": {
            "imu": args.imu_input_topic,
        },
        "outputs": {
            "fastlio_imu": args.fastlio_imu_topic,
            "sunray_imu": args.sunray_imu_topic,
        },
        "frames": {
            "imu_frame": args.imu_frame,
        },
        "claim_boundary": claim_boundary(),
    }
    write_json(args.output_json, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def run_node(args: argparse.Namespace) -> int:
    ensure_ros_log_dir()
    try:
        import rclpy
        from rclpy.node import Node
        from sensor_msgs.msg import Imu
    except Exception as exc:
        report = {
            "schema": "mosim.fastlio_imu_passthrough.v1",
            "status": "blocked",
            "error": f"{exc.__class__.__name__}: {exc}",
            "claim_boundary": claim_boundary(),
        }
        write_json(args.output_json, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    stop_requested = {"value": False}

    def request_stop(_signum: int, _frame: Any) -> None:
        stop_requested["value"] = True

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)

    rclpy.init()

    class FastlioImuPassthrough(Node):
        def __init__(self) -> None:
            super().__init__("mosim_gazebo_fastlio_imu_passthrough")
            self.started_at = time.time()
            self.last_report_write_at = 0.0
            self.last_report_status: str | None = None
            self.report_interval_s = 1.0
            self.counts = {
                "imu_received": 0,
                "fastlio_imu_published": 0,
                "sunray_imu_published": 0,
                "frame_mismatch_count": 0,
            }
            self.rate = RateTracker()
            self.fastlio_imu_pub = self.create_publisher(Imu, args.fastlio_imu_topic, 100)
            self.sunray_imu_pub = self.create_publisher(Imu, args.sunray_imu_topic, 100)
            self.create_subscription(Imu, args.imu_input_topic, self.handle_imu, 200)
            self.write_report("started", force=True)

        def handle_imu(self, message: Any) -> None:
            now = time.time()
            self.rate.mark(now)
            self.counts["imu_received"] += 1
            input_frame = str(message.header.frame_id)
            if args.imu_frame and input_frame != args.imu_frame:
                self.counts["frame_mismatch_count"] += 1
                if self.counts["frame_mismatch_count"] <= 5:
                    self.get_logger().warning(
                        f"IMU frame mismatch: expected {args.imu_frame!r}, got {input_frame!r}"
                    )
            output = clone_imu_with_frame(message, args.imu_frame or None)
            self.fastlio_imu_pub.publish(output)
            self.sunray_imu_pub.publish(output)
            self.counts["fastlio_imu_published"] += 1
            self.counts["sunray_imu_published"] += 1
            self.write_report("active")

        def write_report(self, status: str, force: bool = False) -> None:
            now = time.time()
            if (
                not force
                and self.last_report_status == status
                and now - self.last_report_write_at < self.report_interval_s
            ):
                return
            self.last_report_status = status
            self.last_report_write_at = now
            average_hz = self.rate.average_hz()
            report = {
                "schema": "mosim.fastlio_imu_passthrough.v1",
                "status": status,
                "node": "mosim_gazebo_fastlio_imu_passthrough",
                "uptime_s": round(now - self.started_at, 3),
                "inputs": {
                    "imu": args.imu_input_topic,
                },
                "outputs": {
                    "fastlio_imu": args.fastlio_imu_topic,
                    "sunray_imu": args.sunray_imu_topic,
                },
                "frames": {
                    "imu_frame": args.imu_frame,
                },
                "counts": self.counts,
                "observed_input_average_hz": round(average_hz, 3) if average_hz is not None else None,
                "claim_boundary": claim_boundary(),
            }
            write_json(args.output_json, report)
            append_jsonl(args.trace_jsonl, report)

    node = FastlioImuPassthrough()
    try:
        while rclpy.ok() and not stop_requested["value"]:
            rclpy.spin_once(node, timeout_sec=0.05)
    finally:
        node.write_report("stopped" if stop_requested["value"] else "shutdown", force=True)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return 0


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.dry_run:
        return dry_run(args)
    return run_node(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
