#!/usr/bin/env python3
"""Build a static index from blocked execution targets to authorization gates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXECUTION_GATE = (
    ROOT
    / "Results/static_audits/final_submission_human_review_execution_gate_20260610"
    / "final_submission_human_review_execution_gate_summary.json"
)
DEFAULT_ACTION_MAP = (
    ROOT
    / "Results/static_audits/final_submission_reviewer_action_map_20260610"
    / "final_submission_reviewer_action_map.json"
)
DEFAULT_PACKET_INDEX = (
    ROOT
    / "Results/static_audits/final_submission_reviewer_packet_index_20260610"
    / "final_submission_reviewer_packet_index.json"
)
DEFAULT_CRITICAL_PATH = (
    ROOT
    / "Results/static_audits/final_submission_post_review_command_critical_path_20260610"
    / "final_submission_post_review_command_critical_path_index.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_execution_authorization_blocker_20260610"

TARGET_ACTIONS = {
    "report_source_edit": ["A1-approve-or-reject-report-source-edits"],
    "pdf_export": [
        "A1-approve-or-reject-report-source-edits",
        "A2-provide-pdf-engine",
        "A4-create-reviewed-final-artifacts",
        "A5-rerun-readiness-gates",
        "A6-review-final-output-execution-decision",
    ],
    "demo_video_recording": [
        "A3-review-demo-storyboard",
        "A4-create-reviewed-final-artifacts",
        "A5-rerun-readiness-gates",
        "A6-review-final-output-execution-decision",
    ],
    "final_acceptance_packet": [
        "A1-approve-or-reject-report-source-edits",
        "A2-provide-pdf-engine",
        "A3-review-demo-storyboard",
        "A4-create-reviewed-final-artifacts",
        "A5-rerun-readiness-gates",
        "A6-review-final-output-execution-decision",
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


def script_from_command(command: str) -> str:
    parts = command.split()
    if len(parts) >= 2 and parts[0] in {"python", "python3"}:
        return parts[1]
    return ""


def artifact_family(script: str) -> str:
    name = Path(script).name
    if "report_source" in name or "simulation_report_source" in name:
        return "report_source_review"
    if "submission_source_output" in name:
        return "source_output_readiness"
    if "pdf_export" in name:
        return "pdf_export"
    if "demo_video" in name:
        return "demo_video"
    if "final_artifact" in name or "final_submission_artifact" in name:
        return "final_artifact_manifest"
    if "final_acceptance" in name:
        return "final_acceptance_prereq"
    if "final_output_execution" in name:
        return "final_output_execution_decision"
    if "readiness_dashboard" in name:
        return "final_submission_dashboard"
    if "human_action_checklist" in name:
        return "human_action_checklist"
    if "reviewer_action_map" in name:
        return "reviewer_action_map"
    if "human_review_decision_packet" in name:
        return "human_review_decision_packet"
    if "human_review_guide" in name:
        return "human_review_guide"
    if "readiness_chain" in name:
        return "readiness_chain"
    if "refresh_order" in name:
        return "refresh_order"
    if "static_audit_index" in name:
        return "static_audit_index"
    if "blocked_gate_triage" in name:
        return "blocked_gate_triage"
    if "human_decision_diff" in name:
        return "human_decision_diff"
    if "reviewer_quickstart" in name:
        return "reviewer_quickstart"
    if "review_progress_snapshot" in name:
        return "review_progress_snapshot"
    return "other_quality_command"


def by_action(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(item.get("action_id", "")): item for item in records if item.get("action_id")}


def command_families(commands: list[Any]) -> list[str]:
    families: list[str] = []
    for command in commands:
        command_text = str(command)
        family = artifact_family(script_from_command(command_text))
        if family not in families:
            families.append(family)
    return families


def packet_action_record(action_id: str, packet: dict[str, Any], critical_path: dict[str, Any]) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "reviewer_packet_available": True,
        "decision_artifact": packet.get("decision_artifact", ""),
        "decision": packet.get("decision", ""),
        "approved": packet.get("approved", False),
        "decision_needed": packet.get("decision_needed", ""),
        "answer_field_count": int(packet.get("answer_field_count", 0)),
        "required_answer_field_count": int(packet.get("required_answer_field_count", 0)),
        "post_review_rerun_command_count": int(packet.get("post_review_rerun_command_count", 0)),
        "action_specific_prefix_families": list(critical_path.get("action_specific_prefix_families", [])),
        "shared_tail_families": list(critical_path.get("shared_tail_families", [])),
        "execution_still_requires": list(packet.get("execution_still_requires", [])),
        "fills_answers_now": False,
        "copies_answers_now": False,
        "edits_decision_artifacts_now": False,
        "runs_rerun_commands_now": False,
        "approves_or_executes_now": False,
    }


def no_packet_action_record(action_id: str, action: dict[str, Any]) -> dict[str, Any]:
    commands = list(action.get("rerun_after_decision", []))
    return {
        "action_id": action_id,
        "reviewer_packet_available": False,
        "reason": "no_current_reviewer_packet",
        "decision_owner": action.get("decision_owner", ""),
        "decision_needed": action.get("decision_needed", ""),
        "decision_artifact": action.get("decision_artifact", ""),
        "review_artifact_count": len(action.get("review_artifacts", [])),
        "rerun_after_decision_count": len(commands),
        "rerun_after_decision_families": command_families(commands),
        "requires_separate_authorization": True,
        "automated_execution_allowed": False,
        "generates_final_outputs": False,
        "final_acceptance": False,
    }


def build_index(
    execution_gate_path: Path,
    action_map_path: Path,
    packet_index_path: Path,
    critical_path_path: Path,
) -> dict[str, Any]:
    execution_gate = read_json(execution_gate_path)
    action_map = read_json(action_map_path)
    packet_index = read_json(packet_index_path)
    critical_path = read_json(critical_path_path)

    action_lookup = by_action(action_map.get("actions", []))
    packet_lookup = by_action(packet_index.get("review_packets", []))
    critical_path_lookup = by_action(critical_path.get("critical_paths", []))
    packet_action_ids: set[str] = set()
    no_packet_action_ids: set[str] = set()
    issues: list[str] = []
    target_rows: list[dict[str, Any]] = []

    for target in execution_gate.get("execution_targets", []):
        if not isinstance(target, dict):
            continue
        target_id = str(target.get("target_id", ""))
        required_action_ids = TARGET_ACTIONS.get(target_id, [])
        reviewer_packet_actions: list[dict[str, Any]] = []
        no_packet_actions: list[dict[str, Any]] = []
        future_families: list[str] = []

        for action_id in required_action_ids:
            action = action_lookup.get(action_id)
            if action is None:
                issues.append(f"{target_id} references unknown action {action_id}")
                continue
            packet = packet_lookup.get(action_id)
            if packet is not None:
                path_record = critical_path_lookup.get(action_id, {})
                record = packet_action_record(action_id, packet, path_record)
                reviewer_packet_actions.append(record)
                packet_action_ids.add(action_id)
                for family in record["action_specific_prefix_families"] + record["shared_tail_families"]:
                    if family not in future_families:
                        future_families.append(family)
            else:
                record = no_packet_action_record(action_id, action)
                no_packet_actions.append(record)
                no_packet_action_ids.add(action_id)
                for family in record["rerun_after_decision_families"]:
                    if family not in future_families:
                        future_families.append(family)

        target_rows.append(
            {
                "target_id": target_id,
                "label": target.get("label", ""),
                "ready_now": target.get("ready_now", False),
                "blocking_reason_count": target.get("blocking_reason_count", 0),
                "blocking_reasons": target.get("blocking_reasons", []),
                "required_action_ids": required_action_ids,
                "reviewer_packet_action_count": len(reviewer_packet_actions),
                "no_packet_action_count": len(no_packet_actions),
                "reviewer_packet_actions": reviewer_packet_actions,
                "no_packet_actions": no_packet_actions,
                "future_command_families": future_families,
                "future_command_family_count": len(future_families),
                "requires_separate_authorization": True,
                "authorizes_execution_now": False,
                "executes_now": False,
            }
        )

    return {
        "index_id": "final_submission_execution_authorization_blocker_index_20260610",
        "status": "execution_authorization_blocker_index_not_execution",
        "sources": {
            "human_review_execution_gate_summary": rel(execution_gate_path),
            "reviewer_action_map": rel(action_map_path),
            "reviewer_packet_index": rel(packet_index_path),
            "command_critical_path_index": rel(critical_path_path),
        },
        "summary": {
            "execution_target_count": len(target_rows),
            "blocked_execution_target_count": sum(1 for row in target_rows if not row["ready_now"]),
            "unique_reviewer_packet_action_count": len(packet_action_ids),
            "unique_no_packet_action_count": len(no_packet_action_ids),
            "target_action_reference_count": sum(len(row["required_action_ids"]) for row in target_rows),
            "target_without_no_packet_action_count": sum(1 for row in target_rows if row["no_packet_action_count"] == 0),
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
        },
        "execution_target_authorization_blockers": target_rows,
        "unique_reviewer_packet_actions": sorted(packet_action_ids),
        "unique_no_packet_actions": sorted(no_packet_action_ids),
        "issues": issues,
        "claim_boundary": [
            "This authorization blocker index is a static review artifact only.",
            "It maps blocked execution targets to human-review actions and future command families.",
            "It does not create reviewer packets for actions that do not currently have one.",
            "It does not answer reviewer questions.",
            "It does not fill or copy answer-sheet values.",
            "It does not edit decision artifacts.",
            "It does not approve execution.",
            "It does not run commands.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(index: dict[str, Any], path: Path) -> None:
    summary = index["summary"]
    lines = [
        "# Final Submission Execution Authorization Blocker Index, 2026-06-10",
        "",
        f"Status: `{index['status']}`",
        "",
        "## Summary",
        "",
        f"- Execution targets: `{summary['execution_target_count']}`",
        f"- Blocked execution targets: `{summary['blocked_execution_target_count']}`",
        f"- Reviewer-packet actions: `{summary['unique_reviewer_packet_action_count']}`",
        f"- No-packet actions: `{summary['unique_no_packet_action_count']}`",
        f"- Target action references: `{summary['target_action_reference_count']}`",
        f"- Issues: `{summary['issue_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Edits decision artifacts now: `{summary['edits_decision_artifacts_now']}`",
        f"- Runs commands now: `{summary['runs_commands_now']}`",
        f"- Authorizes execution now: `{summary['authorizes_execution_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Execution Targets",
        "",
    ]
    for target in index["execution_target_authorization_blockers"]:
        lines.extend(
            [
                f"### {target['target_id']}",
                "",
                f"- Label: {target['label']}",
                f"- Ready now: `{target['ready_now']}`",
                f"- Blocking reasons: `{target['blocking_reason_count']}`",
                f"- Required actions: `{', '.join(target['required_action_ids'])}`",
                f"- Reviewer-packet actions: `{target['reviewer_packet_action_count']}`",
                f"- No-packet actions: `{target['no_packet_action_count']}`",
                f"- Future command families: `{', '.join(target['future_command_families'])}`",
                f"- Authorizes execution now: `{target['authorizes_execution_now']}`",
                f"- Executes now: `{target['executes_now']}`",
                "",
            ]
        )
    lines.extend(["## No-Packet Actions", ""])
    for action_id in index["unique_no_packet_actions"]:
        lines.append(f"- `{action_id}` requires separate authorization; no current reviewer packet is created here.")
    lines.extend(["", "## Issues", ""])
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
    parser.add_argument("--execution-gate", default=str(DEFAULT_EXECUTION_GATE.relative_to(ROOT)))
    parser.add_argument("--action-map", default=str(DEFAULT_ACTION_MAP.relative_to(ROOT)))
    parser.add_argument("--packet-index", default=str(DEFAULT_PACKET_INDEX.relative_to(ROOT)))
    parser.add_argument("--critical-path", default=str(DEFAULT_CRITICAL_PATH.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    index = build_index(
        repo_path(args.execution_gate),
        repo_path(args.action_map),
        repo_path(args.packet_index),
        repo_path(args.critical_path),
    )
    json_path = output_dir / "final_submission_execution_authorization_blocker_index.json"
    md_path = output_dir / "final_submission_execution_authorization_blocker_index.md"
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
