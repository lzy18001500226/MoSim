#!/usr/bin/env python3
"""Build a prioritized human-action checklist from final submission blockers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DASHBOARD = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_readiness_dashboard_20260610"
    / "final_submission_readiness_dashboard.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_human_action_checklist_20260610"

ACTION_RULES = [
    {
        "match": "report_source_edit_not_approved",
        "action_id": "A1-approve-or-reject-report-source-edits",
        "priority": 1,
        "owner": "user_or_PMO",
        "action": "Review the simulation-report source edit preview/readiness gate and approve, reject, or narrow final report-source edits.",
        "success_evidence": "A reviewed decision is recorded and the source edit readiness gate can be regenerated with the decision reflected.",
    },
    {
        "match": "report_source_edit_application_plan_not_ready",
        "action_id": "A1-approve-or-reject-report-source-edits",
        "priority": 1,
        "owner": "user_or_PMO",
        "action": "Review the simulation-report source edit preview/readiness gate and approve, reject, or narrow final report-source edits.",
        "success_evidence": "A reviewed decision is recorded and the source edit readiness gate can be regenerated with the decision reflected.",
    },
    {
        "match": "report_source_edit_application_not_applied",
        "action_id": "A1-approve-or-reject-report-source-edits",
        "priority": 1,
        "owner": "user_or_PMO",
        "action": "Review the simulation-report source edit preview/readiness gate and approve, reject, or narrow final report-source edits.",
        "success_evidence": "A reviewed decision is recorded and the source edit readiness gate can be regenerated with the decision reflected.",
    },
    {
        "match": "pdf_engine_missing",
        "action_id": "A2-provide-pdf-engine",
        "priority": 2,
        "owner": "local_environment_owner",
        "action": "Install or expose a Pandoc-compatible PDF engine such as xelatex, lualatex, tectonic, pdflatex, wkhtmltopdf, or weasyprint.",
        "success_evidence": "The PDF export dry-run plan reports pdf_engine_available=true.",
    },
    {
        "match": "demo_video_recording_not_approved",
        "action_id": "A3-review-demo-storyboard",
        "priority": 3,
        "owner": "user_or_PMO",
        "action": "Review the demo-video storyboard, wording, evidence mapping, and forbidden claims before any recording.",
        "success_evidence": "Storyboard review decision is recorded and safe_to_record_demo_video_now can become true in a follow-up gate.",
    },
    {
        "match": "manual_storyboard_review_required",
        "action_id": "A3-review-demo-storyboard",
        "priority": 3,
        "owner": "user_or_PMO",
        "action": "Review the demo-video storyboard, wording, evidence mapping, and forbidden claims before any recording.",
        "success_evidence": "Storyboard review decision is recorded and safe_to_record_demo_video_now can become true in a follow-up gate.",
    },
    {
        "match": "final_outputs_missing",
        "action_id": "A4-create-reviewed-final-artifacts",
        "priority": 4,
        "owner": "packaging_or_manual_operator",
        "action": "After approvals, create reviewed final PDFs and demo_video.mp4, then rerun the final artifact manifest without --allow-missing.",
        "success_evidence": "Final artifact manifest reports final_submission_artifacts_ready=true.",
    },
    {
        "match": "final_artifacts_missing",
        "action_id": "A4-create-reviewed-final-artifacts",
        "priority": 4,
        "owner": "packaging_or_manual_operator",
        "action": "After approvals, create reviewed final PDFs and demo_video.mp4, then rerun the final artifact manifest without --allow-missing.",
        "success_evidence": "Final artifact manifest reports final_submission_artifacts_ready=true.",
    },
    {
        "match": "final_artifacts_not_ready",
        "action_id": "A4-create-reviewed-final-artifacts",
        "priority": 4,
        "owner": "packaging_or_manual_operator",
        "action": "After approvals, create reviewed final PDFs and demo_video.mp4, then rerun the final artifact manifest without --allow-missing.",
        "success_evidence": "Final artifact manifest reports final_submission_artifacts_ready=true.",
    },
    {
        "match": "demo_video_not_recorded",
        "action_id": "A4-create-reviewed-final-artifacts",
        "priority": 4,
        "owner": "packaging_or_manual_operator",
        "action": "After approvals, create reviewed final PDFs and demo_video.mp4, then rerun the final artifact manifest without --allow-missing.",
        "success_evidence": "Final artifact manifest reports final_submission_artifacts_ready=true.",
    },
    {
        "match": "pdf_export_not_ready",
        "action_id": "A5-rerun-readiness-gates",
        "priority": 5,
        "owner": "operator",
        "action": "Rerun PDF, video, artifact, source-output, acceptance-prereq, and dashboard gates after A1-A4 are complete.",
        "success_evidence": "Dashboard blocking_gate_count decreases and final_submission_ready reflects current artifacts.",
    },
    {
        "match": "source_output_readiness_blocks_acceptance",
        "action_id": "A5-rerun-readiness-gates",
        "priority": 5,
        "owner": "operator",
        "action": "Rerun PDF, video, artifact, source-output, acceptance-prereq, and dashboard gates after A1-A4 are complete.",
        "success_evidence": "Dashboard blocking_gate_count decreases and final_submission_ready reflects current artifacts.",
    },
    {
        "match": "authorizes_pdf_export",
        "action_id": "A6-review-final-output-execution-decision",
        "priority": 6,
        "owner": "user_or_PMO",
        "action": "Review and approve or keep pending the final-output execution decision for PDF export, demo video, and final acceptance packet writing.",
        "success_evidence": "The final output execution decision checker reports the relevant authorizes_* fields as true after upstream gates pass.",
    },
    {
        "match": "authorizes_demo_video_recording",
        "action_id": "A6-review-final-output-execution-decision",
        "priority": 6,
        "owner": "user_or_PMO",
        "action": "Review and approve or keep pending the final-output execution decision for PDF export, demo video, and final acceptance packet writing.",
        "success_evidence": "The final output execution decision checker reports the relevant authorizes_* fields as true after upstream gates pass.",
    },
    {
        "match": "authorizes_final_acceptance_packet",
        "action_id": "A6-review-final-output-execution-decision",
        "priority": 6,
        "owner": "user_or_PMO",
        "action": "Review and approve or keep pending the final-output execution decision for PDF export, demo video, and final acceptance packet writing.",
        "success_evidence": "The final output execution decision checker reports the relevant authorizes_* fields as true after upstream gates pass.",
    },
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


def action_for_blocker(blocker: dict[str, Any]) -> dict[str, Any]:
    blocker_id = str(blocker.get("blocker_id", ""))
    for rule in ACTION_RULES:
        if rule["match"] == blocker_id:
            return {
                "action_id": rule["action_id"],
                "priority": rule["priority"],
                "owner": rule["owner"],
                "action": rule["action"],
                "success_evidence": rule["success_evidence"],
                "source_blockers": [blocker],
            }
    return {
        "action_id": f"A9-review-unclassified-{blocker_id or 'blocker'}",
        "priority": 9,
        "owner": "user_or_PMO",
        "action": "Review unclassified final-submission blocker and decide the next action.",
        "success_evidence": "A specific owner/action is recorded and the dashboard is regenerated.",
        "source_blockers": [blocker],
    }


def merge_actions(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for action in actions:
        key = str(action["action_id"])
        if key not in merged:
            merged[key] = action
        else:
            merged[key]["source_blockers"].extend(action["source_blockers"])
    return sorted(merged.values(), key=lambda item: (int(item["priority"]), str(item["action_id"])))


def build_checklist(dashboard_path: Path) -> dict[str, Any]:
    dashboard = read_json(dashboard_path)
    blockers = [item for item in dashboard.get("blockers", []) if isinstance(item, dict)]
    actions = merge_actions([action_for_blocker(blocker) for blocker in blockers])
    return {
        "checklist_id": "final_submission_human_action_checklist_20260610",
        "status": "human_action_checklist_not_execution",
        "source_dashboard": rel(dashboard_path),
        "summary": {
            "source_blocker_count": len(blockers),
            "action_count": len(actions),
            "automated_execution_allowed": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "actions": actions,
        "claim_boundary": [
            "This checklist is a human-action planning artifact.",
            "It does not install tools.",
            "It does not approve report-source edits.",
            "It does not export PDFs or record video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(checklist: dict[str, Any], path: Path) -> None:
    summary = checklist["summary"]
    lines = [
        "# Final Submission Human Action Checklist, 2026-06-10",
        "",
        f"Status: `{checklist['status']}`",
        "",
        "## Summary",
        "",
        f"- Source blockers: `{summary['source_blocker_count']}`",
        f"- Actions: `{summary['action_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Claim Boundary",
        "",
    ]
    for item in checklist["claim_boundary"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Actions", ""])
    for action in checklist["actions"]:
        lines.extend(
            [
                f"### {action['action_id']}",
                "",
                f"- Priority: `{action['priority']}`",
                f"- Owner: `{action['owner']}`",
                f"- Action: {action['action']}",
                f"- Success evidence: {action['success_evidence']}",
                "- Source blockers:",
            ]
        )
        for blocker in action["source_blockers"]:
            lines.append(
                f"  - `{blocker.get('gate_id', '')}/{blocker.get('blocker_id', '')}`: {blocker.get('reason', '')}"
            )
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dashboard", default=str(DEFAULT_DASHBOARD.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    checklist = build_checklist(repo_path(args.dashboard))
    json_path = output_dir / "final_submission_human_action_checklist.json"
    md_path = output_dir / "final_submission_human_action_checklist.md"
    json_path.write_text(json.dumps(checklist, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(checklist, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "checklist_json": rel(json_path),
                "checklist_markdown": rel(md_path),
                "action_count": checklist["summary"]["action_count"],
                "automated_execution_allowed": checklist["summary"]["automated_execution_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
