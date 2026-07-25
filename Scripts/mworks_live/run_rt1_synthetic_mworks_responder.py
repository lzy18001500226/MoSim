#!/usr/bin/env python3
"""Synthetic RT1 responder for Gazebo-step protocol tests only."""

from __future__ import annotations

import argparse
import json
import socket
import time
from pathlib import Path

from rt1_contract import CommandFrame, StateReferenceFrame
from sunray150_virtual_px4_classic_profile import load_rt1_controller_defaults


RT1_MASS_KG, RT1_GRAVITY_MPS2, _ = load_rt1_controller_defaults()
HOVER_THRUST_N = RT1_MASS_KG * RT1_GRAVITY_MPS2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bind-host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=49020)
    parser.add_argument("--duration-s", type=float, default=5.0)
    parser.add_argument("--stall-after-s", type=float, default=-1.0)
    parser.add_argument("--stall-duration-s", type=float, default=0.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    started = time.monotonic()
    deadline = started + args.duration_s
    stall_done = False
    stall_started_monotonic_ns: int | None = None
    stall_finished_monotonic_ns: int | None = None
    received = 0
    sent = 0
    state_sequences: list[int] = []
    command_sequence = 1
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((args.bind_host, args.port))
        sock.settimeout(0.1)
        while time.monotonic() < deadline:
            try:
                payload, peer = sock.recvfrom(1024)
            except socket.timeout:
                continue
            frame = StateReferenceFrame.unpack(payload)
            received += 1
            state_sequences.append(frame.sequence)
            elapsed = time.monotonic() - started
            if (
                not stall_done
                and args.stall_after_s >= 0
                and elapsed >= args.stall_after_s
            ):
                stall_started_monotonic_ns = time.monotonic_ns()
                time.sleep(args.stall_duration_s)
                stall_finished_monotonic_ns = time.monotonic_ns()
                stall_done = True
            command = CommandFrame(
                run_id=frame.run_id,
                sequence=command_sequence,
                state_sequence=frame.sequence,
                source_stamp_ns=frame.receive_monotonic_ns,
                produced_monotonic_ns=time.monotonic_ns(),
                valid_until_ns=frame.receive_monotonic_ns + 50_000_000,
                q_enu_from_flu_des_xyzw=(0.0, 0.0, 0.0, 1.0),
                collective_thrust_n=HOVER_THRUST_N,
            )
            sock.sendto(command.pack(), peer)
            sent += 1
            command_sequence += 1

    result = {
        "schema": "mosim.mworks_live.synthetic_responder.v1",
        "execution_source": "python_synthetic_protocol_test_only",
        "received_state_count": received,
        "sent_command_count": sent,
        "stall_injected": stall_done,
        "stall_duration_s": args.stall_duration_s if stall_done else 0.0,
        "stall_started_monotonic_ns": stall_started_monotonic_ns,
        "stall_finished_monotonic_ns": stall_finished_monotonic_ns,
        "first_state_sequence": state_sequences[0] if state_sequences else None,
        "last_state_sequence": state_sequences[-1] if state_sequences else None,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if received and sent else 2


if __name__ == "__main__":
    raise SystemExit(main())
