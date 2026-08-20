#!/usr/bin/env python3
"""Exercise the MWORKS RT1 graphical bridge with a local UDP peer only."""

from __future__ import annotations

import argparse
import json
import math
import socket
import statistics
import time
from pathlib import Path

from rt1_contract import COMMAND_VALUES, HEADER, CommandFrame, StateReferenceFrame


def hover_values() -> tuple[float, ...]:
    return (
        0.0, 0.0, 1.0,
        0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 1.0,
        0.0, 0.0, 0.0,
        0.0, 0.0, 1.0,
        0.0, 0.0, 0.0,
        0.0, 0.0, 0.0,
        0.0, 0.0,
    )


def rt2_outer_loop_excitation_values(sequence: int) -> tuple[float, ...]:
    """Return deterministic identity-attitude states for RT2 outer-loop checks."""
    phase = sequence * 0.25
    position_x = 0.05 * math.sin(phase)
    position_y = 0.04 * math.cos(phase)
    position_z = 1.0 + 0.03 * math.sin(0.5 * phase)
    velocity_x = 0.08 * math.cos(phase)
    velocity_y = -0.05 * math.sin(phase)
    velocity_z = 0.015 * math.cos(0.5 * phase)
    reference_x = 0.12 * math.sin(0.5 * phase)
    reference_y = -0.1 * math.cos(0.5 * phase)
    reference_z = 1.0 + 0.08 * math.cos(0.25 * phase)
    reference_vx = 0.06 * math.cos(0.5 * phase)
    reference_vy = 0.05 * math.sin(0.5 * phase)
    reference_vz = -0.02 * math.sin(0.25 * phase)
    reference_ax = 0.03 * math.sin(phase)
    reference_ay = -0.025 * math.cos(phase)
    reference_az = 0.02 * math.sin(0.5 * phase)
    return (
        position_x,
        position_y,
        position_z,
        velocity_x,
        velocity_y,
        velocity_z,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        reference_x,
        reference_y,
        reference_z,
        reference_vx,
        reference_vy,
        reference_vz,
        reference_ax,
        reference_ay,
        reference_az,
        0.0,
        0.0,
    )


def state_values(profile: str, sequence: int) -> tuple[float, ...]:
    if profile == "hover":
        return hover_values()
    if profile == "rt2_outer_loop_excitation":
        return rt2_outer_loop_excitation_values(sequence)
    raise ValueError(f"unsupported_fixture_profile:{profile}")


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(fraction * len(ordered)) - 1))
    return ordered[index]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=49020)
    parser.add_argument("--run-id", default="rt1-mworks-graphical-loopback")
    parser.add_argument("--rate-hz", type=float, default=100.0)
    parser.add_argument("--duration-s", type=float, default=4.0)
    parser.add_argument("--minimum-responses", type=int, default=20)
    parser.add_argument(
        "--profile",
        choices=("hover", "rt2_outer_loop_excitation"),
        default="hover",
    )
    parser.add_argument("--stop-on-pass", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.rate_hz <= 0 or args.duration_s <= 0 or args.minimum_responses < 1:
        raise SystemExit("rate, duration, and minimum responses must be positive")

    period_ns = round(1e9 / args.rate_hz)
    started_ns = time.monotonic_ns()
    deadline_ns = started_ns + round(args.duration_s * 1e9)
    next_send_ns = started_ns
    sequence = 0
    sent_sequences: set[int] = set()
    sent_frames: dict[int, dict[str, object]] = {}
    responses: list[dict[str, object]] = []
    expected_size = HEADER.size + COMMAND_VALUES.size
    stop_early = False

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.setblocking(False)
        while time.monotonic_ns() < deadline_ns:
            now_ns = time.monotonic_ns()
            while now_ns >= next_send_ns:
                values = state_values(args.profile, sequence)
                frame = StateReferenceFrame(
                    run_id=args.run_id,
                    sequence=sequence,
                    source_stamp_ns=next_send_ns,
                    receive_monotonic_ns=next_send_ns,
                    valid_until_ns=next_send_ns + 50_000_000,
                    armed=True,
                    state_valid=True,
                    reference_valid=True,
                    values=values,
                )
                sock.sendto(frame.pack(), (args.host, args.port))
                sent_sequences.add(sequence)
                sent_frames[sequence] = {
                    "sequence": sequence,
                    "source_stamp_ns": next_send_ns,
                    "values": list(values),
                }
                sequence += 1
                next_send_ns += period_ns

            while True:
                try:
                    payload, _peer = sock.recvfrom(expected_size + 64)
                except BlockingIOError:
                    break
                except ConnectionResetError:
                    break
                received_ns = time.monotonic_ns()
                try:
                    command = CommandFrame.unpack(payload)
                except ValueError:
                    continue
                quaternion_norm = math.sqrt(
                    sum(value * value for value in command.q_enu_from_flu_des_xyzw)
                )
                responses.append(
                    {
                        "command_sequence": command.sequence,
                        "state_sequence": command.state_sequence,
                        "run_id": command.run_id,
                        "received_monotonic_ns": received_ns,
                        "output_valid": command.output_valid,
                        "controller_status": command.controller_status,
                        "collective_thrust_n": command.collective_thrust_n,
                        "q_xyzw": list(command.q_enu_from_flu_des_xyzw),
                        "quaternion_norm": quaternion_norm,
                    }
                )
                valid_count = sum(
                    1
                    for row in responses
                    if bool(row["output_valid"])
                    and int(row["controller_status"]) == 1
                    and float(row["collective_thrust_n"]) > 0
                    and abs(float(row["quaternion_norm"]) - 1.0) <= 1e-6
                    and str(row["run_id"]) == args.run_id
                    and int(row["state_sequence"]) in sent_sequences
                )
                if args.stop_on_pass and valid_count >= args.minimum_responses and valid_count == len(responses):
                    stop_early = True
                    break
            if stop_early:
                break
            time.sleep(0.0005)

    valid_outputs = [
        row
        for row in responses
        if bool(row["output_valid"])
        and int(row["controller_status"]) == 1
        and float(row["collective_thrust_n"]) > 0
        and abs(float(row["quaternion_norm"]) - 1.0) <= 1e-6
        and str(row["run_id"]) == args.run_id
        and int(row["state_sequence"]) in sent_sequences
    ]
    received_ns = [int(row["received_monotonic_ns"]) for row in valid_outputs]
    elapsed_s = (received_ns[-1] - received_ns[0]) / 1e9 if len(received_ns) > 1 else 0.0
    result = {
        "schema": "mosim.mworks_rt1_graphical_loopback.v1",
        "execution_source": "local_udp_fixture_to_mworks_realtime_simulation",
        "claim_boundary": (
            "MWORKS graphical-control and local UDP transport smoke only; "
            "no ROS, PX4, Gazebo, planner, localization, or flight was executed."
        ),
        "run_id": args.run_id,
        "fixture_profile": args.profile,
        "requested_rate_hz": args.rate_hz,
        "request_count": sequence,
        "response_count": len(responses),
        "valid_output_count": len(valid_outputs),
        "valid_output_rate_hz": (
            (len(valid_outputs) - 1) / elapsed_s if elapsed_s > 0 else 0.0
        ),
        "quaternion_norm_p99": percentile(
            [float(row["quaternion_norm"]) for row in valid_outputs], 0.99
        ),
        "minimum_responses": args.minimum_responses,
        "stopped_early_after_valid_outputs": stop_early,
        "passed": len(valid_outputs) >= args.minimum_responses
        and len(valid_outputs) == len(responses),
        "sent_frames": [sent_frames[key] for key in sorted(sent_frames)],
        "responses": responses,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "responses"}, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
