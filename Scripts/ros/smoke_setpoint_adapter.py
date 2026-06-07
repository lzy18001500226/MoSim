#!/usr/bin/env python3
"""No-RViz smoke test for the MoSim planner setpoint adapter node."""

from __future__ import annotations

import argparse
import json
import signal
import subprocess
import sys
import time
from pathlib import Path

import rclpy
from mosim_msgs.msg import PlannerSetpoint, SetpointAdapterStatus


ROOT = Path(__file__).resolve().parents[2]


def make_command(node: rclpy.node.Node, sequence: int) -> PlannerSetpoint:
    msg = PlannerSetpoint()
    msg.header.stamp = node.get_clock().now().to_msg()
    msg.header.frame_id = "map"
    msg.sequence = sequence
    msg.frame_id = "map"
    msg.position_m = [0.0, 0.0, 1.2]
    msg.velocity_mps = [0.0, 0.0, 0.0]
    msg.acceleration_mps2 = [0.0, 0.0, 0.0]
    msg.yaw_rad = 0.0
    msg.yaw_rate_radps = 0.0
    msg.trajectory_status = 1
    msg.planner_id = "smoke"
    return msg


def terminate(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.send_signal(signal.SIGINT)
    try:
        process.wait(timeout=3.0)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=3.0)


def run_smoke(timeout_s: float, output: Path, log: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("wb") as log_file:
        process = subprocess.Popen(
            ["ros2", "run", "mosim_setpoint_adapter", "planner_setpoint_adapter_node"],
            stdout=log_file,
            stderr=subprocess.STDOUT,
        )
        try:
            time.sleep(2.0)
            result: dict[str, object] = {
                "published": False,
                "status_messages": [],
                "setpoint_messages": [],
                "adapter_returncode_before_cleanup": process.poll(),
            }

            rclpy.init()
            node = rclpy.create_node("mosim_setpoint_adapter_smoke_harness")

            status_messages: list[dict[str, object]] = []
            setpoint_messages: list[dict[str, object]] = []

            def on_status(msg: SetpointAdapterStatus) -> None:
                status_messages.append(
                    {
                        "accepted": bool(msg.accepted),
                        "mode": msg.mode,
                        "reject_reason": msg.reject_reason,
                        "stale": bool(msg.stale),
                        "last_sequence": int(msg.last_sequence),
                        "planner_id": msg.planner_id,
                        "age_s": float(msg.age_s),
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

            node.create_subscription(
                SetpointAdapterStatus,
                "/mosim/planner/setpoint_adapter_status",
                on_status,
                10,
            )
            node.create_subscription(
                PlannerSetpoint,
                "/mosim/planner/setpoint",
                on_setpoint,
                10,
            )
            pub = node.create_publisher(
                PlannerSetpoint,
                "/mosim/planner/position_cmd",
                10,
            )

            deadline = time.time() + timeout_s
            sequence = 1
            while time.time() < deadline and not setpoint_messages:
                command = make_command(node, sequence)
                command.header.stamp = node.get_clock().now().to_msg()
                pub.publish(command)
                result["published"] = True
                sequence += 1
                rclpy.spin_once(node, timeout_sec=0.1)
                time.sleep(0.05)

            while time.time() < deadline and not any(
                item["accepted"] and item["mode"] == "track" for item in status_messages
            ):
                rclpy.spin_once(node, timeout_sec=0.1)

            result["status_messages"] = status_messages
            result["setpoint_messages"] = setpoint_messages
            result["status_count"] = len(status_messages)
            result["setpoint_count"] = len(setpoint_messages)
            result["pass"] = bool(setpoint_messages) and any(
                item["accepted"]
                and item["mode"] == "track"
                and item["planner_id"] == "smoke"
                for item in status_messages
            )
            node.destroy_node()
            rclpy.shutdown()
            output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["pass"] else 2
        finally:
            terminate(process)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout-s", type=float, default=8.0)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "Results" / "tmp" / "mosim_setpoint_adapter_smoke.json",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=ROOT / "Results" / "tmp" / "mosim_setpoint_adapter_node.log",
    )
    args = parser.parse_args()
    return run_smoke(args.timeout_s, args.output, args.log)


if __name__ == "__main__":
    raise SystemExit(main())
