#!/usr/bin/env python3
"""Record header-stamp and receive-time rates for a ROS2 topic.

This is a diagnostic helper for simulated sensors. ``ros2 topic hz`` measures
subscriber receive rate, which can drop when Gazebo/WSL is overloaded. This
script also records the rate implied by message ``header.stamp`` so sensor
configuration and runtime performance can be separated in evidence.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Any


def stamp_to_seconds(stamp: Any) -> float | None:
    sec = getattr(stamp, "sec", None)
    nanosec = getattr(stamp, "nanosec", None)
    if sec is None or nanosec is None:
        return None
    try:
        return float(sec) + float(nanosec) * 1e-9
    except (TypeError, ValueError):
        return None


def mean_rate(times: list[float]) -> dict[str, Any]:
    if len(times) < 2:
        return {
            "sample_count": len(times),
            "duration_s": 0.0,
            "average_rate_hz": None,
            "min_delta_s": None,
            "max_delta_s": None,
            "negative_delta_count": 0,
        }
    deltas = [b - a for a, b in zip(times, times[1:])]
    positive = [item for item in deltas if item > 0]
    duration = times[-1] - times[0]
    rate = (len(times) - 1) / duration if duration > 0 else None
    return {
        "sample_count": len(times),
        "duration_s": duration,
        "average_rate_hz": rate if rate is not None and math.isfinite(rate) else None,
        "min_delta_s": min(deltas),
        "max_delta_s": max(deltas),
        "positive_delta_count": len(positive),
        "negative_delta_count": sum(1 for item in deltas if item < 0),
        "zero_delta_count": sum(1 for item in deltas if item == 0),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--type", dest="msg_type", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--target-samples", type=int, default=40)
    parser.add_argument("--timeout-seconds", type=float, default=15.0)
    args = parser.parse_args()

    if args.target_samples <= 0:
        raise SystemExit("--target-samples must be positive")
    if args.timeout_seconds <= 0:
        raise SystemExit("--timeout-seconds must be positive")

    import rclpy  # type: ignore
    from rosidl_runtime_py.utilities import get_message  # type: ignore

    msg_cls = get_message(args.msg_type)
    rclpy.init()
    node = rclpy.create_node("mosim_record_topic_header_rate")

    header_times: list[float] = []
    receive_times: list[float] = []
    frame_ids: list[str] = []

    def on_msg(msg: Any) -> None:
        receive_times.append(time.monotonic())
        header = getattr(msg, "header", None)
        stamp_s = stamp_to_seconds(getattr(header, "stamp", None))
        if stamp_s is not None:
            header_times.append(stamp_s)
        frame_id = getattr(header, "frame_id", None)
        if isinstance(frame_id, str) and frame_id and frame_id not in frame_ids:
            frame_ids.append(frame_id)

    node.create_subscription(msg_cls, args.topic, on_msg, 10)

    deadline = time.monotonic() + args.timeout_seconds
    while rclpy.ok() and time.monotonic() < deadline and len(receive_times) < args.target_samples:
        rclpy.spin_once(node, timeout_sec=0.1)

    node.destroy_node()
    rclpy.shutdown()

    payload = {
        "schema": "mosim.ros2_topic_header_rate.v1",
        "status": "recorded" if receive_times else "no_samples",
        "topic": args.topic,
        "type": args.msg_type,
        "target_samples": args.target_samples,
        "timeout_seconds": args.timeout_seconds,
        "frame_ids": frame_ids,
        "header_stamp_rate": mean_rate(header_times),
        "receive_wall_rate": mean_rate(receive_times),
        "claim_boundary": [
            "header_stamp_rate measures message header time and is evidence for simulated sensor timestamp cadence",
            "receive_wall_rate measures subscriber receive cadence and can expose runtime/WSL/Gazebo performance bottlenecks",
            "this script does not prove localization, planner readiness, closed loop, or controller performance",
        ],
    }
    output = Path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if receive_times else 1


if __name__ == "__main__":
    raise SystemExit(main())
