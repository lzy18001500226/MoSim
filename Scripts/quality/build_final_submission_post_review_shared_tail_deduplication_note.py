#!/usr/bin/env python3
"""Build a static deduplication note for shared post-review rerun families."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CRITICAL_PATH = (
    ROOT
    / "Results/static_audits/final_submission_post_review_command_critical_path_20260610"
    / "final_submission_post_review_command_critical_path_index.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_post_review_shared_tail_deduplication_20260610"


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


def shared_family_records(critical_path: dict[str, Any]) -> list[dict[str, Any]]:
    shared_tail = [str(family) for family in critical_path.get("shared_tail_families", [])]
    critical_paths = [
        item
        for item in critical_path.get("critical_paths", [])
        if isinstance(item, dict)
    ]
    records: list[dict[str, Any]] = []
    for order, family in enumerate(shared_tail, start=1):
        action_ids: list[str] = []
        command_count_by_action: dict[str, int] = {}
        representative_commands: list[str] = []
        for path in critical_paths:
            action_id = str(path.get("action_id", ""))
            for step in path.get("family_steps", []):
                if isinstance(step, dict) and step.get("family") == family and step.get("phase") == "shared_tail":
                    action_ids.append(action_id)
                    command_count_by_action[action_id] = int(step.get("command_count", 0))
                    for command in step.get("commands", []):
                        command = str(command)
                        if command not in representative_commands:
                            representative_commands.append(command)
        records.append(
            {
                "order": order,
                "family": family,
                "action_count": len(set(action_ids)),
                "actions": sorted(set(action_ids)),
                "command_count_by_action": dict(sorted(command_count_by_action.items())),
                "representative_commands": representative_commands,
                "dedupe_guidance": "Review once as a common downstream family after the action-specific prefix has been handled.",
                "run_once_now": False,
                "runs_commands_now": False,
            }
        )
    return records


def build_note(critical_path_path: Path) -> dict[str, Any]:
    critical_path = read_json(critical_path_path)
    records = shared_family_records(critical_path)
    action_count = int(critical_path.get("summary", {}).get("action_count", 0))
    not_shared = [
        {
            "action_id": str(path.get("action_id", "")),
            "action_specific_prefix_families": path.get("action_specific_prefix_families", []),
        }
        for path in critical_path.get("critical_paths", [])
        if isinstance(path, dict)
    ]
    issue_count = sum(1 for record in records if record["action_count"] != action_count)
    return {
        "note_id": "final_submission_post_review_shared_tail_deduplication_20260610",
        "status": "post_review_shared_tail_deduplication_note_not_execution",
        "source_critical_path_index": rel(critical_path_path),
        "summary": {
            "action_count": action_count,
            "shared_tail_family_count": len(records),
            "shared_tail_action_coverage_issue_count": issue_count,
            "action_specific_prefix_group_count": len(not_shared),
            "automated_execution_allowed": False,
            "runs_commands_now": False,
            "applies_transitions_now": False,
            "edits_decision_artifacts_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "shared_tail_families": records,
        "action_specific_prefixes_not_deduped": not_shared,
        "deduplication_rules": [
            "Only shared-tail families are deduplication candidates.",
            "Action-specific prefixes remain action-scoped and must not be collapsed across A1/A3/A6.",
            "This note is for reviewer navigation only; it does not authorize running a command once or many times.",
            "Any future rerun still requires separate human/PMO authorization and current refresh-order checks.",
        ],
        "issues": [
            f"{record['family']} does not appear in all action paths"
            for record in records
            if record["action_count"] != action_count
        ],
        "claim_boundary": [
            "This shared-tail note is a static review-aid artifact only.",
            "It does not run post-review rerun commands.",
            "It does not deduplicate executed work now.",
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


def write_markdown(note: dict[str, Any], path: Path) -> None:
    summary = note["summary"]
    lines = [
        "# Final Submission Post-Review Shared-Tail Deduplication Note, 2026-06-10",
        "",
        f"Status: `{note['status']}`",
        "",
        "## Summary",
        "",
        f"- Actions: `{summary['action_count']}`",
        f"- Shared-tail families: `{summary['shared_tail_family_count']}`",
        f"- Shared-tail coverage issues: `{summary['shared_tail_action_coverage_issue_count']}`",
        f"- Action-specific prefix groups: `{summary['action_specific_prefix_group_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Runs commands now: `{summary['runs_commands_now']}`",
        f"- Applies transitions now: `{summary['applies_transitions_now']}`",
        f"- Edits decision artifacts now: `{summary['edits_decision_artifacts_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Deduplication Rules",
        "",
    ]
    for rule in note["deduplication_rules"]:
        lines.append(f"- {rule}")
    lines.extend(["", "## Shared-Tail Families", ""])
    for record in note["shared_tail_families"]:
        lines.extend(
            [
                f"{record['order']}. `{record['family']}`",
                f"   - Actions: `{', '.join(record['actions'])}`",
                f"   - Action count: `{record['action_count']}`",
                f"   - Representative commands: `{len(record['representative_commands'])}`",
                f"   - Runs commands now: `{record['runs_commands_now']}`",
            ]
        )
    lines.extend(["", "## Action-Specific Prefixes Not Deduped", ""])
    for prefix in note["action_specific_prefixes_not_deduped"]:
        families = ", ".join(map(str, prefix["action_specific_prefix_families"]))
        lines.append(f"- `{prefix['action_id']}`: `{families}`")
    lines.extend(["", "## Issues", ""])
    if note["issues"]:
        for issue in note["issues"]:
            lines.append(f"- {issue}")
    else:
        lines.append("- None")
    lines.extend(["", "## Claim Boundary", ""])
    for item in note["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--critical-path", default=str(DEFAULT_CRITICAL_PATH.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    note = build_note(repo_path(args.critical_path))
    json_path = output_dir / "final_submission_post_review_shared_tail_deduplication_note.json"
    md_path = output_dir / "final_submission_post_review_shared_tail_deduplication_note.md"
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
