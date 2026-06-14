#!/usr/bin/env python3
"""Validate final-output execution decisions without executing them.

This checker validates the human/PMO decision surface for PDF export, demo
video recording/rendering, and canonical final acceptance. It does not create
`Results/submission`, run Pandoc, record video, or write acceptance packets.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DECISION = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_output_execution_decision_20260610"
    / "final_output_execution_decision.template.json"
)
DEFAULT_PDF_PLAN = ROOT / "Results/static_audits/pdf_export_dry_run_plan_20260610/pdf_export_dry_run_plan.json"
DEFAULT_VIDEO_PLAN = ROOT / "Results/static_audits/demo_video_storyboard_plan_20260610/demo_video_storyboard_plan.json"
DEFAULT_ACCEPTANCE_PREREQ = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_acceptance_packet_prereq_20260610"
    / "final_acceptance_packet_prereq_plan.json"
)
DEFAULT_OUTPUT_JSON = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_output_execution_decision_20260610"
    / "final_output_execution_decision_check.json"
)

VALID_ACTION_DECISIONS = ["pending_review", "approved", "rejected"]
PLACEHOLDER_VALUES = {"", "<user_or_PMO>", "<ISO8601_after_review>"}
ACTION_GATE_MAP = {
    "pdf_export": {
        "artifact": "pdf_export_plan",
        "ready_key": "safe_to_run_pdf_export_now",
        "forbidden_now_key": "runs_pandoc_now",
    },
    "demo_video_recording": {
        "artifact": "demo_video_storyboard_plan",
        "ready_key": "safe_to_record_demo_video_now",
        "forbidden_now_key": "records_or_renders_video_now",
    },
    "final_acceptance_packet": {
        "artifact": "final_acceptance_packet_prereq_plan",
        "ready_key": "safe_to_write_final_acceptance_packet_now",
        "forbidden_now_key": "writes_canonical_acceptance_packet_now",
    },
}
REQUIRED_BOUNDARIES = [
    "Do not create Results/submission unless final-output execution is explicitly approved and upstream gates pass.",
    "Do not run Pandoc unless pdf_export is approved and pdf_export_plan.safe_to_run_pdf_export_now=true.",
    "Do not record or render demo video unless demo_video_recording is approved and storyboard gate permits it.",
    "Do not write canonical PMO final acceptance unless final_acceptance_packet is approved and prerequisite gate permits it.",
    "Do not claim final submission ready until final artifact manifest passes and PMO accepts it.",
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


def summary(data: dict[str, Any]) -> dict[str, Any]:
    value = data.get("summary", {})
    return value if isinstance(value, dict) else {}


def string_list(value: Any) -> tuple[list[str], bool]:
    if not isinstance(value, list):
        return [], False
    if not all(isinstance(item, str) and item for item in value):
        return [str(item) for item in value], False
    return list(value), True


def looks_like_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or value in PLACEHOLDER_VALUES:
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return True


def validate_action(
    action_id: str,
    action: dict[str, Any],
    upstream_ready: bool,
) -> tuple[dict[str, Any], list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []
    decision = str(action.get("decision", ""))
    if decision not in VALID_ACTION_DECISIONS:
        issues.append(f"{action_id}.decision must be one of {VALID_ACTION_DECISIONS}")

    approved = decision == "approved"
    if action.get("approved") is not approved:
        issues.append(f"{action_id}.approved must match decision==approved")

    if approved:
        if not isinstance(action.get("approved_by"), str) or action.get("approved_by") in PLACEHOLDER_VALUES:
            issues.append(f"{action_id} approval must record a non-placeholder approved_by")
        if not looks_like_timestamp(action.get("approved_at")):
            issues.append(f"{action_id} approval must record an ISO8601 approved_at timestamp")
        if not str(action.get("review_notes", "")).strip():
            warnings.append(f"{action_id} approval has empty review_notes")
        if not upstream_ready:
            issues.append(f"{action_id} is approved but its upstream readiness gate is false")
    elif decision == "pending_review":
        warnings.append(f"{action_id} is pending_review and does not authorize execution")

    return (
        {
            "action_id": action_id,
            "decision": decision,
            "approved": approved,
            "upstream_ready": upstream_ready,
            "authorizes_execution": approved and upstream_ready and not issues,
        },
        issues,
        warnings,
    )


def validate_decision(
    decision_doc: dict[str, Any],
    pdf_plan: dict[str, Any],
    video_plan: dict[str, Any],
    acceptance_prereq: dict[str, Any],
    decision_path: Path,
) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []

    actions = decision_doc.get("actions", {})
    if not isinstance(actions, dict):
        issues.append("actions must be an object")
        actions = {}

    boundaries, boundaries_are_list = string_list(decision_doc.get("required_boundaries", []))
    if not boundaries_are_list:
        issues.append("required_boundaries must be a list of non-empty strings")
    missing_boundaries = [item for item in REQUIRED_BOUNDARIES if item not in boundaries]
    if missing_boundaries:
        issues.append("required_boundaries missing: " + " | ".join(missing_boundaries))

    upstream = {
        "pdf_export": summary(pdf_plan).get("safe_to_run_pdf_export_now") is True,
        "demo_video_recording": summary(video_plan).get("safe_to_record_demo_video_now") is True,
        "final_acceptance_packet": summary(acceptance_prereq).get("safe_to_write_final_acceptance_packet_now") is True,
    }

    action_results: dict[str, Any] = {}
    for action_id in ACTION_GATE_MAP:
        action = actions.get(action_id)
        if not isinstance(action, dict):
            issues.append(f"missing action object: {action_id}")
            action = {}
        result, action_issues, action_warnings = validate_action(action_id, action, upstream[action_id])
        action_results[action_id] = result
        issues.extend(action_issues)
        warnings.extend(action_warnings)

    explicit_flags = decision_doc.get("execution_flags", {})
    if not isinstance(explicit_flags, dict):
        issues.append("execution_flags must be an object")
        explicit_flags = {}
    expected_false_flags = [
        "creates_submission_dir_now",
        "runs_pandoc_now",
        "records_or_renders_video_now",
        "writes_canonical_acceptance_packet_now",
        "generates_final_outputs",
        "final_acceptance",
    ]
    for flag in expected_false_flags:
        if explicit_flags.get(flag) is not False:
            issues.append(f"execution_flags.{flag} must be false in this static decision surface")

    authorizes_pdf_export = action_results.get("pdf_export", {}).get("authorizes_execution") is True
    authorizes_demo_video_recording = (
        action_results.get("demo_video_recording", {}).get("authorizes_execution") is True
    )
    authorizes_final_acceptance_packet = (
        action_results.get("final_acceptance_packet", {}).get("authorizes_execution") is True
    )

    return {
        "ok": not issues,
        "check_id": "final_output_execution_decision_20260610",
        "status": "execution_decision_check_not_execution",
        "decision_path": rel(decision_path),
        "summary": {
            "issue_count": len(issues),
            "warning_count": len(warnings),
            "authorizes_pdf_export": authorizes_pdf_export,
            "authorizes_demo_video_recording": authorizes_demo_video_recording,
            "authorizes_final_acceptance_packet": authorizes_final_acceptance_packet,
            "creates_submission_dir_now": False,
            "runs_pandoc_now": False,
            "records_or_renders_video_now": False,
            "writes_canonical_acceptance_packet_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "actions": action_results,
        "upstream_ready": upstream,
        "issues": issues,
        "warnings": warnings,
        "claim_boundary": [
            "This checker validates final-output execution decisions only.",
            "It does not create Results/submission.",
            "It does not run Pandoc.",
            "It does not record or render demo video.",
            "It does not write canonical PMO final acceptance.",
        ],
    }


def validate_paths(
    decision_path: Path,
    pdf_plan_path: Path,
    video_plan_path: Path,
    acceptance_prereq_path: Path,
) -> dict[str, Any]:
    try:
        return validate_decision(
            read_json(decision_path),
            read_json(pdf_plan_path),
            read_json(video_plan_path),
            read_json(acceptance_prereq_path),
            decision_path,
        )
    except Exception as exc:
        return {
            "ok": False,
            "check_id": "final_output_execution_decision_20260610",
            "status": "execution_decision_check_not_execution",
            "decision_path": rel(decision_path),
            "summary": {
                "issue_count": 1,
                "warning_count": 0,
                "authorizes_pdf_export": False,
                "authorizes_demo_video_recording": False,
                "authorizes_final_acceptance_packet": False,
                "creates_submission_dir_now": False,
                "runs_pandoc_now": False,
                "records_or_renders_video_now": False,
                "writes_canonical_acceptance_packet_now": False,
                "generates_final_outputs": False,
                "final_acceptance": False,
            },
            "actions": {},
            "upstream_ready": {},
            "issues": [str(exc)],
            "warnings": [],
            "claim_boundary": [
                "This checker validates final-output execution decisions only.",
                "It does not create Results/submission.",
                "It does not run Pandoc.",
                "It does not record or render demo video.",
                "It does not write canonical PMO final acceptance.",
            ],
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decision", default=str(DEFAULT_DECISION.relative_to(ROOT)))
    parser.add_argument("--pdf-plan", default=str(DEFAULT_PDF_PLAN.relative_to(ROOT)))
    parser.add_argument("--video-plan", default=str(DEFAULT_VIDEO_PLAN.relative_to(ROOT)))
    parser.add_argument("--acceptance-prereq", default=str(DEFAULT_ACCEPTANCE_PREREQ.relative_to(ROOT)))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON.relative_to(ROOT)))
    args = parser.parse_args()

    result = validate_paths(
        repo_path(args.decision),
        repo_path(args.pdf_plan),
        repo_path(args.video_plan),
        repo_path(args.acceptance_prereq),
    )
    output_json = repo_path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
