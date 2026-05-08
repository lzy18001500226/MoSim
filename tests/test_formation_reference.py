#!/usr/bin/env python3
"""Regression checks for formation reference generation."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "results" / "raw" / "reference_formation_triangle_switch.csv"
METRICS = ROOT / "results" / "metrics" / "formation_triangle_switch.json"
REPLAY = ROOT / "results" / "replay" / "formation_triangle_switch.json"


def main() -> int:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_formation_reference.py")],
        cwd=ROOT,
        check=True,
    )
    with REFERENCE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) < 100:
        raise AssertionError(f"Expected at least 100 formation rows, got {len(rows)}")
    required = {"time", "formation_mode", "uav_0_x_ref", "uav_1_x_ref", "uav_2_x_ref"}
    missing = required.difference(rows[0])
    if missing:
        raise AssertionError(f"Missing formation columns: {sorted(missing)}")
    modes = {row["formation_mode"] for row in rows}
    if "line" not in modes or "triangle" not in modes:
        raise AssertionError(f"Expected triangle and line modes, got {sorted(modes)}")

    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    if metrics["minimum_inter_uav_distance"] < metrics["safety_distance_m"]:
        raise AssertionError("Formation violates safety distance")
    if metrics["formation_error_rmse"] > 1e-9:
        raise AssertionError(f"Unexpected formation error: {metrics['formation_error_rmse']}")
    replay = json.loads(REPLAY.read_text(encoding="utf-8"))
    if replay["frame_count"] <= 0:
        raise AssertionError("Formation replay has no frames")

    print("[OK] formation reference regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
