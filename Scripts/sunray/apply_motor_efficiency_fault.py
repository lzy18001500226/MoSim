#!/usr/bin/env python3
"""Apply a bounded physical rotor-efficiency loss without controller takeover."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--rotor-index", type=int, choices=range(1, 5), default=1)
    parser.add_argument("--effectiveness", type=float, default=0.65)
    parser.add_argument("--duration-s", type=float, default=20.0)
    parser.add_argument("--rate-hz", type=float, default=20.0)
    parser.add_argument("--minimum-altitude-m", type=float, default=0.65)
    parser.add_argument("--airborne-timeout-s", type=float, default=90.0)
    parser.add_argument("--reset-hold-s", type=float, default=2.0)
    parser.add_argument("--command-topic", default="/uav1/mosim/ftc_actuator_command")
    parser.add_argument("--telemetry-topic", default="/uav1/mosim/ftc_actuator_telemetry")
    args = parser.parse_args()
    if not 0.0 < args.effectiveness <= 1.0:
        raise SystemExit("effectiveness must be in (0, 1]")
    if args.duration_s <= 0.0 or args.rate_hz <= 0.0 or args.airborne_timeout_s <= 0.0:
        raise SystemExit("duration, rate, and timeout must be positive")

    import rospy
    from nav_msgs.msg import Odometry
    from std_msgs.msg import Float64MultiArray

    args.result_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.result_dir / "MOTOR_EFFICIENCY_INJECTION_EVIDENCE.json"
    samples_path = args.result_dir / "motor_efficiency_samples.jsonl"
    latest_altitude = {"local_odom": None, "sunray_truth": None}
    latest_telemetry = [None]

    def odom_callback(message: Odometry) -> None:
        latest_altitude["local_odom"] = float(message.pose.pose.position.z)

    def truth_callback(message: Odometry) -> None:
        latest_altitude["sunray_truth"] = float(message.pose.pose.position.z)

    def telemetry_callback(message: Float64MultiArray) -> None:
        latest_telemetry[0] = list(message.data)

    rospy.init_node("mosim_motor_efficiency_fault", anonymous=True)
    publisher = rospy.Publisher(args.command_topic, Float64MultiArray, queue_size=5)
    rospy.Subscriber("/uav1/mavros/local_position/odom", Odometry, odom_callback, queue_size=10)
    rospy.Subscriber("/uav1/sunray/gazebo_pose", Odometry, truth_callback, queue_size=10)
    rospy.Subscriber(args.telemetry_topic, Float64MultiArray, telemetry_callback, queue_size=20)
    rate = rospy.Rate(args.rate_hz)
    deadline = time.monotonic() + args.airborne_timeout_s
    while not rospy.is_shutdown():
        airborne_source = next(
            (source for source, altitude in latest_altitude.items()
             if altitude is not None and altitude >= args.minimum_altitude_m),
            None,
        )
        ready = (
            publisher.get_num_connections() > 0
            and airborne_source is not None
            and latest_telemetry[0] is not None
            and len(latest_telemetry[0]) == 18
        )
        if ready:
            break
        if time.monotonic() >= deadline:
            payload = {
                "schema": "mosim.final_controller_ab.motor_efficiency_injection.v1",
                "status": "blocked",
                "reason": "plugin_or_airborne_readiness_timeout",
                "last_altitude_m": max(
                    (altitude for altitude in latest_altitude.values() if altitude is not None),
                    default=None,
                ),
                "last_altitude_by_source_m": latest_altitude,
                "publisher_connections": publisher.get_num_connections(),
                "telemetry_available": latest_telemetry[0] is not None,
            }
            summary_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            return 2
        rate.sleep()

    effectiveness = [1.0] * 4
    effectiveness[args.rotor_index - 1] = args.effectiveness

    def publish(values: list[float]) -> None:
        message = Float64MultiArray()
        # override_enabled=0 keeps the active controller in sole command authority.
        message.data = [0.0, *values, 0.0, 0.0, 0.0, 0.0]
        publisher.publish(message)

    started = time.monotonic()
    samples = 0
    observed = 0
    override_observed = False
    with samples_path.open("w", encoding="utf-8", newline="\n") as stream:
        while not rospy.is_shutdown() and time.monotonic() - started < args.duration_s:
            publish(effectiveness)
            telemetry = latest_telemetry[0]
            if telemetry and len(telemetry) == 18:
                samples += 1
                eta = [float(value) for value in telemetry[13:17]]
                override_enabled = telemetry[17] >= 0.5
                override_observed = override_observed or override_enabled
                if abs(eta[args.rotor_index - 1] - args.effectiveness) <= 1e-6:
                    observed += 1
                stream.write(json.dumps({
                    "elapsed_s": time.monotonic() - started,
                    "altitude_m": max(
                        (altitude for altitude in latest_altitude.values() if altitude is not None),
                        default=None,
                    ),
                    "effectiveness": eta,
                    "override_enabled": override_enabled,
                }, ensure_ascii=True) + "\n")
                stream.flush()
            rate.sleep()

        reset_started = time.monotonic()
        while not rospy.is_shutdown() and time.monotonic() - reset_started < args.reset_hold_s:
            publish([1.0] * 4)
            rate.sleep()

    status = "passed" if samples > 0 and observed > 0 and not override_observed else "blocked"
    payload = {
        "schema": "mosim.final_controller_ab.motor_efficiency_injection.v1",
        "status": status,
        "rotor_index": args.rotor_index,
        "effectiveness": args.effectiveness,
        "duration_s": time.monotonic() - started - args.reset_hold_s,
        "minimum_altitude_m": args.minimum_altitude_m,
        "telemetry_samples": samples,
        "fault_effectiveness_observed_samples": observed,
        "controller_override_observed": override_observed,
        "reset_to_nominal_commanded": True,
        "sample_log": samples_path.name,
        "claim_boundary": (
            "Gazebo actuator-plugin acknowledgement of physical rotor-efficiency loss only; "
            "controller commands are never overridden and robustness is evaluated by same-run mission metrics."
        ),
    }
    summary_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
