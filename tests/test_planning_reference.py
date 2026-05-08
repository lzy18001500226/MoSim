#!/usr/bin/env python3
"""Regression checks for waypoint planning reference generation."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "results" / "raw" / "reference_planning_trackable_waypoint.csv"
REPORT = ROOT / "results" / "metrics" / "trackability_planning_trackable_waypoint.json"
REPLAY = ROOT / "results" / "replay" / "planning_trackable_waypoint.json"


def main() -> int:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_planning_reference.py")],
        cwd=ROOT,
        check=True,
    )
    with REFERENCE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) < 100:
        raise AssertionError(f"Expected at least 100 reference rows, got {len(rows)}")
    required = {"time", "x_ref", "y_ref", "z_ref", "vx_ref", "vy_ref", "vz_ref", "ax_ref", "ay_ref", "az_ref", "yaw_ref"}
    missing = required.difference(rows[0])
    if missing:
        raise AssertionError(f"Missing reference columns: {sorted(missing)}")

    report = json.loads(REPORT.read_text(encoding="utf-8"))
    if report["final_trackability_score"] < 0.8:
        raise AssertionError(f"Trackability score too low: {report['final_trackability_score']}")
    if report["dynamic_violation_count"] != 0:
        raise AssertionError(f"Unexpected dynamic violations: {report['dynamic_violation_count']}")
    replay = json.loads(REPLAY.read_text(encoding="utf-8"))
    if replay["frame_count"] <= 0:
        raise AssertionError("Replay has no frames")

    print("[OK] planning reference regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
