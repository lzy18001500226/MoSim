#!/usr/bin/env python3
"""Evaluate an RT1 Shadow status file against the flight-entry gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def analyze(
    status: dict[str, Any],
    *,
    minimum_window_s: float = 300.0,
    minimum_state_rate_hz: float = 198.0,
    minimum_command_rate_hz: float = 198.0,
    maximum_command_age_ms: float = 50.0,
) -> dict[str, Any]:
    transport = status.get("transport", {})
    rejection_counts = status.get("rejection_counts", {})
    metrics = {
        "process_window_s": float(transport.get("process_window_s", 0.0)),
        "state_send_rate_hz": float(transport.get("state_send_rate_hz", 0.0)),
        "command_receive_rate_hz": float(transport.get("command_receive_rate_hz", 0.0)),
        "command_age_ms_max": float(status.get("command_age_ms_max") or 0.0),
        "output_stale_count": int(rejection_counts.get("output_stale", 0)),
        "send_error_count": int(transport.get("send_error_count", 0)),
        "missing_command_count": int(transport.get("missing_command_count", 0)),
        "duplicate_command_count": int(transport.get("duplicate_command_count", 0)),
        "out_of_order_command_count": int(transport.get("out_of_order_command_count", 0)),
    }
    failures: list[dict[str, Any]] = []

    def require(code: str, passed: bool, actual: Any, expected: str) -> None:
        if not passed:
            failures.append(
                {"reason_code": code, "actual": actual, "expected": expected}
            )

    require(
        "shadow_window_too_short",
        metrics["process_window_s"] >= minimum_window_s,
        metrics["process_window_s"],
        f">= {minimum_window_s} s",
    )
    require(
        "state_rate_below_minimum",
        metrics["state_send_rate_hz"] >= minimum_state_rate_hz,
        metrics["state_send_rate_hz"],
        f">= {minimum_state_rate_hz} Hz",
    )
    require(
        "command_rate_below_minimum",
        metrics["command_receive_rate_hz"] >= minimum_command_rate_hz,
        metrics["command_receive_rate_hz"],
        f">= {minimum_command_rate_hz} Hz",
    )
    require(
        "command_age_exceeded",
        metrics["command_age_ms_max"] < maximum_command_age_ms,
        metrics["command_age_ms_max"],
        f"< {maximum_command_age_ms} ms",
    )
    require(
        "stale_output_observed",
        metrics["output_stale_count"] == 0,
        metrics["output_stale_count"],
        "0",
    )
    for key in (
        "send_error_count",
        "missing_command_count",
        "duplicate_command_count",
        "out_of_order_command_count",
    ):
        require(key, metrics[key] == 0, metrics[key], "0")

    safe_shadow = status.get("state") == "SHADOW" and status.get("shadow_only") is True
    require(
        "not_shadow_only",
        safe_shadow,
        {"state": status.get("state"), "shadow_only": status.get("shadow_only")},
        "state=SHADOW and shadow_only=true",
    )
    return {
        "schema": "mosim.mworks_live_rt1_shadow_gate.v1",
        "run_id": status.get("run_id", ""),
        "adapter_backend": status.get("adapter_backend", ""),
        "accepted": not failures,
        "decision": "shadow_gate_passed" if not failures else "shadow_gate_failed",
        "flight_entry_allowed": not failures,
        "metrics": metrics,
        "thresholds": {
            "minimum_window_s": minimum_window_s,
            "minimum_state_rate_hz": minimum_state_rate_hz,
            "minimum_command_rate_hz": minimum_command_rate_hz,
            "maximum_command_age_ms": maximum_command_age_ms,
            "maximum_output_stale_count": 0,
        },
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("status", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--minimum-window-s", type=float, default=300.0)
    parser.add_argument("--minimum-state-rate-hz", type=float, default=198.0)
    parser.add_argument("--minimum-command-rate-hz", type=float, default=198.0)
    parser.add_argument("--maximum-command-age-ms", type=float, default=50.0)
    args = parser.parse_args()
    result = analyze(
        json.loads(args.status.read_text(encoding="utf-8")),
        minimum_window_s=args.minimum_window_s,
        minimum_state_rate_hz=args.minimum_state_rate_hz,
        minimum_command_rate_hz=args.minimum_command_rate_hz,
        maximum_command_age_ms=args.maximum_command_age_ms,
    )
    payload = json.dumps(result, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if result["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
