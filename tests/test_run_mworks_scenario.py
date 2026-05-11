#!/usr/bin/env python3
"""Regression checks for scenario YAML to MCP command translation."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "run_mworks_scenario.py"
    spec = importlib.util.spec_from_file_location("run_mworks_scenario", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load run_mworks_scenario.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Args:
    scenario = ROOT / "scenarios" / "smoke" / "example1_pid_mcp_smoke.yaml"
    stop_time = None
    evidence_level = None
    shutdown_session = False
    no_quality_gate = False
    allow_needs_iteration = False
    min_rmse_improvement_pct = 0.5


def test_run_mworks_scenario_command_regression() -> None:
    module = load_module()
    config = module.read_yaml(Args.scenario)
    command = module.scenario_command(Args, config)
    joined = " ".join(command)
    if "--target-time 0,1" not in joined:
        raise AssertionError(f"Smoke target time not preserved: {joined}")
    if "--evidence-level real_sysplorer_mcp_smoke" not in joined:
        raise AssertionError(f"Smoke evidence level not preserved: {joined}")
    if "official_example1_pid_baseline.csv" in joined:
        raise AssertionError("Smoke run must not write into formal baseline raw path")
    if "mworks_mcp_example1_pid_smoke.csv" not in joined:
        raise AssertionError("Smoke raw path missing")
    if config.get("generate_replay_html"):
        raise AssertionError("Default smoke scenario should not request replay HTML generation")


def test_run_mworks_scenario_stop_time_override() -> None:
    module = load_module()
    config = module.read_yaml(Args.scenario)
    args = Args()
    args.stop_time = 10.0
    command = module.scenario_command(args, config)
    joined = " ".join(command)
    if "--target-time 0,10" not in joined:
        raise AssertionError(f"--stop-time should override scenario stop_time_s: {joined}")


def main() -> int:
    test_run_mworks_scenario_command_regression()
    test_run_mworks_scenario_stop_time_override()
    print("[OK] run_mworks_scenario command regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
