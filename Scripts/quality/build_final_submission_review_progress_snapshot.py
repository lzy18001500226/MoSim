#!/usr/bin/env python3
"""Build a non-executing final-submission review progress snapshot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATIC_INDEX = (
    ROOT
    / "Results/static_audits/final_submission_static_audit_index_20260610"
    / "final_submission_static_audit_index.json"
)
DEFAULT_TRIAGE_MAP = (
    ROOT
    / "Results/static_audits/final_submission_blocked_gate_triage_map_20260610"
    / "final_submission_blocked_gate_triage_map.json"
)
DEFAULT_DIFF_TEMPLATE = (
    ROOT
    / "Results/static_audits/final_submission_human_decision_diff_template_20260610"
    / "final_submission_human_decision_diff_template.json"
)
DEFAULT_QUICKSTART = (
    ROOT
    / "Results/static_audits/final_submission_reviewer_quickstart_20260610"
    / "final_submission_reviewer_quickstart.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_review_progress_snapshot_20260610"


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


def source_status(source_id: str, path: Path, data: dict[str, Any]) -> dict[str, Any]:
    summary = data.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}
    return {
        "source_id": source_id,
        "path": rel(path),
        "status": data.get("status", ""),
        "summary": summary,
    }


def decision_group_summary(diff_template: dict[str, Any]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for group in diff_template.get("decision_groups", []):
        if not isinstance(group, dict):
            continue
        field_changes = group.get("field_changes", [])
        if not isinstance(field_changes, list):
            field_changes = []
        groups.append(
            {
                "decision_group_id": group.get("decision_group_id", ""),
                "owner": group.get("owner", ""),
                "field_change_count": len(field_changes),
                "required_checker_after_edit": group.get("required_checker_after_edit", ""),
            }
        )
    return groups


def review_action_summary(quickstart: dict[str, Any]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for section in quickstart.get("sections", []):
        if not isinstance(section, dict):
            continue
        missing_files = [
            item.get("path", "")
            for item in section.get("minimum_open_files", [])
            if isinstance(item, dict) and item.get("exists") is not True
        ]
        actions.append(
            {
                "action_id": section.get("action_id", ""),
                "decision_owner": section.get("decision_owner", ""),
                "current_decision": section.get("current_decision", ""),
                "decision_needed": section.get("decision_needed", ""),
                "decision_artifact": section.get("decision_artifact", ""),
                "decision_diff_group": section.get("decision_diff_group", ""),
                "missing_open_files": missing_files,
                "approves_or_executes_now": section.get("approves_or_executes_now", False),
            }
        )
    return actions


def review_aid_records(
    triage_path: Path,
    triage_map: dict[str, Any],
    diff_path: Path,
    diff_template: dict[str, Any],
    quickstart_path: Path,
    quickstart: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "aid_id": "blocked_gate_triage_map",
            "path": rel(triage_path),
            "status": triage_map.get("status", ""),
            "purpose": "groups blocked artifacts by blocker class and next human action",
            "key_counts": {
                "blocked_artifact_count": triage_map.get("summary", {}).get("blocked_artifact_count"),
                "blocker_class_count": triage_map.get("summary", {}).get("blocker_class_count"),
                "dashboard_blocker_count": triage_map.get("summary", {}).get("dashboard_blocker_count"),
            },
            "next_use": "use before deciding which human review lane to clear first",
            "approves_or_executes_now": False,
        },
        {
            "aid_id": "human_decision_diff_template",
            "path": rel(diff_path),
            "status": diff_template.get("status", ""),
            "purpose": "lists pending A1/A6 decision fields without editing templates",
            "key_counts": {
                "report_source_field_count": diff_template.get("summary", {}).get("report_source_field_count"),
                "final_output_action_count": diff_template.get("summary", {}).get("final_output_action_count"),
                "final_output_field_count": diff_template.get("summary", {}).get("final_output_field_count"),
            },
            "next_use": "use as the checklist for explicit user or PMO edits to decision templates",
            "approves_or_executes_now": False,
        },
        {
            "aid_id": "reviewer_quickstart",
            "path": rel(quickstart_path),
            "status": quickstart.get("status", ""),
            "purpose": "orders the minimum files for A1/A3/A6 human review",
            "key_counts": {
                "review_action_count": quickstart.get("summary", {}).get("review_action_count"),
                "minimum_open_file_count": quickstart.get("summary", {}).get("minimum_open_file_count"),
                "missing_open_file_count": quickstart.get("summary", {}).get("missing_open_file_count"),
            },
            "next_use": "open these files in order during human review",
            "approves_or_executes_now": False,
        },
    ]


def build_snapshot(
    static_index_path: Path,
    triage_path: Path,
    diff_path: Path,
    quickstart_path: Path,
) -> dict[str, Any]:
    static_index = read_json(static_index_path)
    triage_map = read_json(triage_path)
    diff_template = read_json(diff_path)
    quickstart = read_json(quickstart_path)

    review_actions = review_action_summary(quickstart)
    missing_open_files = sorted(
        {path for action in review_actions for path in action["missing_open_files"] if path}
    )
    aids = review_aid_records(
        triage_path,
        triage_map,
        diff_path,
        diff_template,
        quickstart_path,
        quickstart,
    )
    return {
        "snapshot_id": "final_submission_review_progress_snapshot_20260610",
        "status": "review_progress_snapshot_not_execution",
        "sources": {
            "static_index": source_status("static_index", static_index_path, static_index),
            "blocked_gate_triage_map": source_status("blocked_gate_triage_map", triage_path, triage_map),
            "human_decision_diff_template": source_status(
                "human_decision_diff_template", diff_path, diff_template
            ),
            "reviewer_quickstart": source_status("reviewer_quickstart", quickstart_path, quickstart),
        },
        "summary": {
            "review_aid_count": len(aids),
            "pending_review_action_count": len(review_actions),
            "blocked_artifact_count": triage_map.get("summary", {}).get("blocked_artifact_count", 0),
            "blocker_class_count": triage_map.get("summary", {}).get("blocker_class_count", 0),
            "minimum_open_file_count": quickstart.get("summary", {}).get("minimum_open_file_count", 0),
            "missing_open_file_count": len(missing_open_files),
            "automated_execution_allowed": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "review_aids": aids,
        "decision_groups": decision_group_summary(diff_template),
        "pending_review_actions": review_actions,
        "missing_open_files": missing_open_files,
        "recommended_review_order": quickstart.get("review_order", []),
        "next_non_executing_step": (
            "Human or PMO reviews A1, A3, and A6 using the quickstart and updates "
            "decision templates only in a separately authorized step."
        ),
        "claim_boundary": [
            "This snapshot summarizes existing static review aids only.",
            "It does not change gates, readiness, approval, or decision templates.",
            "It does not apply report-source edits.",
            "It does not execute post-review checkers.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(snapshot: dict[str, Any], path: Path) -> None:
    summary = snapshot["summary"]
    lines = [
        "# Final Submission Review Progress Snapshot, 2026-06-10",
        "",
        f"Status: `{snapshot['status']}`",
        "",
        "## Summary",
        "",
        f"- Review aids: `{summary['review_aid_count']}`",
        f"- Pending review actions: `{summary['pending_review_action_count']}`",
        f"- Blocked artifacts: `{summary['blocked_artifact_count']}`",
        f"- Blocker classes: `{summary['blocker_class_count']}`",
        f"- Minimum open files: `{summary['minimum_open_file_count']}`",
        f"- Missing open files: `{summary['missing_open_file_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Review Aids",
        "",
    ]
    for aid in snapshot["review_aids"]:
        lines.extend(
            [
                f"### {aid['aid_id']}",
                "",
                f"- Path: `{aid['path']}`",
                f"- Status: `{aid['status']}`",
                f"- Purpose: {aid['purpose']}",
                f"- Next use: {aid['next_use']}",
                f"- Approves or executes now: `{aid['approves_or_executes_now']}`",
                "- Key counts:",
            ]
        )
        for key, value in aid["key_counts"].items():
            lines.append(f"  - `{key}`: `{value}`")
        lines.append("")
    lines.extend(["## Pending Review Actions", ""])
    for action in snapshot["pending_review_actions"]:
        lines.extend(
            [
                f"- `{action['action_id']}`",
                f"  - Owner: `{action['decision_owner']}`",
                f"  - Current decision: `{action['current_decision']}`",
                f"  - Decision needed: {action['decision_needed']}",
                f"  - Decision artifact: `{action['decision_artifact']}`",
                f"  - Decision diff group: `{action['decision_diff_group']}`",
                f"  - Missing open files: `{len(action['missing_open_files'])}`",
                f"  - Approves or executes now: `{action['approves_or_executes_now']}`",
            ]
        )
    lines.extend(["", "## Decision Groups", ""])
    for group in snapshot["decision_groups"]:
        lines.extend(
            [
                f"- `{group['decision_group_id']}`",
                f"  - Owner: `{group['owner']}`",
                f"  - Field changes: `{group['field_change_count']}`",
                f"  - Required checker after edit: `{group['required_checker_after_edit']}`",
            ]
        )
    lines.extend(["", "## Next Non-Executing Step", "", snapshot["next_non_executing_step"], ""])
    lines.extend(["## Claim Boundary", ""])
    for item in snapshot["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static-index", default=str(DEFAULT_STATIC_INDEX.relative_to(ROOT)))
    parser.add_argument("--triage-map", default=str(DEFAULT_TRIAGE_MAP.relative_to(ROOT)))
    parser.add_argument("--decision-diff-template", default=str(DEFAULT_DIFF_TEMPLATE.relative_to(ROOT)))
    parser.add_argument("--reviewer-quickstart", default=str(DEFAULT_QUICKSTART.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot = build_snapshot(
        repo_path(args.static_index),
        repo_path(args.triage_map),
        repo_path(args.decision_diff_template),
        repo_path(args.reviewer_quickstart),
    )
    json_path = output_dir / "final_submission_review_progress_snapshot.json"
    md_path = output_dir / "final_submission_review_progress_snapshot.md"
    json_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(snapshot, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "snapshot_json": rel(json_path),
                "snapshot_markdown": rel(md_path),
                "review_aid_count": snapshot["summary"]["review_aid_count"],
                "pending_review_action_count": snapshot["summary"]["pending_review_action_count"],
                "blocked_artifact_count": snapshot["summary"]["blocked_artifact_count"],
                "missing_open_file_count": snapshot["summary"]["missing_open_file_count"],
                "automated_execution_allowed": snapshot["summary"]["automated_execution_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
