#!/usr/bin/env python3
"""Apply and record a bounded same-run Gazebo wind wrench for P9 A/B."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--body-name", default="uav1::base_link")
    parser.add_argument("--force-n", type=float, default=0.9)
    parser.add_argument("--direction-deg", type=float, default=35.0)
    parser.add_argument("--duration-s", type=float, default=20.0)
    parser.add_argument("--rate-hz", type=float, default=10.0)
    parser.add_argument("--minimum-altitude-m", type=float, default=0.65)
    parser.add_argument("--airborne-timeout-s", type=float, default=90.0)
    args = parser.parse_args()
    if args.force_n <= 0.0 or args.duration_s <= 0.0 or args.rate_hz <= 0.0:
        raise SystemExit("force, duration, and rate must be positive")

    import rospy
    from gazebo_msgs.msg import ModelStates
    from gazebo_msgs.srv import ApplyBodyWrench
    from geometry_msgs.msg import Point, Wrench

    args.result_dir.mkdir(parents=True, exist_ok=True)
    samples_path = args.result_dir / "wind_wrench_samples.jsonl"
    summary_path = args.result_dir / "WIND_INJECTION_EVIDENCE.json"
    latest_altitude = [None]

    def model_states(message: ModelStates) -> None:
        model_name = args.body_name.split("::", 1)[0]
        if model_name in message.name:
            latest_altitude[0] = float(message.pose[message.name.index(model_name)].position.z)

    rospy.init_node("mosim_p9_learning_wind_wrench", anonymous=True)
    rospy.Subscriber("/gazebo/model_states", ModelStates, model_states, queue_size=10)
    rospy.wait_for_service("/gazebo/apply_body_wrench", timeout=args.airborne_timeout_s)
    apply_wrench = rospy.ServiceProxy("/gazebo/apply_body_wrench", ApplyBodyWrench)
    deadline = time.monotonic() + args.airborne_timeout_s
    rate = rospy.Rate(args.rate_hz)
    while not rospy.is_shutdown() and (
        latest_altitude[0] is None or latest_altitude[0] < args.minimum_altitude_m
    ):
        if time.monotonic() >= deadline:
            payload = {
                "schema": "mosim.p9_learning_wind_injection.v1",
                "status": "blocked",
                "reason": "airborne_altitude_timeout",
                "last_altitude_m": latest_altitude[0],
            }
            summary_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            return 2
        rate.sleep()

    angle = math.radians(args.direction_deg)
    force_x = args.force_n * math.cos(angle)
    force_y = args.force_n * math.sin(angle)
    started = time.time()
    accepted = 0
    attempted = 0
    with samples_path.open("w", encoding="utf-8", newline="\n") as stream:
        while not rospy.is_shutdown() and time.time() - started < args.duration_s:
            wrench = Wrench()
            wrench.force.x = force_x
            wrench.force.y = force_y
            attempted += 1
            response = apply_wrench(
                body_name=args.body_name,
                reference_frame="world",
                reference_point=Point(),
                wrench=wrench,
                start_time=rospy.Time(0),
                duration=rospy.Duration(0.15),
            )
            accepted += int(bool(response.success))
            stream.write(json.dumps({
                "timestamp": time.time(),
                "altitude_m": latest_altitude[0],
                "force_n": [force_x, force_y, 0.0],
                "accepted": bool(response.success),
                "message": str(response.status_message),
            }, ensure_ascii=True) + "\n")
            stream.flush()
            rate.sleep()

    payload = {
        "schema": "mosim.p9_learning_wind_injection.v1",
        "status": "passed" if attempted > 0 and accepted == attempted else "blocked",
        "body_name": args.body_name,
        "force_n": args.force_n,
        "direction_deg": args.direction_deg,
        "duration_s": time.time() - started,
        "minimum_altitude_m": args.minimum_altitude_m,
        "attempted_samples": attempted,
        "accepted_samples": accepted,
        "sample_log": samples_path.name,
        "claim_boundary": "Gazebo ApplyBodyWrench acknowledgement only; controller robustness is evaluated by the same-run mission metrics.",
    }
    summary_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
