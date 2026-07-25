#!/usr/bin/env python3
"""Feed synthetic hover state/reference frames to the RT1 realtime model."""

from __future__ import annotations

import argparse
import json
import math
import socket
import statistics
import time
from pathlib import Path

from rt1_contract import COMMAND_VALUES, HEADER, CommandFrame, StateReferenceFrame
from sunray150_virtual_px4_classic_profile import load_rt1_controller_defaults


RT1_MASS_KG, RT1_GRAVITY_MPS2, _ = load_rt1_controller_defaults()
HOVER_THRUST_N = RT1_MASS_KG * RT1_GRAVITY_MPS2


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return math.nan
    index = min(len(ordered) - 1, max(0, math.ceil(fraction * len(ordered)) - 1))
    return ordered[index]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=49020)
    parser.add_argument("--run-id", default="rt1-synthetic-shadow")
    parser.add_argument("--rate-hz", type=float, default=50.0)
    parser.add_argument("--duration-s", type=float, default=16.0)
    parser.add_argument("--minimum-responses", type=int, default=500)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    period_ns = round(1e9 / args.rate_hz)
    started_ns = time.monotonic_ns()
    deadline_ns = started_ns + round(args.duration_s * 1e9)
    next_send_ns = started_ns
    sequence = 0
    commands: dict[int, dict[str, object]] = {}
    expected_size = HEADER.size + COMMAND_VALUES.size

    values = (
        0.0, 0.0, 1.0,
        0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 1.0,
        0.0, 0.0, 0.0,
        0.0, 0.0, 1.0,
        0.0, 0.0, 0.0,
        0.0, 0.0, 0.0,
        0.0, 0.0,
    )
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.setblocking(False)
        while time.monotonic_ns() < deadline_ns:
            now_ns = time.monotonic_ns()
            while now_ns >= next_send_ns:
                frame = StateReferenceFrame(
                    run_id=args.run_id,
                    sequence=sequence,
                    source_stamp_ns=next_send_ns,
                    receive_monotonic_ns=next_send_ns,
                    valid_until_ns=next_send_ns + 50_000_000,
                    armed=False,
                    state_valid=True,
                    reference_valid=True,
                    values=values,
                )
                sock.sendto(frame.pack(), (args.host, args.port))
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
                commands[command.sequence] = {
                    "sequence": command.sequence,
                    "state_sequence": command.state_sequence,
                    "source_stamp_ns": command.source_stamp_ns,
                    "received_monotonic_ns": received_ns,
                    "command_age_ms": (received_ns - command.source_stamp_ns) / 1e6,
                    "q_xyzw": command.q_enu_from_flu_des_xyzw,
                    "collective_thrust_n": command.collective_thrust_n,
                    "output_valid": command.output_valid,
                    "controller_status": command.controller_status,
                }
            time.sleep(0.0005)

    rows = [commands[key] for key in sorted(commands)]
    ages = [float(row["command_age_ms"]) for row in rows]
    thrust_errors = [abs(float(row["collective_thrust_n"]) - HOVER_THRUST_N) for row in rows]
    quaternion_errors = [
        max(abs(float(value) - expected) for value, expected in zip(row["q_xyzw"], (0.0, 0.0, 0.0, 1.0)))
        for row in rows
    ]
    elapsed_s = (
        (int(rows[-1]["received_monotonic_ns"]) - int(rows[0]["received_monotonic_ns"])) / 1e9
        if len(rows) > 1 else 0.0
    )
    result = {
        "schema": "mosim.mworks_live_rt1_synthetic_shadow.v1",
        "ok": (
            len(rows) >= args.minimum_responses
            and all(bool(row["output_valid"]) for row in rows)
            and max(thrust_errors, default=math.inf) <= 1e-9
            and max(quaternion_errors, default=math.inf) <= 1e-9
            and max(ages, default=math.inf) < 50.0
        ),
        "request_count": sequence,
        "response_count": len(rows),
        "output_rate_hz": ((len(rows) - 1) / elapsed_s if elapsed_s > 0 else 0.0),
        "command_age_mean_ms": statistics.fmean(ages) if ages else None,
        "command_age_p99_ms": percentile(ages, 0.99) if ages else None,
        "command_age_max_ms": max(ages) if ages else None,
        "max_collective_thrust_error_n": max(thrust_errors, default=None),
        "max_quaternion_component_error": max(quaternion_errors, default=None),
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "rows"}, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
