#!/usr/bin/env python3
"""Build a non-applying manual-review answer sheet template."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_QUICKSTART = (
    ROOT
    / "Results/static_audits/final_submission_reviewer_quickstart_20260610"
    / "final_submission_reviewer_quickstart.json"
)
DEFAULT_DIFF_TEMPLATE = (
    ROOT
    / "Results/static_audits/final_submission_human_decision_diff_template_20260610"
    / "final_submission_human_decision_diff_template.json"
)
DEFAULT_RERUN_MATRIX = (
    ROOT
    / "Results/static_audits/final_submission_post_review_rerun_matrix_20260610"
    / "final_submission_post_review_rerun_matrix.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_manual_review_answer_sheet_20260610"


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


def groups_by_id(diff_template: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(group.get("decision_group_id", "")): group
        for group in diff_template.get("decision_groups", [])
        if isinstance(group, dict)
    }


def rerun_rows_by_action(rerun_matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("action_id", "")): row
        for row in rerun_matrix.get("rows", [])
        if isinstance(row, dict)
    }


def field_answers(section: dict[str, Any], diff_group: dict[str, Any]) -> list[dict[str, Any]]:
    answers: list[dict[str, Any]] = []
    for field in diff_group.get("field_changes", []):
        if not isinstance(field, dict):
            continue
        answers.append(
            {
                "field_path": field.get("field_path", ""),
                "current_value": field.get("current_value"),
                "allowed_values": field.get("allowed_values", []),
                "human_choice_required": field.get("human_choice_required", False),
                "proposed_value": "<fill_after_review>",
                "review_note": "",
                "copy_to_decision_artifact": section.get("decision_artifact", ""),
            }
        )
    return answers


def answer_section(
    section: dict[str, Any],
    diff_groups: dict[str, dict[str, Any]],
    rerun_rows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    action_id = str(section.get("action_id", ""))
    diff_group_id = str(section.get("decision_diff_group", ""))
    diff_group = diff_groups.get(diff_group_id, {})
    rerun_row = rerun_rows.get(action_id, {})
    return {
        "action_id": action_id,
        "decision_owner": section.get("decision_owner", "user_or_PMO"),
        "current_decision": section.get("current_decision", "pending_review"),
        "decision_needed": section.get("decision_needed", ""),
        "decision_artifact": section.get("decision_artifact", ""),
        "decision_diff_group": diff_group_id,
        "review_questions": section.get("review_questions", []),
        "minimum_open_files": section.get("minimum_open_files", []),
        "answer_fields": field_answers(section, diff_group),
        "post_review_rerun_readiness": rerun_row.get("rerun_readiness", ""),
        "post_review_rerun_commands": rerun_row.get("rerun_commands_after_separate_review_edit", []),
        "execution_still_requires": rerun_row.get("execution_still_requires", []),
        "human_review_answer": {
            "decision": "<pending_review|approved|rejected|narrowed|needs_revision>",
            "approved": False,
            "reviewed_by": "<user_or_PMO>",
            "reviewed_at": "<ISO8601_after_review>",
            "approved_scope": [],
            "rejected_scope": [],
            "narrowed_scope_notes": "",
            "review_notes": "",
        },
        "copies_answers_now": False,
        "edits_decision_artifact_now": False,
        "approves_or_executes_now": False,
    }


def build_answer_sheet(
    quickstart_path: Path,
    diff_template_path: Path,
    rerun_matrix_path: Path,
) -> dict[str, Any]:
    quickstart = read_json(quickstart_path)
    diff_template = read_json(diff_template_path)
    rerun_matrix = read_json(rerun_matrix_path)
    diff_groups = groups_by_id(diff_template)
    rerun_rows = rerun_rows_by_action(rerun_matrix)
    sections = [
        answer_section(section, diff_groups, rerun_rows)
        for section in quickstart.get("sections", [])
        if isinstance(section, dict)
    ]
    field_count = sum(len(section["answer_fields"]) for section in sections)
    required_field_count = sum(
        1
        for section in sections
        for field in section["answer_fields"]
        if field["human_choice_required"] is True
    )
    missing_open_file_count = sum(
        1
        for section in sections
        for item in section["minimum_open_files"]
        if isinstance(item, dict) and item.get("exists") is not True
    )
    return {
        "answer_sheet_id": "final_submission_manual_review_answer_sheet_20260610",
        "status": "manual_review_answer_sheet_template_not_execution",
        "sources": {
            "reviewer_quickstart": rel(quickstart_path),
            "human_decision_diff_template": rel(diff_template_path),
            "post_review_rerun_matrix": rel(rerun_matrix_path),
        },
        "summary": {
            "review_action_count": len(sections),
            "answer_field_count": field_count,
            "required_answer_field_count": required_field_count,
            "missing_open_file_count": missing_open_file_count,
            "automated_execution_allowed": False,
            "copies_answers_now": False,
            "edits_decision_artifacts_now": False,
            "approves_or_executes_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "sections": sections,
        "claim_boundary": [
            "This answer sheet is a template for future human review.",
            "It does not fill answers for the user.",
            "It does not copy answers into decision artifacts.",
            "It does not edit decision templates.",
            "It does not approve decisions.",
            "It does not run post-review checkers.",
            "It does not apply report-source edits.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(sheet: dict[str, Any], path: Path) -> None:
    summary = sheet["summary"]
    lines = [
        "# Final Submission Manual Review Answer Sheet Template, 2026-06-10",
        "",
        f"Status: `{sheet['status']}`",
        "",
        "## Summary",
        "",
        f"- Review actions: `{summary['review_action_count']}`",
        f"- Answer fields: `{summary['answer_field_count']}`",
        f"- Required answer fields: `{summary['required_answer_field_count']}`",
        f"- Missing open files: `{summary['missing_open_file_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Copies answers now: `{summary['copies_answers_now']}`",
        f"- Edits decision artifacts now: `{summary['edits_decision_artifacts_now']}`",
        f"- Approves or executes now: `{summary['approves_or_executes_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Answer Sections",
        "",
    ]
    for section in sheet["sections"]:
        lines.extend(
            [
                f"### {section['action_id']}",
                "",
                f"- Decision owner: `{section['decision_owner']}`",
                f"- Current decision: `{section['current_decision']}`",
                f"- Decision needed: {section['decision_needed']}",
                f"- Decision artifact: `{section['decision_artifact']}`",
                f"- Decision diff group: `{section['decision_diff_group']}`",
                f"- Post-review rerun readiness: `{section['post_review_rerun_readiness']}`",
                "- Review questions:",
            ]
        )
        for question in section["review_questions"]:
            lines.append(f"  - {question}")
        lines.append("- Answer fields:")
        for field in section["answer_fields"]:
            required = field["human_choice_required"]
            lines.append(f"  - `{field['field_path']}` required=`{required}` proposed=`{field['proposed_value']}`")
        lines.append("- Post-review rerun commands:")
        for command in section["post_review_rerun_commands"]:
            lines.append(f"  - `{command}`")
        lines.append("")
    lines.extend(["## Claim Boundary", ""])
    for item in sheet["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer-quickstart", default=str(DEFAULT_QUICKSTART.relative_to(ROOT)))
    parser.add_argument("--decision-diff-template", default=str(DEFAULT_DIFF_TEMPLATE.relative_to(ROOT)))
    parser.add_argument("--rerun-matrix", default=str(DEFAULT_RERUN_MATRIX.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    sheet = build_answer_sheet(
        repo_path(args.reviewer_quickstart),
        repo_path(args.decision_diff_template),
        repo_path(args.rerun_matrix),
    )
    json_path = output_dir / "final_submission_manual_review_answer_sheet_template.json"
    md_path = output_dir / "final_submission_manual_review_answer_sheet_template.md"
    sheet_path = output_dir / "final_submission_manual_review_answer_sheet.template.json"
    json_path.write_text(json.dumps(sheet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sheet_path.write_text(json.dumps(sheet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(sheet, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "answer_sheet_json": rel(json_path),
                "answer_sheet_markdown": rel(md_path),
                "answer_sheet_template": rel(sheet_path),
                "review_action_count": sheet["summary"]["review_action_count"],
                "answer_field_count": sheet["summary"]["answer_field_count"],
                "required_answer_field_count": sheet["summary"]["required_answer_field_count"],
                "automated_execution_allowed": sheet["summary"]["automated_execution_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
