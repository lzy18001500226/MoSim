#!/usr/bin/env python3
"""Wait until a named Gazebo model appears in /gazebo/model_states."""

import argparse
import time

import rospy
from gazebo_msgs.msg import ModelStates


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="uav1")
    parser.add_argument("--timeout-s", type=float, default=180.0)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    seen = {"value": False}

    def callback(message: ModelStates) -> None:
        if args.model in message.name:
            seen["value"] = True

    rospy.init_node("mosim_wait_for_gazebo_model", anonymous=True)
    rospy.Subscriber("/gazebo/model_states", ModelStates, callback, queue_size=1)
    deadline = time.monotonic() + args.timeout_s
    while not rospy.is_shutdown() and time.monotonic() < deadline:
        if seen["value"]:
            with open(args.output, "w", encoding="utf-8") as stream:
                stream.write(f"model: {args.model}\nstatus: ready\n")
            return 0
        # Do not let a missing /clock suspend this wall-clock readiness probe.
        time.sleep(0.1)

    with open(args.output, "w", encoding="utf-8") as stream:
        stream.write(f"model: {args.model}\nstatus: timeout\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
