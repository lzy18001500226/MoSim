#!/usr/bin/env python3
"""Regression checks for scenario quality gate decisions."""

from __future__ import annotations

import importlib.util
from pathlib import Path


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


def main() -> int:
    test_example3_awff_sysblock_passes_figure8_gate()
    test_example2_awff_sysblock_needs_iteration_without_rmse_gain()
    test_smoke_result_is_smoke_only()
    print("[OK] quality gate regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
