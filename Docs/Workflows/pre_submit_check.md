# Pre-Submit Check Workflow

> Purpose: verify that the project is ready for competition submission.

---

## 1. Goal

Before submission, check that the project contains required files, runnable models, reproducible experiments, valid metrics, report figures, and documentation.

---

## 2. Required Deliverables

The project should include:

```text
complete MWORKS model files
controller source files
scenario configuration files
planning / trajectory scripts if used
formation scripts or models if used
batch simulation scripts
raw simulation results
metrics tables
figures
user manual PDF
simulation analysis report PDF
demo video
README.md
AGENTS.md
```

---

## 3. MCP Check

Run `/mcp` in Codex.

Pass condition:

```text
syslab has tools
sysplorer_mcp has tools
```

Expected Syslab tools:

```text
detect_syslab_toolboxes
evaluate_julia_code
run_julia_file
search_syslab_docs
read_syslab_doc
```

Expected Sysplorer tools:

```text
session_manager
model_manager
check_model
simulate_model
result_manager
get_api_document
```

Notes:

```text
Auth: Unsupported is normal.
Tools: (none) is failure.
```

---

## 4. Directory Check

Required project entry points:

```text
Scripts/
Docs/
Docs/Index/
Docs/MworksDocs/converted/
Models/MoSimQuadrotorModel/Vehicle/
Docs/Workflows/
```

Implementation directories are created only when they contain real files:

```text
Config/controllers/
Config/planners/
Config/scenarios/
Scripts/tests/
Results/{group}/{scene}/{experiment}/raw/
Results/{group}/{scene}/{experiment}/metrics/
Results/{group}/{scene}/{experiment}/figures/
Docs/figures/
```

Run:

```bash
python Scripts/quality/qa_check.py
python Scripts/quality/check_reference_outputs.py
```

### Skill / Workflow Hygiene Check

Project-local skills and workflows must stay discoverable and credential-free:

```text
every `Docs/Skills/Mworks/*` skill has `SKILL.md`
each `SKILL.md` has YAML frontmatter with `name` and `description`
workflow links in `Docs/Index/workflow_index.md` resolve
no copied OAuth/provider configs, private `.env`, token, or key files are tracked
external skill/runtime repositories remain reference material unless explicitly promoted
```

### Per-Task Git Closeout Gate

Every task that changes project files must close its own Git slice before it
reports `complete`. A large unrelated worktree, a pending `References/` import,
or another task's dirty paths does not waive this gate.

Required closeout sequence:

1. Inspect tracked and untracked changes only under the task-owned paths.
2. Run targeted tests plus credential-like-content and oversized-file checks
   for those paths.
3. Stage only the exact reviewed task paths and inspect the staged file list.
4. Run the staged whitespace/error check, then create a scoped commit.
5. Push the current branch and verify that it is synchronized with upstream.

Closeout rules:

1. `complete` requires either no task-owned diff or a reviewed commit that has
   been pushed and verified against its upstream.
2. Normal source, scripts, configs, models, and documentation are committed in
   their own scoped batch even when `References/` contains thousands of pending
   files.
3. Do not stage unrelated pre-existing changes. If task-owned edits overlap an
   unreviewed existing change and cannot be separated safely, return a blocker.
4. A local commit with an authentication, remote rejection, or network failure
   is not pushed completion. Preserve the commit and report the exact blocker.
5. Reference crawls and directory migrations use repo-sized drain batches. Pair
   an intentional old-path deletion with its corresponding new-path addition
   in the same reviewed migration commit whenever practical.
6. Broad staging, destructive cleanup, history rewriting, and forced remote
   updates are not shortcuts for this gate.

### Reference / Large-File / Secret Check

Before staging or packaging, inspect newly added reference trees and generated
assets. This is mandatory when `Docs/Skills/`, `References/`, `UE5/`, `Results/`,
or downloaded open-source repositories changed.

```bash
git status --short
find . -type f -size +100M -not -path './.git/*' -print
rg -n --hidden --glob '!.git/**' \
  '(API_KEY|SECRET|TOKEN|OAuth|oauth|Bearer |PRIVATE KEY|GITHUB_TOKEN|OPENAI_API_KEY|COMPOSIO_API_KEY)' \
  AGENTS.md README.md PROGRESS.md Config Docs Models References Results Scripts UE5
```

Rules:

1. Do not stage whole reference repositories only because they are useful for
   reading. Promote only selected project-owned files, manifests, or translated
   workflows.
2. External automation skills that require OAuth, SaaS accounts, browser
   profiles, or cross-workspace file organization are not submission assets.
3. Binary/fonts/media/reference payloads are allowed only when they are required
   project assets, under GitHub limits, and have clear license/source notes.
4. If a large or credential-like hit is intentional documentation, verify that
   it is an example placeholder, not a real token or private config.
5. If a source tree contains too many files to inspect or push safely, ignore
   the entire tree first, then unignore/stage/commit/push one reviewed slice at
   a time. Each slice must pass the checks above before the next slice is
   opened.

---

## 5. Required Experiment Check

At minimum, the following experiments should be runnable or documented:

```text
PID hover baseline
PID step baseline
PID figure8 baseline
optimized controller figure8
optimized controller spiral
wind disturbance scenario
mass change or motor fault scenario
```

Recommended additional experiments:

```text
path planning obstacle avoidance
three-UAV formation
formation switching
motor efficiency degradation
```

---

## 6. Metrics Check

For every experiment used in the report, verify that metrics exist.

Required metrics:

```text
position_rmse
max_position_error
steady_state_error
attitude_rmse
control_energy
```

For step response:

```text
overshoot
settling_time
rise_time
```

For robustness:

```text
disturbance_recovery_time
performance_degradation
improvement_over_baseline
```

For path planning:

```text
path_length
planning_time
minimum_obstacle_distance
trajectory_smoothness
```

For formation:

```text
formation_error_rmse
formation_error_max
minimum_inter_uav_distance
formation_keeping_rate
```

---

## 7. Candidate Evidence Manifest Check

Before drafting final report claims, build or verify a candidate submission
evidence manifest. The manifest is a review input, not final PMO acceptance.

Current static-review manifest:

```text
Results/static_audits/submission_evidence_manifest_20260610/candidate_submission_evidence_manifest.json
Results/static_audits/candidate_report_table_scaffold_20260610/candidate_report_table_scaffold.json
Results/static_audits/candidate_report_table_scaffold_20260610/candidate_report_table_scaffold.md
Results/static_audits/final_report_outline_gap_20260610/final_report_outline_gap_inventory.json
Results/static_audits/final_report_outline_gap_20260610/final_report_outline_gap_inventory.md
Results/static_audits/final_report_unmapped_claim_rewrite_20260610/final_report_unmapped_claim_rewrite_plan.json
Results/static_audits/final_report_unmapped_claim_rewrite_20260610/final_report_unmapped_claim_rewrite_plan.md
Results/static_audits/simulation_report_source_hygiene_20260610/simulation_report_source_hygiene_plan.json
Results/static_audits/simulation_report_source_hygiene_20260610/simulation_report_source_hygiene_plan.md
Results/static_audits/simulation_report_edit_sequence_20260610/simulation_report_edit_sequence_plan.json
Results/static_audits/simulation_report_edit_sequence_20260610/simulation_report_edit_sequence_plan.md
Results/static_audits/simulation_report_patch_preview_20260610/simulation_report_patch_preview.json
Results/static_audits/simulation_report_patch_preview_20260610/simulation_report_patch_preview.md
Results/static_audits/simulation_report_source_edit_readiness_20260610/simulation_report_source_edit_readiness_gate.json
Results/static_audits/simulation_report_source_edit_readiness_20260610/simulation_report_source_edit_readiness_gate.md
Results/static_audits/simulation_report_source_edit_application_plan_20260610/simulation_report_source_edit_application_plan.json
Results/static_audits/simulation_report_source_edit_application_plan_20260610/simulation_report_source_edit_application_plan.md
Results/static_audits/simulation_report_source_edit_reviewer_summary_20260610/simulation_report_source_edit_reviewer_summary.json
Results/static_audits/simulation_report_source_edit_reviewer_summary_20260610/simulation_report_source_edit_reviewer_summary.md
Results/static_audits/simulation_report_source_edit_application_audit_checklist_20260610/simulation_report_source_edit_application_audit_checklist.json
Results/static_audits/simulation_report_source_edit_application_audit_checklist_20260610/simulation_report_source_edit_application_audit_checklist.md
Results/static_audits/submission_source_output_readiness_20260610/submission_source_output_readiness.json
Results/static_audits/submission_source_output_readiness_20260610/submission_source_output_readiness.md
Results/static_audits/final_submission_artifacts_20260610/final_submission_artifact_manifest_check.json
Results/static_audits/final_submission_artifacts_20260610/final_submission_artifact_manifest_check.md
Results/static_audits/pdf_export_dry_run_plan_20260610/pdf_export_dry_run_plan.json
Results/static_audits/pdf_export_dry_run_plan_20260610/pdf_export_dry_run_plan.md
Results/static_audits/demo_video_storyboard_plan_20260610/demo_video_storyboard_plan.json
Results/static_audits/demo_video_storyboard_plan_20260610/demo_video_storyboard_plan.md
Results/static_audits/final_acceptance_packet_prereq_20260610/final_acceptance_packet_prereq_plan.json
Results/static_audits/final_acceptance_packet_prereq_20260610/final_acceptance_packet_prereq_plan.md
Results/static_audits/final_acceptance_packet_prereq_20260610/PMO-FINAL-SUBMISSION-ACCEPTANCE.draft-template.json
Results/static_audits/final_submission_readiness_dashboard_20260610/final_submission_readiness_dashboard.json
Results/static_audits/final_submission_readiness_dashboard_20260610/final_submission_readiness_dashboard.md
Results/static_audits/final_submission_human_action_checklist_20260610/final_submission_human_action_checklist.json
Results/static_audits/final_submission_human_action_checklist_20260610/final_submission_human_action_checklist.md
Results/static_audits/final_submission_reviewer_action_map_20260610/final_submission_reviewer_action_map.json
Results/static_audits/final_submission_reviewer_action_map_20260610/final_submission_reviewer_action_map.md
Results/static_audits/final_submission_human_review_decision_packet_20260610/final_submission_human_review_decision_packet_template.json
Results/static_audits/final_submission_human_review_decision_packet_20260610/final_submission_human_review_decision_packet_template.md
Results/static_audits/final_submission_human_review_decision_packet_20260610/final_submission_human_review_decision_packet.template.json
Results/static_audits/final_submission_human_review_decision_packet_20260610/final_submission_human_review_decision_packet_check.json
Results/static_audits/final_submission_human_review_guide_20260610/final_submission_human_review_guide.json
Results/static_audits/final_submission_human_review_guide_20260610/final_submission_human_review_guide.md
Results/static_audits/report_source_edit_decision_template_20260610/report_source_edit_decision_template.json
Results/static_audits/report_source_edit_decision_template_20260610/report_source_edit_decision_template.md
Results/static_audits/report_source_edit_decision_template_20260610/report_source_edit_decision.template.json
Results/static_audits/report_source_edit_decision_template_20260610/report_source_edit_decision_check.json
Results/static_audits/final_submission_readiness_chain_20260610/final_submission_readiness_chain_check.json
Results/static_audits/final_submission_readiness_chain_20260610/final_submission_readiness_chain_check.md
Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision_template.json
Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision_template.md
Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision.template.json
Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision_check.json
Results/static_audits/final_submission_refresh_order_20260610/final_submission_refresh_order_check.json
Results/static_audits/final_submission_refresh_order_20260610/final_submission_refresh_order_check.md
Results/static_audits/final_submission_static_audit_index_20260610/final_submission_static_audit_index.json
Results/static_audits/final_submission_static_audit_index_20260610/final_submission_static_audit_index.md
Results/static_audits/final_submission_static_audit_index_20260610/README.md
Results/static_audits/final_submission_blocked_gate_triage_map_20260610/final_submission_blocked_gate_triage_map.json
Results/static_audits/final_submission_blocked_gate_triage_map_20260610/final_submission_blocked_gate_triage_map.md
Results/static_audits/final_submission_human_decision_diff_template_20260610/final_submission_human_decision_diff_template.json
Results/static_audits/final_submission_human_decision_diff_template_20260610/final_submission_human_decision_diff_template.md
Results/static_audits/final_submission_reviewer_quickstart_20260610/final_submission_reviewer_quickstart.json
Results/static_audits/final_submission_reviewer_quickstart_20260610/final_submission_reviewer_quickstart.md
Results/static_audits/final_submission_review_progress_snapshot_20260610/final_submission_review_progress_snapshot.json
Results/static_audits/final_submission_review_progress_snapshot_20260610/final_submission_review_progress_snapshot.md
Results/static_audits/final_submission_post_review_rerun_matrix_20260610/final_submission_post_review_rerun_matrix.json
Results/static_audits/final_submission_post_review_rerun_matrix_20260610/final_submission_post_review_rerun_matrix.md
Results/static_audits/final_submission_manual_review_answer_sheet_20260610/final_submission_manual_review_answer_sheet_template.json
Results/static_audits/final_submission_manual_review_answer_sheet_20260610/final_submission_manual_review_answer_sheet_template.md
Results/static_audits/final_submission_manual_review_answer_sheet_20260610/final_submission_manual_review_answer_sheet.template.json
Results/static_audits/final_submission_manual_review_answer_sheet_20260610/final_submission_answer_sheet_decision_consistency_check.json
Results/static_audits/final_submission_review_artifact_bundle_20260610/final_submission_review_artifact_bundle_index.json
Results/static_audits/final_submission_review_artifact_bundle_20260610/final_submission_review_artifact_bundle_index.md
Results/static_audits/final_submission_reviewer_handoff_note_20260610/final_submission_reviewer_handoff_note.json
Results/static_audits/final_submission_reviewer_handoff_note_20260610/final_submission_reviewer_handoff_note.md
Results/static_audits/final_submission_manual_review_closure_checklist_20260610/final_submission_manual_review_closure_checklist.json
Results/static_audits/final_submission_manual_review_closure_checklist_20260610/final_submission_manual_review_closure_checklist.md
Results/static_audits/final_submission_post_review_state_transition_plan_20260610/final_submission_post_review_state_transition_plan.json
Results/static_audits/final_submission_post_review_state_transition_plan_20260610/final_submission_post_review_state_transition_plan.md
Results/static_audits/final_submission_post_review_command_plan_coverage_20260610/final_submission_post_review_command_plan_coverage_check.json
Results/static_audits/final_submission_post_review_command_plan_coverage_20260610/final_submission_post_review_command_plan_coverage_check.md
Results/static_audits/final_submission_review_artifact_dependency_graph_20260610/final_submission_review_artifact_dependency_graph.json
Results/static_audits/final_submission_review_artifact_dependency_graph_20260610/final_submission_review_artifact_dependency_graph.md
Results/static_audits/final_submission_review_aid_freshness_20260610/final_submission_review_aid_freshness_check.json
Results/static_audits/final_submission_review_aid_freshness_20260610/final_submission_review_aid_freshness_check.md
Results/static_audits/final_submission_reviewer_packet_index_20260610/final_submission_reviewer_packet_index.json
Results/static_audits/final_submission_reviewer_packet_index_20260610/final_submission_reviewer_packet_index.md
Results/static_audits/final_submission_blocker_question_crosswalk_20260610/final_submission_blocker_question_crosswalk.json
Results/static_audits/final_submission_blocker_question_crosswalk_20260610/final_submission_blocker_question_crosswalk.md
Results/static_audits/final_submission_post_review_command_grouping_20260610/final_submission_post_review_command_grouping_index.json
Results/static_audits/final_submission_post_review_command_grouping_20260610/final_submission_post_review_command_grouping_index.md
Results/static_audits/final_submission_post_review_command_critical_path_20260610/final_submission_post_review_command_critical_path_index.json
Results/static_audits/final_submission_post_review_command_critical_path_20260610/final_submission_post_review_command_critical_path_index.md
Results/static_audits/final_submission_post_review_shared_tail_deduplication_20260610/final_submission_post_review_shared_tail_deduplication_note.json
Results/static_audits/final_submission_post_review_shared_tail_deduplication_20260610/final_submission_post_review_shared_tail_deduplication_note.md
Results/static_audits/final_submission_post_review_reviewer_checklist_20260610/final_submission_post_review_reviewer_checklist.json
Results/static_audits/final_submission_post_review_reviewer_checklist_20260610/final_submission_post_review_reviewer_checklist.md
Results/static_audits/final_submission_human_review_execution_gate_20260610/final_submission_human_review_execution_gate_summary.json
Results/static_audits/final_submission_human_review_execution_gate_20260610/final_submission_human_review_execution_gate_summary.md
Results/static_audits/final_submission_execution_authorization_blocker_20260610/final_submission_execution_authorization_blocker_index.json
Results/static_audits/final_submission_execution_authorization_blocker_20260610/final_submission_execution_authorization_blocker_index.md
Results/static_audits/final_submission_no_packet_action_escalation_20260610/final_submission_no_packet_action_escalation_note.json
Results/static_audits/final_submission_no_packet_action_escalation_20260610/final_submission_no_packet_action_escalation_note.md
Results/static_audits/final_submission_forbidden_action_guard_20260610/final_submission_forbidden_action_guard_check.json
Results/static_audits/final_submission_forbidden_action_guard_20260610/final_submission_forbidden_action_guard_check.md
Results/static_audits/final_submission_reviewer_evidence_index_20260610/final_submission_reviewer_evidence_index.json
Results/static_audits/final_submission_reviewer_evidence_index_20260610/final_submission_reviewer_evidence_index.md
Results/static_audits/final_submission_reviewer_open_file_checksum_index_20260610/final_submission_reviewer_open_file_checksum_index.json
Results/static_audits/final_submission_reviewer_open_file_checksum_index_20260610/final_submission_reviewer_open_file_checksum_index.md
Results/static_audits/final_submission_execution_blocker_owner_status_digest_20260610/final_submission_execution_blocker_owner_status_digest.json
Results/static_audits/final_submission_execution_blocker_owner_status_digest_20260610/final_submission_execution_blocker_owner_status_digest.md
Results/static_audits/final_submission_manual_review_shortest_path_20260610/final_submission_manual_review_shortest_path_note.json
Results/static_audits/final_submission_manual_review_shortest_path_20260610/final_submission_manual_review_shortest_path_note.md
Results/static_audits/final_submission_open_file_shortest_path_bundle_20260610/final_submission_open_file_shortest_path_bundle.json
Results/static_audits/final_submission_open_file_shortest_path_bundle_20260610/final_submission_open_file_shortest_path_bundle.md
Results/static_audits/final_submission_human_review_status_packet_skeleton_20260610/final_submission_human_review_status_packet_skeleton.json
Results/static_audits/final_submission_human_review_status_packet_skeleton_20260610/final_submission_human_review_status_packet_skeleton.md
Results/static_audits/final_submission_status_packet_dependency_summary_20260610/final_submission_status_packet_dependency_summary.json
Results/static_audits/final_submission_status_packet_dependency_summary_20260610/final_submission_status_packet_dependency_summary.md
```

Run:

```bash
python Scripts/quality/check_evidence_map_claim_boundary.py
python Scripts/quality/check_candidate_submission_manifest.py
python Scripts/quality/build_candidate_figure_readiness_inventory.py
python Scripts/quality/build_candidate_report_table_scaffold.py
python Scripts/quality/build_pre_submit_readiness_inventory.py
python Scripts/quality/build_final_packaging_gap_inventory.py
python Scripts/quality/build_final_report_outline_gap_inventory.py
python Scripts/quality/build_final_report_unmapped_claim_rewrite_plan.py
python Scripts/quality/build_simulation_report_source_hygiene_plan.py
python Scripts/quality/build_simulation_report_edit_sequence_plan.py
python Scripts/quality/build_simulation_report_patch_preview.py
python Scripts/quality/check_simulation_report_patch_preview.py
python Scripts/quality/build_simulation_report_source_edit_readiness_gate.py
python Scripts/quality/build_simulation_report_source_edit_application_plan.py
python Scripts/quality/build_simulation_report_source_edit_reviewer_summary.py
python Scripts/quality/build_simulation_report_source_edit_application_audit_checklist.py
python Scripts/quality/build_submission_source_output_readiness.py
python Scripts/quality/check_final_submission_artifact_manifest.py --allow-missing
python Scripts/quality/build_pdf_export_dry_run_plan.py
python Scripts/quality/build_demo_video_storyboard_plan.py
python Scripts/quality/build_final_acceptance_packet_prereq_plan.py
python Scripts/quality/build_final_submission_readiness_dashboard.py
python Scripts/quality/build_final_submission_human_action_checklist.py
python Scripts/quality/build_final_submission_reviewer_action_map.py
python Scripts/quality/build_final_submission_human_review_decision_packet_template.py
python Scripts/quality/build_final_submission_human_review_guide.py
python Scripts/quality/build_report_source_edit_decision_template.py
python Scripts/quality/check_report_source_edit_decision.py
python Scripts/quality/check_final_submission_readiness_chain.py
python Scripts/quality/build_final_output_execution_decision_template.py
python Scripts/quality/check_final_output_execution_decision.py
python Scripts/quality/check_final_submission_refresh_order.py
python Scripts/quality/build_final_submission_static_audit_index.py
python Scripts/quality/build_final_submission_blocked_gate_triage_map.py
python Scripts/quality/build_final_submission_human_decision_diff_template.py
python Scripts/quality/build_final_submission_reviewer_quickstart.py
python Scripts/quality/build_final_submission_review_progress_snapshot.py
python Scripts/quality/build_final_submission_post_review_rerun_matrix.py
python Scripts/quality/build_final_submission_manual_review_answer_sheet_template.py
python Scripts/quality/check_final_submission_answer_sheet_decision_consistency.py
python Scripts/quality/build_final_submission_review_artifact_bundle_index.py
python Scripts/quality/build_final_submission_reviewer_handoff_note.py
python Scripts/quality/build_final_submission_manual_review_closure_checklist.py
python Scripts/quality/build_final_submission_post_review_state_transition_plan.py
python Scripts/quality/check_final_submission_post_review_command_plan_coverage.py
python Scripts/quality/build_final_submission_review_artifact_dependency_graph.py
python Scripts/quality/check_final_submission_review_aid_freshness.py
python Scripts/quality/build_final_submission_reviewer_packet_index.py
python Scripts/quality/build_final_submission_blocker_question_crosswalk.py
python Scripts/quality/build_final_submission_post_review_command_grouping_index.py
python Scripts/quality/build_final_submission_post_review_command_critical_path_index.py
python Scripts/quality/build_final_submission_post_review_shared_tail_deduplication_note.py
python Scripts/quality/build_final_submission_post_review_reviewer_checklist.py
python Scripts/quality/build_final_submission_human_review_execution_gate_summary.py
python Scripts/quality/build_final_submission_execution_authorization_blocker_index.py
python Scripts/quality/build_final_submission_no_packet_action_escalation_note.py
python Scripts/quality/check_final_submission_forbidden_action_guard.py
python Scripts/quality/build_final_submission_reviewer_evidence_index.py
python Scripts/quality/build_final_submission_reviewer_open_file_checksum_index.py
python Scripts/quality/build_final_submission_execution_blocker_owner_status_digest.py
python Scripts/quality/build_final_submission_manual_review_shortest_path_note.py
python Scripts/quality/build_final_submission_open_file_shortest_path_bundle.py
python Scripts/quality/build_final_submission_human_review_status_packet_skeleton.py
python Scripts/quality/build_final_submission_status_packet_dependency_summary.py
```

Pass condition:

```text
manifest status is review_candidate_not_final_acceptance
candidate rows come only from source evidence-map candidate rows
metrics-only rows are not promoted into positive report evidence
needs_iteration rows are not promoted into positive report evidence
candidate figure readiness inventory has report_figure_ready_count equal to
  candidate_row_count and not_ready_count=0 before report figures are treated
  as ready for drafting
candidate report table scaffold has row_count equal to candidate_row_count,
  no missing figure slots, and no non-pass quality slots before it is used as
  report table input
final report outline gap inventory lists section-level static-update targets,
  human/live review sections, and unmapped candidate claim families before
  report source is rewritten
final report unmapped claim rewrite plan provides draft-only wording for any
  unmapped candidate claim families before they are inserted, reviewed, or
  explicitly excluded
simulation report source hygiene plan identifies stale/conflicting source
  areas before old-stage, smoke/staged, or numbering cleanup is attempted
simulation report edit sequence plan orders report-source edits before any
  source patch is applied
simulation report patch preview provides concrete before/after snippets but
  remains draft_patch_preview_not_report_edit
simulation report patch preview checker validates anchors, non-applying status,
  and forbidden final/runtime claim boundaries
simulation report source edit readiness gate remains blocked until explicit
  human/PMO approval exists for applying preview snippets
simulation report source edit application plan remains blocked until the A1
  report-source edit decision approves or narrows snippets, and it still does
  not apply edits by itself
simulation report source edit reviewer summary groups the seven preview
  snippets into A1 review questions while remaining non-executing
simulation report source edit application audit checklist records backup,
  diff, revert, and post-edit guard requirements for a future authorized edit
  while remaining non-executing
submission source output readiness confirms source docs/tooling state but
  keeps PDF/video/final acceptance generation blocked until approved
  report-source edits have separate application evidence
final submission artifact manifest check verifies final PDFs, demo video, and
  final acceptance packet presence but remains
  final_artifacts_missing_not_final_submission until all four artifacts exist
PDF export dry-run plan records future Pandoc commands but remains
  dry_run_pdf_export_plan_not_final_output and does not run Pandoc
demo video storyboard plan maps candidate evidence to scenes but remains
  storyboard_plan_not_demo_video_acceptance and does not record or render video
final acceptance packet prerequisite plan creates only a blocked draft template
  and keeps safe_to_write_final_acceptance_packet_now=false
final submission readiness dashboard aggregates static gates but remains
  static_dashboard_not_final_submission_acceptance while any gate is blocked
final submission human action checklist groups dashboard blockers into
  reviewable actions but remains human_action_checklist_not_execution
final submission reviewer action map binds those actions to owner decisions,
  review artifacts, and rerun commands while remaining
  reviewer_action_map_not_execution
final submission human review decision packet groups A1/A3/A6 decisions as
  pending templates while remaining
  human_review_decision_packet_pending_review_not_execution
final submission human review guide explains how to inspect those pending
  decisions while remaining human_review_guide_not_execution
report source edit decision template records a pending decision surface but
  remains decision_template_pending_review_not_approval
report source edit decision checker validates the decision file but keeps
  authorizes_application=false while decision=pending_review
final submission readiness chain checker confirms downstream artifact paths and
  blocked/not-final flags while remaining static_chain_check_not_final_submission
final output execution decision template/checker remains pending and does not
  authorize PDF export, video recording, or final acceptance packet writing
final submission refresh order checker records the serial generation order and
  remains static_refresh_order_check_not_execution
final submission static audit index summarizes current static audit artifacts
  but remains static_audit_index_not_final_submission
global exclusions keep native Syslab, live MWORKS no-start attach, ROS2
  planner_ready/closed_loop, and UE build/runtime/editor claims blocked unless
  separately proven
```

Rules:

1. A candidate manifest can support report drafting, table planning, and figure
   selection.
2. It cannot by itself accept final controller performance, final integration,
   live runtime success, or final submission readiness.
3. Any final claim must cite the exact run bundle, metrics file, figure, or
   reviewed packet that supports that claim.
4. `candidate_figure_readiness_inventory.json` only proves that local static
   metrics/raw/figure/replay/log files exist for candidate rows. It is not
   final PMO acceptance and does not prove live MWORKS, ROS2, UE, or native
   Syslab completion.
5. `candidate_report_table_scaffold.json` is a drafting scaffold. It does not
   rank controllers, choose final wording, or approve final performance claims.
6. `final_report_outline_gap_inventory.json` is a report editing plan. It does
   not edit the report, generate PDFs/video, or approve final acceptance.
7. `final_report_unmapped_claim_rewrite_plan.json` provides patch-ready draft
   wording only. It must not be treated as accepted report text.
8. `simulation_report_source_hygiene_plan.json` is a review aid for old-stage
   or conflicting report-source areas. It must not delete or edit report
   content by itself.
9. `simulation_report_edit_sequence_plan.json` is an ordered source-edit plan.
   It does not apply edits, delete historical evidence, or accept final claims.
10. `simulation_report_patch_preview.json` is a non-applying preview. It must
    not be treated as a patch file or an applied report edit.
11. `final_submission_artifact_manifest_check.json` is a final-output presence
    gate. It validates existing final artifacts only; it does not export PDFs,
    record or render video, or write PMO final acceptance.
12. `pdf_export_dry_run_plan.json` is a command plan only. It does not create
    `Results/submission`, run Pandoc, or write final PDFs.
13. `demo_video_storyboard_plan.json` is a storyboard and recording checklist
    only. It does not record, render, encode, or accept the demo video.
14. `final_acceptance_packet_prereq_plan.json` and the draft template under
    `static_audits` are not the canonical PMO final acceptance packet. They
    must not be copied to `Results/agent_packets/returns/` until final
    artifacts and manual/PMO review gates pass.
15. `final_submission_readiness_dashboard.json` is a static aggregation only.
    It does not replace manual/PMO review or final acceptance.
16. `final_submission_human_action_checklist.json` is a planning aid only. It
    does not approve, install tools, export PDFs, record video, or write final
    acceptance.
17. `final_submission_reviewer_action_map.json` is a reviewer aid only. It maps
    actions to owners, source artifacts, and rerun commands; it does not make
    decisions or execute commands.
18. `final_submission_human_review_decision_packet.template.json` is a pending
    human-review draft only. It groups A1/A3/A6 decisions, but it does not
    approve report edits, video recording, PDF export, or final acceptance.
19. `final_submission_human_review_guide.json` is an explanatory review guide
    only. It does not edit decisions, execute rerun commands, or change
    readiness state.
20. `report_source_edit_decision.template.json` is not an approval. It must
    remain `pending_review` unless the user/PMO explicitly decides approved,
    rejected, or narrowed scope.
21. `report_source_edit_decision_check.json` validates the decision artifact
    only. `ok=true` means the artifact is structurally valid; it does not mean
    report-source edits are authorized unless `authorizes_application=true`.
22. `final_submission_readiness_chain_check.json` validates static artifact
    chaining only. It must not be treated as final output generation,
    final-report approval, or PMO final acceptance.
23. `final_output_execution_decision.template.json` and
    `final_output_execution_decision_check.json` separate human execution
    approval from upstream readiness gates. `ok=true` on the checker means the
    decision surface is structurally valid; it does not authorize PDF export,
    demo video recording, or final acceptance unless each `authorizes_*` field
    is true.
24. `final_submission_refresh_order_check.json` is a static ordering guard. It
    records the generator order and serial barriers only; it must not be
    treated as executing the generators or creating final outputs.
25. `final_submission_static_audit_index.json` is a review index only. It
    summarizes static audit artifacts and blocked gates; it does not authorize
    PDF export, demo video recording, report-source edits, or PMO final
    acceptance. Its `README.md` separates `Hard Gates` from `Review Aids` for
    human reviewers without changing readiness or execution authority.
26. `final_submission_blocked_gate_triage_map.json` is a downstream review aid
    derived from the static audit index, dashboard, and reviewer action map. It
    groups blocked artifacts by blocker class, next human action, and safe
    rerun command; it does not execute those commands or reduce blocked gates.
27. `final_submission_human_decision_diff_template.json` is a non-applying
    review aid for pending A1/A6 human decision fields. It lists field paths,
    current values, allowed values, and required post-edit checkers; it does
    not edit the decision templates or approve pending decisions.
28. `final_submission_reviewer_quickstart.json` is a compact ordered human
    review guide for A1, A3, and A6. It lists the minimum files to open and
    review questions only; it does not edit decision artifacts, approve
    decisions, or run post-review checkers.
29. `final_submission_review_progress_snapshot.json` is a non-executing
    progress snapshot for the downstream review aids. It summarizes the triage
    map, decision diff template, and reviewer quickstart; it does not change
    gates, readiness, approval state, decision templates, or final outputs.
30. `final_submission_post_review_rerun_matrix.json` is a non-executing
    post-review rerun matrix. It lists what should be rerun after a future
    separate A1/A3/A6 human decision edit; it does not run commands, apply
    decisions, apply report-source edits, or authorize final-output execution.
31. `final_submission_manual_review_answer_sheet_template.json` is a
    non-applying manual-review answer sheet template for A1/A3/A6. It carries
    placeholders for human answers; it does not fill answers, copy answers into
    decision artifacts, edit templates, approve decisions, or run commands.
32. `final_submission_answer_sheet_decision_consistency_check.json` verifies
    the answer sheet still contains placeholders and that the current decision
    templates remain unapproved. It does not copy answer-sheet values, edit
    decision templates, approve decisions, or run post-review commands.
33. `final_submission_review_artifact_bundle_index.json` is a downstream
    review artifact bundle for human navigation. It intentionally stays out of
    `final_submission_static_audit_index.json` to avoid self-reference; it
    does not change gates, approve decisions, or execute commands.
34. `final_submission_reviewer_handoff_note.json` is a downstream reviewer
    handoff note. It orders the already-built bundle, answer sheet, and
    consistency check into review steps; it does not fill answer values, edit
    decision templates, approve decisions, run rerun commands, or generate
    final outputs.
35. `final_submission_manual_review_closure_checklist.json` is a downstream
    closure checklist for after future human review. It lists what must be
    confirmed after answer-sheet fields are filled in a separately authorized
    step; it does not copy answers, edit decision templates, approve
    decisions, run rerun commands, or generate final outputs.
36. `final_submission_post_review_state_transition_plan.json` is a static
    post-review state-transition plan. It shows which A1/A3/A6 gate chains
    become eligible only after separate human/PMO decision edits; it does not
    apply state transitions, edit decision templates, run rerun commands, or
    generate final outputs.
37. `final_submission_post_review_command_plan_coverage_check.json` validates
    that post-review transition command references point to existing
    `Scripts/quality/*.py` files. It does not run those commands, apply state
    transitions, edit decision templates, or generate final outputs.
38. `final_submission_review_artifact_dependency_graph.json` is a downstream
    review-aid dependency graph for the post-static-audit review artifacts. It
    records node/edge relationships only; it does not update the static audit
    index, run commands, apply transitions, edit decision templates, or
    generate final outputs.
39. `final_submission_review_aid_freshness_check.json` is a read-only
    freshness check for downstream review aids. It compares required outputs,
    statuses, and dependency mtimes only; it does not regenerate artifacts,
    run commands, update the static audit index, or generate final outputs.
40. `final_submission_reviewer_packet_index.json` is a reviewer navigation
    index for the pending A1/A3/A6 human decision packets. It maps each packet
    to review artifacts, answer-sheet fields, and post-review rerun commands;
    it does not fill answers, edit decision artifacts, approve decisions, or
    run commands.
41. `final_submission_blocker_question_crosswalk.json` is a blocker-to-question
    crosswalk for human review. It maps dashboard blockers and source blockers
    to reviewer packet questions where a packet exists; it does not answer
    questions, edit decision artifacts, approve decisions, or run commands.
42. `final_submission_post_review_command_grouping_index.json` is a static
    grouping index for future post-review rerun commands. It groups unique
    commands by artifact family and A1/A3/A6 decision action only; it does not
    run commands, apply transitions, edit decision artifacts, generate final
    outputs, or write PMO final acceptance.
43. `final_submission_post_review_command_critical_path_index.json` is a static
    critical-path index for future post-review rerun command families. It
    compresses already-listed commands into action-specific prefixes and a
    shared tail only; it does not run commands, choose live resource
    scheduling, apply transitions, edit decision artifacts, generate final
    outputs, or write PMO final acceptance.
44. `final_submission_post_review_shared_tail_deduplication_note.json` is a
    static note for common downstream command-family review. It identifies
    shared-tail families that appear in all A1/A3/A6 future rerun paths; it
    does not deduplicate executed work now, run commands, choose live resource
    scheduling, apply transitions, edit decision artifacts, generate final
    outputs, or write PMO final acceptance.
45. `final_submission_post_review_reviewer_checklist.json` is a static
    reviewer navigation checklist. It combines blocker questions, command
    grouping, critical paths, and shared-tail notes into A1/A3/A6 review items;
    it does not answer questions, fill answer-sheet values, edit decision
    artifacts, run commands, apply transitions, generate final outputs, or
    write PMO final acceptance.
46. `final_submission_human_review_execution_gate_summary.json` is a static
    execution-gate summary. It states which report edit, PDF export, demo
    recording, and final acceptance targets remain blocked before any separate
    execution authorization; it does not answer questions, edit decisions, run
    commands, create final outputs, or write PMO final acceptance.
47. `final_submission_execution_authorization_blocker_index.json` is a static
    execution authorization blocker index. It maps each blocked execution
    target to the human-review actions, no-packet actions, and future command
    families that must change before any separate execution authorization; it
    does not create reviewer packets, answer questions, edit decisions,
    authorize execution, run commands, create final outputs, or write PMO
    final acceptance.
48. `final_submission_no_packet_action_escalation_note.json` is a static
    escalation note for A2/A4/A5 no-packet actions. It explains why PDF-engine
    setup, final artifact creation, and post-change gate reruns require
    separate authorization instead of being folded into existing reviewer
    packets; it does not create packets, install tools, create artifacts, rerun
    gates, authorize execution, or generate final outputs.
49. `final_submission_forbidden_action_guard_check.json` is a static
    forbidden-action guard. It cross-checks current review aids still forbid
    PDF export, demo recording, final acceptance writing, live tools, and
    visible-thread dispatch until explicit authorization changes the relevant
    decision artifacts; it does not edit decisions, install tools, create final
    artifacts, run live tools, or dispatch visible threads.
50. `final_submission_reviewer_evidence_index.json` is a static reviewer
    evidence index. It lists the exact evidence files to open for A1/A3/A6
    reviewer-packet actions and A2/A4/A5 no-packet escalation actions; it does
    not fill answers, edit decision templates, approve execution, install
    tools, create final artifacts, run commands, or generate final outputs.
51. `final_submission_reviewer_open_file_checksum_index.json` is a static
    reviewer-open-file checksum index. It records size, mtime, and SHA256 for
    the 21 unique files listed by the reviewer evidence index so accidental
    drift can be detected; it does not open files in a UI, fill answers, edit
    decision templates, run commands, authorize execution, or generate final
    outputs.
52. `final_submission_execution_blocker_owner_status_digest.json` is a static
    owner/status digest. It groups current final-submission blockers by owner,
    required action, execution target, and blocker class so manual review can
    focus on the shortest unblocking path; it does not answer questions, edit
    decisions, run commands, authorize execution, or generate final outputs.
53. `final_submission_manual_review_shortest_path_note.json` is a static
    manual-review shortest-path note. It orders A1-A6 into a read-only review
    sequence and separates reviewer-packet actions from no-packet escalation
    actions; it does not answer questions, edit decisions, run commands,
    authorize execution, create final artifacts, or generate final outputs.
54. `final_submission_open_file_shortest_path_bundle.json` is a static
    open-file shortest-path bundle. It joins the A1-A6 shortest path with
    reviewer evidence and checksum metadata so repeated review files can be
    reused; it does not open files in a UI, answer questions, edit decisions,
    run commands, authorize execution, create final artifacts, or generate
    final outputs.
55. `final_submission_human_review_status_packet_skeleton.json` is a static
    human-review status packet skeleton. It lists which A1/A3/A6 fields remain
    intentionally blank and which A2/A4/A5 or dashboard prerequisites must
    change before any final-output execution can be requested; it does not fill
    answers, edit decision templates, create reviewer packets for no-packet
    actions, run commands, authorize execution, create final artifacts, or
    generate final outputs.
56. `final_submission_status_packet_dependency_summary.json` is a static
    dependency summary for the human-review status packet skeleton. It groups
    the 16 dashboard blockers into prerequisite classes and maps them back to
    A1-A6 review actions; it does not satisfy dependencies, answer questions,
    edit decision templates, run commands, authorize execution, create final
    artifacts, or generate final outputs.

---

## 8. Figure Check

Every report claim should have a figure or table.

Current static figure inventory:

```text
Results/static_audits/candidate_figure_readiness_20260610/candidate_figure_readiness_inventory.json
Results/static_audits/candidate_figure_readiness_20260610/candidate_figure_readiness_inventory.md
```

Run:

```bash
python Scripts/quality/build_candidate_figure_readiness_inventory.py
```

Pass condition for candidate report drafting:

```text
candidate_figure_readiness_inventory.json status is static_figure_inventory_not_final_report_acceptance
report_figure_ready_count equals candidate_row_count
not_ready_count=0
no missing core trajectory_xy, position_error, metrics_summary, or
  altitude_tracking figure for any candidate row
```

Required figures:

```text
environment setup screenshot
MCP verification screenshot
official quadrotor model screenshot
official PID controller screenshot
system architecture diagram
NMPC-INDI-L1 controller diagram
PID vs optimized 8-shaped trajectory
wind disturbance error curve
metrics comparison table or bar chart
```

Recommended figures:

```text
spiral trajectory
motor fault response
path planning obstacle map
planned path vs actual trajectory
formation trajectory
formation error curve
MCP tool call result
Syslab metrics generation result
```

---

## 9. Report Check

User manual must include:

```text
system overview
environment configuration
software installation
MCP configuration
how to open model
how to run simulation
how to reproduce scenarios
parameter explanation
interface explanation
common troubleshooting
```

Simulation report must include:

```text
algorithm design
system architecture
baseline PID analysis
optimized control method
experiment settings
metrics definition
comparison results
robustness analysis
scenario validation
innovation summary
conclusion
```

---

## 10. Video Check

Demo video should include:

```text
project overview
system architecture
baseline PID problem
optimized controller result
disturbance or fault scenario
path planning or formation if implemented
metrics and comparison
innovation summary
```

Length:

```text
<= 7 minutes
```

Do not show features that are not implemented.

---

## 11. Code Review Check

Before final submission, review:

```text
no broken absolute paths
no missing source files
no missing model dependencies
no untracked generated result required by report
no report claim without figure/metric
no copied code without source note
no temporary debug-only file in final package
```

---

## 12. Final Pass Criteria

A submission is ready if:

```text
MCP tools are available
baseline PID runs
optimized controller runs
metrics are generated
figures are generated
candidate submission evidence manifest validates
candidate figure readiness inventory exists
candidate figure readiness inventory has not_ready_count=0
pre-submit readiness inventory exists
pre-submit readiness inventory has candidate_paths_ready=true
pre-submit readiness inventory has final_review_missing_count=0
pre-submit readiness inventory has no unresolved live claim blocker for any
  claim included in the submitted report or demo video
final packaging gap inventory exists
final packaging gap inventory has source_inputs_ready=true,
  missing_final_artifact_count=0, and final_submission_ready=true
final report outline gap inventory exists
final report outline gap inventory has no unmapped claim families unless the
  final report intentionally excludes those claim families
final report unmapped claim rewrite plan exists when unmapped candidate
  families remain and remains draft_rewrite_plan_not_final_report_acceptance
simulation report source hygiene plan exists before old-stage or smoke/staged
  report-source cleanup and remains draft_hygiene_plan_not_report_edit
simulation report edit sequence plan exists before source edits are applied
  and remains draft_edit_sequence_not_report_edit
simulation report patch preview exists before reviewer-approved source edits
  and remains draft_patch_preview_not_report_edit
simulation report source edit readiness gate exists and keeps
  safe_to_apply_report_source_edits_now=false until explicit human/PMO approval
simulation report source edit application plan exists and keeps
  source_edit_application_plan_blocked_pending_human_review and
  source_edit_application_plan_applied=false until approved edits are applied
  in a separate authorized step
simulation report source edit reviewer summary exists and keeps
  source_edit_reviewer_summary_not_execution and manual_review_required_count=7
simulation report source edit application audit checklist exists and keeps
  source_edit_application_audit_checklist_not_execution,
  pre_edit_check_count=7, and post_edit_guard_command_count=16
submission source output readiness exists and keeps
  safe_to_export_final_pdfs_now=false while report-source edits are not
  approved or not applied
final submission artifact manifest check exists and keeps
  final_artifacts_missing_not_final_submission until final PDFs, demo video,
  and final acceptance packet exist
PDF export dry-run plan exists and keeps
  dry_run_pdf_export_plan_not_final_output, safe_to_run_pdf_export_now=false,
  runs_pandoc_now=false, and generates_final_outputs=false until explicit
  approval and tooling gates are satisfied
demo video storyboard plan exists and keeps
  storyboard_plan_not_demo_video_acceptance, safe_to_record_demo_video_now=false,
  and records_or_renders_video_now=false until manual storyboard review and
  recording approval exist
final acceptance packet prerequisite plan exists and keeps
  blocked_template_not_final_acceptance, safe_to_write_final_acceptance_packet_now=false,
  writes_canonical_acceptance_packet_now=false, and final_acceptance=false
  until reviewed final PDFs, demo video, and acceptance evidence exist
final submission readiness dashboard exists and keeps
  static_dashboard_not_final_submission_acceptance with final_submission_ready=false
  while any final-submission gate remains blocked
final submission human action checklist exists and keeps
  human_action_checklist_not_execution, automated_execution_allowed=false, and
  action_count=6 until a human or PMO owner executes the actions
report source edit decision template exists and keeps
  decision_template_pending_review_not_approval, decision=pending_review, and
  safe_to_apply_report_source_edits=false until an explicit user/PMO decision
  is recorded
report can reference saved figures and metrics
README and user manual explain how to reproduce results
video matches implemented features
final PDF files, demo video, and final acceptance packet exist
```

If any item fails, either fix it or remove the corresponding claim from the report.

Current static final-packaging gap inventory:

```text
Results/static_audits/final_packaging_gap_20260610/final_packaging_gap_inventory.json
Results/static_audits/final_packaging_gap_20260610/final_packaging_gap_inventory.md
```

Run:

```bash
python Scripts/quality/build_final_packaging_gap_inventory.py
```

Current boundary:

```text
final_packaging_gap_inventory.json status is final_packaging_gap_inventory_not_final_acceptance
source_inputs_ready=true means source docs and static inventories exist
final_submission_ready=false while user_manual.pdf,
  simulation_analysis_report.pdf, demo_video.mp4, or
  PMO-FINAL-SUBMISSION-ACCEPTANCE.json is missing
```

Current static final-report outline gap inventory:

```text
Results/static_audits/final_report_outline_gap_20260610/final_report_outline_gap_inventory.json
Results/static_audits/final_report_outline_gap_20260610/final_report_outline_gap_inventory.md
```

Run:

```bash
python Scripts/quality/build_final_report_outline_gap_inventory.py
```

Current boundary:

```text
final_report_outline_gap_inventory.json status is static_report_outline_gap_not_final_acceptance
static_update sections are report-editing candidates only
human_or_live_review sections and unmapped claim families require report
  review before final source rewrite or exclusion
```

Current static unmapped-claim rewrite plan:

```text
Results/static_audits/final_report_unmapped_claim_rewrite_20260610/final_report_unmapped_claim_rewrite_plan.json
Results/static_audits/final_report_unmapped_claim_rewrite_20260610/final_report_unmapped_claim_rewrite_plan.md
```

Run:

```bash
python Scripts/quality/build_final_report_unmapped_claim_rewrite_plan.py
```

Current boundary:

```text
final_report_unmapped_claim_rewrite_plan.json status is draft_rewrite_plan_not_final_report_acceptance
it provides patch-ready wording only and does not edit Docs/simulation_report.md
all wording keeps candidate_report_evidence_only_not_final_pmo_acceptance boundaries
```

Current static simulation-report source hygiene plan:

```text
Results/static_audits/simulation_report_source_hygiene_20260610/simulation_report_source_hygiene_plan.json
Results/static_audits/simulation_report_source_hygiene_20260610/simulation_report_source_hygiene_plan.md
```

Run:

```bash
python Scripts/quality/build_simulation_report_source_hygiene_plan.py
```

Current boundary:

```text
simulation_report_source_hygiene_plan.json status is draft_hygiene_plan_not_report_edit
it identifies obsolete, confusing, or conflicting source areas before report cleanup
it does not edit Docs/simulation_report.md, delete content, or change final acceptance
```

Current static simulation-report edit sequence plan:

```text
Results/static_audits/simulation_report_edit_sequence_20260610/simulation_report_edit_sequence_plan.json
Results/static_audits/simulation_report_edit_sequence_20260610/simulation_report_edit_sequence_plan.md
```

Run:

```bash
python Scripts/quality/build_simulation_report_edit_sequence_plan.py
```

Current boundary:

```text
simulation_report_edit_sequence_plan.json status is draft_edit_sequence_not_report_edit
it sequences report-source edits from the outline gap, unmapped rewrite, and hygiene plans
it does not edit Docs/simulation_report.md, delete historical evidence, or change final acceptance
```

Current static simulation-report patch preview:

```text
Results/static_audits/simulation_report_patch_preview_20260610/simulation_report_patch_preview.json
Results/static_audits/simulation_report_patch_preview_20260610/simulation_report_patch_preview.md
```

Run:

```bash
python Scripts/quality/build_simulation_report_patch_preview.py
```

Current boundary:

```text
simulation_report_patch_preview.json status is draft_patch_preview_not_report_edit
it provides concrete before/after snippets for review only
it does not edit Docs/simulation_report.md, generate an applyable patch, delete historical evidence, or change final acceptance
check_simulation_report_patch_preview.py returns ok=true before any reviewer-approved report edit uses this preview
```

Current static simulation-report source edit readiness gate:

```text
Results/static_audits/simulation_report_source_edit_readiness_20260610/simulation_report_source_edit_readiness_gate.json
Results/static_audits/simulation_report_source_edit_readiness_20260610/simulation_report_source_edit_readiness_gate.md
```

Run:

```bash
python Scripts/quality/build_simulation_report_source_edit_readiness_gate.py
```

Current boundary:

```text
simulation_report_source_edit_readiness_gate.json status is source_edit_application_blocked_pending_human_review
safe_to_apply_report_source_edits_now=false
the gate does not edit Docs/simulation_report.md or authorize automatic patch application
```

Current static simulation-report source edit application plan:

```text
Results/static_audits/simulation_report_source_edit_application_plan_20260610/simulation_report_source_edit_application_plan.json
Results/static_audits/simulation_report_source_edit_application_plan_20260610/simulation_report_source_edit_application_plan.md
```

Run:

```bash
python Scripts/quality/build_simulation_report_source_edit_application_plan.py
```

Current boundary:

```text
simulation_report_source_edit_application_plan.json status is source_edit_application_plan_blocked_pending_human_review
safe_to_apply_report_source_edits_now=false
source_edit_application_plan_applied=false
the plan turns approved previews into non-applying application steps only and does not edit Docs/simulation_report.md
```

Current static simulation-report source edit reviewer summary:

```text
Results/static_audits/simulation_report_source_edit_reviewer_summary_20260610/simulation_report_source_edit_reviewer_summary.json
Results/static_audits/simulation_report_source_edit_reviewer_summary_20260610/simulation_report_source_edit_reviewer_summary.md
```

Run:

```bash
python Scripts/quality/build_simulation_report_source_edit_reviewer_summary.py
```

Current boundary:

```text
simulation_report_source_edit_reviewer_summary.json status is source_edit_reviewer_summary_not_execution
manual_review_required_count=7
automated_execution_allowed=false
the summary groups preview impact, evidence inputs, and A1 review questions only; it does not approve or apply edits
```

Current static simulation-report source edit application audit checklist:

```text
Results/static_audits/simulation_report_source_edit_application_audit_checklist_20260610/simulation_report_source_edit_application_audit_checklist.json
Results/static_audits/simulation_report_source_edit_application_audit_checklist_20260610/simulation_report_source_edit_application_audit_checklist.md
```

Run:

```bash
python Scripts/quality/build_simulation_report_source_edit_application_audit_checklist.py
```

Current boundary:

```text
simulation_report_source_edit_application_audit_checklist.json status is source_edit_application_audit_checklist_not_execution
pre_edit_check_count=7
post_edit_guard_command_count=16
safe_to_apply_report_source_edits_now=false
the checklist documents future backup/diff/revert/post-edit guards only; it does not create backups, edit the report, or run guards
```

Current static submission source output readiness:

```text
Results/static_audits/submission_source_output_readiness_20260610/submission_source_output_readiness.json
Results/static_audits/submission_source_output_readiness_20260610/submission_source_output_readiness.md
```

Run:

```bash
python Scripts/quality/build_submission_source_output_readiness.py
```

Current boundary:

```text
submission_source_output_readiness.json status is static_source_output_readiness_not_final_submission
Pandoc available only means PDF export tooling is visible
safe_to_export_final_pdfs_now=false and final_submission_ready=false
the readiness inventory requires source edit readiness, application-plan approval, and separate application evidence before PDF export; it does not export PDFs, record video, edit report source, or write PMO final acceptance
```

Current static final submission artifact manifest check:

```text
Results/static_audits/final_submission_artifacts_20260610/final_submission_artifact_manifest_check.json
Results/static_audits/final_submission_artifacts_20260610/final_submission_artifact_manifest_check.md
```

Run current-state audit without turning missing final artifacts into a shell
failure:

```bash
python Scripts/quality/check_final_submission_artifact_manifest.py --allow-missing
```

Run final blocking gate before declaring submission ready:

```bash
python Scripts/quality/check_final_submission_artifact_manifest.py
```

Current boundary:

```text
final_submission_artifact_manifest_check.json status is final_artifacts_missing_not_final_submission
the checker validates existing final artifacts only if they exist
it does not create PDFs, record or render demo video, or write PMO final acceptance
final_submission_artifacts_ready=false while user_manual.pdf,
  simulation_analysis_report.pdf, demo_video.mp4, or
  PMO-FINAL-SUBMISSION-ACCEPTANCE.json is missing
```

Current static PDF export dry-run plan:

```text
Results/static_audits/pdf_export_dry_run_plan_20260610/pdf_export_dry_run_plan.json
Results/static_audits/pdf_export_dry_run_plan_20260610/pdf_export_dry_run_plan.md
```

Run:

```bash
python Scripts/quality/build_pdf_export_dry_run_plan.py
```

Current boundary:

```text
pdf_export_dry_run_plan.json status is dry_run_pdf_export_plan_not_final_output
safe_to_run_pdf_export_now=false
runs_pandoc_now=false and generates_final_outputs=false
the plan does not create Results/submission, write PDFs, record video, or write PMO final acceptance
```

Current static demo video storyboard plan:

```text
Results/static_audits/demo_video_storyboard_plan_20260610/demo_video_storyboard_plan.json
Results/static_audits/demo_video_storyboard_plan_20260610/demo_video_storyboard_plan.md
```

Run:

```bash
python Scripts/quality/build_demo_video_storyboard_plan.py
```

Current boundary:

```text
demo_video_storyboard_plan.json status is storyboard_plan_not_demo_video_acceptance
storyboard_ready_for_review=true means candidate rows and figure links are mapped for review only
safe_to_record_demo_video_now=false and records_or_renders_video_now=false
the plan does not record, render, encode, or create demo_video.mp4
the video must not claim planner_ready, closed_loop, UE build/runtime/editor success, or final acceptance
```

Current static final acceptance packet prerequisite plan:

```text
Results/static_audits/final_acceptance_packet_prereq_20260610/final_acceptance_packet_prereq_plan.json
Results/static_audits/final_acceptance_packet_prereq_20260610/final_acceptance_packet_prereq_plan.md
Results/static_audits/final_acceptance_packet_prereq_20260610/PMO-FINAL-SUBMISSION-ACCEPTANCE.draft-template.json
```

Run:

```bash
python Scripts/quality/build_final_acceptance_packet_prereq_plan.py
```

Current boundary:

```text
final_acceptance_packet_prereq_plan.json status is blocked_template_not_final_acceptance
the draft template status is draft_template_not_final_acceptance
safe_to_write_final_acceptance_packet_now=false
writes_canonical_acceptance_packet_now=false and final_acceptance=false
the plan does not write Results/agent_packets/returns/PMO-FINAL-SUBMISSION-ACCEPTANCE.json
```

Current static final submission readiness dashboard:

```text
Results/static_audits/final_submission_readiness_dashboard_20260610/final_submission_readiness_dashboard.json
Results/static_audits/final_submission_readiness_dashboard_20260610/final_submission_readiness_dashboard.md
```

Run:

```bash
python Scripts/quality/build_final_submission_readiness_dashboard.py
```

Current boundary:

```text
final_submission_readiness_dashboard.json status is static_dashboard_not_final_submission_acceptance
blocking_gate_count=7 and final_submission_ready=false
the dashboard does not export PDFs, record or render demo video, write PMO final acceptance, or replace manual/PMO review
```

Current static final submission human action checklist:

```text
Results/static_audits/final_submission_human_action_checklist_20260610/final_submission_human_action_checklist.json
Results/static_audits/final_submission_human_action_checklist_20260610/final_submission_human_action_checklist.md
```

Run:

```bash
python Scripts/quality/build_final_submission_human_action_checklist.py
```

Current boundary:

```text
final_submission_human_action_checklist.json status is human_action_checklist_not_execution
source_blocker_count=16 and action_count=6
automated_execution_allowed=false
the checklist does not approve report-source edits, install tools, export PDFs, record video, or write PMO final acceptance
```

Current static final submission reviewer action map:

```text
Results/static_audits/final_submission_reviewer_action_map_20260610/final_submission_reviewer_action_map.json
Results/static_audits/final_submission_reviewer_action_map_20260610/final_submission_reviewer_action_map.md
```

Run:

```bash
python Scripts/quality/build_final_submission_reviewer_action_map.py
```

Current boundary:

```text
final_submission_reviewer_action_map.json status is reviewer_action_map_not_execution
action_count=6
missing_review_artifact_count=0
automated_execution_allowed=false
generates_final_outputs=false and final_acceptance=false
the map links review actions to owner decisions, source artifacts, and rerun commands but does not approve decisions or execute commands
```

Current static final submission human review decision packet:

```text
Results/static_audits/final_submission_human_review_decision_packet_20260610/final_submission_human_review_decision_packet_template.json
Results/static_audits/final_submission_human_review_decision_packet_20260610/final_submission_human_review_decision_packet_template.md
Results/static_audits/final_submission_human_review_decision_packet_20260610/final_submission_human_review_decision_packet.template.json
Results/static_audits/final_submission_human_review_decision_packet_20260610/final_submission_human_review_decision_packet_check.json
```

Run:

```bash
python Scripts/quality/build_final_submission_human_review_decision_packet_template.py
```

Current boundary:

```text
final_submission_human_review_decision_packet_template.json status is human_review_decision_packet_pending_review_not_execution
final_submission_human_review_decision_packet_check.json status is human_review_decision_packet_check_not_execution
decision_count=3
pending_decision_count=3
automated_execution_allowed=false
generates_final_outputs=false and final_acceptance=false
the packet groups A1/A3/A6 decision surfaces only and does not approve decisions, apply edits, export PDFs, record video, or write PMO final acceptance
```

Current static final submission human review guide:

```text
Results/static_audits/final_submission_human_review_guide_20260610/final_submission_human_review_guide.json
Results/static_audits/final_submission_human_review_guide_20260610/final_submission_human_review_guide.md
```

Run:

```bash
python Scripts/quality/build_final_submission_human_review_guide.py
```

Current boundary:

```text
final_submission_human_review_guide.json status is human_review_guide_not_execution
review_step_count=3
pending_decision_count=3
automated_execution_allowed=false
generates_final_outputs=false and final_acceptance=false
the guide explains how to inspect pending A1/A3/A6 decisions but does not edit decisions, execute commands, apply edits, export PDFs, record video, or write PMO final acceptance
```

Current static final submission readiness chain check:

```text
Results/static_audits/final_submission_readiness_chain_20260610/final_submission_readiness_chain_check.json
Results/static_audits/final_submission_readiness_chain_20260610/final_submission_readiness_chain_check.md
```

Run:

```bash
python Scripts/quality/check_final_submission_readiness_chain.py
```

Current boundary:

```text
final_submission_readiness_chain_check.json status is static_chain_check_not_final_submission
issue_count=0
dashboard_blocking_gate_count=7
final_submission_ready=false
generates_final_outputs=false and final_acceptance=false
the checker validates static readiness artifact chaining only and does not export PDFs, record video, edit source docs, or write PMO final acceptance
```

Current static final output execution decision template:

```text
Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision_template.json
Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision_template.md
Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision.template.json
Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision_check.json
```

Run:

```bash
python Scripts/quality/build_final_output_execution_decision_template.py
python Scripts/quality/check_final_output_execution_decision.py
```

Current boundary:

```text
final_output_execution_decision_template.json status is execution_decision_template_pending_review_not_execution
final_output_execution_decision_check.json status is execution_decision_check_not_execution
authorizes_pdf_export=false
authorizes_demo_video_recording=false
authorizes_final_acceptance_packet=false
creates_submission_dir_now=false
runs_pandoc_now=false
records_or_renders_video_now=false
writes_canonical_acceptance_packet_now=false
generates_final_outputs=false and final_acceptance=false
the template/checker validates execution decisions only and does not create Results/submission, run Pandoc, record video, or write PMO final acceptance
```

Current static final submission refresh order check:

```text
Results/static_audits/final_submission_refresh_order_20260610/final_submission_refresh_order_check.json
Results/static_audits/final_submission_refresh_order_20260610/final_submission_refresh_order_check.md
```

Run:

```bash
python Scripts/quality/check_final_submission_refresh_order.py
```

Current boundary:

```text
final_submission_refresh_order_check.json status is static_refresh_order_check_not_execution
node_count=50
issue_count=0
the check records serial barriers such as source_edit_reviewer_summary after source_edit_application_plan, source_edit_application_audit_checklist after source_edit_reviewer_summary, source_output_readiness after source_edit_application_plan, dashboard after final_output_execution_decision, checklist after dashboard, reviewer_action_map after checklist, human_review_decision_packet after reviewer_action_map, guide after decision_packet, chain after dashboard/checklist/map/decision_packet, refresh_order after chain, static_audit_index after source_edit_reviewer_summary/audit_checklist/readiness_chain/refresh_order, blocked_gate_triage_map after static_audit_index, human_decision_diff_template after blocked_gate_triage_map, reviewer_quickstart after human_decision_diff_template, review_progress_snapshot after reviewer_quickstart, post_review_rerun_matrix after review_progress_snapshot, manual_review_answer_sheet after post_review_rerun_matrix, answer_sheet_decision_consistency after manual_review_answer_sheet, review_artifact_bundle_index after answer_sheet_decision_consistency, reviewer_handoff_note after review_artifact_bundle_index, manual_review_closure_checklist after reviewer_handoff_note, post_review_state_transition_plan after manual_review_closure_checklist, post_review_command_plan_coverage after post_review_state_transition_plan, review_artifact_dependency_graph after post_review_command_plan_coverage, review_aid_freshness after review_artifact_dependency_graph, reviewer_packet_index after review_aid_freshness, blocker_question_crosswalk after reviewer_packet_index, post_review_command_grouping_index after blocker_question_crosswalk, post_review_command_critical_path_index after post_review_command_grouping_index, post_review_shared_tail_deduplication_note after post_review_command_critical_path_index, post_review_reviewer_checklist after post_review_shared_tail_deduplication_note, human_review_execution_gate_summary after post_review_reviewer_checklist, execution_authorization_blocker_index after human_review_execution_gate_summary, no_packet_action_escalation_note after execution_authorization_blocker_index, forbidden_action_guard after no_packet_action_escalation_note, reviewer_evidence_index after forbidden_action_guard, reviewer_open_file_checksum_index after reviewer_evidence_index, execution_blocker_owner_status_digest after reviewer_open_file_checksum_index, manual_review_shortest_path_note after execution_blocker_owner_status_digest, and open_file_shortest_path_bundle after manual_review_shortest_path_note
the checker validates refresh order only and does not run generators, export PDFs, record video, or write PMO final acceptance
```

Current static final submission audit index:

```text
Results/static_audits/final_submission_static_audit_index_20260610/final_submission_static_audit_index.json
Results/static_audits/final_submission_static_audit_index_20260610/final_submission_static_audit_index.md
Results/static_audits/final_submission_static_audit_index_20260610/README.md
```

Run:

```bash
python Scripts/quality/build_final_submission_static_audit_index.py
```

Current boundary:

```text
final_submission_static_audit_index.json status is static_audit_index_not_final_submission
artifact_count=18
blocked_count=17
final_submission_ready=false
generates_final_outputs=false and final_acceptance=false
the index summarizes static audit artifacts only and does not run generators, export PDFs, record video, edit report source, or write PMO final acceptance
README.md distinguishes Hard Gates from Review Aids for review only
```

Current static final submission blocked-gate triage map:

```text
Results/static_audits/final_submission_blocked_gate_triage_map_20260610/final_submission_blocked_gate_triage_map.json
Results/static_audits/final_submission_blocked_gate_triage_map_20260610/final_submission_blocked_gate_triage_map.md
```

Run:

```bash
python Scripts/quality/build_final_submission_blocked_gate_triage_map.py
```

Current boundary:

```text
final_submission_blocked_gate_triage_map.json status is blocked_gate_triage_map_not_execution
blocked_artifact_count=17
dashboard_blocker_count=16
automated_execution_allowed=false
the map groups blocked artifacts by blocker class, next human action, and safe rerun command but does not run commands, export PDFs, record video, edit report source, or write PMO final acceptance
```

Current static human decision diff template:

```text
Results/static_audits/final_submission_human_decision_diff_template_20260610/final_submission_human_decision_diff_template.json
Results/static_audits/final_submission_human_decision_diff_template_20260610/final_submission_human_decision_diff_template.md
```

Run:

```bash
python Scripts/quality/build_final_submission_human_decision_diff_template.py
```

Current boundary:

```text
final_submission_human_decision_diff_template.json status is human_decision_diff_template_not_execution
report_source_field_count=8
final_output_action_count=3
final_output_field_count=15
applies_decisions_now=false
edits_decision_templates_now=false
the template lists pending decision fields only and does not approve decisions, edit templates, export PDFs, record video, edit report source, or write PMO final acceptance
```

Current static reviewer quickstart:

```text
Results/static_audits/final_submission_reviewer_quickstart_20260610/final_submission_reviewer_quickstart.json
Results/static_audits/final_submission_reviewer_quickstart_20260610/final_submission_reviewer_quickstart.md
```

Run:

```bash
python Scripts/quality/build_final_submission_reviewer_quickstart.py
```

Current boundary:

```text
final_submission_reviewer_quickstart.json status is reviewer_quickstart_not_execution
review_action_count=3
minimum_open_file_count=10
missing_open_file_count=0
automated_execution_allowed=false
the quickstart lists minimum A1/A3/A6 review files and questions only; it does not approve decisions, run checkers, export PDFs, record video, edit report source, or write PMO final acceptance
```

Current static review progress snapshot:

```text
Results/static_audits/final_submission_review_progress_snapshot_20260610/final_submission_review_progress_snapshot.json
Results/static_audits/final_submission_review_progress_snapshot_20260610/final_submission_review_progress_snapshot.md
```

Run:

```bash
python Scripts/quality/build_final_submission_review_progress_snapshot.py
```

Current boundary:

```text
final_submission_review_progress_snapshot.json status is review_progress_snapshot_not_execution
review_aid_count=3
pending_review_action_count=3
blocked_artifact_count=17
minimum_open_file_count=10
missing_open_file_count=0
automated_execution_allowed=false
the snapshot summarizes downstream review aids only; it does not change gates, readiness, approval state, decision templates, final outputs, or PMO final acceptance
```

Current static post-review rerun matrix:

```text
Results/static_audits/final_submission_post_review_rerun_matrix_20260610/final_submission_post_review_rerun_matrix.json
Results/static_audits/final_submission_post_review_rerun_matrix_20260610/final_submission_post_review_rerun_matrix.md
```

Run:

```bash
python Scripts/quality/build_final_submission_post_review_rerun_matrix.py
```

Current boundary:

```text
final_submission_post_review_rerun_matrix.json status is post_review_rerun_matrix_not_execution
matrix_row_count=3
blocked_pending_review_row_count=3
runs_rerun_commands_now=false
applies_decisions_now=false
automated_execution_allowed=false
the post-review rerun matrix lists future rerun order only; it does not edit decision templates, approve decisions, run commands, apply report-source edits, export PDFs, record video, or write PMO final acceptance
```

Current static manual-review answer sheet template:

```text
Results/static_audits/final_submission_manual_review_answer_sheet_20260610/final_submission_manual_review_answer_sheet_template.json
Results/static_audits/final_submission_manual_review_answer_sheet_20260610/final_submission_manual_review_answer_sheet_template.md
Results/static_audits/final_submission_manual_review_answer_sheet_20260610/final_submission_manual_review_answer_sheet.template.json
```

Run:

```bash
python Scripts/quality/build_final_submission_manual_review_answer_sheet_template.py
```

Current boundary:

```text
final_submission_manual_review_answer_sheet_template.json status is manual_review_answer_sheet_template_not_execution
answer_field_count=38
required_answer_field_count=29
copies_answers_now=false
edits_decision_artifacts_now=false
approves_or_executes_now=false
automated_execution_allowed=false
the manual-review answer sheet carries placeholders for future human answers only; it does not fill answers, copy answers into decision artifacts, edit templates, approve decisions, run commands, export PDFs, record video, or write PMO final acceptance
```

Current static answer-sheet decision consistency check:

```text
Results/static_audits/final_submission_manual_review_answer_sheet_20260610/final_submission_answer_sheet_decision_consistency_check.json
```

Run:

```bash
python Scripts/quality/check_final_submission_answer_sheet_decision_consistency.py
```

Current boundary:

```text
final_submission_answer_sheet_decision_consistency_check.json status is answer_sheet_decision_consistency_check_not_execution
answer_field_count=38
unfilled_placeholder_field_count=38
copied_field_count=0
final_output_pending_action_count=3
automated_execution_allowed=false
the answer-sheet consistency check compares placeholders and current decision templates only; it does not copy values, edit templates, approve decisions, run commands, apply report-source edits, export PDFs, record video, or write PMO final acceptance
```

Current static review artifact bundle index:

```text
Results/static_audits/final_submission_review_artifact_bundle_20260610/final_submission_review_artifact_bundle_index.json
Results/static_audits/final_submission_review_artifact_bundle_20260610/final_submission_review_artifact_bundle_index.md
```

Run:

```bash
python Scripts/quality/build_final_submission_review_artifact_bundle_index.py
```

Current boundary:

```text
final_submission_review_artifact_bundle_index.json status is review_artifact_bundle_index_not_execution
bundle_artifact_count=7
ready_bundle_artifact_count=7
included_in_static_audit_index=false
automated_execution_allowed=false
the review artifact bundle is a downstream human navigation aid only; it is not added back into final_submission_static_audit_index.json and does not edit templates, approve decisions, run commands, apply report-source edits, export PDFs, record video, or write PMO final acceptance
```

Current static reviewer handoff note:

```text
Results/static_audits/final_submission_reviewer_handoff_note_20260610/final_submission_reviewer_handoff_note.json
Results/static_audits/final_submission_reviewer_handoff_note_20260610/final_submission_reviewer_handoff_note.md
```

Run:

```bash
python Scripts/quality/build_final_submission_reviewer_handoff_note.py
```

Current boundary:

```text
final_submission_reviewer_handoff_note.json status is reviewer_handoff_note_not_execution
handoff_step_count=5
bundle_artifact_count=7
answer_field_count=38
copied_field_count=0
approves_or_executes_now=false
automated_execution_allowed=false
the reviewer handoff note orders existing review aids only; it does not fill answers, edit decision templates, approve decisions, run rerun commands, apply report-source edits, export PDFs, record video, or write PMO final acceptance
```

Current static manual-review closure checklist:

```text
Results/static_audits/final_submission_manual_review_closure_checklist_20260610/final_submission_manual_review_closure_checklist.json
Results/static_audits/final_submission_manual_review_closure_checklist_20260610/final_submission_manual_review_closure_checklist.md
```

Run:

```bash
python Scripts/quality/build_final_submission_manual_review_closure_checklist.py
```

Current boundary:

```text
final_submission_manual_review_closure_checklist.json status is manual_review_closure_checklist_not_execution
closure_item_count=3
answer_field_count=38
copied_field_count=0
runs_rerun_commands_now=false
copies_answers_now=false
edits_decision_templates_now=false
automated_execution_allowed=false
the manual-review closure checklist lists after-review confirmation items only; it does not copy answers, edit decision templates, approve decisions, run rerun commands, apply report-source edits, export PDFs, record video, or write PMO final acceptance
```

Current static post-review state-transition plan:

```text
Results/static_audits/final_submission_post_review_state_transition_plan_20260610/final_submission_post_review_state_transition_plan.json
Results/static_audits/final_submission_post_review_state_transition_plan_20260610/final_submission_post_review_state_transition_plan.md
```

Run:

```bash
python Scripts/quality/build_final_submission_post_review_state_transition_plan.py
```

Current boundary:

```text
final_submission_post_review_state_transition_plan.json status is post_review_state_transition_plan_not_execution
transition_count=3
dashboard_blocking_gate_count=7
applies_transitions_now=false
runs_rerun_commands_now=false
edits_decision_templates_now=false
automated_execution_allowed=false
the post-review state transition plan describes future eligibility only; it does not apply transitions, edit decision templates, approve decisions, run rerun commands, apply report-source edits, export PDFs, record video, or write PMO final acceptance
```

Current static post-review command-plan coverage check:

```text
Results/static_audits/final_submission_post_review_command_plan_coverage_20260610/final_submission_post_review_command_plan_coverage_check.json
Results/static_audits/final_submission_post_review_command_plan_coverage_20260610/final_submission_post_review_command_plan_coverage_check.md
```

Run:

```bash
python Scripts/quality/check_final_submission_post_review_command_plan_coverage.py
```

Current boundary:

```text
final_submission_post_review_command_plan_coverage_check.json status is post_review_command_plan_coverage_check_not_execution
transition_count=3
total_command_reference_count=45
unique_command_count=20
covered_unique_command_count=20
runs_rerun_commands_now=false
applies_transitions_now=false
automated_execution_allowed=false
the post-review command-plan coverage checker validates command references only; it does not run rerun commands, apply transitions, edit decision templates, approve decisions, apply report-source edits, export PDFs, record video, or write PMO final acceptance
```

Current static review artifact dependency graph:

```text
Results/static_audits/final_submission_review_artifact_dependency_graph_20260610/final_submission_review_artifact_dependency_graph.json
Results/static_audits/final_submission_review_artifact_dependency_graph_20260610/final_submission_review_artifact_dependency_graph.md
```

Run:

```bash
python Scripts/quality/build_final_submission_review_artifact_dependency_graph.py
```

Current boundary:

```text
final_submission_review_artifact_dependency_graph.json status is review_artifact_dependency_graph_not_execution
review_node_count=12
dependency_edge_count=11
missing_output_count=0
updates_static_audit_index=false
runs_commands_now=false
automated_execution_allowed=false
the review artifact dependency graph records downstream review-aid dependencies only; it does not run commands, update the static audit index, edit decision templates, approve decisions, apply report-source edits, export PDFs, record video, or write PMO final acceptance
```

Current static review-aid freshness check:

```text
Results/static_audits/final_submission_review_aid_freshness_20260610/final_submission_review_aid_freshness_check.json
Results/static_audits/final_submission_review_aid_freshness_20260610/final_submission_review_aid_freshness_check.md
```

Run:

```bash
python Scripts/quality/check_final_submission_review_aid_freshness.py
```

Current boundary:

```text
final_submission_review_aid_freshness_check.json status is review_aid_freshness_check_not_execution
review_node_count=13
dependency_edge_count=12
missing_output_count=0
status_mismatch_count=0
stale_dependency_count=0
refreshes_artifacts_now=false
runs_commands_now=false
updates_static_audit_index=false
automated_execution_allowed=false
the review-aid freshness checker reads downstream review-aid artifacts only; it does not regenerate artifacts, run commands, update the static audit index, edit decision templates, approve decisions, apply report-source edits, export PDFs, record video, or write PMO final acceptance
```

Current static reviewer packet index:

```text
Results/static_audits/final_submission_reviewer_packet_index_20260610/final_submission_reviewer_packet_index.json
Results/static_audits/final_submission_reviewer_packet_index_20260610/final_submission_reviewer_packet_index.md
```

Run:

```bash
python Scripts/quality/build_final_submission_reviewer_packet_index.py
```

Current boundary:

```text
final_submission_reviewer_packet_index.json status is reviewer_packet_index_not_execution
packet_count=3
pending_packet_count=3
total_answer_field_count=38
required_answer_field_count=29
total_rerun_command_count=45
fills_answers_now=false
copies_answers_now=false
edits_decision_artifacts_now=false
runs_rerun_commands_now=false
automated_execution_allowed=false
the reviewer packet index maps pending A1/A3/A6 human decisions to review files, answer fields, and future rerun commands only; it does not fill answers, edit decision artifacts, approve decisions, run rerun commands, apply report-source edits, export PDFs, record video, or write PMO final acceptance
```

Current static blocker-to-question crosswalk:

```text
Results/static_audits/final_submission_blocker_question_crosswalk_20260610/final_submission_blocker_question_crosswalk.json
Results/static_audits/final_submission_blocker_question_crosswalk_20260610/final_submission_blocker_question_crosswalk.md
```

Run:

```bash
python Scripts/quality/build_final_submission_blocker_question_crosswalk.py
```

Current boundary:

```text
final_submission_blocker_question_crosswalk.json status is blocker_question_crosswalk_not_execution
dashboard_blocker_count=16
crosswalk_row_count=16
reviewer_packet_action_count=3
actions_without_reviewer_packet_count=3
unmapped_dashboard_blocker_count=0
question_backed_row_count=9
answers_questions_now=false
edits_decision_artifacts_now=false
runs_rerun_commands_now=false
automated_execution_allowed=false
the blocker-to-question crosswalk maps blockers to review questions only; it does not answer questions, fill answer-sheet fields, edit decision artifacts, approve decisions, run rerun commands, apply report-source edits, export PDFs, record video, or write PMO final acceptance
```

Current static post-review command grouping index:

```text
Results/static_audits/final_submission_post_review_command_grouping_20260610/final_submission_post_review_command_grouping_index.json
Results/static_audits/final_submission_post_review_command_grouping_20260610/final_submission_post_review_command_grouping_index.md
```

Run:

```bash
python Scripts/quality/build_final_submission_post_review_command_grouping_index.py
```

Current boundary:

```text
final_submission_post_review_command_grouping_index.json status is post_review_command_grouping_index_not_execution
transition_count=3
unique_command_count=20
family_count=18
action_count=3
total_command_reference_count=45
action_count_mismatch_count=0
runs_commands_now=false
applies_transitions_now=false
edits_decision_artifacts_now=false
generates_final_outputs=false
final_acceptance=false
the post-review command grouping index groups future rerun commands by artifact family and decision action only; it does not execute commands, apply state transitions, edit decision artifacts, approve decisions, apply report-source edits, export PDFs, record video, or write PMO final acceptance
```

Current static post-review command critical-path index:

```text
Results/static_audits/final_submission_post_review_command_critical_path_20260610/final_submission_post_review_command_critical_path_index.json
Results/static_audits/final_submission_post_review_command_critical_path_20260610/final_submission_post_review_command_critical_path_index.md
```

Run:

```bash
python Scripts/quality/build_final_submission_post_review_command_critical_path_index.py
```

Current boundary:

```text
final_submission_post_review_command_critical_path_index.json status is post_review_command_critical_path_index_not_execution
critical_path_count=3
family_count=18
unique_command_count=20
total_command_reference_count=45
shared_tail_family_count=12
unique_action_specific_family_count=6
runs_commands_now=false
applies_transitions_now=false
edits_decision_artifacts_now=false
generates_final_outputs=false
final_acceptance=false
the post-review command critical-path index compresses already-listed future rerun commands into action-specific prefixes and a shared tail only; it does not execute commands, choose live resource scheduling, edit decision artifacts, approve decisions, apply report-source edits, export PDFs, record video, or write PMO final acceptance
```

Current static post-review shared-tail deduplication note:

```text
Results/static_audits/final_submission_post_review_shared_tail_deduplication_20260610/final_submission_post_review_shared_tail_deduplication_note.json
Results/static_audits/final_submission_post_review_shared_tail_deduplication_20260610/final_submission_post_review_shared_tail_deduplication_note.md
```

Run:

```bash
python Scripts/quality/build_final_submission_post_review_shared_tail_deduplication_note.py
```

Current boundary:

```text
final_submission_post_review_shared_tail_deduplication_note.json status is post_review_shared_tail_deduplication_note_not_execution
action_count=3
shared_tail_family_count=12
shared_tail_action_coverage_issue_count=0
action_specific_prefix_group_count=3
runs_commands_now=false
applies_transitions_now=false
edits_decision_artifacts_now=false
generates_final_outputs=false
final_acceptance=false
the post-review shared-tail deduplication note identifies common downstream review families only; it does not deduplicate executed work now, execute commands, choose live resource scheduling, edit decision artifacts, approve decisions, apply report-source edits, export PDFs, record video, or write PMO final acceptance
```

Current static post-review reviewer checklist:

```text
Results/static_audits/final_submission_post_review_reviewer_checklist_20260610/final_submission_post_review_reviewer_checklist.json
Results/static_audits/final_submission_post_review_reviewer_checklist_20260610/final_submission_post_review_reviewer_checklist.md
```

Run:

```bash
python Scripts/quality/build_final_submission_post_review_reviewer_checklist.py
```

Current boundary:

```text
final_submission_post_review_reviewer_checklist.json status is post_review_reviewer_checklist_not_execution
review_action_count=3
actions_without_reviewer_packet_count=3
total_blocker_row_count=9
total_question_count=9
total_command_reference_count=45
shared_tail_family_count=12
answers_questions_now=false
edits_decision_artifacts_now=false
runs_commands_now=false
applies_transitions_now=false
generates_final_outputs=false
final_acceptance=false
the post-review reviewer checklist combines review navigation only; it does not answer questions, fill answer-sheet values, edit decision artifacts, approve decisions, execute commands, apply report-source edits, export PDFs, record video, or write PMO final acceptance
```

Current static human-review execution gate summary:

```text
Results/static_audits/final_submission_human_review_execution_gate_20260610/final_submission_human_review_execution_gate_summary.json
Results/static_audits/final_submission_human_review_execution_gate_20260610/final_submission_human_review_execution_gate_summary.md
```

Run:

```bash
python Scripts/quality/build_final_submission_human_review_execution_gate_summary.py
```

Current boundary:

```text
final_submission_human_review_execution_gate_summary.json status is human_review_execution_gate_summary_not_execution
execution_target_count=4
blocked_execution_target_count=4
dashboard_blocking_gate_count=7
dashboard_blocker_count=16
review_action_count=3
total_question_count=9
answers_questions_now=false
edits_decision_artifacts_now=false
runs_commands_now=false
creates_submission_dir_now=false
runs_pandoc_now=false
records_or_renders_video_now=false
writes_canonical_acceptance_packet_now=false
generates_final_outputs=false
final_acceptance=false
the human-review execution gate summary states current execution blockers only; it does not answer questions, edit decisions, apply report-source edits, create Results/submission, run Pandoc, export PDFs, record video, or write canonical PMO final acceptance
```

Current static execution authorization blocker index:

```text
Results/static_audits/final_submission_execution_authorization_blocker_20260610/final_submission_execution_authorization_blocker_index.json
Results/static_audits/final_submission_execution_authorization_blocker_20260610/final_submission_execution_authorization_blocker_index.md
```

Run:

```bash
python Scripts/quality/build_final_submission_execution_authorization_blocker_index.py
```

Current boundary:

```text
final_submission_execution_authorization_blocker_index.json status is execution_authorization_blocker_index_not_execution
execution_target_count=4
blocked_execution_target_count=4
unique_reviewer_packet_action_count=3
unique_no_packet_action_count=3
target_action_reference_count=16
target_without_no_packet_action_count=1
answers_questions_now=false
fills_answers_now=false
edits_decision_artifacts_now=false
runs_commands_now=false
authorizes_execution_now=false
generates_final_outputs=false
final_acceptance=false
the execution authorization blocker index maps blocked execution targets to review actions and future command families only; it does not create reviewer packets for no-packet actions, answer questions, edit decisions, authorize execution, run commands, export PDFs, record video, or write PMO final acceptance
```

Current static no-packet action escalation note:

```text
Results/static_audits/final_submission_no_packet_action_escalation_20260610/final_submission_no_packet_action_escalation_note.json
Results/static_audits/final_submission_no_packet_action_escalation_20260610/final_submission_no_packet_action_escalation_note.md
```

Run:

```bash
python Scripts/quality/build_final_submission_no_packet_action_escalation_note.py
```

Current boundary:

```text
final_submission_no_packet_action_escalation_note.json status is no_packet_action_escalation_note_not_execution
no_packet_action_count=3
environment_dependency_count=1
final_artifact_creation_count=1
post_change_gate_rerun_count=1
total_referenced_target_count=8
missing_review_artifact_count=0
reviewer_packet_created_now=false
answers_questions_now=false
edits_decision_artifacts_now=false
runs_commands_now=false
authorizes_execution_now=false
generates_final_outputs=false
final_acceptance=false
the no-packet action escalation note explains A2/A4/A5 separate-authorization needs only; it does not create reviewer packets, install tools, create final artifacts, rerun gates, authorize execution, or generate final outputs
```

Current static final-submission forbidden-action guard:

```text
Results/static_audits/final_submission_forbidden_action_guard_20260610/final_submission_forbidden_action_guard_check.json
Results/static_audits/final_submission_forbidden_action_guard_20260610/final_submission_forbidden_action_guard_check.md
```

Run:

```bash
python Scripts/quality/check_final_submission_forbidden_action_guard.py
```

Current boundary:

```text
final_submission_forbidden_action_guard_check.json status is forbidden_action_guard_not_execution
artifact_count=16
false_flag_check_count=88
command_field_check_count=20
issue_count=0
pdf_export_still_forbidden=true
demo_recording_still_forbidden=true
final_acceptance_still_forbidden=true
live_tools_still_forbidden=true
visible_thread_dispatch_still_forbidden=true
generates_final_outputs=false
final_acceptance=false
the forbidden-action guard validates existing static review aids only; it does not edit decision templates, install PDF tooling, create Results/submission, run Pandoc, export PDFs, record/render demo video, write canonical PMO final acceptance, run MWORKS/ROS2/UE tools, or dispatch visible threads
```

Current static final-submission reviewer evidence index:

```text
Results/static_audits/final_submission_reviewer_evidence_index_20260610/final_submission_reviewer_evidence_index.json
Results/static_audits/final_submission_reviewer_evidence_index_20260610/final_submission_reviewer_evidence_index.md
```

Run:

```bash
python Scripts/quality/build_final_submission_reviewer_evidence_index.py
```

Current boundary:

```text
final_submission_reviewer_evidence_index.json status is reviewer_evidence_index_not_execution
action_count=6
reviewer_packet_action_count=3
no_packet_action_count=3
unique_review_evidence_file_count=21
missing_review_evidence_file_count=0
pdf_export_still_forbidden=true
demo_recording_still_forbidden=true
final_acceptance_still_forbidden=true
live_tools_still_forbidden=true
visible_thread_dispatch_still_forbidden=true
fills_answers_now=false
edits_decision_artifacts_now=false
runs_commands_now=false
authorizes_execution_now=false
generates_final_outputs=false
final_acceptance=false
the reviewer evidence index lists review files only; it does not fill answers, copy answers into decision artifacts, edit templates, approve decisions, install PDF tooling, create final artifacts, run commands, export PDFs, record video, write PMO final acceptance, or run live/visible-thread tools
```

Current static final-submission reviewer-open-file checksum index:

```text
Results/static_audits/final_submission_reviewer_open_file_checksum_index_20260610/final_submission_reviewer_open_file_checksum_index.json
Results/static_audits/final_submission_reviewer_open_file_checksum_index_20260610/final_submission_reviewer_open_file_checksum_index.md
```

Run:

```bash
python Scripts/quality/build_final_submission_reviewer_open_file_checksum_index.py
```

Current boundary:

```text
final_submission_reviewer_open_file_checksum_index.json status is reviewer_open_file_checksum_index_not_execution
unique_open_file_count=21
total_open_file_reference_count=33
duplicate_open_file_reference_count=12
checksum_file_count=21
missing_open_file_count=0
unreadable_open_file_count=0
drift_from_previous_output_count=0
runs_commands_now=false
authorizes_execution_now=false
generates_final_outputs=false
final_acceptance=false
the reviewer-open-file checksum index records path metadata and SHA256 only; it does not open files in a UI, fill answers, copy answers into decision artifacts, edit templates, approve decisions, install PDF tooling, create final artifacts, run commands, export PDFs, record video, write PMO final acceptance, or run live/visible-thread tools
```

Current static final-submission execution-blocker owner/status digest:

```text
Results/static_audits/final_submission_execution_blocker_owner_status_digest_20260610/final_submission_execution_blocker_owner_status_digest.json
Results/static_audits/final_submission_execution_blocker_owner_status_digest_20260610/final_submission_execution_blocker_owner_status_digest.md
```

Run:

```bash
python Scripts/quality/build_final_submission_execution_blocker_owner_status_digest.py
```

Current boundary:

```text
final_submission_execution_blocker_owner_status_digest.json status is execution_blocker_owner_status_digest_not_execution
owner_count=4
action_count=6
execution_target_count=4
blocked_execution_target_count=4
target_action_reference_count=16
blocked_artifact_count=17
blocker_class_count=10
dashboard_blocking_gate_count=7
dashboard_blocker_count=16
reviewer_open_file_count=21
reviewer_open_file_drift_count=0
runs_commands_now=false
authorizes_execution_now=false
generates_final_outputs=false
final_acceptance=false
the owner/status digest groups blockers by owner, required action, execution target, and blocker class only; it does not answer questions, copy answers into decision artifacts, edit templates, approve decisions, install PDF tooling, create final artifacts, run commands, export PDFs, record video, write PMO final acceptance, or run live/visible-thread tools
```

Current static final-submission manual-review shortest-path note:

```text
Results/static_audits/final_submission_manual_review_shortest_path_20260610/final_submission_manual_review_shortest_path_note.json
Results/static_audits/final_submission_manual_review_shortest_path_20260610/final_submission_manual_review_shortest_path_note.md
```

Run:

```bash
python Scripts/quality/build_final_submission_manual_review_shortest_path_note.py
```

Current boundary:

```text
final_submission_manual_review_shortest_path_note.json status is manual_review_shortest_path_note_not_execution
path_step_count=6
human_review_action_count=3
no_packet_action_count=3
independent_start_action_count=3
blocked_execution_target_count=4
target_action_reference_count=16
dashboard_blocker_count=16
reviewer_open_file_count=21
reviewer_open_file_drift_count=0
runs_commands_now=false
authorizes_execution_now=false
generates_final_outputs=false
final_acceptance=false
the manual-review shortest-path note orders A1-A6 only; it does not answer questions, fill or copy answer-sheet values, edit decision artifacts, approve decisions, install PDF tooling, create final artifacts, rerun readiness gates, run commands, export PDFs, record video, write PMO final acceptance, or run live/visible-thread tools
```

Current static final-submission open-file shortest-path bundle:

```text
Results/static_audits/final_submission_open_file_shortest_path_bundle_20260610/final_submission_open_file_shortest_path_bundle.json
Results/static_audits/final_submission_open_file_shortest_path_bundle_20260610/final_submission_open_file_shortest_path_bundle.md
```

Run:

```bash
python Scripts/quality/build_final_submission_open_file_shortest_path_bundle.py
```

Current boundary:

```text
final_submission_open_file_shortest_path_bundle.json status is open_file_shortest_path_bundle_not_execution
path_step_count=6
unique_open_file_count=21
total_open_file_reference_count=33
new_open_file_count=21
reused_open_file_reference_count=12
checksum_file_count=21
missing_open_file_count=0
unreadable_open_file_count=0
drift_from_previous_output_count=0
opens_files_now=false
runs_commands_now=false
authorizes_execution_now=false
generates_final_outputs=false
final_acceptance=false
the open-file shortest-path bundle groups existing review files by A1-A6 step only; it does not open files in a UI, answer questions, fill or copy answer-sheet values, edit decision artifacts, approve decisions, install PDF tooling, create final artifacts, rerun gates, run commands, export PDFs, record video, write PMO final acceptance, or run live/visible-thread tools
```

Current static final-submission human-review status packet skeleton:

```text
Results/static_audits/final_submission_human_review_status_packet_skeleton_20260610/final_submission_human_review_status_packet_skeleton.json
Results/static_audits/final_submission_human_review_status_packet_skeleton_20260610/final_submission_human_review_status_packet_skeleton.md
```

Run:

```bash
python Scripts/quality/build_final_submission_human_review_status_packet_skeleton.py
```

Current boundary:

```text
final_submission_human_review_status_packet_skeleton.json status is human_review_status_packet_skeleton_not_execution
review_action_count=3
reviewer_packet_action_count=3
no_packet_action_count=3
pending_field_count=38
required_pending_field_count=29
blocked_execution_target_count=4
dashboard_blocking_gate_count=7
dashboard_blocker_count=16
fills_answers_now=false
edits_decision_artifacts_now=false
runs_commands_now=false
authorizes_execution_now=false
generates_final_outputs=false
final_acceptance=false
the human-review status packet skeleton leaves A1/A3/A6 fields intentionally blank and records upstream A2/A4/A5/dashboard prerequisites only; it does not answer questions, copy answer-sheet values, edit decision templates, create reviewer packets for no-packet actions, run commands, export PDFs, record video, write PMO final acceptance, or run live/visible-thread tools
```

Current static final-submission status-packet dependency summary:

```text
Results/static_audits/final_submission_status_packet_dependency_summary_20260610/final_submission_status_packet_dependency_summary.json
Results/static_audits/final_submission_status_packet_dependency_summary_20260610/final_submission_status_packet_dependency_summary.md
```

Run:

```bash
python Scripts/quality/build_final_submission_status_packet_dependency_summary.py
```

Current boundary:

```text
final_submission_status_packet_dependency_summary.json status is status_packet_dependency_summary_not_execution
dashboard_blocker_count=16
prerequisite_class_count=5
mapped_action_count=6
execution_target_count=4
blocked_execution_target_count=4
issue_count=0
satisfies_dependencies_now=false
runs_commands_now=false
authorizes_execution_now=false
generates_final_outputs=false
final_acceptance=false
the status-packet dependency summary groups dashboard blockers into prerequisite classes and maps them to A1-A6 only; it does not satisfy prerequisites, answer questions, fill answer-sheet values, edit decision templates, create final artifacts, run commands, export PDFs, record video, write PMO final acceptance, or run live/visible-thread tools
```

Current static report source edit decision template:

```text
Results/static_audits/report_source_edit_decision_template_20260610/report_source_edit_decision_template.json
Results/static_audits/report_source_edit_decision_template_20260610/report_source_edit_decision_template.md
Results/static_audits/report_source_edit_decision_template_20260610/report_source_edit_decision.template.json
Results/static_audits/report_source_edit_decision_template_20260610/report_source_edit_decision_check.json
```

Run:

```bash
python Scripts/quality/build_report_source_edit_decision_template.py
python Scripts/quality/check_report_source_edit_decision.py
```

Current boundary:

```text
report_source_edit_decision_template.json status is decision_template_pending_review_not_approval
report_source_edit_decision.template.json decision is pending_review
report_source_edit_decision_check.json ok=true and authorizes_application=false while decision=pending_review
safe_to_apply_report_source_edits=false
the template does not approve edits, edit Docs/simulation_report.md, export PDFs/video, or write PMO final acceptance
the checker validates structure only and does not apply report-source edits
```
