#!/usr/bin/env python3
"""Compare RT1 loopback commands with the identity-attitude graphical outer loop."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


OUTER_LOOP_GAIN = 1.5
GRAVITY_MPS2 = 9.80665
IDENTITY_ATTITUDE = (0.0, 0.0, 0.0, 1.0)


def expected_command(values: list[float] | tuple[float, ...]) -> dict[str, Any]:
    """Return the RT1 wire command implied by the graphical outer loop.

    RT2 intentionally fixes the measured attitude at identity. This isolates
    the three-axis graphical PD/feed-forward core from the separate attitude
    convention and full-controller equivalence gates.
    """
    if len(values) != 24 or not all(math.isfinite(value) for value in values):
        raise ValueError("invalid_state_values")
    if any(
        abs(actual - expected) > 1e-12
        for actual, expected in zip(values[6:10], IDENTITY_ATTITUDE)
    ):
        raise ValueError("rt2_requires_identity_attitude")

    position = values[0:3]
    velocity = values[3:6]
    position_ref = values[13:16]
    velocity_ref = values[16:19]
    acceleration_ref = values[19:22]
    acceleration_x = (
        acceleration_ref[0]
        + OUTER_LOOP_GAIN * (velocity_ref[0] - velocity[0])
        + OUTER_LOOP_GAIN * (position_ref[0] - position[0])
    )
    acceleration_y = (
        acceleration_ref[1]
        + OUTER_LOOP_GAIN * (velocity_ref[1] - velocity[1])
        + OUTER_LOOP_GAIN * (position_ref[1] - position[1])
    )
    acceleration_z = (
        acceleration_ref[2]
        + OUTER_LOOP_GAIN * (velocity_ref[2] - velocity[2])
        + OUTER_LOOP_GAIN * (position_ref[2] - position[2])
        + GRAVITY_MPS2
    )

    # For the identity measured-attitude profile, the adapter emits a root
    # roll command from the graphical Y acceleration and a pitch command from
    # its X acceleration. The wire quaternion uses that same root convention.
    roll = acceleration_y / GRAVITY_MPS2
    pitch = acceleration_x / GRAVITY_MPS2
    qx = math.cos(pitch / 2.0) * math.sin(roll / 2.0)
    qy = math.sin(pitch / 2.0) * math.cos(roll / 2.0)
    qz = -math.sin(pitch / 2.0) * math.sin(roll / 2.0)
    qw = math.cos(pitch / 2.0) * math.cos(roll / 2.0)
    return {
        "q_xyzw": [qx, qy, qz, qw],
        "collective_thrust_n": acceleration_z,
        "graphical_desired_acceleration_mps2": [
            acceleration_x,
            acceleration_y,
            acceleration_z,
        ],
    }


def analyze(fixture: dict[str, Any], *, tolerance: float = 1e-6) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    if tolerance <= 0:
        raise ValueError("tolerance_must_be_positive")
    if fixture.get("execution_source") != "local_udp_fixture_to_mworks_realtime_simulation":
        failures.append({"reason_code": "unexpected_execution_source"})
    if fixture.get("fixture_profile") != "rt2_outer_loop_excitation":
        failures.append({"reason_code": "unexpected_fixture_profile"})
    if not fixture.get("passed"):
        failures.append({"reason_code": "loopback_fixture_not_passed"})

    states: dict[int, list[float]] = {}
    for frame in fixture.get("sent_frames", []):
        try:
            states[int(frame["sequence"])] = [float(value) for value in frame["values"]]
        except (KeyError, TypeError, ValueError):
            failures.append({"reason_code": "invalid_sent_frame"})

    comparisons: list[dict[str, Any]] = []
    for response in fixture.get("responses", []):
        try:
            state_sequence = int(response["state_sequence"])
            actual_quaternion = [float(value) for value in response["q_xyzw"]]
            actual_thrust = float(response["collective_thrust_n"])
            output_valid = bool(response["output_valid"])
            controller_status = int(response["controller_status"])
        except (KeyError, TypeError, ValueError):
            failures.append({"reason_code": "invalid_response"})
            continue
        if len(actual_quaternion) != 4:
            failures.append(
                {"reason_code": "invalid_response_quaternion", "state_sequence": state_sequence}
            )
            continue
        if not output_valid or controller_status != 1:
            failures.append(
                {
                    "reason_code": "invalid_controller_output",
                    "state_sequence": state_sequence,
                }
            )
            continue
        values = states.get(state_sequence)
        if values is None:
            failures.append(
                {"reason_code": "response_state_not_recorded", "state_sequence": state_sequence}
            )
            continue
        try:
            expected = expected_command(values)
        except ValueError as error:
            failures.append(
                {
                    "reason_code": str(error),
                    "state_sequence": state_sequence,
                }
            )
            continue
        quaternion_error = max(
            abs(actual - reference)
            for actual, reference in zip(actual_quaternion, expected["q_xyzw"])
        )
        thrust_error = abs(actual_thrust - float(expected["collective_thrust_n"]))
        comparisons.append(
            {
                "state_sequence": state_sequence,
                "max_quaternion_component_error": quaternion_error,
                "collective_thrust_error_n": thrust_error,
                "expected": expected,
                "actual": {
                    "q_xyzw": actual_quaternion,
                    "collective_thrust_n": actual_thrust,
                },
            }
        )
        if quaternion_error > tolerance or thrust_error > tolerance:
            failures.append(
                {
                    "reason_code": "graphical_outer_loop_mismatch",
                    "state_sequence": state_sequence,
                    "max_quaternion_component_error": quaternion_error,
                    "collective_thrust_error_n": thrust_error,
                }
            )

    minimum_responses = int(fixture.get("minimum_responses", 1))
    if len(comparisons) < minimum_responses:
        failures.append(
            {
                "reason_code": "insufficient_comparable_outputs",
                "actual": len(comparisons),
                "expected": minimum_responses,
            }
        )
    return {
        "schema": "mosim.mworks_rt1_graphical_equivalence.v1",
        "source": "analysis_of_mworks_local_udp_loopback_fixture",
        "run_id": fixture.get("run_id", ""),
        "fixture_profile": fixture.get("fixture_profile"),
        "passed": not failures,
        "tolerance": tolerance,
        "comparison_count": len(comparisons),
        "max_quaternion_component_error": max(
            (item["max_quaternion_component_error"] for item in comparisons),
            default=None,
        ),
        "max_collective_thrust_error_n": max(
            (item["collective_thrust_error_n"] for item in comparisons),
            default=None,
        ),
        "failures": failures,
        "comparisons": comparisons,
        "claim_boundary": (
            "Identity-attitude, three-axis graphical outer-loop equivalence on a "
            "real MWORKS local UDP loopback fixture only; no ROS, PX4, Gazebo, "
            "planner, localization, closed-loop, or flight acceptance."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tolerance", type=float, default=1e-6)
    args = parser.parse_args()

    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    result = analyze(fixture, tolerance=args.tolerance)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "comparisons"}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
