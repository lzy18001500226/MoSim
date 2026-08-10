#!/usr/bin/env python3
"""Validate a report-source edit decision artifact.

This checker validates the human/PMO decision surface for applying previewed
edits to `Docs/报告/仿真分析报告_正文骨架.md`. It does not create or apply edits.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DECISION_TEMPLATE = (
    ROOT
    / "Results"
    / "static_audits"
    / "report_source_edit_decision_template_20260610"
    / "report_source_edit_decision.template.json"
)
DEFAULT_PATCH_PREVIEW = (
    ROOT
    / "Results"
    / "static_audits"
    / "simulation_report_patch_preview_20260610"
    / "simulation_report_patch_preview.json"
)
DEFAULT_OUTPUT_JSON = (
    ROOT
    / "Results"
    / "static_audits"
    / "report_source_edit_decision_template_20260610"
    / "report_source_edit_decision_check.json"
)

VALID_DECISIONS = ["pending_review", "approved", "rejected", "narrowed"]
CANONICAL_REPORT_SOURCE = "Docs/报告/仿真分析报告_正文骨架.md"
LEGACY_REPORT_SOURCE = "Docs/simulation_report.md"
REQUIRED_BOUNDARIES = [
    "Do not claim final PMO acceptance.",
    "Do not claim final submission ready.",
    "Do not claim planner_ready or closed_loop.",
    "Do not claim UE build/runtime/editor success.",
    "Do not delete historical evidence without explicit approval.",
]
PLACEHOLDER_VALUES = {"", "<user_or_PMO>", "<ISO8601_after_review>"}


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


def string_list(value: Any) -> tuple[list[str], bool]:
    if not isinstance(value, list):
        return [], False
    if not all(isinstance(item, str) and item for item in value):
        return [str(item) for item in value], False
    return list(value), True


def preview_ids_from_patch_preview(patch_preview: dict[str, Any]) -> set[str]:
    previews = patch_preview.get("previews", [])
    if not isinstance(previews, list):
        return set()
    return {
        str(item.get("preview_id", ""))
        for item in previews
        if isinstance(item, dict) and item.get("preview_id")
    }


def looks_like_reviewed_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or value in PLACEHOLDER_VALUES:
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return True


def validate_decision_template(
    template: dict[str, Any],
    patch_preview: dict[str, Any],
    decision_path: Path,
    patch_preview_path: Path,
) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []

    available_from_preview = preview_ids_from_patch_preview(patch_preview)
    decision = str(template.get("decision", ""))
    approved, approved_is_list = string_list(template.get("approved_preview_ids", []))
    rejected, rejected_is_list = string_list(template.get("rejected_preview_ids", []))
    available_in_template, available_is_list = string_list(template.get("available_preview_ids", []))
    required_boundaries, boundaries_is_list = string_list(template.get("required_boundaries", []))

    if decision not in VALID_DECISIONS:
        issues.append(f"decision must be one of {VALID_DECISIONS}")
    if not approved_is_list:
        issues.append("approved_preview_ids must be a list of non-empty strings")
    if not rejected_is_list:
        issues.append("rejected_preview_ids must be a list of non-empty strings")
    if not available_is_list:
        issues.append("available_preview_ids must be a list of non-empty strings")
    if not boundaries_is_list:
        issues.append("required_boundaries must be a list of non-empty strings")

    duplicate_approved = sorted({item for item in approved if approved.count(item) > 1})
    duplicate_rejected = sorted({item for item in rejected if rejected.count(item) > 1})
    if duplicate_approved:
        issues.append("approved_preview_ids contains duplicates: " + ", ".join(duplicate_approved))
    if duplicate_rejected:
        issues.append("rejected_preview_ids contains duplicates: " + ", ".join(duplicate_rejected))

    overlap = sorted(set(approved) & set(rejected))
    if overlap:
        issues.append("preview ids cannot be both approved and rejected: " + ", ".join(overlap))

    unknown = sorted((set(approved) | set(rejected) | set(available_in_template)) - available_from_preview)
    if unknown:
        issues.append("decision references unknown preview ids: " + ", ".join(unknown))

    missing_from_template = sorted(available_from_preview - set(available_in_template))
    if missing_from_template:
        issues.append("available_preview_ids omits patch preview ids: " + ", ".join(missing_from_template))

    safe_flag = template.get("safe_to_apply_report_source_edits") is True
    if safe_flag and decision not in {"approved", "narrowed"}:
        issues.append("safe_to_apply_report_source_edits=true requires approved or narrowed decision")
    if decision == "pending_review" and approved:
        issues.append("pending_review decision must not approve preview ids")
    if decision == "pending_review" and safe_flag:
        issues.append("pending_review decision must keep safe_to_apply_report_source_edits=false")
    if decision == "rejected" and approved:
        issues.append("rejected decision must not approve preview ids")
    if decision == "rejected" and safe_flag:
        issues.append("rejected decision must keep safe_to_apply_report_source_edits=false")
    if decision in {"approved", "narrowed"} and not approved:
        issues.append("approved/narrowed decision must name approved_preview_ids")
    if decision in {"approved", "narrowed"} and not safe_flag:
        issues.append("approved/narrowed decision must set safe_to_apply_report_source_edits=true")

    missing_boundaries = [item for item in REQUIRED_BOUNDARIES if item not in required_boundaries]
    if missing_boundaries:
        issues.append("required_boundaries missing: " + " | ".join(missing_boundaries))

    decision_owner = template.get("decision_owner")
    decided_at = template.get("decided_at")
    if decision in {"approved", "narrowed"}:
        if not isinstance(decision_owner, str) or decision_owner in PLACEHOLDER_VALUES:
            issues.append("approved/narrowed decision must record a non-placeholder decision_owner")
        if not looks_like_reviewed_timestamp(decided_at):
            issues.append("approved/narrowed decision must record an ISO8601 decided_at timestamp")
        if not str(template.get("review_notes", "")).strip():
            warnings.append("approved/narrowed decision has empty review_notes")
    elif decision == "pending_review":
        warnings.append("decision is pending_review and does not authorize report-source edits")

    applies_to = template.get("applies_to", {})
    if not isinstance(applies_to, dict):
        issues.append("applies_to must be an object")
    else:
        report_source = applies_to.get("simulation_report")
        if report_source not in {CANONICAL_REPORT_SOURCE, LEGACY_REPORT_SOURCE}:
            issues.append(
                "applies_to.simulation_report must be "
                f"{CANONICAL_REPORT_SOURCE} (or the preserved historical {LEGACY_REPORT_SOURCE})"
            )
        elif report_source == LEGACY_REPORT_SOURCE:
            warnings.append(
                "decision artifact uses the preserved historical report path; "
                f"new artifacts must use {CANONICAL_REPORT_SOURCE}"
            )
        if applies_to.get("patch_preview") != rel(patch_preview_path):
            issues.append("applies_to.patch_preview must match the checked patch preview path")

    authorizes_application = (
        not issues
        and decision in {"approved", "narrowed"}
        and bool(approved)
        and safe_flag
    )

    return {
        "ok": not issues,
        "decision_path": rel(decision_path),
        "patch_preview": rel(patch_preview_path),
        "decision": decision,
        "valid_decisions": VALID_DECISIONS,
        "approved_preview_count": len(approved),
        "rejected_preview_count": len(rejected),
        "available_preview_count": len(available_from_preview),
        "safe_to_apply_report_source_edits": safe_flag,
        "authorizes_application": authorizes_application,
        "issues": issues,
        "warnings": warnings,
        "claim_boundary": [
            "This checker validates a decision artifact only.",
            "It does not edit Docs/报告/仿真分析报告_正文骨架.md.",
            "It does not approve pending_review decisions.",
            "It does not export PDFs/video or write PMO final acceptance.",
        ],
    }


def validate_paths(decision_path: Path, patch_preview_path: Path) -> dict[str, Any]:
    try:
        template = read_json(decision_path)
        patch_preview = read_json(patch_preview_path)
        return validate_decision_template(template, patch_preview, decision_path, patch_preview_path)
    except Exception as exc:
        return {
            "ok": False,
            "decision_path": rel(decision_path),
            "patch_preview": rel(patch_preview_path),
            "decision": "unreadable",
            "valid_decisions": VALID_DECISIONS,
            "approved_preview_count": 0,
            "rejected_preview_count": 0,
            "available_preview_count": 0,
            "safe_to_apply_report_source_edits": False,
            "authorizes_application": False,
            "issues": [str(exc)],
            "warnings": [],
            "claim_boundary": [
                "This checker validates a decision artifact only.",
                "It does not edit Docs/报告/仿真分析报告_正文骨架.md.",
                "It does not approve pending_review decisions.",
                "It does not export PDFs/video or write PMO final acceptance.",
            ],
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decision", default=str(DEFAULT_DECISION_TEMPLATE.relative_to(ROOT)))
    parser.add_argument("--patch-preview", default=str(DEFAULT_PATCH_PREVIEW.relative_to(ROOT)))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON.relative_to(ROOT)))
    args = parser.parse_args()

    result = validate_paths(repo_path(args.decision), repo_path(args.patch_preview))
    output_json = repo_path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
