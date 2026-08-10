#!/usr/bin/env python3
"""Build a pre/post audit checklist for future report-source edit application.

This artifact documents what must be true before a future authorized edit may
touch Docs/报告/仿真分析报告_正文骨架.md, and which checks must run after editing. It
does not create backups, edit files, run patches, or execute guard commands.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_APPLICATION_PLAN = (
    ROOT
    / "Results/static_audits/simulation_report_source_edit_application_plan_20260610"
    / "simulation_report_source_edit_application_plan.json"
)
DEFAULT_REVIEWER_SUMMARY = (
    ROOT
    / "Results/static_audits/simulation_report_source_edit_reviewer_summary_20260610"
    / "simulation_report_source_edit_reviewer_summary.json"
)
DEFAULT_DECISION_CHECK = (
    ROOT
    / "Results/static_audits/report_source_edit_decision_template_20260610"
    / "report_source_edit_decision_check.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/simulation_report_source_edit_application_audit_checklist_20260610"


PRE_EDIT_CHECKS = [
    {
        "check_id": "explicit_a1_approval",
        "required": True,
        "evidence": "report_source_edit_decision_check.authorizes_application=true",
        "current_status": "blocked_pending_review",
        "why": "Report source edits need explicit human/PMO approval before any file write.",
    },
    {
        "check_id": "application_plan_regenerated_after_decision",
        "required": True,
        "evidence": "simulation_report_source_edit_application_plan generated after A1 decision update",
        "current_status": "blocked_pending_review",
        "why": "Approved/narrowed preview ids must be reflected in the non-applying application plan.",
    },
    {
        "check_id": "reviewer_summary_consulted",
        "required": True,
        "evidence": "simulation_report_source_edit_reviewer_summary reviewed for all seven preview snippets",
        "current_status": "available_for_review",
        "why": "High-impact boundary changes and candidate inserts need manual review before editing.",
    },
    {
        "check_id": "pre_edit_diff_captured",
        "required": True,
        "evidence": "git diff -- Docs/报告/仿真分析报告_正文骨架.md captured before edits",
        "current_status": "not_captured_by_this_artifact",
        "why": "The operator must know whether the report already has unrelated edits.",
    },
    {
        "check_id": "backup_or_revert_path_declared",
        "required": True,
        "evidence": "backup copy or exact git diff/revert plan recorded before edits",
        "current_status": "not_created_by_this_artifact",
        "why": "Report-source edits must be reversible without losing unrelated work.",
    },
    {
        "check_id": "target_file_scope_limited",
        "required": True,
        "evidence": "write scope limited to Docs/报告/仿真分析报告_正文骨架.md and generated audit outputs",
        "current_status": "planned_only",
        "why": "A report-source application step must not drift into final output generation.",
    },
    {
        "check_id": "post_edit_guard_plan_ready",
        "required": True,
        "evidence": "post_edit_guard_commands listed in this artifact",
        "current_status": "ready",
        "why": "Every future report-source edit must be followed by boundary and chain checks.",
    },
]

POST_EDIT_GUARD_COMMANDS = [
    "python Scripts/quality/check_report_manual_current_boundaries.py --output-json Results/static_audits/submission_evidence_manifest_20260610/report_manual_current_boundaries_check.json",
    "python Scripts/quality/check_pre_submit_manifest_alignment.py Docs/Workflows/pre_submit_check.md --output-json Results/static_audits/submission_evidence_manifest_20260610/pre_submit_manifest_alignment_check.json",
    "python Scripts/quality/build_simulation_report_source_edit_readiness_gate.py",
    "python Scripts/quality/build_simulation_report_source_edit_application_plan.py",
    "python Scripts/quality/build_submission_source_output_readiness.py",
    "python Scripts/quality/build_pdf_export_dry_run_plan.py",
    "python Scripts/quality/build_final_submission_readiness_dashboard.py",
    "python Scripts/quality/build_final_submission_human_action_checklist.py",
    "python Scripts/quality/build_final_submission_reviewer_action_map.py",
    "python Scripts/quality/build_final_submission_human_review_decision_packet_template.py",
    "python Scripts/quality/build_final_submission_human_review_guide.py",
    "python Scripts/quality/check_final_submission_readiness_chain.py",
    "python Scripts/quality/check_final_submission_refresh_order.py",
    "python Scripts/quality/build_final_submission_static_audit_index.py",
    "python Scripts/tests/test_report_manual_current_boundaries.py",
    "python Scripts/tests/test_pre_submit_manifest_alignment.py",
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


def build_checklist(application_plan_path: Path, reviewer_summary_path: Path, decision_check_path: Path) -> dict[str, Any]:
    application_plan = read_json(application_plan_path)
    reviewer_summary = read_json(reviewer_summary_path)
    decision_check = read_json(decision_check_path)
    decision_authorizes = decision_check.get("authorizes_application") is True
    application_safe = application_plan.get("summary", {}).get("safe_to_apply_report_source_edits_now") is True
    review_count = reviewer_summary.get("summary", {}).get("manual_review_required_count", 0)
    pre_edit_ready = decision_authorizes and application_safe
    checks = []
    for check in PRE_EDIT_CHECKS:
        item = dict(check)
        if check["check_id"] == "explicit_a1_approval" and decision_authorizes:
            item["current_status"] = "satisfied"
        elif check["check_id"] == "application_plan_regenerated_after_decision" and application_safe:
            item["current_status"] = "satisfied"
        checks.append(item)
    return {
        "checklist_id": "simulation_report_source_edit_application_audit_checklist_20260610",
        "status": "source_edit_application_audit_checklist_not_execution",
        "inputs": {
            "simulation_report": "Docs/报告/仿真分析报告_正文骨架.md",
            "source_edit_application_plan": rel(application_plan_path),
            "source_edit_reviewer_summary": rel(reviewer_summary_path),
            "report_source_edit_decision_check": rel(decision_check_path),
        },
        "summary": {
            "pre_edit_check_count": len(checks),
            "post_edit_guard_command_count": len(POST_EDIT_GUARD_COMMANDS),
            "manual_review_required_count": review_count,
            "decision_authorizes_application": decision_authorizes,
            "application_plan_safe_to_apply": application_safe,
            "safe_to_apply_report_source_edits_now": pre_edit_ready,
            "creates_backup_now": False,
            "edits_report_source": False,
            "applies_report_source_edits_now": False,
            "runs_post_edit_guards_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "pre_edit_checks": checks,
        "post_edit_guard_commands": POST_EDIT_GUARD_COMMANDS,
        "forbidden_now": [
            "Do not edit Docs/报告/仿真分析报告_正文骨架.md from this checklist.",
            "Do not create or overwrite backups from this checklist.",
            "Do not run patch/apply commands from this checklist.",
            "Do not export PDFs, record video, or write PMO final acceptance.",
        ],
        "claim_boundary": [
            "This checklist is a static audit plan only.",
            "It does not edit Docs/报告/仿真分析报告_正文骨架.md.",
            "It does not create backups or restore points.",
            "It does not execute post-edit guard commands.",
            "It does not export PDFs/video or write PMO final acceptance.",
        ],
    }


def write_markdown(checklist: dict[str, Any], path: Path) -> None:
    summary = checklist["summary"]
    lines = [
        "# Simulation Report Source Edit Application Audit Checklist, 2026-06-10",
        "",
        f"Status: `{checklist['status']}`",
        "",
        "## Summary",
        "",
        f"- Pre-edit checks: `{summary['pre_edit_check_count']}`",
        f"- Post-edit guard commands: `{summary['post_edit_guard_command_count']}`",
        f"- Manual review required: `{summary['manual_review_required_count']}`",
        f"- Decision authorizes application: `{summary['decision_authorizes_application']}`",
        f"- Application plan safe to apply: `{summary['application_plan_safe_to_apply']}`",
        f"- Safe to apply now: `{summary['safe_to_apply_report_source_edits_now']}`",
        f"- Creates backup now: `{summary['creates_backup_now']}`",
        f"- Applies report source edits now: `{summary['applies_report_source_edits_now']}`",
        f"- Runs post-edit guards now: `{summary['runs_post_edit_guards_now']}`",
        "",
        "## Pre-Edit Checks",
        "",
        "| Check | Required | Current Status | Evidence |",
        "|---|---|---|---|",
    ]
    for item in checklist["pre_edit_checks"]:
        lines.append(
            f"| `{item['check_id']}` | `{item['required']}` | `{item['current_status']}` | {item['evidence']} |"
        )
    lines.extend(["", "## Post-Edit Guard Commands", ""])
    for command in checklist["post_edit_guard_commands"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Forbidden Now", ""])
    for item in checklist["forbidden_now"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Claim Boundary", ""])
    for item in checklist["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--application-plan", default=str(DEFAULT_APPLICATION_PLAN.relative_to(ROOT)))
    parser.add_argument("--reviewer-summary", default=str(DEFAULT_REVIEWER_SUMMARY.relative_to(ROOT)))
    parser.add_argument("--decision-check", default=str(DEFAULT_DECISION_CHECK.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    checklist = build_checklist(
        repo_path(args.application_plan),
        repo_path(args.reviewer_summary),
        repo_path(args.decision_check),
    )
    json_path = output_dir / "simulation_report_source_edit_application_audit_checklist.json"
    md_path = output_dir / "simulation_report_source_edit_application_audit_checklist.md"
    json_path.write_text(json.dumps(checklist, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(checklist, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "checklist_json": rel(json_path),
                "checklist_markdown": rel(md_path),
                "pre_edit_check_count": checklist["summary"]["pre_edit_check_count"],
                "post_edit_guard_command_count": checklist["summary"]["post_edit_guard_command_count"],
                "safe_to_apply_report_source_edits_now": checklist["summary"]["safe_to_apply_report_source_edits_now"],
                "applies_report_source_edits_now": checklist["summary"]["applies_report_source_edits_now"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
