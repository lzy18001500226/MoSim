#!/usr/bin/env python3
"""Check current report/manual boundary notes.

This guard keeps user-facing docs aligned with the current static evidence
inventory: candidate manifests support drafting only, while live/runtime and
final submission claims still need separate evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "Docs" / "simulation_report.md"
MANUAL = ROOT / "Docs" / "user_manual.md"

REPORT_REQUIRED_TERMS = [
    "candidate_submission_evidence_manifest.json",
    "pre_submit_readiness_inventory.md",
    "candidate_figure_readiness_inventory.md",
    "candidate_report_table_scaffold.md",
    "final_packaging_gap_inventory.md",
    "final_report_outline_gap_inventory.md",
    "final_report_unmapped_claim_rewrite_plan.md",
    "simulation_report_source_hygiene_plan.md",
    "simulation_report_edit_sequence_plan.md",
    "simulation_report_patch_preview.md",
    "simulation_report_source_edit_readiness_gate.md",
    "simulation_report_source_edit_application_plan.md",
    "simulation_report_source_edit_reviewer_summary.md",
    "simulation_report_source_edit_application_audit_checklist.md",
    "submission_source_output_readiness.md",
    "final_submission_artifact_manifest_check.md",
    "pdf_export_dry_run_plan.md",
    "demo_video_storyboard_plan.md",
    "final_acceptance_packet_prereq_plan.md",
    "final_submission_readiness_dashboard.md",
    "final_submission_human_action_checklist.md",
    "final_submission_reviewer_action_map.md",
    "final_submission_human_review_decision_packet_template.md",
    "final_submission_human_review_guide.md",
    "report_source_edit_decision_template.md",
    "report_source_edit_decision_check.json",
    "final_submission_readiness_chain_check.md",
    "final_output_execution_decision_template.md",
    "final_submission_refresh_order_check.md",
    "final_submission_static_audit_index.md",
    "README.md",
    "Hard Gates",
    "Review Aids",
    "final_submission_blocked_gate_triage_map.md",
    "blocked artifacts",
    "blocker class",
    "final_submission_human_decision_diff_template.md",
    "pending A1/A6",
    "final_submission_reviewer_quickstart.md",
    "最小人工打开文件",
    "final_submission_review_progress_snapshot.md",
    "review progress snapshot",
    "final_submission_post_review_rerun_matrix.md",
    "post-review rerun matrix",
    "final_submission_manual_review_answer_sheet_template.md",
    "manual-review answer sheet",
    "final_submission_answer_sheet_decision_consistency_check.json",
    "answer-sheet consistency",
    "final_submission_review_artifact_bundle_index.md",
    "review artifact bundle",
    "final_submission_reviewer_handoff_note.md",
    "reviewer handoff note",
    "final_submission_manual_review_closure_checklist.md",
    "manual review closure checklist",
    "final_submission_post_review_state_transition_plan.md",
    "post-review state transition plan",
    "final_submission_post_review_command_plan_coverage_check.md",
    "post-review command plan coverage",
    "final_submission_review_artifact_dependency_graph.md",
    "review artifact dependency graph",
    "final_submission_review_aid_freshness_check.md",
    "review-aid freshness",
    "final_submission_reviewer_packet_index.md",
    "reviewer packet index",
    "final_submission_blocker_question_crosswalk.md",
    "blocker-to-question crosswalk",
    "final_submission_post_review_command_grouping_index.md",
    "post-review command grouping index",
    "final_submission_post_review_command_critical_path_index.md",
    "post-review command critical-path index",
    "final_submission_post_review_shared_tail_deduplication_note.md",
    "post-review shared-tail deduplication note",
    "final_submission_post_review_reviewer_checklist.md",
    "post-review reviewer checklist",
    "final_submission_human_review_execution_gate_summary.md",
    "human-review execution gate summary",
    "final_submission_execution_authorization_blocker_index.md",
    "execution authorization blocker index",
    "final_submission_no_packet_action_escalation_note.md",
    "no-packet action escalation note",
    "final_submission_forbidden_action_guard_check.md",
    "forbidden-action guard",
    "final_submission_reviewer_evidence_index.md",
    "reviewer evidence index",
    "final_submission_reviewer_open_file_checksum_index.md",
    "reviewer open-file checksum index",
    "final_submission_execution_blocker_owner_status_digest.md",
    "execution-blocker owner/status digest",
    "final_submission_manual_review_shortest_path_note.md",
    "manual-review shortest-path note",
    "final_submission_open_file_shortest_path_bundle.md",
    "open-file shortest-path bundle",
    "final_submission_human_review_status_packet_skeleton.md",
    "human-review status packet skeleton",
    "final_submission_status_packet_dependency_summary.md",
    "status-packet dependency summary",
    "不是最终 PMO 验收",
    "native Syslab",
    "live MWORKS no-start attach",
    "planner_ready",
    "closed_loop",
    "UE build/runtime/editor",
]

MANUAL_REQUIRED_TERMS = [
    "Windows 原生 Codex",
    "check_candidate_submission_manifest.py",
    "check_pre_submit_manifest_alignment.py",
    "build_candidate_figure_readiness_inventory.py",
    "build_candidate_report_table_scaffold.py",
    "build_pre_submit_readiness_inventory.py",
    "build_final_packaging_gap_inventory.py",
    "build_final_report_outline_gap_inventory.py",
    "build_final_report_unmapped_claim_rewrite_plan.py",
    "build_simulation_report_source_hygiene_plan.py",
    "build_simulation_report_edit_sequence_plan.py",
    "build_simulation_report_patch_preview.py",
    "check_simulation_report_patch_preview.py",
    "build_simulation_report_source_edit_readiness_gate.py",
    "build_simulation_report_source_edit_application_plan.py",
    "build_simulation_report_source_edit_reviewer_summary.py",
    "build_simulation_report_source_edit_application_audit_checklist.py",
    "build_submission_source_output_readiness.py",
    "check_final_submission_artifact_manifest.py",
    "build_pdf_export_dry_run_plan.py",
    "build_demo_video_storyboard_plan.py",
    "build_final_acceptance_packet_prereq_plan.py",
    "build_final_submission_readiness_dashboard.py",
    "build_final_submission_human_action_checklist.py",
    "build_final_submission_reviewer_action_map.py",
    "build_final_submission_human_review_decision_packet_template.py",
    "build_final_submission_human_review_guide.py",
    "build_report_source_edit_decision_template.py",
    "check_report_source_edit_decision.py",
    "check_final_submission_readiness_chain.py",
    "build_final_output_execution_decision_template.py",
    "check_final_output_execution_decision.py",
    "check_final_submission_refresh_order.py",
    "build_final_submission_static_audit_index.py",
    "build_final_submission_blocked_gate_triage_map.py",
    "build_final_submission_human_decision_diff_template.py",
    "build_final_submission_reviewer_quickstart.py",
    "build_final_submission_review_progress_snapshot.py",
    "build_final_submission_post_review_rerun_matrix.py",
    "build_final_submission_manual_review_answer_sheet_template.py",
    "check_final_submission_answer_sheet_decision_consistency.py",
    "build_final_submission_review_artifact_bundle_index.py",
    "build_final_submission_reviewer_handoff_note.py",
    "build_final_submission_manual_review_closure_checklist.py",
    "build_final_submission_post_review_state_transition_plan.py",
    "check_final_submission_post_review_command_plan_coverage.py",
    "build_final_submission_review_artifact_dependency_graph.py",
    "check_final_submission_review_aid_freshness.py",
    "build_final_submission_reviewer_packet_index.py",
    "build_final_submission_blocker_question_crosswalk.py",
    "build_final_submission_post_review_command_grouping_index.py",
    "build_final_submission_post_review_command_critical_path_index.py",
    "build_final_submission_post_review_shared_tail_deduplication_note.py",
    "build_final_submission_post_review_reviewer_checklist.py",
    "build_final_submission_human_review_execution_gate_summary.py",
    "build_final_submission_execution_authorization_blocker_index.py",
    "build_final_submission_no_packet_action_escalation_note.py",
    "check_final_submission_forbidden_action_guard.py",
    "build_final_submission_reviewer_evidence_index.py",
    "build_final_submission_reviewer_open_file_checksum_index.py",
    "build_final_submission_execution_blocker_owner_status_digest.py",
    "build_final_submission_manual_review_shortest_path_note.py",
    "build_final_submission_open_file_shortest_path_bundle.py",
    "build_final_submission_human_review_status_packet_skeleton.py",
    "build_final_submission_status_packet_dependency_summary.py",
    "static_figure_inventory_not_final_report_acceptance",
    "draft_table_scaffold_not_final_report_acceptance",
    "static_inventory_not_final_submission_acceptance",
    "final_packaging_gap_inventory_not_final_acceptance",
    "static_report_outline_gap_not_final_acceptance",
    "draft_rewrite_plan_not_final_report_acceptance",
    "draft_hygiene_plan_not_report_edit",
    "draft_edit_sequence_not_report_edit",
    "draft_patch_preview_not_report_edit",
    "simulation report patch preview checker returns ok=true",
    "safe_to_apply_report_source_edits_now=false",
    "source_edit_application_plan_blocked_pending_human_review",
    "source_edit_application_plan_applied=false",
    "source_edit_reviewer_summary_not_execution",
    "manual_review_required_count=7",
    "source_edit_application_audit_checklist_not_execution",
    "pre_edit_check_count=7",
    "post_edit_guard_command_count=16",
    "safe_to_export_final_pdfs_now=false",
    "final_artifacts_missing_not_final_submission",
    "dry_run_pdf_export_plan_not_final_output",
    "safe_to_run_pdf_export_now=false",
    "runs_pandoc_now=false",
    "generates_final_outputs=false",
    "storyboard_plan_not_demo_video_acceptance",
    "safe_to_record_demo_video_now=false",
    "records_or_renders_video_now=false",
    "blocked_template_not_final_acceptance",
    "safe_to_write_final_acceptance_packet_now=false",
    "writes_canonical_acceptance_packet_now=false",
    "final_acceptance=false",
    "static_dashboard_not_final_submission_acceptance",
    "blocking_gate_count=7",
    "human_action_checklist_not_execution",
    "source_blocker_count=16",
    "action_count=6",
    "automated_execution_allowed=false",
    "reviewer_action_map_not_execution",
    "missing_review_artifact_count=0",
    "human_review_decision_packet_pending_review_not_execution",
    "human_review_decision_packet_check_not_execution",
    "pending_decision_count=3",
    "human_review_guide_not_execution",
    "review_step_count=3",
    "decision_template_pending_review_not_approval",
    "safe_to_apply_report_source_edits=false",
    "authorizes_application=false",
    "static_chain_check_not_final_submission",
    "issue_count=0",
    "execution_decision_template_pending_review_not_execution",
    "authorizes_pdf_export=false",
    "authorizes_demo_video_recording=false",
    "authorizes_final_acceptance_packet=false",
    "static_refresh_order_check_not_execution",
    "node_count=50",
    "static_audit_index_not_final_submission",
    "artifact_count=18",
    "blocked_count=17",
    "final submission static audit README distinguishes Hard Gates from Review Aids for review only",
    "blocked_gate_triage_map_not_execution",
    "blocked_artifact_count=17",
    "dashboard_blocker_count=16",
    "human_decision_diff_template_not_execution",
    "report_source_field_count=8",
    "final_output_action_count=3",
    "final_output_field_count=15",
    "applies_decisions_now=false",
    "reviewer_quickstart_not_execution",
    "review_action_count=3",
    "minimum_open_file_count=10",
    "missing_open_file_count=0",
    "review_progress_snapshot_not_execution",
    "review_aid_count=3",
    "pending_review_action_count=3",
    "post_review_rerun_matrix_not_execution",
    "matrix_row_count=3",
    "blocked_pending_review_row_count=3",
    "runs_rerun_commands_now=false",
    "manual_review_answer_sheet_template_not_execution",
    "answer_field_count=38",
    "required_answer_field_count=29",
    "copies_answers_now=false",
    "answer_sheet_decision_consistency_check_not_execution",
    "unfilled_placeholder_field_count=38",
    "copied_field_count=0",
    "review_artifact_bundle_index_not_execution",
    "bundle_artifact_count=7",
    "ready_bundle_artifact_count=7",
    "included_in_static_audit_index=false",
    "reviewer_handoff_note_not_execution",
    "handoff_step_count=5",
    "approves_or_executes_now=false",
    "manual_review_closure_checklist_not_execution",
    "closure_item_count=3",
    "runs_rerun_commands_now=false",
    "post_review_state_transition_plan_not_execution",
    "transition_count=3",
    "applies_transitions_now=false",
    "post_review_command_plan_coverage_check_not_execution",
    "unique_command_count=20",
    "covered_unique_command_count=20",
    "review_artifact_dependency_graph_not_execution",
    "review_node_count=12",
    "dependency_edge_count=11",
    "review_aid_freshness_check_not_execution",
    "stale_dependency_count=0",
    "refreshes_artifacts_now=false",
    "reviewer_packet_index_not_execution",
    "packet_count=3",
    "total_answer_field_count=38",
    "blocker_question_crosswalk_not_execution",
    "crosswalk_row_count=16",
    "question_backed_row_count=9",
    "post_review_command_grouping_index_not_execution",
    "family_count=18",
    "total_command_reference_count=45",
    "post_review_command_critical_path_index_not_execution",
    "critical_path_count=3",
    "shared_tail_family_count=12",
    "unique_action_specific_family_count=6",
    "post_review_shared_tail_deduplication_note_not_execution",
    "shared_tail_action_coverage_issue_count=0",
    "post_review_reviewer_checklist_not_execution",
    "review_action_count=3",
    "actions_without_reviewer_packet_count=3",
    "total_question_count=9",
    "human_review_execution_gate_summary_not_execution",
    "execution_target_count=4",
    "blocked_execution_target_count=4",
    "dashboard_blocking_gate_count=7",
    "execution_authorization_blocker_index_not_execution",
    "unique_reviewer_packet_action_count=3",
    "unique_no_packet_action_count=3",
    "target_action_reference_count=16",
    "authorizes_execution_now=false",
    "no_packet_action_escalation_note_not_execution",
    "no_packet_action_count=3",
    "environment_dependency_count=1",
    "final_artifact_creation_count=1",
    "post_change_gate_rerun_count=1",
    "reviewer_packet_created_now=false",
    "forbidden_action_guard_not_execution",
    "pdf_export_still_forbidden=true",
    "demo_recording_still_forbidden=true",
    "final_acceptance_still_forbidden=true",
    "live_tools_still_forbidden=true",
    "visible_thread_dispatch_still_forbidden=true",
    "reviewer_evidence_index_not_execution",
    "reviewer_packet_action_count=3",
    "unique_review_evidence_file_count=21",
    "reviewer_open_file_checksum_index_not_execution",
    "unique_open_file_count=21",
    "total_open_file_reference_count=33",
    "drift_from_previous_output_count=0",
    "execution_blocker_owner_status_digest_not_execution",
    "owner_count=4",
    "blocked_execution_target_count=4",
    "dashboard_blocker_count=16",
    "manual_review_shortest_path_note_not_execution",
    "path_step_count=6",
    "human_review_action_count=3",
    "no_packet_action_count=3",
    "open_file_shortest_path_bundle_not_execution",
    "unique_open_file_count=21",
    "reused_open_file_reference_count=12",
]

FORBIDDEN_MANUAL_TERMS = [
    "当前 WSL 自动化优先",
]


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def validate(report_path: Path = REPORT, manual_path: Path = MANUAL) -> dict:
    issues: list[str] = []
    warnings: list[str] = []

    report_text = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
    manual_text = manual_path.read_text(encoding="utf-8") if manual_path.exists() else ""

    if not report_text:
        issues.append(f"missing report: {rel(report_path)}")
    if not manual_text:
        issues.append(f"missing manual: {rel(manual_path)}")

    for term in REPORT_REQUIRED_TERMS:
        if term not in report_text:
            issues.append(f"simulation_report missing boundary term: {term}")

    for term in MANUAL_REQUIRED_TERMS:
        if term not in manual_text:
            issues.append(f"user_manual missing current workflow term: {term}")

    for term in FORBIDDEN_MANUAL_TERMS:
        if term in manual_text:
            issues.append(f"user_manual still contains obsolete term: {term}")

    if "final submission readiness" in report_text and "not final" not in report_text.lower():
        warnings.append("report mentions final submission readiness without nearby not-final boundary")

    return {
        "ok": not issues,
        "report": rel(report_path),
        "manual": rel(manual_path),
        "issues": issues,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", help="Optional validation report path")
    args = parser.parse_args()

    try:
        result = validate()
    except Exception as exc:
        result = {
            "ok": False,
            "report": rel(REPORT),
            "manual": rel(MANUAL),
            "issues": [str(exc)],
            "warnings": [],
        }

    if args.output_json:
        output = Path(args.output_json)
        if not output.is_absolute():
            output = ROOT / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
