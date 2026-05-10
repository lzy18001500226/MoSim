#!/usr/bin/env python3
"""Regression checks for the project metrics script."""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "tests" / "fixtures" / "sample_tracking.csv"

REQUIRED_METRICS = [
    "position_rmse_m",
    "max_position_error_m",
    "steady_state_error_m",
    "settling_time_s",
    "disturbance_peak_error_m",
    "disturbance_recovery_time_s",
    "overshoot_max_pct",
    "control_energy",
    "control_smoothness",
    "saturation_ratio",
    "minimum_altitude_m",
    "constraint_violation_count",
    "tracking_score",
    "robustness_score",
    "safety_score",
    "energy_score",
    "smoothness_score",
    "fault_tolerance_score",
    "total_health_score",
]


def main() -> int:
    temp_dir = ROOT / ".tmp" / f"metrics_{uuid4().hex}"
    try:
        output = temp_dir / "sample_tracking_metrics.json"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "calc_metrics.py"),
                str(RAW),
                str(output),
                "sample_tracking",
                "fixture",
            ],
            check=True,
            cwd=ROOT,
        )
        metrics = json.loads(output.read_text(encoding="utf-8"))
    finally:
        if temp_dir.exists():
            for item in sorted(temp_dir.glob("*"), reverse=True):
                item.unlink()
            temp_dir.rmdir()
        tmp_root = ROOT / ".tmp"
        if tmp_root.exists() and not any(tmp_root.iterdir()):
            tmp_root.rmdir()
    missing = [name for name in REQUIRED_METRICS if name not in metrics]
    if missing:
        raise AssertionError(f"Missing metrics: {', '.join(missing)}")

    if metrics["row_count"] != 11:
        raise AssertionError(f"Unexpected row_count: {metrics['row_count']}")
    if not math.isclose(metrics["position_rmse_m"], 0.019540168418367847, rel_tol=1e-9):
        raise AssertionError(f"Unexpected RMSE: {metrics['position_rmse_m']}")
    if metrics["settling_time_s"] is not None:
        raise AssertionError("Short fixture should not report a 2 s settling time")
    if metrics["total_health_score"] < 0.0 or metrics["total_health_score"] > 100.0:
        raise AssertionError(f"Invalid health score: {metrics['total_health_score']}")

    print("[OK] metrics regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
