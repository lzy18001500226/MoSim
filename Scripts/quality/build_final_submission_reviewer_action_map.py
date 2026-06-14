#!/usr/bin/env python3
"""Build a reviewer-facing map for final-submission human actions.

The map expands the human-action checklist into owner, decision, evidence, and
rerun-command fields. It is a static review aid only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CHECKLIST = (
    ROOT
    / "Results/static_audits/final_submission_human_action_checklist_20260610"
    / "final_submission_human_action_checklist.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_reviewer_action_map_20260610"

ACTION_DETAILS = {
    "A1-approve-or-reject-report-source-edits": {
        "decision_owner": "user_or_PMO",
        "decision_needed": "approve, reject, keep pending, or narrow the report-source edit preview scope",
        "review_artifacts": [
            "Results/static_audits/simulation_report_patch_preview_20260610/simulation_report_patch_preview.md",
            "Results/static_audits/simulation_report_source_edit_readiness_20260610/simulation_report_source_edit_readiness_gate.md",
            "Results/static_audits/simulation_report_source_edit_application_plan_20260610/simulation_report_source_edit_application_plan.md",
            "Results/static_audits/report_source_edit_decision_template_20260610/report_source_edit_decision.template.json",
            "Results/static_audits/report_source_edit_decision_template_20260610/report_source_edit_decision_check.json",
        ],
        "decision_artifact": "Results/static_audits/report_source_edit_decision_template_20260610/report_source_edit_decision.template.json",
        "rerun_after_decision": [
            "python Scripts/quality/check_report_source_edit_decision.py",
            "python Scripts/quality/build_simulation_report_source_edit_readiness_gate.py",
            "python Scripts/quality/build_simulation_report_source_edit_application_plan.py",
            "python Scripts/quality/build_submission_source_output_readiness.py",
        ],
    },
    "A2-provide-pdf-engine": {
        "decision_owner": "local_environment_owner",
        "decision_needed": "install or expose an approved Pandoc PDF engine, or keep final PDF export blocked",
        "review_artifacts": [
            "Results/static_audits/pdf_export_dry_run_plan_20260610/pdf_export_dry_run_plan.md",
            "Results/static_audits/submission_source_output_readiness_20260610/submission_source_output_readiness.md",
        ],
        "decision_artifact": "",
        "rerun_after_decision": [
            "python Scripts/quality/build_pdf_export_dry_run_plan.py",
            "python Scripts/quality/build_final_submission_readiness_dashboard.py",
        ],
    },
    "A3-review-demo-storyboard": {
        "decision_owner": "user_or_PMO",
        "decision_needed": "approve, reject, or revise storyboard scenes, wording, and evidence boundaries",
        "review_artifacts": [
            "Results/static_audits/demo_video_storyboard_plan_20260610/demo_video_storyboard_plan.md",
            "Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision.template.json",
        ],
        "decision_artifact": "Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision.template.json",
        "rerun_after_decision": [
            "python Scripts/quality/build_demo_video_storyboard_plan.py",
            "python Scripts/quality/check_final_output_execution_decision.py",
            "python Scripts/quality/build_final_submission_readiness_dashboard.py",
        ],
    },
    "A4-create-reviewed-final-artifacts": {
        "decision_owner": "packaging_or_manual_operator",
        "decision_needed": "after approvals, create reviewed final PDFs and demo_video.mp4, then verify artifact presence",
        "review_artifacts": [
            "Results/static_audits/final_submission_artifacts_20260610/final_submission_artifact_manifest_check.md",
            "Results/static_audits/pdf_export_dry_run_plan_20260610/pdf_export_dry_run_plan.md",
            "Results/static_audits/demo_video_storyboard_plan_20260610/demo_video_storyboard_plan.md",
        ],
        "decision_artifact": "",
        "rerun_after_decision": [
            "python Scripts/quality/check_final_submission_artifact_manifest.py",
            "python Scripts/quality/build_final_acceptance_packet_prereq_plan.py",
            "python Scripts/quality/build_final_submission_readiness_dashboard.py",
        ],
    },
    "A5-rerun-readiness-gates": {
        "decision_owner": "operator",
        "decision_needed": "rerun readiness gates only after A1-A4 decisions or artifacts change",
        "review_artifacts": [
            "Results/static_audits/final_submission_readiness_dashboard_20260610/final_submission_readiness_dashboard.md",
            "Results/static_audits/final_submission_readiness_chain_20260610/final_submission_readiness_chain_check.md",
            "Results/static_audits/final_submission_refresh_order_20260610/final_submission_refresh_order_check.md",
        ],
        "decision_artifact": "",
        "rerun_after_decision": [
            "python Scripts/quality/build_submission_source_output_readiness.py",
            "python Scripts/quality/build_pdf_export_dry_run_plan.py",
            "python Scripts/quality/build_final_acceptance_packet_prereq_plan.py",
            "python Scripts/quality/build_final_submission_readiness_dashboard.py",
            "python Scripts/quality/build_final_submission_human_action_checklist.py",
            "python Scripts/quality/check_final_submission_readiness_chain.py",
            "python Scripts/quality/check_final_submission_refresh_order.py",
        ],
    },
    "A6-review-final-output-execution-decision": {
        "decision_owner": "user_or_PMO",
        "decision_needed": "explicitly authorize or keep blocked PDF export, demo video recording, and final acceptance packet writing",
        "review_artifacts": [
            "Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision_template.md",
            "Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision.template.json",
            "Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision_check.json",
        ],
        "decision_artifact": "Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision.template.json",
        "rerun_after_decision": [
            "python Scripts/quality/check_final_output_execution_decision.py",
            "python Scripts/quality/build_final_submission_readiness_dashboard.py",
            "python Scripts/quality/build_final_submission_human_action_checklist.py",
        ],
    },
}

HUMAN_REVIEW_DECISION_PACKET = (
    "Results/static_audits/final_submission_human_review_decision_packet_20260610/"
    "final_submission_human_review_decision_packet.template.json"
)


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


def artifact_status(path_value: str) -> dict[str, Any]:
    if not path_value:
        return {"path": "", "exists": False, "required": False}
    path = repo_path(path_value)
    return {"path": path_value, "exists": path.exists(), "required": True}


def build_action_record(action: dict[str, Any]) -> dict[str, Any]:
    action_id = str(action.get("action_id", ""))
    detail = ACTION_DETAILS.get(action_id, {})
    review_artifacts = [artifact_status(path) for path in detail.get("review_artifacts", [])]
    missing = [item["path"] for item in review_artifacts if item["required"] and not item["exists"]]
    return {
        "action_id": action_id,
        "priority": action.get("priority"),
        "checklist_owner": action.get("owner", ""),
        "decision_owner": detail.get("decision_owner", action.get("owner", "")),
        "decision_needed": detail.get("decision_needed", "review and decide the next action"),
        "decision_artifact": detail.get("decision_artifact", ""),
        "source_blocker_count": len(action.get("source_blockers", [])),
        "review_artifacts": review_artifacts,
        "missing_review_artifacts": missing,
        "rerun_after_decision": detail.get("rerun_after_decision", []),
        "automated_execution_allowed": False,
        "generates_final_outputs": False,
        "final_acceptance": False,
    }


def build_map(checklist_path: Path) -> dict[str, Any]:
    checklist = read_json(checklist_path)
    actions = [item for item in checklist.get("actions", []) if isinstance(item, dict)]
    records = [build_action_record(action) for action in actions]
    missing = sorted({path for record in records for path in record["missing_review_artifacts"]})
    return {
        "map_id": "final_submission_reviewer_action_map_20260610",
        "status": "reviewer_action_map_not_execution",
        "source_checklist": rel(checklist_path),
        "summary": {
            "action_count": len(records),
            "missing_review_artifact_count": len(missing),
            "automated_execution_allowed": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "actions": records,
        "human_review_decision_packet_template": HUMAN_REVIEW_DECISION_PACKET,
        "missing_review_artifacts": missing,
        "claim_boundary": [
            "This map is a reviewer-facing static aid.",
            "It does not approve decisions.",
            "It does not install tools.",
            "It does not apply report-source edits.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(action_map: dict[str, Any], path: Path) -> None:
    summary = action_map["summary"]
    lines = [
        "# Final Submission Reviewer Action Map, 2026-06-10",
        "",
        f"Status: `{action_map['status']}`",
        "",
        "## Summary",
        "",
        f"- Actions: `{summary['action_count']}`",
        f"- Missing review artifacts: `{summary['missing_review_artifact_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Actions",
        "",
    ]
    for item in action_map["actions"]:
        lines.extend(
            [
                f"### {item['action_id']}",
                "",
                f"- Decision owner: `{item['decision_owner']}`",
                f"- Decision needed: {item['decision_needed']}",
                f"- Decision artifact: `{item['decision_artifact'] or 'none'}`",
                f"- Source blockers: `{item['source_blocker_count']}`",
                "- Review artifacts:",
            ]
        )
        for artifact in item["review_artifacts"]:
            lines.append(f"  - `{artifact['path']}` exists=`{artifact['exists']}`")
        lines.append("- Rerun after decision:")
        for command in item["rerun_after_decision"]:
            lines.append(f"  - `{command}`")
        lines.append("")
    lines.extend(["## Claim Boundary", ""])
    for item in action_map["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checklist", default=str(DEFAULT_CHECKLIST.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    action_map = build_map(repo_path(args.checklist))
    json_path = output_dir / "final_submission_reviewer_action_map.json"
    md_path = output_dir / "final_submission_reviewer_action_map.md"
    json_path.write_text(json.dumps(action_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(action_map, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "map_json": rel(json_path),
                "map_markdown": rel(md_path),
                "action_count": action_map["summary"]["action_count"],
                "missing_review_artifact_count": action_map["summary"]["missing_review_artifact_count"],
                "automated_execution_allowed": action_map["summary"]["automated_execution_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
