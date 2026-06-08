# COAGENT-ARCH-LONGRUN-01 Architecture Problem Matrix

Date: 2026-05-30
Status: active working matrix

## Purpose

This matrix keeps the 10-hour architecture task problem-driven. The design work
must answer these problems with durable architecture decisions, experiments, or
explicit deferrals.

## Status Vocabulary

| Status | Meaning |
|---|---|
| `working` | actively being designed in this long task |
| `needs_experiment` | requires a proof before the design can be accepted |
| `needs_user_decision` | needs user choice because it changes direction or risk |
| `decided_baseline` | existing design is acceptable but may need refinement |
| `deferred_gated` | valid need, but implementation is gated |

## Core Problems

| ID | Problem | Owner | Current Status | Required Output |
|---|---|---|---|---|
| P01 | How does one user task become a canonical durable task instead of fragmented chat instructions? | DispatchAgent | decided_baseline | task charter rule and runtime task record |
| P02 | How does Dispatch decide whether to use main thread, one scoped conversation, many scoped conversations, or subagents? | DispatchAgent | decided_baseline | `dynamic_team_decision_rules.md` |
| P03 | How many permanent departments are required, and which capabilities stay hosted or conditional? | ProductStrategyAgent + DispatchAgent | decided_baseline | `product_appetite_and_non_goals.md`, conversation mapping update and promotion/demotion criteria |
| P04 | How is context given to new conversations without full transcript bloat or semantic drift? | ContextMemoryAgent + DispatchAgent | decided_baseline_design_needs_validator | `context_pack.md`, `communication_context_protocol.md`, `context_lifecycle_schema.md`, `context_delta_checker_design.md`, `context_index_and_assembly_design.md` |
| P05 | How do conversations communicate without hidden, lossy, or conflicting chat? | DispatchAgent + KnowledgeSecretaryAgent + VerificationAgent | decided_baseline_design_needs_validator | `communication_context_protocol.md`, `mailbox_ledger_and_replay_design.md` |
| P06 | How do task-scoped conversations close cleanly? | DispatchAgent + VerificationAgent | decided_baseline_design_needs_validator | `dynamic_team_decision_rules.md`, `communication_context_protocol.md`, `mailbox_ledger_and_replay_design.md`, result packet format hardening and closeout import test |
| P07 | How do we prevent a worker from silently changing the task goal? | DispatchAgent + SafetyComplianceAgent | decided_baseline | goal ownership and review-required transition |
| P08 | How do worktrees map to conversations and task teams? | DevOpsReleaseAgent + RuntimePlatformAgent | decided_baseline_design_needs_implementation | `worktree_git_integration_protocol.md`, `worktree_merge_recovery_experiment_design.md`, `worktree_git_recovery_validator_design.md`, future worktree-binding validator |
| P09 | How is Git handled for large imports, renames, or many-file changes? | DevOpsReleaseAgent | decided_baseline_design_needs_implementation | `worktree_git_integration_protocol.md`, `worktree_merge_recovery_experiment_design.md`, `worktree_git_recovery_validator_design.md`, future Git-heavy validator |
| P10 | How do we detect that an Agent has gone down the wrong path before 5 hours are wasted? | VerificationAgent + Flow Analytics hosted by Dispatch | decided_baseline_design_needs_fixture_implementation | `verification_evaluation_protocol.md`, `operating_metrics_and_anti_drift_cadence.md`, `operating_metrics_snapshot_design.md`, `early_drift_detection_experiment_design.md`, `task_health_monitoring_and_intervention_design.md`, future early-drift fixtures/checker |
| P11 | How are manual login/license/GUI/activation blockers handled without endless retry loops? | SafetyComplianceAgent + Operator Experience hosted by MainAgent | decided_baseline | `safety_human_intervention_protocol.md` |
| P12 | How does CoAgent use Codex App/VSCode/CLI features without treating UI state as source of truth? | RuntimePlatformAgent | decided_baseline_design_needs_fixture_implementation | Codex feature-use matrix, visibility/recovery tests, `transport_timeout_hardening_design.md`, `codex_visibility_recovery_experiment_design.md`, 60s resume transport reliability test |
| P13 | How are MCP/tool failures handled, especially UE/MWORKS/Fab workflows? | ToolchainMCPAgent + SafetyComplianceAgent + VerificationAgent | decided_baseline_design_needs_implementation | `tool_capability_health_and_fallback_protocol.md`, `tool_capability_health_gate_checker_design.md`, future `COAGENT-IMPL-NEXT-27` checker |
| P14 | How do we distinguish product correctness evidence from process evidence? | VerificationAgent | decided_baseline | `verification_evaluation_protocol.md` |
| P15 | How do external articles and open-source projects become useful architecture changes instead of generic summaries? | ExternalIntelligenceAgent + KnowledgeSecretaryAgent | decided_baseline | `self_evolution_protocol.md` |
| P16 | How do accepted lessons become skills, hooks, doctor checks, workflow docs, or runtime tasks? | KnowledgeSecretaryAgent + Architecture hosted by Dispatch | decided_baseline | `knowledge_promotion_protocol.md` |
| P17 | How do we handle peer-to-peer communication between task conversations? | DispatchAgent + VerificationAgent | decided_baseline_design_needs_validator | `communication_context_protocol.md`, `mailbox_ledger_and_replay_design.md` |
| P18 | How are contradictory results resolved? | VerificationAgent + DispatchAgent | decided_baseline_design_needs_validator | `communication_context_protocol.md`, `mailbox_ledger_and_replay_design.md`, `verification_evaluation_protocol.md` |
| P19 | How does a task team scale down after completion? | DispatchAgent + DevOpsReleaseAgent | decided_baseline | `dynamic_team_decision_rules.md`, `worktree_git_integration_protocol.md` |
| P20 | How do we preserve enough history for future conversations while releasing old context? | ContextMemoryAgent + KnowledgeSecretaryAgent + VerificationAgent | decided_baseline_design_needs_validator | `communication_context_protocol.md`, `knowledge_promotion_protocol.md`, `context_index_and_assembly_design.md` |
| P21 | How should the system handle PX4 log parameter identification end to end? | ProductStrategyAgent + VerificationAgent | decided_baseline_design_needs_proof | `stress_test_px4_parameter_identification.md`, `candidate_b_px4_parameter_proof_package.md`, `real_task_execution_walkthroughs.md` |
| P22 | How should the system handle UE scene truth and RflySim-like productization end to end? | ToolchainMCPAgent + ProductStrategyAgent | decided_baseline_design_needs_proof | `stress_test_ue_scene_truth_product.md`, `candidate_c_ue_scene_truth_proof_package.md`, `real_task_execution_walkthroughs.md` |
| P23 | What is the smallest safe implementation sequence after design is accepted? | DispatchAgent + RuntimePlatformAgent + VerificationAgent | decided_baseline | `implementation_sequence_and_release_plan.md`, post-design implementation backlog, phase ladder R0-R8 |
| P24 | Which features are useful but explicitly not approved yet? | SafetyComplianceAgent | decided_baseline | gated-feature list and approval criteria |
| P25 | How do we measure whether this CoAgent organization is actually improving productivity and quality? | VerificationAgent + DispatchAgent | decided_baseline_design_needs_validator | `operating_metrics_and_anti_drift_cadence.md`, `operating_metrics_snapshot_design.md`, `task_health_monitoring_and_intervention_design.md` |
| P26 | How do we make result packet contracts robust against worker YAML formatting drift? | RuntimePlatformAgent + VerificationAgent | decided_baseline_design_needs_validator | `result_packet_contract_hardening.md`, `result_packet_validator_design.md` |
| P27 | How are blocked transport, invalid packet, auth/license, manual review, and destructive actions represented as resumable durable state? | SafetyComplianceAgent + RuntimePlatformAgent + DispatchAgent | decided_baseline_design_needs_validator | `blocker_packet_templates.md`, `transport_timeout_hardening_design.md`, and future blocker validator |
| P28 | How do enterprise-management ideas become concrete CoAgent execution objects instead of another fixed bureaucracy? | DispatchAgent + KnowledgeSecretaryAgent | decided_baseline | `enterprise_to_coagent_execution_mapping.md` |
| P29 | How does a long-running task detect drift, fake parallelism, stale context, blocked work, and review escapes before hours are wasted? | VerificationAgent + Flow Analytics hosted by Dispatch | decided_baseline_design_needs_fixture_implementation | `operating_metrics_and_anti_drift_cadence.md`, `operating_metrics_snapshot_design.md`, `early_drift_detection_experiment_design.md`, `task_health_monitoring_and_intervention_design.md`, future metrics snapshot checker and early-drift fixtures |
| P30 | What is the smallest visible multi-conversation proof that proves CoAgent can coordinate real task work without hidden chat memory? | DispatchAgent + VerificationAgent | decided_baseline_design_needs_experiment | `minimal_multiconversation_proof_requirements.md` |
| P31 | How are handoff choices and task workflow dependencies represented so routing is not prose-only? | DispatchAgent + RuntimePlatformAgent | decided_baseline_design_needs_validator | `handoff_mode_and_workflow_graph_design.md`, `handoff_workflow_validator_design.md`, protocol templates `handoff_mode.yaml` and `workflow_graph.yaml` |
| P32 | How do vendor articles and local open-source projects become CoAgent improvements without broad summary drift? | ExternalIntelligenceAgent + KnowledgeSecretaryAgent | decided_baseline_design_needs_validator | `problem_driven_external_adoption_queue.md`, `external_adoption_proposal_contract.md`, `external_adoption_store_checker_design.md` |
| P33 | How is Candidate A specified tightly enough that a later multi-conversation proof cannot invent routing, packets, or pass criteria during execution? | DispatchAgent + VerificationAgent + ContextMemoryAgent | decided_baseline_design_needs_user_or_runtime_gate | `candidate_a_packet_chain_blueprint.md` |
| P34 | How do we prove a live multi-conversation proof package is structurally valid before spending transport/runtime budget on dispatch? | DispatchAgent + RuntimePlatformAgent + VerificationAgent | decided_baseline_design_needs_validator | `candidate_a_proof_package_design.md`, `candidate_a_validator_execution_design.md` |
| P35 | How does the PX4 parameter-identification task become a proof package with honest identifiability, uncertainty, simulation-evidence labels, and blocker handling? | ProductStrategyAgent + VerificationAgent + ContextMemoryAgent | decided_baseline_design_needs_proof | `candidate_b_px4_parameter_proof_package.md` |
| P36 | How does the UE scene-truth task become a proof package that separates visual rendering from planning truth and stops safely on Fab/UE/MCP blockers? | ToolchainMCPAgent + ProductStrategyAgent + VerificationAgent | decided_baseline_design_needs_proof | `candidate_c_ue_scene_truth_proof_package.md` |
| P37 | How does CoAgent handle huge Git changes, renames, imports, generated outputs, and large assets without broad unsafe staging or blocking the main thread? | DevOpsReleaseAgent + SafetyComplianceAgent + VerificationAgent | decided_baseline_design_needs_implementation | `candidate_d_git_heavy_change_proof_package.md`, `worktree_merge_recovery_experiment_design.md`, `worktree_git_recovery_validator_design.md` |
| P38 | How does CoAgent turn auth/license/GUI/manual-review interruptions into durable blocker/resume state instead of retry loops or lost context? | SafetyComplianceAgent + DispatchAgent + VerificationAgent | decided_baseline_design_needs_proof | `candidate_e_auth_license_interruption_proof_package.md` |
| P39 | How do A-E proof packages become an ordered ladder so implementation does not jump into high-risk product automation before packet/context/review/blocker mechanics are proven? | DispatchAgent + VerificationAgent | decided_baseline | `proof_ladder_and_validator_order.md` |
| P40 | How do all proof packages share one validator contract instead of each candidate inventing separate preflight and closeout rules? | VerificationAgent + RuntimePlatformAgent | decided_baseline_design_needs_implementation | `common_proof_package_validator_design.md` |
| P41 | How will the 10-hour goal be audited requirement-by-requirement without mistaking partial design evidence for completion? | DispatchAgent + VerificationAgent | decided_baseline | `goal_requirement_audit_map.md` |
| P42 | How do we make Candidate A validator implementation deterministic instead of prose-driven, with fixture cases that fail for the right reasons before live dispatch? | VerificationAgent + DispatchAgent | decided_baseline_design_needs_implementation | `candidate_a_fixture_spec.md`, `candidate_a_validator_execution_design.md` |
| P43 | How does one incoming user task choose the right proof path, first gate, dynamic team, and secondary-risk order instead of defaulting to all departments or a static org chart? | DispatchAgent + ProductStrategyAgent + VerificationAgent | decided_baseline | `task_intake_to_proof_ladder_decision_table.md` |
| P44 | How does the user audit the 10-hour architecture push without reading every file linearly or mistaking design evidence for live proof? | DispatchAgent + VerificationAgent + MainAgent | decided_baseline | `ten_hour_audit_package.md` |
| P45 | How does an external idea move from source slice to accepted, rejected, deferred, validated, and promoted CoAgent knowledge without polluting context or bypassing safety? | ExternalIntelligenceAgent + KnowledgeSecretaryAgent + VerificationAgent | decided_baseline_design_needs_validator | `external_adoption_proposal_contract.md`, `external_adoption_store_checker_design.md`, future `COAGENT-IMPL-NEXT-10` checker |
| P46 | How does CoAgent assemble a minimal sufficient context pack for a new scoped conversation from indexes, while excluding stale/rejected assumptions and respecting model context budget? | ContextMemoryAgent + DispatchAgent + VerificationAgent | decided_baseline_design_needs_validator | `context_index_and_assembly_design.md`, future `COAGENT-IMPL-NEXT-21` checker |
| P47 | How does CoAgent prevent recurring Codex visible-thread metadata drift from repeatedly breaking department dispatch readiness? | RuntimePlatformAgent + DispatchAgent + SafetyComplianceAgent | decided_baseline_design_needs_fixture_implementation | `codex_visibility_drift_reliability_design.md`, `codex_visibility_recovery_experiment_design.md`, future `COAGENT-IMPL-NEXT-22` gate |
| P48 | How does CoAgent replay cross-conversation mailbox state after session loss, timeout, contradiction, or context compaction without relying on hidden chat memory? | DispatchAgent + VerificationAgent + KnowledgeSecretaryAgent | decided_baseline_design_needs_validator | `mailbox_ledger_and_replay_design.md`, future `COAGENT-IMPL-NEXT-23` checker |
| P49 | How are blocker packets validated so blocked work is resumable without vague user asks, unsafe retries, duplicate prompts, or missing last-safe-state evidence? | SafetyComplianceAgent + RuntimePlatformAgent + VerificationAgent | decided_baseline_design_needs_validator | `blocker_packet_validator_design.md`, future `COAGENT-IMPL-NEXT-05` validator |
| P50 | How do PX4 and UE product-adjacent stress tests reject overclaims before simulator parameters or planning truth are accepted? | ProductStrategyAgent + ToolchainMCPAgent + VerificationAgent | decided_baseline_design_needs_validator | `stress_test_artifact_validator_design.md`, future `COAGENT-IMPL-NEXT-06` validators |
| P51 | How does CoAgent prevent design-only, offline, manual, Git/runtime, GUI, MCP, and external-reference evidence from being mislabeled or inflated? | VerificationAgent + SafetyComplianceAgent | decided_baseline_design_needs_validator | `evidence_label_doctor_design.md`, future `COAGENT-IMPL-NEXT-07` doctor |
| P52 | How does CoAgent sequence validators as a dependency graph so later gates cannot bypass missing evidence, packet, blocker, context, workflow, or proof-package checks? | VerificationAgent + DispatchAgent + RuntimePlatformAgent | decided_baseline_design_needs_implementation | `validator_dependency_and_rollout_plan.md`, future validator reports must use `needs_dependency` instead of silent pass |
| P53 | What exact files and fields must exist for the minimal Candidate A proof package so fixture generation and validation are deterministic instead of improvised? | DispatchAgent + VerificationAgent + ContextMemoryAgent | decided_baseline_design_needs_fixture_implementation | `candidate_a_minimal_package_contract.md`, future Candidate A fixture generator/validator |
| P54 | How are Candidate A fixtures generated repeatably from one valid package and controlled mutations instead of hand-written examples that drift from the validator contract? | DispatchAgent + VerificationAgent + RuntimePlatformAgent | decided_baseline_design_needs_fixture_implementation | `candidate_a_fixture_generation_plan.md`, future `COAGENT-IMPL-NEXT-24` fixture generator |
| P55 | If the user wants to inspect Candidate A before validators are implemented, how can a supervised manual rehearsal run without being mistaken for automated dispatch or validated proof? | DispatchAgent + MainAgent + VerificationAgent | decided_baseline_design_needs_user_approval_for_rehearsal | `candidate_a_manual_rehearsal_plan.md`, manual rehearsal requires explicit user approval and forbidden claims |
| P56 | How can the 10-hour design goal be closed without overclaiming runtime implementation or leaving design requirements only partially covered? | DispatchAgent + MainAgent + VerificationAgent | decided_baseline_design_needs_final_audit | `goal_completion_gate_protocol.md`, final `final_goal_completion_audit.md` before any complete claim |
| P57 | How can the user audit major architecture tradeoffs without reading every detailed protocol file linearly? | DispatchAgent + KnowledgeSecretaryAgent + VerificationAgent | decided_baseline | `architecture_decision_record_summary.md` |
| P58 | How does CoAgent prevent lower-level task, department, conversation, subagent, implementation, or recreated runtime goals from weakening the user's objective into setup work or activity metrics? | DispatchAgent + MainAgent + VerificationAgent | decided_baseline_design_needs_validator | `goal_authority_and_decomposition_protocol.md`, `goal_creation_and_recovery_protocol.md`, future `goal_alignment_checker` |
| P59 | How do repeated failures, user corrections, review escapes, and incidents become closed improvement actions instead of scattered notes that future agents forget? | KnowledgeSecretaryAgent + DispatchAgent + VerificationAgent | decided_baseline_design_needs_implementation | `retrospective_and_improvement_closure_protocol.md`, `retrospective_closure_checker_design.md`, future `COAGENT-IMPL-NEXT-26` checker |
| P60 | How can the operating metrics checker prove it catches wrong goals, fake progress, fake parallelism, stale context, missing blockers, and completion overclaims before live long-running work relies on it? | VerificationAgent + DispatchAgent + MainAgent | decided_baseline_design_needs_fixture_implementation | `early_drift_detection_experiment_design.md`, `task_health_monitoring_and_intervention_design.md`, future fixture package under `CoAgent/tests/fixtures/operating_metrics/early_drift/` |
| P61 | How can CoAgent prove visible Codex department state is recoverable enough for bounded dispatch without claiming root-cause reliability or touching unrelated Codex state? | RuntimePlatformAgent + SafetyComplianceAgent + VerificationAgent | decided_baseline_design_needs_fixture_implementation | `codex_visibility_recovery_experiment_design.md`, future synthetic Codex state fixtures and recovery evidence records |
| P62 | How does CoAgent recover from risky Git/worktree states such as same-file conflicts, broad staging plans, large binaries, external paths, Git locks, slow Git commands, missing rollback, or main-thread Git blockage? | DevOpsReleaseAgent + SafetyComplianceAgent + VerificationAgent | decided_baseline_design_needs_implementation | `worktree_merge_recovery_experiment_design.md`, `worktree_git_recovery_validator_design.md`, future `GIT_*` fixture package and validator |
| P63 | How does CoAgent compose all protocols into one end-to-end task operating sequence so serious user tasks are routed, reviewed, integrated, learned from, and closed without relying on chat memory or ad-hoc judgment? | DispatchAgent + MainAgent + VerificationAgent + KnowledgeSecretaryAgent | decided_baseline_design_needs_validator | `end_to_end_task_operating_runbook.md`, `real_task_execution_walkthroughs.md`, `task_health_monitoring_and_intervention_design.md`, future runbook readiness checker |
| P64 | How does CoAgent ask the user for manual review or external intervention without vague prompts, duplicate asks, unsafe retries, secret leakage, or lost resume state? | MainAgent + SafetyComplianceAgent + DispatchAgent + VerificationAgent | decided_baseline_design_needs_implementation | `human_review_intervention_ux_design.md`, `human_review_package_checker_design.md`, future `COAGENT-IMPL-NEXT-29` checker after blocker validator |
| P65 | How do all future validators report decisions, findings, dependencies, evidence paths, side effects, and claim boundaries in one consumable format instead of each checker inventing local semantics? | VerificationAgent + RuntimePlatformAgent + DispatchAgent | decided_baseline_design_needs_implementation | `validator_shared_envelope_design.md`, future `COAGENT-IMPL-NEXT-00` shared constants/schema/fixtures |
| P66 | How does CoAgent validate that task charters, scoped objectives, worker results, checkpoints, and completion audits still prove the original user objective instead of a weakened setup/activity goal? | DispatchAgent + MainAgent + VerificationAgent | decided_baseline_design_needs_implementation | `goal_alignment_checker_design.md`, future `COAGENT-IMPL-NEXT-25` checker |
| P67 | How does CoAgent know a serious task package is actually ready for multi-conversation execution, proof validation, manual rehearsal, integration, or closeout instead of relying on chat-only next actions? | DispatchAgent + VerificationAgent + KnowledgeSecretaryAgent | decided_baseline_design_needs_implementation | `runbook_readiness_checker_design.md`, `task_health_monitoring_and_intervention_design.md`, future `COAGENT-IMPL-NEXT-30` checker |
| P68 | How does CoAgent prevent backlog entries, phase order, broad design acceptance, or vague "continue" messages from becoming implicit approval for runtime, transport, schema, tool, MCP, Git, scheduler, notification, automation, or permanent conversation changes? | DispatchAgent + SafetyComplianceAgent + VerificationAgent | decided_baseline_design_needs_implementation | `implementation_approval_gate_design.md`, future `COAGENT-IMPL-NEXT-31` checker |

## Immediate Design Pressure Points

### User Task Flow

For a task like PX4 log parameter identification, CoAgent must answer:

1. what is the canonical task goal;
2. what can be decided from intake alone;
3. what data sufficiency gate runs first;
4. which conversations are created immediately;
5. which conversations wait for gate outputs;
6. how context is seeded into each conversation;
7. how results return and contradict each other;
8. how simulation/license/manual review blockers are escalated;
9. how code, evidence, docs, and Git are merged;
10. what makes the task complete rather than merely busy.

`real_task_execution_walkthroughs.md` now answers these at scenario level for
PX4/Sunray150 parameter identification, including initial team, scoped
conversations, context contents, workflow graph, contradiction handling, human
asks, Git disposition, and completion criteria.

### Product Mainline Flow

For UE scene truth and RflySim-like simulation, CoAgent must answer:

1. how map sources are classified and gated;
2. how UE/MCP capability is proved before long execution;
3. how scene truth is exported and validated;
4. how planning/navigation algorithms receive truth artifacts;
5. how wind and motor-degradation experiments are represented;
6. how user-facing UI/product scope is controlled;
7. how manual visual review is requested and resumed;
8. how large asset/Git/LFS decisions are handled;
9. how failed Fab/UE/MCP routes are stopped without wasting days;
10. how accepted lessons update tools, skills, workflows, and docs.

`real_task_execution_walkthroughs.md` now answers these at scenario level for
UE/Fab/local scene truth, including source intake, capability cards, truth
manifest gates, manual import handling, evidence boundaries, large-asset Git
policy, and completion criteria.

## Initial Open Decisions

| Decision | Default For This Task | Needs Later Approval? |
|---|---|---|
| Use active 11 permanent conversations | yes | no, user confirmed visibility |
| Add more permanent departments now | no | yes |
| Allow task-scoped conversation proposals | design only | yes for automatic creation |
| Use `codex exec resume` to dispatch packets | allowed for bounded tests | may need transport hardening |
| Treat App/VSCode sync as durable state | no | no |
| Implement email sender | no | yes |
| Implement automatic worktree creation | no | yes |
| Implement app-server transport | no | yes |

## Next Matrix Update

Each design cycle must update at least one of:

- status;
- owner;
- required output;
- decision baseline;
- experiment requirement;
- deferral reason.

## Design Gaps From Stress Tests

| Gap | Source | Proposed Next Artifact |
|---|---|---|
| reusable parameter-identifiability matrix | PX4 stress test | protocol template |
| log-analysis context-pack generator | PX4 stress test | implementation backlog item |
| MWORKS activation/license blocker packet | PX4 stress test | blocker template |
| evidence label checker for MWORKS versus offline demo | PX4 stress test | doctor/check item |
| scene-source capability card | UE stress test | protocol template |
| Fab/UE manual-import blocker/resume packet | UE stress test | blocker template |
| truth-artifact manifest schema | UE stress test | protocol template |
| large UE asset Git policy | UE stress test | DevOps workflow |
| visual review versus planning truth rubric | UE stress test | verification rubric |

Template status:

- `CoAgent/protocol/templates/px4_parameter_identifiability_matrix.yaml`
  drafted for PX4 log parameter identification;
- `CoAgent/protocol/templates/ue_scene_truth_capability_card.yaml`
  drafted for scene-source and UE/MCP capability review;
- `CoAgent/protocol/templates/scene_truth_artifact_manifest.yaml`
  drafted for planning-truth artifact review;
- validators and negative fixtures remain future implementation work;
- `blocker_packet_validator_design.md` drafted for validating resumable
  blockers before retry, user ask, or closeout;
- `stress_test_artifact_validator_design.md` drafted for validating PX4
  identifiability and UE scene-truth artifacts;
- `evidence_label_doctor_design.md` drafted for enforcing evidence provenance
  labels and rejecting label inflation;
- `validator_dependency_and_rollout_plan.md` drafted for sequencing validators
  as a dependency graph with shared output envelope and dependency-failure
  policy;
- `candidate_a_minimal_package_contract.md` drafted as the source of truth for
  exact Candidate A package and fixture file contents.
- `candidate_a_fixture_generation_plan.md` drafted as the generation plan for
  building one valid Candidate A fixture, deriving negative fixtures by
  controlled mutation, and recording expected decisions and finding codes.
- `candidate_a_manual_rehearsal_plan.md` drafted as the supervised path for a
  manual visible-conversation Candidate A rehearsal if the user approves
  running before validators and fixture generator exist.
- `goal_completion_gate_protocol.md` drafted as the final completion gate for
  closing the long-run design goal without confusing design readiness with
  runtime implementation or live proof.
- `architecture_decision_record_summary.md` drafted as the ADR-style summary
  of accepted, gated, deferred, and rejected architecture decisions for the
  10-hour user audit.
- `goal_creation_and_recovery_protocol.md` drafted as the operational preflight
  for creating or recreating Codex goals without turning user outcomes into
  setup actions, and as the recovery path when a wrong goal must be deleted and
  recreated.
- `tool_capability_health_and_fallback_protocol.md` drafted as the general
  P13 protocol for MWORKS/Sysplorer/Syslab, UE, Fab/manual import, Codex
  transport, Git/DevOps, and external-reference routes, including health
  levels, capability-card fields, stop/fallback rules, evidence-label
  interaction, and future `TOOL_*` checker codes.
- `tool_capability_health_gate_checker_design.md` drafted as the concrete
  P13/NEXT-27 checker contract for discovering required capability cards,
  enforcing health-level claim ceilings, rejecting stale or unsafe tool-route
  claims, validating fallback/blocker policies, and defining `TOOL_*`
  positive/negative fixtures.
- `implementation_sequence_and_release_plan.md` drafted as the P23 phase
  ladder from design audit to validator atoms, Candidate A, recovery,
  product-adjacent proofs, tool-backed product execution, and operating
  evolution, with entry/exit evidence, skip rules, release milestones, and
  approval-packet fields.
- `early_drift_detection_experiment_design.md` drafted as the P10/P29/P60
  experiment design for negative scenarios that catch wrong goals, missing
  evidence deltas, fake parallelism, stale context, missing blockers, timeout
  closeout gaps, unsupported tool claims, and completion overclaims before
  long-running tasks rely on the metrics checker.
- `task_health_monitoring_and_intervention_design.md` drafted as the
  P10/P25/P29/P60/P63/P67 intervention layer that turns metrics and task state
  into continue, watch, shrink, pause, block, review, close, or reject
  decisions with named owners and required evidence.
- `codex_visibility_recovery_experiment_design.md` drafted as the P12/P47/P61
  experiment design for clean registry, single and multi-department drift,
  unknown thread, missing rollout, Windows sync failure, repeated drift,
  provider-config, and credential/cache safety scenarios.
- `worktree_merge_recovery_experiment_design.md` drafted as the P08/P09/P37/P62
  experiment design for worktree mode selection, same-file conflicts, broad
  staging rejection, large-file policy, external path rejection, destructive
  action blockers, Git lock/timeout closeout, role separation, rollback, and
  worktree cleanup scenarios.
- `end_to_end_task_operating_runbook.md` drafted as the P63 composition layer
  that turns intake, goal authority, proof path, context, workflow graph,
  topology, execution, mailbox, review, integration, knowledge promotion, and
  closeout into one ordered operating sequence for serious user tasks.
- `real_task_execution_walkthroughs.md` drafted as the concrete P21/P22/P63
  walkthrough layer for PX4/Sunray150 parameter identification and UE/Fab/local
  scene-truth productization, mapping each task to conversations, context,
  mailbox packets, blockers, Git disposition, review gates, and completion
  criteria.
- `human_review_intervention_ux_design.md` drafted as the P64 PMO-facing
  intervention UX layer that defines review packets, allowed user decisions,
  severity, dedupe/rate-limit, redaction, resume mapping, and required cases
  for MWORKS license/login, UE/Fab manual import, visual review, destructive
  approval, invalid packets, and transport timeouts.
- `human_review_package_checker_design.md` drafted as the P64 checker contract
  for PMO-facing review packet fields, blocker-specific resume mapping,
  one-action asks, allowed decisions, dedupe, redaction, safe parallel work,
  manual evidence boundaries, notification readiness, and `HREV_*` fixtures.
- `validator_shared_envelope_design.md` drafted as the P65 shared validator
  envelope contract for schema version, decisions, dependency report shape,
  finding shape, evidence paths, side-effect declarations, claim boundaries,
  report storage, fixtures, and implementation boundary for
  `COAGENT-IMPL-NEXT-00`.
- `goal_alignment_checker_design.md` drafted as the P66 L0 checker contract
  for user/canonical/scoped goal, result mutation, checkpoint, and completion
  overclaim validation.
- `runbook_readiness_checker_design.md` drafted as the P67 readiness checker
  contract for serious task packages before multi-conversation dispatch,
  manual rehearsal, integration, or closeout.
- `implementation_approval_gate_design.md` drafted as the P68 implementation
  approval gate contract for explicit slice approval, phase entry evidence,
  scope, forbidden actions, dependency reports, exit evidence, and claim
  boundaries before any implementation starts.

## Dispatch Review Result

Source:

`Results/agent_packets/tasks/coagent_architecture/COAGENT-ARCH-LONGRUN-01-DISPATCH-01.yaml`

Accepted finding:

```text
Dynamic-team topology, communication, and context ownership rules are concrete
enough to continue the next architecture phase.
```

Remaining Dispatch-visible risks:

- runtime checks must reject missing canonical goal, scope, context pack,
  result path, review owner, and close condition before spawning;
- task board, mailbox, stale-context acknowledgement, and contradiction
  resolution need enforceable templates or checks;
- P12 and P25 remain active risk areas:
  App/VSCode/CLI recovery and productivity/process metrics.
- P13 now has a design baseline for tool capability cards, health gates,
  stop/fallback rules, and a concrete future checker contract, but no live
  tool reliability or automation is claimed.
- P23 now has a design baseline for implementation sequencing: R0 review
  baseline, R1 validator foundation, R2 packet/blocker atoms, R3 Candidate A
  preflight, R4 supervised Candidate A proof, R5 communication recovery, R6
  product-adjacent proofs, R7 tool-backed product execution, and R8 operating
  evolution.

## ContextMemoryAgent Review Result

Source:

`Results/agent_packets/tasks/coagent_architecture/COAGENT-ARCH-LONGRUN-01-CONTEXT-01.yaml`

Accepted with caveat:

```text
The context pack is sufficient for scoped handoff, but stale-context and
context-delta enforcement are still procedural.
```

Required follow-up:

- task packets and mailbox events must carry `context_pack_id`,
  `context_pack_version_or_hash`, `context_delta_id`, `supersedes`,
  `affected_slices`, `acknowledgement_required`,
  `acknowledgement_state`, `pause_until_refresh`, `reviewer`, and
  `resume_condition`;
- high-risk work cannot resume from stale context until the acknowledgement
  state is machine-checkable;
- knowledge promotion must mark accepted, superseded, rejected, and draft
  material explicitly.

## Context Delta Checker Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/context_delta_checker_design.md`

Decision:

```text
High-risk work cannot resume from stale context unless a read-only checker can
prove required context delta fields, affected receivers, acknowledgement state,
resume condition, reviewer, evidence, and context hash consistency.
```

Designed components:

- checker modes for delta-only, ack-only, pre-resume, post-result, and
  fixtures;
- stricter required delta lifecycle fields beyond the current template;
- required acknowledgement record fields;
- derived state model for fresh, stale, paused, ack-pending, ack-complete,
  blocked, and superseded context;
- pre-resume checks for missing ack, pause/resume, stale hash, reviewer, and
  high-risk work;
- post-result checks for stale context references, missing deltas, unreviewed
  changes, unnamed affected conversations, and invalid knowledge promotion;
- output JSON, stable `CTX_*` finding codes, fixture matrix, and integration
  with Candidate A, context index, mailbox, and handoff/workflow validators;
- future `COAGENT-IMPL-NEXT-02` implementation boundary.

Remaining requirement:

The checker is not implemented. Candidate A and any high-risk product proof
must treat stale-context resume as unsafe until this checker or an explicit
manual review gate exists.

## Context Index And Assembly Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/context_index_and_assembly_design.md`

Decision:

```text
New scoped conversations must receive context assembled from named index
families and task-specific slices, not from raw transcript volume or recency.
The assembler must cite source paths, record excluded stale material, enforce a
context budget class, and include rejected assumptions when a worker is likely
to repeat them.
```

Designed components:

- context index families for task, decision, context, evidence, safety,
  worktree/Git, tool capability, external adoption, and product scope;
- slice types such as goal, role, authority, evidence, safety, worktree,
  external learning, product scope, and closeout;
- assembly inputs required before a context pack is emitted;
- retrieval manifest shape;
- budget classes from compact to oversized;
- stale and rejected material filters;
- context fit checks;
- PX4 and UE context assembly examples;
- future `COAGENT-IMPL-NEXT-21` checker scope.

Remaining requirement:

The design does not implement retrieval. A later checker must verify retrieval
manifests, context budget, stale acknowledgement, source-path citation, and
high-risk rejected-assumption inclusion before automatic dispatch is trusted.

## RuntimePlatformAgent Dispatch Finding

Source:

`Results/coagent_transport/runs/COAGENT-ARCH-LONGRUN-01-RUNTIME-01.summary.md`

Finding:

```text
The visible conversation transport can resume a department thread and read
evidence, but the current run did not produce a result packet within the 60s
budget. Startup plugin sync/MCP file operations consumed the budget, and the
identified process had to be cleaned up.
```

Required follow-up:

- keep automatic conversation dispatch gated;
- add transport mode that disables or bypasses startup plugin sync if the
  runtime supports it, or increase timeout only for explicitly approved
  long-running dispatches;
- require a timeout blocker packet when a result file is missing after the
  budget;
- ensure an open dispatch edge is closed on timeout cleanup.

## Transport Timeout Hardening Design Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/transport_timeout_hardening_design.md`

Decision:

```text
Every visible-conversation dispatch attempt must end in exactly one durable
closeout state: accepted result, review-required result, invalid-result
blocker, transport-timeout blocker, canceled dispatch, or explicit retry
proposal. A timeout cannot remain as ambiguous background activity.
```

Designed components:

- dispatch-attempt state machine from planned/start/waiting/result/timeout to
  closeout;
- timeout classes for quick review, long review, implementation slice, and
  manual monitor;
- startup noise classification for plugin sync, plugin clone timeout, missing
  local plugin, MCP startup, state DB drift, and productive evidence reading;
- required closeout JSON and Markdown summary records;
- timeout blocker packet fields, dedupe key, retry policy, and evidence paths;
- late-result reconciliation rules that preserve timeout evidence;
- targeted cleanup policy and forbidden broad cleanup;
- runtime dispatch-edge reconciliation rules;
- stable `TRN_*` finding codes and fixtures;
- future `COAGENT-IMPL-NEXT-12` implementation boundary.

Remaining requirement:

The hardening logic is not implemented. Before Candidate A live proof is
trusted, the runtime should be able to reconcile no result, invalid result,
late result, live process, cleanup failure, and open edge into durable blocker
or result state.

## Codex Visibility Drift Reliability Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/codex_visibility_drift_reliability_design.md`

Decision:

```text
Recurring Codex visible-thread metadata drift is a pre-dispatch reliability
risk. Department visibility must be proved immediately before dispatch. If
drift appears, the system must either perform a bounded registered-thread
repair with evidence or emit a `codex_visibility_drift` blocker packet.
```

Designed components:

- visibility invariants for registry, WSL/Windows indexes, WSL main DB, WSL
  alternate DB, Windows DB, rollout path, cwd, and title;
- pre-dispatch gate sequence;
- allowed and forbidden repair policy;
- `codex_visibility_drift` blocker packet fields;
- evidence record paths for checks, repairs, and blockers;
- state machine from `visible_verified` to `repair_succeeded` or
  `blocked_visibility`;
- future `COAGENT-IMPL-NEXT-22` gate scope.

Remaining requirement:

The design does not implement the gate. Root cause is still unknown. The next
implementation should prioritize safe detection, bounded repair, evidence, and
blocker creation before investigating Codex internals.

## VerificationAgent Review Result

Source:

`Results/agent_packets/tasks/coagent_architecture/COAGENT-ARCH-LONGRUN-01-VERIFY-01.yaml`

Accepted with caveat:

```text
The verification protocol detects the right drift modes conceptually, but is
not yet an executable gate.
```

Required follow-up:

- define metric thresholds for critical path time, blocked time, fake
  parallelism, serial collapse, handoff failure, context refresh latency,
  rework, review escape, and closeout latency;
- add mandatory evidence templates for PX4 identifiability and UE scene truth;
- add a negative drift-packet dry run that must be rejected by the gate;
- require exact files, schemas, packet fields, and import/review outputs for
  minimal closed-loop acceptance.

## Result Packet And Blocker Contract Update

Sources:

- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/result_packet_contract_hardening.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/result_packet_validator_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/blocker_packet_templates.md`

Decision:

```text
Durable department communication must use a flat router-compatible result
packet until the router supports nested YAML. Conditional completion is modeled
with review_status=needs_review and acceptance_state=partially_met, not custom
status strings.
```

Designed components:

- required packet fields and conditional fields;
- allowed statuses, review statuses, and acceptance states;
- structural rejection rules for nested YAML, YAML block scalars, bad lists,
  duplicate fields, and raw transcript evidence;
- semantic rejection rules for goal mutation, missing evidence, stale context,
  scope violation, blocker incompleteness, missing reviewer, and capability
  overclaim;
- validator JSON output and stable finding codes;
- positive and negative fixture matrix;
- repair policy that permits only non-substantive shape repair with a
  `repair_note`;
- future `COAGENT-IMPL-NEXT-11` read-only validator scope.

Remaining requirement:

The result packet validator is not implemented. Future Candidate A or live
department dispatch should run this checker before treating returned packets
as durable communication.

## Mailbox Ledger And Replay Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/mailbox_ledger_and_replay_design.md`

Decision:

```text
Any cross-conversation message that changes work state must be recorded in a
project-owned mailbox ledger. Replay must reconstruct open messages, blockers,
acknowledgements, expected responses, contradictions, supersessions, and the
next safe action without relying on raw chat.
```

Designed components:

- task-local message ids and file-first storage model;
- required message fields;
- allowed message types;
- message state machine from `draft` to `closed`, `blocked`, or `superseded`;
- acknowledgement record;
- replay contract;
- timeout/retry rules;
- contradiction handling;
- closeout and recovery rules;
- future `COAGENT-IMPL-NEXT-23` checker scope.

Remaining requirement:

The mailbox ledger is not implemented. The next validator should prove message
schema, ack requirements, replay, duplicate blocker dedupe, contradiction
handling, and closeout failure before live multi-conversation proof is trusted.

Blocker classes now required for future implementation backlog:

- `transport_timeout`;
- `invalid_result_packet`;
- `auth_or_license_required`;
- `manual_review_required`;
- `destructive_action_approval_required`.

## Enterprise Execution Mapping Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/enterprise_to_coagent_execution_mapping.md`

Decision:

```text
Enterprise-management concepts are useful only when they map to durable
CoAgent objects: task charter, task team, scoped conversation, context pack,
mailbox, result/review/blocker packet, worktree binding, integration packet,
knowledge promotion record, or retrospective action.
```

Design consequence:

- the system stays task-first rather than department-first;
- departments remain capability and review lanes;
- scoped conversations own slices, not canonical task goals;
- subagents remain disposable bounded helpers;
- enterprise practices become packet/state/review transitions instead of
  process decoration.

## Operating Metrics And Anti-Drift Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/operating_metrics_and_anti_drift_cadence.md`

Decision:

```text
Long-running tasks need fast worker checkpoints, medium Dispatch board
reviews, and slow retrospective learning loops. Drift detection must be based
on metrics and packets, not late intuition.
```

Metrics now drafted:

- progress metrics: critical path age, checkpoint age, accepted artifact count,
  integration queue age;
- coordination metrics: open mailbox count, handoff failures, context refresh
  latency, unresolved contradiction age;
- quality metrics: evidence gaps, review escapes, rework, unsupported claims;
- organization metrics: fake parallelism, serial collapse, WIP overrun, idle
  permanent lanes;
- safety/reliability metrics: blocked time without packet, unsafe retry,
  transport timeout, duplicate manual asks.

Remaining requirement:

These metrics are design baseline only. They need a future read-only snapshot
implementation and negative drift fixtures before they become an executable
gate.

## Operating Metrics Snapshot Design Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/operating_metrics_snapshot_design.md`

Decision:

```text
A long-running task cannot be called healthy merely because there is recent
chat activity or many documents. Health must be computed from durable task
state, checkpoints, packets, board state, audit evidence, blockers, context
freshness, transport findings, and review status.
```

Designed components:

- read-only input contract for task root, runtime DB, events JSONL,
  department registry, result packets, and transport summaries;
- metric object model with allowed states: `ok`, `info`,
  `needs_instrumentation`, `review_required`, `blocked`, and `rejected`;
- progress, coordination, quality, organization, safety, and reliability
  metric categories;
- data classification: measured, derived, reported, needs instrumentation, or
  not applicable;
- drift detection rules for goal drift, context drift, evidence drift, scope
  bloat, topology bloat, research loops, implementation-before-gate, and
  review escape;
- negative fixture requirements for stale checkpoints, completion overclaim,
  missing context ack, timeout without blocker, WIP excess, unmapped research,
  unsupported claims, fake parallelism, and missing data;
- stable `OMS_*` finding codes;
- JSON and Markdown output shapes;
- integration points with result packet, context delta, handoff/workflow,
  mailbox, visibility drift, and proof-package validators;
- future `COAGENT-IMPL-NEXT-09` implementation boundary.

Remaining requirement:

The snapshot is not implemented. Until `COAGENT-IMPL-NEXT-09` or an explicit
manual audit is accepted, operating health remains a design contract rather
than an executable gate.

## Minimal Multi-Conversation Proof Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/minimal_multiconversation_proof_requirements.md`

Decision:

```text
The next proof should not use all 11 permanent conversations. It should use the
smallest visible set that proves the control loop: MainAgent, DispatchAgent,
ContextMemoryAgent, VerificationAgent, and KnowledgeSecretaryAgent, with
optional Runtime/DevOps/Safety/Toolchain only when the proof requires them.
```

Recommended proof:

- Candidate A: architecture packet chain first;
- Candidate B: PX4 parameter-identification gate after packet chain is stable;
- Candidate C: UE scene-truth capability gate after packet chain is stable.

Pass/fail rules now require:

- complete packet chain;
- unchanged canonical task goal;
- no stale-context high-risk continuation;
- no open required mailbox response;
- review disposition and closeout;
- blocker packet for invalid packet or transport timeout.

## Handoff Mode And Workflow Graph Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/handoff_mode_and_workflow_graph_design.md`

Decision:

```text
Routing decisions must become `handoff_mode` and `workflow_graph` objects, not
only prose. Future dispatch automation should validate these objects before
starting a scoped conversation or department handoff.
```

Design objects:

- `CoAgent/protocol/templates/handoff_mode.yaml`;
- `CoAgent/protocol/templates/workflow_graph.yaml`.

Remaining requirement:

These objects are design contracts. Runtime graph execution and automatic
validation remain future implementation work.

## Problem-Driven External Adoption Queue Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/problem_driven_external_adoption_queue.md`

Decision:

```text
External learning must start from a current CoAgent problem id, read the
smallest relevant source slice, and produce an adoption/rejection decision with
evidence level. Broad "study all projects again" work is not acceptable without
a problem matrix entry.
```

Priority queue:

- `EXT-003`: handoff/workflow objects;
- `EXT-002`: context lifecycle and delta acknowledgement;
- `EXT-001`: transport timeout/blocker reliability;
- `EXT-006`: operating metrics and fake-parallelism detection;
- `EXT-011`: trace evaluation and artifact manifests;
- `EXT-007`: worktree binding validator;
- `EXT-012`: adoption queue mechanics.

Remaining requirement:

This queue is design baseline. `external_adoption_proposal_contract.md` now
defines the structured proposal lifecycle, required fields, examples, and
future validator checks. A later implementation slice should add the proposal
store/checker and at least one accepted plus one rejected fixture.

## External Adoption Proposal Contract Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/external_adoption_proposal_contract.md`

Decision:

```text
External ideas must be handled as auditable proposals, not as raw summaries or
chat memory. Every proposal must name one problem id, one bounded source slice,
one decision, one evidence level, one owner, one review owner, one promotion or
rejection path, and one future verification method.
```

Designed components:

- proposal id format: `ADOPT-YYYYMMDD-<problem_id>-<short_slug>`;
- storage model for future proposal, decision, and rejection records;
- required proposal fields;
- lifecycle states from `draft` through `promoted` or `superseded`;
- decision vocabulary;
- evidence levels from `source_seen` to `promoted`;
- acceptance and rejection rules;
- positive and rejection examples;
- future read-only validator checks.

Remaining requirement:

The contract is design evidence. `COAGENT-IMPL-NEXT-10` must still implement a
proposal store/checker before self-evolution can be claimed beyond design.

## External Adoption Store Checker Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/external_adoption_store_checker_design.md`

Decision:

```text
External learning is valid only when one bounded source slice maps to one
current CoAgent problem and one auditable adoption decision. Broad source
summaries are not accepted architecture changes.
```

Designed components:

- future `CoAgent/adoption/` store layout for proposals, decisions,
  rejections, and fixtures;
- checker modes for single proposal, full store, promotion, and fixtures;
- required proposal schema with problem id, source refs, source slice, fit,
  risk, license/security notes, adaptation, evidence level, decision, owner,
  reviewer, and next trigger;
- lifecycle and store-level checks for duplicates, supersession, accepted
  proposals, rejected proposals, and draft leakage into context;
- evidence-level guard that rejects `validated`, `proved_in_loop`, or
  `promoted` claims without matching artifacts;
- source boundary rules for local reference corpus, unsafe paths, and code-copy
  license/security separation;
- decision rules for accepted, rejected, and probe-first proposals;
- JSON output, stable `ADOPT_*` finding codes, fixture matrix, and integration
  with problem matrix, context index, operating metrics, and proof ladder;
- future `COAGENT-IMPL-NEXT-10` implementation boundary.

Remaining requirement:

The store/checker is not implemented. Until it exists, future external study
must remain task-local and manually linked to the problem matrix, adoption
queue, and proposal contract.

## Candidate A Packet Chain Blueprint Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_packet_chain_blueprint.md`

Decision:

```text
Candidate A is the next low-tool-risk proof, but it must be executed from a
fixed blueprint rather than improvised during dispatch. The proof task id is
COAGENT-PROOF-CANDIDATE-A, and the minimal required visible set is MainAgent,
DispatchAgent, ContextMemoryAgent, VerificationAgent, and
KnowledgeSecretaryAgent.
```

Required packet chain:

- task charter and handoff records;
- context sufficiency result or blocker;
- verification review packet and trace evaluation;
- knowledge promotion or rejected-idea record;
- at least one context delta;
- closeout that states what was proven and what remains gated.

Pass criteria now explicitly forbid:

- automatic conversation creation;
- automatic worktree creation;
- app-server transport;
- email/desktop notification;
- UE/MWORKS/Fab execution;
- broad Git operations;
- canonical-goal mutation by any worker.

Remaining requirement:

Do not run Candidate A until the user or PMO explicitly moves from design to
the proof experiment. If executed later, the proof should produce valid result
or blocker packets without manual repair, or it should be treated as evidence
that packet/transport hardening must come first.

## Candidate A Proof Package Design Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_proof_package_design.md`
`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_validator_execution_design.md`

Decision:

```text
Candidate A should be treated as a proof package first and live dispatch
second. The package must define required inputs, required outputs, workflow
graph shape, validation checks, negative fixtures, and result interpretation
before any multi-conversation execution starts.
```

Required future package root:

```text
Results/coagent_proofs/COAGENT-PROOF-CANDIDATE-A/
```

Validation emphasis:

- preflight rejects missing context pack, missing review gate, external result
  paths, raw transcript context, forbidden graph nodes, or canonical-goal
  mutation;
- post-dispatch rejects missing packets, missing context delta, missing trace
  metric, unacknowledged context change, or timeout without blocker;
- negative fixtures become the basis for a later package validator.

Remaining requirement:

Add a future validator or fixture generator before making Candidate A the
default live proof. The validator execution design now defines the CLI modes,
package layout, validation pipeline, dependency boundaries, output JSON,
Candidate A finding codes, fixture execution, live-proof gate, post-dispatch
closeout gate, and implementation boundary. A manual live proof can still be
approved, but it should use this package shape and be judged against these
checks.

## Handoff Workflow Validator Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/handoff_workflow_validator_design.md`

Decision:

```text
Handoff and workflow graph objects are not dispatch authority until a
read-only validator proves task id, canonical goal, context, result path,
review, return path, blocker/resume, closeout, and high-risk-node semantics.
```

Designed components:

- validator modes for handoff-only, workflow-only, pre-dispatch,
  post-dispatch, and fixtures;
- required fields for handoff and workflow objects;
- allowed mode, authority, node, edge, and state values;
- cross-object checks between charter, handoff, workflow, and node outputs;
- dispatch safety checks for context pack, result path, review owner, resume
  rules, forbidden actions, cycles, reachability, and high-risk nodes;
- post-dispatch checks for missing outputs, non-terminal reviews, open
  blockers, goal mutation, and unsafe integration requests;
- output JSON, stable `HWFLOW_*` finding codes, fixture matrix, and Candidate A
  integration;
- future `COAGENT-IMPL-NEXT-13` implementation boundary.

Remaining requirement:

The validator is not implemented. Candidate A preflight should depend on this
checker before any live multi-conversation dispatch is treated as safe by
default.

## Candidate B PX4 Parameter Proof Package Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_b_px4_parameter_proof_package.md`

Decision:

```text
PX4 parameter identification must start with log audit and identifiability,
not estimator code. The proof package must classify each simulator parameter as
directly observed, estimated, calibrated, assumed, behavior-matched, or
non-identifiable, with uncertainty, residuals, evidence labels, and blockers.
```

Key gates:

- estimator implementation starts only for identifiable or weakly identifiable
  rows;
- MWORKS tuning starts only after model/tool health and simulator mapping pass;
- offline outputs remain labeled `offline_script`;
- missing signals, missing vehicle specs, high uncertainty, and license/tool
  failures become blocker packets.

Remaining requirement:

Do not run Candidate B until Candidate A packet-chain mechanics are stable or
the user explicitly accepts packet/transport risk. The first live gate should
be the identifiability matrix.

## Candidate C UE Scene Truth Proof Package Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_c_ue_scene_truth_proof_package.md`

Decision:

```text
UE scene work must start with scene-source classification and UE/MCP
capability, not rendering or map modification. Planning readiness requires
truth artifacts such as collision, navmesh, occupancy, SDF, semantic map,
path feasibility, or coordinate calibration.
```

Key gates:

- Fab/manual-import and UE/MCP failures become blocker packets rather than
  endless retries;
- visual review supports manual acceptance but cannot substitute for planning
  truth;
- large assets require Git/LFS/ignore policy before integration;
- algorithm integration starts only after planning-readiness is true or
  limitations are explicit.

Remaining requirement:

Do not run Candidate C until Candidate A packet-chain mechanics are stable or
the user explicitly accepts packet/transport risk. The first live gate should
be scene-source classification and UE/MCP capability, not map editing.

## Candidate D Git Heavy Change Proof Package Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_d_git_heavy_change_proof_package.md`

Decision:

```text
Large Git work must start with change inventory, path-family classification,
worktree binding decision, integration plan, verification plan, and blocker
policy. The proof must reject broad `git add -A` as a strategy.
```

Key gates:

- classify source, docs, generated outputs, binaries, external references,
  deleted/renamed paths, large-file candidates, and ignored/untracked scope;
- name merge owner, review owner, close owner, checks, rollback, and cleanup;
- block destructive or broad staging actions until explicit approval;
- treat real staging, commit, push, and worktree creation as later approved
  implementation work.

## Worktree Merge Recovery Experiment Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/worktree_merge_recovery_experiment_design.md`

Decision:

```text
Git-heavy work needs a recovery experiment, not only a high-level proof
package. The future checker must prove CoAgent can pick a workspace mode,
block unsafe Git plans, assign review/merge/close owners, and recover from
locks, timeouts, conflicts, large files, and user changes without broad
staging or main-thread blockage.
```

Key scenarios:

- shared workspace allowed only for small low-conflict changes with a recorded
  waiver;
- task, slice, review, arena, and integration worktrees require explicit
  binding records before implementation;
- same-file conflicts require sequencing, section ownership, or one
  integration owner;
- broad `git add -A`, external path staging, large binaries without policy,
  missing rollback, missing cleanup, and high-risk role collapse are rejected;
- Git lock, slow Git, or timeout states become blocker/recovery records rather
  than repeated broad commands.

Remaining requirement:

Future `COAGENT-IMPL-NEXT-04` and `COAGENT-IMPL-NEXT-18` should share the
`GIT_*` scenario contract from this experiment. The design still does not
approve real staging, committing, pushing, worktree creation, cleanup, or
destructive Git repair.

## End-To-End Task Operating Runbook Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/end_to_end_task_operating_runbook.md`

Decision:

```text
CoAgent needs an explicit end-to-end operating runbook that composes the
individual protocols. A serious user task should move through intake,
canonical charter, proof-path classification, context assembly, workflow graph,
topology selection, execution checkpoints, mailbox replay, evidence review,
integration/hold, knowledge promotion, retrospective, and closeout.
```

Key gates:

- task goals are outcomes, not activity placeholders;
- proof-path first gates decide which conversations are needed;
- delegated work needs context, result path, review owner, return path, and
  close condition before execution;
- closeout requires result, review, blocker state, context delta, mailbox
  closure, Git disposition, knowledge decision, and next work representation;
- design, runtime, tool, Git, and product claims stay separated by evidence
  labels.

Remaining requirement:

Future implementation should add a read-only runbook readiness checker after
the shared validator envelope exists. The runbook itself does not approve live
dispatch, worktree creation, Git operations, MCP/tool execution, notification,
or automatic completion.

## Validator Shared Envelope Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/validator_shared_envelope_design.md`

Decision:

```text
All validators and doctor-style checks must emit a shared report envelope so
decisions, missing dependencies, findings, evidence paths, side effects, and
claim boundaries are consumable by downstream validators, operating metrics,
and completion audits.
```

Key gates:

- common decisions are `pass`, `pass_with_warnings`, `needs_review`,
  `needs_dependency`, `fail_before_dispatch`, `blocked`, `reject`, and
  `not_applicable`;
- `ok=true` is allowed only for `pass`, `pass_with_warnings`, or
  `not_applicable`;
- missing required dependencies cannot be downgraded to pass;
- side effects must be declared, and read-only validators must forbid live
  dispatch, conversation creation, runtime mutation, MCP/tool calls, GUI
  automation, credential handling, Git mutation, notifications, and external
  fetches;
- claim boundaries must state what the report proves and what it does not
  prove.

Remaining requirement:

Future `COAGENT-IMPL-NEXT-00` should implement shared constants/schema,
sample reports, and envelope fixtures before domain-specific validators are
implemented.

## Goal Alignment Checker Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/goal_alignment_checker_design.md`

Decision:

```text
Goal alignment must be a level-zero gate. A downstream validator passing is
not meaningful if the canonical task goal, local objective, result packet,
checkpoint, or completion audit has weakened the user's original objective
into setup work, topology, elapsed time, document volume, or unapproved
implementation.
```

Key gates:

- task charters must expose user objective, canonical goal, required scope
  components, and non-substitution summary;
- scoped packets must include a concrete `alignment_to_canonical_goal`;
- result packets must not mutate or narrow the assigned objective;
- long-task checkpoints must record evidence deltas and requirements advanced;
- completion audits must not pass requirements from weak, indirect, or pending
  evidence;
- recreated goals must preserve prior scope and have recovery records.

Remaining requirement:

Future `COAGENT-IMPL-NEXT-25` should implement the read-only checker with
`GOAL_*` fixtures and the shared validator envelope before unattended
long-task orchestration or completion automation is trusted.

## Candidate E Auth/License Interruption Proof Package Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_e_auth_license_interruption_proof_package.md`

Decision:

```text
Manual intervention is a task state, not a failure. Login, license, GUI,
manual-review, tool-unavailable, and approval blockers must produce durable
blocker packets with last safe state, exact PMO user ask, resume condition,
safe parallel work decision, dedupe key, and retry policy.
```

Key gates:

- only MainAgent/PMO sends the user-facing ask;
- tool slices stop after suspected login/license blockers instead of retrying;
- safe parallel work may continue only if blocked claims remain blocked;
- email/desktop notification remains gated until blocker/resume semantics are
  proven and redaction/rate-limit/audit design exists.

## Proof Ladder And Validator Order Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/proof_ladder_and_validator_order.md`

Decision:

```text
The default bridge from architecture design to implementation is now a proof
ladder: A communication packet chain, then product-adjacent PX4/UE proofs, plus
Git-heavy and auth/license operational-risk proofs when triggered.
```

Validator order:

1. result packet hardening;
2. Candidate A proof-package validator;
3. handoff/workflow graph validators;
4. context delta checker;
5. operating metrics snapshot;
6. transport timeout hardening;
7. PX4 and UE product proof validators;
8. Git-heavy and auth/license operational-risk validators.

Design consequence:

New task types must either fit an existing candidate, extend the shared
proof-package contract, or add a new candidate with the same preflight,
post-dispatch, blocker, review, and closeout discipline.

## Common Proof Package Validator Design Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/common_proof_package_validator_design.md`

Decision:

```text
A future read-only validator should enforce one common proof-package contract
across Candidate A-E before live dispatch and after closeout. Candidate-specific
rules extend the common checks instead of replacing them.
```

Designed components:

- input modes: `preflight`, `post_dispatch`, and `fixture`;
- expected package layout under `Results/coagent_proofs/<proof-id>/`;
- common preflight error codes;
- common post-dispatch error codes;
- Candidate A-E extension checks;
- JSON output format and high-level decisions;
- fixture matrix for valid and negative cases;
- read-only implementation boundary.

Remaining requirement:

Implementation remains gated under `COAGENT-IMPL-NEXT-20`. The validator must
not live-dispatch conversations, call tools, create worktrees, stage Git, send
notifications, or automate GUI/login/license flows.

## Goal Requirement Audit Map Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/goal_requirement_audit_map.md`

Decision:

```text
The active 10-hour goal must be audited by requirement, evidence, and remaining
gap. Partial design progress is not completion unless current evidence proves
the relevant requirement.
```

The audit map now records:

- active goal requirements;
- evidence map for task-first design, multi-conversation work, context, Git,
  review, safety, human intervention, external learning, self-evolution,
  proof design, department results, implementation backlog, and final audit;
- strong evidence;
- weak or incomplete evidence;
- audit-time commands;
- next work priority;
- explicit interim conclusion that the goal remains active and incomplete.

## Human Review And Intervention UX Update

Source:

`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/human_review_intervention_ux_design.md`

Decision:

```text
Human intervention needs a PMO-facing review packet and deterministic resume
path. A manual ask must state one action, reason, last safe state, allowed
decision values, resume condition, safe parallel work, timeout/default, dedupe
key, redaction boundary, and post-resume verification.
```

Key gates:

- only MainAgent/PMO sends user-facing asks;
- worker conversations propose review packets but do not directly ask the user
  for external action;
- duplicate blockers update one active packet instead of sending repeated asks;
- auth/license/GUI blockers do not trigger blind retries;
- manual visual acceptance stays labeled as `manual_review` and cannot become
  planning truth, MWORKS evidence, UE evidence, or automated proof;
- email and desktop notification remain gated until schema, dedupe, severity,
  rate limit, redaction, test mode, opt-in, and audit log are proven.

Remaining requirement:

A future read-only human-review package checker should validate review packet
fields, decision vocabulary, dedupe, redaction, blocker-specific resume probes,
safe parallel-work claims, and notification readiness. It must not send email,
open GUIs, call MCP/tools, create conversations, mutate runtime state, or
handle credentials.
