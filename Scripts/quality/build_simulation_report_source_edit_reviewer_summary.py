#!/usr/bin/env python3
"""Build a reviewer summary for simulation-report source edit previews.

The summary groups non-applying preview snippets by impact, evidence inputs,
and review questions. It never edits Docs/simulation_report.md.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PREVIEW = (
    ROOT
    / "Results/static_audits/simulation_report_patch_preview_20260610"
    / "simulation_report_patch_preview.json"
)
DEFAULT_SEQUENCE = (
    ROOT
    / "Results/static_audits/simulation_report_edit_sequence_20260610"
    / "simulation_report_edit_sequence_plan.json"
)
DEFAULT_APPLICATION_PLAN = (
    ROOT
    / "Results/static_audits/simulation_report_source_edit_application_plan_20260610"
    / "simulation_report_source_edit_application_plan.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/simulation_report_source_edit_reviewer_summary_20260610"


IMPACT_BY_KIND = {
    "boundary_guard": ("high", "acceptance_boundary"),
    "targeted_sentence_rewrite": ("high", "claim_boundary_update"),
    "candidate_subsection_insert": ("medium", "candidate_body_insert"),
    "condense_without_delete": ("medium", "source_hygiene_condense"),
    "structure_cleanup": ("low", "navigation_cleanup"),
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


def by_action_id(sequence: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(action.get("action_id")): action
        for action in sequence.get("actions", [])
        if isinstance(action, dict) and action.get("action_id")
    }


def review_questions(action: dict[str, Any], preview: dict[str, Any]) -> list[str]:
    kind = str(action.get("kind", ""))
    questions = [
        "Does this preview preserve the listed safety boundary?",
        "Is the target section correct for this change?",
        "Should this preview be approved, rejected, narrowed, or sent back for revision?",
    ]
    if kind == "candidate_subsection_insert":
        questions.append("Do the candidate metrics and figures support the proposed draft-only wording?")
    if kind == "condense_without_delete":
        questions.append("Can the historical/smoke material be condensed without deleting provenance?")
    if kind == "targeted_sentence_rewrite":
        questions.append("Does the rewrite separate available MWORKS/Sysplorer candidate evidence from unproven online formation claims?")
    if str(preview.get("operation", "")) == "verify_keep_existing_text":
        questions.append("Should the existing not-final acceptance boundary remain unchanged near the report front matter?")
    return questions


def build_item(
    preview: dict[str, Any],
    action: dict[str, Any],
    application_step: dict[str, Any] | None,
) -> dict[str, Any]:
    kind = str(action.get("kind", ""))
    impact_level, impact_class = IMPACT_BY_KIND.get(kind, ("medium", "manual_review"))
    return {
        "preview_id": str(preview.get("preview_id", "")),
        "source_action_id": str(preview.get("source_action_id", "")),
        "sequence_order": action.get("order"),
        "operation": preview.get("operation", ""),
        "target": preview.get("target", ""),
        "line_hint": preview.get("line_hint"),
        "kind": kind,
        "claim_family": action.get("claim_family", ""),
        "impact_level": impact_level,
        "impact_class": impact_class,
        "decision_options": ["pending_review", "approved", "rejected", "narrowed", "needs_revision"],
        "recommended_default": "pending_review",
        "planned_for_application": bool(application_step and application_step.get("planned_for_application") is True),
        "applies_now": False,
        "evidence_inputs": action.get("inputs", []),
        "safety_boundary": preview.get("safety_boundary", ""),
        "review_questions": review_questions(action, preview),
    }


def build_summary(preview_path: Path, sequence_path: Path, application_plan_path: Path) -> dict[str, Any]:
    preview = read_json(preview_path)
    sequence = read_json(sequence_path)
    application_plan = read_json(application_plan_path)
    actions = by_action_id(sequence)
    application_steps = {
        str(step.get("source_action_id")): step
        for step in application_plan.get("application_steps", [])
        if isinstance(step, dict) and step.get("source_action_id")
    }
    items = [
        build_item(item, actions.get(str(item.get("source_action_id")), {}), application_steps.get(str(item.get("source_action_id"))))
        for item in preview.get("previews", [])
        if isinstance(item, dict)
    ]
    missing_actions = [
        item["source_action_id"]
        for item in items
        if item["source_action_id"] and item["source_action_id"] not in actions
    ]
    high_impact_count = sum(1 for item in items if item["impact_level"] == "high")
    candidate_insert_count = sum(1 for item in items if item["impact_class"] == "candidate_body_insert")
    return {
        "summary_id": "simulation_report_source_edit_reviewer_summary_20260610",
        "status": "source_edit_reviewer_summary_not_execution",
        "inputs": {
            "simulation_report_patch_preview": rel(preview_path),
            "simulation_report_edit_sequence_plan": rel(sequence_path),
            "simulation_report_source_edit_application_plan": rel(application_plan_path),
        },
        "summary": {
            "preview_count": len(items),
            "missing_sequence_action_count": len(missing_actions),
            "high_impact_count": high_impact_count,
            "candidate_insert_count": candidate_insert_count,
            "manual_review_required_count": len(items),
            "automated_execution_allowed": False,
            "edits_report_source": False,
            "applies_report_source_edits_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "missing_sequence_actions": missing_actions,
        "review_items": items,
        "review_sequence": [
            "Review high-impact boundary items before candidate inserts.",
            "Approve, reject, narrow, or request revision for each preview id in the A1 decision artifact.",
            "Regenerate the readiness gate and application plan after the A1 decision changes.",
            "Apply approved report-source edits only in a separate explicitly authorized step.",
        ],
        "claim_boundary": [
            "This summary is a reviewer aid only.",
            "It does not edit Docs/simulation_report.md.",
            "It does not approve preview snippets.",
            "It does not apply report-source edits.",
            "It does not export PDFs/video or write PMO final acceptance.",
        ],
    }


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    data = summary["summary"]
    lines = [
        "# Simulation Report Source Edit Reviewer Summary, 2026-06-10",
        "",
        f"Status: `{summary['status']}`",
        "",
        "## Summary",
        "",
        f"- Previews: `{data['preview_count']}`",
        f"- Missing sequence actions: `{data['missing_sequence_action_count']}`",
        f"- High-impact items: `{data['high_impact_count']}`",
        f"- Candidate inserts: `{data['candidate_insert_count']}`",
        f"- Manual review required: `{data['manual_review_required_count']}`",
        f"- Automated execution allowed: `{data['automated_execution_allowed']}`",
        f"- Applies report source edits now: `{data['applies_report_source_edits_now']}`",
        f"- Final acceptance: `{data['final_acceptance']}`",
        "",
        "## Review Sequence",
        "",
    ]
    for index, item in enumerate(summary["review_sequence"], start=1):
        lines.append(f"{index}. {item}")
    lines.extend(
        [
            "",
            "## Review Items",
            "",
            "| Order | Preview | Impact | Kind | Target | Applies Now |",
            "|---:|---|---|---|---|---|",
        ]
    )
    for item in summary["review_items"]:
        lines.append(
            f"| {item['sequence_order']} | `{item['preview_id']}` | `{item['impact_level']}` | `{item['impact_class']}` | {item['target']} | `{item['applies_now']}` |"
        )
    lines.extend(["", "## Questions", ""])
    for item in summary["review_items"]:
        lines.extend([f"### {item['preview_id']}", "", f"- Safety boundary: {item['safety_boundary']}"])
        for question in item["review_questions"]:
            lines.append(f"- {question}")
        lines.append("")
    lines.extend(["## Claim Boundary", ""])
    for item in summary["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", default=str(DEFAULT_PREVIEW.relative_to(ROOT)))
    parser.add_argument("--sequence", default=str(DEFAULT_SEQUENCE.relative_to(ROOT)))
    parser.add_argument("--application-plan", default=str(DEFAULT_APPLICATION_PLAN.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = build_summary(repo_path(args.preview), repo_path(args.sequence), repo_path(args.application_plan))
    json_path = output_dir / "simulation_report_source_edit_reviewer_summary.json"
    md_path = output_dir / "simulation_report_source_edit_reviewer_summary.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(summary, md_path)
    print(
        json.dumps(
            {
                "ok": summary["summary"]["missing_sequence_action_count"] == 0,
                "summary_json": rel(json_path),
                "summary_markdown": rel(md_path),
                "preview_count": summary["summary"]["preview_count"],
                "high_impact_count": summary["summary"]["high_impact_count"],
                "candidate_insert_count": summary["summary"]["candidate_insert_count"],
                "automated_execution_allowed": summary["summary"]["automated_execution_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if summary["summary"]["missing_sequence_action_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
