#!/usr/bin/env python3
"""Build a static human-review status packet skeleton.

The skeleton summarizes which review fields remain intentionally blank and
which upstream artifacts must change before any final-output execution can be
requested. It does not fill answers, edit decision templates, run commands, or
authorize final-output execution.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ANSWER_SHEET = (
    ROOT
    / "Results/static_audits/final_submission_manual_review_answer_sheet_20260610"
    / "final_submission_manual_review_answer_sheet.template.json"
)
DEFAULT_EXECUTION_GATE = (
    ROOT
    / "Results/static_audits/final_submission_human_review_execution_gate_20260610"
    / "final_submission_human_review_execution_gate_summary.json"
)
DEFAULT_AUTHORIZATION_BLOCKERS = (
    ROOT
    / "Results/static_audits/final_submission_execution_authorization_blocker_20260610"
    / "final_submission_execution_authorization_blocker_index.json"
)
DEFAULT_DASHBOARD = (
    ROOT
    / "Results/static_audits/final_submission_readiness_dashboard_20260610"
    / "final_submission_readiness_dashboard.json"
)
DEFAULT_OPEN_FILE_BUNDLE = (
    ROOT
    / "Results/static_audits/final_submission_open_file_shortest_path_bundle_20260610"
    / "final_submission_open_file_shortest_path_bundle.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_human_review_status_packet_skeleton_20260610"


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


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def is_placeholder(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("<") and value.endswith(">")


def pending_fields_for_section(section: dict[str, Any]) -> list[dict[str, Any]]:
    pending_fields: list[dict[str, Any]] = []
    for field in as_list(section.get("answer_fields")):
        if not isinstance(field, dict):
            continue
        proposed_value = field.get("proposed_value")
        current_value = field.get("current_value")
        intentionally_blank = (
            is_placeholder(proposed_value)
            or is_placeholder(current_value)
            or current_value == ""
            or current_value == []
            or (
                field.get("human_choice_required") is True
                and field.get("field_path", "").endswith(".approved")
                and current_value is False
            )
        )
        if intentionally_blank:
            pending_fields.append(
                {
                    "field_path": field.get("field_path", ""),
                    "current_value": current_value,
                    "proposed_value": proposed_value,
                    "human_choice_required": bool(field.get("human_choice_required", False)),
                    "copy_to_decision_artifact": field.get("copy_to_decision_artifact", ""),
                    "intentionally_blank": True,
                }
            )
    return pending_fields


def blocked_targets_by_action(authorization_blockers: dict[str, Any]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for target in as_list(authorization_blockers.get("execution_target_authorization_blockers")):
        if not isinstance(target, dict):
            continue
        target_id = str(target.get("target_id", ""))
        for action_id in as_list(target.get("required_action_ids")):
            mapping.setdefault(str(action_id), []).append(target_id)
    return mapping


def no_packet_actions(authorization_blockers: dict[str, Any]) -> list[str]:
    return [str(item) for item in as_list(authorization_blockers.get("unique_no_packet_actions")) if str(item)]


def reviewer_actions(authorization_blockers: dict[str, Any]) -> list[str]:
    return [str(item) for item in as_list(authorization_blockers.get("unique_reviewer_packet_actions")) if str(item)]


def build_skeleton(
    answer_sheet_path: Path,
    execution_gate_path: Path,
    authorization_blockers_path: Path,
    dashboard_path: Path,
    open_file_bundle_path: Path,
) -> dict[str, Any]:
    answer_sheet = read_json(answer_sheet_path)
    execution_gate = read_json(execution_gate_path)
    authorization_blockers = read_json(authorization_blockers_path)
    dashboard = read_json(dashboard_path)
    open_file_bundle = read_json(open_file_bundle_path)

    issues: list[str] = []
    expected_statuses = {
        "answer_sheet": (answer_sheet, "manual_review_answer_sheet_template_not_execution"),
        "execution_gate": (execution_gate, "human_review_execution_gate_summary_not_execution"),
        "authorization_blockers": (authorization_blockers, "execution_authorization_blocker_index_not_execution"),
        "dashboard": (dashboard, "static_dashboard_not_final_submission_acceptance"),
        "open_file_bundle": (open_file_bundle, "open_file_shortest_path_bundle_not_execution"),
    }
    for label, (artifact, expected) in expected_statuses.items():
        if artifact.get("status") != expected:
            issues.append(f"{label} status is not {expected}")

    answer_summary = as_dict(answer_sheet.get("summary"))
    gate_summary = as_dict(execution_gate.get("summary"))
    blocker_summary = as_dict(authorization_blockers.get("summary"))
    dashboard_summary = as_dict(dashboard.get("summary"))
    open_file_summary = as_dict(open_file_bundle.get("summary"))
    if int(open_file_summary.get("issue_count", 0)) != 0:
        issues.append("open-file shortest-path bundle has open issues")
    if int(blocker_summary.get("issue_count", 0)) != 0:
        issues.append("authorization blocker index has open issues")

    target_map = blocked_targets_by_action(authorization_blockers)
    review_actions: list[dict[str, Any]] = []
    pending_field_count = 0
    required_pending_field_count = 0
    review_question_count = 0
    minimum_open_file_count = 0

    for section in as_list(answer_sheet.get("sections")):
        if not isinstance(section, dict):
            continue
        action_id = str(section.get("action_id", ""))
        pending_fields = pending_fields_for_section(section)
        required_fields = [field for field in pending_fields if field["human_choice_required"]]
        pending_field_count += len(pending_fields)
        required_pending_field_count += len(required_fields)
        questions = [str(item) for item in as_list(section.get("review_questions"))]
        open_files = [item for item in as_list(section.get("minimum_open_files")) if isinstance(item, dict)]
        review_question_count += len(questions)
        minimum_open_file_count += len(open_files)
        review_actions.append(
            {
                "action_id": action_id,
                "decision_owner": section.get("decision_owner", ""),
                "current_decision": section.get("current_decision", ""),
                "decision_needed": section.get("decision_needed", ""),
                "decision_artifact": section.get("decision_artifact", ""),
                "pending_field_count": len(pending_fields),
                "required_pending_field_count": len(required_fields),
                "review_question_count": len(questions),
                "minimum_open_file_count": len(open_files),
                "blocked_execution_targets": sorted(set(target_map.get(action_id, []))),
                "intentionally_blank_fields": pending_fields,
                "execution_still_requires": [str(item) for item in as_list(section.get("execution_still_requires"))],
                "copies_answers_now": False,
                "edits_decision_artifact_now": False,
                "approves_or_executes_now": False,
            }
        )

    dashboard_blockers = as_list(dashboard.get("blockers"))
    upstream_change_requirements = [
        {
            "class": "human_review_answers",
            "required_change": "A1/A3/A6 review fields must be filled by an explicit human or PMO review step.",
            "current_state": f"{required_pending_field_count} required fields remain intentionally blank.",
        },
        {
            "class": "decision_artifacts",
            "required_change": "Decision templates must be edited only in a separately authorized step after review.",
            "current_state": "Current skeleton does not edit report-source or final-output decision templates.",
        },
        {
            "class": "no_packet_dependencies",
            "required_change": "A2/A4/A5 no-packet dependencies must be satisfied by the owning manual/operator action.",
            "current_state": ", ".join(no_packet_actions(authorization_blockers)),
        },
        {
            "class": "readiness_dashboard",
            "required_change": "All blocking readiness gates must turn ready before final-output execution can be requested.",
            "current_state": f"{dashboard_summary.get('blocking_gate_count', 0)} gates and {dashboard_summary.get('blocker_count', 0)} blockers remain blocked.",
        },
    ]

    skeleton = {
        "packet_skeleton_id": "final_submission_human_review_status_packet_skeleton_20260610",
        "status": "human_review_status_packet_skeleton_not_execution",
        "sources": {
            "manual_review_answer_sheet": rel(answer_sheet_path),
            "human_review_execution_gate_summary": rel(execution_gate_path),
            "execution_authorization_blocker_index": rel(authorization_blockers_path),
            "readiness_dashboard": rel(dashboard_path),
            "open_file_shortest_path_bundle": rel(open_file_bundle_path),
        },
        "summary": {
            "review_action_count": len(review_actions),
            "reviewer_packet_action_count": len(reviewer_actions(authorization_blockers)),
            "no_packet_action_count": len(no_packet_actions(authorization_blockers)),
            "pending_field_count": pending_field_count,
            "required_pending_field_count": required_pending_field_count,
            "review_question_count": review_question_count,
            "minimum_open_file_count": minimum_open_file_count,
            "unique_open_file_count": int(open_file_summary.get("unique_open_file_count", 0)),
            "blocked_execution_target_count": int(gate_summary.get("blocked_execution_target_count", 0)),
            "dashboard_blocking_gate_count": int(gate_summary.get("dashboard_blocking_gate_count", 0)),
            "dashboard_blocker_count": len(dashboard_blockers),
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
        "review_actions": review_actions,
        "no_packet_actions": no_packet_actions(authorization_blockers),
        "upstream_change_requirements": upstream_change_requirements,
        "dashboard_blockers": dashboard_blockers,
        "issues": issues,
        "claim_boundary": [
            "This status packet skeleton is a static review-state artifact only.",
            "It intentionally leaves human-review fields blank.",
            "It does not answer review questions.",
            "It does not fill or copy answer-sheet values.",
            "It does not edit report-source or final-output decision templates.",
            "It does not approve or reject decisions.",
            "It does not create reviewer packets for no-packet actions.",
            "It does not run post-review commands.",
            "It does not install PDF tooling.",
            "It does not create final artifacts.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
            "It does not run live tools or visible-thread dispatch.",
        ],
    }

    # Cross-check the source answer-sheet summary after constructing the packet.
    if pending_field_count != int(answer_summary.get("answer_field_count", pending_field_count)):
        issues.append(
            f"pending field count mismatch: skeleton={pending_field_count} answer_sheet={answer_summary.get('answer_field_count')}"
        )
    if required_pending_field_count != int(answer_summary.get("required_answer_field_count", required_pending_field_count)):
        issues.append(
            "required pending field count mismatch: "
            f"skeleton={required_pending_field_count} answer_sheet={answer_summary.get('required_answer_field_count')}"
        )
    skeleton["summary"]["issue_count"] = len(issues)
    return skeleton


def write_markdown(skeleton: dict[str, Any], path: Path) -> None:
    summary = skeleton["summary"]
    lines = [
        "# Final Submission Human-Review Status Packet Skeleton, 2026-06-10",
        "",
        f"Status: `{skeleton['status']}`",
        "",
        "## Summary",
        "",
        f"- Review actions: `{summary['review_action_count']}`",
        f"- Reviewer-packet actions: `{summary['reviewer_packet_action_count']}`",
        f"- No-packet actions: `{summary['no_packet_action_count']}`",
        f"- Pending fields: `{summary['pending_field_count']}`",
        f"- Required pending fields: `{summary['required_pending_field_count']}`",
        f"- Review questions: `{summary['review_question_count']}`",
        f"- Minimum open files: `{summary['minimum_open_file_count']}`",
        f"- Unique open files: `{summary['unique_open_file_count']}`",
        f"- Blocked execution targets: `{summary['blocked_execution_target_count']}`",
        f"- Dashboard blocking gates: `{summary['dashboard_blocking_gate_count']}`",
        f"- Dashboard blockers: `{summary['dashboard_blocker_count']}`",
        f"- Issues: `{summary['issue_count']}`",
        f"- Fills answers now: `{summary['fills_answers_now']}`",
        f"- Edits decision artifacts now: `{summary['edits_decision_artifacts_now']}`",
        f"- Runs commands now: `{summary['runs_commands_now']}`",
        f"- Authorizes execution now: `{summary['authorizes_execution_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Review Actions",
        "",
    ]
    for action in skeleton["review_actions"]:
        lines.extend(
            [
                f"### {action['action_id']}",
                "",
                f"- Decision owner: `{action['decision_owner']}`",
                f"- Current decision: `{action['current_decision']}`",
                f"- Pending fields: `{action['pending_field_count']}`",
                f"- Required pending fields: `{action['required_pending_field_count']}`",
                f"- Review questions: `{action['review_question_count']}`",
                f"- Minimum open files: `{action['minimum_open_file_count']}`",
                f"- Blocked execution targets: `{', '.join(action['blocked_execution_targets']) or 'none'}`",
                "",
                "Intentionally blank fields:",
                "",
            ]
        )
        for field in action["intentionally_blank_fields"]:
            lines.append(f"- `{field['field_path']}` required=`{field['human_choice_required']}`")
        lines.extend(["", "Execution still requires:", ""])
        for item in action["execution_still_requires"]:
            lines.append(f"- {item}")
        lines.append("")

    lines.extend(["## No-Packet Actions", ""])
    for action_id in skeleton["no_packet_actions"]:
        lines.append(f"- `{action_id}`")
    lines.extend(["", "## Upstream Change Requirements", ""])
    for item in skeleton["upstream_change_requirements"]:
        lines.append(f"- `{item['class']}`: {item['required_change']} Current: {item['current_state']}")
    lines.extend(["", "## Issues", ""])
    if skeleton["issues"]:
        for issue in skeleton["issues"]:
            lines.append(f"- {issue}")
    else:
        lines.append("- None")
    lines.extend(["", "## Claim Boundary", ""])
    for item in skeleton["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--answer-sheet", default=str(DEFAULT_ANSWER_SHEET.relative_to(ROOT)))
    parser.add_argument("--execution-gate", default=str(DEFAULT_EXECUTION_GATE.relative_to(ROOT)))
    parser.add_argument("--authorization-blockers", default=str(DEFAULT_AUTHORIZATION_BLOCKERS.relative_to(ROOT)))
    parser.add_argument("--dashboard", default=str(DEFAULT_DASHBOARD.relative_to(ROOT)))
    parser.add_argument("--open-file-bundle", default=str(DEFAULT_OPEN_FILE_BUNDLE.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    skeleton = build_skeleton(
        repo_path(args.answer_sheet),
        repo_path(args.execution_gate),
        repo_path(args.authorization_blockers),
        repo_path(args.dashboard),
        repo_path(args.open_file_bundle),
    )
    json_path = output_dir / "final_submission_human_review_status_packet_skeleton.json"
    md_path = output_dir / "final_submission_human_review_status_packet_skeleton.md"
    json_path.write_text(json.dumps(skeleton, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(skeleton, md_path)
    print(
        json.dumps(
            {"ok": not skeleton["issues"], **skeleton["summary"], "json": rel(json_path), "markdown": rel(md_path)},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not skeleton["issues"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
