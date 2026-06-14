#!/usr/bin/env python3
"""Guard final-submission review aids against accidental execution claims.

This checker reads static final-submission review artifacts and verifies that
they still forbid final-output execution, live tool work, and visible-thread
dispatch until explicit authorization changes the relevant decision artifacts.
It does not run generators or final-output commands.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_JSON = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_forbidden_action_guard_20260610"
    / "final_submission_forbidden_action_guard_check.json"
)
DEFAULT_OUTPUT_MD = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_forbidden_action_guard_20260610"
    / "final_submission_forbidden_action_guard_check.md"
)

ARTIFACTS = {
    "source_output_readiness": "Results/static_audits/submission_source_output_readiness_20260610/submission_source_output_readiness.json",
    "pdf_export_plan": "Results/static_audits/pdf_export_dry_run_plan_20260610/pdf_export_dry_run_plan.json",
    "demo_video_storyboard": "Results/static_audits/demo_video_storyboard_plan_20260610/demo_video_storyboard_plan.json",
    "final_acceptance_prereq": "Results/static_audits/final_acceptance_packet_prereq_20260610/final_acceptance_packet_prereq_plan.json",
    "final_output_execution_decision": "Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision_check.json",
    "final_submission_dashboard": "Results/static_audits/final_submission_readiness_dashboard_20260610/final_submission_readiness_dashboard.json",
    "human_action_checklist": "Results/static_audits/final_submission_human_action_checklist_20260610/final_submission_human_action_checklist.json",
    "reviewer_action_map": "Results/static_audits/final_submission_reviewer_action_map_20260610/final_submission_reviewer_action_map.json",
    "reviewer_packet_index": "Results/static_audits/final_submission_reviewer_packet_index_20260610/final_submission_reviewer_packet_index.json",
    "blocker_question_crosswalk": "Results/static_audits/final_submission_blocker_question_crosswalk_20260610/final_submission_blocker_question_crosswalk.json",
    "post_review_command_grouping": "Results/static_audits/final_submission_post_review_command_grouping_20260610/final_submission_post_review_command_grouping_index.json",
    "post_review_command_critical_path": "Results/static_audits/final_submission_post_review_command_critical_path_20260610/final_submission_post_review_command_critical_path_index.json",
    "post_review_reviewer_checklist": "Results/static_audits/final_submission_post_review_reviewer_checklist_20260610/final_submission_post_review_reviewer_checklist.json",
    "human_review_execution_gate_summary": "Results/static_audits/final_submission_human_review_execution_gate_20260610/final_submission_human_review_execution_gate_summary.json",
    "execution_authorization_blocker_index": "Results/static_audits/final_submission_execution_authorization_blocker_20260610/final_submission_execution_authorization_blocker_index.json",
    "no_packet_action_escalation_note": "Results/static_audits/final_submission_no_packet_action_escalation_20260610/final_submission_no_packet_action_escalation_note.json",
}

EXPECTED_FALSE_FLAGS = {
    "source_output_readiness": [
        "safe_to_export_final_pdfs_now",
        "safe_to_record_demo_video_now",
        "safe_to_write_final_acceptance_now",
        "generates_final_outputs",
        "final_acceptance",
    ],
    "pdf_export_plan": [
        "safe_to_run_pdf_export_now",
        "runs_pandoc_now",
        "creates_submission_dir_now",
        "generates_final_outputs",
        "final_acceptance",
    ],
    "demo_video_storyboard": [
        "safe_to_record_demo_video_now",
        "records_or_renders_video_now",
        "generates_final_outputs",
        "final_acceptance",
    ],
    "final_acceptance_prereq": [
        "safe_to_write_final_acceptance_packet_now",
        "writes_canonical_acceptance_packet_now",
        "final_acceptance",
    ],
    "final_output_execution_decision": [
        "authorizes_pdf_export",
        "authorizes_demo_video_recording",
        "authorizes_final_acceptance_packet",
        "creates_submission_dir_now",
        "runs_pandoc_now",
        "records_or_renders_video_now",
        "writes_canonical_acceptance_packet_now",
        "generates_final_outputs",
        "final_acceptance",
    ],
    "final_submission_dashboard": [
        "final_submission_ready",
        "generates_final_outputs",
        "final_acceptance",
    ],
    "human_action_checklist": [
        "automated_execution_allowed",
        "generates_final_outputs",
        "final_acceptance",
    ],
    "reviewer_action_map": [
        "automated_execution_allowed",
        "generates_final_outputs",
        "final_acceptance",
    ],
    "reviewer_packet_index": [
        "automated_execution_allowed",
        "fills_answers_now",
        "copies_answers_now",
        "edits_decision_artifacts_now",
        "runs_rerun_commands_now",
    ],
    "blocker_question_crosswalk": [
        "automated_execution_allowed",
        "answers_questions_now",
        "edits_decision_artifacts_now",
        "runs_rerun_commands_now",
    ],
    "post_review_command_grouping": [
        "runs_commands_now",
        "applies_transitions_now",
        "edits_decision_artifacts_now",
        "generates_final_outputs",
        "final_acceptance",
    ],
    "post_review_command_critical_path": [
        "runs_commands_now",
        "applies_transitions_now",
        "edits_decision_artifacts_now",
        "generates_final_outputs",
        "final_acceptance",
    ],
    "post_review_reviewer_checklist": [
        "automated_execution_allowed",
        "answers_questions_now",
        "edits_decision_artifacts_now",
        "runs_commands_now",
        "applies_transitions_now",
        "generates_final_outputs",
        "final_acceptance",
    ],
    "human_review_execution_gate_summary": [
        "automated_execution_allowed",
        "answers_questions_now",
        "edits_decision_artifacts_now",
        "runs_commands_now",
        "creates_submission_dir_now",
        "runs_pandoc_now",
        "records_or_renders_video_now",
        "writes_canonical_acceptance_packet_now",
        "generates_final_outputs",
        "final_acceptance",
    ],
    "execution_authorization_blocker_index": [
        "automated_execution_allowed",
        "answers_questions_now",
        "fills_answers_now",
        "copies_answers_now",
        "edits_decision_artifacts_now",
        "runs_commands_now",
        "authorizes_execution_now",
        "generates_final_outputs",
        "final_acceptance",
    ],
    "no_packet_action_escalation_note": [
        "automated_execution_allowed",
        "reviewer_packet_created_now",
        "answers_questions_now",
        "edits_decision_artifacts_now",
        "runs_commands_now",
        "authorizes_execution_now",
        "generates_final_outputs",
        "final_acceptance",
    ],
}

FORBIDDEN_TRUE_FLAG_SUFFIXES = (
    "authorized_now",
    "authorizes_execution_now",
    "approves_or_executes_now",
    "runs_commands_now",
    "runs_rerun_commands_now",
    "runs_pandoc_now",
    "creates_submission_dir_now",
    "records_or_renders_video_now",
    "writes_canonical_acceptance_packet_now",
    "generates_final_outputs",
    "final_acceptance",
    "dispatches_visible_threads_now",
    "runs_live_tools_now",
)

FORBIDDEN_COMMAND_TOKENS = (
    "simulate_model",
    "check_model",
    "sysplorer",
    "syslab",
    "mworks",
    "ros2",
    "rviz",
    "fast-lio",
    "unreal",
    "ue5",
    "codex_delegation",
    "send_message_to_thread",
    "create_thread",
    "fork_thread",
    "set_thread_archived",
    "wechat",
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


def get_summary(data: dict[str, Any]) -> dict[str, Any]:
    summary = data.get("summary", {})
    return summary if isinstance(summary, dict) else {}


def walk_json(value: Any, prefix: str = "") -> list[tuple[str, Any]]:
    rows = [(prefix, value)]
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(walk_json(child, child_prefix))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_prefix = f"{prefix}[{index}]"
            rows.extend(walk_json(child, child_prefix))
    return rows


def validate(artifacts: dict[str, str] = ARTIFACTS) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []
    loaded: dict[str, dict[str, Any]] = {}
    false_flag_checks: list[str] = []
    command_checks: list[str] = []

    for artifact_id, path_value in artifacts.items():
        path = repo_path(path_value)
        if not path.exists():
            issues.append(f"missing artifact {artifact_id}: {path_value}")
            loaded[artifact_id] = {}
            continue
        try:
            loaded[artifact_id] = read_json(path)
        except Exception as exc:
            issues.append(f"cannot read artifact {artifact_id}: {exc}")
            loaded[artifact_id] = {}

    for artifact_id, required_flags in EXPECTED_FALSE_FLAGS.items():
        summary = get_summary(loaded.get(artifact_id, {}))
        for flag in required_flags:
            actual = summary.get(flag)
            false_flag_checks.append(f"{artifact_id}.summary.{flag}")
            if actual is not False:
                issues.append(f"{artifact_id}.summary.{flag} must be false, got {actual!r}")

    execution_decision = loaded.get("final_output_execution_decision", {})
    actions = execution_decision.get("actions", {})
    if not isinstance(actions, dict) or set(actions) != {
        "pdf_export",
        "demo_video_recording",
        "final_acceptance_packet",
    }:
        issues.append("final_output_execution_decision.actions must contain the three final-output actions")
    elif isinstance(actions, dict):
        for action_id, action in actions.items():
            if not isinstance(action, dict):
                issues.append(f"final_output_execution_decision.actions.{action_id} must be an object")
                continue
            if action.get("decision") != "pending_review":
                issues.append(f"{action_id}.decision must remain pending_review")
            if action.get("approved") is not False:
                issues.append(f"{action_id}.approved must remain false")
            if action.get("upstream_ready") is not False:
                issues.append(f"{action_id}.upstream_ready must remain false")
            if action.get("authorizes_execution") is not False:
                issues.append(f"{action_id}.authorizes_execution must remain false")

    for artifact_id, data in loaded.items():
        for path, value in walk_json(data):
            leaf_name = path.rsplit(".", 1)[-1]
            normalized_leaf = leaf_name.replace("]", "").split("[", 1)[0]
            if isinstance(value, bool) and value is True:
                if normalized_leaf.endswith(FORBIDDEN_TRUE_FLAG_SUFFIXES):
                    issues.append(f"{artifact_id}.{path} is forbidden true")
            if normalized_leaf == "command" and isinstance(value, str):
                command_checks.append(f"{artifact_id}.{path}")
                lowered = value.lower()
                for token in FORBIDDEN_COMMAND_TOKENS:
                    if token in lowered:
                        issues.append(f"{artifact_id}.{path} contains forbidden command token {token!r}")

    return {
        "ok": not issues,
        "check_id": "final_submission_forbidden_action_guard_20260610",
        "status": "forbidden_action_guard_not_execution",
        "artifacts": artifacts,
        "summary": {
            "artifact_count": len(artifacts),
            "false_flag_check_count": len(false_flag_checks),
            "command_field_check_count": len(command_checks),
            "issue_count": len(issues),
            "warning_count": len(warnings),
            "pdf_export_still_forbidden": True,
            "demo_recording_still_forbidden": True,
            "final_acceptance_still_forbidden": True,
            "live_tools_still_forbidden": True,
            "visible_thread_dispatch_still_forbidden": True,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "checked_false_flags": false_flag_checks,
        "checked_command_fields": command_checks,
        "issues": issues,
        "warnings": warnings,
        "claim_boundary": [
            "This guard validates existing static review aids only.",
            "It does not edit decision templates.",
            "It does not install PDF tooling.",
            "It does not create Results/submission.",
            "It does not run Pandoc.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write canonical PMO final acceptance.",
            "It does not run MWORKS, ROS2, UE, or visible-thread dispatch tools.",
        ],
    }


def write_markdown(result: dict[str, Any], path: Path) -> None:
    summary = result["summary"]
    lines = [
        "# Final Submission Forbidden Action Guard, 2026-06-10",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Summary",
        "",
        f"- OK: `{result['ok']}`",
        f"- Artifacts checked: `{summary['artifact_count']}`",
        f"- False-flag checks: `{summary['false_flag_check_count']}`",
        f"- Command-field checks: `{summary['command_field_check_count']}`",
        f"- Issues: `{summary['issue_count']}`",
        f"- PDF export still forbidden: `{summary['pdf_export_still_forbidden']}`",
        f"- Demo recording still forbidden: `{summary['demo_recording_still_forbidden']}`",
        f"- Final acceptance still forbidden: `{summary['final_acceptance_still_forbidden']}`",
        f"- Live tools still forbidden: `{summary['live_tools_still_forbidden']}`",
        f"- Visible-thread dispatch still forbidden: `{summary['visible_thread_dispatch_still_forbidden']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Artifacts",
        "",
    ]
    for artifact_id, path_value in result["artifacts"].items():
        lines.append(f"- `{artifact_id}`: `{path_value}`")
    lines.extend(["", "## Issues", ""])
    if result["issues"]:
        for item in result["issues"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines.extend(["", "## Claim Boundary", ""])
    for item in result["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON.relative_to(ROOT)))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD.relative_to(ROOT)))
    args = parser.parse_args()

    result = validate()
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
