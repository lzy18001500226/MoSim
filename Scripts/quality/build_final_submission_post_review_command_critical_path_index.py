#!/usr/bin/env python3
"""Build a static critical-path index for post-review rerun command families."""

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
DEFAULT_GROUPING = (
    ROOT
    / "Results/static_audits/final_submission_post_review_command_grouping_20260610"
    / "final_submission_post_review_command_grouping_index.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_post_review_command_critical_path_20260610"


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


def command_family_map(grouping: dict[str, Any]) -> dict[str, str]:
    commands = grouping.get("unique_commands", [])
    if not isinstance(commands, list):
        return {}
    mapping: dict[str, str] = {}
    for command in commands:
        if isinstance(command, dict) and command.get("command"):
            mapping[str(command["command"])] = str(command.get("family", "unknown_family"))
    return mapping


def ordered_family_steps(commands: list[dict[str, Any]], family_by_command: dict[str, str]) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    for command_record in commands:
        if not isinstance(command_record, dict):
            continue
        command = str(command_record.get("command", ""))
        family = family_by_command.get(command, "unknown_family")
        if steps and steps[-1]["family"] == family:
            steps[-1]["commands"].append(command)
            steps[-1]["command_count"] += 1
            steps[-1]["all_commands_covered"] = bool(steps[-1]["all_commands_covered"] and command_record.get("covered", False))
            continue
        steps.append(
            {
                "order": len(steps) + 1,
                "family": family,
                "command_count": 1,
                "commands": [command],
                "all_commands_covered": bool(command_record.get("covered", False)),
                "runs_now": False,
            }
        )
    return steps


def longest_common_suffix(paths: list[list[str]]) -> list[str]:
    if not paths:
        return []
    suffix: list[str] = []
    min_length = min(len(path) for path in paths)
    for offset in range(1, min_length + 1):
        values = {path[-offset] for path in paths}
        if len(values) != 1:
            break
        suffix.append(values.pop())
    return list(reversed(suffix))


def build_critical_path_index(coverage_path: Path, grouping_path: Path) -> dict[str, Any]:
    coverage = read_json(coverage_path)
    grouping = read_json(grouping_path)
    family_by_command = command_family_map(grouping)
    transition_records = [
        item
        for item in coverage.get("transition_command_coverage", [])
        if isinstance(item, dict)
    ]
    raw_paths: list[dict[str, Any]] = []
    family_sequences: list[list[str]] = []
    issues: list[str] = []

    for transition in transition_records:
        commands = transition.get("commands", [])
        if not isinstance(commands, list):
            commands = []
        steps = ordered_family_steps(commands, family_by_command)
        unknown_commands = [
            command
            for command in commands
            if isinstance(command, dict) and str(command.get("command", "")) not in family_by_command
        ]
        if unknown_commands:
            issues.append(f"{transition.get('action_id', '')} has commands missing from grouping index")
        if transition.get("runs_rerun_commands_now") is not False:
            issues.append(f"{transition.get('action_id', '')} runs_rerun_commands_now must remain false")
        if transition.get("applies_transition_now") is not False:
            issues.append(f"{transition.get('action_id', '')} applies_transition_now must remain false")
        family_sequence = [step["family"] for step in steps]
        family_sequences.append(family_sequence)
        raw_paths.append(
            {
                "action_id": str(transition.get("action_id", "")),
                "transition_id": str(transition.get("transition_id", "")),
                "command_reference_count": int(transition.get("command_count", len(commands))),
                "covered_command_count": int(transition.get("covered_command_count", 0)),
                "family_sequence": family_sequence,
                "family_steps": steps,
                "runs_rerun_commands_now": False,
                "applies_transition_now": False,
            }
        )

    shared_tail = longest_common_suffix(family_sequences)
    critical_paths: list[dict[str, Any]] = []
    for path in raw_paths:
        sequence = path["family_sequence"]
        prefix_length = len(sequence) - len(shared_tail)
        family_steps = []
        for step in path["family_steps"]:
            phase = "action_specific_prefix" if step["order"] <= prefix_length else "shared_tail"
            family_steps.append({**step, "phase": phase})
        path = {
            **path,
            "family_step_count": len(sequence),
            "action_specific_prefix_families": sequence[:prefix_length],
            "shared_tail_families": shared_tail,
            "family_steps": family_steps,
            "automated_execution_allowed": False,
        }
        critical_paths.append(path)

    grouping_summary = grouping.get("summary", {})
    if not isinstance(grouping_summary, dict):
        grouping_summary = {}
    coverage_summary = coverage.get("summary", {})
    if not isinstance(coverage_summary, dict):
        coverage_summary = {}
    action_specific_families = [
        family
        for path in critical_paths
        for family in path["action_specific_prefix_families"]
    ]
    result_summary = {
        "action_count": len(critical_paths),
        "critical_path_count": len(critical_paths),
        "family_count": int(grouping_summary.get("family_count", 0)),
        "unique_command_count": int(grouping_summary.get("unique_command_count", 0)),
        "total_command_reference_count": int(coverage_summary.get("total_command_reference_count", 0)),
        "total_family_step_count": sum(path["family_step_count"] for path in critical_paths),
        "shared_tail_family_count": len(shared_tail),
        "action_specific_prefix_step_count": len(action_specific_families),
        "unique_action_specific_family_count": len(set(action_specific_families)),
        "issue_count": len(issues),
        "automated_execution_allowed": False,
        "runs_commands_now": False,
        "applies_transitions_now": False,
        "edits_decision_artifacts_now": False,
        "generates_final_outputs": False,
        "final_acceptance": False,
    }
    return {
        "index_id": "final_submission_post_review_command_critical_path_20260610",
        "status": "post_review_command_critical_path_index_not_execution",
        "sources": {
            "command_plan_coverage": rel(coverage_path),
            "command_grouping_index": rel(grouping_path),
        },
        "summary": result_summary,
        "shared_tail_families": shared_tail,
        "critical_paths": critical_paths,
        "issues": issues,
        "claim_boundary": [
            "This critical-path index is a static navigation artifact only.",
            "It groups already-listed future rerun commands into family order.",
            "It does not run post-review rerun commands.",
            "It does not choose live resource scheduling.",
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
        "# Final Submission Post-Review Command Critical-Path Index, 2026-06-10",
        "",
        f"Status: `{index['status']}`",
        "",
        "## Summary",
        "",
        f"- Actions: `{summary['action_count']}`",
        f"- Critical paths: `{summary['critical_path_count']}`",
        f"- Families: `{summary['family_count']}`",
        f"- Unique commands: `{summary['unique_command_count']}`",
        f"- Total command references: `{summary['total_command_reference_count']}`",
        f"- Total family steps: `{summary['total_family_step_count']}`",
        f"- Shared tail families: `{summary['shared_tail_family_count']}`",
        f"- Action-specific prefix steps: `{summary['action_specific_prefix_step_count']}`",
        f"- Unique action-specific families: `{summary['unique_action_specific_family_count']}`",
        f"- Issues: `{summary['issue_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Runs commands now: `{summary['runs_commands_now']}`",
        f"- Applies transitions now: `{summary['applies_transitions_now']}`",
        f"- Edits decision artifacts now: `{summary['edits_decision_artifacts_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Shared Tail",
        "",
    ]
    for index_number, family in enumerate(index["shared_tail_families"], start=1):
        lines.append(f"{index_number}. `{family}`")
    lines.extend(["", "## Critical Paths", ""])
    for critical_path in index["critical_paths"]:
        lines.extend(
            [
                f"### {critical_path['action_id']}",
                "",
                f"- Family steps: `{critical_path['family_step_count']}`",
                f"- Command references: `{critical_path['command_reference_count']}`",
                f"- Action-specific prefix: `{', '.join(critical_path['action_specific_prefix_families'])}`",
                f"- Shared tail: `{', '.join(critical_path['shared_tail_families'])}`",
                f"- Runs commands now: `{critical_path['runs_rerun_commands_now']}`",
                f"- Applies transition now: `{critical_path['applies_transition_now']}`",
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
    parser.add_argument("--grouping", default=str(DEFAULT_GROUPING.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    index = build_critical_path_index(repo_path(args.coverage), repo_path(args.grouping))
    json_path = output_dir / "final_submission_post_review_command_critical_path_index.json"
    md_path = output_dir / "final_submission_post_review_command_critical_path_index.md"
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
