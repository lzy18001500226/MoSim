#!/usr/bin/env python3
"""Drive and capture the real external-I/O side of the Sysplorer RT0 probe."""

from __future__ import annotations

import argparse
import json
import socket
import struct
import time
from pathlib import Path


REQUEST_MAGIC = 0x4D525451
RESPONSE_MAGIC = 0x4D525452
VERSION = 1
REQUEST = struct.Struct("<IHHIQQdddd")
RESPONSE = struct.Struct("<IHHIQQQddddi")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=49010)
    parser.add_argument("--rate-hz", type=float, default=100.0)
    parser.add_argument("--duration-s", type=float, default=16.0)
    parser.add_argument("--idle-exit-s", type=float, default=1.5)
    parser.add_argument("--minimum-responses", type=int, default=1000)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()

    period_ns = round(1e9 / args.rate_hz)
    responses: dict[int, dict[str, object]] = {}
    sent: dict[int, tuple[int, int]] = {}
    started_ns = time.perf_counter_ns()
    deadline_ns = started_ns + round(args.duration_s * 1e9)
    next_send_ns = started_ns
    sequence = 0
    last_response_ns: int | None = None

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((args.host, 0))
        sock.setblocking(False)
        while time.perf_counter_ns() < deadline_ns:
            now_ns = time.perf_counter_ns()
            while now_ns >= next_send_ns:
                source_stamp_ns = time.perf_counter_ns()
                position = 0.25 * ((sequence % 20) - 10) / 10.0
                payload = REQUEST.pack(
                    REQUEST_MAGIC,
                    VERSION,
                    0,
                    sequence,
                    source_stamp_ns,
                    source_stamp_ns,
                    position,
                    0.05,
                    1.0,
                    0.0,
                )
                sock.sendto(payload, (args.host, args.port))
                sent[sequence] = (source_stamp_ns, source_stamp_ns)
                sequence += 1
                next_send_ns += period_ns
            while True:
                try:
                    payload, _ = sock.recvfrom(RESPONSE.size)
                except BlockingIOError:
                    break
                except ConnectionResetError:
                    # Windows reports ICMP port-unreachable as WSAECONNRESET
                    # while the realtime model is still opening its socket.
                    break
                received_ns = time.perf_counter_ns()
                if len(payload) != RESPONSE.size:
                    continue
                unpacked = RESPONSE.unpack(payload)
                magic, version, status, response_sequence = unpacked[:4]
                if magic != RESPONSE_MAGIC or version != VERSION:
                    continue
                source_stamp_ns, sent_ns = sent.get(response_sequence, (0, 0))
                responses[response_sequence] = {
                    "sequence": response_sequence,
                    "input_sent_monotonic_ns": sent_ns,
                    "compute_started_monotonic_ns": unpacked[5],
                    "compute_finished_monotonic_ns": unpacked[6],
                    "output_received_monotonic_ns": received_ns,
                    "command_source_stamp_ns": source_stamp_ns,
                    "output_valid": status == 0 and unpacked[11] == 1,
                    "execution_source": "mworks_sysplorer_realtime",
                    "sim_mode": 2,
                    "desired_qz": unpacked[7],
                    "desired_qw": unpacked[8],
                    "collective_thrust_N": unpacked[9],
                    "controller_output": unpacked[10],
                }
                last_response_ns = received_ns
            if (
                last_response_ns is not None
                and len(responses) >= args.minimum_responses
                and time.perf_counter_ns() - last_response_ns >= round(args.idle_exit_s * 1e9)
            ):
                break
            sleep_ns = next_send_ns - time.perf_counter_ns()
            if sleep_ns > 0:
                time.sleep(min(sleep_ns / 1e9, 0.001))

    ordered = [responses[key] for key in sorted(responses)]
    args.trace.parent.mkdir(parents=True, exist_ok=True)
    args.trace.write_text(
        "".join(json.dumps(row, separators=(",", ":")) + "\n" for row in ordered),
        encoding="utf-8",
    )
    summary = {
        "schema": "mosim.mworks_live_rt0_capture.v1",
        "selection_policy": "latest_state_wins",
        "sequence_gap_interpretation": "coalesced_or_unobserved_requests_not_transport_loss",
        "request_count": sequence,
        "response_count": len(ordered),
        "first_response_sequence": ordered[0]["sequence"] if ordered else None,
        "last_response_sequence": ordered[-1]["sequence"] if ordered else None,
        "trace": str(args.trace.resolve()),
        "claim_boundary": "Requires matching Sysplorer sim_mode=2 invocation evidence.",
    }
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if ordered else 2


if __name__ == "__main__":
    raise SystemExit(main())
