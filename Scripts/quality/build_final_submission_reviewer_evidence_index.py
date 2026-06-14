#!/usr/bin/env python3
"""Build a static reviewer evidence index for final-submission review.

This index combines A1/A3/A6 reviewer-packet evidence with A2/A4/A5
no-packet escalation evidence. It is a navigation artifact only and does not
fill answers, edit decision templates, run commands, or generate final outputs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ACTION_MAP = (
    ROOT
    / "Results/static_audits/final_submission_reviewer_action_map_20260610"
    / "final_submission_reviewer_action_map.json"
)
DEFAULT_QUICKSTART = (
    ROOT
    / "Results/static_audits/final_submission_reviewer_quickstart_20260610"
    / "final_submission_reviewer_quickstart.json"
)
DEFAULT_PACKET_INDEX = (
    ROOT
    / "Results/static_audits/final_submission_reviewer_packet_index_20260610"
    / "final_submission_reviewer_packet_index.json"
)
DEFAULT_NO_PACKET_NOTE = (
    ROOT
    / "Results/static_audits/final_submission_no_packet_action_escalation_20260610"
    / "final_submission_no_packet_action_escalation_note.json"
)
DEFAULT_FORBIDDEN_GUARD = (
    ROOT
    / "Results/static_audits/final_submission_forbidden_action_guard_20260610"
    / "final_submission_forbidden_action_guard_check.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_reviewer_evidence_index_20260610"

NO_PACKET_NOTE_MD = (
    "Results/static_audits/final_submission_no_packet_action_escalation_20260610/"
    "final_submission_no_packet_action_escalation_note.md"
)
QUICKSTART_MD = (
    "Results/static_audits/final_submission_reviewer_quickstart_20260610/"
    "final_submission_reviewer_quickstart.md"
)
PACKET_INDEX_MD = (
    "Results/static_audits/final_submission_reviewer_packet_index_20260610/"
    "final_submission_reviewer_packet_index.md"
)
FORBIDDEN_GUARD_MD = (
    "Results/static_audits/final_submission_forbidden_action_guard_20260610/"
    "final_submission_forbidden_action_guard_check.md"
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


def by_action(rows: list[dict[str, Any]], action_key: str = "action_id") -> dict[str, dict[str, Any]]:
    return {str(row.get(action_key, "")): row for row in rows if row.get(action_key)}


def append_file(files: list[dict[str, Any]], path_value: str, source: str, required: bool = True) -> None:
    if not path_value:
        return
    normalized = Path(path_value).as_posix()
    if any(item["path"] == normalized for item in files):
        return
    files.append(
        {
            "path": normalized,
            "source": source,
            "required": required,
            "exists": repo_path(normalized).exists(),
        }
    )


def artifact_paths(rows: list[dict[str, Any]], source: str) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for row in rows:
        if isinstance(row, dict):
            append_file(files, str(row.get("path", "")), source, bool(row.get("required", True)))
    return files


def merge_files(*groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for group in groups:
        for item in group:
            append_file(files, str(item.get("path", "")), str(item.get("source", "unknown")), bool(item.get("required", True)))
    return files


def build_index(
    action_map_path: Path,
    quickstart_path: Path,
    packet_index_path: Path,
    no_packet_note_path: Path,
    forbidden_guard_path: Path,
) -> dict[str, Any]:
    action_map = read_json(action_map_path)
    quickstart = read_json(quickstart_path)
    packet_index = read_json(packet_index_path)
    no_packet_note = read_json(no_packet_note_path)
    forbidden_guard = read_json(forbidden_guard_path)

    actions = sorted(action_map.get("actions", []), key=lambda row: int(row.get("priority", 0)))
    quickstart_lookup = by_action(quickstart.get("sections", []))
    packet_lookup = by_action(packet_index.get("review_packets", []))
    no_packet_lookup = by_action(no_packet_note.get("no_packet_actions", []))

    rows: list[dict[str, Any]] = []
    issues: list[str] = []
    unique_paths: set[str] = set()

    for action in actions:
        action_id = str(action.get("action_id", ""))
        if action_id in packet_lookup:
            packet_class = "reviewer_packet"
            packet = packet_lookup[action_id]
            quick = quickstart_lookup.get(action_id, {})
            files = merge_files(
                artifact_paths(action.get("review_artifacts", []), "reviewer_action_map"),
                artifact_paths(packet.get("review_artifacts", []), "reviewer_packet_index"),
                artifact_paths(quick.get("minimum_open_files", []), "reviewer_quickstart"),
            )
            append_file(files, QUICKSTART_MD, "reviewer_quickstart")
            append_file(files, PACKET_INDEX_MD, "reviewer_packet_index")
            decision = packet.get("decision", quick.get("current_decision", "pending_review"))
            approved = packet.get("approved", False)
            answer_field_count = packet.get("answer_field_count", 0)
            required_answer_field_count = packet.get("required_answer_field_count", 0)
            separate_authorization_needed = "; ".join(packet.get("execution_still_requires", []))
            escalation_class = ""
            why_no_packet = ""
            forbidden_without_authorization = packet.get("forbidden_actions", [])
        elif action_id in no_packet_lookup:
            packet_class = "no_packet_escalation"
            note = no_packet_lookup[action_id]
            files = artifact_paths(action.get("review_artifacts", []), "reviewer_action_map")
            append_file(files, NO_PACKET_NOTE_MD, "no_packet_action_escalation_note")
            append_file(files, FORBIDDEN_GUARD_MD, "forbidden_action_guard")
            decision = "requires_separate_authorization"
            approved = False
            answer_field_count = 0
            required_answer_field_count = 0
            separate_authorization_needed = str(note.get("separate_authorization_needed", ""))
            escalation_class = str(note.get("escalation_class", ""))
            why_no_packet = str(note.get("why_no_packet", ""))
            forbidden_without_authorization = note.get("forbidden_without_authorization", [])
        else:
            packet_class = "unknown"
            files = artifact_paths(action.get("review_artifacts", []), "reviewer_action_map")
            decision = "unknown"
            approved = False
            answer_field_count = 0
            required_answer_field_count = 0
            separate_authorization_needed = ""
            escalation_class = ""
            why_no_packet = ""
            forbidden_without_authorization = []
            issues.append(f"action {action_id} is neither reviewer-packet nor no-packet escalation")

        missing_files = [item["path"] for item in files if item["required"] and not item["exists"]]
        if missing_files:
            issues.append(f"{action_id} missing required evidence files: {', '.join(missing_files)}")
        for item in files:
            unique_paths.add(item["path"])

        rows.append(
            {
                "action_id": action_id,
                "priority": action.get("priority", 0),
                "packet_class": packet_class,
                "owner": action.get("decision_owner", action.get("checklist_owner", "")),
                "decision_needed": action.get("decision_needed", ""),
                "decision_artifact": action.get("decision_artifact", ""),
                "decision": decision,
                "approved": approved,
                "answer_field_count": answer_field_count,
                "required_answer_field_count": required_answer_field_count,
                "review_evidence_files": files,
                "review_evidence_file_count": len(files),
                "missing_review_evidence_file_count": len(missing_files),
                "escalation_class": escalation_class,
                "why_no_packet": why_no_packet,
                "separate_authorization_needed": separate_authorization_needed,
                "forbidden_without_authorization": forbidden_without_authorization,
                "fills_answers_now": False,
                "copies_answers_now": False,
                "edits_decision_artifacts_now": False,
                "runs_commands_now": False,
                "authorizes_execution_now": False,
                "generates_final_outputs": False,
                "final_acceptance": False,
            }
        )

    forbidden_summary = forbidden_guard.get("summary", {})
    expected_forbidden = {
        "pdf_export_still_forbidden": True,
        "demo_recording_still_forbidden": True,
        "final_acceptance_still_forbidden": True,
        "live_tools_still_forbidden": True,
        "visible_thread_dispatch_still_forbidden": True,
    }
    for key, expected in expected_forbidden.items():
        if forbidden_summary.get(key) is not expected:
            issues.append(f"forbidden guard summary {key} must be {expected}")

    reviewer_packet_count = sum(1 for row in rows if row["packet_class"] == "reviewer_packet")
    no_packet_count = sum(1 for row in rows if row["packet_class"] == "no_packet_escalation")
    missing_count = sum(row["missing_review_evidence_file_count"] for row in rows)

    return {
        "index_id": "final_submission_reviewer_evidence_index_20260610",
        "status": "reviewer_evidence_index_not_execution",
        "sources": {
            "reviewer_action_map": rel(action_map_path),
            "reviewer_quickstart": rel(quickstart_path),
            "reviewer_packet_index": rel(packet_index_path),
            "no_packet_action_escalation_note": rel(no_packet_note_path),
            "forbidden_action_guard": rel(forbidden_guard_path),
        },
        "summary": {
            "action_count": len(rows),
            "reviewer_packet_action_count": reviewer_packet_count,
            "no_packet_action_count": no_packet_count,
            "unique_review_evidence_file_count": len(unique_paths),
            "missing_review_evidence_file_count": missing_count,
            "issue_count": len(issues),
            "pdf_export_still_forbidden": True,
            "demo_recording_still_forbidden": True,
            "final_acceptance_still_forbidden": True,
            "live_tools_still_forbidden": True,
            "visible_thread_dispatch_still_forbidden": True,
            "automated_execution_allowed": False,
            "fills_answers_now": False,
            "copies_answers_now": False,
            "edits_decision_artifacts_now": False,
            "runs_commands_now": False,
            "authorizes_execution_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "review_actions": rows,
        "issues": issues,
        "claim_boundary": [
            "This reviewer evidence index is a static navigation artifact only.",
            "It does not fill answers.",
            "It does not copy answers into decision artifacts.",
            "It does not edit decision templates.",
            "It does not approve decisions.",
            "It does not install PDF tooling.",
            "It does not create final artifacts.",
            "It does not run commands.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
            "It does not run MWORKS, ROS2, UE, or visible-thread dispatch tools.",
        ],
    }


def write_markdown(index: dict[str, Any], path: Path) -> None:
    summary = index["summary"]
    lines = [
        "# Final Submission Reviewer Evidence Index, 2026-06-10",
        "",
        f"Status: `{index['status']}`",
        "",
        "## Summary",
        "",
        f"- Actions: `{summary['action_count']}`",
        f"- Reviewer-packet actions: `{summary['reviewer_packet_action_count']}`",
        f"- No-packet actions: `{summary['no_packet_action_count']}`",
        f"- Unique review evidence files: `{summary['unique_review_evidence_file_count']}`",
        f"- Missing review evidence files: `{summary['missing_review_evidence_file_count']}`",
        f"- Issues: `{summary['issue_count']}`",
        f"- PDF export still forbidden: `{summary['pdf_export_still_forbidden']}`",
        f"- Demo recording still forbidden: `{summary['demo_recording_still_forbidden']}`",
        f"- Final acceptance still forbidden: `{summary['final_acceptance_still_forbidden']}`",
        f"- Runs commands now: `{summary['runs_commands_now']}`",
        f"- Authorizes execution now: `{summary['authorizes_execution_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Review Actions",
        "",
    ]
    for row in index["review_actions"]:
        lines.extend(
            [
                f"### {row['action_id']}",
                "",
                f"- Class: `{row['packet_class']}`",
                f"- Owner: `{row['owner']}`",
                f"- Decision: `{row['decision']}`",
                f"- Decision needed: {row['decision_needed']}",
                f"- Decision artifact: `{row['decision_artifact'] or 'none'}`",
                f"- Evidence files: `{row['review_evidence_file_count']}`",
                f"- Missing evidence files: `{row['missing_review_evidence_file_count']}`",
            ]
        )
        if row["separate_authorization_needed"]:
            lines.append(f"- Separate authorization needed: {row['separate_authorization_needed']}")
        if row["why_no_packet"]:
            lines.append(f"- Why no packet: {row['why_no_packet']}")
        lines.append("")
        for item in row["review_evidence_files"]:
            lines.append(f"  - `{item['path']}`")
        lines.append("")
    lines.extend(["## Issues", ""])
    if index["issues"]:
        for item in index["issues"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines.extend(["", "## Claim Boundary", ""])
    for item in index["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--action-map", default=str(DEFAULT_ACTION_MAP.relative_to(ROOT)))
    parser.add_argument("--quickstart", default=str(DEFAULT_QUICKSTART.relative_to(ROOT)))
    parser.add_argument("--packet-index", default=str(DEFAULT_PACKET_INDEX.relative_to(ROOT)))
    parser.add_argument("--no-packet-note", default=str(DEFAULT_NO_PACKET_NOTE.relative_to(ROOT)))
    parser.add_argument("--forbidden-guard", default=str(DEFAULT_FORBIDDEN_GUARD.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    index = build_index(
        repo_path(args.action_map),
        repo_path(args.quickstart),
        repo_path(args.packet_index),
        repo_path(args.no_packet_note),
        repo_path(args.forbidden_guard),
    )
    json_path = output_dir / "final_submission_reviewer_evidence_index.json"
    md_path = output_dir / "final_submission_reviewer_evidence_index.md"
    json_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(index, md_path)
    print(
        json.dumps(
            {"ok": not index["issues"], **index["summary"], "json": rel(json_path), "markdown": rel(md_path)},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not index["issues"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
