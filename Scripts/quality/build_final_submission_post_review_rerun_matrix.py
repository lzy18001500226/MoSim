#!/usr/bin/env python3
"""Build a non-executing post-review rerun readiness matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROGRESS_SNAPSHOT = (
    ROOT
    / "Results/static_audits/final_submission_review_progress_snapshot_20260610"
    / "final_submission_review_progress_snapshot.json"
)
DEFAULT_REPORT_DECISION = (
    ROOT
    / "Results/static_audits/report_source_edit_decision_template_20260610"
    / "report_source_edit_decision.template.json"
)
DEFAULT_FINAL_OUTPUT_DECISION = (
    ROOT
    / "Results/static_audits/final_output_execution_decision_20260610"
    / "final_output_execution_decision.template.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_post_review_rerun_matrix_20260610"

REPORT_SOURCE_RERUN = [
    "python Scripts/quality/check_report_source_edit_decision.py",
    "python Scripts/quality/build_simulation_report_source_edit_readiness_gate.py",
    "python Scripts/quality/build_simulation_report_source_edit_application_plan.py",
    "python Scripts/quality/build_submission_source_output_readiness.py",
    "python Scripts/quality/build_pdf_export_dry_run_plan.py",
    "python Scripts/quality/build_final_acceptance_packet_prereq_plan.py",
    "python Scripts/quality/build_final_submission_readiness_dashboard.py",
    "python Scripts/quality/build_final_submission_human_action_checklist.py",
    "python Scripts/quality/build_final_submission_reviewer_action_map.py",
    "python Scripts/quality/build_final_submission_human_review_decision_packet_template.py",
    "python Scripts/quality/build_final_submission_human_review_guide.py",
    "python Scripts/quality/check_final_submission_readiness_chain.py",
    "python Scripts/quality/check_final_submission_refresh_order.py",
    "python Scripts/quality/build_final_submission_static_audit_index.py",
    "python Scripts/quality/build_final_submission_blocked_gate_triage_map.py",
    "python Scripts/quality/build_final_submission_human_decision_diff_template.py",
    "python Scripts/quality/build_final_submission_reviewer_quickstart.py",
    "python Scripts/quality/build_final_submission_review_progress_snapshot.py",
]

STORYBOARD_RERUN = [
    "python Scripts/quality/build_demo_video_storyboard_plan.py",
    "python Scripts/quality/check_final_output_execution_decision.py",
    "python Scripts/quality/build_final_submission_readiness_dashboard.py",
    "python Scripts/quality/build_final_submission_human_action_checklist.py",
    "python Scripts/quality/build_final_submission_reviewer_action_map.py",
    "python Scripts/quality/build_final_submission_human_review_decision_packet_template.py",
    "python Scripts/quality/build_final_submission_human_review_guide.py",
    "python Scripts/quality/check_final_submission_readiness_chain.py",
    "python Scripts/quality/check_final_submission_refresh_order.py",
    "python Scripts/quality/build_final_submission_static_audit_index.py",
    "python Scripts/quality/build_final_submission_blocked_gate_triage_map.py",
    "python Scripts/quality/build_final_submission_human_decision_diff_template.py",
    "python Scripts/quality/build_final_submission_reviewer_quickstart.py",
    "python Scripts/quality/build_final_submission_review_progress_snapshot.py",
]

FINAL_OUTPUT_RERUN = [
    "python Scripts/quality/check_final_output_execution_decision.py",
    "python Scripts/quality/build_final_submission_readiness_dashboard.py",
    "python Scripts/quality/build_final_submission_human_action_checklist.py",
    "python Scripts/quality/build_final_submission_reviewer_action_map.py",
    "python Scripts/quality/build_final_submission_human_review_decision_packet_template.py",
    "python Scripts/quality/build_final_submission_human_review_guide.py",
    "python Scripts/quality/check_final_submission_readiness_chain.py",
    "python Scripts/quality/check_final_submission_refresh_order.py",
    "python Scripts/quality/build_final_submission_static_audit_index.py",
    "python Scripts/quality/build_final_submission_blocked_gate_triage_map.py",
    "python Scripts/quality/build_final_submission_human_decision_diff_template.py",
    "python Scripts/quality/build_final_submission_reviewer_quickstart.py",
    "python Scripts/quality/build_final_submission_review_progress_snapshot.py",
]

COMMON_FORBIDDEN = [
    "Do not apply report-source edits from this matrix.",
    "Do not run post-review checkers from this matrix.",
    "Do not export PDFs from this matrix.",
    "Do not record or render demo video from this matrix.",
    "Do not write PMO final acceptance from this matrix.",
    "Do not run live MWORKS, ROS2, UE, or visible-thread dispatch from this matrix.",
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


def report_source_row(report_decision: dict[str, Any]) -> dict[str, Any]:
    decision = report_decision.get("decision", "")
    safe_to_apply = report_decision.get("safe_to_apply_report_source_edits") is True
    approved_count = len(report_decision.get("approved_preview_ids", []))
    if decision in {"approved", "narrowed"} and safe_to_apply and approved_count > 0:
        readiness = "rerun_allowed_after_separate_authorized_source_edit"
    elif decision == "rejected":
        readiness = "rerun_allowed_to_refresh_blocked_state_only"
    else:
        readiness = "blocked_pending_human_review"
    return {
        "action_id": "A1-approve-or-reject-report-source-edits",
        "source_template": rel(DEFAULT_REPORT_DECISION),
        "current_decision": decision,
        "current_safe_flag": safe_to_apply,
        "expected_future_decisions": ["approved", "rejected", "narrowed", "pending_review"],
        "rerun_readiness": readiness,
        "rerun_commands_after_separate_review_edit": REPORT_SOURCE_RERUN,
        "execution_still_requires": [
            "explicit approved or narrowed report-source decision",
            "non-empty approved_preview_ids when edits are approved",
            "a separate authorized report-source edit step before final source-output readiness can pass",
        ],
        "forbidden_actions": COMMON_FORBIDDEN,
        "runs_now": False,
        "approves_now": False,
    }


def storyboard_row(final_output_decision: dict[str, Any]) -> dict[str, Any]:
    video_action = final_output_decision.get("actions", {}).get("demo_video_recording", {})
    decision = video_action.get("decision", "")
    approved = video_action.get("approved") is True
    readiness = "rerun_allowed_after_storyboard_review" if decision in {"approved", "rejected"} else "blocked_pending_human_review"
    return {
        "action_id": "A3-review-demo-storyboard",
        "source_template": rel(DEFAULT_FINAL_OUTPUT_DECISION),
        "current_decision": decision,
        "current_approved_flag": approved,
        "expected_future_decisions": ["approved", "rejected", "pending_review"],
        "rerun_readiness": readiness,
        "rerun_commands_after_separate_review_edit": STORYBOARD_RERUN,
        "execution_still_requires": [
            "storyboard review outcome recorded in a separate decision step",
            "demo video recording remains blocked until final-output execution decision and upstream gates pass",
        ],
        "forbidden_actions": COMMON_FORBIDDEN,
        "runs_now": False,
        "approves_now": False,
    }


def final_output_row(final_output_decision: dict[str, Any]) -> dict[str, Any]:
    actions = final_output_decision.get("actions", {})
    action_decisions = {
        action_id: {
            "decision": item.get("decision", ""),
            "approved": item.get("approved") is True,
        }
        for action_id, item in actions.items()
        if isinstance(item, dict)
    }
    any_approved = any(item["approved"] for item in action_decisions.values())
    all_reviewed = all(item["decision"] in {"approved", "rejected"} for item in action_decisions.values())
    if any_approved:
        readiness = "rerun_allowed_but_execution_still_requires_upstream_gates"
    elif all_reviewed and action_decisions:
        readiness = "rerun_allowed_to_refresh_rejected_or_blocked_state"
    else:
        readiness = "blocked_pending_human_review"
    return {
        "action_id": "A6-review-final-output-execution-decision",
        "source_template": rel(DEFAULT_FINAL_OUTPUT_DECISION),
        "current_action_decisions": action_decisions,
        "expected_future_decisions": ["approved", "rejected", "pending_review"],
        "rerun_readiness": readiness,
        "rerun_commands_after_separate_review_edit": FINAL_OUTPUT_RERUN,
        "execution_still_requires": [
            "upstream source-output readiness true before PDF export",
            "PDF engine available before PDF export",
            "storyboard gate permits recording before demo video work",
            "final acceptance prerequisite gate true before canonical PMO packet writing",
            "a separate final-output execution authorization before any output generation",
        ],
        "forbidden_actions": COMMON_FORBIDDEN,
        "runs_now": False,
        "approves_now": False,
    }


def build_matrix(
    progress_snapshot_path: Path,
    report_decision_path: Path,
    final_output_decision_path: Path,
) -> dict[str, Any]:
    progress_snapshot = read_json(progress_snapshot_path)
    report_decision = read_json(report_decision_path)
    final_output_decision = read_json(final_output_decision_path)
    rows = [
        report_source_row(report_decision),
        storyboard_row(final_output_decision),
        final_output_row(final_output_decision),
    ]
    blocked_rows = [row for row in rows if row["rerun_readiness"] == "blocked_pending_human_review"]
    total_commands = sum(len(row["rerun_commands_after_separate_review_edit"]) for row in rows)
    unique_commands = sorted(
        {command for row in rows for command in row["rerun_commands_after_separate_review_edit"]}
    )
    return {
        "matrix_id": "final_submission_post_review_rerun_matrix_20260610",
        "status": "post_review_rerun_matrix_not_execution",
        "sources": {
            "review_progress_snapshot": rel(progress_snapshot_path),
            "report_source_edit_decision": rel(report_decision_path),
            "final_output_execution_decision": rel(final_output_decision_path),
        },
        "source_statuses": {
            "review_progress_snapshot": progress_snapshot.get("status", ""),
            "report_source_edit_decision": report_decision.get("status", ""),
            "final_output_execution_decision": final_output_decision.get("status", ""),
        },
        "summary": {
            "matrix_row_count": len(rows),
            "blocked_pending_review_row_count": len(blocked_rows),
            "total_rerun_command_count": total_commands,
            "unique_rerun_command_count": len(unique_commands),
            "automated_execution_allowed": False,
            "runs_rerun_commands_now": False,
            "applies_decisions_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "rows": rows,
        "unique_rerun_commands": unique_commands,
        "claim_boundary": [
            "This matrix is a static planning artifact for future post-review reruns.",
            "It does not edit decision templates.",
            "It does not approve decisions.",
            "It does not run any listed rerun command.",
            "It does not apply report-source edits.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(matrix: dict[str, Any], path: Path) -> None:
    summary = matrix["summary"]
    lines = [
        "# Final Submission Post-Review Rerun Matrix, 2026-06-10",
        "",
        f"Status: `{matrix['status']}`",
        "",
        "## Summary",
        "",
        f"- Matrix rows: `{summary['matrix_row_count']}`",
        f"- Blocked pending-review rows: `{summary['blocked_pending_review_row_count']}`",
        f"- Total rerun commands: `{summary['total_rerun_command_count']}`",
        f"- Unique rerun commands: `{summary['unique_rerun_command_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Runs rerun commands now: `{summary['runs_rerun_commands_now']}`",
        f"- Applies decisions now: `{summary['applies_decisions_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Matrix Rows",
        "",
    ]
    for row in matrix["rows"]:
        lines.extend(
            [
                f"### {row['action_id']}",
                "",
                f"- Rerun readiness: `{row['rerun_readiness']}`",
                f"- Runs now: `{row['runs_now']}`",
                f"- Approves now: `{row['approves_now']}`",
                "- Rerun commands after separate review edit:",
            ]
        )
        for command in row["rerun_commands_after_separate_review_edit"]:
            lines.append(f"  - `{command}`")
        lines.append("- Execution still requires:")
        for item in row["execution_still_requires"]:
            lines.append(f"  - {item}")
        lines.append("")
    lines.extend(["## Claim Boundary", ""])
    for item in matrix["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--progress-snapshot", default=str(DEFAULT_PROGRESS_SNAPSHOT.relative_to(ROOT)))
    parser.add_argument("--report-decision", default=str(DEFAULT_REPORT_DECISION.relative_to(ROOT)))
    parser.add_argument("--final-output-decision", default=str(DEFAULT_FINAL_OUTPUT_DECISION.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    matrix = build_matrix(
        repo_path(args.progress_snapshot),
        repo_path(args.report_decision),
        repo_path(args.final_output_decision),
    )
    json_path = output_dir / "final_submission_post_review_rerun_matrix.json"
    md_path = output_dir / "final_submission_post_review_rerun_matrix.md"
    json_path.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(matrix, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "matrix_json": rel(json_path),
                "matrix_markdown": rel(md_path),
                "matrix_row_count": matrix["summary"]["matrix_row_count"],
                "blocked_pending_review_row_count": matrix["summary"]["blocked_pending_review_row_count"],
                "unique_rerun_command_count": matrix["summary"]["unique_rerun_command_count"],
                "automated_execution_allowed": matrix["summary"]["automated_execution_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
