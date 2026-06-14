#!/usr/bin/env python3
"""Build a static guide for reviewing final-submission human decisions.

The guide explains how to inspect A1/A3/A6 pending decisions without approving
or executing anything. It is not a checklist executor.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PACKET = (
    ROOT
    / "Results/static_audits/final_submission_human_review_decision_packet_20260610"
    / "final_submission_human_review_decision_packet_template.json"
)
DEFAULT_REVIEWER_MAP = (
    ROOT
    / "Results/static_audits/final_submission_reviewer_action_map_20260610"
    / "final_submission_reviewer_action_map.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_human_review_guide_20260610"


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


def build_step(action_id: str, decision: dict[str, Any], reviewer_action: dict[str, Any]) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "decision_owner": decision.get("decision_owner", ""),
        "current_decision": decision.get("decision", ""),
        "approved": decision.get("approved"),
        "decision_needed": decision.get("decision_needed", ""),
        "decision_artifact": decision.get("decision_artifact", ""),
        "review_artifacts": decision.get("review_artifacts", []),
        "rerun_after_review": reviewer_action.get("rerun_after_decision", []),
        "editable_fields": [
            "decision",
            "approved",
            "decided_at",
            "narrowed_scope_notes",
            "review_notes",
        ],
        "forbidden_without_separate_gate": [
            "execution_flags.applies_report_source_edits_now",
            "execution_flags.authorizes_pdf_export_now",
            "execution_flags.authorizes_demo_video_recording_now",
            "execution_flags.writes_canonical_acceptance_packet_now",
            "execution_flags.generates_final_outputs",
            "execution_flags.final_acceptance",
        ],
    }


def build_guide(packet_path: Path, reviewer_map_path: Path) -> dict[str, Any]:
    packet = read_json(packet_path)
    reviewer_map = read_json(reviewer_map_path)
    decisions = packet.get("template", {}).get("decisions", {})
    reviewer_actions = {
        str(action.get("action_id")): action
        for action in reviewer_map.get("actions", [])
        if isinstance(action, dict) and action.get("action_id")
    }
    steps = [
        build_step(action_id, decision, reviewer_actions.get(action_id, {}))
        for action_id, decision in decisions.items()
        if isinstance(decision, dict)
    ]
    return {
        "guide_id": "final_submission_human_review_guide_20260610",
        "status": "human_review_guide_not_execution",
        "source_decision_packet": rel(packet_path),
        "source_reviewer_action_map": rel(reviewer_map_path),
        "summary": {
            "review_step_count": len(steps),
            "pending_decision_count": sum(1 for step in steps if step["current_decision"] == "pending_review"),
            "automated_execution_allowed": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "review_steps": steps,
        "review_sequence": [
            "Open the listed review artifacts for the action.",
            "Record human/PMO notes in the pending decision packet template.",
            "Keep execution flags false unless separate upstream gates pass and the user/PMO explicitly authorizes execution.",
            "Run the listed rerun commands after any decision artifact changes.",
            "Rebuild the readiness chain, refresh order, and static audit index after review artifacts change.",
        ],
        "claim_boundary": [
            "This guide is explanatory only.",
            "It does not edit decision artifacts.",
            "It does not approve decisions.",
            "It does not execute rerun commands.",
            "It does not export PDFs, record video, edit report source, or write PMO final acceptance.",
        ],
    }


def write_markdown(guide: dict[str, Any], path: Path) -> None:
    summary = guide["summary"]
    lines = [
        "# Final Submission Human Review Guide, 2026-06-10",
        "",
        f"Status: `{guide['status']}`",
        "",
        "## Summary",
        "",
        f"- Review steps: `{summary['review_step_count']}`",
        f"- Pending decisions: `{summary['pending_decision_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Review Sequence",
        "",
    ]
    for index, item in enumerate(guide["review_sequence"], start=1):
        lines.append(f"{index}. {item}")
    lines.extend(["", "## Review Steps", ""])
    for step in guide["review_steps"]:
        lines.extend(
            [
                f"### {step['action_id']}",
                "",
                f"- Owner: `{step['decision_owner']}`",
                f"- Current decision: `{step['current_decision']}`",
                f"- Approved: `{step['approved']}`",
                f"- Decision artifact: `{step['decision_artifact'] or 'none'}`",
                "- Review artifacts:",
            ]
        )
        for artifact in step["review_artifacts"]:
            lines.append(f"  - `{artifact}`")
        lines.append("- Rerun after review:")
        for command in step["rerun_after_review"]:
            lines.append(f"  - `{command}`")
        lines.append("- Forbidden without separate gate:")
        for field in step["forbidden_without_separate_gate"]:
            lines.append(f"  - `{field}`")
        lines.append("")
    lines.extend(["## Claim Boundary", ""])
    for item in guide["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decision-packet", default=str(DEFAULT_PACKET.relative_to(ROOT)))
    parser.add_argument("--reviewer-action-map", default=str(DEFAULT_REVIEWER_MAP.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    guide = build_guide(repo_path(args.decision_packet), repo_path(args.reviewer_action_map))
    json_path = output_dir / "final_submission_human_review_guide.json"
    md_path = output_dir / "final_submission_human_review_guide.md"
    json_path.write_text(json.dumps(guide, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(guide, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "guide_json": rel(json_path),
                "guide_markdown": rel(md_path),
                "review_step_count": guide["summary"]["review_step_count"],
                "pending_decision_count": guide["summary"]["pending_decision_count"],
                "automated_execution_allowed": guide["summary"]["automated_execution_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
