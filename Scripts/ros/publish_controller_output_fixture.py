#!/usr/bin/env python3
"""Publish a bounded MoSim ControllerOutput fixture.

The fixture is for ROS2/Gazebo adapter handoff validation only. It does not
represent a flight controller, planner, or accepted control-performance run.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


DEFAULT_TOPIC = "/mosim/sunray150/controller_output"
DEFAULT_COMMAND = [0.5, 0.5, 0.5, 0.5]


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def finite_float_list(values: list[float]) -> list[float]:
    import math

    result = [float(item) for item in values]
    for index, value in enumerate(result):
        if not math.isfinite(value):
            raise ValueError(f"command[{index}] is not finite")
    return result


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", default=DEFAULT_TOPIC)
    parser.add_argument("--vehicle-id", default="sunray150")
    parser.add_argument("--command-type", default="normalized_motor_speed")
    parser.add_argument("--command", nargs="*", type=float, default=DEFAULT_COMMAND)
    parser.add_argument("--command-frame", default="body_motor_order_rotor_0_1_2_3")
    parser.add_argument("--mode", default="normal")
    parser.add_argument("--status", default="valid")
    parser.add_argument("--backend", default="fixture")
    parser.add_argument("--source-authority", default="bounded_fixture_no_flight_authority")
    parser.add_argument("--rate-hz", type=float, default=5.0)
    parser.add_argument("--times", type=int, default=5)
    parser.add_argument("--issued-at-unix", type=float)
    parser.add_argument("--stale-age-s", type=float, default=0.0)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def build_report(args: argparse.Namespace, published: int = 0) -> dict[str, Any]:
    command = finite_float_list(list(args.command))
    if len(command) != 4:
        raise ValueError("ControllerOutput fixture requires exactly four command values")
    if args.rate_hz <= 0:
        raise ValueError("--rate-hz must be positive")
    if args.times <= 0:
        raise ValueError("--times must be positive")
    issued_at_unix = args.issued_at_unix
    if issued_at_unix is None and args.stale_age_s > 0:
        issued_at_unix = time.time() - args.stale_age_s
    return {
        "schema": "mosim.controller_output_fixture_publisher.v1",
        "status": "dry_run_ready" if published == 0 else "published",
        "topic": args.topic,
        "type": "mosim_msgs/msg/ControllerOutput",
        "vehicle_id": args.vehicle_id,
        "command_type": args.command_type,
        "command": command,
        "command_frame": args.command_frame,
        "mode": args.mode,
        "message_status": args.status,
        "backend": args.backend,
        "source_authority": args.source_authority,
        "issued_at_unix": issued_at_unix,
        "stale_age_s": args.stale_age_s,
        "rate_hz": args.rate_hz,
        "times": args.times,
        "published_count": published,
        "claim_boundary": [
            "bounded fixture for ControllerOutput adapter handoff only",
            "does not arm, does not publish setpoints, does not prove hover, closed_loop, planner_ready, or controller performance",
        ],
    }


def write_json(path: Path | None, payload: dict[str, Any]) -> None:
    if path is None:
        return
    output = repo_path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_publisher(args: argparse.Namespace) -> int:
    try:
        import rclpy
        from mosim_msgs.msg import ControllerOutput
        from rclpy.node import Node
    except Exception as exc:
        report = {
            "schema": "mosim.controller_output_fixture_publisher.v1",
            "status": "blocked",
            "error": f"{exc.__class__.__name__}: {exc}",
            "topic": args.topic,
            "claim_boundary": [
                "No ControllerOutput message was published.",
                "This blocker does not prove or disprove Gazebo, hover, closed_loop, or controller performance.",
            ],
        }
        write_json(args.output_json, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    command = finite_float_list(list(args.command))
    issued_at_unix = args.issued_at_unix
    if issued_at_unix is None and args.stale_age_s > 0:
        issued_at_unix = time.time() - args.stale_age_s
    rclpy.init()

    class FixturePublisher(Node):
        def __init__(self) -> None:
            super().__init__("mosim_controller_output_fixture_publisher")
            self.publisher = self.create_publisher(ControllerOutput, args.topic, 10)

    node = FixturePublisher()
    published = 0
    try:
        # Allow discovery before the first bounded fixture sample.
        deadline = time.time() + 0.8
        while time.time() < deadline:
            rclpy.spin_once(node, timeout_sec=0.05)

        period = 1.0 / args.rate_hz
        for index in range(args.times):
            message = ControllerOutput()
            message.header.stamp = node.get_clock().now().to_msg()
            if issued_at_unix is not None:
                sec = int(issued_at_unix)
                nanosec = int(round((float(issued_at_unix) - sec) * 1_000_000_000))
                if nanosec >= 1_000_000_000:
                    sec += 1
                    nanosec -= 1_000_000_000
                message.header.stamp.sec = sec
                message.header.stamp.nanosec = nanosec
            message.header.frame_id = args.command_frame
            message.sequence = index + 1
            message.vehicle_id = args.vehicle_id
            message.command_type = args.command_type
            message.command = command
            message.command_frame = args.command_frame
            message.mode = args.mode
            message.status = args.status
            message.backend = args.backend
            message.saturation = False
            message.source_authority = args.source_authority
            node.publisher.publish(message)
            published += 1
            rclpy.spin_once(node, timeout_sec=0.05)
            time.sleep(period)
    finally:
        node.destroy_node()
        rclpy.shutdown()

    if issued_at_unix is not None:
        args.issued_at_unix = issued_at_unix
    report = build_report(args, published=published)
    write_json(args.output_json, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        if args.dry_run:
            report = build_report(args, published=0)
            write_json(args.output_json, report)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0
        return run_publisher(args)
    except Exception as exc:
        report = {
            "schema": "mosim.controller_output_fixture_publisher.v1",
            "status": "blocked",
            "error": f"{exc.__class__.__name__}: {exc}",
        }
        write_json(args.output_json, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
