#!/usr/bin/env python3
"""Regression checks for A* obstacle planning reference generation."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH_CSV = ROOT / "results" / "raw" / "path_planning_obstacle_corridor.csv"
REFERENCE = ROOT / "results" / "raw" / "reference_planning_obstacle_corridor.csv"
METRICS = ROOT / "results" / "metrics" / "planning_obstacle_corridor.json"
REPLAY = ROOT / "results" / "replay" / "planning_obstacle_corridor.json"


def main() -> int:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_obstacle_planning_reference.py")],
        cwd=ROOT,
        check=True,
    )
    with PATH_CSV.open(newline="", encoding="utf-8") as handle:
        path_rows = list(csv.DictReader(handle))
    if len(path_rows) < 4:
        raise AssertionError(f"Expected a non-trivial obstacle path, got {len(path_rows)} nodes")

    with REFERENCE.open(newline="", encoding="utf-8") as handle:
        ref_rows = list(csv.DictReader(handle))
    if len(ref_rows) < 100:
        raise AssertionError(f"Expected at least 100 reference rows, got {len(ref_rows)}")
    required = {"time", "x_ref", "y_ref", "z_ref", "vx_ref", "vy_ref", "vz_ref", "yaw_ref"}
    missing = required.difference(ref_rows[0])
    if missing:
        raise AssertionError(f"Missing obstacle reference columns: {sorted(missing)}")

    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    if metrics["obstacle_violation_count"] != 0:
        raise AssertionError(f"Obstacle violations found: {metrics['obstacle_violation_count']}")
    if metrics["minimum_obstacle_distance_m"] < metrics["safety_margin_m"]:
        raise AssertionError("Obstacle clearance is below safety margin")
    if metrics["final_trackability_score"] < 0.8:
        raise AssertionError(f"Trackability score too low: {metrics['final_trackability_score']}")
    if not metrics["accepted"]:
        raise AssertionError("Obstacle planning metrics were not accepted")

    replay = json.loads(REPLAY.read_text(encoding="utf-8"))
    if replay["frame_count"] <= 0 or not replay.get("obstacles"):
        raise AssertionError("Obstacle replay is missing frames or obstacle metadata")

    print("[OK] obstacle planning regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
