#!/usr/bin/env python3
"""Wait for one ROS1 topic sample and write it to a text file."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import rospy
import rostopic


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--timeout-s", type=float, default=10.0)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("", encoding="utf-8")

    rospy.init_node("mosim_wait_for_topic_sample", anonymous=True, disable_signals=True)
    deadline = time.time() + max(args.timeout_s, 0.0)
    topic_type = None
    while not rospy.is_shutdown() and time.time() < deadline:
        topic_type, _, _ = rostopic.get_topic_class(args.topic, blocking=False)
        if topic_type is not None:
            break
        time.sleep(0.1)
    if topic_type is None:
        output.write_text("topic_type_unavailable\n", encoding="utf-8")
        return 2

    remaining = max(0.1, deadline - time.time())
    try:
        msg = rospy.wait_for_message(args.topic, topic_type, timeout=remaining)
    except rospy.ROSException as exc:
        output.write_text(f"wait_timeout_or_error: {exc}\n", encoding="utf-8")
        return 1

    output.write_text(f"topic: {args.topic}\ntype: {topic_type._type}\n---\n{msg}\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
