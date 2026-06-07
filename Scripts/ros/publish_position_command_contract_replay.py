#!/usr/bin/env python3
"""Publish a B0 smoke-only PositionCommand contract replay stream.

This is not a planner and does not consume a local map. It exists only to
exercise the Sunray/EGO PositionCommand shape, converter, 20Hz adapter, and
passive recorder until a real B1 planner/runtime source is available.
"""

from __future__ import annotations

import argparse
import math
import time
from typing import Any


def make_stamp(stamp_type: Any, start_stamp_ns: int, elapsed_s: float) -> Any:
    stamp_ns = start_stamp_ns + int(elapsed_s * 1_000_000_000)
    stamp = stamp_type()
    stamp.sec = int(stamp_ns // 1_000_000_000)
    stamp.nanosec = int(stamp_ns % 1_000_000_000)
    return stamp


def fill_command(msg: Any, *, stamp: Any, t: float, sequence: int, frame_id: str) -> None:
    radius_m = 0.35
    omega = 0.45
    msg.header.stamp = stamp
    msg.header.frame_id = frame_id
    msg.position.x = radius_m * math.sin(omega * t)
    msg.position.y = radius_m * (1.0 - math.cos(omega * t))
    msg.position.z = 1.2 + 0.05 * math.sin(0.5 * omega * t)
    msg.velocity.x = radius_m * omega * math.cos(omega * t)
    msg.velocity.y = radius_m * omega * math.sin(omega * t)
    msg.velocity.z = 0.05 * 0.5 * omega * math.cos(0.5 * omega * t)
    msg.acceleration.x = -radius_m * omega * omega * math.sin(omega * t)
    msg.acceleration.y = radius_m * omega * omega * math.cos(omega * t)
    msg.acceleration.z = -0.05 * (0.5 * omega) ** 2 * math.sin(0.5 * omega * t)
    msg.yaw = math.atan2(msg.velocity.y, msg.velocity.x)
    msg.yaw_dot = omega
    msg.kx = [0.0, 0.0, 0.0]
    msg.kv = [0.0, 0.0, 0.0]
    msg.trajectory_id = sequence
    msg.trajectory_flag = 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", default="/position_cmd")
    parser.add_argument("--frame-id", default="world")
    parser.add_argument("--rate-hz", type=float, default=20.0)
    parser.add_argument("--duration-s", type=float, default=12.0)
    args = parser.parse_args()
    if args.rate_hz <= 0.0 or args.duration_s <= 0.0:
        raise SystemExit("rate-hz and duration-s must be positive")

    try:
        import rclpy
        from mosim_msgs.msg import PositionCommand
    except (ImportError, ModuleNotFoundError) as exc:
        raise SystemExit(
            "ROS2 Python environment is not available. Run this inside WSL after "
            "sourcing /opt/ros/humble/setup.bash and the MoSim ROS2 overlay "
            "(for example: source install/setup.bash)."
        ) from exc

    rclpy.init()
    node = rclpy.create_node("mosim_position_command_contract_replay_b0")
    pub = node.create_publisher(PositionCommand, args.topic, 10)
    period_s = 1.0 / float(args.rate_hz)
    start = time.monotonic()
    start_stamp_ns = int(node.get_clock().now().nanoseconds)
    next_tick = start
    sequence = 1
    try:
        while time.monotonic() - start < float(args.duration_s):
            msg = PositionCommand()
            elapsed_s = time.monotonic() - start
            fill_command(
                msg,
                stamp=make_stamp(type(msg.header.stamp), start_stamp_ns, elapsed_s),
                t=elapsed_s,
                sequence=sequence,
                frame_id=args.frame_id,
            )
            pub.publish(msg)
            sequence += 1
            rclpy.spin_once(node, timeout_sec=0.0)
            next_tick += period_s
            time.sleep(max(0.0, next_tick - time.monotonic()))
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
