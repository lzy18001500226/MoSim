#!/usr/bin/env python3
"""Validate candidate submission evidence manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_GLOBAL_EXCLUSION_TERMS = [
    "Not final PMO acceptance",
    "native Syslab",
    "live MWORKS no-start attach",
    "ROS2 planner_ready",
    "closed_loop",
    "UE build/runtime/editor",
    "metrics-only rows",
    "needs_iteration rows",
]


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def validate(manifest_path: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    issues: list[str] = []
    warnings: list[str] = []

    if manifest.get("status") != "review_candidate_not_final_acceptance":
        issues.append("status must be review_candidate_not_final_acceptance")

    source_map_value = str(manifest.get("source_evidence_map", ""))
    if not source_map_value:
        issues.append("source_evidence_map is required")
        source_map = {}
    else:
        source_map_path = repo_path(source_map_value)
        if not source_map_path.exists():
            issues.append(f"source_evidence_map does not exist: {source_map_value}")
            source_map = {}
        else:
            source_map = read_json(source_map_path)

    candidate_source_rows = {
        str(row.get("experiment_id", "")): row
        for row in as_list(source_map.get("candidate_submission_evidence_rows"))
        if isinstance(row, dict)
    }
    exclusion_source_ids = {
        str(row.get("experiment_id", ""))
        for row in as_list(source_map.get("needs_iteration_exclusions"))
        if isinstance(row, dict)
    }

    rows = as_list(manifest.get("candidate_rows"))
    if manifest.get("row_count") != len(rows):
        issues.append("row_count must match candidate_rows length")
    if not rows:
        issues.append("candidate_rows must not be empty")

    seen_slots: set[str] = set()
    seen_ids: set[str] = set()
    for index, row_any in enumerate(rows):
        row = as_dict(row_any)
        slot = str(row.get("claim_slot", ""))
        experiment_id = str(row.get("experiment_id", ""))
        if not slot:
            issues.append(f"candidate row {index} missing claim_slot")
        if slot in seen_slots:
            issues.append(f"duplicate claim_slot: {slot}")
        seen_slots.add(slot)
        if not experiment_id:
            issues.append(f"candidate row {slot or index} missing experiment_id")
            continue
        if experiment_id in seen_ids:
            issues.append(f"duplicate experiment_id: {experiment_id}")
        seen_ids.add(experiment_id)
        if experiment_id not in candidate_source_rows:
            issues.append(f"candidate row not found in source candidate rows: {experiment_id}")
        if experiment_id in exclusion_source_ids:
            issues.append(f"needs_iteration source row selected as positive candidate: {experiment_id}")
        if row.get("quality_status") != "pass":
            issues.append(f"candidate row must have quality_status=pass: {experiment_id}")
        if not str(row.get("priority", "")):
            issues.append(f"candidate row must have non-empty priority: {experiment_id}")
        if str(row.get("claim_ceiling", "")) != "candidate_report_evidence_only_not_final_pmo_acceptance":
            issues.append(f"candidate row has wrong claim_ceiling: {experiment_id}")
        metrics_file = str(row.get("metrics_file", ""))
        raw_file = str(row.get("raw_file", ""))
        if not metrics_file:
            issues.append(f"candidate row missing metrics_file: {experiment_id}")
        elif not repo_path(metrics_file).exists():
            issues.append(f"candidate metrics_file does not exist: {experiment_id}: {metrics_file}")
        if not raw_file:
            issues.append(f"candidate row missing raw_file: {experiment_id}")
        elif not repo_path(raw_file).exists():
            issues.append(f"candidate raw_file does not exist: {experiment_id}: {raw_file}")

    exclusions_text = "\n".join(str(item) for item in as_list(manifest.get("global_exclusions")))
    for term in REQUIRED_GLOBAL_EXCLUSION_TERMS:
        if term not in exclusions_text:
            issues.append(f"global_exclusions missing term: {term}")

    if len(rows) < 8:
        warnings.append("candidate manifest has fewer than 8 rows; verify report coverage is intentional")

    return {
        "ok": not issues,
        "manifest": rel(manifest_path),
        "source_evidence_map": source_map_value,
        "row_count": len(rows),
        "issues": issues,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "manifest",
        nargs="?",
        default="Results/static_audits/submission_evidence_manifest_20260610/candidate_submission_evidence_manifest.json",
    )
    parser.add_argument("--output-json", help="Optional validation report path")
    args = parser.parse_args()

    manifest_path = repo_path(args.manifest)
    try:
        report = validate(manifest_path)
    except Exception as exc:
        report = {
            "ok": False,
            "manifest": rel(manifest_path),
            "source_evidence_map": "",
            "row_count": 0,
            "issues": [str(exc)],
            "warnings": [],
        }

    if args.output_json:
        output = repo_path(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
