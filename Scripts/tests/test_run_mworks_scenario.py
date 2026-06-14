#!/usr/bin/env python3
"""Regression checks for scenario YAML to MCP command translation."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "Scripts" / "mworks" / "run_mworks_scenario.py"
    spec = importlib.util.spec_from_file_location("run_mworks_scenario", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load run_mworks_scenario.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Args:
    scenario = ROOT / "Config" / "scenarios" / "official" / "example1_pid_baseline.yaml"
    stop_time = None
    allow_overwrite_evidence = False
    evidence_level = None
    wrapper = None
    no_gui_result_viewer = False
    gui_reset_windows = False
    shutdown_session = False
    no_quality_gate = False
    allow_needs_iteration = False
    min_rmse_improvement_pct = 0.5
    no_gui_open = False
    gui_review_stop_time = None
    gui_review_full_time = False
    gui_review_interval = None
    gui_review_native_result_dir = None
    allow_readable_result_after_simulate_false = False


def test_run_mworks_scenario_command_regression() -> None:
    module = load_module()
    config = module.read_yaml(Args.scenario)
    command = module.scenario_command(Args, config)
    joined = " ".join(command)
    if "--target-time 0,50" not in joined:
        raise AssertionError(f"Official target time not preserved: {joined}")
    if "--evidence-level real_sysplorer_mcp_full_baseline" not in joined:
        raise AssertionError(f"Official evidence level not preserved: {joined}")
    if "official_example1_pid_baseline.csv" not in joined:
        raise AssertionError("Official baseline raw path missing")
    if "Results/smoke" in joined:
        raise AssertionError("Official run must not write into removed smoke result path")
    if config.get("generate_replay_html"):
        raise AssertionError("Default official scenario should not request replay HTML generation")


def test_run_mworks_scenario_stop_time_override() -> None:
    module = load_module()
    config = module.read_yaml(Args.scenario)
    args = Args()
    args.stop_time = 10.0
    command = module.scenario_command(args, config)
    joined = " ".join(command)
    if "--target-time 0,10" not in joined:
        raise AssertionError(f"--stop-time should override scenario stop_time_s: {joined}")


def test_run_mworks_scenario_wrapper_passthrough() -> None:
    module = load_module()
    config = module.read_yaml(Args.scenario)
    args = Args()
    args.wrapper = r"C:\Users\HP\mcp-wrappers\sysplorer_mcp.cmd"
    command = module.scenario_command(args, config)
    joined = " ".join(command)
    if r"--wrapper C:\Users\HP\mcp-wrappers\sysplorer_mcp.cmd" not in joined:
        raise AssertionError(f"Wrapper path should be passed to run_sysplorer_mcp_smoke.py: {joined}")


def test_run_mworks_scenario_no_gui_result_viewer_passthrough() -> None:
    module = load_module()
    config = module.read_yaml(Args.scenario)
    args = Args()
    args.no_gui_result_viewer = True
    command = module.scenario_command(args, config)
    joined = " ".join(command)
    if "--no-gui-result-viewer" not in joined:
        raise AssertionError(f"GUI result viewer flag should be passed through: {joined}")


def test_run_mworks_scenario_gui_reset_windows_passthrough() -> None:
    module = load_module()
    config = module.read_yaml(Args.scenario)
    args = Args()
    args.gui_reset_windows = True
    command = module.scenario_command(args, config)
    joined = " ".join(command)
    if "--gui-reset-windows" not in joined:
        raise AssertionError(f"GUI reset flag should be passed through: {joined}")


def test_run_mworks_scenario_gui_review_passthrough() -> None:
    module = load_module()
    config = module.read_yaml(Args.scenario)
    args = Args()
    args.gui_review_stop_time = 3.0
    args.gui_review_native_result_dir = Path("Results/native_result_cache/gui_review_probe")
    command = module.scenario_command(args, config)
    joined = " ".join(command)
    if "--gui-review-stop-time 3" not in joined:
        raise AssertionError(f"GUI review stop time should be passed through: {joined}")
    if "--gui-review-native-result-dir Results/native_result_cache/gui_review_probe" not in joined.replace("\\", "/"):
        raise AssertionError(f"GUI review native result dir should be passed through: {joined}")


def test_run_mworks_scenario_full_gui_review_passthrough() -> None:
    module = load_module()
    config = module.read_yaml(Args.scenario)
    args = Args()
    args.gui_review_full_time = True
    args.gui_review_interval = 0.5
    args.gui_review_native_result_dir = Path("Results/native_result_cache/gui_review_full_probe")
    command = module.scenario_command(args, config)
    joined = " ".join(command)
    if "--gui-review-full-time" not in joined:
        raise AssertionError(f"Full GUI review flag should be passed through: {joined}")
    if "--gui-review-interval 0.5" not in joined:
        raise AssertionError(f"GUI review interval should be passed through: {joined}")
    if "--gui-review-native-result-dir Results/native_result_cache/gui_review_full_probe" not in joined.replace("\\", "/"):
        raise AssertionError(f"GUI review native result dir should be passed through: {joined}")


def test_run_mworks_scenario_refuses_short_smoke_overwrite() -> None:
    module = load_module()
    config = module.read_yaml(Args.scenario)
    args = Args()
    args.stop_time = 1.0
    command = module.scenario_command(args, config)
    try:
        module.require_non_destructive_smoke(args, config, command)
    except RuntimeError as exc:
        if "Refusing to run a shortened smoke simulation" not in str(exc):
            raise
        return
    raise AssertionError("Shortened smoke run should not overwrite existing official evidence")


def test_run_mworks_scenario_minimal_dynamics_strategy_generates_load_tree() -> None:
    module = load_module()
    scenario = ROOT / "Config" / "scenarios" / "diagnostics" / "mosimquad_dynamics_hover_smoke.yaml"
    config = module.read_yaml(scenario)
    args = Args()
    args.scenario = scenario
    args.no_gui_result_viewer = True
    args.no_gui_open = True
    command = module.scenario_command(args, config)
    joined = " ".join(command).replace("\\", "/")
    if "Results/generated_mworks/minimal_dynamics_only/QuadrotorExperiments/package.mo" not in joined:
        raise AssertionError(f"minimal strategy should load generated dependency package first: {joined}")
    if "Results/generated_mworks/minimal_dynamics_only/MoSimQuadrotorModel/package.mo" not in joined:
        raise AssertionError(f"minimal strategy should load generated formal package as extra package: {joined}")
    if "Models/MoSimQuadrotorModel/package.mo" in joined:
        raise AssertionError(f"minimal strategy must not broad-load the formal top-level package: {joined}")
    generated_root = ROOT / "Results" / "generated_mworks" / "minimal_dynamics_only"
    if not (generated_root / "MoSimQuadrotorModel" / "Dynamics" / "HoverSmoke.mo").exists():
        raise AssertionError("generated formal Dynamics smoke file missing")
    order_text = (generated_root / "MoSimQuadrotorModel" / "package.order").read_text(encoding="utf-8")
    if order_text.strip() != "Dynamics":
        raise AssertionError(f"generated formal package.order must contain only Dynamics, got: {order_text!r}")
    if "--variable-profile diagnostics_declared" not in joined:
        raise AssertionError(f"formal Dynamics smoke must export declared variables only: {joined}")
    if "--metrics-profile diagnostics_smoke" not in joined:
        raise AssertionError(f"formal Dynamics smoke must use diagnostics smoke metrics: {joined}")


def test_formal_dynamics_postprocess_summary_uses_diagnostics_contract() -> None:
    module = load_module()
    scenario = ROOT / "Config" / "scenarios" / "diagnostics" / "mosimquad_dynamics_hover_smoke.yaml"
    config = module.read_yaml(scenario)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        raw_file = tmp_root / "raw.csv"
        metrics_file = tmp_root / "metrics.json"
        summary_file = tmp_root / "summary.json"
        raw_file.write_text(
            "time,dynamics_total_thrust,dynamics_total_moment_body,dynamics_hover_thrust_error,dynamics_omega,dynamics_thrust\n"
            "0,1,0,0,100,0.25\n"
            "0.1,1,0,0,100,0.25\n",
            encoding="utf-8",
            newline="\n",
        )
        metrics_file.write_text(
            '{"metrics_profile":"diagnostics_smoke","claim_role":"dynamics_smoke_only","valid":true}\n',
            encoding="utf-8",
        )
        config["result"]["postprocess_summary"] = str(summary_file)
        module.write_diagnostics_smoke_postprocess_summary(config, raw_file, metrics_file)
        payload = json.loads(summary_file.read_text(encoding="utf-8"))
        if not payload["valid"]:
            raise AssertionError(payload)
        if payload["claim_role"] != "dynamics_smoke_only":
            raise AssertionError(payload)
        if "no tracking RMSE/performance claim" not in payload["claim_boundary"]:
            raise AssertionError(payload)


def main() -> int:
    test_run_mworks_scenario_command_regression()
    test_run_mworks_scenario_stop_time_override()
    test_run_mworks_scenario_wrapper_passthrough()
    test_run_mworks_scenario_no_gui_result_viewer_passthrough()
    test_run_mworks_scenario_gui_reset_windows_passthrough()
    test_run_mworks_scenario_gui_review_passthrough()
    test_run_mworks_scenario_full_gui_review_passthrough()
    test_run_mworks_scenario_refuses_short_smoke_overwrite()
    test_run_mworks_scenario_minimal_dynamics_strategy_generates_load_tree()
    test_formal_dynamics_postprocess_summary_uses_diagnostics_contract()
    print("[OK] run_mworks_scenario command regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
