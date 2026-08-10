#!/usr/bin/env python3
"""Wait for a nonempty ROS1 PointCloud2 sample and record compact evidence."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import rospy
from sensor_msgs.msg import PointCloud2


def write_result(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--timeout-s", type=float, default=60.0)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    output = Path(args.output)
    state: dict[str, object] = {
        "topic": args.topic,
        "samples_seen": 0,
        "last_width": 0,
        "last_height": 0,
        "last_data_bytes": 0,
    }

    def on_cloud(msg: PointCloud2) -> None:
        state["samples_seen"] = int(state["samples_seen"]) + 1
        state["last_width"] = int(msg.width)
        state["last_height"] = int(msg.height)
        state["last_data_bytes"] = len(msg.data)
        if msg.width > 0 and msg.height > 0 and len(msg.data) > 0:
            state.update(
                {
                    "status": "passed",
                    "frame_id": msg.header.frame_id,
                    "width": int(msg.width),
                    "height": int(msg.height),
                    "point_step": int(msg.point_step),
                    "row_step": int(msg.row_step),
                    "data_bytes": len(msg.data),
                    "stamp": {"secs": int(msg.header.stamp.secs), "nsecs": int(msg.header.stamp.nsecs)},
                }
            )

    try:
        rospy.init_node("mosim_wait_for_nonempty_pointcloud2", anonymous=True, disable_signals=True)
        rospy.Subscriber(args.topic, PointCloud2, on_cloud, queue_size=1)
        deadline = time.monotonic() + max(args.timeout_s, 0.0)
        rate = rospy.Rate(20)
        while (
            not rospy.is_shutdown()
            and state.get("status") != "passed"
            and time.monotonic() < deadline
        ):
            rate.sleep()
    except Exception as exc:  # rospy startup errors need to become actionable artifacts.
        state.update({"status": "error", "error": str(exc)})
        write_result(output, state)
        return 2

    if state.get("status") == "passed":
        write_result(output, state)
        return 0

    state.update(
        {
            "status": "timeout",
            "message": "No nonempty PointCloud2 message arrived before the deadline.",
        }
    )
    write_result(output, state)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
