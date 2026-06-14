#!/usr/bin/env python3
"""Build a compact reviewer quickstart for A1/A3/A6 final-submission review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GUIDE = (
    ROOT
    / "Results/static_audits/final_submission_human_review_guide_20260610"
    / "final_submission_human_review_guide.json"
)
DEFAULT_DIFF_TEMPLATE = (
    ROOT
    / "Results/static_audits/final_submission_human_decision_diff_template_20260610"
    / "final_submission_human_decision_diff_template.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_reviewer_quickstart_20260610"

ACTION_ORDER = [
    "A1-approve-or-reject-report-source-edits",
    "A3-review-demo-storyboard",
    "A6-review-final-output-execution-decision",
]

ACTION_QUESTIONS = {
    "A1-approve-or-reject-report-source-edits": [
        "Which report-source preview ids are approved, rejected, narrowed, or still pending?",
        "Does any approved/narrowed choice preserve final-acceptance, planner_ready, closed_loop, and UE runtime boundaries?",
        "Should safe_to_apply_report_source_edits remain false or become true after explicit approval?",
    ],
    "A3-review-demo-storyboard": [
        "Are the storyboard scenes, evidence references, and wording acceptable for a future demo video?",
        "Does the storyboard avoid unsupported final performance, runtime, or acceptance claims?",
        "Should demo video recording stay blocked or be considered for a separate execution decision after gates pass?",
    ],
    "A6-review-final-output-execution-decision": [
        "Should PDF export, demo video recording, and final acceptance packet writing remain pending, be rejected, or be approved?",
        "Are upstream readiness gates true before any action is approved?",
        "Do all execution flags stay false until a separate authorized execution step?",
    ],
}

ACTION_MIN_FILES = {
    "A1-approve-or-reject-report-source-edits": [
        "Results/static_audits/final_submission_human_decision_diff_template_20260610/final_submission_human_decision_diff_template.md",
        "Results/static_audits/simulation_report_patch_preview_20260610/simulation_report_patch_preview.md",
        "Results/static_audits/simulation_report_source_edit_reviewer_summary_20260610/simulation_report_source_edit_reviewer_summary.md",
        "Results/static_audits/report_source_edit_decision_template_20260610/report_source_edit_decision.template.json",
    ],
    "A3-review-demo-storyboard": [
        "Results/static_audits/demo_video_storyboard_plan_20260610/demo_video_storyboard_plan.md",
        "Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision.template.json",
    ],
    "A6-review-final-output-execution-decision": [
        "Results/static_audits/final_submission_human_decision_diff_template_20260610/final_submission_human_decision_diff_template.md",
        "Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision_template.md",
        "Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision.template.json",
        "Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision_check.json",
    ],
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


def review_steps_by_action(guide: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(step.get("action_id", "")): step
        for step in guide.get("review_steps", [])
        if isinstance(step, dict)
    }


def decision_group_for_action(action_id: str, diff_template: dict[str, Any]) -> str:
    if action_id == "A1-approve-or-reject-report-source-edits":
        return "A1-report-source-edit-decision"
    if action_id in {
        "A3-review-demo-storyboard",
        "A6-review-final-output-execution-decision",
    }:
        return "A6-final-output-execution-decision"
    return ""


def quickstart_section(
    action_id: str,
    guide_step: dict[str, Any],
    diff_template: dict[str, Any],
) -> dict[str, Any]:
    minimum_files = [
        {"path": path, "exists": repo_path(path).exists()}
        for path in ACTION_MIN_FILES[action_id]
    ]
    return {
        "action_id": action_id,
        "decision_owner": guide_step.get("decision_owner", "user_or_PMO"),
        "current_decision": guide_step.get("current_decision", "pending_review"),
        "decision_needed": guide_step.get("decision_needed", ""),
        "decision_artifact": guide_step.get("decision_artifact", ""),
        "decision_diff_group": decision_group_for_action(action_id, diff_template),
        "minimum_open_files": minimum_files,
        "review_questions": ACTION_QUESTIONS[action_id],
        "post_review_checkers": guide_step.get("rerun_after_review", []),
        "forbidden_without_separate_gate": guide_step.get("forbidden_without_separate_gate", []),
        "approves_or_executes_now": False,
    }


def build_quickstart(guide_path: Path, diff_template_path: Path) -> dict[str, Any]:
    guide = read_json(guide_path)
    diff_template = read_json(diff_template_path)
    steps = review_steps_by_action(guide)
    sections = [
        quickstart_section(action_id, steps.get(action_id, {}), diff_template)
        for action_id in ACTION_ORDER
    ]
    missing_files = sorted(
        {
            item["path"]
            for section in sections
            for item in section["minimum_open_files"]
            if item["exists"] is not True
        }
    )
    return {
        "quickstart_id": "final_submission_reviewer_quickstart_20260610",
        "status": "reviewer_quickstart_not_execution",
        "source_guide": rel(guide_path),
        "source_human_decision_diff_template": rel(diff_template_path),
        "summary": {
            "review_action_count": len(sections),
            "minimum_open_file_count": sum(len(section["minimum_open_files"]) for section in sections),
            "missing_open_file_count": len(missing_files),
            "automated_execution_allowed": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "review_order": ACTION_ORDER,
        "sections": sections,
        "missing_open_files": missing_files,
        "claim_boundary": [
            "This quickstart is a compact review guide only.",
            "It does not edit decision artifacts.",
            "It does not approve decisions.",
            "It does not execute post-review checkers.",
            "It does not apply report-source edits.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(quickstart: dict[str, Any], path: Path) -> None:
    summary = quickstart["summary"]
    lines = [
        "# Final Submission Reviewer Quickstart, 2026-06-10",
        "",
        f"Status: `{quickstart['status']}`",
        "",
        "## Summary",
        "",
        f"- Review actions: `{summary['review_action_count']}`",
        f"- Minimum open files: `{summary['minimum_open_file_count']}`",
        f"- Missing open files: `{summary['missing_open_file_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Review Order",
        "",
    ]
    for index, action_id in enumerate(quickstart["review_order"], start=1):
        lines.append(f"{index}. `{action_id}`")
    lines.extend(["", "## Quickstart Sections", ""])
    for section in quickstart["sections"]:
        lines.extend(
            [
                f"### {section['action_id']}",
                "",
                f"- Decision owner: `{section['decision_owner']}`",
                f"- Current decision: `{section['current_decision']}`",
                f"- Decision needed: {section['decision_needed']}",
                f"- Decision artifact: `{section['decision_artifact']}`",
                f"- Decision diff group: `{section['decision_diff_group']}`",
                "- Minimum open files:",
            ]
        )
        for item in section["minimum_open_files"]:
            lines.append(f"  - `{item['path']}` exists=`{item['exists']}`")
        lines.append("- Review questions:")
        for question in section["review_questions"]:
            lines.append(f"  - {question}")
        lines.append("- Post-review checkers:")
        for command in section["post_review_checkers"]:
            lines.append(f"  - `{command}`")
        lines.append("")
    lines.extend(["## Claim Boundary", ""])
    for item in quickstart["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--guide", default=str(DEFAULT_GUIDE.relative_to(ROOT)))
    parser.add_argument("--decision-diff-template", default=str(DEFAULT_DIFF_TEMPLATE.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    quickstart = build_quickstart(repo_path(args.guide), repo_path(args.decision_diff_template))
    json_path = output_dir / "final_submission_reviewer_quickstart.json"
    md_path = output_dir / "final_submission_reviewer_quickstart.md"
    json_path.write_text(json.dumps(quickstart, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(quickstart, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "quickstart_json": rel(json_path),
                "quickstart_markdown": rel(md_path),
                "review_action_count": quickstart["summary"]["review_action_count"],
                "minimum_open_file_count": quickstart["summary"]["minimum_open_file_count"],
                "missing_open_file_count": quickstart["summary"]["missing_open_file_count"],
                "automated_execution_allowed": quickstart["summary"]["automated_execution_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
