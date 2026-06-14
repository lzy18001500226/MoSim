#!/usr/bin/env python3
"""Build a pending human-review decision packet template.

This packet groups A1/A3/A6 review decisions into one human-facing draft. It
does not approve, execute, or write canonical PMO final acceptance artifacts.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REVIEWER_MAP = (
    ROOT
    / "Results/static_audits/final_submission_reviewer_action_map_20260610"
    / "final_submission_reviewer_action_map.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_human_review_decision_packet_20260610"
SELF_PATH = ROOT / "Scripts/quality/build_final_submission_human_review_decision_packet_template.py"

REVIEW_DECISION_IDS = [
    "A1-approve-or-reject-report-source-edits",
    "A3-review-demo-storyboard",
    "A6-review-final-output-execution-decision",
]
VALID_DECISIONS = ["pending_review", "approved", "rejected", "narrowed", "needs_revision"]


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


def load_self_module():
    spec = importlib.util.spec_from_file_location("human_review_decision_packet_self", SELF_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load self module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pending_decision(action: dict[str, Any]) -> dict[str, Any]:
    action_id = str(action["action_id"])
    return {
        "action_id": action_id,
        "decision": "pending_review",
        "approved": False,
        "decision_owner": action.get("decision_owner", "<user_or_PMO>"),
        "decided_at": "<ISO8601_after_review>",
        "decision_needed": action.get("decision_needed", ""),
        "decision_artifact": action.get("decision_artifact", ""),
        "review_artifacts": [item["path"] for item in action.get("review_artifacts", []) if item.get("path")],
        "source_blocker_count": action.get("source_blocker_count", 0),
        "narrowed_scope_notes": "",
        "review_notes": "",
        "required_boundaries": [
            "Do not approve report-source edits without explicit human/PMO review.",
            "Do not authorize video recording without storyboard review.",
            "Do not authorize PDF export or final acceptance unless upstream gates pass.",
            "Do not claim final submission ready from this draft packet.",
        ],
    }


def build_template(reviewer_map_path: Path) -> dict[str, Any]:
    reviewer_map = read_json(reviewer_map_path)
    actions = {
        str(item.get("action_id")): item
        for item in reviewer_map.get("actions", [])
        if isinstance(item, dict) and item.get("action_id") in REVIEW_DECISION_IDS
    }
    return {
        "decision_packet_id": "final_submission_human_review_decision_packet_20260610",
        "status": "human_review_decision_packet_pending_review",
        "source_reviewer_action_map": rel(reviewer_map_path),
        "valid_decisions": VALID_DECISIONS,
        "decisions": {action_id: pending_decision(actions[action_id]) for action_id in REVIEW_DECISION_IDS if action_id in actions},
        "execution_flags": {
            "applies_report_source_edits_now": False,
            "authorizes_pdf_export_now": False,
            "authorizes_demo_video_recording_now": False,
            "writes_canonical_acceptance_packet_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
    }


def validate_template(template: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []
    decisions = template.get("decisions", {})
    if not isinstance(decisions, dict):
        issues.append("decisions must be an object")
        decisions = {}
    for action_id in REVIEW_DECISION_IDS:
        item = decisions.get(action_id)
        if not isinstance(item, dict):
            issues.append(f"missing decision for {action_id}")
            continue
        if item.get("decision") not in VALID_DECISIONS:
            issues.append(f"{action_id} decision must be one of {', '.join(VALID_DECISIONS)}")
        if item.get("decision") == "pending_review" and item.get("approved") is not False:
            issues.append(f"{action_id} pending_review must keep approved=false")
        review_artifacts = item.get("review_artifacts", [])
        if not isinstance(review_artifacts, list) or not review_artifacts:
            issues.append(f"{action_id} must list review_artifacts")
        else:
            for artifact in review_artifacts:
                if not repo_path(str(artifact)).exists():
                    issues.append(f"{action_id} review artifact missing: {artifact}")
    flags = template.get("execution_flags", {})
    if not isinstance(flags, dict):
        issues.append("execution_flags must be an object")
        flags = {}
    for key in [
        "applies_report_source_edits_now",
        "authorizes_pdf_export_now",
        "authorizes_demo_video_recording_now",
        "writes_canonical_acceptance_packet_now",
        "generates_final_outputs",
        "final_acceptance",
    ]:
        if flags.get(key) is not False:
            issues.append(f"execution_flags.{key} must remain false")
    return {
        "ok": not issues,
        "status": "human_review_decision_packet_check_not_execution",
        "summary": {
            "decision_count": len(decisions),
            "pending_decision_count": sum(
                1 for item in decisions.values() if isinstance(item, dict) and item.get("decision") == "pending_review"
            ),
            "issue_count": len(issues),
            "warning_count": len(warnings),
            "automated_execution_allowed": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "issues": issues,
        "warnings": warnings,
        "claim_boundary": [
            "This checker validates a pending human-review decision draft only.",
            "It does not approve decisions.",
            "It does not execute commands.",
            "It does not export PDFs, record video, edit report source, or write PMO final acceptance.",
        ],
    }


def build_artifact(reviewer_map_path: Path) -> dict[str, Any]:
    template = build_template(reviewer_map_path)
    validation = validate_template(template)
    return {
        "artifact_id": "final_submission_human_review_decision_packet_20260610",
        "status": "human_review_decision_packet_pending_review_not_execution",
        "template": template,
        "validation": validation,
        "summary": {
            "decision_count": validation["summary"]["decision_count"],
            "pending_decision_count": validation["summary"]["pending_decision_count"],
            "automated_execution_allowed": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "claim_boundary": [
            "This artifact is a draft human-review decision packet.",
            "It does not approve report-source edits.",
            "It does not authorize final output execution.",
            "It does not create final outputs or PMO final acceptance.",
        ],
    }


def write_markdown(artifact: dict[str, Any], path: Path) -> None:
    summary = artifact["summary"]
    validation = artifact["validation"]
    lines = [
        "# Final Submission Human Review Decision Packet Template, 2026-06-10",
        "",
        f"Status: `{artifact['status']}`",
        "",
        "## Summary",
        "",
        f"- Decisions: `{summary['decision_count']}`",
        f"- Pending decisions: `{summary['pending_decision_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Validation",
        "",
        f"- OK: `{validation['ok']}`",
        f"- Issues: `{validation['summary']['issue_count']}`",
        f"- Warnings: `{validation['summary']['warning_count']}`",
        "",
        "## Decisions",
        "",
    ]
    for action_id, decision in artifact["template"]["decisions"].items():
        lines.extend(
            [
                f"### {action_id}",
                "",
                f"- Decision: `{decision['decision']}`",
                f"- Approved: `{decision['approved']}`",
                f"- Owner: `{decision['decision_owner']}`",
                f"- Decision artifact: `{decision['decision_artifact'] or 'none'}`",
                f"- Review artifacts: `{len(decision['review_artifacts'])}`",
                "",
            ]
        )
    lines.extend(["## Claim Boundary", ""])
    for item in artifact["claim_boundary"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Template", "", "```json", json.dumps(artifact["template"], ensure_ascii=False, indent=2), "```"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer-action-map", default=str(DEFAULT_REVIEWER_MAP.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = build_artifact(repo_path(args.reviewer_action_map))
    json_path = output_dir / "final_submission_human_review_decision_packet_template.json"
    md_path = output_dir / "final_submission_human_review_decision_packet_template.md"
    template_path = output_dir / "final_submission_human_review_decision_packet.template.json"
    check_path = output_dir / "final_submission_human_review_decision_packet_check.json"
    json_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    template_path.write_text(json.dumps(artifact["template"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    check_path.write_text(json.dumps(artifact["validation"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(artifact, md_path)
    print(
        json.dumps(
            {
                "ok": artifact["validation"]["ok"],
                "artifact_json": rel(json_path),
                "artifact_markdown": rel(md_path),
                "template": rel(template_path),
                "decision_check": rel(check_path),
                "decision_count": artifact["summary"]["decision_count"],
                "pending_decision_count": artifact["summary"]["pending_decision_count"],
                "automated_execution_allowed": artifact["summary"]["automated_execution_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if artifact["validation"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
