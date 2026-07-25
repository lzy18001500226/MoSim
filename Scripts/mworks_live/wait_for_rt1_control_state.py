#!/usr/bin/env python3
"""Wait for a run-matched RT1 control-owner state before mission start."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--expected-state", default="ACTIVE")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--timeout-s", type=float, default=30.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    import rospy
    from std_msgs.msg import String

    observed: dict[str, Any] = {}

    def callback(message: String) -> None:
        nonlocal observed
        try:
            value = json.loads(message.data)
        except (TypeError, ValueError):
            return
        if isinstance(value, dict):
            observed = value

    rospy.init_node("mosim_wait_for_rt1_control_state", anonymous=True, disable_signals=True)
    subscriber = rospy.Subscriber(args.topic, String, callback, queue_size=2)
    started = time.monotonic()
    accepted = False
    reason_code = "control_owner_timeout"
    while not rospy.is_shutdown() and time.monotonic() - started < args.timeout_s:
        run_matches = not args.run_id or observed.get("run_id") == args.run_id
        if run_matches and observed.get("state") == args.expected_state:
            accepted = True
            reason_code = "control_owner_ready"
            break
        # This gate must expire in wall time even when Gazebo is paused or its
        # /clock publisher disappears during a failed-start cleanup.
        time.sleep(0.05)
    subscriber.unregister()
    result = {
        "schema": "mosim.mworks_live.pre_mission_owner_gate.v1",
        "accepted": accepted,
        "reason_code": reason_code,
        "topic": args.topic,
        "expected_state": args.expected_state,
        "expected_run_id": args.run_id,
        "observed": observed,
        "elapsed_s": time.monotonic() - started,
    }
    atomic_json(args.output, result)
    print(json.dumps(result, indent=2))
    return 0 if accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
