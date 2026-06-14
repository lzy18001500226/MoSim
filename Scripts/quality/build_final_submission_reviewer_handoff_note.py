#!/usr/bin/env python3
"""Build a non-executing reviewer handoff note for final-submission review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUNDLE = (
    ROOT
    / "Results/static_audits/final_submission_review_artifact_bundle_20260610"
    / "final_submission_review_artifact_bundle_index.json"
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
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_reviewer_handoff_note_20260610"


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


def artifact_by_id(bundle: dict[str, Any]) -> dict[str, dict[str, Any]]:
    artifacts = bundle.get("artifacts", [])
    if not isinstance(artifacts, list):
        return {}
    return {
        str(item.get("artifact_id", "")): item
        for item in artifacts
        if isinstance(item, dict)
    }


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


def handoff_steps(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    artifacts = artifact_by_id(bundle)
    return [
        {
            "step_id": "H1-open-reviewer-quickstart-first",
            "action": "Open reviewer_quickstart before any decision edit.",
            "artifact_id": "reviewer_quickstart",
            "artifact_path": artifacts.get("reviewer_quickstart", {}).get("markdown_path", ""),
            "expected_status": "reviewer_quickstart_not_execution",
            "execution_allowed": False,
        },
        {
            "step_id": "H2-pick-blocker-lane-from-triage-map",
            "action": "Use the blocked-gate triage map to choose whether A1, A3, or A6 should be reviewed first.",
            "artifact_id": "blocked_gate_triage_map",
            "artifact_path": artifacts.get("blocked_gate_triage_map", {}).get("markdown_path", ""),
            "expected_status": "blocked_gate_triage_map_not_execution",
            "execution_allowed": False,
        },
        {
            "step_id": "H3-use-decision-diff-and-answer-sheet",
            "action": "Use the human-decision diff template plus the manual-review answer sheet for A1/A3/A6 answers.",
            "artifact_id": "manual_review_answer_sheet",
            "artifact_path": artifacts.get("manual_review_answer_sheet", {}).get("markdown_path", ""),
            "expected_status": "manual_review_answer_sheet_template_not_execution",
            "execution_allowed": False,
        },
        {
            "step_id": "H4-confirm-answer-sheet-consistency",
            "action": "Confirm copied_field_count remains 0 before treating answers as still un-applied placeholders.",
            "artifact_id": "answer_sheet_decision_consistency",
            "artifact_path": artifacts.get("answer_sheet_decision_consistency", {}).get("json_path", ""),
            "expected_status": "answer_sheet_decision_consistency_check_not_execution",
            "execution_allowed": False,
        },
        {
            "step_id": "H5-use-rerun-matrix-only-after-human-decision-edit",
            "action": "Use the post-review rerun matrix only after a separate human decision edit authorizes reruns.",
            "artifact_id": "post_review_rerun_matrix",
            "artifact_path": artifacts.get("post_review_rerun_matrix", {}).get("markdown_path", ""),
            "expected_status": "post_review_rerun_matrix_not_execution",
            "execution_allowed": False,
        },
    ]


def build_handoff_note(
    bundle_path: Path,
    answer_sheet_path: Path,
    consistency_check_path: Path,
) -> dict[str, Any]:
    bundle = read_json(bundle_path)
    answer_sheet = read_json(answer_sheet_path)
    consistency_check = read_json(consistency_check_path)
    steps = handoff_steps(bundle)
    copied_field_count = consistency_check.get("summary", {}).get("copied_field_count", 0)
    return {
        "handoff_id": "final_submission_reviewer_handoff_note_20260610",
        "status": "reviewer_handoff_note_not_execution",
        "sources": {
            "review_artifact_bundle": source_record("review_artifact_bundle", bundle_path, bundle),
            "manual_review_answer_sheet": source_record("manual_review_answer_sheet", answer_sheet_path, answer_sheet),
            "answer_sheet_decision_consistency": source_record(
                "answer_sheet_decision_consistency", consistency_check_path, consistency_check
            ),
        },
        "summary": {
            "handoff_step_count": len(steps),
            "bundle_artifact_count": bundle.get("summary", {}).get("bundle_artifact_count", 0),
            "ready_bundle_artifact_count": bundle.get("summary", {}).get("ready_bundle_artifact_count", 0),
            "answer_field_count": answer_sheet.get("summary", {}).get("answer_field_count", 0),
            "required_answer_field_count": answer_sheet.get("summary", {}).get("required_answer_field_count", 0),
            "copied_field_count": copied_field_count,
            "automated_execution_allowed": False,
            "approves_or_executes_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "handoff_steps": steps,
        "first_review_targets": [
            "A1-approve-or-reject-report-source-edits",
            "A3-review-demo-storyboard",
            "A6-review-final-output-execution-decision",
        ],
        "pre_execution_guard": [
            "Do not edit decision templates from this handoff note.",
            "Do not copy answer-sheet placeholders into decision artifacts.",
            "Do not run post-review rerun commands before a separate human decision edit.",
            "Do not export PDFs, record demo video, or write final acceptance from this handoff note.",
        ],
        "claim_boundary": [
            "This handoff note summarizes the review order only.",
            "It does not fill answer-sheet values.",
            "It does not edit decision templates.",
            "It does not approve decisions.",
            "It does not run post-review commands.",
            "It does not apply report-source edits.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(handoff: dict[str, Any], path: Path) -> None:
    summary = handoff["summary"]
    lines = [
        "# Final Submission Reviewer Handoff Note, 2026-06-10",
        "",
        f"Status: `{handoff['status']}`",
        "",
        "## Summary",
        "",
        f"- Handoff steps: `{summary['handoff_step_count']}`",
        f"- Bundle artifacts: `{summary['bundle_artifact_count']}`",
        f"- Ready bundle artifacts: `{summary['ready_bundle_artifact_count']}`",
        f"- Answer fields: `{summary['answer_field_count']}`",
        f"- Required answer fields: `{summary['required_answer_field_count']}`",
        f"- Copied fields: `{summary['copied_field_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Approves or executes now: `{summary['approves_or_executes_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Handoff Steps",
        "",
    ]
    for index, step in enumerate(handoff["handoff_steps"], start=1):
        lines.extend(
            [
                f"{index}. `{step['step_id']}`",
                f"   - Action: {step['action']}",
                f"   - Artifact: `{step['artifact_id']}`",
                f"   - Path: `{step['artifact_path']}`",
                f"   - Expected status: `{step['expected_status']}`",
                f"   - Execution allowed: `{step['execution_allowed']}`",
            ]
        )
    lines.extend(["", "## First Review Targets", ""])
    for target in handoff["first_review_targets"]:
        lines.append(f"- `{target}`")
    lines.extend(["", "## Pre-Execution Guard", ""])
    for item in handoff["pre_execution_guard"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Claim Boundary", ""])
    for item in handoff["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", default=str(DEFAULT_BUNDLE.relative_to(ROOT)))
    parser.add_argument("--answer-sheet", default=str(DEFAULT_ANSWER_SHEET.relative_to(ROOT)))
    parser.add_argument("--consistency-check", default=str(DEFAULT_CONSISTENCY_CHECK.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    handoff = build_handoff_note(
        repo_path(args.bundle),
        repo_path(args.answer_sheet),
        repo_path(args.consistency_check),
    )
    json_path = output_dir / "final_submission_reviewer_handoff_note.json"
    md_path = output_dir / "final_submission_reviewer_handoff_note.md"
    json_path.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(handoff, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "handoff_json": rel(json_path),
                "handoff_markdown": rel(md_path),
                "handoff_step_count": handoff["summary"]["handoff_step_count"],
                "bundle_artifact_count": handoff["summary"]["bundle_artifact_count"],
                "answer_field_count": handoff["summary"]["answer_field_count"],
                "copied_field_count": handoff["summary"]["copied_field_count"],
                "automated_execution_allowed": handoff["summary"]["automated_execution_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
