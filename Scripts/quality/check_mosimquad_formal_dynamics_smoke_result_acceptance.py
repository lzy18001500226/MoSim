#!/usr/bin/env python3
"""Validate formal Dynamics smoke outputs after a future live MWORKS run.

This checker is read-only. Before live results exist, it reports
pending_live_results and exits successfully so it can remain in the long-run
queue without triggering MWORKS.
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
SCENARIO_DIR = ROOT / "Config" / "scenarios" / "diagnostics"
DEFAULT_OUTPUT = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260611_mosimquad_formal_dynamics_smoke_result_acceptance"
    / "result_acceptance.json"
)

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


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def read_csv_header_and_counts(path: Path) -> tuple[list[str], int, int]:
    with path.open(newline="", encoding="utf-8") as handle:
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
    return headers, row_count, non_finite_count


def add_finding(findings: list[dict[str, Any]], code: str, message: str, target: str) -> None:
    findings.append({"code": code, "message": message, "target": target})


def scenario_files(scenario_dir: Path) -> list[Path]:
    return sorted(scenario_dir.glob("mosimquad_dynamics_*_smoke.yaml"))


def validate_scenario(scenario_path: Path, findings: list[dict[str, Any]]) -> dict[str, Any]:
    config = read_yaml(scenario_path)
    experiment_id = str(config.get("experiment_id", scenario_path.stem))
    result = config.get("result", {})
    if not isinstance(result, dict):
        add_finding(findings, "result_not_mapping", "scenario result field must be a mapping", rel(scenario_path))
        result = {}
    raw_path = repo_path(str(result.get("raw_file", "")))
    metrics_path = repo_path(str(result.get("metrics_file", "")))
    expected_aliases = sorted(str(alias) for alias in (result.get("extra_variables", {}) or {}).keys())
    row: dict[str, Any] = {
        "scenario": rel(scenario_path),
        "experiment_id": experiment_id,
        "raw_file": rel(raw_path) if raw_path.is_absolute() and raw_path.is_relative_to(ROOT) else str(raw_path),
        "metrics_file": rel(metrics_path) if metrics_path.is_absolute() and metrics_path.is_relative_to(ROOT) else str(metrics_path),
        "result_state": "missing",
        "expected_aliases": expected_aliases,
    }

    if not raw_path.exists() and not metrics_path.exists():
        return row
    if not raw_path.exists():
        add_finding(findings, "raw_missing", "raw CSV missing while metrics exist", rel(scenario_path))
        return row
    if not metrics_path.exists():
        add_finding(findings, "metrics_missing", "metrics JSON missing while raw CSV exists", rel(scenario_path))
        return row

    headers, row_count, non_finite_count = read_csv_header_and_counts(raw_path)
    metrics = read_json(metrics_path)
    missing_aliases = sorted(set(expected_aliases + ["time"]) - set(headers))
    row.update(
        {
            "result_state": "present",
            "csv_headers": headers,
            "row_count": row_count,
            "non_finite_count": non_finite_count,
            "missing_aliases": missing_aliases,
            "metrics_profile": metrics.get("metrics_profile"),
            "claim_role": metrics.get("claim_role"),
            "metrics_valid": metrics.get("valid"),
        }
    )

    if missing_aliases:
        add_finding(findings, "missing_csv_aliases", f"CSV missing aliases: {', '.join(missing_aliases)}", rel(scenario_path))
    if row_count <= 10:
        add_finding(findings, "row_count_too_small", f"row_count={row_count}", rel(scenario_path))
    if non_finite_count:
        add_finding(findings, "non_finite_values", f"non_finite_count={non_finite_count}", rel(scenario_path))
    if metrics.get("metrics_profile") != "diagnostics_smoke":
        add_finding(findings, "wrong_metrics_profile", "metrics_profile must be diagnostics_smoke", rel(scenario_path))
    if metrics.get("claim_role") != "dynamics_smoke_only":
        add_finding(findings, "wrong_claim_role", "claim_role must be dynamics_smoke_only", rel(scenario_path))
    if metrics.get("valid") is not True:
        add_finding(findings, "metrics_not_valid", "metrics valid must be true", rel(scenario_path))
    forbidden = {"position_rmse_m", "total_health_score"}
    leaked = sorted(forbidden.intersection(metrics))
    if leaked:
        add_finding(findings, "tracking_or_quality_claim_leak", f"diagnostics metrics include forbidden keys: {', '.join(leaked)}", rel(scenario_path))
    if metrics.get("quality_status") not in {None, "smoke_only"}:
        add_finding(findings, "wrong_quality_status", "diagnostics smoke quality_status must be smoke_only when present", rel(scenario_path))
    if metrics.get("quality_pass") not in {None, True}:
        add_finding(findings, "wrong_quality_pass", "diagnostics smoke quality_pass must be true when present", rel(scenario_path))
    return row


def build_summary(scenario_dir: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    rows = [validate_scenario(path, findings) for path in scenario_files(scenario_dir)]
    present_count = sum(1 for row in rows if row["result_state"] == "present")
    missing_count = sum(1 for row in rows if row["result_state"] == "missing")
    status = "pending_live_results" if present_count == 0 and not findings else "passed"
    if findings:
        status = "failed"
    elif present_count and missing_count:
        status = "partial_results_pending"
    return {
        "schema": "mosim.mworks.formal_dynamics_smoke_result_acceptance.v1",
        "status": status,
        "static_read_only": True,
        "live_mworks_touched": False,
        "scenario_count": len(rows),
        "present_result_count": present_count,
        "missing_result_count": missing_count,
        "scenarios": rows,
        "claim_boundary": [
            "diagnostics smoke result acceptance only",
            "does not run MWORKS, check_model, SimulateModel, or GUI actions",
            "does not prove controller performance, mission success, or closed_loop",
        ],
        "findings": findings,
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Formal Dynamics Smoke Result Acceptance",
        "",
        f"Status: `{summary['status']}`",
        f"Present results: `{summary['present_result_count']}` / `{summary['scenario_count']}`",
        "",
        "This checker is read-only and does not run MWORKS.",
        "",
        "## Scenarios",
        "",
    ]
    for row in summary["scenarios"]:
        lines.append(f"- `{row['scenario']}`: `{row['result_state']}`")
    lines.extend(["", "## Findings", ""])
    if summary["findings"]:
        lines.extend(f"- `{item['code']}` at `{item['target']}`: {item['message']}" for item in summary["findings"])
    else:
        lines.append("- none")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario-dir", type=Path, default=SCENARIO_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    scenario_dir = args.scenario_dir if args.scenario_dir.is_absolute() else ROOT / args.scenario_dir
    output = args.output if args.output.is_absolute() else ROOT / args.output
    summary = build_summary(scenario_dir)
    write_json(output, summary)
    write_markdown(output.with_suffix(".md"), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if summary["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
