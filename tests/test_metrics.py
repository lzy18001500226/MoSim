#!/usr/bin/env python3
"""Regression checks for the project metrics script."""

from __future__ import annotations

import json
import math
import importlib.util
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
    "control_energy_per_second",
    "control_smoothness",
    "control_smoothness_per_second",
    "saturation_ratio",
    "minimum_altitude_m",
    "constraint_violation_count",
    "constraint_violation_rate_hz",
    "altitude_violation_rate_hz",
    "tilt_violation_rate_hz",
    "sample_rate_hz",
    "tracking_score",
    "robustness_score",
    "safety_score",
    "energy_score",
    "smoothness_score",
    "fault_tolerance_score",
    "total_health_score",
]


def load_metrics_module():
    spec = importlib.util.spec_from_file_location("calc_metrics", ROOT / "scripts" / "calc_metrics.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load calc_metrics.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_metrics_regression() -> None:
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
    if not math.isclose(metrics["sample_rate_hz"], 10.0, rel_tol=1e-9):
        raise AssertionError(f"Unexpected sample_rate_hz: {metrics['sample_rate_hz']}")
    if not math.isclose(metrics["position_rmse_m"], 0.019540168418367847, rel_tol=1e-9):
        raise AssertionError(f"Unexpected RMSE: {metrics['position_rmse_m']}")
    if not math.isclose(
        metrics["control_energy_per_second"],
        metrics["control_energy"] / metrics["duration_s"],
        rel_tol=1e-12,
    ):
        raise AssertionError("control_energy_per_second is inconsistent")
    if not math.isclose(
        metrics["control_smoothness_per_second"],
        metrics["control_smoothness"] / metrics["duration_s"],
        rel_tol=1e-12,
    ):
        raise AssertionError("control_smoothness_per_second is inconsistent")
    if metrics["settling_time_s"] is not None:
        raise AssertionError("Short fixture should not report a 2 s settling time")
    if metrics["total_health_score"] < 0.0 or metrics["total_health_score"] > 100.0:
        raise AssertionError(f"Invalid health score: {metrics['total_health_score']}")


def test_metrics_rejects_empty_input() -> None:
    module = load_metrics_module()
    empty_data = {
        "time": [],
        "x": [],
        "y": [],
        "z": [],
        "x_ref": [],
        "y_ref": [],
        "z_ref": [],
        "roll": [],
        "pitch": [],
        "yaw": [],
        "u1": [],
        "u2": [],
        "u3": [],
        "u4": [],
    }
    try:
        module.compute_metrics(empty_data, ROOT / "empty.csv", "empty", "fixture")
    except ValueError as exc:
        if "no data rows" not in str(exc):
            raise AssertionError(f"Unexpected error message: {exc}") from exc
    else:
        raise AssertionError("Empty metrics input should fail")


def main() -> int:
    test_metrics_regression()
    test_metrics_rejects_empty_input()
    print("[OK] metrics regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
