#!/usr/bin/env python3
"""Validate evidence-map claim boundaries.

This checker prevents static result summaries from being overclaimed as final
acceptance. It is intentionally narrow: it validates the generated evidence map
and, optionally, a design/evidence document that references the map.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_NOT_SUPPORTED_TERMS = [
    "priority-empty metrics-only",
    "needs_iteration",
    "native Syslab",
    "live MWORKS no-start attach",
    "ROS2 planner readiness",
    "UE build/runtime success",
    "final closed-loop product acceptance",
]

REQUIRED_DESIGN_TERMS = [
    "evidence_map.json",
    "64 formal pass rows",
    "17 formal needs_iteration rows",
    "95 priority-empty metrics-only rows",
    "source_static_only",
    "build_only_gate_ready",
    "blocked_absent",
]

NEGATED_OVERCLAIM_MARKERS = [
    "do not",
    "must not",
    "not ",
    "不要",
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


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def text_contains_all(text: str, terms: list[str]) -> list[str]:
    return [term for term in terms if term not in text]


def validate_evidence_map(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []

    if data.get("status") != "static_audit_only":
        issues.append("status must be static_audit_only")

    row_counts = as_dict(data.get("row_counts"))
    total_rows = int(row_counts.get("total_rows", -1))
    metrics_only = int(row_counts.get("metrics_only_rows_priority_empty", -1))
    formal = int(row_counts.get("formal_rows_priority_nonempty", -1))
    formal_pass = int(row_counts.get("formal_pass_rows", -1))
    formal_needs = int(row_counts.get("formal_needs_iteration_rows", -1))

    if total_rows != metrics_only + formal:
        issues.append("row_counts total_rows must equal metrics_only + formal rows")
    if formal != formal_pass + formal_needs:
        issues.append("formal_rows_priority_nonempty must equal formal_pass_rows + formal_needs_iteration_rows")
    if metrics_only <= 0:
        warnings.append("metrics_only_rows_priority_empty is zero; verify no metrics-only rows were dropped")
    if formal_pass <= 0:
        issues.append("formal_pass_rows must be positive")
    if formal_needs <= 0:
        warnings.append("formal_needs_iteration_rows is zero; verify exclusion handling still exists")

    candidates = as_list(data.get("candidate_submission_evidence_rows"))
    exclusions = as_list(data.get("needs_iteration_exclusions"))
    if len(candidates) != formal_pass:
        issues.append("candidate_submission_evidence_rows count must match formal_pass_rows")
    if len(exclusions) != formal_needs:
        issues.append("needs_iteration_exclusions count must match formal_needs_iteration_rows")

    candidate_ids: set[str] = set()
    for index, row_any in enumerate(candidates):
        row = as_dict(row_any)
        row_id = str(row.get("experiment_id", f"<candidate:{index}>"))
        candidate_ids.add(row_id)
        if not str(row.get("priority", "")):
            issues.append(f"candidate row has empty priority: {row_id}")
        if row.get("quality_status") != "pass":
            issues.append(f"candidate row must have quality_status=pass: {row_id}")
        if str(row.get("notes", "")).lower() == "metrics-only evidence":
            issues.append(f"candidate row must not be metrics-only evidence: {row_id}")
        if not str(row.get("metrics_file", "")):
            issues.append(f"candidate row missing metrics_file: {row_id}")
        if not str(row.get("claim_family", "")):
            issues.append(f"candidate row missing claim_family: {row_id}")

    for index, row_any in enumerate(exclusions):
        row = as_dict(row_any)
        row_id = str(row.get("experiment_id", f"<exclusion:{index}>"))
        if not str(row.get("priority", "")):
            issues.append(f"exclusion row has empty priority: {row_id}")
        if row.get("quality_status") != "needs_iteration":
            issues.append(f"exclusion row must have quality_status=needs_iteration: {row_id}")
        if row_id in candidate_ids:
            issues.append(f"row appears in both candidate and exclusion sets: {row_id}")
        if row.get("exclusion_reason") != "quality_status=needs_iteration":
            issues.append(f"exclusion row has wrong exclusion_reason: {row_id}")

    claim_boundary = as_dict(data.get("claim_boundary"))
    not_supported_text = "\n".join(str(item) for item in as_list(claim_boundary.get("not_supported")))
    missing_terms = text_contains_all(not_supported_text, REQUIRED_NOT_SUPPORTED_TERMS)
    for term in missing_terms:
        issues.append(f"claim_boundary.not_supported missing term: {term}")

    return issues, warnings


def validate_design_doc(path: Path) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []
    if not path.exists():
        issues.append(f"design document does not exist: {rel(path)}")
        return issues, warnings

    text = path.read_text(encoding="utf-8")
    for term in text_contains_all(text, REQUIRED_DESIGN_TERMS):
        issues.append(f"design document missing boundary term: {term}")

    dangerous_positive_markers = [
        "ROS2 planner readiness accepted",
        "UE build/runtime success accepted",
        "final closed-loop product acceptance",
        "all robustness cases pass",
    ]
    for marker in dangerous_positive_markers:
        for line in text.splitlines():
            if marker not in line:
                continue
            lowered = line.lower()
            if any(negated in lowered for negated in NEGATED_OVERCLAIM_MARKERS):
                continue
            issues.append(f"design document contains overclaim marker: {marker}")

    if "This table is a review candidate, not final PMO acceptance" not in text:
        warnings.append("design document should preserve candidate-not-final wording")

    return issues, warnings


def validate(evidence_map_path: Path, design_doc_path: Path | None = None) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []

    data = read_json(evidence_map_path)
    map_issues, map_warnings = validate_evidence_map(data)
    issues.extend(map_issues)
    warnings.extend(map_warnings)

    if design_doc_path is not None:
        doc_issues, doc_warnings = validate_design_doc(design_doc_path)
        issues.extend(doc_issues)
        warnings.extend(doc_warnings)

    return {
        "ok": not issues,
        "evidence_map": rel(evidence_map_path),
        "design_doc": rel(design_doc_path) if design_doc_path is not None else "",
        "issues": issues,
        "warnings": warnings,
        "row_counts": as_dict(data.get("row_counts")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "evidence_map",
        nargs="?",
        default="Results/static_audits/mworks_control_evidence_map_20260610/evidence_map.json",
        help="Path to evidence_map.json",
    )
    parser.add_argument(
        "--design-doc",
        default="Docs/Cache/design/old_architecture/08_赛题闭环实现证据矩阵.md",
        help="Optional historical/static evidence document to validate",
    )
    parser.add_argument("--output-json", help="Optional path for validation report")
    args = parser.parse_args()

    evidence_map_path = repo_path(args.evidence_map)
    design_doc_path = repo_path(args.design_doc) if args.design_doc else None

    try:
        report = validate(evidence_map_path, design_doc_path)
    except Exception as exc:
        report = {
            "ok": False,
            "evidence_map": rel(evidence_map_path),
            "design_doc": rel(design_doc_path) if design_doc_path is not None else "",
            "issues": [str(exc)],
            "warnings": [],
            "row_counts": {},
        }

    if args.output_json:
        output = repo_path(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
