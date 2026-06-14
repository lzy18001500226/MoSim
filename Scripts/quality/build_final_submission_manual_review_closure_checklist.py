#!/usr/bin/env python3
"""Build a non-executing closure checklist for manual final-submission review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HANDOFF = (
    ROOT
    / "Results/static_audits/final_submission_reviewer_handoff_note_20260610"
    / "final_submission_reviewer_handoff_note.json"
)
DEFAULT_ANSWER_SHEET = (
    ROOT
    / "Results/static_audits/final_submission_manual_review_answer_sheet_20260610"
    / "final_submission_manual_review_answer_sheet_template.json"
)
DEFAULT_CONSISTENCY_CHECK = (
    ROOT
    / "Results/static_audits/final_submission_manual_review_answer_sheet_20260610"
    / "final_submission_answer_sheet_decision_consistency_check.json"
)
DEFAULT_RERUN_MATRIX = (
    ROOT
    / "Results/static_audits/final_submission_post_review_rerun_matrix_20260610"
    / "final_submission_post_review_rerun_matrix.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_manual_review_closure_checklist_20260610"


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


def source_record(source_id: str, path: Path, data: dict[str, Any]) -> dict[str, Any]:
    summary = data.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}
    return {
        "source_id": source_id,
        "path": rel(path),
        "status": data.get("status", ""),
        "summary": summary,
    }


def checklist_items(answer_sheet: dict[str, Any]) -> list[dict[str, Any]]:
    sections = answer_sheet.get("sections", [])
    if not isinstance(sections, list):
        sections = []
    items: list[dict[str, Any]] = []
    for section in sections:
        if not isinstance(section, dict):
            continue
        action_id = str(section.get("action_id", ""))
        answer_fields = [item for item in section.get("answer_fields", []) if isinstance(item, dict)]
        items.append(
            {
                "item_id": f"CLOSE-{len(items) + 1:02d}-{action_id}",
                "action_id": action_id,
                "decision_artifact": section.get("decision_artifact", ""),
                "answer_field_count": len(answer_fields),
                "required_answer_field_count": sum(
                    1 for item in answer_fields if item.get("human_choice_required") is True
                ),
                "must_confirm": [
                    "Human/PMO reviewed the corresponding source files.",
                    "Required answer fields are no longer placeholders in a separately edited answer artifact.",
                    "Any decision-template edit is performed in a separate authorized step.",
                    "Post-review rerun commands remain blocked until the decision edit is complete.",
                ],
                "copies_answers_now": False,
                "edits_decision_templates_now": False,
                "runs_rerun_commands_now": False,
                "approves_or_executes_now": False,
            }
        )
    return items


def build_closure_checklist(
    handoff_path: Path,
    answer_sheet_path: Path,
    consistency_check_path: Path,
    rerun_matrix_path: Path,
) -> dict[str, Any]:
    handoff = read_json(handoff_path)
    answer_sheet = read_json(answer_sheet_path)
    consistency_check = read_json(consistency_check_path)
    rerun_matrix = read_json(rerun_matrix_path)
    items = checklist_items(answer_sheet)
    return {
        "closure_checklist_id": "final_submission_manual_review_closure_checklist_20260610",
        "status": "manual_review_closure_checklist_not_execution",
        "sources": {
            "reviewer_handoff_note": source_record("reviewer_handoff_note", handoff_path, handoff),
            "manual_review_answer_sheet": source_record("manual_review_answer_sheet", answer_sheet_path, answer_sheet),
            "answer_sheet_decision_consistency": source_record(
                "answer_sheet_decision_consistency", consistency_check_path, consistency_check
            ),
            "post_review_rerun_matrix": source_record("post_review_rerun_matrix", rerun_matrix_path, rerun_matrix),
        },
        "summary": {
            "closure_item_count": len(items),
            "handoff_step_count": handoff.get("summary", {}).get("handoff_step_count", 0),
            "answer_field_count": answer_sheet.get("summary", {}).get("answer_field_count", 0),
            "required_answer_field_count": answer_sheet.get("summary", {}).get("required_answer_field_count", 0),
            "copied_field_count": consistency_check.get("summary", {}).get("copied_field_count", 0),
            "rerun_matrix_row_count": rerun_matrix.get("summary", {}).get("matrix_row_count", 0),
            "automated_execution_allowed": False,
            "copies_answers_now": False,
            "edits_decision_templates_now": False,
            "runs_rerun_commands_now": False,
            "approves_or_executes_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "closure_items": items,
        "required_after_manual_fill_checks": [
            "python Scripts/quality/check_final_submission_answer_sheet_decision_consistency.py",
            "python Scripts/quality/check_report_source_edit_decision.py",
            "python Scripts/quality/check_final_output_execution_decision.py",
            "python Scripts/quality/check_final_submission_refresh_order.py",
        ],
        "claim_boundary": [
            "This closure checklist is a static checklist for after future human review.",
            "It does not fill answer-sheet values.",
            "It does not copy answer values into decision artifacts.",
            "It does not edit decision templates.",
            "It does not approve decisions.",
            "It does not run rerun commands.",
            "It does not apply report-source edits.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(checklist: dict[str, Any], path: Path) -> None:
    summary = checklist["summary"]
    lines = [
        "# Final Submission Manual Review Closure Checklist, 2026-06-10",
        "",
        f"Status: `{checklist['status']}`",
        "",
        "## Summary",
        "",
        f"- Closure items: `{summary['closure_item_count']}`",
        f"- Handoff steps: `{summary['handoff_step_count']}`",
        f"- Answer fields: `{summary['answer_field_count']}`",
        f"- Required answer fields: `{summary['required_answer_field_count']}`",
        f"- Copied fields: `{summary['copied_field_count']}`",
        f"- Rerun matrix rows: `{summary['rerun_matrix_row_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Copies answers now: `{summary['copies_answers_now']}`",
        f"- Edits decision templates now: `{summary['edits_decision_templates_now']}`",
        f"- Runs rerun commands now: `{summary['runs_rerun_commands_now']}`",
        f"- Approves or executes now: `{summary['approves_or_executes_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Closure Items",
        "",
    ]
    for item in checklist["closure_items"]:
        lines.extend(
            [
                f"### {item['item_id']}",
                "",
                f"- Action: `{item['action_id']}`",
                f"- Decision artifact: `{item['decision_artifact']}`",
                f"- Answer fields: `{item['answer_field_count']}`",
                f"- Required answer fields: `{item['required_answer_field_count']}`",
                f"- Copies answers now: `{item['copies_answers_now']}`",
                f"- Edits decision templates now: `{item['edits_decision_templates_now']}`",
                f"- Runs rerun commands now: `{item['runs_rerun_commands_now']}`",
                "- Must confirm:",
            ]
        )
        for confirm in item["must_confirm"]:
            lines.append(f"  - {confirm}")
        lines.append("")
    lines.extend(["## Required After Manual Fill Checks", ""])
    for command in checklist["required_after_manual_fill_checks"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Claim Boundary", ""])
    for item in checklist["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handoff", default=str(DEFAULT_HANDOFF.relative_to(ROOT)))
    parser.add_argument("--answer-sheet", default=str(DEFAULT_ANSWER_SHEET.relative_to(ROOT)))
    parser.add_argument("--consistency-check", default=str(DEFAULT_CONSISTENCY_CHECK.relative_to(ROOT)))
    parser.add_argument("--rerun-matrix", default=str(DEFAULT_RERUN_MATRIX.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    checklist = build_closure_checklist(
        repo_path(args.handoff),
        repo_path(args.answer_sheet),
        repo_path(args.consistency_check),
        repo_path(args.rerun_matrix),
    )
    json_path = output_dir / "final_submission_manual_review_closure_checklist.json"
    md_path = output_dir / "final_submission_manual_review_closure_checklist.md"
    json_path.write_text(json.dumps(checklist, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(checklist, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "closure_json": rel(json_path),
                "closure_markdown": rel(md_path),
                "closure_item_count": checklist["summary"]["closure_item_count"],
                "answer_field_count": checklist["summary"]["answer_field_count"],
                "copied_field_count": checklist["summary"]["copied_field_count"],
                "runs_rerun_commands_now": checklist["summary"]["runs_rerun_commands_now"],
                "automated_execution_allowed": checklist["summary"]["automated_execution_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
