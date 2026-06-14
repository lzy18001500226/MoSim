#!/usr/bin/env python3
"""Validate the single-UAV control batch results before multi-UAV work.

This checker is read-only. It consumes scenario YAML, raw CSV, metrics JSON,
and declared MCP logs. It does not call MWORKS, Sysplorer, MCP, check_model,
SimulateModel, ROS2, UE, or GUI/window tools.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260611_single_uav_control_batch_result_acceptance"
    / "single_uav_control_batch_result_acceptance.json"
)

REQUIRED_RAW_COLUMNS = ["time", "x", "y", "z", "x_ref", "y_ref", "z_ref"]
REQUIRED_METRIC_KEYS = [
    "source",
    "evidence_level",
    "valid",
    "quality_status",
    "quality_pass",
    "position_rmse_m",
    "max_position_error_m",
    "total_health_score",
    "nan_count",
]
ALLOWED_QUALITY_STATUSES = {"pass", "needs_iteration", "smoke_only"}
EXPECTED_SOURCE = "MWORKS_MCP"

sys.path.insert(0, str(ROOT / "Scripts" / "quality"))
sys.path.insert(0, str(ROOT / "Scripts" / "mworks"))
from build_single_uav_control_batch_contract import SCENARIO_PATHS  # noqa: E402
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


def add_finding(findings: list[dict[str, Any]], code: str, message: str, target: str) -> None:
    findings.append({"code": code, "message": message, "target": target})


def csv_profile(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        row_count = 0
        non_finite_count = 0
        for row in reader:
            row_count += 1
            for value in row.values():
                if value == "":
                    non_finite_count += 1
                    continue
                try:
                    if not math.isfinite(float(value)):
                        non_finite_count += 1
                except ValueError:
                    non_finite_count += 1
    return {"headers": headers, "row_count": row_count, "non_finite_count": non_finite_count}


def baseline_experiment(config: dict[str, Any], controller_id: str, scene_id: str) -> str:
    controller = config.get("controller", {})
    if isinstance(controller, dict) and controller.get("baseline_experiment"):
        return str(controller["baseline_experiment"])
    if controller_id and controller_id != "pid_baseline" and scene_id:
        return f"{scene_id}_pid_baseline"
    return ""


def validate_scenario(path_text: str, findings: list[dict[str, Any]]) -> dict[str, Any]:
    scenario_path = repo_path(path_text)
    row: dict[str, Any] = {
        "scenario": rel(scenario_path),
        "state": "missing_scenario",
        "raw_state": "missing",
        "metrics_state": "missing",
        "mcp_log_state": "missing",
    }
    if not scenario_path.exists():
        add_finding(findings, "missing_scenario", "scenario YAML is missing", rel(scenario_path))
        return row

    config = read_yaml(scenario_path)
    result = config.get("result", {})
    if not isinstance(result, dict):
        add_finding(findings, "result_not_mapping", "scenario result field must be a mapping", rel(scenario_path))
        result = {}

    experiment_id = str(config.get("experiment_id", scenario_path.stem))
    scene_id = str(config.get("scene_id", ""))
    controller_id = str(config.get("controller_id", ""))
    raw_path = repo_path(result.get("raw_file", ""))
    metrics_path = repo_path(result.get("metrics_file", ""))
    mcp_log_path = repo_path(result.get("mcp_log", ""))
    baseline_id = baseline_experiment(config, controller_id, scene_id)

    row.update(
        {
            "state": "present",
            "experiment_id": experiment_id,
            "scene_id": scene_id,
            "controller_id": controller_id,
            "baseline_experiment": baseline_id,
            "raw_file": rel(raw_path),
            "metrics_file": rel(metrics_path),
            "mcp_log": rel(mcp_log_path),
            "raw_state": "present" if raw_path.exists() else "missing",
            "metrics_state": "present" if metrics_path.exists() else "missing",
            "mcp_log_state": "present" if mcp_log_path.exists() else "missing",
            "acceptance_state": "pending_live_result",
        }
    )

    missing_required_artifact = False
    if not raw_path.exists():
        add_finding(findings, "raw_missing", "raw CSV is missing", rel(scenario_path))
        missing_required_artifact = True
    if not metrics_path.exists():
        add_finding(findings, "metrics_missing", "metrics JSON is missing", rel(scenario_path))
        missing_required_artifact = True
    if not mcp_log_path.exists():
        add_finding(findings, "mcp_log_missing", "declared MCP log is missing", rel(scenario_path))
        missing_required_artifact = True
    if missing_required_artifact:
        return row

    profile = csv_profile(raw_path)
    metrics = read_json(metrics_path)
    missing_columns = sorted(set(REQUIRED_RAW_COLUMNS) - set(profile["headers"]))
    missing_metrics = sorted(set(REQUIRED_METRIC_KEYS) - set(metrics))
    row.update(
        {
            "acceptance_state": "accepted" if metrics.get("quality_status") == "pass" else "needs_iteration",
            "csv_headers": profile["headers"],
            "row_count": profile["row_count"],
            "non_finite_count": profile["non_finite_count"],
            "missing_columns": missing_columns,
            "missing_metric_keys": missing_metrics,
            "source": metrics.get("source"),
            "evidence_level": metrics.get("evidence_level"),
            "metrics_valid": metrics.get("valid"),
            "quality_status": metrics.get("quality_status"),
            "quality_pass": metrics.get("quality_pass"),
            "position_rmse_m": metrics.get("position_rmse_m"),
            "max_position_error_m": metrics.get("max_position_error_m"),
            "total_health_score": metrics.get("total_health_score"),
            "quality_baseline_experiment": metrics.get("quality_baseline_experiment"),
            "quality_rmse_improvement_pct": metrics.get("quality_rmse_improvement_pct"),
        }
    )

    if missing_columns:
        add_finding(findings, "missing_raw_columns", f"raw CSV missing columns: {', '.join(missing_columns)}", rel(scenario_path))
    if profile["row_count"] <= 10:
        add_finding(findings, "row_count_too_small", f"row_count={profile['row_count']}", rel(scenario_path))
    if profile["non_finite_count"]:
        add_finding(findings, "non_finite_raw_values", f"non_finite_count={profile['non_finite_count']}", rel(scenario_path))
    if missing_metrics:
        add_finding(findings, "missing_metric_keys", f"metrics missing keys: {', '.join(missing_metrics)}", rel(scenario_path))
    if metrics.get("source") != EXPECTED_SOURCE:
        add_finding(findings, "wrong_source", "metrics source must be MWORKS_MCP", rel(scenario_path))
    if metrics.get("valid") is not True:
        add_finding(findings, "metrics_not_valid", "metrics valid must be true", rel(scenario_path))
    if metrics.get("quality_status") not in ALLOWED_QUALITY_STATUSES:
        add_finding(findings, "unknown_quality_status", "quality_status is not accepted by the batch gate", rel(scenario_path))
    if metrics.get("quality_pass") is True and metrics.get("quality_status") != "pass":
        add_finding(findings, "quality_pass_status_mismatch", "quality_pass true requires quality_status=pass", rel(scenario_path))
    if controller_id != "pid_baseline" and baseline_id:
        metric_baseline = metrics.get("quality_baseline_experiment")
        if metric_baseline != baseline_id:
            add_finding(findings, "baseline_mismatch", f"metrics baseline {metric_baseline!r} does not match scenario baseline {baseline_id!r}", rel(scenario_path))
        if "quality_rmse_improvement_pct" not in metrics:
            add_finding(findings, "missing_rmse_improvement", "non-baseline scenario must record RMSE improvement", rel(scenario_path))

    return row


def build_summary(paths: list[str]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    rows = [validate_scenario(path, findings) for path in paths]
    present_count = sum(1 for row in rows if row.get("raw_state") == "present" and row.get("metrics_state") == "present")
    accepted_count = sum(1 for row in rows if row.get("acceptance_state") == "accepted")
    iteration_count = sum(1 for row in rows if row.get("acceptance_state") == "needs_iteration")
    pending_count = sum(1 for row in rows if row.get("acceptance_state") == "pending_live_result")

    if findings:
        status = "failed"
    elif pending_count == len(rows):
        status = "pending_live_results"
    elif iteration_count:
        status = "needs_iteration"
    else:
        status = "passed"

    return {
        "schema": "mosim.mworks.single_uav_control_batch_result_acceptance.v1",
        "status": status,
        "static_read_only": True,
        "live_mworks_touched": False,
        "scope": "single_uav_control_before_multi_uav",
        "scenario_count": len(rows),
        "present_result_count": present_count,
        "accepted_result_count": accepted_count,
        "needs_iteration_count": iteration_count,
        "pending_result_count": pending_count,
        "scenarios": rows,
        "iteration_targets": [
            {
                "scenario": row["scenario"],
                "quality_status": row.get("quality_status"),
                "quality_pass": row.get("quality_pass"),
                "position_rmse_m": row.get("position_rmse_m"),
                "total_health_score": row.get("total_health_score"),
            }
            for row in rows
            if row.get("acceptance_state") == "needs_iteration"
        ],
        "claim_boundary": [
            "Read-only acceptance of declared single-UAV raw/metrics/log artifacts.",
            "Existing artifacts may be historical evidence; this checker does not prove this turn ran live MWORKS.",
            "Status needs_iteration is preserved as engineering progress, not hidden as failure.",
            "This does not prove multi-UAV readiness and stops before formation work.",
        ],
        "findings": findings,
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Single-UAV Control Batch Result Acceptance",
        "",
        f"Status: `{summary['status']}`",
        f"Present results: `{summary['present_result_count']}` / `{summary['scenario_count']}`",
        f"Accepted results: `{summary['accepted_result_count']}`",
        f"Needs iteration: `{summary['needs_iteration_count']}`",
        "",
        "This checker is read-only. It does not run MWORKS, Sysplorer, MCP, `check_model`, `SimulateModel`, ROS2, UE, or GUI/window tools.",
        "",
        "## Scenarios",
        "",
    ]
    for row in summary["scenarios"]:
        lines.append(
            f"- `{row['scenario']}`: `{row.get('acceptance_state')}`"
            f" / quality=`{row.get('quality_status', '')}`"
        )
    lines.extend(["", "## Iteration Targets", ""])
    if summary["iteration_targets"]:
        for item in summary["iteration_targets"]:
            lines.append(
                f"- `{item['scenario']}`: quality=`{item['quality_status']}`, "
                f"rmse=`{item['position_rmse_m']}`, health=`{item['total_health_score']}`"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Claim Boundary", ""])
    lines.extend(f"- {item}" for item in summary["claim_boundary"])
    lines.extend(["", "## Findings", ""])
    if summary["findings"]:
        lines.extend(f"- `{item['code']}` at `{item['target']}`: {item['message']}" for item in summary["findings"])
    else:
        lines.append("- none")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("scenario", nargs="*", help="Optional scenario YAML list. Defaults to the curated single-UAV batch.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output = args.output if args.output.is_absolute() else ROOT / args.output
    summary = build_summary(args.scenario or SCENARIO_PATHS)
    write_json(output, summary)
    write_markdown(output.with_suffix(".md"), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if summary["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
