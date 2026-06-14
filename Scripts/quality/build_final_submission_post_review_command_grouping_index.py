#!/usr/bin/env python3
"""Group post-review rerun commands by artifact family and decision action."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COVERAGE = (
    ROOT
    / "Results/static_audits/final_submission_post_review_command_plan_coverage_20260610"
    / "final_submission_post_review_command_plan_coverage_check.json"
)
DEFAULT_PACKET_INDEX = (
    ROOT
    / "Results/static_audits/final_submission_reviewer_packet_index_20260610"
    / "final_submission_reviewer_packet_index.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_post_review_command_grouping_20260610"


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


def action_command_counts(packet_index: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    packets = packet_index.get("review_packets", [])
    if not isinstance(packets, list):
        return counts
    for packet in packets:
        if isinstance(packet, dict) and packet.get("action_id"):
            counts[str(packet["action_id"])] = int(packet.get("post_review_rerun_command_count", 0))
    return counts


def build_grouping_index(coverage_path: Path, packet_index_path: Path) -> dict[str, Any]:
    coverage = read_json(coverage_path)
    packet_index = read_json(packet_index_path)
    unique_commands: dict[str, dict[str, Any]] = {}
    family_groups: dict[str, dict[str, Any]] = {}
    action_groups: dict[str, dict[str, Any]] = {}

    transitions = coverage.get("transition_command_coverage", [])
    if not isinstance(transitions, list):
        transitions = []
    for transition in transitions:
        if not isinstance(transition, dict):
            continue
        action_id = str(transition.get("action_id", ""))
        action_group = action_groups.setdefault(
            action_id,
            {
                "action_id": action_id,
                "command_reference_count": 0,
                "unique_command_count": 0,
                "families": {},
                "runs_commands_now": False,
            },
        )
        commands = transition.get("commands", [])
        if not isinstance(commands, list):
            continue
        for command_record in commands:
            if not isinstance(command_record, dict):
                continue
            command = str(command_record.get("command", ""))
            script = str(command_record.get("script", "")) or script_from_command(command)
            family = artifact_family(script)
            action_group["command_reference_count"] += 1
            action_group["families"][family] = action_group["families"].get(family, 0) + 1
            family_group = family_groups.setdefault(
                family,
                {
                    "family": family,
                    "unique_command_count": 0,
                    "command_reference_count": 0,
                    "actions": set(),
                    "commands": [],
                    "runs_commands_now": False,
                },
            )
            family_group["command_reference_count"] += 1
            family_group["actions"].add(action_id)
            if command not in unique_commands:
                unique_commands[command] = {
                    "command": command,
                    "script": script,
                    "family": family,
                    "covered": bool(command_record.get("covered", False)),
                    "actions": set(),
                    "reference_count": 0,
                    "runs_now": False,
                }
                family_group["commands"].append(command)
            unique_commands[command]["actions"].add(action_id)
            unique_commands[command]["reference_count"] += 1

    for command in unique_commands.values():
        command["actions"] = sorted(command["actions"])
    for group in family_groups.values():
        group["actions"] = sorted(group["actions"])
        group["commands"] = sorted(set(group["commands"]))
        group["unique_command_count"] = len(group["commands"])
    for action_id, group in action_groups.items():
        commands_for_action = [
            command
            for command in unique_commands.values()
            if action_id in command["actions"]
        ]
        group["unique_command_count"] = len(commands_for_action)
        group["families"] = dict(sorted(group["families"].items()))

    packet_action_counts = action_command_counts(packet_index)
    action_count_mismatches = [
        {
            "action_id": action_id,
            "packet_index_count": expected,
            "coverage_count": action_groups.get(action_id, {}).get("command_reference_count", 0),
        }
        for action_id, expected in packet_action_counts.items()
        if action_groups.get(action_id, {}).get("command_reference_count", 0) != expected
    ]
    issue_count = len(action_count_mismatches)
    summary = coverage.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}
    result_summary = {
        "transition_count": len(transitions),
        "unique_command_count": len(unique_commands),
        "family_count": len(family_groups),
        "action_count": len(action_groups),
        "total_command_reference_count": sum(group["command_reference_count"] for group in action_groups.values()),
        "coverage_unique_command_count": int(summary.get("unique_command_count", 0)),
        "action_count_mismatch_count": len(action_count_mismatches),
        "issue_count": issue_count,
        "automated_execution_allowed": False,
        "runs_commands_now": False,
        "applies_transitions_now": False,
        "edits_decision_artifacts_now": False,
        "generates_final_outputs": False,
        "final_acceptance": False,
    }
    return {
        "index_id": "final_submission_post_review_command_grouping_20260610",
        "status": "post_review_command_grouping_index_not_execution",
        "sources": {
            "command_plan_coverage": rel(coverage_path),
            "reviewer_packet_index": rel(packet_index_path),
        },
        "summary": result_summary,
        "family_groups": sorted(family_groups.values(), key=lambda item: item["family"]),
        "action_groups": sorted(action_groups.values(), key=lambda item: item["action_id"]),
        "unique_commands": sorted(unique_commands.values(), key=lambda item: item["command"]),
        "action_count_mismatches": action_count_mismatches,
        "issues": [
            f"{item['action_id']} command count mismatch: packet={item['packet_index_count']} coverage={item['coverage_count']}"
            for item in action_count_mismatches
        ],
        "claim_boundary": [
            "This command grouping index is a static navigation artifact only.",
            "It does not run post-review rerun commands.",
            "It does not edit decision artifacts.",
            "It does not approve decisions.",
            "It does not apply transitions.",
            "It does not apply report-source edits.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(index: dict[str, Any], path: Path) -> None:
    summary = index["summary"]
    lines = [
        "# Final Submission Post-Review Command Grouping Index, 2026-06-10",
        "",
        f"Status: `{index['status']}`",
        "",
        "## Summary",
        "",
        f"- Transitions: `{summary['transition_count']}`",
        f"- Unique commands: `{summary['unique_command_count']}`",
        f"- Families: `{summary['family_count']}`",
        f"- Actions: `{summary['action_count']}`",
        f"- Total command references: `{summary['total_command_reference_count']}`",
        f"- Action count mismatches: `{summary['action_count_mismatch_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Runs commands now: `{summary['runs_commands_now']}`",
        f"- Applies transitions now: `{summary['applies_transitions_now']}`",
        f"- Edits decision artifacts now: `{summary['edits_decision_artifacts_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Families",
        "",
    ]
    for group in index["family_groups"]:
        lines.extend(
            [
                f"### {group['family']}",
                "",
                f"- Unique commands: `{group['unique_command_count']}`",
                f"- Command references: `{group['command_reference_count']}`",
                f"- Actions: `{', '.join(group['actions'])}`",
                f"- Runs commands now: `{group['runs_commands_now']}`",
                "",
            ]
        )
    lines.extend(["## Actions", ""])
    for group in index["action_groups"]:
        lines.extend(
            [
                f"### {group['action_id']}",
                "",
                f"- Command references: `{group['command_reference_count']}`",
                f"- Unique commands: `{group['unique_command_count']}`",
                f"- Runs commands now: `{group['runs_commands_now']}`",
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
    parser.add_argument("--coverage", default=str(DEFAULT_COVERAGE.relative_to(ROOT)))
    parser.add_argument("--packet-index", default=str(DEFAULT_PACKET_INDEX.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    index = build_grouping_index(repo_path(args.coverage), repo_path(args.packet_index))
    json_path = output_dir / "final_submission_post_review_command_grouping_index.json"
    md_path = output_dir / "final_submission_post_review_command_grouping_index.md"
    json_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(index, md_path)
    print(json.dumps({"ok": not index["issues"], **index["summary"], "json": rel(json_path), "markdown": rel(md_path)}, ensure_ascii=False, indent=2))
    return 0 if not index["issues"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
