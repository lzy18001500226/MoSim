#!/usr/bin/env python3
"""Check the topological refresh order for final-submission static audits.

This checker prevents stale-read and parallel-write mistakes by documenting and
validating the required static audit refresh order. It does not run generators.
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
    / "final_submission_refresh_order_20260610"
    / "final_submission_refresh_order_check.json"
)
DEFAULT_OUTPUT_MD = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_refresh_order_20260610"
    / "final_submission_refresh_order_check.md"
)

NODES = [
    {
        "node_id": "report_source_edit_decision",
        "command": "python Scripts/quality/check_report_source_edit_decision.py",
        "outputs": [
            "Results/static_audits/report_source_edit_decision_template_20260610/report_source_edit_decision_check.json"
        ],
        "after": [],
    },
    {
        "node_id": "source_edit_readiness",
        "command": "python Scripts/quality/build_simulation_report_source_edit_readiness_gate.py",
        "outputs": [
            "Results/static_audits/simulation_report_source_edit_readiness_20260610/simulation_report_source_edit_readiness_gate.json"
        ],
        "after": ["report_source_edit_decision"],
    },
    {
        "node_id": "source_edit_application_plan",
        "command": "python Scripts/quality/build_simulation_report_source_edit_application_plan.py",
        "outputs": [
            "Results/static_audits/simulation_report_source_edit_application_plan_20260610/simulation_report_source_edit_application_plan.json"
        ],
        "after": ["source_edit_readiness"],
    },
    {
        "node_id": "source_edit_reviewer_summary",
        "command": "python Scripts/quality/build_simulation_report_source_edit_reviewer_summary.py",
        "outputs": [
            "Results/static_audits/simulation_report_source_edit_reviewer_summary_20260610/simulation_report_source_edit_reviewer_summary.json"
        ],
        "after": ["source_edit_application_plan"],
    },
    {
        "node_id": "source_edit_application_audit_checklist",
        "command": "python Scripts/quality/build_simulation_report_source_edit_application_audit_checklist.py",
        "outputs": [
            "Results/static_audits/simulation_report_source_edit_application_audit_checklist_20260610/simulation_report_source_edit_application_audit_checklist.json"
        ],
        "after": ["source_edit_reviewer_summary"],
    },
    {
        "node_id": "source_output_readiness",
        "command": "python Scripts/quality/build_submission_source_output_readiness.py",
        "outputs": [
            "Results/static_audits/submission_source_output_readiness_20260610/submission_source_output_readiness.json"
        ],
        "after": ["source_edit_application_plan"],
    },
    {
        "node_id": "pdf_export_plan",
        "command": "python Scripts/quality/build_pdf_export_dry_run_plan.py",
        "outputs": ["Results/static_audits/pdf_export_dry_run_plan_20260610/pdf_export_dry_run_plan.json"],
        "after": ["source_output_readiness"],
    },
    {
        "node_id": "demo_video_storyboard",
        "command": "python Scripts/quality/build_demo_video_storyboard_plan.py",
        "outputs": ["Results/static_audits/demo_video_storyboard_plan_20260610/demo_video_storyboard_plan.json"],
        "after": [],
    },
    {
        "node_id": "final_artifact_manifest",
        "command": "python Scripts/quality/check_final_submission_artifact_manifest.py --allow-missing",
        "outputs": [
            "Results/static_audits/final_submission_artifacts_20260610/final_submission_artifact_manifest_check.json"
        ],
        "after": [],
    },
    {
        "node_id": "final_acceptance_prereq",
        "command": "python Scripts/quality/build_final_acceptance_packet_prereq_plan.py",
        "outputs": [
            "Results/static_audits/final_acceptance_packet_prereq_20260610/final_acceptance_packet_prereq_plan.json"
        ],
        "after": ["source_output_readiness", "pdf_export_plan", "demo_video_storyboard", "final_artifact_manifest"],
    },
    {
        "node_id": "final_output_execution_decision",
        "command": "python Scripts/quality/build_final_output_execution_decision_template.py",
        "outputs": [
            "Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision_check.json"
        ],
        "after": ["pdf_export_plan", "demo_video_storyboard", "final_acceptance_prereq"],
    },
    {
        "node_id": "final_submission_dashboard",
        "command": "python Scripts/quality/build_final_submission_readiness_dashboard.py",
        "outputs": [
            "Results/static_audits/final_submission_readiness_dashboard_20260610/final_submission_readiness_dashboard.json"
        ],
        "after": [
            "source_output_readiness",
            "pdf_export_plan",
            "demo_video_storyboard",
            "final_artifact_manifest",
            "final_acceptance_prereq",
            "final_output_execution_decision",
        ],
    },
    {
        "node_id": "final_submission_human_action_checklist",
        "command": "python Scripts/quality/build_final_submission_human_action_checklist.py",
        "outputs": [
            "Results/static_audits/final_submission_human_action_checklist_20260610/final_submission_human_action_checklist.json"
        ],
        "after": ["final_submission_dashboard"],
    },
    {
        "node_id": "final_submission_reviewer_action_map",
        "command": "python Scripts/quality/build_final_submission_reviewer_action_map.py",
        "outputs": [
            "Results/static_audits/final_submission_reviewer_action_map_20260610/final_submission_reviewer_action_map.json"
        ],
        "after": ["final_submission_human_action_checklist"],
    },
    {
        "node_id": "final_submission_human_review_decision_packet",
        "command": "python Scripts/quality/build_final_submission_human_review_decision_packet_template.py",
        "outputs": [
            "Results/static_audits/final_submission_human_review_decision_packet_20260610/final_submission_human_review_decision_packet_check.json"
        ],
        "after": ["final_submission_reviewer_action_map"],
    },
    {
        "node_id": "final_submission_human_review_guide",
        "command": "python Scripts/quality/build_final_submission_human_review_guide.py",
        "outputs": [
            "Results/static_audits/final_submission_human_review_guide_20260610/final_submission_human_review_guide.json"
        ],
        "after": ["final_submission_human_review_decision_packet"],
    },
    {
        "node_id": "final_submission_readiness_chain",
        "command": "python Scripts/quality/check_final_submission_readiness_chain.py",
        "outputs": [
            "Results/static_audits/final_submission_readiness_chain_20260610/final_submission_readiness_chain_check.json"
        ],
        "after": [
            "final_submission_dashboard",
            "final_submission_human_action_checklist",
            "final_submission_reviewer_action_map",
            "final_submission_human_review_decision_packet",
        ],
    },
    {
        "node_id": "final_submission_refresh_order",
        "command": "python Scripts/quality/check_final_submission_refresh_order.py",
        "outputs": [
            "Results/static_audits/final_submission_refresh_order_20260610/final_submission_refresh_order_check.json"
        ],
        "after": ["final_submission_readiness_chain"],
    },
    {
        "node_id": "final_submission_static_audit_index",
        "command": "python Scripts/quality/build_final_submission_static_audit_index.py",
        "outputs": [
            "Results/static_audits/final_submission_static_audit_index_20260610/final_submission_static_audit_index.json"
        ],
        "after": [
            "source_edit_reviewer_summary",
            "source_edit_application_audit_checklist",
            "final_submission_readiness_chain",
            "final_submission_refresh_order",
        ],
    },
    {
        "node_id": "final_submission_blocked_gate_triage_map",
        "command": "python Scripts/quality/build_final_submission_blocked_gate_triage_map.py",
        "outputs": [
            "Results/static_audits/final_submission_blocked_gate_triage_map_20260610/final_submission_blocked_gate_triage_map.json"
        ],
        "after": ["final_submission_static_audit_index"],
    },
    {
        "node_id": "final_submission_human_decision_diff_template",
        "command": "python Scripts/quality/build_final_submission_human_decision_diff_template.py",
        "outputs": [
            "Results/static_audits/final_submission_human_decision_diff_template_20260610/final_submission_human_decision_diff_template.json"
        ],
        "after": ["final_submission_blocked_gate_triage_map"],
    },
    {
        "node_id": "final_submission_reviewer_quickstart",
        "command": "python Scripts/quality/build_final_submission_reviewer_quickstart.py",
        "outputs": [
            "Results/static_audits/final_submission_reviewer_quickstart_20260610/final_submission_reviewer_quickstart.json"
        ],
        "after": ["final_submission_human_decision_diff_template"],
    },
    {
        "node_id": "final_submission_review_progress_snapshot",
        "command": "python Scripts/quality/build_final_submission_review_progress_snapshot.py",
        "outputs": [
            "Results/static_audits/final_submission_review_progress_snapshot_20260610/final_submission_review_progress_snapshot.json"
        ],
        "after": ["final_submission_reviewer_quickstart"],
    },
    {
        "node_id": "final_submission_post_review_rerun_matrix",
        "command": "python Scripts/quality/build_final_submission_post_review_rerun_matrix.py",
        "outputs": [
            "Results/static_audits/final_submission_post_review_rerun_matrix_20260610/final_submission_post_review_rerun_matrix.json"
        ],
        "after": ["final_submission_review_progress_snapshot"],
    },
    {
        "node_id": "final_submission_manual_review_answer_sheet",
        "command": "python Scripts/quality/build_final_submission_manual_review_answer_sheet_template.py",
        "outputs": [
            "Results/static_audits/final_submission_manual_review_answer_sheet_20260610/final_submission_manual_review_answer_sheet_template.json"
        ],
        "after": ["final_submission_post_review_rerun_matrix"],
    },
    {
        "node_id": "final_submission_answer_sheet_decision_consistency",
        "command": "python Scripts/quality/check_final_submission_answer_sheet_decision_consistency.py",
        "outputs": [
            "Results/static_audits/final_submission_manual_review_answer_sheet_20260610/final_submission_answer_sheet_decision_consistency_check.json"
        ],
        "after": ["final_submission_manual_review_answer_sheet"],
    },
    {
        "node_id": "final_submission_review_artifact_bundle_index",
        "command": "python Scripts/quality/build_final_submission_review_artifact_bundle_index.py",
        "outputs": [
            "Results/static_audits/final_submission_review_artifact_bundle_20260610/final_submission_review_artifact_bundle_index.json"
        ],
        "after": ["final_submission_answer_sheet_decision_consistency"],
    },
    {
        "node_id": "final_submission_reviewer_handoff_note",
        "command": "python Scripts/quality/build_final_submission_reviewer_handoff_note.py",
        "outputs": [
            "Results/static_audits/final_submission_reviewer_handoff_note_20260610/final_submission_reviewer_handoff_note.json"
        ],
        "after": ["final_submission_review_artifact_bundle_index"],
    },
    {
        "node_id": "final_submission_manual_review_closure_checklist",
        "command": "python Scripts/quality/build_final_submission_manual_review_closure_checklist.py",
        "outputs": [
            "Results/static_audits/final_submission_manual_review_closure_checklist_20260610/final_submission_manual_review_closure_checklist.json"
        ],
        "after": ["final_submission_reviewer_handoff_note"],
    },
    {
        "node_id": "final_submission_post_review_state_transition_plan",
        "command": "python Scripts/quality/build_final_submission_post_review_state_transition_plan.py",
        "outputs": [
            "Results/static_audits/final_submission_post_review_state_transition_plan_20260610/final_submission_post_review_state_transition_plan.json"
        ],
        "after": ["final_submission_manual_review_closure_checklist"],
    },
    {
        "node_id": "final_submission_post_review_command_plan_coverage",
        "command": "python Scripts/quality/check_final_submission_post_review_command_plan_coverage.py",
        "outputs": [
            "Results/static_audits/final_submission_post_review_command_plan_coverage_20260610/final_submission_post_review_command_plan_coverage_check.json"
        ],
        "after": ["final_submission_post_review_state_transition_plan"],
    },
    {
        "node_id": "final_submission_review_artifact_dependency_graph",
        "command": "python Scripts/quality/build_final_submission_review_artifact_dependency_graph.py",
        "outputs": [
            "Results/static_audits/final_submission_review_artifact_dependency_graph_20260610/final_submission_review_artifact_dependency_graph.json"
        ],
        "after": ["final_submission_post_review_command_plan_coverage"],
    },
    {
        "node_id": "final_submission_review_aid_freshness",
        "command": "python Scripts/quality/check_final_submission_review_aid_freshness.py",
        "outputs": [
            "Results/static_audits/final_submission_review_aid_freshness_20260610/final_submission_review_aid_freshness_check.json"
        ],
        "after": ["final_submission_review_artifact_dependency_graph"],
    },
    {
        "node_id": "final_submission_reviewer_packet_index",
        "command": "python Scripts/quality/build_final_submission_reviewer_packet_index.py",
        "outputs": [
            "Results/static_audits/final_submission_reviewer_packet_index_20260610/final_submission_reviewer_packet_index.json"
        ],
        "after": ["final_submission_review_aid_freshness"],
    },
    {
        "node_id": "final_submission_blocker_question_crosswalk",
        "command": "python Scripts/quality/build_final_submission_blocker_question_crosswalk.py",
        "outputs": [
            "Results/static_audits/final_submission_blocker_question_crosswalk_20260610/final_submission_blocker_question_crosswalk.json"
        ],
        "after": ["final_submission_reviewer_packet_index"],
    },
    {
        "node_id": "final_submission_post_review_command_grouping_index",
        "command": "python Scripts/quality/build_final_submission_post_review_command_grouping_index.py",
        "outputs": [
            "Results/static_audits/final_submission_post_review_command_grouping_20260610/final_submission_post_review_command_grouping_index.json"
        ],
        "after": ["final_submission_blocker_question_crosswalk"],
    },
    {
        "node_id": "final_submission_post_review_command_critical_path_index",
        "command": "python Scripts/quality/build_final_submission_post_review_command_critical_path_index.py",
        "outputs": [
            "Results/static_audits/final_submission_post_review_command_critical_path_20260610/final_submission_post_review_command_critical_path_index.json"
        ],
        "after": ["final_submission_post_review_command_grouping_index"],
    },
    {
        "node_id": "final_submission_post_review_shared_tail_deduplication_note",
        "command": "python Scripts/quality/build_final_submission_post_review_shared_tail_deduplication_note.py",
        "outputs": [
            "Results/static_audits/final_submission_post_review_shared_tail_deduplication_20260610/final_submission_post_review_shared_tail_deduplication_note.json"
        ],
        "after": ["final_submission_post_review_command_critical_path_index"],
    },
    {
        "node_id": "final_submission_post_review_reviewer_checklist",
        "command": "python Scripts/quality/build_final_submission_post_review_reviewer_checklist.py",
        "outputs": [
            "Results/static_audits/final_submission_post_review_reviewer_checklist_20260610/final_submission_post_review_reviewer_checklist.json"
        ],
        "after": ["final_submission_post_review_shared_tail_deduplication_note"],
    },
    {
        "node_id": "final_submission_human_review_execution_gate_summary",
        "command": "python Scripts/quality/build_final_submission_human_review_execution_gate_summary.py",
        "outputs": [
            "Results/static_audits/final_submission_human_review_execution_gate_20260610/final_submission_human_review_execution_gate_summary.json"
        ],
        "after": ["final_submission_post_review_reviewer_checklist"],
    },
    {
        "node_id": "final_submission_execution_authorization_blocker_index",
        "command": "python Scripts/quality/build_final_submission_execution_authorization_blocker_index.py",
        "outputs": [
            "Results/static_audits/final_submission_execution_authorization_blocker_20260610/final_submission_execution_authorization_blocker_index.json"
        ],
        "after": ["final_submission_human_review_execution_gate_summary"],
    },
    {
        "node_id": "final_submission_no_packet_action_escalation_note",
        "command": "python Scripts/quality/build_final_submission_no_packet_action_escalation_note.py",
        "outputs": [
            "Results/static_audits/final_submission_no_packet_action_escalation_20260610/final_submission_no_packet_action_escalation_note.json"
        ],
        "after": ["final_submission_execution_authorization_blocker_index"],
    },
    {
        "node_id": "final_submission_forbidden_action_guard",
        "command": "python Scripts/quality/check_final_submission_forbidden_action_guard.py",
        "outputs": [
            "Results/static_audits/final_submission_forbidden_action_guard_20260610/final_submission_forbidden_action_guard_check.json"
        ],
        "after": ["final_submission_no_packet_action_escalation_note"],
    },
    {
        "node_id": "final_submission_reviewer_evidence_index",
        "command": "python Scripts/quality/build_final_submission_reviewer_evidence_index.py",
        "outputs": [
            "Results/static_audits/final_submission_reviewer_evidence_index_20260610/final_submission_reviewer_evidence_index.json"
        ],
        "after": ["final_submission_forbidden_action_guard"],
    },
    {
        "node_id": "final_submission_reviewer_open_file_checksum_index",
        "command": "python Scripts/quality/build_final_submission_reviewer_open_file_checksum_index.py",
        "outputs": [
            "Results/static_audits/final_submission_reviewer_open_file_checksum_index_20260610/final_submission_reviewer_open_file_checksum_index.json"
        ],
        "after": ["final_submission_reviewer_evidence_index"],
    },
    {
        "node_id": "final_submission_execution_blocker_owner_status_digest",
        "command": "python Scripts/quality/build_final_submission_execution_blocker_owner_status_digest.py",
        "outputs": [
            "Results/static_audits/final_submission_execution_blocker_owner_status_digest_20260610/final_submission_execution_blocker_owner_status_digest.json"
        ],
        "after": ["final_submission_reviewer_open_file_checksum_index"],
    },
    {
        "node_id": "final_submission_manual_review_shortest_path_note",
        "command": "python Scripts/quality/build_final_submission_manual_review_shortest_path_note.py",
        "outputs": [
            "Results/static_audits/final_submission_manual_review_shortest_path_20260610/final_submission_manual_review_shortest_path_note.json"
        ],
        "after": ["final_submission_execution_blocker_owner_status_digest"],
    },
    {
        "node_id": "final_submission_open_file_shortest_path_bundle",
        "command": "python Scripts/quality/build_final_submission_open_file_shortest_path_bundle.py",
        "outputs": [
            "Results/static_audits/final_submission_open_file_shortest_path_bundle_20260610/final_submission_open_file_shortest_path_bundle.json"
        ],
        "after": ["final_submission_manual_review_shortest_path_note"],
    },
    {
        "node_id": "final_submission_human_review_status_packet_skeleton",
        "command": "python Scripts/quality/build_final_submission_human_review_status_packet_skeleton.py",
        "outputs": [
            "Results/static_audits/final_submission_human_review_status_packet_skeleton_20260610/final_submission_human_review_status_packet_skeleton.json"
        ],
        "after": ["final_submission_open_file_shortest_path_bundle"],
    },
    {
        "node_id": "final_submission_status_packet_dependency_summary",
        "command": "python Scripts/quality/build_final_submission_status_packet_dependency_summary.py",
        "outputs": [
            "Results/static_audits/final_submission_status_packet_dependency_summary_20260610/final_submission_status_packet_dependency_summary.json"
        ],
        "after": ["final_submission_human_review_status_packet_skeleton"],
    },
]


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def validate_order(nodes: list[dict[str, Any]] = NODES) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []
    ids = [str(node.get("node_id", "")) for node in nodes]
    duplicates = sorted({node_id for node_id in ids if ids.count(node_id) > 1})
    if duplicates:
        issues.append("duplicate node ids: " + ", ".join(duplicates))

    known = set(ids)
    position = {node_id: index for index, node_id in enumerate(ids)}
    for node in nodes:
        node_id = str(node.get("node_id", ""))
        after = node.get("after", [])
        if not isinstance(after, list):
            issues.append(f"{node_id}.after must be a list")
            after = []
        for dep in after:
            dep = str(dep)
            if dep not in known:
                issues.append(f"{node_id} depends on unknown node {dep}")
            elif position[dep] >= position[node_id]:
                issues.append(f"{node_id} appears before dependency {dep}")
        outputs = node.get("outputs", [])
        if not isinstance(outputs, list) or not outputs:
            issues.append(f"{node_id}.outputs must be a non-empty list")
            outputs = []
        for output in outputs:
            if not repo_path(str(output)).exists():
                warnings.append(f"{node_id} output missing or not generated yet: {output}")

    serial_barriers = [
        "Do not run dashboard before final_output_execution_decision.",
        "Do not run source_edit_reviewer_summary before source_edit_application_plan.",
        "Do not run source_edit_application_audit_checklist before source_edit_reviewer_summary.",
        "Do not run source_output_readiness before source_edit_application_plan.",
        "Do not run human_action_checklist before dashboard.",
        "Do not run final_submission_reviewer_action_map before human_action_checklist.",
        "Do not run final_submission_human_review_decision_packet before reviewer_action_map.",
        "Do not run final_submission_human_review_guide before human_review_decision_packet.",
        "Do not run final_submission_readiness_chain before dashboard, human_action_checklist, reviewer_action_map, and human_review_decision_packet.",
        "Do not run final_submission_refresh_order before final_submission_readiness_chain.",
        "Do not run final_submission_static_audit_index before readiness_chain and refresh_order.",
        "Do not run final_submission_blocked_gate_triage_map before final_submission_static_audit_index.",
        "Do not run final_submission_human_decision_diff_template before final_submission_blocked_gate_triage_map.",
        "Do not run final_submission_reviewer_quickstart before final_submission_human_decision_diff_template.",
        "Do not run final_submission_review_progress_snapshot before final_submission_reviewer_quickstart.",
        "Do not run final_submission_post_review_rerun_matrix before final_submission_review_progress_snapshot.",
        "Do not run final_submission_manual_review_answer_sheet before final_submission_post_review_rerun_matrix.",
        "Do not run final_submission_answer_sheet_decision_consistency before final_submission_manual_review_answer_sheet.",
        "Do not run final_submission_review_artifact_bundle_index before final_submission_answer_sheet_decision_consistency.",
        "Do not run final_submission_reviewer_handoff_note before final_submission_review_artifact_bundle_index.",
        "Do not run final_submission_manual_review_closure_checklist before final_submission_reviewer_handoff_note.",
        "Do not run final_submission_post_review_state_transition_plan before final_submission_manual_review_closure_checklist.",
        "Do not run final_submission_post_review_command_plan_coverage before final_submission_post_review_state_transition_plan.",
        "Do not run final_submission_review_artifact_dependency_graph before final_submission_post_review_command_plan_coverage.",
        "Do not run final_submission_review_aid_freshness before final_submission_review_artifact_dependency_graph.",
        "Do not run final_submission_reviewer_packet_index before final_submission_review_aid_freshness.",
        "Do not run final_submission_blocker_question_crosswalk before final_submission_reviewer_packet_index.",
        "Do not run final_submission_post_review_command_grouping_index before final_submission_blocker_question_crosswalk.",
        "Do not run final_submission_post_review_command_critical_path_index before final_submission_post_review_command_grouping_index.",
        "Do not run final_submission_post_review_shared_tail_deduplication_note before final_submission_post_review_command_critical_path_index.",
        "Do not run final_submission_post_review_reviewer_checklist before final_submission_post_review_shared_tail_deduplication_note.",
        "Do not run final_submission_human_review_execution_gate_summary before final_submission_post_review_reviewer_checklist.",
        "Do not run final_submission_execution_authorization_blocker_index before final_submission_human_review_execution_gate_summary.",
        "Do not run final_submission_no_packet_action_escalation_note before final_submission_execution_authorization_blocker_index.",
        "Do not run final_submission_forbidden_action_guard before final_submission_no_packet_action_escalation_note.",
        "Do not run final_submission_reviewer_evidence_index before final_submission_forbidden_action_guard.",
        "Do not run final_submission_reviewer_open_file_checksum_index before final_submission_reviewer_evidence_index.",
        "Do not run final_submission_execution_blocker_owner_status_digest before final_submission_reviewer_open_file_checksum_index.",
        "Do not run final_submission_manual_review_shortest_path_note before final_submission_execution_blocker_owner_status_digest.",
        "Do not run final_submission_open_file_shortest_path_bundle before final_submission_manual_review_shortest_path_note.",
        "Do not run final_submission_human_review_status_packet_skeleton before final_submission_open_file_shortest_path_bundle.",
        "Do not run final_submission_status_packet_dependency_summary before final_submission_human_review_status_packet_skeleton.",
        "Do not run these dependent generators in parallel when they read/write the same static audit files.",
    ]

    return {
        "ok": not issues,
        "check_id": "final_submission_refresh_order_20260610",
        "status": "static_refresh_order_check_not_execution",
        "summary": {
            "node_count": len(nodes),
            "issue_count": len(issues),
            "warning_count": len(warnings),
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "nodes": nodes,
        "serial_barriers": serial_barriers,
        "issues": issues,
        "warnings": warnings,
        "claim_boundary": [
            "This checker validates refresh order only.",
            "It does not run generators.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(result: dict[str, Any], path: Path) -> None:
    summary = result["summary"]
    lines = [
        "# Final Submission Static Audit Refresh Order, 2026-06-10",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Summary",
        "",
        f"- OK: `{result['ok']}`",
        f"- Nodes: `{summary['node_count']}`",
        f"- Issues: `{summary['issue_count']}`",
        f"- Warnings: `{summary['warning_count']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Refresh Order",
        "",
    ]
    for index, node in enumerate(result["nodes"], start=1):
        after = ", ".join(node["after"]) if node["after"] else "none"
        lines.append(f"{index}. `{node['node_id']}` after `{after}`: `{node['command']}`")
    lines.extend(["", "## Serial Barriers", ""])
    for item in result["serial_barriers"]:
        lines.append(f"- {item}")
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

    result = validate_order()
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
