#!/usr/bin/env python3
"""Build a static dependency summary for the human-review status packet skeleton.

This artifact compresses dashboard blockers into prerequisite classes and maps
them back to A1-A6 review actions. It does not answer questions, edit decision
templates, satisfy prerequisites, run commands, or authorize final-output
execution.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATUS_SKELETON = (
    ROOT
    / "Results/static_audits/final_submission_human_review_status_packet_skeleton_20260610"
    / "final_submission_human_review_status_packet_skeleton.json"
)
DEFAULT_AUTHORIZATION_BLOCKERS = (
    ROOT
    / "Results/static_audits/final_submission_execution_authorization_blocker_20260610"
    / "final_submission_execution_authorization_blocker_index.json"
)
DEFAULT_SHORTEST_PATH = (
    ROOT
    / "Results/static_audits/final_submission_manual_review_shortest_path_20260610"
    / "final_submission_manual_review_shortest_path_note.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_status_packet_dependency_summary_20260610"


CLASS_RULES = [
    {
        "class_id": "report_source_review",
        "match": ["report_source", "source_edit", "source_output"],
        "default_action_ids": ["A1-approve-or-reject-report-source-edits"],
    },
    {
        "class_id": "pdf_engine",
        "match": ["pdf_engine", "pdf_export", "pdf"],
        "default_action_ids": ["A2-provide-pdf-engine", "A6-review-final-output-execution-decision"],
    },
    {
        "class_id": "demo_storyboard_and_video",
        "match": ["demo_video", "storyboard"],
        "default_action_ids": [
            "A3-review-demo-storyboard",
            "A4-create-reviewed-final-artifacts",
            "A6-review-final-output-execution-decision",
        ],
    },
    {
        "class_id": "final_artifact_creation",
        "match": ["final_outputs", "final_artifacts", "final_artifact", "artifact"],
        "default_action_ids": ["A4-create-reviewed-final-artifacts"],
    },
    {
        "class_id": "final_output_execution_decision",
        "match": ["authorizes_", "final_output_execution_decision", "execution decision"],
        "default_action_ids": ["A6-review-final-output-execution-decision"],
    },
    {
        "class_id": "post_change_gate_rerun",
        "match": ["rerun", "regenerate", "re-run"],
        "default_action_ids": ["A5-rerun-readiness-gates"],
    },
]

EXPLICIT_BLOCKER_RULES: dict[str, tuple[str, list[str]]] = {
    "report_source_edit_not_approved": (
        "report_source_review",
        ["A1-approve-or-reject-report-source-edits"],
    ),
    "report_source_edit_application_plan_not_ready": (
        "report_source_review",
        ["A1-approve-or-reject-report-source-edits"],
    ),
    "report_source_edit_application_not_applied": (
        "report_source_review",
        ["A1-approve-or-reject-report-source-edits", "A5-rerun-readiness-gates"],
    ),
    "source_output_readiness_blocks_acceptance": (
        "report_source_review",
        ["A1-approve-or-reject-report-source-edits", "A5-rerun-readiness-gates"],
    ),
    "pdf_engine_missing": (
        "pdf_engine",
        ["A2-provide-pdf-engine", "A6-review-final-output-execution-decision"],
    ),
    "pdf_export_not_ready": (
        "pdf_engine",
        ["A2-provide-pdf-engine", "A5-rerun-readiness-gates", "A6-review-final-output-execution-decision"],
    ),
    "manual_storyboard_review_required": (
        "demo_storyboard_and_video",
        ["A3-review-demo-storyboard"],
    ),
    "demo_video_not_recorded": (
        "demo_storyboard_and_video",
        ["A3-review-demo-storyboard", "A4-create-reviewed-final-artifacts", "A6-review-final-output-execution-decision"],
    ),
    "demo_video_recording_not_approved": (
        "demo_storyboard_and_video",
        ["A3-review-demo-storyboard", "A6-review-final-output-execution-decision"],
    ),
    "final_outputs_missing": (
        "final_artifact_creation",
        [
            "A1-approve-or-reject-report-source-edits",
            "A2-provide-pdf-engine",
            "A3-review-demo-storyboard",
            "A4-create-reviewed-final-artifacts",
            "A6-review-final-output-execution-decision",
        ],
    ),
    "final_artifacts_missing": (
        "final_artifact_creation",
        ["A2-provide-pdf-engine", "A4-create-reviewed-final-artifacts", "A5-rerun-readiness-gates"],
    ),
    "final_artifacts_not_ready": (
        "final_artifact_creation",
        ["A4-create-reviewed-final-artifacts", "A5-rerun-readiness-gates"],
    ),
    "authorizes_pdf_export": (
        "final_output_execution_decision",
        ["A6-review-final-output-execution-decision"],
    ),
    "authorizes_demo_video_recording": (
        "final_output_execution_decision",
        ["A6-review-final-output-execution-decision"],
    ),
    "authorizes_final_acceptance_packet": (
        "final_output_execution_decision",
        ["A6-review-final-output-execution-decision"],
    ),
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


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def classify_blocker(blocker: dict[str, Any]) -> tuple[str, list[str]]:
    blocker_id = str(blocker.get("blocker_id", ""))
    if blocker_id in EXPLICIT_BLOCKER_RULES:
        class_id, action_ids = EXPLICIT_BLOCKER_RULES[blocker_id]
        return class_id, sorted(set(action_ids))

    text = " ".join(
        [
            str(blocker.get("blocker_id", "")),
            str(blocker.get("reason", "")),
            str(blocker.get("needed_action", "")),
        ]
    ).lower()
    matched_classes: list[str] = []
    matched_actions: list[str] = []
    for rule in CLASS_RULES:
        if any(term in text for term in rule["match"]):
            matched_classes.append(rule["class_id"])
            matched_actions.extend(rule["default_action_ids"])
    if not matched_classes:
        matched_classes.append("other_manual_prerequisite")
    if not matched_actions:
        matched_actions.append("A5-rerun-readiness-gates")
    return matched_classes[0], sorted(set(matched_actions))


def target_actions(authorization_blockers: dict[str, Any]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for target in as_list(authorization_blockers.get("execution_target_authorization_blockers")):
        if not isinstance(target, dict):
            continue
        target_id = str(target.get("target_id", ""))
        for action_id in as_list(target.get("required_action_ids")):
            mapping.setdefault(target_id, []).append(str(action_id))
    return {target_id: sorted(set(actions)) for target_id, actions in mapping.items()}


def action_orders(shortest_path: dict[str, Any]) -> dict[str, int]:
    result: dict[str, int] = {}
    for step in as_list(shortest_path.get("shortest_path")):
        if isinstance(step, dict) and step.get("action_id"):
            result[str(step["action_id"])] = int(step.get("order", len(result) + 1))
    return result


def build_summary(
    status_skeleton_path: Path,
    authorization_blockers_path: Path,
    shortest_path_path: Path,
) -> dict[str, Any]:
    status_skeleton = read_json(status_skeleton_path)
    authorization_blockers = read_json(authorization_blockers_path)
    shortest_path = read_json(shortest_path_path)
    skeleton_summary = as_dict(status_skeleton.get("summary"))
    blocker_summary = as_dict(authorization_blockers.get("summary"))

    issues: list[str] = []
    if status_skeleton.get("status") != "human_review_status_packet_skeleton_not_execution":
        issues.append("status skeleton status is not human_review_status_packet_skeleton_not_execution")
    if authorization_blockers.get("status") != "execution_authorization_blocker_index_not_execution":
        issues.append("authorization blocker status is not execution_authorization_blocker_index_not_execution")
    if shortest_path.get("status") != "manual_review_shortest_path_note_not_execution":
        issues.append("shortest-path status is not manual_review_shortest_path_note_not_execution")
    if int(skeleton_summary.get("issue_count", 0)) != 0:
        issues.append("status skeleton has open issues")
    if int(blocker_summary.get("issue_count", 0)) != 0:
        issues.append("authorization blocker index has open issues")

    order_by_action = action_orders(shortest_path)
    class_rows: dict[str, dict[str, Any]] = {}
    blocker_rows: list[dict[str, Any]] = []
    for blocker in as_list(status_skeleton.get("dashboard_blockers")):
        if not isinstance(blocker, dict):
            continue
        class_id, action_ids = classify_blocker(blocker)
        row = {
            "gate_id": blocker.get("gate_id", ""),
            "blocker_id": blocker.get("blocker_id", ""),
            "reason": blocker.get("reason", ""),
            "needed_action": blocker.get("needed_action", ""),
            "prerequisite_class": class_id,
            "mapped_action_ids": action_ids,
            "mapped_action_orders": [order_by_action.get(action_id) for action_id in action_ids],
            "satisfies_dependency_now": False,
            "runs_commands_now": False,
        }
        blocker_rows.append(row)
        class_record = class_rows.setdefault(
            class_id,
            {
                "prerequisite_class": class_id,
                "blocker_count": 0,
                "blocker_keys": [],
                "mapped_action_ids": set(),
                "earliest_action_order": None,
                "satisfies_dependency_now": False,
                "runs_commands_now": False,
            },
        )
        class_record["blocker_count"] += 1
        class_record["blocker_keys"].append(f"{row['gate_id']}:{row['blocker_id']}")
        class_record["mapped_action_ids"].update(action_ids)

    prerequisite_classes: list[dict[str, Any]] = []
    for class_record in class_rows.values():
        action_ids = sorted(class_record["mapped_action_ids"], key=lambda item: order_by_action.get(item, 999))
        orders = [order_by_action.get(action_id) for action_id in action_ids if order_by_action.get(action_id) is not None]
        prerequisite_classes.append(
            {
                "prerequisite_class": class_record["prerequisite_class"],
                "blocker_count": class_record["blocker_count"],
                "blocker_keys": class_record["blocker_keys"],
                "mapped_action_ids": action_ids,
                "earliest_action_order": min(orders) if orders else None,
                "satisfies_dependency_now": False,
                "runs_commands_now": False,
            }
        )
    prerequisite_classes.sort(key=lambda item: (item["earliest_action_order"] or 999, item["prerequisite_class"]))

    target_action_map = target_actions(authorization_blockers)
    action_to_classes: dict[str, list[str]] = {}
    for class_record in prerequisite_classes:
        for action_id in class_record["mapped_action_ids"]:
            action_to_classes.setdefault(action_id, []).append(class_record["prerequisite_class"])

    expected_blockers = int(skeleton_summary.get("dashboard_blocker_count", len(blocker_rows)))
    if len(blocker_rows) != expected_blockers:
        issues.append(f"dashboard blocker count mismatch: summary={expected_blockers} rows={len(blocker_rows)}")

    return {
        "dependency_summary_id": "final_submission_status_packet_dependency_summary_20260610",
        "status": "status_packet_dependency_summary_not_execution",
        "sources": {
            "human_review_status_packet_skeleton": rel(status_skeleton_path),
            "execution_authorization_blocker_index": rel(authorization_blockers_path),
            "manual_review_shortest_path_note": rel(shortest_path_path),
        },
        "summary": {
            "dashboard_blocker_count": len(blocker_rows),
            "prerequisite_class_count": len(prerequisite_classes),
            "mapped_action_count": len(action_to_classes),
            "execution_target_count": len(target_action_map),
            "blocked_execution_target_count": int(blocker_summary.get("blocked_execution_target_count", 0)),
            "issue_count": len(issues),
            "automated_execution_allowed": False,
            "answers_questions_now": False,
            "fills_answers_now": False,
            "edits_decision_artifacts_now": False,
            "satisfies_dependencies_now": False,
            "runs_commands_now": False,
            "authorizes_execution_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "prerequisite_classes": prerequisite_classes,
        "blocker_rows": blocker_rows,
        "execution_target_action_map": target_action_map,
        "action_to_prerequisite_classes": {
            action_id: sorted(classes)
            for action_id, classes in sorted(action_to_classes.items(), key=lambda item: order_by_action.get(item[0], 999))
        },
        "issues": issues,
        "claim_boundary": [
            "This dependency summary is a static grouping artifact only.",
            "It does not satisfy prerequisites.",
            "It does not answer review questions.",
            "It does not fill or copy answer-sheet values.",
            "It does not edit decision templates.",
            "It does not approve or reject decisions.",
            "It does not create final artifacts.",
            "It does not run post-review commands.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
            "It does not run live tools or visible-thread dispatch.",
        ],
    }


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    metrics = summary["summary"]
    lines = [
        "# Final Submission Status-Packet Dependency Summary, 2026-06-10",
        "",
        f"Status: `{summary['status']}`",
        "",
        "## Summary",
        "",
        f"- Dashboard blockers: `{metrics['dashboard_blocker_count']}`",
        f"- Prerequisite classes: `{metrics['prerequisite_class_count']}`",
        f"- Mapped actions: `{metrics['mapped_action_count']}`",
        f"- Execution targets: `{metrics['execution_target_count']}`",
        f"- Blocked execution targets: `{metrics['blocked_execution_target_count']}`",
        f"- Issues: `{metrics['issue_count']}`",
        f"- Satisfies dependencies now: `{metrics['satisfies_dependencies_now']}`",
        f"- Runs commands now: `{metrics['runs_commands_now']}`",
        f"- Authorizes execution now: `{metrics['authorizes_execution_now']}`",
        f"- Generates final outputs: `{metrics['generates_final_outputs']}`",
        f"- Final acceptance: `{metrics['final_acceptance']}`",
        "",
        "## Prerequisite Classes",
        "",
    ]
    for item in summary["prerequisite_classes"]:
        lines.extend(
            [
                f"### {item['prerequisite_class']}",
                "",
                f"- Blockers: `{item['blocker_count']}`",
                f"- Mapped actions: `{', '.join(item['mapped_action_ids'])}`",
                f"- Earliest action order: `{item['earliest_action_order']}`",
                f"- Satisfies dependency now: `{item['satisfies_dependency_now']}`",
                "",
            ]
        )
    lines.extend(["## Action To Prerequisite Classes", ""])
    for action_id, classes in summary["action_to_prerequisite_classes"].items():
        lines.append(f"- `{action_id}`: {', '.join(f'`{item}`' for item in classes)}")
    lines.extend(["", "## Issues", ""])
    if summary["issues"]:
        for issue in summary["issues"]:
            lines.append(f"- {issue}")
    else:
        lines.append("- None")
    lines.extend(["", "## Claim Boundary", ""])
    for item in summary["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status-skeleton", default=str(DEFAULT_STATUS_SKELETON.relative_to(ROOT)))
    parser.add_argument("--authorization-blockers", default=str(DEFAULT_AUTHORIZATION_BLOCKERS.relative_to(ROOT)))
    parser.add_argument("--shortest-path", default=str(DEFAULT_SHORTEST_PATH.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = build_summary(
        repo_path(args.status_skeleton),
        repo_path(args.authorization_blockers),
        repo_path(args.shortest_path),
    )
    json_path = output_dir / "final_submission_status_packet_dependency_summary.json"
    md_path = output_dir / "final_submission_status_packet_dependency_summary.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(summary, md_path)
    print(
        json.dumps(
            {"ok": not summary["issues"], **summary["summary"], "json": rel(json_path), "markdown": rel(md_path)},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not summary["issues"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
