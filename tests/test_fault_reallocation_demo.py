#!/usr/bin/env python3
"""Regression checks for fault-aware control allocation comparison."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results" / "raw" / "fault_reallocation_compare.csv"
REFERENCE = ROOT / "results" / "raw" / "reference_fault_reallocation_compare.csv"
METRICS = ROOT / "results" / "metrics" / "fault_reallocation_compare.json"
EVENTS = ROOT / "results" / "logs" / "fault_reallocation_compare_events.jsonl"
REPLAY = ROOT / "results" / "replay" / "fault_reallocation_compare.json"


def main() -> int:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_fault_reallocation_demo.py")],
        cwd=ROOT,
        check=True,
    )
    with RAW.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) < 1000:
        raise AssertionError(f"Expected at least 1000 allocation rows, got {len(rows)}")
    required = {
        "time",
        "eta2",
        "fault_active",
        "no_realloc_motor_2",
        "realloc_motor_2",
        "no_realloc_wrench_error",
        "realloc_wrench_error",
        "controller_mode",
    }
    missing = required.difference(rows[0])
    if missing:
        raise AssertionError(f"Missing allocation columns: {sorted(missing)}")
    if not REFERENCE.exists():
        raise AssertionError("Reallocation reference CSV missing")

    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    if metrics["eta_min"] != 0.7:
        raise AssertionError(f"Unexpected eta_min: {metrics['eta_min']}")
    if metrics["wrench_error_reduction_pct"] < 80.0:
        raise AssertionError(f"Wrench reduction too low: {metrics['wrench_error_reduction_pct']}")
    if metrics["realloc_wrench_rmse"] >= metrics["no_realloc_wrench_rmse"]:
        raise AssertionError("Reallocation did not improve wrench RMSE")
    if not metrics["accepted"]:
        raise AssertionError("Fault reallocation demo was not accepted")

    events = [json.loads(line) for line in EVENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not any(event.get("event") == "reallocator_enabled" for event in events):
        raise AssertionError("Event log does not contain reallocator_enabled")

    replay = json.loads(REPLAY.read_text(encoding="utf-8"))
    if replay["frame_count"] <= 0:
        raise AssertionError("Fault reallocation replay has no frames")

    print("[OK] fault reallocation demo regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
