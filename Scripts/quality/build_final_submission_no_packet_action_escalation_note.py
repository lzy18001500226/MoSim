#!/usr/bin/env python3
"""Build a static escalation note for no-packet final-submission actions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AUTHORIZATION_INDEX = (
    ROOT
    / "Results/static_audits/final_submission_execution_authorization_blocker_20260610"
    / "final_submission_execution_authorization_blocker_index.json"
)
DEFAULT_ACTION_MAP = (
    ROOT
    / "Results/static_audits/final_submission_reviewer_action_map_20260610"
    / "final_submission_reviewer_action_map.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_no_packet_action_escalation_20260610"

ACTION_ESCALATION = {
    "A2-provide-pdf-engine": {
        "escalation_class": "environment_dependency",
        "why_no_packet": "PDF engine installation or exposure is a local environment action, not a report/content review answer.",
        "separate_authorization_needed": "approve installing or exposing a specific PDF engine, or keep PDF export blocked",
        "forbidden_without_authorization": [
            "Do not install PDF tooling.",
            "Do not change PATH or persistent environment settings.",
            "Do not run final PDF export.",
        ],
    },
    "A4-create-reviewed-final-artifacts": {
        "escalation_class": "final_artifact_creation",
        "why_no_packet": "Creating reviewed PDFs and demo_video.mp4 is output generation, not a reviewer-packet decision field.",
        "separate_authorization_needed": "approve the specific final artifact creation step after upstream human decisions pass",
        "forbidden_without_authorization": [
            "Do not create Results/submission final outputs.",
            "Do not overwrite candidate final artifacts.",
            "Do not record, render, or export final media.",
        ],
    },
    "A5-rerun-readiness-gates": {
        "escalation_class": "post_change_gate_rerun",
        "why_no_packet": "Readiness gate reruns are only meaningful after A1-A4 state changes or artifacts change.",
        "separate_authorization_needed": "authorize rerunning the relevant gate chain after an upstream decision or artifact state changes",
        "forbidden_without_authorization": [
            "Do not treat unchanged gate reruns as progress.",
            "Do not run downstream gates to imply approval.",
            "Do not mark final submission ready from stale inputs.",
        ],
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


def by_action(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(item.get("action_id", "")): item for item in records if item.get("action_id")}


def target_references(index: dict[str, Any]) -> dict[str, list[str]]:
    refs: dict[str, list[str]] = {}
    for target in index.get("execution_target_authorization_blockers", []):
        if not isinstance(target, dict):
            continue
        target_id = str(target.get("target_id", ""))
        for action in target.get("no_packet_actions", []):
            if isinstance(action, dict):
                refs.setdefault(str(action.get("action_id", "")), []).append(target_id)
    return {action_id: sorted(set(targets)) for action_id, targets in refs.items() if action_id}


def build_note(authorization_index_path: Path, action_map_path: Path) -> dict[str, Any]:
    authorization_index = read_json(authorization_index_path)
    action_map = read_json(action_map_path)
    action_lookup = by_action(action_map.get("actions", []))
    target_lookup = target_references(authorization_index)
    rows: list[dict[str, Any]] = []
    issues: list[str] = []

    for action_id in sorted(ACTION_ESCALATION):
        action = action_lookup.get(action_id)
        if action is None:
            issues.append(f"missing no-packet action in action map: {action_id}")
            continue
        guidance = ACTION_ESCALATION[action_id]
        rows.append(
            {
                "action_id": action_id,
                "priority": action.get("priority", 0),
                "owner": action.get("decision_owner", ""),
                "decision_needed": action.get("decision_needed", ""),
                "decision_artifact": action.get("decision_artifact", ""),
                "review_artifact_count": len(action.get("review_artifacts", [])),
                "missing_review_artifact_count": len(action.get("missing_review_artifacts", [])),
                "rerun_after_decision_count": len(action.get("rerun_after_decision", [])),
                "referenced_by_execution_targets": target_lookup.get(action_id, []),
                "referenced_target_count": len(target_lookup.get(action_id, [])),
                "escalation_class": guidance["escalation_class"],
                "why_no_packet": guidance["why_no_packet"],
                "separate_authorization_needed": guidance["separate_authorization_needed"],
                "forbidden_without_authorization": guidance["forbidden_without_authorization"],
                "reviewer_packet_created_now": False,
                "automated_execution_allowed": False,
                "runs_commands_now": False,
                "authorizes_execution_now": False,
                "generates_final_outputs": False,
                "final_acceptance": False,
            }
        )

    return {
        "note_id": "final_submission_no_packet_action_escalation_note_20260610",
        "status": "no_packet_action_escalation_note_not_execution",
        "sources": {
            "execution_authorization_blocker_index": rel(authorization_index_path),
            "reviewer_action_map": rel(action_map_path),
        },
        "summary": {
            "no_packet_action_count": len(rows),
            "environment_dependency_count": sum(1 for row in rows if row["escalation_class"] == "environment_dependency"),
            "final_artifact_creation_count": sum(1 for row in rows if row["escalation_class"] == "final_artifact_creation"),
            "post_change_gate_rerun_count": sum(1 for row in rows if row["escalation_class"] == "post_change_gate_rerun"),
            "total_referenced_target_count": sum(row["referenced_target_count"] for row in rows),
            "missing_review_artifact_count": sum(row["missing_review_artifact_count"] for row in rows),
            "issue_count": len(issues),
            "automated_execution_allowed": False,
            "reviewer_packet_created_now": False,
            "answers_questions_now": False,
            "edits_decision_artifacts_now": False,
            "runs_commands_now": False,
            "authorizes_execution_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "no_packet_actions": rows,
        "issues": issues,
        "claim_boundary": [
            "This no-packet action escalation note is a static review artifact only.",
            "It explains why A2, A4, and A5 need separate authorization.",
            "It does not create reviewer packets.",
            "It does not answer reviewer questions.",
            "It does not edit decision artifacts.",
            "It does not install tools.",
            "It does not create final artifacts.",
            "It does not rerun readiness gates.",
            "It does not authorize execution.",
            "It does not generate final outputs or final acceptance.",
        ],
    }


def write_markdown(note: dict[str, Any], path: Path) -> None:
    summary = note["summary"]
    lines = [
        "# Final Submission No-Packet Action Escalation Note, 2026-06-10",
        "",
        f"Status: `{note['status']}`",
        "",
        "## Summary",
        "",
        f"- No-packet actions: `{summary['no_packet_action_count']}`",
        f"- Environment dependencies: `{summary['environment_dependency_count']}`",
        f"- Final artifact creation actions: `{summary['final_artifact_creation_count']}`",
        f"- Post-change gate reruns: `{summary['post_change_gate_rerun_count']}`",
        f"- Referenced execution targets: `{summary['total_referenced_target_count']}`",
        f"- Missing review artifacts: `{summary['missing_review_artifact_count']}`",
        f"- Issues: `{summary['issue_count']}`",
        f"- Reviewer packet created now: `{summary['reviewer_packet_created_now']}`",
        f"- Runs commands now: `{summary['runs_commands_now']}`",
        f"- Authorizes execution now: `{summary['authorizes_execution_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## No-Packet Actions",
        "",
    ]
    for row in note["no_packet_actions"]:
        lines.extend(
            [
                f"### {row['action_id']}",
                "",
                f"- Escalation class: `{row['escalation_class']}`",
                f"- Owner: `{row['owner']}`",
                f"- Decision needed: {row['decision_needed']}",
                f"- Referenced targets: `{', '.join(row['referenced_by_execution_targets'])}`",
                f"- Why no packet: {row['why_no_packet']}",
                f"- Separate authorization needed: {row['separate_authorization_needed']}",
                f"- Reviewer packet created now: `{row['reviewer_packet_created_now']}`",
                f"- Runs commands now: `{row['runs_commands_now']}`",
                "",
            ]
        )
    lines.extend(["## Issues", ""])
    if note["issues"]:
        for item in note["issues"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines.extend(["", "## Claim Boundary", ""])
    for item in note["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authorization-index", default=str(DEFAULT_AUTHORIZATION_INDEX.relative_to(ROOT)))
    parser.add_argument("--action-map", default=str(DEFAULT_ACTION_MAP.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    note = build_note(repo_path(args.authorization_index), repo_path(args.action_map))
    json_path = output_dir / "final_submission_no_packet_action_escalation_note.json"
    md_path = output_dir / "final_submission_no_packet_action_escalation_note.md"
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
