#!/usr/bin/env python3
"""Regression checks for scenario quality gate decisions."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import csv
import json
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]


def load_quality_module():
    path = ROOT / "scripts" / "evaluate_result_quality.py"
    spec = importlib.util.spec_from_file_location("evaluate_result_quality", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load evaluate_result_quality.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluate(scenario: str) -> dict:
    module = load_quality_module()
    scenario_path = ROOT / scenario
    config = module.read_yaml(scenario_path)
    return module.evaluate_quality(config, scenario_path, min_rmse_improvement_pct=0.5)


def test_example3_awff_sysblock_passes_figure8_gate() -> None:
    quality = evaluate("scenarios/official/example3_awff_sysblock.yaml")
    if quality["quality_status"] != "pass":
        raise AssertionError(quality)
    if quality.get("figure8_corr_x", 0.0) <= 0.98 or quality.get("figure8_corr_y", 0.0) <= 0.98:
        raise AssertionError(quality)


def test_example2_awff_sysblock_needs_iteration_without_rmse_gain() -> None:
    quality = evaluate("scenarios/official/example2_awff_sysblock.yaml")
    if quality["quality_status"] != "needs_iteration":
        raise AssertionError(quality)
    if "RMSE improvement" not in " ".join(quality["quality_issues"]):
        raise AssertionError(quality)


def test_smoke_result_is_smoke_only() -> None:
    quality = evaluate("scenarios/smoke/example1_pid_mcp_smoke.yaml")
    if quality["quality_status"] != "smoke_only":
        raise AssertionError(quality)


def test_fault_index_gate_rejects_wrong_isolation() -> None:
    module = load_quality_module()
    temp_dir = ROOT / ".tmp" / f"fault_gate_{uuid4().hex}"
    try:
        raw = temp_dir / "raw" / "fault.csv"
        metrics_path = temp_dir / "metrics" / "fault.json"
        raw.parent.mkdir(parents=True)
        metrics_path.parent.mkdir(parents=True)
        with raw.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(["time", "x", "y", "z", "x_ref", "y_ref", "z_ref", "fault_index"])
            for index in range(60):
                t = float(index)
                writer.writerow([t, 0, 0, 1, 0, 0, 1, 1])
        metrics_path.write_text(
            json.dumps(
                {
                    "valid": True,
                    "nan_count": 0,
                    "row_count": 60,
                    "duration_s": 59,
                    "position_rmse_m": 0.1,
                    "max_position_error_m": 0.1,
                    "total_health_score": 80.0,
                    "max_tilt_rad": 0.1,
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        scenario_path = temp_dir / "scenario.yaml"
        scenario_path.write_text("", encoding="utf-8")
        config = {
            "experiment_id": "fault_gate_fixture",
            "scene_id": "robust_rotor2_loss15_example1",
            "controller_id": "l1_multi_fault_isolation_sysblock",
            "simulation": {"start_time_s": 0.0, "stop_time_s": 59.0},
            "disturbance": {"expected_fault_index": 2},
            "result": {"raw_file": str(raw), "metrics_file": str(metrics_path)},
        }
        quality = module.evaluate_quality(config, scenario_path, min_rmse_improvement_pct=0.5)
    finally:
        if temp_dir.exists():
            for item in sorted(temp_dir.glob("**/*"), key=lambda p: len(p.parts), reverse=True):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    item.rmdir()
            temp_dir.rmdir()
        tmp_root = ROOT / ".tmp"
        if tmp_root.exists() and not any(tmp_root.iterdir()):
            tmp_root.rmdir()

    if quality["quality_status"] != "needs_iteration":
        raise AssertionError(quality)
    if "fault_index accuracy" not in " ".join(quality["quality_issues"]):
        raise AssertionError(quality)


def main() -> int:
    test_example3_awff_sysblock_passes_figure8_gate()
    test_example2_awff_sysblock_needs_iteration_without_rmse_gain()
    test_smoke_result_is_smoke_only()
    test_fault_index_gate_rejects_wrong_isolation()
    print("[OK] quality gate regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
