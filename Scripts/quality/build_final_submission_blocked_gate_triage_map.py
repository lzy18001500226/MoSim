#!/usr/bin/env python3
"""Build a static triage map for blocked final-submission audit artifacts.

The map helps reviewers understand the current blocked static artifacts. It
does not execute generators, apply report-source edits, export final outputs,
or authorize acceptance.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INDEX = (
    ROOT
    / "Results/static_audits/final_submission_static_audit_index_20260610"
    / "final_submission_static_audit_index.json"
)
DEFAULT_DASHBOARD = (
    ROOT
    / "Results/static_audits/final_submission_readiness_dashboard_20260610"
    / "final_submission_readiness_dashboard.json"
)
DEFAULT_ACTION_MAP = (
    ROOT
    / "Results/static_audits/final_submission_reviewer_action_map_20260610"
    / "final_submission_reviewer_action_map.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_blocked_gate_triage_map_20260610"

ARTIFACT_TRIAGE = {
    "report_source_edit_decision": {
        "blocker_class": "human_report_source_decision",
        "next_human_action": "Review and update the report source edit decision artifact, or keep edits blocked.",
        "safe_rerun_commands": ["python Scripts/quality/check_report_source_edit_decision.py"],
    },
    "source_edit_readiness": {
        "blocker_class": "human_report_source_decision",
        "next_human_action": "Approve, reject, or narrow the report-source preview before source edits are allowed.",
        "safe_rerun_commands": [
            "python Scripts/quality/check_report_source_edit_decision.py",
            "python Scripts/quality/build_simulation_report_source_edit_readiness_gate.py",
        ],
    },
    "source_edit_application_plan": {
        "blocker_class": "human_report_source_decision",
        "next_human_action": "Regenerate the non-applying application plan only after the report-source decision changes.",
        "safe_rerun_commands": [
            "python Scripts/quality/build_simulation_report_source_edit_application_plan.py"
        ],
    },
    "source_edit_reviewer_summary": {
        "blocker_class": "review_aid_not_execution",
        "next_human_action": "Use the summary during A1 review; do not treat it as edit approval.",
        "safe_rerun_commands": [
            "python Scripts/quality/build_simulation_report_source_edit_reviewer_summary.py"
        ],
    },
    "source_edit_application_audit_checklist": {
        "blocker_class": "review_aid_not_execution",
        "next_human_action": "Use the checklist immediately before any future authorized report-source edit.",
        "safe_rerun_commands": [
            "python Scripts/quality/build_simulation_report_source_edit_application_audit_checklist.py"
        ],
    },
    "source_output_readiness": {
        "blocker_class": "source_output_not_ready",
        "next_human_action": "Resolve report-source approval/application and final-output prerequisites before export.",
        "safe_rerun_commands": ["python Scripts/quality/build_submission_source_output_readiness.py"],
    },
    "pdf_export_plan": {
        "blocker_class": "environment_or_export_authorization",
        "next_human_action": "Provide an approved PDF engine and keep export blocked until source-output gates allow it.",
        "safe_rerun_commands": ["python Scripts/quality/build_pdf_export_dry_run_plan.py"],
    },
    "demo_video_storyboard": {
        "blocker_class": "human_storyboard_review",
        "next_human_action": "Review storyboard scenes, wording, and evidence boundaries before recording.",
        "safe_rerun_commands": ["python Scripts/quality/build_demo_video_storyboard_plan.py"],
    },
    "final_artifact_manifest": {
        "blocker_class": "final_outputs_missing",
        "next_human_action": "Create reviewed final PDFs and demo video after approvals, then verify artifacts.",
        "safe_rerun_commands": [
            "python Scripts/quality/check_final_submission_artifact_manifest.py --allow-missing"
        ],
    },
    "final_acceptance_prereq": {
        "blocker_class": "acceptance_prerequisites_blocked",
        "next_human_action": "Complete source-output, PDF, video, and final artifact gates before acceptance.",
        "safe_rerun_commands": ["python Scripts/quality/build_final_acceptance_packet_prereq_plan.py"],
    },
    "final_output_execution_decision": {
        "blocker_class": "human_execution_authorization",
        "next_human_action": "Explicitly authorize or keep blocked PDF export, video production, and final acceptance writing.",
        "safe_rerun_commands": [
            "python Scripts/quality/build_final_output_execution_decision_template.py",
            "python Scripts/quality/check_final_output_execution_decision.py",
        ],
    },
    "final_submission_dashboard": {
        "blocker_class": "aggregate_static_gate_blocked",
        "next_human_action": "Regenerate the dashboard after upstream blocker sources change.",
        "safe_rerun_commands": ["python Scripts/quality/build_final_submission_readiness_dashboard.py"],
    },
    "final_submission_human_action_checklist": {
        "blocker_class": "review_aid_not_execution",
        "next_human_action": "Use the checklist to coordinate human actions; it does not approve execution.",
        "safe_rerun_commands": ["python Scripts/quality/build_final_submission_human_action_checklist.py"],
    },
    "final_submission_reviewer_action_map": {
        "blocker_class": "review_aid_not_execution",
        "next_human_action": "Use the reviewer action map to locate decisions and evidence; it does not make decisions.",
        "safe_rerun_commands": ["python Scripts/quality/build_final_submission_reviewer_action_map.py"],
    },
    "final_submission_human_review_decision_packet": {
        "blocker_class": "human_review_decision_pending",
        "next_human_action": "Review the A1/A3/A6 decision packet template and record explicit decisions if authorized.",
        "safe_rerun_commands": [
            "python Scripts/quality/build_final_submission_human_review_decision_packet_template.py"
        ],
    },
    "final_submission_human_review_guide": {
        "blocker_class": "review_aid_not_execution",
        "next_human_action": "Use the guide to perform A1/A3/A6 review; it does not change readiness.",
        "safe_rerun_commands": ["python Scripts/quality/build_final_submission_human_review_guide.py"],
    },
    "final_submission_readiness_chain": {
        "blocker_class": "aggregate_static_gate_blocked",
        "next_human_action": "Rerun the chain checker after dashboard/action-map/decision packet inputs change.",
        "safe_rerun_commands": ["python Scripts/quality/check_final_submission_readiness_chain.py"],
    },
}


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


def dashboard_blockers_by_gate(dashboard: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    by_gate: dict[str, list[dict[str, Any]]] = {}
    for blocker in dashboard.get("blockers", []):
        if not isinstance(blocker, dict):
            continue
        gate_id = str(blocker.get("gate_id", ""))
        by_gate.setdefault(gate_id, []).append(blocker)
    return by_gate


def action_records_by_id(action_map: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(action.get("action_id", "")): action
        for action in action_map.get("actions", [])
        if isinstance(action, dict)
    }


def linked_action_ids(artifact_id: str) -> list[str]:
    mapping = {
        "report_source_edit_decision": ["A1-approve-or-reject-report-source-edits"],
        "source_edit_readiness": ["A1-approve-or-reject-report-source-edits"],
        "source_edit_application_plan": ["A1-approve-or-reject-report-source-edits"],
        "source_edit_reviewer_summary": ["A1-approve-or-reject-report-source-edits"],
        "source_edit_application_audit_checklist": ["A1-approve-or-reject-report-source-edits"],
        "source_output_readiness": [
            "A1-approve-or-reject-report-source-edits",
            "A5-rerun-readiness-gates",
        ],
        "pdf_export_plan": ["A2-provide-pdf-engine", "A5-rerun-readiness-gates"],
        "demo_video_storyboard": ["A3-review-demo-storyboard"],
        "final_artifact_manifest": ["A4-create-reviewed-final-artifacts"],
        "final_acceptance_prereq": [
            "A4-create-reviewed-final-artifacts",
            "A5-rerun-readiness-gates",
        ],
        "final_output_execution_decision": ["A6-review-final-output-execution-decision"],
        "final_submission_dashboard": ["A5-rerun-readiness-gates"],
        "final_submission_human_action_checklist": ["A5-rerun-readiness-gates"],
        "final_submission_reviewer_action_map": ["A5-rerun-readiness-gates"],
        "final_submission_human_review_decision_packet": [
            "A6-review-final-output-execution-decision"
        ],
        "final_submission_human_review_guide": ["A6-review-final-output-execution-decision"],
        "final_submission_readiness_chain": ["A5-rerun-readiness-gates"],
    }
    return mapping.get(artifact_id, [])


def triage_record(
    artifact: dict[str, Any],
    dashboard_by_gate: dict[str, list[dict[str, Any]]],
    actions_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    artifact_id = str(artifact["artifact_id"])
    triage = ARTIFACT_TRIAGE.get(
        artifact_id,
        {
            "blocker_class": "unclassified_static_blocker",
            "next_human_action": "Review the blocked artifact and assign an owner.",
            "safe_rerun_commands": [],
        },
    )
    gate_ids = [artifact_id]
    if artifact_id == "final_artifact_manifest":
        gate_ids.append("final_artifact_manifest")
    dashboard_blockers = [
        blocker
        for gate_id in gate_ids
        for blocker in dashboard_by_gate.get(gate_id, [])
    ]
    action_ids = linked_action_ids(artifact_id)
    linked_actions = [
        {
            "action_id": action_id,
            "decision_owner": actions_by_id.get(action_id, {}).get("decision_owner", ""),
            "decision_needed": actions_by_id.get(action_id, {}).get("decision_needed", ""),
        }
        for action_id in action_ids
    ]
    return {
        "artifact_id": artifact_id,
        "path": artifact["path"],
        "status": artifact["status"],
        "ready": artifact["ready"],
        "role": artifact["role"],
        "blocker_class": triage["blocker_class"],
        "next_human_action": triage["next_human_action"],
        "safe_rerun_commands": triage["safe_rerun_commands"],
        "linked_human_actions": linked_actions,
        "dashboard_blockers": dashboard_blockers,
        "automated_execution_allowed": False,
        "generates_final_outputs": False,
        "final_acceptance": False,
    }


def build_map(index_path: Path, dashboard_path: Path, action_map_path: Path) -> dict[str, Any]:
    index = read_json(index_path)
    dashboard = read_json(dashboard_path)
    action_map = read_json(action_map_path)
    dashboard_by_gate = dashboard_blockers_by_gate(dashboard)
    actions_by_id = action_records_by_id(action_map)
    blocked_artifacts = [
        artifact
        for artifact in index.get("artifacts", [])
        if isinstance(artifact, dict) and artifact.get("ready") is not True
    ]
    records = [
        triage_record(artifact, dashboard_by_gate, actions_by_id)
        for artifact in blocked_artifacts
    ]
    blocker_classes = sorted({record["blocker_class"] for record in records})
    return {
        "map_id": "final_submission_blocked_gate_triage_map_20260610",
        "status": "blocked_gate_triage_map_not_execution",
        "source_index": rel(index_path),
        "source_dashboard": rel(dashboard_path),
        "source_action_map": rel(action_map_path),
        "summary": {
            "blocked_artifact_count": len(records),
            "blocker_class_count": len(blocker_classes),
            "dashboard_blocker_count": int(dashboard.get("summary", {}).get("blocker_count", 0)),
            "automated_execution_allowed": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "blocker_classes": blocker_classes,
        "blocked_artifacts": records,
        "claim_boundary": [
            "This triage map is a static review aid.",
            "It does not execute safe rerun commands.",
            "It does not apply report-source edits.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(triage_map: dict[str, Any], path: Path) -> None:
    summary = triage_map["summary"]
    lines = [
        "# Final Submission Blocked Gate Triage Map, 2026-06-10",
        "",
        f"Status: `{triage_map['status']}`",
        "",
        "## Summary",
        "",
        f"- Blocked artifacts: `{summary['blocked_artifact_count']}`",
        f"- Blocker classes: `{summary['blocker_class_count']}`",
        f"- Dashboard blockers: `{summary['dashboard_blocker_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Blocker Classes",
        "",
    ]
    for blocker_class in triage_map["blocker_classes"]:
        lines.append(f"- `{blocker_class}`")
    lines.extend(["", "## Blocked Artifacts", ""])
    for item in triage_map["blocked_artifacts"]:
        lines.extend(
            [
                f"### {item['artifact_id']}",
                "",
                f"- Status: `{item['status']}`",
                f"- Blocker class: `{item['blocker_class']}`",
                f"- Next human action: {item['next_human_action']}",
                "- Safe rerun commands:",
            ]
        )
        for command in item["safe_rerun_commands"]:
            lines.append(f"  - `{command}`")
        if not item["safe_rerun_commands"]:
            lines.append("  - none")
        lines.append("- Linked human actions:")
        for action in item["linked_human_actions"]:
            lines.append(
                f"  - `{action['action_id']}` owner=`{action['decision_owner']}`"
            )
        if not item["linked_human_actions"]:
            lines.append("  - none")
        lines.append("")
    lines.extend(["## Claim Boundary", ""])
    for item in triage_map["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", default=str(DEFAULT_INDEX.relative_to(ROOT)))
    parser.add_argument("--dashboard", default=str(DEFAULT_DASHBOARD.relative_to(ROOT)))
    parser.add_argument("--action-map", default=str(DEFAULT_ACTION_MAP.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    triage_map = build_map(
        repo_path(args.index),
        repo_path(args.dashboard),
        repo_path(args.action_map),
    )
    json_path = output_dir / "final_submission_blocked_gate_triage_map.json"
    md_path = output_dir / "final_submission_blocked_gate_triage_map.md"
    json_path.write_text(json.dumps(triage_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(triage_map, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "map_json": rel(json_path),
                "map_markdown": rel(md_path),
                "blocked_artifact_count": triage_map["summary"]["blocked_artifact_count"],
                "blocker_class_count": triage_map["summary"]["blocker_class_count"],
                "dashboard_blocker_count": triage_map["summary"]["dashboard_blocker_count"],
                "automated_execution_allowed": triage_map["summary"]["automated_execution_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
