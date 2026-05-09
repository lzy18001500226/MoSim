#!/usr/bin/env python3
"""Regression checks for safety-filter guard demo generation."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results" / "raw" / "safety_filter_guard.csv"
REFERENCE = ROOT / "results" / "raw" / "reference_safety_filter_guard.csv"
METRICS = ROOT / "results" / "metrics" / "safety_filter_guard.json"
EVENTS = ROOT / "results" / "logs" / "safety_filter_guard_events.jsonl"
REPLAY = ROOT / "results" / "replay" / "safety_filter_guard.json"


def main() -> int:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_safety_filter_demo.py")],
        cwd=ROOT,
        check=True,
    )
    with RAW.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) < 300:
        raise AssertionError(f"Expected at least 300 safety rows, got {len(rows)}")
    required = {
        "time",
        "x_raw_ref",
        "z_raw_ref",
        "x_safe_ref",
        "z_safe_ref",
        "raw_obstacle_distance_m",
        "safe_obstacle_distance_m",
        "safety_active",
        "controller_mode",
    }
    missing = required.difference(rows[0])
    if missing:
        raise AssertionError(f"Missing safety demo columns: {sorted(missing)}")
    if not REFERENCE.exists():
        raise AssertionError("Safety filtered reference CSV missing")

    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    if metrics["safe_constraint_violation_count"] >= metrics["raw_constraint_violation_count"]:
        raise AssertionError("Safety filter did not reduce total violations")
    if metrics["safe_altitude_violation_count"] != 0:
        raise AssertionError("Safety-filtered reference still violates altitude")
    if metrics["safe_obstacle_violation_count"] != 0:
        raise AssertionError("Safety-filtered reference still violates obstacle distance")
    if metrics["constraint_violation_reduction_pct"] < 50.0:
        raise AssertionError(f"Violation reduction too low: {metrics['constraint_violation_reduction_pct']}")
    if not metrics["accepted"]:
        raise AssertionError("Safety filter demo was not accepted")

    events = [json.loads(line) for line in EVENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not any(event.get("to") == "SAFETY_PROTECTION" for event in events):
        raise AssertionError("Event log does not contain SAFETY_PROTECTION transition")

    replay = json.loads(REPLAY.read_text(encoding="utf-8"))
    if replay["frame_count"] <= 0 or not replay.get("obstacles"):
        raise AssertionError("Safety replay is missing frames or obstacle metadata")

    print("[OK] safety filter demo regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
