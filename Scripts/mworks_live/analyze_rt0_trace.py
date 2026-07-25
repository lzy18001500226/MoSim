#!/usr/bin/env python3
"""Fail-closed analysis of a real MWORKS Sysplorer realtime RT0 JSONL trace."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import fmean
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACT = ROOT / "Config/control_platform/mworks_live_attitude_thrust_contract_v1.json"
DEFAULT_CATALOG = ROOT / "Config/profiles/catalog.json"


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return math.nan
    index = (len(ordered) - 1) * fraction
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: expected JSON object")
        rows.append(value)
    return rows


def load_optional_json(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def rate_hz(stamps_ns: list[int]) -> float:
    if len(stamps_ns) < 2 or stamps_ns[-1] <= stamps_ns[0]:
        return 0.0
    return (len(stamps_ns) - 1) * 1e9 / (stamps_ns[-1] - stamps_ns[0])


def maximum_consecutive_true(values: list[bool]) -> int:
    maximum = 0
    current = 0
    for value in values:
        current = current + 1 if value else 0
        maximum = max(maximum, current)
    return maximum


def analyze(
    contract: dict[str, Any],
    rows: list[dict[str, Any]],
    timing_override: dict[str, Any] | None = None,
    capture_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    required = {
        "sequence",
        "input_sent_monotonic_ns",
        "compute_started_monotonic_ns",
        "compute_finished_monotonic_ns",
        "output_received_monotonic_ns",
        "command_source_stamp_ns",
        "output_valid",
        "execution_source",
        "sim_mode",
    }
    for index, row in enumerate(rows):
        missing = sorted(required - row.keys())
        if missing:
            errors.append(f"row {index}: missing {', '.join(missing)}")
    if errors:
        return {"schema": "mosim.mworks_live_rt0_result.v1", "ok": False, "errors": errors}

    acceptance = contract["rt0_acceptance"]
    timing = timing_override or contract["timing_candidates"]
    source = acceptance["required_execution_source"]
    sim_mode = acceptance["required_sim_mode"]
    if any(row["execution_source"] != source for row in rows):
        errors.append(f"all rows must use execution_source={source}")
    if any(row["sim_mode"] != sim_mode for row in rows):
        errors.append(f"all rows must use sim_mode={sim_mode}")

    sequences = [int(row["sequence"]) for row in rows]
    duplicate_count = len(sequences) - len(set(sequences))
    out_of_order_count = sum(b <= a for a, b in zip(sequences, sequences[1:]))
    sequence_drop_count = sum(max(0, b - a - 1) for a, b in zip(sequences, sequences[1:]))
    invalid_count = sum(not bool(row["output_valid"]) for row in rows)
    input_stamps = [int(row["input_sent_monotonic_ns"]) for row in rows]
    compute_stamps = [int(row["compute_finished_monotonic_ns"]) for row in rows]
    output_stamps = sorted(int(row["output_received_monotonic_ns"]) for row in rows)
    latency_ms = [
        (int(row["output_received_monotonic_ns"]) - int(row["input_sent_monotonic_ns"])) / 1e6
        for row in rows
    ]
    compute_ms = [
        (int(row["compute_finished_monotonic_ns"]) - int(row["compute_started_monotonic_ns"])) / 1e6
        for row in rows
    ]
    command_age_ms = [
        (int(row["output_received_monotonic_ns"]) - int(row["command_source_stamp_ns"])) / 1e6
        for row in rows
    ]
    deadline_ms = float(timing["deadline_ms"])
    output_period_deadline_ms = float(
        timing.get("output_period_deadline_ms", deadline_ms)
    )
    deadline_misses = [value > deadline_ms for value in latency_ms]
    deadline_miss_count = sum(deadline_misses)
    max_consecutive_deadline_misses = maximum_consecutive_true(deadline_misses)
    periods_ms = [(b - a) / 1e6 for a, b in zip(output_stamps, output_stamps[1:])]
    nominal_period = float(timing["nominal_period_ms"])
    jitter_ms = [abs(value - nominal_period) for value in periods_ms]
    duration_s = (output_stamps[-1] - output_stamps[0]) / 1e9 if len(rows) > 1 else 0.0

    if len(rows) < int(acceptance["minimum_samples"]):
        errors.append("sample count below RT0 minimum")
    if duration_s < float(acceptance["minimum_duration_s"]):
        errors.append("trace duration below RT0 minimum")
    output_rate = rate_hz(output_stamps)
    if output_rate < float(timing["minimum_sustained_rate_hz"]):
        errors.append("output rate below minimum sustained rate")
    period_p99_ms = percentile(periods_ms, 0.99)
    period_max_ms = max(periods_ms, default=math.inf)
    if period_p99_ms > output_period_deadline_ms:
        errors.append("output period p99 exceeds output-period deadline")
    if period_max_ms > float(timing["command_stale_ms"]):
        errors.append("maximum output gap exceeds stale threshold")
    if max_consecutive_deadline_misses >= int(
        timing["consecutive_deadline_misses_before_degrade"]
    ):
        errors.append("consecutive end-to-end deadline misses trigger degradation")
    if max(command_age_ms, default=math.inf) > float(timing["command_stale_ms"]):
        errors.append("maximum command age exceeds stale threshold")
    capture = capture_summary or {}
    selection_policy = capture.get("selection_policy", "unknown")
    unobserved_or_coalesced_count = max(
        int(capture.get("request_count", len(rows))) - len(rows), 0
    )
    explicit_transport_drop_count = int(capture.get("transport_drop_count", 0))
    if duplicate_count or out_of_order_count or invalid_count:
        errors.append("trace contains duplicate, out-of-order, or invalid outputs")
    if explicit_transport_drop_count:
        errors.append("capture reports transport drops")

    return {
        "schema": "mosim.mworks_live_rt0_result.v1",
        "ok": not errors,
        "execution_source": source,
        "sim_mode": sim_mode,
        "sample_count": len(rows),
        "duration_s": duration_s,
        "metrics": {
            "input_rate_hz": rate_hz(input_stamps),
            "compute_rate_hz": rate_hz(compute_stamps),
            "output_rate_hz": output_rate,
            "compute_mean_ms": fmean(compute_ms),
            "compute_p99_ms": percentile(compute_ms, 0.99),
            "latency_mean_ms": fmean(latency_ms),
            "latency_p95_ms": percentile(latency_ms, 0.95),
            "latency_p99_ms": percentile(latency_ms, 0.99),
            "latency_max_ms": max(latency_ms),
            "deadline_ms": deadline_ms,
            "output_period_deadline_ms": output_period_deadline_ms,
            "deadline_miss_count": deadline_miss_count,
            "max_consecutive_deadline_misses": max_consecutive_deadline_misses,
            "jitter_p99_ms": percentile(jitter_ms, 0.99),
            "output_period_p50_ms": percentile(periods_ms, 0.50),
            "output_period_p95_ms": percentile(periods_ms, 0.95),
            "output_period_p99_ms": period_p99_ms,
            "output_period_max_ms": period_max_ms,
            "drop_count": explicit_transport_drop_count,
            "sequence_gap_count": sequence_drop_count,
            "unobserved_or_coalesced_count": unobserved_or_coalesced_count,
            "selection_policy": selection_policy,
            "duplicate_count": duplicate_count,
            "out_of_order_count": out_of_order_count,
            "invalid_count": invalid_count,
            "command_age_max_ms": max(command_age_ms),
        },
        "errors": errors,
        "claim_boundary": "Pass is valid only when trace provenance is independently bound to a real Sysplorer sim_mode=2 run.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--frequency-profile")
    parser.add_argument("--capture-summary", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    timing_override = None
    if args.frequency_profile:
        catalog = load_json(args.catalog)
        timing_override = catalog.get("frequency_profiles", {}).get(args.frequency_profile)
        if not isinstance(timing_override, dict):
            raise SystemExit(f"Unknown frequency profile: {args.frequency_profile}")
    result = analyze(
        load_json(args.contract),
        load_rows(args.trace),
        timing_override,
        load_optional_json(args.capture_summary),
    )
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
