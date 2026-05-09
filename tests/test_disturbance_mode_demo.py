#!/usr/bin/env python3
"""Regression checks for wind disturbance mode-switch demo generation."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results" / "raw" / "wind_nmpc_indi_l1.csv"
METRICS = ROOT / "results" / "metrics" / "wind_nmpc_indi_l1.json"
EVENTS = ROOT / "results" / "logs" / "wind_nmpc_indi_l1_events.jsonl"
REPLAY = ROOT / "results" / "replay" / "wind_nmpc_indi_l1.json"


def main() -> int:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_disturbance_mode_demo.py")],
        cwd=ROOT,
        check=True,
    )
    with RAW.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) < 1000:
        raise AssertionError(f"Expected at least 1000 wind demo rows, got {len(rows)}")
    required = {
        "time",
        "x_ref",
        "y_ref",
        "z_ref",
        "acc_residual_raw_x_m_s2",
        "disturbance_hat_x_m_s2",
        "disturbance_comp_x_m_s2",
        "controller_mode",
        "disturbance_type",
    }
    missing = required.difference(rows[0])
    if missing:
        raise AssertionError(f"Missing wind demo columns: {sorted(missing)}")
    modes = {row["controller_mode"] for row in rows}
    if "WIND_REJECTION" not in modes:
        raise AssertionError(f"Expected WIND_REJECTION mode, got {sorted(modes)}")

    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    if not metrics["wind_rejection_entered"]:
        raise AssertionError("Mode switch to WIND_REJECTION was not detected")
    if metrics["residual_reduction_pct"] < 20.0:
        raise AssertionError(f"Residual reduction too low: {metrics['residual_reduction_pct']}")
    if not metrics["accepted"]:
        raise AssertionError("Wind disturbance demo was not accepted")

    events = [json.loads(line) for line in EVENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not any(event.get("to") == "WIND_REJECTION" for event in events):
        raise AssertionError("Event log does not contain WIND_REJECTION transition")

    replay = json.loads(REPLAY.read_text(encoding="utf-8"))
    if replay["frame_count"] <= 0:
        raise AssertionError("Wind disturbance replay has no frames")

    print("[OK] disturbance mode demo regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
