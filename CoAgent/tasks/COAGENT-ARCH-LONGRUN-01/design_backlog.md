# COAGENT-ARCH-LONGRUN-01 Design Backlog

Date: 2026-05-30
Status: active

## Purpose

This backlog keeps the 10-hour architecture task moving beyond Phase 1 setup.

## Phase 1: Control Plane And Problem Matrix

Status: in_progress

Tasks:

- activate confirmed visible departments;
- create task charter, board, context pack, issue matrix, dispatch plan;
- register runtime task and conversation edges;
- write first task-flow design.

Acceptance:

- user can audit the task from `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/`;
- runtime state shows the task is active;
- issue matrix identifies owners and required outputs.

## Phase 2: Dynamic Task-Team Architecture Refinement

Status: active

Tasks:

- refine topology selector thresholds;
- define task team creation and decommission criteria;
- define scoped conversation lifecycle;
- define subagent use boundaries;
- define peer communication and contradiction resolution.
- map enterprise-management concepts to concrete CoAgent execution objects.
- define handoff mode and workflow graph as first-class design objects.
- define the intake classifier that maps user tasks to proof path A-E, first
  gate, team shape, and secondary-risk ordering.
- define mailbox ledger, message state machine, acknowledgements, replay,
  timeout/retry, contradiction handling, and closeout recovery.

Target docs:

- `CoAgent/docs/architecture/coagent_dynamic_task_team_v2_design.md`
- `CoAgent/docs/architecture/coagent_agent_design_protocol.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/architecture_problem_matrix.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/enterprise_to_coagent_execution_mapping.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/handoff_mode_and_workflow_graph_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/task_intake_to_proof_ladder_decision_table.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/mailbox_ledger_and_replay_design.md`

## Phase 3: Context, Memory, And Knowledge Architecture

Status: active

Tasks:

- design context-pack quality metrics;
- define shared context versus slice context;
- define context delta and refresh protocol;
- define stale-context detection;
- define accepted-decision and rejected-idea indexes;
- define how skills/hooks/docs receive promoted knowledge.
- define machine-checkable context lifecycle fields discovered by
  `COAGENT-ARCH-LONGRUN-01-CONTEXT-01`;
- define acknowledgement and pause/resume rules for stale context.
- define context index families, slice types, retrieval manifest, context
  budget classes, stale/rejected material filters, and assembly fit checks.

Target docs:

- `CoAgent/context/context_pack_contract.md`
- `CoAgent/docs/architecture/coagent_solution_synthesis.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/context_pack.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/context_index_and_assembly_design.md`

## Phase 4: Runtime, Conversation, Worktree, And Git Design

Status: active

Tasks:

- map Codex App/VSCode/CLI features to CoAgent objects;
- define visibility and recovery invariants;
- define worktree binding policy;
- define integration owner and merge gates;
- define large-change, rename, asset, and generated-output policies.
- record the 60s `codex exec resume` timeout failure mode from
  `COAGENT-ARCH-LONGRUN-01-RUNTIME-01`;
- design transport cleanup, timeout blocker, and packet-format feedback loops.

Target docs:

- `CoAgent/docs/status/codex_visible_thread_sop.md`
- `CoAgent/docs/architecture/coagent_dynamic_agent_codex_feature_gap_2026_05_29.md`
- `CoAgent/docs/architecture/coagent_review_merge_protocol.md`

## Phase 5: Safety, Human Intervention, And Incident Design

Status: planned

Tasks:

- define blocker classes and stop/resume rules;
- define future notification template and dedupe policy;
- define login/license/GUI/manual-review handling;
- define incident command for repeated tool/runtime failures;
- define approval boundaries for gated runtime features.
- define `transport_timeout` and `invalid_result_packet` blocker templates
  from real department dispatch failures.

Target docs:

- `CoAgent/docs/architecture/coagent_user_intervention_ux.md`
- `CoAgent/docs/architecture/coagent_solution_synthesis.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/architecture_problem_matrix.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/blocker_packet_templates.md`

## Phase 6: Verification, Evidence, And Operating Metrics

Status: active

Tasks:

- separate product correctness evidence from process evidence;
- define trace/eval rubric;
- define drift and handoff failure metrics;
- define minimal closed-loop proof criteria;
- define review gates for architecture decisions and implementation slices.
- define thresholds and required packet fields for process metrics;
- define negative drift-packet tests and stress-test evidence templates.
- define checkpoint cadence, anti-drift states, board review questions, and
  retrospective triggers.
- define the smallest visible multi-conversation proof with pass/fail rules.
- define Candidate A as a concrete packet-chain blueprint before any live
  proof execution.
- define Candidate A proof-package inputs, outputs, validation checks, and
  negative fixtures before any live dispatch.
- define concrete Candidate A positive/negative fixture specifications with
  stable expected error codes and validator order.

Target docs:

- `CoAgent/docs/architecture/coagent_minimal_closed_loop_protocol.md`
- `CoAgent/docs/architecture/coagent_solution_synthesis.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/review_brief.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/operating_metrics_and_anti_drift_cadence.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/minimal_multiconversation_proof_requirements.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_packet_chain_blueprint.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_proof_package_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_fixture_spec.md`

## Phase 7: External Intelligence And Self-Evolution

Status: active

Tasks:

- convert vendor/open-source learning into problem-led intake;
- define credibility/relevance scoring;
- define adoption proposal template;
- define rejected-idea archive;
- define scheduled learning and update cadence as design only.
- define problem-driven adoption queue and evidence levels.
- define structured adoption proposal lifecycle, required fields,
  accept/reject rules, examples, and future checker boundary.

Target docs:

- `CoAgent/docs/research/LEARNING_STRATEGY.md`
- `CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md`
- `CoAgent/docs/research/multi_agent_learning_urls.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/problem_driven_external_adoption_queue.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/external_adoption_proposal_contract.md`

## Phase 8: Stress-Test Architecture Walkthroughs

Status: completed_draft

Tasks:

- run paper walkthrough for PX4 log parameter identification;
- run paper walkthrough for UE scene truth / RflySim-like simulation;
- define PX4 parameter-identification proof-package shape.
- define UE scene-truth proof-package shape.
- run paper walkthrough for Git-heavy rename/import incident;
- run paper walkthrough for activation/license interruption;
- define Git-heavy change proof-package shape.
- define auth/license interruption proof-package shape.
- consolidate A-E proof packages into a default proof ladder and validator
  order.
- define common proof-package validator fields, error codes, fixtures, and
  read-only boundary.
- record gaps and next experiments.

Target docs:

- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/task_flow_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/stress_test_px4_parameter_identification.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/stress_test_ue_scene_truth_product.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_b_px4_parameter_proof_package.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_c_ue_scene_truth_proof_package.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_d_git_heavy_change_proof_package.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_e_auth_license_interruption_proof_package.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/proof_ladder_and_validator_order.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/common_proof_package_validator_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/architecture_problem_matrix.md`
- new stress-test review notes if needed.

## Phase 9: Implementation Backlog Draft

Status: completed_draft

Tasks:

- split approved architecture into small implementation tasks;
- mark gated versus approved tasks;
- define acceptance and checks for each;
- identify first minimal safe implementation slice after user review.

Target docs:

- `CoAgent/docs/decisions/coagent_post_approval_backlog.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/post_design_implementation_backlog.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/review_brief.md`

## Phase 10: 10-Hour Audit Package

Status: active

Tasks:

- summarize changed files;
- list decisions and unresolved questions;
- list proposed next implementation tasks;
- run design/static checks;
- prepare final user audit note.
- map active goal requirements to evidence, weak/incomplete evidence, and
  audit-time checks.
- provide one concentrated audit package with verdict format, required
  commands, requirement mapping, forbidden claims, user decision points, next
  approval queue, and final closeout checklist.

Target docs:

- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/review_brief.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/goal_requirement_audit_map.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/ten_hour_audit_package.md`
- `PROGRESS.md`
- `CoAgent/STATUS.md`
