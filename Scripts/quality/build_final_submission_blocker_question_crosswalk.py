#!/usr/bin/env python3
"""Build a static blocker-to-review-question crosswalk for final-submission review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DASHBOARD = (
    ROOT
    / "Results/static_audits/final_submission_readiness_dashboard_20260610"
    / "final_submission_readiness_dashboard.json"
)
DEFAULT_HUMAN_ACTIONS = (
    ROOT
    / "Results/static_audits/final_submission_human_action_checklist_20260610"
    / "final_submission_human_action_checklist.json"
)
DEFAULT_ANSWER_SHEET = (
    ROOT
    / "Results/static_audits/final_submission_manual_review_answer_sheet_20260610"
    / "final_submission_manual_review_answer_sheet_template.json"
)
DEFAULT_PACKET_INDEX = (
    ROOT
    / "Results/static_audits/final_submission_reviewer_packet_index_20260610"
    / "final_submission_reviewer_packet_index.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_blocker_question_crosswalk_20260610"


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


def by_action(items: list[Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        if isinstance(item, dict) and item.get("action_id"):
            result[str(item["action_id"])] = item
    return result


def blocker_key(blocker: dict[str, Any]) -> str:
    return f"{blocker.get('gate_id', '')}:{blocker.get('blocker_id', '')}"


def build_crosswalk(
    dashboard_path: Path,
    human_actions_path: Path,
    answer_sheet_path: Path,
    packet_index_path: Path,
) -> dict[str, Any]:
    dashboard = read_json(dashboard_path)
    human_actions = read_json(human_actions_path)
    answer_sheet = read_json(answer_sheet_path)
    packet_index = read_json(packet_index_path)
    action_rows = by_action(human_actions.get("actions", []))
    answer_sections = by_action(answer_sheet.get("sections", []))
    packet_rows = by_action(packet_index.get("review_packets", []))
    rows: list[dict[str, Any]] = []
    missing_packet_action_ids: set[str] = set()

    for action_id, action in action_rows.items():
        answer = answer_sections.get(action_id, {})
        packet = packet_rows.get(action_id, {})
        questions = [str(item) for item in answer.get("review_questions", [])]
        packet_exists = bool(packet)
        if not packet_exists:
            missing_packet_action_ids.add(action_id)
        for blocker in action.get("source_blockers", []):
            if not isinstance(blocker, dict):
                continue
            rows.append(
                {
                    "action_id": action_id,
                    "action_priority": action.get("priority"),
                    "owner": action.get("owner", ""),
                    "blocker_key": blocker_key(blocker),
                    "gate_id": blocker.get("gate_id", ""),
                    "blocker_id": blocker.get("blocker_id", ""),
                    "reason": blocker.get("reason", ""),
                    "needed_action": blocker.get("needed_action", ""),
                    "reviewer_packet_available": packet_exists,
                    "review_questions": questions,
                    "review_question_count": len(questions),
                    "answer_field_count": packet.get("answer_field_count", 0),
                    "decision_artifact": packet.get("decision_artifact", action.get("decision_artifact", "")),
                    "post_review_rerun_command_count": packet.get("post_review_rerun_command_count", 0),
                    "answers_questions_now": False,
                    "edits_decision_artifacts_now": False,
                    "runs_rerun_commands_now": False,
                }
            )

    dashboard_blockers = dashboard.get("blockers", [])
    dashboard_keys = {
        blocker_key(blocker)
        for blocker in dashboard_blockers
        if isinstance(blocker, dict)
    }
    mapped_keys = {row["blocker_key"] for row in rows}
    unmapped_dashboard_blockers = sorted(dashboard_keys - mapped_keys)
    issue_count = 0
    summary = {
        "dashboard_blocker_count": len(dashboard_keys),
        "crosswalk_row_count": len(rows),
        "reviewer_packet_action_count": len(packet_rows),
        "actions_without_reviewer_packet_count": len(missing_packet_action_ids),
        "unmapped_dashboard_blocker_count": len(unmapped_dashboard_blockers),
        "question_backed_row_count": sum(1 for row in rows if row["review_question_count"] > 0),
        "issue_count": issue_count,
        "automated_execution_allowed": False,
        "answers_questions_now": False,
        "edits_decision_artifacts_now": False,
        "runs_rerun_commands_now": False,
        "generates_final_outputs": False,
        "final_acceptance": False,
    }
    return {
        "crosswalk_id": "final_submission_blocker_question_crosswalk_20260610",
        "status": "blocker_question_crosswalk_not_execution",
        "sources": {
            "dashboard": rel(dashboard_path),
            "human_action_checklist": rel(human_actions_path),
            "manual_review_answer_sheet": rel(answer_sheet_path),
            "reviewer_packet_index": rel(packet_index_path),
        },
        "summary": summary,
        "rows": rows,
        "actions_without_reviewer_packet": sorted(missing_packet_action_ids),
        "unmapped_dashboard_blockers": unmapped_dashboard_blockers,
        "claim_boundary": [
            "This crosswalk maps blockers to review questions only.",
            "It does not answer review questions.",
            "It does not fill answer-sheet fields.",
            "It does not edit decision artifacts.",
            "It does not approve decisions.",
            "It does not run rerun commands.",
            "It does not apply report-source edits.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(crosswalk: dict[str, Any], path: Path) -> None:
    summary = crosswalk["summary"]
    lines = [
        "# Final Submission Blocker-To-Question Crosswalk, 2026-06-10",
        "",
        f"Status: `{crosswalk['status']}`",
        "",
        "## Summary",
        "",
        f"- Dashboard blockers: `{summary['dashboard_blocker_count']}`",
        f"- Crosswalk rows: `{summary['crosswalk_row_count']}`",
        f"- Reviewer packet actions: `{summary['reviewer_packet_action_count']}`",
        f"- Actions without reviewer packet: `{summary['actions_without_reviewer_packet_count']}`",
        f"- Unmapped dashboard blockers: `{summary['unmapped_dashboard_blocker_count']}`",
        f"- Question-backed rows: `{summary['question_backed_row_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Answers questions now: `{summary['answers_questions_now']}`",
        f"- Edits decision artifacts now: `{summary['edits_decision_artifacts_now']}`",
        f"- Runs rerun commands now: `{summary['runs_rerun_commands_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Rows",
        "",
    ]
    for row in crosswalk["rows"]:
        lines.extend(
            [
                f"### {row['blocker_key']}",
                "",
                f"- Action: `{row['action_id']}`",
                f"- Reviewer packet available: `{row['reviewer_packet_available']}`",
                f"- Review questions: `{row['review_question_count']}`",
                f"- Decision artifact: `{row['decision_artifact']}`",
                f"- Runs rerun commands now: `{row['runs_rerun_commands_now']}`",
                "",
            ]
        )
    lines.extend(["## Actions Without Reviewer Packet", ""])
    if crosswalk["actions_without_reviewer_packet"]:
        for action_id in crosswalk["actions_without_reviewer_packet"]:
            lines.append(f"- `{action_id}`")
    else:
        lines.append("- None")
    lines.extend(["", "## Claim Boundary", ""])
    for item in crosswalk["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dashboard", default=str(DEFAULT_DASHBOARD.relative_to(ROOT)))
    parser.add_argument("--human-actions", default=str(DEFAULT_HUMAN_ACTIONS.relative_to(ROOT)))
    parser.add_argument("--answer-sheet", default=str(DEFAULT_ANSWER_SHEET.relative_to(ROOT)))
    parser.add_argument("--packet-index", default=str(DEFAULT_PACKET_INDEX.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    crosswalk = build_crosswalk(
        repo_path(args.dashboard),
        repo_path(args.human_actions),
        repo_path(args.answer_sheet),
        repo_path(args.packet_index),
    )
    json_path = output_dir / "final_submission_blocker_question_crosswalk.json"
    md_path = output_dir / "final_submission_blocker_question_crosswalk.md"
    json_path.write_text(json.dumps(crosswalk, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(crosswalk, md_path)
    print(json.dumps({"ok": True, **crosswalk["summary"], "json": rel(json_path), "markdown": rel(md_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
