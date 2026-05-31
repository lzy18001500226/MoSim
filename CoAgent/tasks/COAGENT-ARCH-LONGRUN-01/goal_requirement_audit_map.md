# COAGENT-ARCH-LONGRUN-01 Goal Requirement Audit Map

Date: 2026-05-30
Status: active audit map, not final completion proof

## Purpose

Map the active long-running goal to concrete evidence and remaining gaps. This
prevents the 10-hour architecture task from being judged by intent, chat
memory, or the existence of a task shell.

The goal remains active. This document is an interim audit aid.

## Active Goal Requirements

The current goal requires sustained architecture design progress around:

1. task-first CoAgent architecture;
2. goal authority and decomposition;
3. multi-conversation and multi-agent collaboration;
4. dynamic task teams;
5. context and memory indexing;
6. cross-conversation communication;
7. tool/MCP capability and fallback;
8. worktree and Git merge strategy;
9. review and testing gates;
10. safety boundaries;
11. human intervention;
12. external intelligence learning;
13. self-evolution mechanism;
14. retrospective and improvement closure;
15. reviewable architecture documents;
16. problem matrix and decision tradeoffs;
17. minimal closed-loop design;
18. department dispatch results;
19. next-stage implementation breakdown;
20. 10-hour user audit package.

## Evidence Map

| Requirement | Current Evidence | Current State | Remaining Gap |
|---|---|---|---|
| Task-first architecture | `task_charter.md`, `task_flow_design.md`, `enterprise_to_coagent_execution_mapping.md`, `task_intake_to_proof_ladder_decision_table.md`, `end_to_end_task_operating_runbook.md`, `real_task_execution_walkthroughs.md`, `task_health_monitoring_and_intervention_design.md` | design baseline plus end-to-end operating sequence, concrete PX4/UE task walkthroughs, and active-task intervention rules exist | needs live proof through Candidate A and later product-adjacent proofs |
| Goal authority/decomposition | `goal_authority_and_decomposition_protocol.md`, `goal_creation_and_recovery_protocol.md`, `goal_alignment_checker_design.md`, `architecture_decision_record_summary.md`, `final_goal_completion_audit.md` | design baseline exists, including L0 checker contract | future goal alignment checker implementation pending |
| Multi-conversation collaboration | visible department registry, department result packets, `minimal_multiconversation_proof_requirements.md`, `codex_visibility_recovery_experiment_design.md` | partially proved by Dispatch/Context/Verify packets and recovery design | full Candidate A packet chain and visible-state recovery fixtures not yet run |
| Dynamic task teams | `dynamic_team_decision_rules.md`, `department_dispatch_plan.md`, `handoff_mode_and_workflow_graph_design.md`, `handoff_workflow_validator_design.md`, `end_to_end_task_operating_runbook.md`, `real_task_execution_walkthroughs.md`, `task_health_monitoring_and_intervention_design.md` | design baseline plus composition runbook, concrete PX4/UE task-team examples, topology shrink rules, and health-state interventions exist | runtime validator and live task-team proof pending |
| Context/memory indexing | `context_pack.md`, `communication_context_protocol.md`, `context_lifecycle_schema.md`, `context_delta_checker_design.md`, `context_index_and_assembly_design.md` | context fields plus index/assembly design baseline exists | retrieval manifest checker and context delta/ack checker pending |
| Cross-conversation communication | result packets, `result_packet_contract_hardening.md`, `result_packet_validator_design.md`, `blocker_packet_templates.md`, `mailbox_ledger_and_replay_design.md`, `transport_timeout_hardening_design.md` | useful but fragile | flat packet validator, mailbox checker, and timeout blocker implementation pending |
| Tool/MCP capability and fallback | `tool_capability_health_and_fallback_protocol.md`, `tool_capability_health_gate_checker_design.md`, `candidate_b_px4_parameter_proof_package.md`, `candidate_c_ue_scene_truth_proof_package.md`, `blocker_packet_validator_design.md`, `evidence_label_doctor_design.md` | design baseline exists for route families, health levels, capability cards, fallback/stop rules, evidence-label interaction, and a concrete read-only checker contract | implementation and proof-package integration pending |
| Worktree/Git merge | `worktree_git_integration_protocol.md`, `candidate_d_git_heavy_change_proof_package.md`, `worktree_merge_recovery_experiment_design.md`, `worktree_git_recovery_validator_design.md` | design baseline plus recovery experiment and validator contract exist | read-only Git-heavy/worktree validator implementation and fixture package pending |
| Review/testing gates | `verification_evaluation_protocol.md`, `verification_gate_hardening.md`, `common_proof_package_validator_design.md`, `candidate_a_validator_execution_design.md`, `candidate_a_fixture_spec.md`, `candidate_a_fixture_generation_plan.md`, `operating_metrics_snapshot_design.md`, `early_drift_detection_experiment_design.md`, `task_health_monitoring_and_intervention_design.md`, `stress_test_artifact_validator_design.md`, `evidence_label_doctor_design.md`, `validator_dependency_and_rollout_plan.md`, `validator_shared_envelope_design.md` | design baseline exists, including shared validator envelope and intervention decisions for drift, fake progress, stale context, blockers, and completion overclaim | executable validators, shared envelope implementation, dependency-aware reports, metrics snapshot, early-drift fixtures, evidence-label doctor, fixture generator, and fixture files pending |
| Safety boundaries | `safety_human_intervention_protocol.md`, `blocker_packet_templates.md`, `blocker_packet_validator_design.md`, `human_review_intervention_ux_design.md`, `human_review_package_checker_design.md` | design baseline exists, including PMO-facing intervention UX and checker contract | blocker validator, human-review package checker implementation, and simulated interruption proof pending |
| Human intervention | `candidate_e_auth_license_interruption_proof_package.md`, `human_review_intervention_ux_design.md`, `human_review_package_checker_design.md` | proof package, review UX, and checker contract designed | no live or fixture proof yet; notification transport remains gated |
| External intelligence learning | `self_evolution_protocol.md`, `problem_driven_external_adoption_queue.md`, `external_adoption_proposal_contract.md`, `external_adoption_store_checker_design.md` | problem-driven intake, proposal contract, and checker design exist | proposal store/checker pending |
| Self-evolution | `knowledge_promotion_protocol.md`, `problem_driven_external_adoption_queue.md`, `external_adoption_proposal_contract.md`, `external_adoption_store_checker_design.md` | design baseline plus proposal accept/reject/promote and evidence-level guard contract exists | proof of promotion/rejection loop pending |
| Retrospective/improvement closure | `retrospective_and_improvement_closure_protocol.md`, `operating_metrics_and_anti_drift_cadence.md`, `knowledge_promotion_protocol.md`, `retrospective_closure_checker_design.md` | design baseline exists for triggers, action schema, owners, promotion/rejection, stale-action policy, checker contract, and future `RETRO_*` fixtures | retrospective record store/checker and closeout proof pending |
| Reviewable docs | task directory, `review_brief.md`, `shared_task_board.md`, `ten_hour_audit_package.md`, `end_to_end_task_operating_runbook.md` | active review surface exists | final audit still needs latest checks near review time |
| Problem matrix | `architecture_problem_matrix.md` with P01-P68 | active matrix exists, including recurring visibility drift P47, mailbox replay P48, goal-substitution control P58, retrospective closure P59, early drift fixtures P60, Codex visibility recovery P61, Git/worktree recovery P62, end-to-end runbook composition P63, human-review intervention UX P64, shared validator envelope P65, goal alignment checker P66, runbook readiness checker P67, and implementation approval gate P68 | statuses need continued maintenance |
| Decision tradeoffs | proof ladder, backlog, known findings, `architecture_decision_record_summary.md` | major tradeoffs recorded and summarized | final user decision points still pending |
| Minimal closed-loop design | `minimal_multiconversation_proof_requirements.md`, Candidate A docs including minimal package contract, fixture generation plan, manual rehearsal plan, validator execution design, `real_task_execution_walkthroughs.md`, and `task_health_monitoring_and_intervention_design.md` | design complete enough to propose proof, show how product tasks later traverse the loop, and decide continue/shrink/pause/block/review/close during execution | Candidate A fixtures/validator and live proof not yet executed; manual rehearsal remains user-approved fallback only |
| Department dispatch results | Dispatch/Context/Verify packets, Runtime timeout, and transport timeout hardening design | real packet evidence exists | broader clean packet chain and timeout closeout proof not yet complete |
| Next implementation breakdown | `post_design_implementation_backlog.md`, `implementation_sequence_and_release_plan.md` | backlog slices through NEXT-27 plus R0-R8 phase ladder exist | needs user approval before implementation |
| 10-hour audit package | `review_brief.md`, this audit map, `ten_hour_audit_package.md`, `goal_completion_gate_protocol.md`, `final_goal_completion_audit.md` | audit package and completion gate structure exist with working final audit draft | final audit refresh, final summary, and latest checks required near review time |

## Current Strong Evidence

Strong evidence means it is backed by current files, runtime events, or command
checks.

- Runtime task `COAGENT-ARCH-LONGRUN-01` exists and is active.
- The shared board lists 11 active visible permanent conversations.
- `check_department_visibility.py` passes with no pending confirmations.
- Department review packets exist for Dispatch, Context, and Verification.
- Runtime timeout is recorded as a finding, not hidden.
- The problem matrix tracks P01-P68 with owners and required outputs.
- Candidate A-E proof packages cover communication, PX4, UE, Git-heavy work,
  and auth/license/manual interruption.
- The proof ladder defines order and deviation rules.
- The common proof-package validator design defines shared preflight and
  post-dispatch checks.
- The shared validator envelope design defines one report format for validator
  schema version, decisions, dependencies, findings, evidence paths, side
  effects, claim boundaries, storage, fixtures, and integration rules.
- Tool capability health protocol defines how MWORKS, UE, Fab/manual import,
  Codex transport, Git, and external-reference routes must use capability
  cards, health levels, evidence labels, blocker policies, and fallback
  claim downgrades before product-adjacent tasks rely on them.
- Tool capability health gate checker design defines how future checks will
  reject missing/stale cards, unsupported route vocabularies, weak evidence,
  unsafe write probes, Fab visibility overclaims, screenshot-as-truth, offline
  MWORKS overclaims, Codex UI overclaims, and undeclared fallbacks.
- Real task walkthroughs define concrete PX4/Sunray150 and UE/Fab/local scene
  execution traces from intake through conversations, context, workflow graph,
  mailbox packets, blockers, Git disposition, review, and closeout.
- Task health monitoring and intervention design defines the runtime
  health-state model, trigger-to-action table, critical-path owner rule,
  topology shrink rules, PMO blocker ask shape, PX4/UE health applications,
  close-ready criteria, and future read-only task-health checker boundary.
- Candidate A fixture specification defines the valid minimal package,
  negative fixture matrix, expected error codes, and validator order.
- Candidate A fixture generation plan defines how to create the valid fixture
  and derive negative fixtures by controlled mutation before live dispatch.
- Candidate A manual rehearsal plan defines the supervised fallback before
  validators exist, including approval record, stop rules, evidence labels, and
  forbidden claims.
- Human review intervention UX design defines PMO-facing one-action asks,
  allowed decision vocabulary, severity, dedupe/rate-limit, redaction,
  blocker-specific resume mapping, required MWORKS/UE/Fab/visual/Git/transport
  cases, audit log, and notification boundary.
- Task intake decision table maps real user tasks to proof paths, first gates,
  minimum teams, secondary risks, and anti-drift questions.
- Ten-hour audit package defines verdict format, required commands, primary
  evidence set, forbidden claims, decision points, and closeout checklist.
- Goal completion gate protocol defines allowed verdicts, evidence hierarchy,
  accepted gated follow-up fields, final audit artifact, and forbidden
  completion shortcuts.
- Architecture decision record summary consolidates accepted, gated, deferred,
  and rejected design decisions for audit.
- Goal authority protocol records how user objective, canonical task goal,
  task-team goal, department goal, scoped conversation objective, subagent
  prompt objective, and implementation step goal must stay aligned.
- Goal creation and recovery protocol records how `create_goal` and wrong-goal
  deletion/recreation must preserve the real user outcome instead of creating a
  task-shell placeholder.
- Goal alignment checker design records the future L0 validation contract for
  user objective, canonical goal, scoped objective alignment, result goal
  mutation, checkpoint evidence delta, completion overclaim, recreated-goal
  scope loss, recovery records, and `GOAL_*` fixtures.
- Runbook readiness checker design records the future validation contract for
  serious task packages before multi-conversation dispatch, manual rehearsal,
  integration, or closeout, including charter, proof path, context, workflow,
  mailbox, packets, evidence labels, Git disposition, knowledge decision,
  dependency reports, and `RUNBOOK_*` fixtures.
- Implementation approval gate design records the future validation contract
  for explicit implementation-slice approval, phase entry evidence, scope,
  forbidden actions, dependency reports, exit evidence, claim boundaries, and
  `APPROVAL_*` fixtures before runtime, transport, schema, tool, MCP, Git,
  scheduler, notification, automation, or permanent conversation changes.
- Early drift detection experiment design records the negative and positive
  scenarios needed to prove future metrics/checkers catch wrong goals, fake
  progress, fake parallelism, stale context, missing blockers, unsupported
  tool claims, and completion overclaims before hours are wasted.
- Codex visibility recovery experiment design records how clean registry,
  registered drift, multi-department drift, unknown threads, missing rollouts,
  Windows sync failures, repeated drift, provider-config requests, and
  credential/cache risks should be checked, repaired, or blocked before
  bounded visible dispatch.
- Worktree merge recovery experiment design records how future Git/worktree
  checks should handle workspace mode choice, same-file conflicts, broad
  staging rejection, large binaries, external paths, destructive actions,
  Git locks/timeouts, role collapse, rollback, cleanup, and main-thread Git
  blockage without executing real Git.
- End-to-end task operating runbook records the ordered path from intake and
  canonical charter through proof-path selection, context, workflow graph,
  topology, execution, mailbox replay, review, integration/hold, knowledge
  promotion, retrospective, and closeout.
- Implementation sequence plan records R0-R8 phases, entry/exit evidence, skip
  rules, approval-packet fields, release milestones, and forbidden claims so
  the backlog cannot be treated as unordered approval to start product
  automation.
- Final goal completion audit exists as a working draft and currently records
  `needs_final_refresh_before_completion_claim`.

## Current Weak Or Incomplete Evidence

These areas cannot be claimed complete yet:

- Candidate A live multi-conversation proof has not been executed.
- Result packet validation is designed, not implemented.
- Shared validator envelope is designed, not implemented.
- Blocker packet validation is designed, not implemented.
- Human-review package checker contract is designed, not implemented.
- Candidate A fixture files and validator are specified, not implemented.
- Candidate A fixture generation is planned, not implemented.
- Candidate A manual rehearsal is planned, not approved or executed.
- Context delta acknowledgement is designed, not implemented as a gate.
- Context index/assembly is designed, not implemented as a retrieval manifest
  checker.
- Operating metrics cadence and snapshot checker are designed, not implemented
  as a read-only report.
- Task health intervention is designed, not implemented as an automatic board
  updater, dashboard, scheduler, or dispatch gate.
- Early drift negative/positive scenarios are designed, but the fixture
  package and executable checker are not implemented.
- Transport timeout hardening is designed, not implemented as closeout/blocker
  logic.
- Codex visibility drift gate is designed, not implemented.
- Codex visibility recovery experiment is designed, but synthetic fixtures and
  before/after evidence records are not implemented.
- Worktree/Git recovery experiment and validator contract are designed, but
  `GIT_*` fixtures and worktree/Git validators are not implemented.
- End-to-end runbook is designed, but no read-only runbook readiness checker
  or live Candidate A proof has validated the full sequence.
- Mailbox ledger and replay are designed, not implemented as a checker or
  replay generator.
- PX4/UE/Git/Auth proof packages are design blueprints, not executed proofs.
- Email/desktop notification is only a gated future transport; no sender,
  opt-in, redaction test, or rate-limit implementation exists.
- PX4/UE stress-test artifact validation and evidence-label checking are
  designed, not implemented.
- Tool capability health gate checker is designed, not implemented; no current
  claim should treat Fab/UE/MWORKS/Codex/Git routes as reliable through
  CoAgent without a fresh capability card and future checker/proof.
- External adoption proposal contract and store checker are designed, but the
  proposal store/checker and promotion/rejection proof are not implemented.
- Retrospective closure protocol and checker contract are designed, but the
  retrospective record store/checker and closeout proof are not implemented.
- The 10-hour audit package is structured but has not been closed with final
  latest checks and user decisions.
- Final `final_goal_completion_audit.md` has been drafted but not refreshed for
  final completion.
- Goal alignment checker is designed as a future item, not implemented.
- Runbook readiness checker is designed as a future item, not implemented.
- Implementation approval gate is designed as a future item, not implemented.
- Retrospective closure checker is designed as a future item, not implemented.
- Implementation sequence is designed, but no implementation slice is approved
  by this design document alone.

## Verification Commands To Run At Audit Time

Minimum:

```bash
python3 CoAgent/doctor/check_design_gate.py
python3 CoAgent/tests/test_design_surface_docs.py
python3 CoAgent/doctor/check_department_visibility.py
python3 CoAgent/runtime/mosim_agent_runtime.py show --task-id COAGENT-ARCH-LONGRUN-01
git diff --check -- CoAgent/tasks/COAGENT-ARCH-LONGRUN-01 CoAgent/STATUS.md PROGRESS.md
```

Optional, depending on what was implemented later:

```bash
python3 CoAgent/doctor/coagent_doctor.py
python3 CoAgent/tests/test_protocol_compliance_smoke.py
python3 CoAgent/tests/test_result_router.py
```

Do not use these commands as proof of implemented validators unless the command
actually covers the relevant validator.

## Next Work Priority

1. Keep `review_brief.md`, `shared_task_board.md`, and this audit map current.
2. If staying in design mode, refine Candidate A fixture details and final
   audit questions.
3. If moving toward implementation, start with the approved small slices:
   result packet hardening, Candidate A proof-package validator, handoff/
   workflow validators, context delta checker, metrics snapshot, transport
   timeout hardening, or tool capability health gate checker.
4. Do not execute product proofs B/C or operational proofs D/E until Candidate
   A mechanics are stable or the user explicitly accepts the transport/packet
   risk.

## Interim Audit Conclusion

The goal is not complete. It has substantial design evidence and an auditable
structure, but the requested end state still requires continued design work,
final audit packaging, and later approved proofs or validators.
