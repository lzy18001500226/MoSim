#!/usr/bin/env python3
"""ROS2 node: ControllerOutput topic to Gazebo Actuators topic.

This is a bounded adapter for the MoSim ControllerOutput ABI. It publishes
Gazebo motor-speed commands only after receiving a ControllerOutput message.
It does not arm, publish trajectory setpoints, validate hover, or prove
closed-loop controller performance.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from controller_output_to_gazebo_actuators import (  # noqa: E402
    DEFAULT_ACTUATOR_ORDER,
    DEFAULT_GAZEBO_TURNING_DIRECTION,
    DEFAULT_MWORKS_SOURCE_ORDER,
    DEFAULT_SPIN_SIGN,
    AdapterConfig,
    AdapterError,
    build_report,
    validate_config,
)


DEFAULT_INPUT_TOPIC = "/mosim/sunray150/controller_output"
DEFAULT_OUTPUT_TOPIC = "/sunray150/gazebo/command/motor_speed"


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-topic", default=DEFAULT_INPUT_TOPIC)
    parser.add_argument("--output-topic", default=DEFAULT_OUTPUT_TOPIC)
    parser.add_argument("--vehicle-id", default="sunray150")
    parser.add_argument("--actuator-order", nargs=4, default=DEFAULT_ACTUATOR_ORDER)
    parser.add_argument("--mworks-source-order", nargs=4, default=DEFAULT_MWORKS_SOURCE_ORDER)
    parser.add_argument("--spin-sign", nargs=4, type=int, default=DEFAULT_SPIN_SIGN)
    parser.add_argument("--gazebo-turning-direction", nargs=4, default=DEFAULT_GAZEBO_TURNING_DIRECTION)
    parser.add_argument("--max-rot-velocity", type=float, default=8000.0)
    parser.add_argument("--normalized-max-rot-velocity", type=float, default=8000.0)
    parser.add_argument("--allow-signed-spin-mismatch", action="store_true")
    parser.add_argument("--max-command-age-s", type=float, default=0.0)
    parser.add_argument("--max-future-skew-s", type=float, default=0.5)
    parser.add_argument("--max-messages", type=int, default=1)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--trace-jsonl", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def adapter_config(args: argparse.Namespace) -> AdapterConfig:
    config = AdapterConfig(
        ros_topic=args.output_topic,
        gz_topic=args.output_topic,
        actuator_order=list(args.actuator_order),
        mworks_source_order=list(args.mworks_source_order),
        spin_sign=list(args.spin_sign),
        gazebo_turning_direction=list(args.gazebo_turning_direction),
        max_rot_velocity=args.max_rot_velocity,
        normalized_max_rot_velocity=args.normalized_max_rot_velocity,
        strict_signed_spin=not args.allow_signed_spin_mismatch,
        expected_vehicle_id=args.vehicle_id,
        required_status="valid",
        max_command_age_s=args.max_command_age_s,
        max_future_skew_s=args.max_future_skew_s,
        now_unix=None,
    )
    validate_config(config)
    return config


def message_to_dict(message: Any) -> dict[str, Any]:
    return {
        "schema": "mosim.controller_output_ros2_message.v1",
        "sequence": int(message.sequence),
        "vehicle_id": str(message.vehicle_id),
        "command_type": str(message.command_type),
        "command": [float(item) for item in message.command],
        "command_frame": str(message.command_frame),
        "mode": str(message.mode),
        "status": str(message.status),
        "backend": str(message.backend),
        "saturation": bool(message.saturation),
        "source_authority": str(message.source_authority),
        "issued_at_unix": float(message.header.stamp.sec) + float(message.header.stamp.nanosec) / 1_000_000_000.0,
    }


def write_json(path: Path | None, payload: dict[str, Any]) -> None:
    if path is None:
        return
    output = repo_path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path | None, payload: dict[str, Any]) -> None:
    if path is None:
        return
    output = repo_path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def dry_run_report(args: argparse.Namespace) -> dict[str, Any]:
    config = adapter_config(args)
    return {
        "schema": "mosim.controller_output_to_gazebo_actuators_node.dry_run.v1",
        "status": "ready",
        "input_topic": args.input_topic,
        "input_type": "mosim_msgs/msg/ControllerOutput",
        "output_topic": args.output_topic,
        "output_type": "actuator_msgs/msg/Actuators",
        "actuator_order": config.actuator_order,
        "mworks_source_order": config.mworks_source_order,
        "mworks_spin_command_sign": config.spin_sign,
        "gazebo_turning_direction": config.gazebo_turning_direction,
        "max_messages": args.max_messages,
        "max_command_age_s": args.max_command_age_s,
        "max_future_skew_s": args.max_future_skew_s,
        "claim_boundary": [
            "dry-run only; no ROS2 graph was touched",
            "the runtime node only maps ControllerOutput to Actuators",
            "when enabled, max_command_age_s rejects stale ControllerOutput messages before publishing Actuators",
            "no setpoint, planner_ready, closed_loop, hover, or controller performance is claimed",
        ],
    }


def run_node(args: argparse.Namespace) -> int:
    try:
        import rclpy
        from actuator_msgs.msg import Actuators
        from mosim_msgs.msg import ControllerOutput
        from rclpy.node import Node
    except Exception as exc:
        report = {
            "schema": "mosim.controller_output_to_gazebo_actuators_node.v1",
            "status": "blocked",
            "error": f"{exc.__class__.__name__}: {exc}",
            "input_topic": args.input_topic,
            "output_topic": args.output_topic,
            "claim_boundary": [
                "No Actuators message was published.",
                "This blocker does not prove or disprove Gazebo, hover, or controller performance.",
            ],
        }
        write_json(args.output_json, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    config = adapter_config(args)

    class ControllerOutputAdapter(Node):
        def __init__(self) -> None:
            super().__init__("mosim_controller_output_to_gazebo_actuators")
            self.received = 0
            self.last_report: dict[str, Any] | None = None
            self.publisher = self.create_publisher(Actuators, args.output_topic, 10)
            self.subscription = self.create_subscription(
                ControllerOutput,
                args.input_topic,
                self.handle_controller_output,
                10,
            )

        def handle_controller_output(self, message: Any) -> None:
            self.received += 1
            data = message_to_dict(message)
            try:
                report = build_report(data, config)
                output = Actuators()
                output.position = []
                output.velocity = [float(item) for item in report["velocity"]]
                output.normalized = []
                self.publisher.publish(output)
                report.update(
                    {
                        "schema": "mosim.controller_output_to_gazebo_actuators_node.v1",
                        "status": "published",
                        "node": "mosim_controller_output_to_gazebo_actuators",
                        "source_topic": args.input_topic,
                        "output_topic": args.output_topic,
                        "input_sequence": data["sequence"],
                        "input_vehicle_id": data["vehicle_id"],
                        "input_command": data["command"],
                        "input_status": data.get("status"),
                        "source_authority": data.get("source_authority"),
                        "metadata_policy": report.get("metadata_policy"),
                        "command_age_s": report.get("command_age_s"),
                        "published_at_unix": time.time(),
                    }
                )
            except Exception as exc:
                report = {
                    "schema": "mosim.controller_output_to_gazebo_actuators_node.v1",
                    "status": "blocked",
                    "node": "mosim_controller_output_to_gazebo_actuators",
                    "source_topic": args.input_topic,
                    "output_topic": args.output_topic,
                    "input_sequence": data.get("sequence"),
                    "input_vehicle_id": data.get("vehicle_id"),
                    "input_command_type": data.get("command_type"),
                    "input_command": data.get("command"),
                    "input_status": data.get("status"),
                    "source_authority": data.get("source_authority"),
                    "issued_at_unix": data.get("issued_at_unix"),
                    "max_command_age_s": args.max_command_age_s,
                    "error": f"{exc.__class__.__name__}: {exc}",
                    "claim_boundary": [
                        "No valid Actuators message was published for this ControllerOutput sample.",
                        "This blocker does not prove or disprove Gazebo, hover, or controller performance.",
                    ],
                }
            self.last_report = report
            write_json(args.output_json, report)
            append_jsonl(args.trace_jsonl, report)

    rclpy.init()
    node = ControllerOutputAdapter()
    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.2)
            if args.max_messages > 0 and node.received >= args.max_messages:
                break
    finally:
        last_report = node.last_report
        node.destroy_node()
        rclpy.shutdown()

    if last_report is None:
        report = {
            "schema": "mosim.controller_output_to_gazebo_actuators_node.v1",
            "status": "blocked",
            "error": "no ControllerOutput message received",
            "source_topic": args.input_topic,
            "output_topic": args.output_topic,
            "claim_boundary": [
                "No Actuators message was published.",
                "This blocker does not prove or disprove Gazebo, hover, or controller performance.",
            ],
        }
        write_json(args.output_json, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(last_report, ensure_ascii=False, indent=2))
    return 0 if last_report.get("status") == "published" else 1


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        if args.dry_run:
            report = dry_run_report(args)
            write_json(args.output_json, report)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0
        return run_node(args)
    except (AdapterError, ValueError) as exc:
        report = {
            "schema": "mosim.controller_output_to_gazebo_actuators_node.v1",
            "status": "blocked",
            "error": f"{exc.__class__.__name__}: {exc}",
        }
        write_json(args.output_json, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
