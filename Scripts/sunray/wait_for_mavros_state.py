#!/usr/bin/env python3
"""Wait for a MAVROS State topic to report connected=True."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import rospy
from mavros_msgs.msg import State


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", default="/uav1/mavros/state")
    parser.add_argument("--timeout-s", type=float, default=60.0)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    last_msg: State | None = None

    def callback(msg: State) -> None:
        nonlocal last_msg
        last_msg = msg

    rospy.init_node("mosim_wait_for_mavros_state", anonymous=True, disable_signals=True)
    rospy.Subscriber(args.topic, State, callback, queue_size=10)

    deadline = time.time() + args.timeout_s
    while not rospy.is_shutdown() and time.time() < deadline:
        if last_msg is not None and last_msg.connected:
            output.write_text(format_state(last_msg), encoding="utf-8")
            return 0
        # MAVROS connection timeout must remain wall-clock bounded before Gazebo publishes /clock.
        time.sleep(0.05)

    if last_msg is not None:
        output.write_text(format_state(last_msg), encoding="utf-8")
    else:
        output.write_text("", encoding="utf-8")
    return 1


def format_state(msg: State) -> str:
    return (
        f"connected: {bool(msg.connected)}\n"
        f"armed: {bool(msg.armed)}\n"
        f"guided: {bool(msg.guided)}\n"
        f"manual_input: {bool(msg.manual_input)}\n"
        f"mode: {msg.mode}\n"
        f"system_status: {int(msg.system_status)}\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
