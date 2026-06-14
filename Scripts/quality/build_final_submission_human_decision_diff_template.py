#!/usr/bin/env python3
"""Build a non-applying human-decision diff template for final submission.

The template lists which pending fields need human/PMO decisions before future
report-source edits or final-output work can be authorized. It does not modify
the decision templates.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_DECISION = (
    ROOT
    / "Results/static_audits/report_source_edit_decision_template_20260610"
    / "report_source_edit_decision.template.json"
)
DEFAULT_EXECUTION_DECISION = (
    ROOT
    / "Results/static_audits/final_output_execution_decision_20260610"
    / "final_output_execution_decision.template.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_human_decision_diff_template_20260610"


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


def report_source_field_changes(template: dict[str, Any]) -> list[dict[str, Any]]:
    available_preview_ids = template.get("available_preview_ids", [])
    return [
        {
            "field_path": "decision",
            "current_value": template.get("decision"),
            "allowed_values": template.get("valid_decisions", []),
            "human_choice_required": True,
            "notes": "Keep pending_review, or choose approved/rejected/narrowed after reviewing preview snippets.",
        },
        {
            "field_path": "decision_owner",
            "current_value": template.get("decision_owner"),
            "allowed_values": ["<non-placeholder user_or_PMO identity>"],
            "human_choice_required": True,
            "notes": "Required for approved or narrowed decisions.",
        },
        {
            "field_path": "decided_at",
            "current_value": template.get("decided_at"),
            "allowed_values": ["<ISO8601_after_review>"],
            "human_choice_required": True,
            "notes": "Required for approved or narrowed decisions.",
        },
        {
            "field_path": "approved_preview_ids",
            "current_value": template.get("approved_preview_ids", []),
            "allowed_values": available_preview_ids,
            "human_choice_required": True,
            "notes": "Must name approved preview ids when decision is approved or narrowed.",
        },
        {
            "field_path": "rejected_preview_ids",
            "current_value": template.get("rejected_preview_ids", []),
            "allowed_values": available_preview_ids,
            "human_choice_required": False,
            "notes": "May record rejected preview ids for rejected or narrowed decisions.",
        },
        {
            "field_path": "narrowed_scope_notes",
            "current_value": template.get("narrowed_scope_notes", ""),
            "allowed_values": ["<freeform reviewed scope note>"],
            "human_choice_required": False,
            "notes": "Required in practice when decision is narrowed.",
        },
        {
            "field_path": "review_notes",
            "current_value": template.get("review_notes", ""),
            "allowed_values": ["<freeform review note>"],
            "human_choice_required": False,
            "notes": "Recommended for approved or narrowed decisions.",
        },
        {
            "field_path": "safe_to_apply_report_source_edits",
            "current_value": template.get("safe_to_apply_report_source_edits"),
            "allowed_values": [False, True],
            "human_choice_required": True,
            "notes": "May become true only when decision is approved or narrowed and approved_preview_ids is non-empty.",
        },
    ]


def execution_field_changes(template: dict[str, Any]) -> list[dict[str, Any]]:
    actions = template.get("actions", {})
    records: list[dict[str, Any]] = []
    for action_id in ["pdf_export", "demo_video_recording", "final_acceptance_packet"]:
        action = actions.get(action_id, {}) if isinstance(actions, dict) else {}
        records.extend(
            [
                {
                    "field_path": f"actions.{action_id}.decision",
                    "current_value": action.get("decision"),
                    "allowed_values": ["pending_review", "approved", "rejected"],
                    "human_choice_required": True,
                    "notes": "Approval still requires the upstream readiness gate to be true.",
                },
                {
                    "field_path": f"actions.{action_id}.approved",
                    "current_value": action.get("approved"),
                    "allowed_values": [False, True],
                    "human_choice_required": True,
                    "notes": "Must match decision==approved; true is invalid while upstream gate is false.",
                },
                {
                    "field_path": f"actions.{action_id}.approved_by",
                    "current_value": action.get("approved_by"),
                    "allowed_values": ["<non-placeholder user_or_PMO identity>"],
                    "human_choice_required": True,
                    "notes": "Required when this action is approved.",
                },
                {
                    "field_path": f"actions.{action_id}.approved_at",
                    "current_value": action.get("approved_at"),
                    "allowed_values": ["<ISO8601_after_review>"],
                    "human_choice_required": True,
                    "notes": "Required when this action is approved.",
                },
                {
                    "field_path": f"actions.{action_id}.review_notes",
                    "current_value": action.get("review_notes", ""),
                    "allowed_values": ["<freeform review note>"],
                    "human_choice_required": False,
                    "notes": "Recommended when this action is approved.",
                },
            ]
        )
    return records


def build_template(report_decision_path: Path, execution_decision_path: Path) -> dict[str, Any]:
    report_decision = read_json(report_decision_path)
    execution_decision = read_json(execution_decision_path)
    report_changes = report_source_field_changes(report_decision)
    execution_changes = execution_field_changes(execution_decision)
    return {
        "template_id": "final_submission_human_decision_diff_template_20260610",
        "status": "human_decision_diff_template_not_execution",
        "source_templates": {
            "report_source_edit_decision": rel(report_decision_path),
            "final_output_execution_decision": rel(execution_decision_path),
        },
        "summary": {
            "report_source_field_count": len(report_changes),
            "final_output_action_count": 3,
            "final_output_field_count": len(execution_changes),
            "applies_decisions_now": False,
            "edits_decision_templates_now": False,
            "automated_execution_allowed": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "decision_groups": [
            {
                "decision_group_id": "A1-report-source-edit-decision",
                "owner": "user_or_PMO",
                "source_template": rel(report_decision_path),
                "required_checker_after_edit": "python Scripts/quality/check_report_source_edit_decision.py",
                "field_changes": report_changes,
            },
            {
                "decision_group_id": "A6-final-output-execution-decision",
                "owner": "user_or_PMO",
                "source_template": rel(execution_decision_path),
                "required_checker_after_edit": "python Scripts/quality/check_final_output_execution_decision.py",
                "field_changes": execution_changes,
            },
        ],
        "claim_boundary": [
            "This is a non-applying diff template for human review.",
            "It does not edit report_source_edit_decision.template.json.",
            "It does not edit final_output_execution_decision.template.json.",
            "It does not approve pending decisions.",
            "It does not apply report-source edits.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(template: dict[str, Any], path: Path) -> None:
    summary = template["summary"]
    lines = [
        "# Final Submission Human Decision Diff Template, 2026-06-10",
        "",
        f"Status: `{template['status']}`",
        "",
        "## Summary",
        "",
        f"- Report-source fields: `{summary['report_source_field_count']}`",
        f"- Final-output actions: `{summary['final_output_action_count']}`",
        f"- Final-output fields: `{summary['final_output_field_count']}`",
        f"- Applies decisions now: `{summary['applies_decisions_now']}`",
        f"- Edits decision templates now: `{summary['edits_decision_templates_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Decision Groups",
        "",
    ]
    for group in template["decision_groups"]:
        lines.extend(
            [
                f"### {group['decision_group_id']}",
                "",
                f"- Owner: `{group['owner']}`",
                f"- Source template: `{group['source_template']}`",
                f"- Required checker after edit: `{group['required_checker_after_edit']}`",
                "",
                "| Field | Current | Allowed | Notes |",
                "|---|---|---|---|",
            ]
        )
        for field in group["field_changes"]:
            current = json.dumps(field["current_value"], ensure_ascii=False)
            allowed = json.dumps(field["allowed_values"], ensure_ascii=False)
            lines.append(f"| `{field['field_path']}` | `{current}` | `{allowed}` | {field['notes']} |")
        lines.append("")
    lines.extend(["## Claim Boundary", ""])
    for item in template["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-decision", default=str(DEFAULT_REPORT_DECISION.relative_to(ROOT)))
    parser.add_argument("--execution-decision", default=str(DEFAULT_EXECUTION_DECISION.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    template = build_template(repo_path(args.report_decision), repo_path(args.execution_decision))
    json_path = output_dir / "final_submission_human_decision_diff_template.json"
    md_path = output_dir / "final_submission_human_decision_diff_template.md"
    json_path.write_text(json.dumps(template, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(template, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "template_json": rel(json_path),
                "template_markdown": rel(md_path),
                "report_source_field_count": template["summary"]["report_source_field_count"],
                "final_output_action_count": template["summary"]["final_output_action_count"],
                "final_output_field_count": template["summary"]["final_output_field_count"],
                "applies_decisions_now": template["summary"]["applies_decisions_now"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
