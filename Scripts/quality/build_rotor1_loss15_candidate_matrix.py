#!/usr/bin/env python3
"""Build the rotor-1 15% efficiency-loss controller candidate matrix.

This read-only checker consolidates existing pure rotor1_loss15 scenario
configs and metrics before multi-UAV work. It does not run MWORKS, Sysplorer,
MCP, check_model, SimulateModel, ROS2, UE, or GUI/window tools.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "Results" / "mworks_model_hygiene" / "20260611_rotor1_loss15_candidate_matrix"
SCENARIOS = [
    "Config/scenarios/robustness/example1_rotor1_loss15_pid_baseline.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_awff_pid.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_improved_pid.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_enhanced_pid.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_l1_residual_sysblock.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_l1_fault_allocation_sysblock.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_l1_online_fault_allocation_sysblock.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_l1_multi_fault_isolation_sysblock.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_linear_mpc_sysblock.yaml",
    "Config/scenarios/robustness/example1_rotor1_loss15_linear_mpc_online_fault_allocation_sysblock.yaml",
]
MIN_HEALTH_SCORE = 40.0

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


def row_for_scenario(path_text: str) -> dict[str, Any]:
    scenario_path = repo_path(path_text)
    config = read_yaml(scenario_path)
    result = config.get("result", {})
    if not isinstance(result, dict):
        result = {}
    controller = config.get("controller", {})
    if not isinstance(controller, dict):
        controller = {}
    disturbance = config.get("disturbance", {})
    if not isinstance(disturbance, dict):
        disturbance = {}

    metrics_path = repo_path(result.get("metrics_file", ""))
    metrics = read_json(metrics_path) if metrics_path.exists() else {}
    quality_status = metrics.get("quality_status")
    quality_pass = metrics.get("quality_pass")
    health = metrics.get("total_health_score")
    return {
        "scenario": rel(scenario_path),
        "scenario_present": scenario_path.exists(),
        "experiment_id": config.get("experiment_id"),
        "controller_id": config.get("controller_id"),
        "priority": config.get("priority"),
        "model_name": (config.get("model", {}) or {}).get("model_name") if isinstance(config.get("model", {}), dict) else "",
        "params_file": controller.get("params_file"),
        "sysblock_controller_file": controller.get("sysblock_controller_file"),
        "known_to_controller": disturbance.get("known_to_controller"),
        "efficiency_ratio": disturbance.get("efficiency_ratio"),
        "metrics_file": rel(metrics_path),
        "metrics_present": metrics_path.exists(),
        "quality_status": quality_status,
        "quality_pass": quality_pass,
        "position_rmse_m": metrics.get("position_rmse_m"),
        "max_position_error_m": metrics.get("max_position_error_m"),
        "steady_state_error_m": metrics.get("steady_state_error_m"),
        "disturbance_recovery_time_s": metrics.get("disturbance_recovery_time_s"),
        "total_health_score": health,
        "quality_baseline_experiment": metrics.get("quality_baseline_experiment"),
        "quality_rmse_improvement_pct": metrics.get("quality_rmse_improvement_pct"),
        "eta_hat_final": metrics.get("eta_hat_final"),
        "fault_index_accuracy_pct": metrics.get("fault_index_accuracy_pct"),
        "candidate_state": "accepted_candidate"
        if quality_status == "pass" and quality_pass is True and isinstance(health, (int, float)) and health >= MIN_HEALTH_SCORE
        else "needs_iteration_or_unverified",
    }


def build_matrix(paths: list[str]) -> dict[str, Any]:
    rows = [row_for_scenario(path) for path in paths]
    findings: list[dict[str, Any]] = []
    for row in rows:
        if not row["scenario_present"]:
            findings.append({"code": "missing_scenario", "target": row["scenario"]})
        if not row["metrics_present"]:
            findings.append({"code": "missing_metrics", "target": row["scenario"]})

    accepted = [row for row in rows if row["candidate_state"] == "accepted_candidate"]
    needs = [row for row in rows if row["candidate_state"] != "accepted_candidate"]
    best = min(
        accepted,
        key=lambda row: float(row["position_rmse_m"]),
        default=None,
    )
    status = "failed" if findings else "ready_with_accepted_candidates" if accepted else "needs_iteration"
    if accepted:
        recommended_next_steps = [
            "Use accepted rotor1_loss15 allocation/isolation candidates as the single-UAV robustness direction before multi-UAV.",
            "Do not promote the plain PID/AWFF rotor1_loss15 rows as passing evidence.",
            "After MWORKS clean preflight, rerun the minimal two-scenario PID/AWFF gate if the report needs refreshed baseline comparison.",
            "If selecting a final rotor-loss controller, rerun the chosen accepted candidate under current MWORKS before final report wording.",
        ]
    else:
        recommended_next_steps = [
            "Continue single-UAV rotor1_loss15 controller/model iteration; no current accepted candidate is available.",
            "Do not promote any rotor1_loss15 row as passing robustness evidence.",
            "Do not enter UE replay/rendering or multi-UAV formation transition from this matrix.",
            "After an engineering change, rerun the relevant rotor1_loss15 scenario(s), refresh metrics, rebuild this matrix, and then rebuild the closeout gate.",
        ]
    return {
        "schema": "mosim.mworks.rotor1_loss15_candidate_matrix.v1",
        "status": status,
        "static_read_only": True,
        "live_mworks_touched": False,
        "scope": "single_uav_rotor1_loss15_candidate_selection_before_multi_uav",
        "acceptance_gate": {
            "min_total_health_score": MIN_HEALTH_SCORE,
            "requires_quality_status_pass": True,
            "requires_quality_pass_true": True,
        },
        "scenario_count": len(rows),
        "accepted_candidate_count": len(accepted),
        "needs_iteration_or_unverified_count": len(needs),
        "best_rmse_candidate": best,
        "rows": rows,
        "recommended_next_steps": recommended_next_steps,
        "claim_boundary": [
            "This matrix reads historical metrics only; it does not prove this turn ran live MWORKS.",
            "It does not enter multi-UAV formation work.",
            "It does not prove final controller acceptance without PMO/report review and any required fresh rerun.",
        ],
        "findings": findings,
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_markdown(path: Path, matrix: dict[str, Any]) -> None:
    lines = [
        "# Rotor1 Loss15 Candidate Matrix",
        "",
        f"Status: `{matrix['status']}`",
        f"Accepted candidates: `{matrix['accepted_candidate_count']}`",
        f"Needs iteration or unverified: `{matrix['needs_iteration_or_unverified_count']}`",
        "",
        "Read-only historical matrix. It does not run MWORKS.",
        "",
        "## Rows",
        "",
        "| Controller | Quality | Health | RMSE | Known fault | State |",
        "|---|---:|---:|---:|---|---|",
    ]
    for row in matrix["rows"]:
        lines.append(
            "| {controller} | {quality} | {health} | {rmse} | {known} | {state} |".format(
                controller=row["controller_id"],
                quality=row["quality_status"],
                health="" if row["total_health_score"] is None else f"{float(row['total_health_score']):.6f}",
                rmse="" if row["position_rmse_m"] is None else f"{float(row['position_rmse_m']):.6f}",
                known=row["known_to_controller"],
                state=row["candidate_state"],
            )
        )
    best = matrix.get("best_rmse_candidate")
    lines.extend(["", "## Best RMSE Candidate", ""])
    if best:
        lines.append(
            f"- `{best['controller_id']}` via `{best['scenario']}`: "
            f"rmse=`{float(best['position_rmse_m']):.6f}`, health=`{float(best['total_health_score']):.6f}`"
        )
    else:
        lines.append("- No accepted candidate found.")
    lines.extend(["", "## Recommended Next Steps", ""])
    lines.extend(f"- {item}" for item in matrix["recommended_next_steps"])
    lines.extend(["", "## Claim Boundary", ""])
    lines.extend(f"- {item}" for item in matrix["claim_boundary"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenarios", nargs="*", default=SCENARIOS)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    matrix = build_matrix(args.scenarios)
    write_json(output_dir / "rotor1_loss15_candidate_matrix.json", matrix)
    write_markdown(output_dir / "rotor1_loss15_candidate_matrix.md", matrix)
    print(json.dumps(matrix, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
