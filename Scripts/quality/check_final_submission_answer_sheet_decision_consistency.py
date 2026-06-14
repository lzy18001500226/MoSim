#!/usr/bin/env python3
"""Check answer-sheet placeholders against current decision templates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ANSWER_SHEET = (
    ROOT
    / "Results/static_audits/final_submission_manual_review_answer_sheet_20260610"
    / "final_submission_manual_review_answer_sheet_template.json"
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
DEFAULT_OUTPUT_JSON = (
    ROOT
    / "Results/static_audits/final_submission_manual_review_answer_sheet_20260610"
    / "final_submission_answer_sheet_decision_consistency_check.json"
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


def nested_get(data: dict[str, Any], dotted_path: str) -> Any:
    value: Any = data
    for key in dotted_path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def action_template_for_section(section: dict[str, Any], report_decision: dict[str, Any], final_output_decision: dict[str, Any]) -> dict[str, Any]:
    if section.get("action_id") == "A1-approve-or-reject-report-source-edits":
        return report_decision
    return final_output_decision


def check_section(
    section: dict[str, Any],
    report_decision: dict[str, Any],
    final_output_decision: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    issues: list[str] = []
    action_id = str(section.get("action_id", ""))
    template = action_template_for_section(section, report_decision, final_output_decision)
    fields = [field for field in section.get("answer_fields", []) if isinstance(field, dict)]
    copied_fields: list[str] = []
    unfilled_fields: list[str] = []
    for field in fields:
        field_path = str(field.get("field_path", ""))
        proposed = field.get("proposed_value")
        if proposed == "<fill_after_review>":
            unfilled_fields.append(field_path)
        else:
            issues.append(f"{action_id}.{field_path} proposed_value is not placeholder")
        current_value = nested_get(template, field_path)
        if current_value == proposed:
            copied_fields.append(field_path)
            issues.append(f"{action_id}.{field_path} appears copied into decision template")
    if section.get("copies_answers_now") is not False:
        issues.append(f"{action_id}.copies_answers_now must be false")
    if section.get("edits_decision_artifact_now") is not False:
        issues.append(f"{action_id}.edits_decision_artifact_now must be false")
    if section.get("approves_or_executes_now") is not False:
        issues.append(f"{action_id}.approves_or_executes_now must be false")
    answer = section.get("human_review_answer", {})
    if not isinstance(answer, dict):
        issues.append(f"{action_id}.human_review_answer must be an object")
        answer = {}
    if answer.get("approved") is not False:
        issues.append(f"{action_id}.human_review_answer.approved must be false")
    return (
        {
            "action_id": action_id,
            "field_count": len(fields),
            "unfilled_placeholder_field_count": len(unfilled_fields),
            "copied_field_count": len(copied_fields),
            "decision_artifact": section.get("decision_artifact", ""),
            "copies_answers_now": section.get("copies_answers_now", None),
            "edits_decision_artifact_now": section.get("edits_decision_artifact_now", None),
            "approves_or_executes_now": section.get("approves_or_executes_now", None),
        },
        issues,
    )


def validate(
    answer_sheet_path: Path,
    report_decision_path: Path,
    final_output_decision_path: Path,
) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []
    answer_sheet = read_json(answer_sheet_path)
    report_decision = read_json(report_decision_path)
    final_output_decision = read_json(final_output_decision_path)

    sections = [section for section in answer_sheet.get("sections", []) if isinstance(section, dict)]
    section_results: list[dict[str, Any]] = []
    for section in sections:
        result, section_issues = check_section(section, report_decision, final_output_decision)
        section_results.append(result)
        issues.extend(section_issues)

    summary = answer_sheet.get("summary", {})
    if not isinstance(summary, dict):
        issues.append("answer_sheet.summary must be an object")
        summary = {}
    expected_false = [
        "automated_execution_allowed",
        "copies_answers_now",
        "edits_decision_artifacts_now",
        "approves_or_executes_now",
        "generates_final_outputs",
        "final_acceptance",
    ]
    for key in expected_false:
        if summary.get(key) is not False:
            issues.append(f"answer_sheet.summary.{key} must be false")

    if report_decision.get("decision") != "pending_review":
        warnings.append("report source decision is no longer pending_review")
    if report_decision.get("safe_to_apply_report_source_edits") is not False:
        issues.append("report source decision safe_to_apply_report_source_edits must remain false")
    final_actions = final_output_decision.get("actions", {})
    if not isinstance(final_actions, dict):
        issues.append("final output decision actions must be an object")
        final_actions = {}
    for action_id, action in final_actions.items():
        if not isinstance(action, dict):
            issues.append(f"final output action {action_id} must be an object")
            continue
        if action.get("decision") != "pending_review":
            warnings.append(f"final output action {action_id} is no longer pending_review")
        if action.get("approved") is not False:
            issues.append(f"final output action {action_id}.approved must remain false")
    flags = final_output_decision.get("execution_flags", {})
    if not isinstance(flags, dict):
        issues.append("final_output_decision.execution_flags must be an object")
        flags = {}
    for flag in [
        "creates_submission_dir_now",
        "runs_pandoc_now",
        "records_or_renders_video_now",
        "writes_canonical_acceptance_packet_now",
        "generates_final_outputs",
        "final_acceptance",
    ]:
        if flags.get(flag) is not False:
            issues.append(f"final_output_decision.execution_flags.{flag} must remain false")

    total_fields = sum(item["field_count"] for item in section_results)
    unfilled = sum(item["unfilled_placeholder_field_count"] for item in section_results)
    copied = sum(item["copied_field_count"] for item in section_results)
    return {
        "ok": not issues,
        "check_id": "final_submission_answer_sheet_decision_consistency_20260610",
        "status": "answer_sheet_decision_consistency_check_not_execution",
        "sources": {
            "answer_sheet": rel(answer_sheet_path),
            "report_source_edit_decision": rel(report_decision_path),
            "final_output_execution_decision": rel(final_output_decision_path),
        },
        "summary": {
            "review_action_count": len(section_results),
            "answer_field_count": total_fields,
            "unfilled_placeholder_field_count": unfilled,
            "copied_field_count": copied,
            "issue_count": len(issues),
            "warning_count": len(warnings),
            "report_source_decision": report_decision.get("decision", ""),
            "final_output_pending_action_count": sum(
                1 for item in final_actions.values() if isinstance(item, dict) and item.get("decision") == "pending_review"
            ),
            "automated_execution_allowed": False,
            "applies_decisions_now": False,
            "edits_decision_templates_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "sections": section_results,
        "issues": issues,
        "warnings": warnings,
        "claim_boundary": [
            "This checker compares placeholders and current decision templates only.",
            "It does not copy answer-sheet values.",
            "It does not edit decision templates.",
            "It does not approve decisions.",
            "It does not run post-review checkers.",
            "It does not apply report-source edits.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--answer-sheet", default=str(DEFAULT_ANSWER_SHEET.relative_to(ROOT)))
    parser.add_argument("--report-decision", default=str(DEFAULT_REPORT_DECISION.relative_to(ROOT)))
    parser.add_argument("--final-output-decision", default=str(DEFAULT_FINAL_OUTPUT_DECISION.relative_to(ROOT)))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON.relative_to(ROOT)))
    args = parser.parse_args()

    result = validate(
        repo_path(args.answer_sheet),
        repo_path(args.report_decision),
        repo_path(args.final_output_decision),
    )
    output_json = repo_path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
