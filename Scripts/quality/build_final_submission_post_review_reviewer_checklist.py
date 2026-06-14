#!/usr/bin/env python3
"""Build a static post-review reviewer checklist from review-aid artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CROSSWALK = (
    ROOT
    / "Results/static_audits/final_submission_blocker_question_crosswalk_20260610"
    / "final_submission_blocker_question_crosswalk.json"
)
DEFAULT_GROUPING = (
    ROOT
    / "Results/static_audits/final_submission_post_review_command_grouping_20260610"
    / "final_submission_post_review_command_grouping_index.json"
)
DEFAULT_CRITICAL_PATH = (
    ROOT
    / "Results/static_audits/final_submission_post_review_command_critical_path_20260610"
    / "final_submission_post_review_command_critical_path_index.json"
)
DEFAULT_SHARED_TAIL = (
    ROOT
    / "Results/static_audits/final_submission_post_review_shared_tail_deduplication_20260610"
    / "final_submission_post_review_shared_tail_deduplication_note.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_post_review_reviewer_checklist_20260610"


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


def rows_by_action(crosswalk: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in crosswalk.get("rows", []):
        if isinstance(row, dict):
            grouped.setdefault(str(row.get("action_id", "")), []).append(row)
    return grouped


def path_by_action(critical_path: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("action_id", "")): item
        for item in critical_path.get("critical_paths", [])
        if isinstance(item, dict)
    }


def grouping_by_action(grouping: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("action_id", "")): item
        for item in grouping.get("action_groups", [])
        if isinstance(item, dict)
    }


def checklist_item(
    action_id: str,
    blocker_rows: list[dict[str, Any]],
    action_path: dict[str, Any],
    action_group: dict[str, Any],
    shared_tail: dict[str, Any],
) -> dict[str, Any]:
    packet_rows = [row for row in blocker_rows if row.get("reviewer_packet_available")]
    question_texts: list[str] = []
    for row in packet_rows:
        for question in row.get("review_questions", []):
            question = str(question)
            if question and question not in question_texts:
                question_texts.append(question)
    decision_artifacts = sorted(
        {
            str(row.get("decision_artifact", ""))
            for row in packet_rows
            if row.get("decision_artifact")
        }
    )
    prefix = list(action_path.get("action_specific_prefix_families", []))
    shared = list(action_path.get("shared_tail_families", []))
    shared_tail_count = int(shared_tail.get("summary", {}).get("shared_tail_family_count", 0))
    return {
        "action_id": action_id,
        "blocker_row_count": len(blocker_rows),
        "reviewer_packet_available": bool(packet_rows),
        "question_count": len(question_texts),
        "review_questions": question_texts,
        "decision_artifacts": decision_artifacts,
        "answer_field_count": sum(int(row.get("answer_field_count", 0)) for row in packet_rows),
        "command_reference_count": int(action_group.get("command_reference_count", 0)),
        "unique_command_count": int(action_group.get("unique_command_count", 0)),
        "action_specific_prefix_families": prefix,
        "shared_tail_families": shared,
        "shared_tail_family_count": len(shared),
        "shared_tail_matches_note": len(shared) == shared_tail_count,
        "review_steps": [
            "Read the blocker rows and reviewer questions.",
            "Record human answers in a separately authorized artifact if the reviewer proceeds.",
            "Edit decision artifacts only in a separately authorized step.",
            "Use action-specific prefix families before the shared tail after separate authorization.",
            "Regenerate downstream static audits only after the relevant decision/edit step is authorized.",
        ],
        "answers_questions_now": False,
        "edits_decision_artifacts_now": False,
        "runs_commands_now": False,
        "applies_transitions_now": False,
    }


def build_checklist(
    crosswalk_path: Path,
    grouping_path: Path,
    critical_path_path: Path,
    shared_tail_path: Path,
) -> dict[str, Any]:
    crosswalk = read_json(crosswalk_path)
    grouping = read_json(grouping_path)
    critical_path = read_json(critical_path_path)
    shared_tail = read_json(shared_tail_path)
    grouped_rows = rows_by_action(crosswalk)
    path_lookup = path_by_action(critical_path)
    group_lookup = grouping_by_action(grouping)
    action_ids = sorted(path_lookup)
    items = [
        checklist_item(
            action_id,
            grouped_rows.get(action_id, []),
            path_lookup.get(action_id, {}),
            group_lookup.get(action_id, {}),
            shared_tail,
        )
        for action_id in action_ids
    ]
    actions_without_packet = [
        action_id
        for action_id, rows in sorted(grouped_rows.items())
        if rows and not any(row.get("reviewer_packet_available") for row in rows)
    ]
    issues = [
        f"{item['action_id']} shared tail does not match shared-tail note"
        for item in items
        if item["reviewer_packet_available"] and not item["shared_tail_matches_note"]
    ]
    return {
        "checklist_id": "final_submission_post_review_reviewer_checklist_20260610",
        "status": "post_review_reviewer_checklist_not_execution",
        "sources": {
            "blocker_question_crosswalk": rel(crosswalk_path),
            "command_grouping_index": rel(grouping_path),
            "command_critical_path_index": rel(critical_path_path),
            "shared_tail_deduplication_note": rel(shared_tail_path),
        },
        "summary": {
            "review_action_count": len(items),
            "actions_without_reviewer_packet_count": len(actions_without_packet),
            "total_blocker_row_count": sum(item["blocker_row_count"] for item in items),
            "total_question_count": sum(item["question_count"] for item in items),
            "total_command_reference_count": sum(item["command_reference_count"] for item in items),
            "shared_tail_family_count": int(shared_tail.get("summary", {}).get("shared_tail_family_count", 0)),
            "issue_count": len(issues),
            "automated_execution_allowed": False,
            "answers_questions_now": False,
            "edits_decision_artifacts_now": False,
            "runs_commands_now": False,
            "applies_transitions_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "review_items": items,
        "actions_without_reviewer_packet": actions_without_packet,
        "issues": issues,
        "claim_boundary": [
            "This reviewer checklist is a static navigation artifact only.",
            "It does not answer reviewer questions.",
            "It does not fill answer-sheet values.",
            "It does not edit decision artifacts.",
            "It does not approve decisions.",
            "It does not run post-review rerun commands.",
            "It does not apply transitions.",
            "It does not apply report-source edits.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(checklist: dict[str, Any], path: Path) -> None:
    summary = checklist["summary"]
    lines = [
        "# Final Submission Post-Review Reviewer Checklist, 2026-06-10",
        "",
        f"Status: `{checklist['status']}`",
        "",
        "## Summary",
        "",
        f"- Review actions: `{summary['review_action_count']}`",
        f"- Actions without reviewer packet: `{summary['actions_without_reviewer_packet_count']}`",
        f"- Blocker rows: `{summary['total_blocker_row_count']}`",
        f"- Questions: `{summary['total_question_count']}`",
        f"- Command references: `{summary['total_command_reference_count']}`",
        f"- Shared-tail families: `{summary['shared_tail_family_count']}`",
        f"- Issues: `{summary['issue_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Answers questions now: `{summary['answers_questions_now']}`",
        f"- Edits decision artifacts now: `{summary['edits_decision_artifacts_now']}`",
        f"- Runs commands now: `{summary['runs_commands_now']}`",
        f"- Applies transitions now: `{summary['applies_transitions_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Review Items",
        "",
    ]
    for item in checklist["review_items"]:
        lines.extend(
            [
                f"### {item['action_id']}",
                "",
                f"- Blocker rows: `{item['blocker_row_count']}`",
                f"- Questions: `{item['question_count']}`",
                f"- Decision artifacts: `{', '.join(item['decision_artifacts'])}`",
                f"- Command references: `{item['command_reference_count']}`",
                f"- Action-specific prefix: `{', '.join(item['action_specific_prefix_families'])}`",
                f"- Shared-tail families: `{item['shared_tail_family_count']}`",
                f"- Answers questions now: `{item['answers_questions_now']}`",
                f"- Edits decision artifacts now: `{item['edits_decision_artifacts_now']}`",
                f"- Runs commands now: `{item['runs_commands_now']}`",
                "",
            ]
        )
    lines.extend(["## Actions Without Reviewer Packet", ""])
    if checklist["actions_without_reviewer_packet"]:
        for action_id in checklist["actions_without_reviewer_packet"]:
            lines.append(f"- `{action_id}`")
    else:
        lines.append("- None")
    lines.extend(["", "## Issues", ""])
    if checklist["issues"]:
        for issue in checklist["issues"]:
            lines.append(f"- {issue}")
    else:
        lines.append("- None")
    lines.extend(["", "## Claim Boundary", ""])
    for item in checklist["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crosswalk", default=str(DEFAULT_CROSSWALK.relative_to(ROOT)))
    parser.add_argument("--grouping", default=str(DEFAULT_GROUPING.relative_to(ROOT)))
    parser.add_argument("--critical-path", default=str(DEFAULT_CRITICAL_PATH.relative_to(ROOT)))
    parser.add_argument("--shared-tail", default=str(DEFAULT_SHARED_TAIL.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    checklist = build_checklist(
        repo_path(args.crosswalk),
        repo_path(args.grouping),
        repo_path(args.critical_path),
        repo_path(args.shared_tail),
    )
    json_path = output_dir / "final_submission_post_review_reviewer_checklist.json"
    md_path = output_dir / "final_submission_post_review_reviewer_checklist.md"
    json_path.write_text(json.dumps(checklist, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(checklist, md_path)
    print(
        json.dumps(
            {"ok": not checklist["issues"], **checklist["summary"], "json": rel(json_path), "markdown": rel(md_path)},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not checklist["issues"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
