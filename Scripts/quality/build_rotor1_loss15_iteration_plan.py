#!/usr/bin/env python3
"""Build the minimal iteration plan for rotor-1 15% efficiency-loss cases.

This is a read-only planning artifact. It does not modify controller
parameters and does not call MWORKS, Sysplorer, MCP, check_model,
SimulateModel, ROS2, UE, or GUI/window tools.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "Results" / "mworks_model_hygiene" / "20260611_rotor1_loss15_iteration_plan"
BLOCKER_SENTINEL = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260611_mosimquad_formal_dynamics_live_preflight"
    / "current_gui_sentinel_after_upgrade_classifier_20260611_234725.json"
)
SCENARIOS = [
    "Config/scenarios/robustness/example1_rotor1_loss15_pid_baseline.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml",
]
TARGETS = {
    "min_total_health_score": 40.0,
    "max_position_rmse_m": 0.45,
    "max_position_error_m": 1.60,
    "min_awff_rmse_improvement_pct": 0.5,
}

sys.path.insert(0, str(ROOT / "Scripts" / "mworks"))
from run_mworks_scenario import read_yaml  # noqa: E402


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def repo_path(value: Any) -> Path:
    path = Path(str(value))
    return path if path.is_absolute() else ROOT / path


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def live_gate_state(sentinel_path: Path) -> dict[str, Any]:
    if not sentinel_path.exists():
        return {
            "state": "unknown_no_current_sentinel",
            "sentinel": rel(sentinel_path),
            "live_run_allowed_now": False,
            "reason": "current MWORKS GUI sentinel is missing",
        }
    sentinel = read_json(sentinel_path)
    blocked = (
        sentinel.get("status") == "incident_detected"
        or sentinel.get("error_kind") == "gui_blocked"
        or sentinel.get("license_state_hint") == "upgrade_model_surface_blocked"
        or int(sentinel.get("blocking_mworks_window_count", 0) or 0) > 0
    )
    return {
        "state": "blocked_by_current_sentinel" if blocked else "clean_by_current_sentinel",
        "sentinel": rel(sentinel_path),
        "live_run_allowed_now": not blocked,
        "status": sentinel.get("status"),
        "error_kind": sentinel.get("error_kind"),
        "license_state_hint": sentinel.get("license_state_hint"),
        "blocking_mworks_window_count": sentinel.get("blocking_mworks_window_count"),
        "upgrade_model_window_count": sentinel.get("upgrade_model_window_count"),
    }


def scenario_row(path_text: str) -> dict[str, Any]:
    scenario_path = repo_path(path_text)
    config = read_yaml(scenario_path)
    result = config.get("result", {})
    if not isinstance(result, dict):
        result = {}
    metrics_path = repo_path(result.get("metrics_file", ""))
    metrics = read_json(metrics_path) if metrics_path.exists() else {}
    disturbance = config.get("disturbance", {})
    if not isinstance(disturbance, dict):
        disturbance = {}
    return {
        "scenario": rel(scenario_path),
        "experiment_id": config.get("experiment_id"),
        "scene_id": config.get("scene_id"),
        "controller_id": config.get("controller_id"),
        "model_name": (config.get("model", {}) or {}).get("model_name") if isinstance(config.get("model", {}), dict) else "",
        "disturbance": {
            "type": disturbance.get("type"),
            "affected_rotor": disturbance.get("affected_rotor"),
            "efficiency_ratio": disturbance.get("efficiency_ratio"),
            "target_component": disturbance.get("target_component"),
        },
        "metrics_file": rel(metrics_path),
        "current_quality_status": metrics.get("quality_status"),
        "current_quality_pass": metrics.get("quality_pass"),
        "position_rmse_m": metrics.get("position_rmse_m"),
        "max_position_error_m": metrics.get("max_position_error_m"),
        "total_health_score": metrics.get("total_health_score"),
        "disturbance_recovery_time_s": metrics.get("disturbance_recovery_time_s"),
        "steady_state_error_m": metrics.get("steady_state_error_m"),
        "quality_issues": metrics.get("quality_issues", []),
        "quality_recommendations": metrics.get("quality_recommendations", []),
    }


def build_plan(sentinel_path: Path) -> dict[str, Any]:
    rows = [scenario_row(path) for path in SCENARIOS]
    gate = live_gate_state(sentinel_path)
    command = [
        sys.executable,
        "Scripts/mworks/run_mworks_batch.py",
        "--no-gui-result-viewer",
        "--no-gui-open",
        "--continue-on-failure",
        "--allow-needs-iteration",
    ] + SCENARIOS
    dry_run_command = [
        sys.executable,
        "Scripts/mworks/run_mworks_batch.py",
        "--dry-run",
        "--no-gui-result-viewer",
        "--no-gui-open",
        "--continue-on-failure",
        "--allow-needs-iteration",
    ] + SCENARIOS
    status = "ready_for_bounded_live_rerun" if gate["live_run_allowed_now"] else "blocked_by_mworks_gui"
    return {
        "schema": "mosim.mworks.rotor1_loss15_iteration_plan.v1",
        "status": status,
        "static_read_only": True,
        "live_mworks_touched": False,
        "scope": "single_uav_rotor1_loss15_iteration_before_multi_uav",
        "live_gate": gate,
        "scenario_count": len(rows),
        "scenarios": rows,
        "acceptance_targets": TARGETS,
        "future_live_rerun_command": command,
        "dry_run_command": dry_run_command,
        "post_rerun_checks": [
            [sys.executable, "Scripts/results/evaluate_result_quality.py", scenario, "--write-metrics"]
            for scenario in SCENARIOS
        ]
        + [
            [
                sys.executable,
                "Scripts/quality/check_single_uav_control_batch_result_acceptance.py",
            ]
        ],
        "iteration_strategy": [
            "First rerun only the two rotor1_loss15 scenarios after fresh clean MWORKS preflight.",
            "Do not tune controller parameters until the two-scenario rerun refreshes raw/metrics evidence.",
            "If both remain needs_iteration, inspect AWFF fault-allocation/control-allocation parameters against the rotor-1 0.85 effectiveness case.",
            "Keep PID baseline as comparative failure/robustness evidence; do not require PID baseline to pass before optimizing AWFF.",
        ],
        "forbidden_actions": [
            "do not run live MWORKS while the upgrade-model GUI blocker is present",
            "do not click upgrade/login/license/save/restart/close controls from this engineering task",
            "do not enter multi-UAV formation work from this plan",
            "do not claim controller improvement until fresh rerun metrics pass the declared quality gate",
        ],
        "claim_boundary": [
            "This is an iteration/rerun plan, not a completed simulation.",
            "Existing metrics are historical evidence and remain the baseline for the next rerun.",
            "The plan does not modify model/controller files.",
        ],
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_markdown(path: Path, plan: dict[str, Any]) -> None:
    lines = [
        "# Rotor1 Loss15 Iteration Plan",
        "",
        f"Status: `{plan['status']}`",
        f"Live gate: `{plan['live_gate']['state']}`",
        "",
        "Read-only plan. It does not run MWORKS or modify controller/model files.",
        "",
        "## Current Targets",
        "",
    ]
    for row in plan["scenarios"]:
        lines.append(
            f"- `{row['scenario']}`: quality=`{row['current_quality_status']}`, "
            f"rmse=`{row['position_rmse_m']}`, health=`{row['total_health_score']}`"
        )
    lines.extend(["", "## Future Live Rerun Command", "", "```powershell"])
    lines.append(" ".join(str(item) for item in plan["future_live_rerun_command"]))
    lines.extend(["```", "", "## Iteration Strategy", ""])
    lines.extend(f"- {item}" for item in plan["iteration_strategy"])
    lines.extend(["", "## Forbidden Actions", ""])
    lines.extend(f"- {item}" for item in plan["forbidden_actions"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sentinel", type=Path, default=BLOCKER_SENTINEL)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    sentinel = args.sentinel if args.sentinel.is_absolute() else ROOT / args.sentinel
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    plan = build_plan(sentinel)
    write_json(output_dir / "rotor1_loss15_iteration_plan.json", plan)
    write_markdown(output_dir / "rotor1_loss15_iteration_plan.md", plan)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
