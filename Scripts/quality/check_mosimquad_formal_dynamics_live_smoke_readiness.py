#!/usr/bin/env python3
"""Check formal Dynamics live-smoke readiness without running MWORKS.

This checker is static/read-only. It validates that the future live smoke batch
has deterministic scenario outputs, result-variable mappings, minimal-load
runner support, and an explicit GUI-blocker gate.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = ROOT / "Config" / "scenarios" / "diagnostics"
SCENARIO_CHECK = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260611_mosimquad_formal_dynamics_smoke_scenario_bindings"
    / "static_validation_summary.json"
)
BATCH_MANIFEST = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260611_mosimquad_formal_dynamics_smoke_batch_manifest"
    / "formal_dynamics_smoke_batch_manifest.json"
)
LIVE_PREFLIGHT_BLOCKER = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260611_mosimquad_formal_dynamics_live_preflight"
    / "live_preflight_blocker_summary.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260611_mosimquad_formal_dynamics_live_smoke_readiness"
    / "live_smoke_readiness.json"
)

sys.path.insert(0, str(ROOT / "Scripts" / "mworks"))
from run_mworks_scenario import read_yaml  # noqa: E402


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def add_finding(findings: list[dict[str, Any]], code: str, message: str, target: str | None = None) -> None:
    item: dict[str, Any] = {"code": code, "message": message}
    if target:
        item["target"] = target
    findings.append(item)


def parent_paths(paths: list[str]) -> list[str]:
    parents: set[str] = set()
    for item in paths:
        path = Path(item)
        if path.parent != Path("."):
            parents.add(path.parent.as_posix())
    return sorted(parents)


def validate_output_contract(scenario_path: Path, findings: list[dict[str, Any]]) -> dict[str, Any]:
    config = read_yaml(scenario_path)
    experiment_id = str(config.get("experiment_id") or scenario_path.stem)
    result = config.get("result", {})
    model = config.get("model", {})
    simulation = config.get("simulation", {})
    if not isinstance(result, dict):
        add_finding(findings, "result_not_mapping", "scenario result field must be a mapping", rel(scenario_path))
        result = {}
    if not isinstance(model, dict):
        add_finding(findings, "model_not_mapping", "scenario model field must be a mapping", rel(scenario_path))
        model = {}
    if not isinstance(simulation, dict):
        add_finding(findings, "simulation_not_mapping", "scenario simulation field must be a mapping", rel(scenario_path))
        simulation = {}

    raw_file = str(result.get("raw_file") or "")
    metrics_file = str(result.get("metrics_file") or "")
    mcp_log = str(result.get("mcp_log") or "")
    expected = [str(item) for item in result.get("expected_result_variables", []) or []]
    extra_variables = result.get("extra_variables", {})
    if not isinstance(extra_variables, dict):
        add_finding(findings, "extra_variables_not_mapping", "result.extra_variables must be a mapping", rel(scenario_path))
        extra_variables = {}
    extra_values = {str(value) for value in extra_variables.values()}

    required_prefix = f"Results/diagnostics/mosimquad_formal_dynamics_smoke/{experiment_id}/"
    for key, path_text, suffix in [
        ("raw_file", raw_file, f"/raw/{experiment_id}.csv"),
        ("metrics_file", metrics_file, f"/metrics/{experiment_id}.json"),
        ("mcp_log", mcp_log, f"/logs/sysplorer_{experiment_id}.jsonl"),
    ]:
        if not path_text:
            add_finding(findings, f"missing_{key}", f"scenario result.{key} is missing", rel(scenario_path))
            continue
        if not path_text.startswith(required_prefix):
            add_finding(findings, f"wrong_{key}_prefix", f"scenario result.{key} is outside the formal smoke result tree", rel(scenario_path))
        if not path_text.endswith(suffix):
            add_finding(findings, f"wrong_{key}_suffix", f"scenario result.{key} has an unexpected filename", rel(scenario_path))

    missing_extra = sorted(set(expected) - extra_values)
    if missing_extra:
        add_finding(findings, "missing_extra_variable_mapping", "expected variables are not all mapped to extra_variables", rel(scenario_path))

    if model.get("live_load_strategy") != "minimal_dynamics_only":
        add_finding(findings, "missing_minimal_dynamics_strategy", "scenario must request minimal_dynamics_only", rel(scenario_path))
    if config.get("evidence_level") != "future_live_mworks_formal_dynamics_smoke_contract":
        add_finding(findings, "wrong_evidence_level", "scenario must remain a future live smoke contract", rel(scenario_path))
    if result.get("postprocess_profile", "diagnostics_smoke") != "diagnostics_smoke":
        add_finding(findings, "wrong_postprocess_profile", "formal Dynamics smoke must use diagnostics_smoke postprocess semantics", rel(scenario_path))
    if float(simulation.get("stop_time_s", -1)) != 0.25:
        add_finding(findings, "wrong_stop_time", "scenario must preserve the 0.25 s smoke horizon", rel(scenario_path))

    output_paths = [raw_file, metrics_file, mcp_log]
    return {
        "scenario": rel(scenario_path),
        "experiment_id": experiment_id,
        "model_name": model.get("model_name"),
        "output_paths": output_paths,
        "output_parent_dirs": parent_paths(output_paths),
        "expected_result_variables": expected,
        "extra_variable_alias_count": len(extra_variables),
        "required_variable_profile": "diagnostics_declared",
        "required_metrics_profile": "diagnostics_smoke",
        "missing_extra_variable_mappings": missing_extra,
    }


def build_summary(
    scenario_dir: Path,
    scenario_check_path: Path,
    batch_manifest_path: Path,
    live_preflight_blocker_path: Path,
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    scenario_check = read_json(scenario_check_path)
    batch_manifest = read_json(batch_manifest_path)
    live_preflight = read_json(live_preflight_blocker_path)

    if scenario_check.get("status") != "passed":
        add_finding(findings, "scenario_check_not_passed", "scenario binding check must pass first", rel(scenario_check_path))
    if batch_manifest.get("status") != "passed":
        add_finding(findings, "batch_manifest_not_passed", "batch manifest must pass first", rel(batch_manifest_path))
    if batch_manifest.get("runner_support_status") != "minimal_dynamics_strategy_consumed":
        add_finding(findings, "runner_support_not_minimal", "runner does not consume minimal_dynamics_only", rel(batch_manifest_path))

    future_command_text = " ".join(str(item) for item in batch_manifest.get("future_live_batch_command", []))
    for fragment in ["--no-gui-result-viewer", "--no-gui-open", "Scripts/mworks/run_mworks_batch.py"]:
        if fragment not in future_command_text.replace("\\", "/"):
            add_finding(findings, "future_command_missing_fragment", f"future live command missing {fragment}", rel(batch_manifest_path))

    current_classifier = live_preflight.get("current_upgrade_classifier", {})
    live_gate_state = "blocked_by_current_gui_surface"
    if live_preflight.get("status") != "blocked_by_upgrade_model_surface":
        add_finding(findings, "live_preflight_status_drift", "live preflight no longer records the upgrade-model blocker", rel(live_preflight_blocker_path))
        live_gate_state = "unknown"
    if current_classifier.get("error_kind") != "gui_blocked":
        add_finding(findings, "current_gui_classifier_not_blocking", "current classifier does not report gui_blocked", rel(live_preflight_blocker_path))
        live_gate_state = "unknown"
    if current_classifier.get("license_state_hint") != "upgrade_model_surface_blocked":
        add_finding(findings, "current_gui_hint_not_upgrade_blocked", "current classifier does not report upgrade_model_surface_blocked", rel(live_preflight_blocker_path))
        live_gate_state = "unknown"

    scenario_summaries: list[dict[str, Any]] = []
    scenario_files = [scenario_dir / Path(item).name for item in batch_manifest.get("scenario_files", [])]
    if len(scenario_files) != 7:
        add_finding(findings, "unexpected_scenario_count", "formal Dynamics live smoke must include exactly seven smoke scenarios")
    seen_outputs: set[str] = set()
    for scenario_path in scenario_files:
        if not scenario_path.exists():
            add_finding(findings, "scenario_file_missing", "scenario file listed by manifest is missing", rel(scenario_path))
            continue
        summary = validate_output_contract(scenario_path, findings)
        for output_path in summary["output_paths"]:
            if output_path in seen_outputs:
                add_finding(findings, "duplicate_output_path", "two scenarios write the same output path", summary["scenario"])
            seen_outputs.add(output_path)
        scenario_summaries.append(summary)

    status = "ready_but_blocked_by_gui" if not findings and live_gate_state == "blocked_by_current_gui_surface" else "failed"
    return {
        "schema": "mosim.mworks.formal_dynamics_live_smoke_readiness.v1",
        "status": status,
        "static_only": True,
        "live_mworks_touched": False,
        "mworks_window_action_touched": False,
        "scenario_check": rel(scenario_check_path),
        "batch_manifest": rel(batch_manifest_path),
        "live_preflight_blocker": rel(live_preflight_blocker_path),
        "live_gate_state": live_gate_state,
        "current_gui_classifier": current_classifier,
        "scenario_count": len(scenario_summaries),
        "scenarios": scenario_summaries,
        "future_live_batch_command": batch_manifest.get("future_live_batch_command", []),
        "claim_boundary": [
            "This readiness guard validates executable preparation only.",
            "It does not run MWORKS, check_model, SimulateModel, result extraction, controller performance, mission success, or closed_loop.",
            "Live execution remains blocked while current_gui_classifier reports upgrade_model_surface_blocked.",
        ],
        "findings": findings,
    }


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Formal Dynamics Live Smoke Readiness",
        "",
        f"Status: `{summary['status']}`",
        f"Live gate state: `{summary['live_gate_state']}`",
        "",
        "This is a static readiness guard. It does not call MWORKS, Sysplorer, MCP, `check_model`, or `SimulateModel`.",
        "",
        "## Current GUI Classifier",
        "",
        "```json",
        json.dumps(summary["current_gui_classifier"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Scenarios",
        "",
    ]
    for item in summary["scenarios"]:
        lines.append(f"- `{item['scenario']}` -> `{item['model_name']}`")
    lines.extend(["", "## Claim Boundary", ""])
    for item in summary["claim_boundary"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Findings", ""])
    if summary["findings"]:
        for item in summary["findings"]:
            lines.append(f"- `{item['code']}`: {item['message']}")
    else:
        lines.append("- none")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario-dir", type=Path, default=SCENARIO_DIR)
    parser.add_argument("--scenario-check", type=Path, default=SCENARIO_CHECK)
    parser.add_argument("--batch-manifest", type=Path, default=BATCH_MANIFEST)
    parser.add_argument("--live-preflight-blocker", type=Path, default=LIVE_PREFLIGHT_BLOCKER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    scenario_dir = args.scenario_dir if args.scenario_dir.is_absolute() else ROOT / args.scenario_dir
    scenario_check = args.scenario_check if args.scenario_check.is_absolute() else ROOT / args.scenario_check
    batch_manifest = args.batch_manifest if args.batch_manifest.is_absolute() else ROOT / args.batch_manifest
    live_preflight = args.live_preflight_blocker if args.live_preflight_blocker.is_absolute() else ROOT / args.live_preflight_blocker
    output = args.output if args.output.is_absolute() else ROOT / args.output
    summary = build_summary(scenario_dir, scenario_check, batch_manifest, live_preflight)
    write_json(output, summary)
    write_markdown(output.with_suffix(".md"), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["status"] == "ready_but_blocked_by_gui" else 1


if __name__ == "__main__":
    raise SystemExit(main())
