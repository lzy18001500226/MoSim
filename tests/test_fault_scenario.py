#!/usr/bin/env python3
"""Regression checks for motor fault return reference generation."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "results" / "raw" / "fault_motor_return_reference.csv"
METRICS = ROOT / "results" / "metrics" / "fault_motor_return.json"
EVENTS = ROOT / "results" / "logs" / "fault_motor_return_events.jsonl"
REPLAY = ROOT / "results" / "replay" / "fault_motor_return.json"


def main() -> int:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_fault_scenario.py")],
        cwd=ROOT,
        check=True,
    )
    with REFERENCE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) < 100:
        raise AssertionError(f"Expected at least 100 fault rows, got {len(rows)}")
    required = {"time", "x_ref", "y_ref", "z_ref", "eta_min", "controller_mode", "fault_type", "return_or_land_status"}
    missing = required.difference(rows[0])
    if missing:
        raise AssertionError(f"Missing fault columns: {sorted(missing)}")
    modes = {row["controller_mode"] for row in rows}
    if "FAULT_TOLERANT" not in modes:
        raise AssertionError(f"Expected FAULT_TOLERANT mode, got {sorted(modes)}")

    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    if metrics["eta_min"] != 0.7:
        raise AssertionError(f"Unexpected eta_min: {metrics['eta_min']}")
    if metrics["fault_tolerance_score"] < 80.0:
        raise AssertionError(f"Fault tolerance score too low: {metrics['fault_tolerance_score']}")
    if metrics["controller_mode_switch_count"] < 3:
        raise AssertionError("Expected at least three mode switch events")
    if metrics["altitude_violation_count"] != 0:
        raise AssertionError("Fault reference violates minimum altitude")

    events = [json.loads(line) for line in EVENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    event_types = {event["event"] for event in events}
    if "motor_fault" not in event_types or "degraded_return_start" not in event_types:
        raise AssertionError(f"Missing expected fault events: {sorted(event_types)}")

    replay = json.loads(REPLAY.read_text(encoding="utf-8"))
    if replay["frame_count"] <= 0:
        raise AssertionError("Fault replay has no frames")

    print("[OK] fault scenario regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
