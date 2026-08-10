#!/usr/bin/env python3
"""Check pre-submit workflow alignment with the candidate evidence manifest.

This is a lightweight prose guard. It prevents the pre-submit workflow from
forgetting that the current static evidence manifest is a review candidate,
not final PMO acceptance or live/runtime success.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
import re


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DOC = ROOT / "Docs" / "Workflows" / "pre_submit_check.md"
DEFAULT_DETAIL_DOC = ROOT / "Docs" / "Cache" / "workflow_history" / "release" / "pre_submit_detail.md"
DEFAULT_MANIFEST = (
    ROOT
    / "Results"
    / "static_audits"
    / "submission_evidence_manifest_20260610"
    / "candidate_submission_evidence_manifest.json"
)

REQUIRED_DETAIL_TERMS = [
    "candidate_submission_evidence_manifest.json",
    "review_candidate_not_final_acceptance",
    "metrics-only rows",
    "needs_iteration rows",
    "native Syslab",
    "live MWORKS no-start attach",
    "ROS2",
    "planner_ready",
    "closed_loop",
    "UE build/runtime/editor",
    "not final PMO acceptance",
    "candidate figure readiness inventory",
    "candidate_figure_readiness_inventory.json",
    "static_figure_inventory_not_final_report_acceptance",
    "not_ready_count=0",
    "candidate report table scaffold",
    "candidate_report_table_scaffold.json",
    "drafting scaffold",
    "pre-submit readiness inventory",
    "candidate_paths_ready=true",
    "final_review_missing_count=0",
    "final packaging gap inventory",
    "final_packaging_gap_inventory.json",
    "final_packaging_gap_inventory_not_final_acceptance",
    "final_submission_ready=true",
    "final acceptance packet",
    "final report outline gap inventory",
    "final_report_outline_gap_inventory.json",
    "static_report_outline_gap_not_final_acceptance",
    "unmapped claim families",
    "final report unmapped claim rewrite plan",
    "final_report_unmapped_claim_rewrite_plan.json",
    "draft_rewrite_plan_not_final_report_acceptance",
    "patch-ready wording",
    "simulation report source hygiene plan",
    "simulation_report_source_hygiene_plan.json",
    "draft_hygiene_plan_not_report_edit",
    "does not edit Docs/报告/仿真分析报告_正文骨架.md",
    "simulation report edit sequence plan",
    "simulation_report_edit_sequence_plan.json",
    "draft_edit_sequence_not_report_edit",
    "does not apply edits",
    "simulation report patch preview",
    "simulation_report_patch_preview.json",
    "draft_patch_preview_not_report_edit",
    "non-applying preview",
    "check_simulation_report_patch_preview.py",
    "forbidden final/runtime claim boundaries",
    "simulation report source edit readiness gate",
    "simulation_report_source_edit_readiness_gate.json",
    "source_edit_application_blocked_pending_human_review",
    "safe_to_apply_report_source_edits_now=false",
    "simulation report source edit application plan",
    "simulation_report_source_edit_application_plan.json",
    "source_edit_application_plan_blocked_pending_human_review",
    "source_edit_application_plan_applied=false",
    "build_simulation_report_source_edit_application_plan.py",
    "simulation report source edit reviewer summary",
    "simulation_report_source_edit_reviewer_summary.json",
    "source_edit_reviewer_summary_not_execution",
    "manual_review_required_count=7",
    "build_simulation_report_source_edit_reviewer_summary.py",
    "simulation report source edit application audit checklist",
    "simulation_report_source_edit_application_audit_checklist.json",
    "source_edit_application_audit_checklist_not_execution",
    "pre_edit_check_count=7",
    "post_edit_guard_command_count=16",
    "build_simulation_report_source_edit_application_audit_checklist.py",
    "submission source output readiness",
    "submission_source_output_readiness.json",
    "static_source_output_readiness_not_final_submission",
    "safe_to_export_final_pdfs_now=false",
    "final submission artifact manifest check",
    "final_submission_artifact_manifest_check.json",
    "final_artifacts_missing_not_final_submission",
    "final_submission_artifacts_ready=false",
    "check_final_submission_artifact_manifest.py",
    "PDF export dry-run plan",
    "pdf_export_dry_run_plan.json",
    "dry_run_pdf_export_plan_not_final_output",
    "safe_to_run_pdf_export_now=false",
    "runs_pandoc_now=false",
    "generates_final_outputs=false",
    "build_pdf_export_dry_run_plan.py",
    "demo video storyboard plan",
    "demo_video_storyboard_plan.json",
    "storyboard_plan_not_demo_video_acceptance",
    "storyboard_ready_for_review=true",
    "safe_to_record_demo_video_now=false",
    "records_or_renders_video_now=false",
    "build_demo_video_storyboard_plan.py",
    "final acceptance packet prerequisite plan",
    "final_acceptance_packet_prereq_plan.json",
    "PMO-FINAL-SUBMISSION-ACCEPTANCE.draft-template.json",
    "blocked_template_not_final_acceptance",
    "draft_template_not_final_acceptance",
    "safe_to_write_final_acceptance_packet_now=false",
    "writes_canonical_acceptance_packet_now=false",
    "final_acceptance=false",
    "build_final_acceptance_packet_prereq_plan.py",
    "final submission readiness dashboard",
    "final_submission_readiness_dashboard.json",
    "static_dashboard_not_final_submission_acceptance",
    "blocking_gate_count=7",
    "build_final_submission_readiness_dashboard.py",
    "final submission human action checklist",
    "final_submission_human_action_checklist.json",
    "human_action_checklist_not_execution",
    "source_blocker_count=16",
    "action_count=6",
    "automated_execution_allowed=false",
    "build_final_submission_human_action_checklist.py",
    "final submission reviewer action map",
    "final_submission_reviewer_action_map.json",
    "reviewer_action_map_not_execution",
    "missing_review_artifact_count=0",
    "build_final_submission_reviewer_action_map.py",
    "final submission human review decision packet",
    "final_submission_human_review_decision_packet_check.json",
    "human_review_decision_packet_pending_review_not_execution",
    "human_review_decision_packet_check_not_execution",
    "pending_decision_count=3",
    "build_final_submission_human_review_decision_packet_template.py",
    "final submission human review guide",
    "final_submission_human_review_guide.json",
    "human_review_guide_not_execution",
    "review_step_count=3",
    "build_final_submission_human_review_guide.py",
    "report source edit decision template",
    "report_source_edit_decision_template.json",
    "report_source_edit_decision.template.json",
    "report_source_edit_decision_check.json",
    "decision_template_pending_review_not_approval",
    "decision=pending_review",
    "safe_to_apply_report_source_edits=false",
    "authorizes_application=false",
    "build_report_source_edit_decision_template.py",
    "check_report_source_edit_decision.py",
    "final submission readiness chain checker",
    "final_submission_readiness_chain_check.json",
    "static_chain_check_not_final_submission",
    "issue_count=0",
    "check_final_submission_readiness_chain.py",
    "final output execution decision template",
    "final_output_execution_decision_template.json",
    "final_output_execution_decision.template.json",
    "final_output_execution_decision_check.json",
    "execution_decision_template_pending_review_not_execution",
    "execution_decision_check_not_execution",
    "authorizes_pdf_export=false",
    "authorizes_demo_video_recording=false",
    "authorizes_final_acceptance_packet=false",
    "creates_submission_dir_now=false",
    "records_or_renders_video_now=false",
    "writes_canonical_acceptance_packet_now=false",
    "build_final_output_execution_decision_template.py",
    "check_final_output_execution_decision.py",
    "final submission refresh order checker",
    "final_submission_refresh_order_check.json",
    "static_refresh_order_check_not_execution",
    "node_count=50",
    "check_final_submission_refresh_order.py",
    "final submission static audit index",
    "final_submission_static_audit_index.json",
    "Results/static_audits/final_submission_static_audit_index_20260610/README.md",
    "static_audit_index_not_final_submission",
    "artifact_count=18",
    "blocked_count=17",
    "README.md distinguishes Hard Gates from Review Aids for review only",
    "build_final_submission_static_audit_index.py",
    "final submission blocked-gate triage map",
    "final_submission_blocked_gate_triage_map.json",
    "blocked_gate_triage_map_not_execution",
    "blocked_artifact_count=17",
    "dashboard_blocker_count=16",
    "build_final_submission_blocked_gate_triage_map.py",
    "final_submission_human_decision_diff_template.json",
    "human_decision_diff_template_not_execution",
    "report_source_field_count=8",
    "final_output_action_count=3",
    "final_output_field_count=15",
    "applies_decisions_now=false",
    "edits_decision_templates_now=false",
    "build_final_submission_human_decision_diff_template.py",
    "final_submission_reviewer_quickstart.json",
    "reviewer_quickstart_not_execution",
    "review_action_count=3",
    "minimum_open_file_count=10",
    "missing_open_file_count=0",
    "build_final_submission_reviewer_quickstart.py",
    "final_submission_review_progress_snapshot.json",
    "review_progress_snapshot_not_execution",
    "review_aid_count=3",
    "pending_review_action_count=3",
    "build_final_submission_review_progress_snapshot.py",
    "final_submission_post_review_rerun_matrix.json",
    "post_review_rerun_matrix_not_execution",
    "matrix_row_count=3",
    "blocked_pending_review_row_count=3",
    "runs_rerun_commands_now=false",
    "build_final_submission_post_review_rerun_matrix.py",
    "final_submission_manual_review_answer_sheet_template.json",
    "manual_review_answer_sheet_template_not_execution",
    "answer_field_count=38",
    "required_answer_field_count=29",
    "copies_answers_now=false",
    "build_final_submission_manual_review_answer_sheet_template.py",
    "final_submission_answer_sheet_decision_consistency_check.json",
    "answer_sheet_decision_consistency_check_not_execution",
    "unfilled_placeholder_field_count=38",
    "copied_field_count=0",
    "check_final_submission_answer_sheet_decision_consistency.py",
    "final_submission_review_artifact_bundle_index.json",
    "review_artifact_bundle_index_not_execution",
    "bundle_artifact_count=7",
    "ready_bundle_artifact_count=7",
    "included_in_static_audit_index=false",
    "build_final_submission_review_artifact_bundle_index.py",
    "final_submission_reviewer_handoff_note.json",
    "reviewer_handoff_note_not_execution",
    "handoff_step_count=5",
    "approves_or_executes_now=false",
    "build_final_submission_reviewer_handoff_note.py",
    "final_submission_manual_review_closure_checklist.json",
    "manual_review_closure_checklist_not_execution",
    "closure_item_count=3",
    "runs_rerun_commands_now=false",
    "build_final_submission_manual_review_closure_checklist.py",
    "final_submission_post_review_state_transition_plan.json",
    "post_review_state_transition_plan_not_execution",
    "transition_count=3",
    "applies_transitions_now=false",
    "build_final_submission_post_review_state_transition_plan.py",
    "final_submission_post_review_command_plan_coverage_check.json",
    "post_review_command_plan_coverage_check_not_execution",
    "unique_command_count=20",
    "covered_unique_command_count=20",
    "check_final_submission_post_review_command_plan_coverage.py",
    "final_submission_review_artifact_dependency_graph.json",
    "review_artifact_dependency_graph_not_execution",
    "review_node_count=12",
    "dependency_edge_count=11",
    "build_final_submission_review_artifact_dependency_graph.py",
    "final_submission_review_aid_freshness_check.json",
    "review_aid_freshness_check_not_execution",
    "stale_dependency_count=0",
    "refreshes_artifacts_now=false",
    "check_final_submission_review_aid_freshness.py",
    "final_submission_reviewer_packet_index.json",
    "reviewer_packet_index_not_execution",
    "packet_count=3",
    "total_answer_field_count=38",
    "build_final_submission_reviewer_packet_index.py",
    "final_submission_blocker_question_crosswalk.json",
    "blocker_question_crosswalk_not_execution",
    "crosswalk_row_count=16",
    "question_backed_row_count=9",
    "build_final_submission_blocker_question_crosswalk.py",
    "final_submission_post_review_command_grouping_index.json",
    "post_review_command_grouping_index_not_execution",
    "family_count=18",
    "unique_command_count=20",
    "total_command_reference_count=45",
    "build_final_submission_post_review_command_grouping_index.py",
    "final_submission_post_review_command_critical_path_index.json",
    "post_review_command_critical_path_index_not_execution",
    "critical_path_count=3",
    "shared_tail_family_count=12",
    "unique_action_specific_family_count=6",
    "build_final_submission_post_review_command_critical_path_index.py",
    "final_submission_post_review_shared_tail_deduplication_note.json",
    "post_review_shared_tail_deduplication_note_not_execution",
    "shared_tail_family_count=12",
    "shared_tail_action_coverage_issue_count=0",
    "build_final_submission_post_review_shared_tail_deduplication_note.py",
    "final_submission_post_review_reviewer_checklist.json",
    "post_review_reviewer_checklist_not_execution",
    "review_action_count=3",
    "actions_without_reviewer_packet_count=3",
    "total_question_count=9",
    "build_final_submission_post_review_reviewer_checklist.py",
    "final_submission_human_review_execution_gate_summary.json",
    "human_review_execution_gate_summary_not_execution",
    "execution_target_count=4",
    "blocked_execution_target_count=4",
    "dashboard_blocking_gate_count=7",
    "build_final_submission_human_review_execution_gate_summary.py",
    "final_submission_execution_authorization_blocker_index.json",
    "execution_authorization_blocker_index_not_execution",
    "unique_reviewer_packet_action_count=3",
    "unique_no_packet_action_count=3",
    "target_action_reference_count=16",
    "authorizes_execution_now=false",
    "build_final_submission_execution_authorization_blocker_index.py",
    "final_submission_no_packet_action_escalation_note.json",
    "no_packet_action_escalation_note_not_execution",
    "no_packet_action_count=3",
    "environment_dependency_count=1",
    "final_artifact_creation_count=1",
    "post_change_gate_rerun_count=1",
    "reviewer_packet_created_now=false",
    "build_final_submission_no_packet_action_escalation_note.py",
    "final_submission_forbidden_action_guard_check.json",
    "forbidden_action_guard_not_execution",
    "pdf_export_still_forbidden=true",
    "demo_recording_still_forbidden=true",
    "final_acceptance_still_forbidden=true",
    "live_tools_still_forbidden=true",
    "visible_thread_dispatch_still_forbidden=true",
    "check_final_submission_forbidden_action_guard.py",
    "final_submission_reviewer_evidence_index.json",
    "reviewer_evidence_index_not_execution",
    "reviewer_packet_action_count=3",
    "unique_review_evidence_file_count=21",
    "build_final_submission_reviewer_evidence_index.py",
    "final_submission_reviewer_open_file_checksum_index.json",
    "reviewer_open_file_checksum_index_not_execution",
    "unique_open_file_count=21",
    "total_open_file_reference_count=33",
    "drift_from_previous_output_count=0",
    "build_final_submission_reviewer_open_file_checksum_index.py",
    "final_submission_execution_blocker_owner_status_digest.json",
    "execution_blocker_owner_status_digest_not_execution",
    "owner_count=4",
    "blocked_execution_target_count=4",
    "dashboard_blocker_count=16",
    "build_final_submission_execution_blocker_owner_status_digest.py",
    "final_submission_manual_review_shortest_path_note.json",
    "manual_review_shortest_path_note_not_execution",
    "path_step_count=6",
    "human_review_action_count=3",
    "no_packet_action_count=3",
    "build_final_submission_manual_review_shortest_path_note.py",
    "final_submission_open_file_shortest_path_bundle.json",
    "open_file_shortest_path_bundle_not_execution",
    "unique_open_file_count=21",
    "reused_open_file_reference_count=12",
    "build_final_submission_open_file_shortest_path_bundle.py",
    "final_submission_human_review_status_packet_skeleton.json",
    "human_review_status_packet_skeleton_not_execution",
    "pending_field_count=38",
    "required_pending_field_count=29",
    "build_final_submission_human_review_status_packet_skeleton.py",
    "final_submission_status_packet_dependency_summary.json",
    "status_packet_dependency_summary_not_execution",
    "prerequisite_class_count=5",
    "satisfies_dependencies_now=false",
    "build_final_submission_status_packet_dependency_summary.py",
]

EXPECTED_HEADINGS = [
    "## 1. Goal",
    "## 2. Required Deliverables",
    "## 3. MCP Check",
    "## 4. Directory Check",
    "## 5. Required Experiment Check",
    "## 6. Metrics Check",
    "## 7. Candidate Evidence Manifest Check",
    "## 8. Figure Check",
    "## 9. Report Check",
    "## 10. Video Check",
    "## 11. Code Review Check",
    "## 12. Final Pass Criteria",
]

REQUIRED_ACTIVE_DOC_TERMS = [
    "Docs/Cache/workflow_history/release/pre_submit_detail.md",
    "Per-Task Git Closeout Gate",
    "git diff --cached --check",
    "candidate_submission_evidence_manifest.json",
    "review_candidate_not_final_acceptance",
    "not final PMO acceptance",
    "Final Pass Criteria",
]


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


def validate(
    doc_path: Path,
    manifest_path: Path,
    detail_path: Path = DEFAULT_DETAIL_DOC,
) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []

    if not doc_path.exists():
        issues.append(f"pre-submit doc does not exist: {rel(doc_path)}")
        doc_text = ""
    else:
        doc_text = doc_path.read_text(encoding="utf-8")

    if not detail_path.exists():
        issues.append(f"archived pre-submit detail does not exist: {rel(detail_path)}")
        detail_text = ""
    else:
        detail_text = detail_path.read_text(encoding="utf-8")

    if not manifest_path.exists():
        issues.append(f"candidate manifest does not exist: {rel(manifest_path)}")
        manifest = {}
    else:
        manifest = read_json(manifest_path)

    for term in REQUIRED_ACTIVE_DOC_TERMS:
        if term not in doc_text:
            issues.append(f"active pre-submit workflow missing required term: {term}")

    for term in REQUIRED_DETAIL_TERMS:
        if term not in detail_text:
            issues.append(f"archived pre-submit detail missing required boundary term: {term}")

    headings = [
        line.strip()
        for line in doc_text.splitlines()
        if re.match(r"^## \d+\. ", line.strip())
    ]
    if headings != EXPECTED_HEADINGS:
        issues.append(
            "pre-submit workflow heading sequence mismatch: "
            + " | ".join(headings)
        )

    status = manifest.get("status")
    if status != "review_candidate_not_final_acceptance":
        issues.append("manifest status must remain review_candidate_not_final_acceptance")

    manifest_rel = rel(manifest_path)
    if manifest_rel not in doc_text:
        warnings.append(f"pre-submit workflow does not mention canonical manifest path: {manifest_rel}")

    row_count = manifest.get("row_count")
    candidate_rows = manifest.get("candidate_rows")
    if isinstance(candidate_rows, list) and row_count != len(candidate_rows):
        issues.append("manifest row_count does not match candidate_rows length")

    return {
        "ok": not issues,
        "pre_submit_doc": rel(doc_path),
        "pre_submit_detail": rel(detail_path),
        "candidate_manifest": rel(manifest_path),
        "issues": issues,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pre_submit_doc", nargs="?", default=str(DEFAULT_DOC.relative_to(ROOT)))
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST.relative_to(ROOT)),
        help="Candidate submission evidence manifest JSON path",
    )
    parser.add_argument(
        "--detail",
        default=str(DEFAULT_DETAIL_DOC.relative_to(ROOT)),
        help="Archived detailed pre-submit reference path",
    )
    parser.add_argument("--output-json", help="Optional validation report path")
    args = parser.parse_args()

    doc_path = repo_path(args.pre_submit_doc)
    manifest_path = repo_path(args.manifest)
    detail_path = repo_path(args.detail)
    try:
        report = validate(doc_path, manifest_path, detail_path)
    except Exception as exc:
        report = {
            "ok": False,
            "pre_submit_doc": rel(doc_path),
            "pre_submit_detail": rel(detail_path),
            "candidate_manifest": rel(manifest_path),
            "issues": [str(exc)],
            "warnings": [],
        }

    if args.output_json:
        output = repo_path(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
