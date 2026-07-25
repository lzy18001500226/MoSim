#!/usr/bin/env python3
"""Fail-closed MWORKS Live endpoint and bidirectional RT1 preflight."""

from __future__ import annotations

import argparse
import ipaddress
import json
import math
import socket
import statistics
import time
import urllib.parse
import xmlrpc.client
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from rt1_contract import CommandFrame, StateReferenceFrame


VALID_RATES_HZ = (50, 100, 200)
IP_UDP_HEADER_BYTES = 28


@dataclass(frozen=True)
class Endpoint:
    target_host: str
    rt1_udp_port: int
    ros_master_uri: str
    local_advertised_ip: str
    requested_rate_hz: int


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(fraction * len(ordered)) - 1))
    return ordered[index]


def resolve_host(host: str) -> list[str]:
    if not host or any(character.isspace() for character in host):
        raise ValueError("invalid_target_host")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    try:
        rows = socket.getaddrinfo(host, None, type=socket.SOCK_DGRAM)
    except socket.gaierror as exc:
        raise ValueError("target_name_resolution_failed") from exc
    addresses = sorted({row[4][0] for row in rows})
    if not addresses:
        raise ValueError("target_name_resolution_failed")
    return addresses


def validate_endpoint(endpoint: Endpoint) -> list[str]:
    addresses = resolve_host(endpoint.target_host)
    if not 1 <= endpoint.rt1_udp_port <= 65535:
        raise ValueError("invalid_udp_port")
    if endpoint.requested_rate_hz not in VALID_RATES_HZ:
        raise ValueError("unsupported_rate_candidate")
    if endpoint.local_advertised_ip != "auto":
        try:
            ipaddress.ip_address(endpoint.local_advertised_ip)
        except ValueError as exc:
            raise ValueError("invalid_local_advertised_ip") from exc
    if endpoint.ros_master_uri:
        parsed = urllib.parse.urlparse(endpoint.ros_master_uri)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or not parsed.port:
            raise ValueError("invalid_ros_master_uri")
    return addresses


def probe_ros_master(uri: str, timeout_s: float) -> dict[str, Any]:
    if not uri:
        return {"configured": False, "reachable": None, "reason_code": "ros_master_not_configured"}
    previous_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout_s)
    started_ns = time.monotonic_ns()
    try:
        proxy = xmlrpc.client.ServerProxy(uri, allow_none=True)
        code, message, master_uri = proxy.getUri("/mosim_mworks_live_preflight")
        elapsed_ms = (time.monotonic_ns() - started_ns) / 1e6
        if int(code) != 1:
            return {
                "configured": True,
                "reachable": False,
                "reason_code": "ros_master_protocol_error",
                "message": str(message),
                "rtt_ms": elapsed_ms,
            }
        return {
            "configured": True,
            "reachable": True,
            "reason_code": "ros_master_reachable",
            "master_uri": str(master_uri),
            "rtt_ms": elapsed_ms,
        }
    except (OSError, xmlrpc.client.Error) as exc:
        return {
            "configured": True,
            "reachable": False,
            "reason_code": "ros_master_unreachable",
            "error_type": type(exc).__name__,
        }
    finally:
        socket.setdefaulttimeout(previous_timeout)


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


def probe_rt1(endpoint: Endpoint, *, timeout_s: float, sample_count: int) -> dict[str, Any]:
    run_id = f"preflight-{time.time_ns()}"
    period_ns = round(1e9 / endpoint.requested_rate_hz)
    rtt_ms: list[float] = []
    received_sequences: set[int] = set()
    protocol_errors: list[str] = []
    state_payload_bytes = 0
    command_payload_bytes = 0
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("0.0.0.0", 0))
        sock.settimeout(timeout_s)
        for sequence in range(sample_count):
            sent_ns = time.monotonic_ns()
            frame = StateReferenceFrame(
                run_id=run_id,
                sequence=sequence,
                source_stamp_ns=sent_ns,
                receive_monotonic_ns=sent_ns,
                valid_until_ns=sent_ns + max(50_000_000, 4 * period_ns),
                armed=False,
                state_valid=True,
                reference_valid=True,
                values=hover_values(),
            )
            payload = frame.pack()
            state_payload_bytes += len(payload)
            try:
                sock.sendto(payload, (endpoint.target_host, endpoint.rt1_udp_port))
                response, _peer = sock.recvfrom(4096)
            except (TimeoutError, socket.timeout, ConnectionResetError):
                continue
            received_ns = time.monotonic_ns()
            command_payload_bytes += len(response)
            try:
                command = CommandFrame.unpack(response)
            except ValueError as exc:
                protocol_errors.append(str(exc))
                continue
            if command.run_id != run_id:
                protocol_errors.append("rt1_run_id_mismatch")
                continue
            if command.state_sequence != sequence:
                protocol_errors.append("rt1_sequence_mismatch")
                continue
            received_sequences.add(sequence)
            rtt_ms.append((received_ns - sent_ns) / 1e6)
            sleep_ns = sent_ns + period_ns - time.monotonic_ns()
            if sleep_ns > 0:
                time.sleep(sleep_ns / 1e9)

    sent_count = sample_count
    received_count = len(received_sequences)
    duration_s = max(sample_count / endpoint.requested_rate_hz, 1e-9)
    payload_bytes = state_payload_bytes + command_payload_bytes
    wire_bytes = payload_bytes + IP_UDP_HEADER_BYTES * (sent_count + received_count)
    reason_code = "rt1_bidirectional_ready"
    if protocol_errors:
        reason_code = protocol_errors[0]
    elif received_count != sent_count:
        reason_code = "rt1_timeout"
    return {
        "reachable": received_count == sent_count and not protocol_errors,
        "reason_code": reason_code,
        "protocol_version": 1,
        "sent_count": sent_count,
        "received_count": received_count,
        "loss_rate": (sent_count - received_count) / sent_count,
        "rtt_mean_ms": statistics.fmean(rtt_ms) if rtt_ms else None,
        "rtt_p95_ms": percentile(rtt_ms, 0.95),
        "rtt_max_ms": max(rtt_ms) if rtt_ms else None,
        "state_frame_bytes": state_payload_bytes // sent_count,
        "command_frame_bytes": command_payload_bytes // received_count if received_count else 0,
        "measured_payload_bytes_per_s": payload_bytes / duration_s,
        "estimated_ip_udp_wire_bytes_per_s": wire_bytes / duration_s,
        "protocol_errors": protocol_errors,
    }


def run_preflight(endpoint: Endpoint, *, timeout_s: float = 0.25, sample_count: int = 5) -> dict[str, Any]:
    started_ns = time.monotonic_ns()
    try:
        addresses = validate_endpoint(endpoint)
    except ValueError as exc:
        return {
            "schema": "mosim.mworks_live_connection_preflight.v1",
            "accepted": False,
            "reason_code": str(exc),
            "endpoint": asdict(endpoint),
        }
    ros = probe_ros_master(endpoint.ros_master_uri, timeout_s)
    rt1 = probe_rt1(endpoint, timeout_s=timeout_s, sample_count=sample_count)
    accepted = bool(rt1["reachable"]) and (not ros["configured"] or bool(ros["reachable"]))
    reason = "connection_preflight_passed" if accepted else str(
        ros["reason_code"] if ros["configured"] and not ros["reachable"] else rt1["reason_code"]
    )
    return {
        "schema": "mosim.mworks_live_connection_preflight.v1",
        "accepted": accepted,
        "reason_code": reason,
        "endpoint": asdict(endpoint),
        "resolved_target_addresses": addresses,
        "ros_master": ros,
        "rt1": rt1,
        "elapsed_ms": (time.monotonic_ns() - started_ns) / 1e6,
        "claim_boundary": "Connectivity only. The selected rate still requires accepted same-machine RT0 evidence before flight prepare.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=49020)
    parser.add_argument("--ros-master-uri", default="http://127.0.0.1:11311")
    parser.add_argument("--local-advertised-ip", default="auto")
    parser.add_argument("--rate-hz", type=int, choices=VALID_RATES_HZ, default=200)
    parser.add_argument("--timeout-s", type=float, default=0.25)
    parser.add_argument("--sample-count", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_preflight(
        Endpoint(args.host, args.port, args.ros_master_uri, args.local_advertised_ip, args.rate_hz),
        timeout_s=args.timeout_s,
        sample_count=args.sample_count,
    )
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
