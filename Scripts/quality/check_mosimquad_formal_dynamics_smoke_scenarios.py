#!/usr/bin/env python3
"""Validate formal MoSimQuadrotorModel Dynamics smoke scenario bindings.

This is a static checker. It does not call MWORKS, Sysplorer, MCP,
check_model, SimulateModel, or any GUI/window surface.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = ROOT / "Config" / "scenarios" / "diagnostics"
PROBE_PLAN = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260722_mosimquad_model_root_consolidation/live_gate_runner"
    / "result_variable_probe_plan.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260722_mosimquad_model_root_consolidation/dynamics_smoke_scenario_bindings"
    / "static_validation_summary.json"
)

sys.path.insert(0, str(ROOT / "Scripts" / "mworks"))
from run_mworks_scenario import read_yaml, scenario_command  # noqa: E402


class Args:
    def __init__(self, scenario: Path) -> None:
        self.scenario = scenario
        self.stop_time: float | None = None
        self.evidence_level: str | None = None
        self.wrapper: str | None = None
        self.no_gui_result_viewer = True
        self.no_gui_open = True
        self.gui_reset_windows = False
        self.gui_review_stop_time: float | None = None
        self.gui_review_full_time = False
        self.gui_review_interval: float | None = None
        self.gui_review_native_result_dir: Path | None = None
        self.shutdown_session = False
        self.allow_readable_result_after_simulate_false = False


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_probe_plan(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def add_finding(findings: list[dict[str, Any]], code: str, message: str, target: str | None = None) -> None:
    finding: dict[str, Any] = {"code": code, "message": message}
    if target:
        finding["target"] = target
    findings.append(finding)


def expected_simulate_probes(probe_plan: dict[str, Any]) -> dict[str, list[str]]:
    probes: dict[str, list[str]] = {}
    for item in probe_plan.get("probes", []):
        if item.get("probe_phase") != "after_simulate_model":
            continue
        target = item.get("target")
        variables = item.get("expected_result_variables", [])
        if isinstance(target, str) and isinstance(variables, list):
            probes[target] = [str(variable) for variable in variables]
    return probes


def load_scenarios(scenario_dir: Path) -> dict[str, dict[str, Any]]:
    scenarios: dict[str, dict[str, Any]] = {}
    for path in sorted(scenario_dir.glob("mosimquad_dynamics_*_smoke.yaml")):
        config = read_yaml(path)
        model = config.get("model", {})
        if not isinstance(model, dict):
            continue
        model_name = model.get("model_name")
        if isinstance(model_name, str):
            scenarios[model_name] = {"path": path, "config": config}
    return scenarios


def validate_binding(
    target: str,
    expected_variables: list[str],
    scenario_info: dict[str, Any],
    findings: list[dict[str, Any]],
) -> dict[str, Any]:
    path = scenario_info["path"]
    config = scenario_info["config"]
    model = config.get("model", {})
    simulation = config.get("simulation", {})
    result = config.get("result", {})

    if model.get("source_package") != "MoSimQuadrotorModel":
        add_finding(findings, "wrong_source_package", "scenario is not marked as MoSimQuadrotorModel", target)
    if model.get("live_load_strategy") != "minimal_dynamics_only":
        add_finding(
            findings,
            "missing_minimal_dynamics_strategy",
            "formal dynamics smoke must explicitly request the minimal Dynamics load strategy",
            target,
        )
    if model.get("base_model_path_hint") != "Models/MoSimQuadrotorModel/package.mo":
        add_finding(findings, "wrong_base_model_path_hint", "scenario does not load the canonical formal root", target)
    if model.get("model_path_hint") != "Models/MoSimQuadrotorModel/package.mo":
        add_finding(findings, "wrong_model_path_hint", "scenario does not identify the canonical MoSim package", target)
    if config.get("controller_id") != "diagnostics_no_controller":
        add_finding(findings, "wrong_controller_id", "formal dynamics smoke must not imply a controller", target)
    if config.get("evidence_level") != "future_live_mworks_formal_dynamics_smoke_contract":
        add_finding(findings, "wrong_evidence_level", "scenario evidence level must stay future-live smoke contract", target)
    if float(simulation.get("stop_time_s", -1)) != 0.25:
        add_finding(findings, "wrong_stop_time", "formal dynamics smoke must preserve the 0.25 s smoke horizon", target)

    scenario_expected = result.get("expected_result_variables", [])
    if not isinstance(scenario_expected, list) or not scenario_expected:
        add_finding(findings, "missing_expected_result_variables", "scenario must declare exportable smoke variables", target)
        scenario_expected = []

    extra_variables = result.get("extra_variables", {})
    if not isinstance(extra_variables, dict):
        add_finding(findings, "extra_variables_not_mapping", "result.extra_variables must be a mapping", target)
        extra_values: set[str] = set()
    else:
        extra_values = {str(value) for value in extra_variables.values()}
    missing_extra = sorted({str(variable) for variable in scenario_expected} - extra_values)
    if missing_extra:
        add_finding(
            findings,
            "missing_extra_variable_mapping",
            "scenario expected variables are not all mapped into result.extra_variables",
            target,
        )

    command = scenario_command(Args(scenario=path), config)
    command_text = " ".join(command)
    required_fragments = [
        "--model-file",
        "Models\\MoSimQuadrotorModel\\package.mo",
        "--no-gui-result-viewer",
        "--no-gui-open",
    ]
    for fragment in required_fragments:
        if fragment not in command_text:
            add_finding(findings, "dry_run_command_fragment_missing", f"missing command fragment {fragment!r}", target)

    return {
        "target": target,
        "scenario_file": rel(path),
        "live_load_strategy": model.get("live_load_strategy"),
        "probe_plan_expected_variables": expected_variables,
        "expected_result_variables": scenario_expected,
        "dry_run_command": command,
        "missing_extra_variable_mappings": missing_extra,
    }


def validate(scenario_dir: Path, probe_plan_path: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    probe_plan = read_probe_plan(probe_plan_path)
    expected = expected_simulate_probes(probe_plan)
    scenarios = load_scenarios(scenario_dir)

    expected_targets = set(expected)
    scenario_targets = set(scenarios)
    for target in sorted(expected_targets - scenario_targets):
        add_finding(findings, "missing_scenario", "no diagnostics scenario YAML found for simulate target", target)
    for target in sorted(scenario_targets - expected_targets):
        add_finding(findings, "unexpected_scenario", "diagnostics smoke scenario is not in 024 simulate probe plan", target)

    bindings: list[dict[str, Any]] = []
    for target in sorted(expected_targets & scenario_targets):
        bindings.append(validate_binding(target, expected[target], scenarios[target], findings))

    return {
        "schema": "mosim.mworks.formal_dynamics_smoke_scenario_bindings.v1",
        "status": "passed" if not findings else "failed",
        "static_only": True,
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "probe_plan": rel(probe_plan_path),
        "scenario_dir": rel(scenario_dir),
        "expected_simulate_target_count": len(expected_targets),
        "scenario_target_count": len(scenario_targets),
        "bindings": bindings,
        "runner_support_status": "minimal_dynamics_strategy_consumed",
        "runner_support_boundary": [
            "Scenario YAML now declares model.live_load_strategy=minimal_dynamics_only.",
            "run_mworks_scenario loads the single canonical MoSimQuadrotorModel root; its embedded Plant and Dynamics remain in one namespace.",
            "The generated live command does not load an external QuadrotorModel package, a generated second package root, or a legacy compatibility package.",
            "Do not treat this as check_model or SimulateModel evidence until a live run succeeds.",
        ],
        "findings": findings,
        "claim_boundary": [
            "This checker validates future live scenario bindings only.",
            "It does not run or prove MWORKS load, check_model, SimulateModel, result variables, controller performance, mission success, or closed_loop.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario-dir", type=Path, default=SCENARIO_DIR)
    parser.add_argument("--probe-plan", type=Path, default=PROBE_PLAN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    scenario_dir = args.scenario_dir if args.scenario_dir.is_absolute() else ROOT / args.scenario_dir
    probe_plan = args.probe_plan if args.probe_plan.is_absolute() else ROOT / args.probe_plan
    output = args.output if args.output.is_absolute() else ROOT / args.output
    summary = validate(scenario_dir, probe_plan)
    write_json(output, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
