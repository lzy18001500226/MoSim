#!/usr/bin/env python3
"""Focused regression test for the three-UAV PX4CTRL ECBF safety-result audit."""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = ROOT / "Scripts" / "planning" / "audit_three_uav_openblocks_px4ctrl_ecbf_safety_result.py"


def load_audit_module():
    spec = importlib.util.spec_from_file_location("ecbf_safety_audit", AUDIT_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Could not load audit module: {AUDIT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def row(sample: int) -> dict[str, float]:
    uav1 = (0.0, 0.0, 1.0)
    uav2 = (1.05, 0.0, 1.0)
    uav3 = (0.0, 3.0, 1.0)
    nominal1 = (0.0, 0.0, 1.0)
    nominal2 = (1.4, 0.0, 1.0)
    nominal3 = (0.0, 3.0, 1.0)
    safe1 = (-0.025, 0.0, 1.0)
    safe2 = (1.075, 0.0, 1.0)
    safe3 = (0.0, 3.0, 1.0)
    payload: dict[str, float] = {
        "time_s": float(sample),
        "uav1_tracking_error_m": 0.025,
        "uav2_tracking_error_m": 0.025,
        "uav3_tracking_error_m": 0.0,
        "minimum_pair_distance_m": 1.05,
        "formation_distance_error_m": 0.45,
        "clearance_lower_bound_m": 0.10,
        "minimum_predicted_pair_distance_m": 1.10,
        "safety_active_pair_count": 1.0,
        "safety_maximum_reference_offset_m": 0.325,
        "safety_maximum_ecbf_residual_m2_s2": 0.2,
        "safety_correction_saturated": 0.0,
        "nominal_formation_deviation_m": 0.30,
    }
    for index, values in enumerate((uav1, uav2, uav3), start=1):
        for axis, value in zip("xyz", values):
            payload[f"uav{index}_{axis}_m"] = value
    for index, values in enumerate((nominal1, nominal2, nominal3), start=1):
        for axis, value in zip("xyz", values):
            payload[f"uav{index}_nominal_ref_{axis}_m"] = value
    for index, values in enumerate((safe1, safe2, safe3), start=1):
        for axis, value in zip("xyz", values):
            payload[f"uav{index}_safe_ref_{axis}_m"] = value
    return payload


def main() -> int:
    audit_module = load_audit_module()
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        raw = root / "result.csv"
        planning = root / "planning.json"
        rows = [row(sample) for sample in range(12)]
        with raw.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        planning.write_text(
            json.dumps({"schedule": {"minimum_pair_distance_m": 1.2}}),
            encoding="utf-8",
        )
        metrics = audit_module.audit(raw, planning)

    assert metrics["accepted"] is True
    assert metrics["status"] == "accepted_for_pairwise_safety_comparison"
    assert math.isclose(metrics["minimum_actual_pair_distance_m"], 1.05)
    assert math.isclose(metrics["minimum_safe_reference_pair_distance_m"], 1.1)
    assert metrics["intervention_sample_count"] == 12
    assert metrics["gates"]["safety_intervened"] is True
    assert metrics["gates"]["pair_separation"] is True
    print("[OK] Three-UAV PX4CTRL ECBF safety-result audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
