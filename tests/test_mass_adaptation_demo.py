#!/usr/bin/env python3
"""Regression checks for delivery mass-change adaptation demo generation."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results" / "raw" / "delivery_mass_change.csv"
METRICS = ROOT / "results" / "metrics" / "delivery_mass_change.json"
EVENTS = ROOT / "results" / "logs" / "delivery_mass_change_events.jsonl"
REPLAY = ROOT / "results" / "replay" / "delivery_mass_change.json"


def main() -> int:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_mass_adaptation_demo.py")],
        cwd=ROOT,
        check=True,
    )
    with RAW.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) < 1000:
        raise AssertionError(f"Expected at least 1000 mass demo rows, got {len(rows)}")
    required = {
        "time",
        "x_ref",
        "y_ref",
        "z_ref",
        "actual_mass_scale",
        "mass_estimate_scale",
        "acc_residual_raw_z_m_s2",
        "disturbance_comp_z_m_s2",
        "controller_mode",
        "task_phase",
    }
    missing = required.difference(rows[0])
    if missing:
        raise AssertionError(f"Missing mass demo columns: {sorted(missing)}")
    modes = {row["controller_mode"] for row in rows}
    if "MASS_ADAPTATION" not in modes:
        raise AssertionError(f"Expected MASS_ADAPTATION mode, got {sorted(modes)}")

    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    if not metrics["mass_adaptation_entered"]:
        raise AssertionError("Mode switch to MASS_ADAPTATION was not detected")
    if metrics["vertical_residual_reduction_pct"] < 20.0:
        raise AssertionError(f"Vertical residual reduction too low: {metrics['vertical_residual_reduction_pct']}")
    if metrics["return_position_error_m"] >= 0.05:
        raise AssertionError(f"Return error too high: {metrics['return_position_error_m']}")
    if not metrics["accepted"]:
        raise AssertionError("Mass adaptation demo was not accepted")

    events = [json.loads(line) for line in EVENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not any(event.get("event") == "delivery" for event in events):
        raise AssertionError("Event log does not contain delivery event")
    if not any(event.get("to") == "MASS_ADAPTATION" for event in events):
        raise AssertionError("Event log does not contain MASS_ADAPTATION transition")

    replay = json.loads(REPLAY.read_text(encoding="utf-8"))
    if replay["frame_count"] <= 0:
        raise AssertionError("Mass adaptation replay has no frames")

    print("[OK] mass adaptation demo regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
