#!/usr/bin/env python3
"""Build a static reviewer packet index for pending final-submission decisions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DECISION_PACKET = (
    ROOT
    / "Results/static_audits/final_submission_human_review_decision_packet_20260610"
    / "final_submission_human_review_decision_packet_template.json"
)
DEFAULT_ANSWER_SHEET = (
    ROOT
    / "Results/static_audits/final_submission_manual_review_answer_sheet_20260610"
    / "final_submission_manual_review_answer_sheet_template.json"
)
DEFAULT_RERUN_MATRIX = (
    ROOT
    / "Results/static_audits/final_submission_post_review_rerun_matrix_20260610"
    / "final_submission_post_review_rerun_matrix.json"
)
DEFAULT_ACTION_MAP = (
    ROOT
    / "Results/static_audits/final_submission_reviewer_action_map_20260610"
    / "final_submission_reviewer_action_map.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_reviewer_packet_index_20260610"


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


def decision_entries(packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    template = packet.get("template", {})
    if not isinstance(template, dict):
        return {}
    decisions = template.get("decisions", {})
    return decisions if isinstance(decisions, dict) else {}


def file_record(path_value: str) -> dict[str, Any]:
    if not path_value:
        return {"path": "", "exists": True, "required": False}
    return {
        "path": path_value,
        "exists": repo_path(path_value).exists(),
        "required": True,
    }


def answer_fields(section: dict[str, Any]) -> list[dict[str, Any]]:
    fields = section.get("answer_fields", [])
    if not isinstance(fields, list):
        return []
    return [
        {
            "field_path": str(field.get("field_path", "")),
            "human_choice_required": bool(field.get("human_choice_required", False)),
            "copy_to_decision_artifact": str(field.get("copy_to_decision_artifact", "")),
            "proposed_value": str(field.get("proposed_value", "")),
        }
        for field in fields
        if isinstance(field, dict)
    ]


def build_packet_index(
    decision_packet_path: Path,
    answer_sheet_path: Path,
    rerun_matrix_path: Path,
    action_map_path: Path,
) -> dict[str, Any]:
    decision_packet = read_json(decision_packet_path)
    answer_sheet = read_json(answer_sheet_path)
    rerun_matrix = read_json(rerun_matrix_path)
    action_map = read_json(action_map_path)

    decisions = decision_entries(decision_packet)
    answer_sections = by_action(answer_sheet.get("sections", []))
    rerun_rows = by_action(rerun_matrix.get("rows", []))
    action_rows = by_action(action_map.get("actions", []))
    packets: list[dict[str, Any]] = []
    issues: list[str] = []

    for action_id, decision in decisions.items():
        answer = answer_sections.get(action_id, {})
        rerun = rerun_rows.get(action_id, {})
        action = action_rows.get(action_id, {})
        review_artifacts = [
            file_record(str(path))
            for path in decision.get("review_artifacts", [])
        ]
        minimum_open_files = answer.get("minimum_open_files", [])
        if isinstance(minimum_open_files, list):
            review_artifacts.extend(
                {
                    "path": str(item.get("path", "")),
                    "exists": bool(item.get("exists", False)),
                    "required": True,
                }
                for item in minimum_open_files
                if isinstance(item, dict)
            )
        unique_review_artifacts: dict[str, dict[str, Any]] = {}
        for artifact in review_artifacts:
            path = str(artifact.get("path", ""))
            if path:
                unique_review_artifacts[path] = artifact
        fields = answer_fields(answer)
        rerun_commands = [
            str(command)
            for command in rerun.get("rerun_commands_after_separate_review_edit", [])
        ]
        if not answer:
            issues.append(f"missing answer-sheet section for {action_id}")
        if not rerun:
            issues.append(f"missing rerun matrix row for {action_id}")
        missing_files = [
            artifact["path"]
            for artifact in unique_review_artifacts.values()
            if artifact.get("required") and not artifact.get("exists")
        ]
        if missing_files:
            issues.append(f"{action_id} missing review files: {', '.join(missing_files)}")
        packets.append(
            {
                "action_id": action_id,
                "decision": decision.get("decision", ""),
                "approved": bool(decision.get("approved", False)),
                "decision_owner": decision.get("decision_owner", ""),
                "decision_needed": decision.get("decision_needed", ""),
                "decision_artifact": decision.get("decision_artifact", ""),
                "source_blocker_count": decision.get("source_blocker_count", 0),
                "action_priority": action.get("priority"),
                "review_artifacts": list(unique_review_artifacts.values()),
                "review_artifact_count": len(unique_review_artifacts),
                "answer_fields": fields,
                "answer_field_count": len(fields),
                "required_answer_field_count": sum(1 for field in fields if field["human_choice_required"]),
                "post_review_rerun_readiness": rerun.get("rerun_readiness", ""),
                "post_review_rerun_commands": rerun_commands,
                "post_review_rerun_command_count": len(rerun_commands),
                "execution_still_requires": rerun.get("execution_still_requires", []),
                "forbidden_actions": rerun.get("forbidden_actions", []),
                "fills_answers_now": False,
                "copies_answers_now": False,
                "edits_decision_artifacts_now": False,
                "runs_rerun_commands_now": False,
                "approves_or_executes_now": False,
            }
        )

    summary = {
        "packet_count": len(packets),
        "pending_packet_count": sum(1 for packet in packets if packet["decision"] == "pending_review"),
        "total_review_artifact_count": sum(packet["review_artifact_count"] for packet in packets),
        "total_answer_field_count": sum(packet["answer_field_count"] for packet in packets),
        "required_answer_field_count": sum(packet["required_answer_field_count"] for packet in packets),
        "total_rerun_command_count": sum(packet["post_review_rerun_command_count"] for packet in packets),
        "issue_count": len(issues),
        "automated_execution_allowed": False,
        "fills_answers_now": False,
        "copies_answers_now": False,
        "edits_decision_artifacts_now": False,
        "runs_rerun_commands_now": False,
        "generates_final_outputs": False,
        "final_acceptance": False,
    }
    return {
        "index_id": "final_submission_reviewer_packet_index_20260610",
        "status": "reviewer_packet_index_not_execution",
        "sources": {
            "human_review_decision_packet": rel(decision_packet_path),
            "manual_review_answer_sheet": rel(answer_sheet_path),
            "post_review_rerun_matrix": rel(rerun_matrix_path),
            "reviewer_action_map": rel(action_map_path),
        },
        "summary": summary,
        "review_packets": packets,
        "issues": issues,
        "claim_boundary": [
            "This reviewer packet index is a static navigation artifact only.",
            "It does not fill answer-sheet fields.",
            "It does not copy answers into decision artifacts.",
            "It does not edit decision templates.",
            "It does not approve decisions.",
            "It does not run post-review rerun commands.",
            "It does not apply report-source edits.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(index: dict[str, Any], path: Path) -> None:
    summary = index["summary"]
    lines = [
        "# Final Submission Reviewer Packet Index, 2026-06-10",
        "",
        f"Status: `{index['status']}`",
        "",
        "## Summary",
        "",
        f"- Packets: `{summary['packet_count']}`",
        f"- Pending packets: `{summary['pending_packet_count']}`",
        f"- Review artifacts: `{summary['total_review_artifact_count']}`",
        f"- Answer fields: `{summary['total_answer_field_count']}`",
        f"- Required answer fields: `{summary['required_answer_field_count']}`",
        f"- Rerun commands: `{summary['total_rerun_command_count']}`",
        f"- Issues: `{summary['issue_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Fills answers now: `{summary['fills_answers_now']}`",
        f"- Copies answers now: `{summary['copies_answers_now']}`",
        f"- Edits decision artifacts now: `{summary['edits_decision_artifacts_now']}`",
        f"- Runs rerun commands now: `{summary['runs_rerun_commands_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Review Packets",
        "",
    ]
    for packet in index["review_packets"]:
        lines.extend(
            [
                f"### {packet['action_id']}",
                "",
                f"- Decision: `{packet['decision']}`",
                f"- Decision artifact: `{packet['decision_artifact']}`",
                f"- Review artifacts: `{packet['review_artifact_count']}`",
                f"- Answer fields: `{packet['answer_field_count']}`",
                f"- Required answer fields: `{packet['required_answer_field_count']}`",
                f"- Rerun commands: `{packet['post_review_rerun_command_count']}`",
                f"- Runs rerun commands now: `{packet['runs_rerun_commands_now']}`",
                "",
            ]
        )
    lines.extend(["## Issues", ""])
    if index["issues"]:
        for issue in index["issues"]:
            lines.append(f"- {issue}")
    else:
        lines.append("- None")
    lines.extend(["", "## Claim Boundary", ""])
    for item in index["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decision-packet", default=str(DEFAULT_DECISION_PACKET.relative_to(ROOT)))
    parser.add_argument("--answer-sheet", default=str(DEFAULT_ANSWER_SHEET.relative_to(ROOT)))
    parser.add_argument("--rerun-matrix", default=str(DEFAULT_RERUN_MATRIX.relative_to(ROOT)))
    parser.add_argument("--action-map", default=str(DEFAULT_ACTION_MAP.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    index = build_packet_index(
        repo_path(args.decision_packet),
        repo_path(args.answer_sheet),
        repo_path(args.rerun_matrix),
        repo_path(args.action_map),
    )
    json_path = output_dir / "final_submission_reviewer_packet_index.json"
    md_path = output_dir / "final_submission_reviewer_packet_index.md"
    json_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(index, md_path)
    print(json.dumps({"ok": not index["issues"], **index["summary"], "json": rel(json_path), "markdown": rel(md_path)}, ensure_ascii=False, indent=2))
    return 0 if not index["issues"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
