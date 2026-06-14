#!/usr/bin/env python3
"""Build a static shortest-path note for final-submission manual review.

The note converts the owner/status digest into an ordered review sequence. It
is a navigation artifact only: it does not answer review questions, edit
decision artifacts, run commands, or authorize final-output execution.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DIGEST = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_execution_blocker_owner_status_digest_20260610"
    / "final_submission_execution_blocker_owner_status_digest.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_manual_review_shortest_path_20260610"

EXPECTED_ACTION_ORDER = [
    "A1-approve-or-reject-report-source-edits",
    "A3-review-demo-storyboard",
    "A2-provide-pdf-engine",
    "A6-review-final-output-execution-decision",
    "A4-create-reviewed-final-artifacts",
    "A5-rerun-readiness-gates",
]

ACTION_PREREQUISITES = {
    "A1-approve-or-reject-report-source-edits": [],
    "A3-review-demo-storyboard": [],
    "A2-provide-pdf-engine": [],
    "A6-review-final-output-execution-decision": [
        "A1-approve-or-reject-report-source-edits",
        "A2-provide-pdf-engine",
        "A3-review-demo-storyboard",
    ],
    "A4-create-reviewed-final-artifacts": [
        "A1-approve-or-reject-report-source-edits",
        "A2-provide-pdf-engine",
        "A3-review-demo-storyboard",
        "A6-review-final-output-execution-decision",
    ],
    "A5-rerun-readiness-gates": [
        "A1-approve-or-reject-report-source-edits",
        "A2-provide-pdf-engine",
        "A3-review-demo-storyboard",
        "A4-create-reviewed-final-artifacts",
        "A6-review-final-output-execution-decision",
    ],
}

HUMAN_REVIEW_ACTIONS = {
    "A1-approve-or-reject-report-source-edits",
    "A3-review-demo-storyboard",
    "A6-review-final-output-execution-decision",
}

NO_PACKET_ACTIONS = {
    "A2-provide-pdf-engine",
    "A4-create-reviewed-final-artifacts",
    "A5-rerun-readiness-gates",
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


def action_lookup(digest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    actions = digest.get("actions", [])
    if not isinstance(actions, list):
        return {}
    return {str(action.get("action_id", "")): action for action in actions if isinstance(action, dict)}


def stage_class(action_id: str) -> str:
    if action_id in HUMAN_REVIEW_ACTIONS:
        return "reviewer_packet_action"
    if action_id in NO_PACKET_ACTIONS:
        return "no_packet_escalation_action"
    return "unknown_action_class"


def stage_instruction(action_id: str) -> str:
    if action_id == "A1-approve-or-reject-report-source-edits":
        return "Review report-source edit preview and decide approve, reject, keep pending, or narrow scope."
    if action_id == "A3-review-demo-storyboard":
        return "Review demo storyboard wording, scenes, and evidence boundaries."
    if action_id == "A2-provide-pdf-engine":
        return "Decide whether an approved PDF engine is available or keep PDF export blocked."
    if action_id == "A6-review-final-output-execution-decision":
        return "Review final-output execution decision after upstream review/environment decisions are known."
    if action_id == "A4-create-reviewed-final-artifacts":
        return "Create reviewed final artifacts only after separate authorization changes the blockers."
    if action_id == "A5-rerun-readiness-gates":
        return "Rerun readiness gates only after human decisions, environment setup, or artifacts change."
    return "Unknown action; do not proceed without PMO/user review."


def build_note(digest_path: Path) -> dict[str, Any]:
    digest = read_json(digest_path)
    lookup = action_lookup(digest)
    digest_summary = digest.get("summary", {})
    if not isinstance(digest_summary, dict):
        digest_summary = {}

    issues: list[str] = []
    if digest.get("status") != "execution_blocker_owner_status_digest_not_execution":
        issues.append("source digest status is not execution_blocker_owner_status_digest_not_execution")
    if int(digest_summary.get("issue_count", 0)) != 0:
        issues.append("source digest has open issues")

    missing = [action_id for action_id in EXPECTED_ACTION_ORDER if action_id not in lookup]
    if missing:
        issues.append("missing expected actions: " + ", ".join(missing))

    path_steps: list[dict[str, Any]] = []
    seen: set[str] = set()
    for order, action_id in enumerate(EXPECTED_ACTION_ORDER, start=1):
        action = lookup.get(action_id, {})
        prerequisites = ACTION_PREREQUISITES[action_id]
        missing_prerequisites = [item for item in prerequisites if item not in lookup]
        if missing_prerequisites:
            issues.append(f"{action_id} has missing prerequisites: {', '.join(missing_prerequisites)}")
        late_prerequisites = [item for item in prerequisites if item in lookup and item not in seen]
        if late_prerequisites:
            issues.append(f"{action_id} appears before prerequisite actions: {', '.join(late_prerequisites)}")
        seen.add(action_id)
        path_steps.append(
            {
                "order": order,
                "action_id": action_id,
                "owner": action.get("owner", ""),
                "stage_class": stage_class(action_id),
                "decision_needed": action.get("decision_needed", ""),
                "instruction": stage_instruction(action_id),
                "prerequisite_action_ids": prerequisites,
                "target_ids": list(action.get("target_ids", [])),
                "blocker_classes": list(action.get("blocker_classes", [])),
                "blocked_artifact_count": int(action.get("blocked_artifact_count", 0)),
                "can_review_in_same_human_session": action_id in HUMAN_REVIEW_ACTIONS,
                "requires_separate_authorization_before_execution": True,
                "answers_questions_now": False,
                "fills_answers_now": False,
                "copies_answers_now": False,
                "edits_decision_artifacts_now": False,
                "runs_commands_now": False,
                "authorizes_execution_now": False,
                "generates_final_outputs": False,
                "final_acceptance": False,
            }
        )

    owner_groups = digest.get("owner_groups", [])
    owner_count = len(owner_groups) if isinstance(owner_groups, list) else 0
    human_review_count = sum(1 for step in path_steps if step["action_id"] in HUMAN_REVIEW_ACTIONS)
    no_packet_count = sum(1 for step in path_steps if step["action_id"] in NO_PACKET_ACTIONS)
    independent_start_count = sum(1 for step in path_steps if not step["prerequisite_action_ids"])

    summary = {
        "source_status": digest.get("status", ""),
        "owner_count": owner_count,
        "source_action_count": int(digest_summary.get("action_count", len(lookup))),
        "path_step_count": len(path_steps),
        "human_review_action_count": human_review_count,
        "no_packet_action_count": no_packet_count,
        "independent_start_action_count": independent_start_count,
        "blocked_execution_target_count": int(digest_summary.get("blocked_execution_target_count", 0)),
        "target_action_reference_count": int(digest_summary.get("target_action_reference_count", 0)),
        "dashboard_blocker_count": int(digest_summary.get("dashboard_blocker_count", 0)),
        "reviewer_open_file_count": int(digest_summary.get("reviewer_open_file_count", 0)),
        "reviewer_open_file_drift_count": int(digest_summary.get("reviewer_open_file_drift_count", 0)),
        "issue_count": len(issues),
        "automated_execution_allowed": False,
        "answers_questions_now": False,
        "fills_answers_now": False,
        "copies_answers_now": False,
        "edits_decision_artifacts_now": False,
        "runs_commands_now": False,
        "authorizes_execution_now": False,
        "generates_final_outputs": False,
        "final_acceptance": False,
    }

    return {
        "note_id": "final_submission_manual_review_shortest_path_20260610",
        "status": "manual_review_shortest_path_note_not_execution",
        "sources": {
            "execution_blocker_owner_status_digest": rel(digest_path),
        },
        "summary": summary,
        "shortest_path": path_steps,
        "review_session_hints": [
            "A1, A3, and A6 share user_or_PMO ownership and can be opened in one human review session.",
            "A6 should not authorize output execution until A1/A2/A3 status is known.",
            "A4 and A5 remain future execution/check steps after separate authorization or artifact changes.",
        ],
        "issues": issues,
        "claim_boundary": [
            "This shortest-path note is a static navigation artifact only.",
            "It orders existing A1-A6 review and blocker actions.",
            "It does not answer review questions.",
            "It does not fill or copy answer-sheet values.",
            "It does not edit decision artifacts.",
            "It does not approve or reject decisions.",
            "It does not install PDF tooling.",
            "It does not create final artifacts.",
            "It does not rerun readiness gates.",
            "It does not run commands.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
            "It does not run live tools or visible-thread dispatch.",
        ],
    }


def write_markdown(note: dict[str, Any], path: Path) -> None:
    summary = note["summary"]
    lines = [
        "# Final Submission Manual-Review Shortest-Path Note, 2026-06-10",
        "",
        f"Status: `{note['status']}`",
        "",
        "## Summary",
        "",
        f"- Source status: `{summary['source_status']}`",
        f"- Owners: `{summary['owner_count']}`",
        f"- Source actions: `{summary['source_action_count']}`",
        f"- Path steps: `{summary['path_step_count']}`",
        f"- Human-review actions: `{summary['human_review_action_count']}`",
        f"- No-packet actions: `{summary['no_packet_action_count']}`",
        f"- Independent start actions: `{summary['independent_start_action_count']}`",
        f"- Blocked execution targets: `{summary['blocked_execution_target_count']}`",
        f"- Target/action references: `{summary['target_action_reference_count']}`",
        f"- Dashboard blockers: `{summary['dashboard_blocker_count']}`",
        f"- Reviewer open files: `{summary['reviewer_open_file_count']}`",
        f"- Reviewer open-file drift: `{summary['reviewer_open_file_drift_count']}`",
        f"- Issues: `{summary['issue_count']}`",
        f"- Runs commands now: `{summary['runs_commands_now']}`",
        f"- Authorizes execution now: `{summary['authorizes_execution_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Shortest Path",
        "",
    ]
    for step in note["shortest_path"]:
        prerequisites = ", ".join(step["prerequisite_action_ids"]) if step["prerequisite_action_ids"] else "none"
        targets = ", ".join(step["target_ids"]) if step["target_ids"] else "none"
        lines.extend(
            [
                f"{step['order']}. `{step['action_id']}`",
                f"   - Owner: `{step['owner']}`",
                f"   - Class: `{step['stage_class']}`",
                f"   - Prerequisites: `{prerequisites}`",
                f"   - Targets: `{targets}`",
                f"   - Decision needed: {step['decision_needed']}",
                f"   - Navigation instruction: {step['instruction']}",
                f"   - Runs commands now: `{step['runs_commands_now']}`",
                f"   - Authorizes execution now: `{step['authorizes_execution_now']}`",
                "",
            ]
        )
    lines.extend(["## Review Session Hints", ""])
    for item in note["review_session_hints"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Issues", ""])
    if note["issues"]:
        for issue in note["issues"]:
            lines.append(f"- {issue}")
    else:
        lines.append("- None")
    lines.extend(["", "## Claim Boundary", ""])
    for item in note["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--digest", default=str(DEFAULT_DIGEST.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    note = build_note(repo_path(args.digest))
    json_path = output_dir / "final_submission_manual_review_shortest_path_note.json"
    md_path = output_dir / "final_submission_manual_review_shortest_path_note.md"
    json_path.write_text(json.dumps(note, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(note, md_path)
    print(
        json.dumps(
            {"ok": not note["issues"], **note["summary"], "json": rel(json_path), "markdown": rel(md_path)},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not note["issues"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
