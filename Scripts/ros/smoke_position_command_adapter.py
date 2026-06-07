#!/usr/bin/env python3
"""No-RViz smoke test for PositionCommand -> PlannerSetpoint -> 20Hz adapter."""

from __future__ import annotations

import argparse
import json
import signal
import subprocess
import time
from pathlib import Path

import rclpy
from mosim_msgs.msg import PlannerSetpoint, PositionCommand, SetpointAdapterStatus


ROOT = Path(__file__).resolve().parents[2]


def terminate(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.send_signal(signal.SIGINT)
    try:
        process.wait(timeout=3.0)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=3.0)


def make_position_command(node: rclpy.node.Node, trajectory_id: int) -> PositionCommand:
    msg = PositionCommand()
    msg.header.stamp = node.get_clock().now().to_msg()
    msg.header.frame_id = "world"
    msg.position.x = 0.0
    msg.position.y = 0.0
    msg.position.z = 1.2
    msg.velocity.x = 0.0
    msg.velocity.y = 0.0
    msg.velocity.z = 0.0
    msg.acceleration.x = 0.0
    msg.acceleration.y = 0.0
    msg.acceleration.z = 0.0
    msg.yaw = 0.0
    msg.yaw_dot = 0.0
    msg.kx = [0.0, 0.0, 0.0]
    msg.kv = [0.0, 0.0, 0.0]
    msg.trajectory_id = trajectory_id
    msg.trajectory_flag = 1
    return msg


def run_smoke(timeout_s: float, output: Path, converter_log: Path, adapter_log: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    converter_log.parent.mkdir(parents=True, exist_ok=True)
    adapter_log.parent.mkdir(parents=True, exist_ok=True)
    with converter_log.open("wb") as converter_log_file, adapter_log.open("wb") as adapter_log_file:
        converter = subprocess.Popen(
            [
                "ros2",
                "run",
                "mosim_setpoint_adapter",
                "position_command_to_planner_setpoint_node",
            ],
            stdout=converter_log_file,
            stderr=subprocess.STDOUT,
        )
        adapter = subprocess.Popen(
            ["ros2", "run", "mosim_setpoint_adapter", "planner_setpoint_adapter_node"],
            stdout=adapter_log_file,
            stderr=subprocess.STDOUT,
        )
        try:
            time.sleep(2.0)
            result: dict[str, object] = {
                "published": False,
                "converted_messages": [],
                "setpoint_messages": [],
                "status_messages": [],
                "converter_returncode_before_cleanup": converter.poll(),
                "adapter_returncode_before_cleanup": adapter.poll(),
            }
            rclpy.init()
            node = rclpy.create_node("mosim_position_command_adapter_smoke_harness")
            converted_messages: list[dict[str, object]] = []
            setpoint_messages: list[dict[str, object]] = []
            status_messages: list[dict[str, object]] = []

            def on_converted(msg: PlannerSetpoint) -> None:
                converted_messages.append(
                    {
                        "sequence": int(msg.sequence),
                        "frame_id": msg.frame_id,
                        "planner_id": msg.planner_id,
                        "position_m": [float(v) for v in msg.position_m],
                    }
                )

            def on_setpoint(msg: PlannerSetpoint) -> None:
                setpoint_messages.append(
                    {
                        "sequence": int(msg.sequence),
                        "frame_id": msg.frame_id,
                        "planner_id": msg.planner_id,
                        "position_m": [float(v) for v in msg.position_m],
                    }
                )

            def on_status(msg: SetpointAdapterStatus) -> None:
                status_messages.append(
                    {
                        "accepted": bool(msg.accepted),
                        "mode": msg.mode,
                        "reject_reason": msg.reject_reason,
                        "stale": bool(msg.stale),
                        "last_sequence": int(msg.last_sequence),
                        "planner_id": msg.planner_id,
                    }
                )

            node.create_subscription(PlannerSetpoint, "/mosim/planner/position_cmd", on_converted, 10)
            node.create_subscription(PlannerSetpoint, "/mosim/planner/setpoint", on_setpoint, 10)
            node.create_subscription(SetpointAdapterStatus, "/mosim/planner/setpoint_adapter_status", on_status, 10)
            pub = node.create_publisher(PositionCommand, "/position_cmd", 10)
            deadline = time.time() + timeout_s
            trajectory_id = 1
            while time.time() < deadline and not setpoint_messages:
                pub.publish(make_position_command(node, trajectory_id))
                result["published"] = True
                trajectory_id += 1
                rclpy.spin_once(node, timeout_sec=0.1)
                time.sleep(0.05)
            while time.time() < deadline and not any(
                item["accepted"] and item["mode"] == "track" for item in status_messages
            ):
                rclpy.spin_once(node, timeout_sec=0.1)

            result["converted_messages"] = converted_messages
            result["setpoint_messages"] = setpoint_messages
            result["status_messages"] = status_messages
            result["converted_count"] = len(converted_messages)
            result["setpoint_count"] = len(setpoint_messages)
            result["status_count"] = len(status_messages)
            result["pass"] = (
                bool(converted_messages)
                and bool(setpoint_messages)
                and any(
                    item["accepted"] and item["mode"] == "track" and item["planner_id"] == "ego_position_cmd"
                    for item in status_messages
                )
            )
            node.destroy_node()
            rclpy.shutdown()
            output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["pass"] else 2
        finally:
            terminate(adapter)
            terminate(converter)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout-s", type=float, default=8.0)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "Results" / "tmp" / "mosim_position_command_adapter_smoke.json",
    )
    parser.add_argument(
        "--converter-log",
        type=Path,
        default=ROOT / "Results" / "tmp" / "mosim_position_command_converter_node.log",
    )
    parser.add_argument(
        "--adapter-log",
        type=Path,
        default=ROOT / "Results" / "tmp" / "mosim_position_command_adapter_node.log",
    )
    args = parser.parse_args()
    return run_smoke(args.timeout_s, args.output, args.converter_log, args.adapter_log)


if __name__ == "__main__":
    raise SystemExit(main())
