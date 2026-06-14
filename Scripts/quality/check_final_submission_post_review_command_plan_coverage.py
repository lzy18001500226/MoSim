#!/usr/bin/env python3
"""Check post-review command-plan coverage without running commands."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TRANSITION_PLAN = (
    ROOT
    / "Results/static_audits/final_submission_post_review_state_transition_plan_20260610"
    / "final_submission_post_review_state_transition_plan.json"
)
DEFAULT_OUTPUT_JSON = (
    ROOT
    / "Results/static_audits/final_submission_post_review_command_plan_coverage_20260610"
    / "final_submission_post_review_command_plan_coverage_check.json"
)
DEFAULT_OUTPUT_MD = (
    ROOT
    / "Results/static_audits/final_submission_post_review_command_plan_coverage_20260610"
    / "final_submission_post_review_command_plan_coverage_check.md"
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


def script_from_command(command: str) -> str:
    parts = command.split()
    if len(parts) < 2:
        return ""
    if parts[0] not in {"python", "python3"}:
        return ""
    return parts[1]


def command_record(command: str) -> dict[str, Any]:
    script = script_from_command(command)
    script_path = repo_path(script) if script else ROOT / "__missing_script__"
    issues: list[str] = []
    if not script:
        issues.append("unsupported_command_shape")
    elif not script_path.exists():
        issues.append("script_missing")
    elif script_path.suffix != ".py":
        issues.append("script_not_python")
    elif not rel(script_path).startswith("Scripts/quality/"):
        issues.append("script_outside_quality_dir")
    return {
        "command": command,
        "script": script,
        "script_exists": bool(script and script_path.exists()),
        "issues": issues,
        "covered": not issues,
        "runs_now": False,
    }


def build_coverage(transition_plan_path: Path) -> dict[str, Any]:
    transition_plan = read_json(transition_plan_path)
    transitions = [item for item in transition_plan.get("transitions", []) if isinstance(item, dict)]
    transition_records: list[dict[str, Any]] = []
    all_commands: list[str] = []
    issues: list[str] = []

    for transition in transitions:
        summary = transition.get("rerun_command_summary", {})
        if not isinstance(summary, dict):
            summary = {}
        commands = [str(command) for command in summary.get("commands", [])]
        all_commands.extend(commands)
        records = [command_record(command) for command in commands]
        missing = [record for record in records if not record["covered"]]
        if transition.get("runs_rerun_commands_now") is not False:
            issues.append(f"{transition.get('transition_id', '')} runs_rerun_commands_now must remain false")
        if transition.get("applies_transition_now") is not False:
            issues.append(f"{transition.get('transition_id', '')} applies_transition_now must remain false")
        for record in missing:
            issues.append(f"{transition.get('transition_id', '')} command issue: {record['command']} -> {record['issues']}")
        transition_records.append(
            {
                "transition_id": transition.get("transition_id", ""),
                "action_id": transition.get("action_id", ""),
                "command_count": len(records),
                "covered_command_count": sum(1 for record in records if record["covered"]),
                "missing_or_invalid_command_count": len(missing),
                "commands": records,
                "runs_rerun_commands_now": transition.get("runs_rerun_commands_now", False),
                "applies_transition_now": transition.get("applies_transition_now", False),
            }
        )

    unique_commands = sorted(set(all_commands))
    summary = transition_plan.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}
    if summary.get("runs_rerun_commands_now") is not False:
        issues.append("transition_plan.summary.runs_rerun_commands_now must remain false")
    if summary.get("applies_transitions_now") is not False:
        issues.append("transition_plan.summary.applies_transitions_now must remain false")

    return {
        "ok": not issues,
        "check_id": "final_submission_post_review_command_plan_coverage_20260610",
        "status": "post_review_command_plan_coverage_check_not_execution",
        "source_transition_plan": rel(transition_plan_path),
        "summary": {
            "transition_count": len(transitions),
            "total_command_reference_count": len(all_commands),
            "unique_command_count": len(unique_commands),
            "covered_unique_command_count": sum(
                1 for command in unique_commands if command_record(command)["covered"]
            ),
            "issue_count": len(issues),
            "automated_execution_allowed": False,
            "runs_rerun_commands_now": False,
            "applies_transitions_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "transition_command_coverage": transition_records,
        "unique_commands": [command_record(command) for command in unique_commands],
        "issues": issues,
        "claim_boundary": [
            "This checker validates command references only.",
            "It does not run listed rerun commands.",
            "It does not edit decision templates.",
            "It does not approve decisions.",
            "It does not apply state transitions.",
            "It does not apply report-source edits.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(result: dict[str, Any], path: Path) -> None:
    summary = result["summary"]
    lines = [
        "# Final Submission Post-Review Command Plan Coverage, 2026-06-10",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Summary",
        "",
        f"- OK: `{result['ok']}`",
        f"- Transitions: `{summary['transition_count']}`",
        f"- Total command references: `{summary['total_command_reference_count']}`",
        f"- Unique commands: `{summary['unique_command_count']}`",
        f"- Covered unique commands: `{summary['covered_unique_command_count']}`",
        f"- Issues: `{summary['issue_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Runs rerun commands now: `{summary['runs_rerun_commands_now']}`",
        f"- Applies transitions now: `{summary['applies_transitions_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Transition Coverage",
        "",
    ]
    for transition in result["transition_command_coverage"]:
        lines.extend(
            [
                f"### {transition['transition_id']}",
                "",
                f"- Action: `{transition['action_id']}`",
                f"- Commands: `{transition['command_count']}`",
                f"- Covered: `{transition['covered_command_count']}`",
                f"- Missing or invalid: `{transition['missing_or_invalid_command_count']}`",
                f"- Runs rerun commands now: `{transition['runs_rerun_commands_now']}`",
                f"- Applies transition now: `{transition['applies_transition_now']}`",
                "",
            ]
        )
    lines.extend(["## Issues", ""])
    if result["issues"]:
        for issue in result["issues"]:
            lines.append(f"- {issue}")
    else:
        lines.append("- None")
    lines.extend(["", "## Claim Boundary", ""])
    for item in result["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transition-plan", default=str(DEFAULT_TRANSITION_PLAN.relative_to(ROOT)))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON.relative_to(ROOT)))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD.relative_to(ROOT)))
    args = parser.parse_args()

    transition_plan_path = repo_path(args.transition_plan)
    result = build_coverage(transition_plan_path)
    output_json = repo_path(args.output_json)
    output_md = repo_path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(result, output_md)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
