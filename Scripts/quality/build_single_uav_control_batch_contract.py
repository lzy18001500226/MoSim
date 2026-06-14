#!/usr/bin/env python3
"""Build the single-UAV control batch contract before multi-UAV work.

This is a static/read-only contract generator. It does not call MWORKS,
Sysplorer, MCP, check_model, SimulateModel, ROS2, UE, or GUI/window tools.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "Results" / "mworks_model_hygiene" / "20260611_single_uav_control_batch_contract"

SCENARIO_PATHS = [
    "Config/scenarios/official/example1_pid_baseline.yaml",
    "Config/scenarios/official/example1_awff_sysblock.yaml",
    "Config/scenarios/official/example2_pid_baseline.yaml",
    "Config/scenarios/official/example2_improved_pid.yaml",
    "Config/scenarios/official/example2_awff_sysblock_helix_tuned.yaml",
    "Config/scenarios/official/example3_pid_baseline.yaml",
    "Config/scenarios/official/example3_awff_sysblock.yaml",
    "Config/scenarios/official/example3_awff_indi_sysblock.yaml",
    "Config/scenarios/official/example3_linear_mpc_sysblock.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_pid_baseline.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml",
    "Config/scenarios/robustness/example1_wind_gust_pid_baseline.yaml",
    "Config/scenarios/robustness/example1_wind_gust_awff_sysblock.yaml",
]

REQUIRED_RESULT_KEYS = ["raw_file", "metrics_file", "mcp_log"]
CONTROL_RESULT_COLUMNS = ["time", "x", "y", "z", "x_ref", "y_ref", "z_ref"]

sys.path.insert(0, str(ROOT / "Scripts" / "mworks"))
from run_mworks_scenario import read_yaml  # noqa: E402


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def repo_path(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def add_finding(findings: list[dict[str, Any]], code: str, message: str, target: str) -> None:
    findings.append({"code": code, "message": message, "target": target})


def scenario_group(path: Path) -> str:
    parts = path.as_posix().split("/")
    if "official" in parts:
        return "official_tracking"
    if "robustness" in parts:
        return "robustness"
    return "unknown"


def validate_scenario(path: Path, all_experiment_ids: set[str], findings: list[dict[str, Any]]) -> dict[str, Any]:
    if not path.exists():
        add_finding(findings, "missing_scenario", "scenario file is missing", rel(path))
        return {"scenario": rel(path), "state": "missing"}

    config = read_yaml(path)
    experiment_id = str(config.get("experiment_id", path.stem))
    scene_id = str(config.get("scene_id", ""))
    controller_id = str(config.get("controller_id", ""))
    model = config.get("model", {})
    controller = config.get("controller", {})
    simulation = config.get("simulation", {})
    result = config.get("result", {})
    disturbance = config.get("disturbance", {})

    if not isinstance(model, dict):
        add_finding(findings, "model_not_mapping", "model field must be a mapping", rel(path))
        model = {}
    if not isinstance(controller, dict):
        controller = {}
    if not isinstance(simulation, dict):
        add_finding(findings, "simulation_not_mapping", "simulation field must be a mapping", rel(path))
        simulation = {}
    if not isinstance(result, dict):
        add_finding(findings, "result_not_mapping", "result field must be a mapping", rel(path))
        result = {}
    if not isinstance(disturbance, dict):
        disturbance = {}

    if "formation" in rel(path).lower() or "formation" in scene_id.lower():
        add_finding(findings, "formation_scope_leak", "single-UAV control batch must stop before formation", rel(path))
    if not scene_id:
        add_finding(findings, "missing_scene_id", "scene_id is missing", rel(path))
    if not controller_id:
        add_finding(findings, "missing_controller_id", "controller_id is missing", rel(path))
    if not model.get("model_name"):
        add_finding(findings, "missing_model_name", "model.model_name is missing", rel(path))
    if not model.get("model_path_hint"):
        add_finding(findings, "missing_model_path_hint", "model.model_path_hint is missing", rel(path))

    for key in REQUIRED_RESULT_KEYS:
        if not result.get(key):
            add_finding(findings, f"missing_result_{key}", f"result.{key} is missing", rel(path))
    for key in ("raw_file", "metrics_file"):
        value = str(result.get(key, ""))
        if value and repo_path(value).suffix not in {".csv", ".json"}:
            add_finding(findings, f"unexpected_{key}_suffix", f"result.{key} suffix is unexpected", rel(path))

    stop_time = float(simulation.get("stop_time_s", 0) or 0)
    step_size = float(simulation.get("step_size_s", 0) or 0)
    if stop_time <= 0:
        add_finding(findings, "invalid_stop_time", "simulation.stop_time_s must be positive", rel(path))
    if step_size <= 0:
        add_finding(findings, "invalid_step_size", "simulation.step_size_s must be positive", rel(path))

    baseline_experiment = str(controller.get("baseline_experiment", "") or "")
    inferred_baseline_experiment = ""
    if controller_id != "pid_baseline" and not baseline_experiment and scene_id:
        inferred_baseline_experiment = f"{scene_id}_pid_baseline"
    if controller_id != "pid_baseline" and not baseline_experiment:
        if inferred_baseline_experiment not in all_experiment_ids:
            add_finding(findings, "missing_baseline_experiment", "non-baseline scenario must declare or infer a batch baseline experiment", rel(path))
    baseline_for_contract = baseline_experiment or inferred_baseline_experiment
    if baseline_for_contract and baseline_for_contract not in all_experiment_ids:
        add_finding(findings, "baseline_not_in_batch", "baseline experiment is not part of this minimal batch", rel(path))

    if controller_id != "pid_baseline" and not controller.get("params_file"):
        add_finding(findings, "missing_controller_params_file", "non-baseline scenario must declare controller.params_file", rel(path))
    if controller_id.endswith("_sysblock"):
        if not controller.get("sysblock_controller_file"):
            add_finding(findings, "missing_sysblock_controller_file", "optimized controller scenario must declare sysblock_controller_file", rel(path))
        if not controller.get("graphical_sysblock_file"):
            add_finding(findings, "missing_graphical_sysblock_file", "optimized controller scenario must declare graphical_sysblock_file", rel(path))

    return {
        "scenario": rel(path),
        "state": "present",
        "group": scenario_group(path),
        "experiment_id": experiment_id,
        "scene_id": scene_id,
        "controller_id": controller_id,
        "model_name": model.get("model_name"),
        "model_path_hint": model.get("model_path_hint"),
        "baseline_experiment": baseline_for_contract,
        "baseline_source": "declared" if baseline_experiment else "inferred_same_scene_pid" if inferred_baseline_experiment else "none",
        "disturbance_type": disturbance.get("type"),
        "simulation": {
            "stop_time_s": stop_time,
            "step_size_s": step_size,
            "solver": simulation.get("solver"),
            "tolerance": simulation.get("tolerance"),
        },
        "result": {key: result.get(key) for key in ["raw_file", "metrics_file", "figure_dir", "replay_file", "mcp_log"]},
        "required_result_columns": CONTROL_RESULT_COLUMNS,
    }


def build_contract(paths: list[str]) -> dict[str, Any]:
    scenario_paths = [repo_path(path) for path in paths]
    all_experiment_ids: set[str] = set()
    for path in scenario_paths:
        if path.exists():
            try:
                all_experiment_ids.add(str(read_yaml(path).get("experiment_id", path.stem)))
            except Exception:
                pass

    findings: list[dict[str, Any]] = []
    scenarios = [validate_scenario(path, all_experiment_ids, findings) for path in scenario_paths]
    scenario_rel = [rel(path) for path in scenario_paths]
    future_command = [
        sys.executable,
        "Scripts/mworks/run_mworks_batch.py",
        "--no-gui-result-viewer",
        "--no-gui-open",
        "--continue-on-failure",
    ] + scenario_rel
    dry_run_command = [
        sys.executable,
        "Scripts/mworks/run_mworks_batch.py",
        "--dry-run",
        "--no-gui-result-viewer",
        "--no-gui-open",
        "--continue-on-failure",
    ] + scenario_rel

    coverage = {
        "official_step": any(item.get("scene_id") == "official_example1" for item in scenarios),
        "official_helix": any(item.get("scene_id") == "official_example2" for item in scenarios),
        "official_figure8": any(item.get("scene_id") == "official_example3" for item in scenarios),
        "pid_baseline": any(item.get("controller_id") == "pid_baseline" for item in scenarios),
        "awff_sysblock": any(item.get("controller_id") == "awff_sysblock" for item in scenarios),
        "linear_mpc_sysblock": any(item.get("controller_id") == "linear_mpc_sysblock" for item in scenarios),
        "single_rotor_efficiency_degradation": any(item.get("disturbance_type") == "actuator_efficiency_loss" for item in scenarios),
        "wind_gust": any(item.get("disturbance_type") == "lateral_world_force_gust" for item in scenarios),
        "formation_excluded": not any("formation" in str(item.get("scenario", "")).lower() for item in scenarios),
    }
    for key, value in coverage.items():
        if not value:
            add_finding(findings, "coverage_gap", f"required coverage is missing: {key}", "scenario_batch")

    status = "passed" if not findings else "failed"
    return {
        "schema": "mosim.mworks.single_uav_control_batch_contract.v1",
        "status": status,
        "static_only": True,
        "live_mworks_touched": False,
        "scope": "single_uav_control_before_multi_uav",
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "coverage": coverage,
        "future_live_batch_command": future_command,
        "dry_run_batch_command": dry_run_command,
        "post_live_quality_commands": [
            [sys.executable, "Scripts/results/evaluate_result_quality.py", scenario]
            for scenario in scenario_rel
        ],
        "preconditions_for_future_live_run": [
            "current MWORKS/Sysplorer/Syslab preflight is clean and not blocked by upgrade, login, license, authorization, crash, save, restart, or unknown windows",
            "formal Dynamics smoke blocker is either cleared or explicitly declared unrelated to this single-UAV control batch by PMO/user",
            "live run uses no automatic GUI result viewer and no GUI-open side paths",
            "after each live result, evaluate_result_quality.py must pass or preserve the failed result as iteration evidence",
        ],
        "claim_boundary": [
            "This contract prepares a single-UAV control batch only.",
            "It does not run MWORKS, check_model, SimulateModel, or GUI actions.",
            "It does not prove controller performance, mission success, closed_loop, or multi-UAV readiness.",
            "Formation scenarios are explicitly out of scope for this goal stage.",
        ],
        "findings": findings,
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_markdown(path: Path, contract: dict[str, Any]) -> None:
    lines = [
        "# Single-UAV Control Batch Contract",
        "",
        f"Status: `{contract['status']}`",
        f"Scenario count: `{contract['scenario_count']}`",
        "",
        "Static/read-only contract. It does not call MWORKS, Sysplorer, MCP, `check_model`, `SimulateModel`, ROS2, UE, or GUI/window tools.",
        "",
        "## Coverage",
        "",
    ]
    lines.extend(f"- `{key}`: `{value}`" for key, value in contract["coverage"].items())
    lines.extend(["", "## Scenarios", ""])
    for item in contract["scenarios"]:
        lines.append(
            f"- `{item['scenario']}` -> `{item.get('model_name')}` / `{item.get('controller_id')}`"
        )
    lines.extend(["", "## Future Live Command", "", "```powershell"])
    lines.append(" ".join(str(item) for item in contract["future_live_batch_command"]))
    lines.extend(["```", "", "## Preconditions", ""])
    lines.extend(f"- {item}" for item in contract["preconditions_for_future_live_run"])
    lines.extend(["", "## Claim Boundary", ""])
    lines.extend(f"- {item}" for item in contract["claim_boundary"])
    lines.extend(["", "## Findings", ""])
    if contract["findings"]:
        lines.extend(f"- `{item['code']}` at `{item['target']}`: {item['message']}" for item in contract["findings"])
    else:
        lines.append("- none")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("scenario", nargs="*", help="Optional scenario YAML list. Defaults to the curated single-UAV batch.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    contract = build_contract(args.scenario or SCENARIO_PATHS)
    write_json(output_dir / "single_uav_control_batch_contract.json", contract)
    write_markdown(output_dir / "single_uav_control_batch_contract.md", contract)
    print(json.dumps(contract, ensure_ascii=False, indent=2))
    return 0 if contract["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
