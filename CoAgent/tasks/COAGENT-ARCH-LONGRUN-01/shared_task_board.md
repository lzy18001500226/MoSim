# COAGENT-ARCH-LONGRUN-01 Shared Task Board

Date: 2026-05-30
Status: active
Board owner: DispatchAgent
Canonical task goal: sustain at least 10 hours of CoAgent architecture design
work and produce reviewable architecture artifacts.

## Current Phase

`phase_2_dynamic_architecture_protocols_and_operating_metrics`

Phase 1 created the recoverable control plane. Phase 2 is refining the actual
architecture protocols that determine how dynamic task teams operate.

## Work In Progress Limit

WIP limit: 4 active design streams at once.

Reason: more parallel streams will increase coordination overhead before the
packet, mailbox, and context-refresh rules are fully audited.

## Permanent Conversation State

| Department | Thread | State | Role In This Task |
|---|---|---|---|
| MainAgent | `MoSim锝滃洓鏃嬬考鏃犱汉鏈轰豢鐪熺郴缁焋 | active_visible | user PMO, final synthesis, review entry |
| DispatchAgent | `MoSim锝滆皟搴︿腑鍙癭 | active_visible | task board, topology, mailbox, result routing |
| ProductStrategyAgent | `MoSim锝滀骇鍝佸彂鐜版垬鐣 | active_visible | product goals, appetite, non-goals |
| RuntimePlatformAgent | `MoSim锝淎gent Runtime 骞冲彴` | active_visible | conversation/session/transport/worktree design |
| ContextMemoryAgent | `MoSim锝滀笂涓嬫枃璁板繂绱㈠紩` | active_visible | context pack, memory, indexing, drift controls |
| ToolchainMCPAgent | `MoSim锝滃伐鍏烽摼 MCP` | active_visible | MCP/tool capability and failure-mode design |
| KnowledgeSecretaryAgent | `MoSim锝滅煡璇嗙涔 | active_visible | docs, decisions, knowledge promotion |
| VerificationAgent | `MoSim锝滈獙璇佽瘎娴媊 | active_visible | evidence, tests, trace/eval rubric |
| SafetyComplianceAgent | `MoSim锝滃畨鍏ㄥ悎瑙刞 | active_visible | safety, policy, human-intervention gates |
| DevOpsReleaseAgent | `MoSim锝淒evOps 鍙戝竷` | active_visible | Git/worktree/merge/release strategy |
| ExternalIntelligenceAgent | `MoSim锝滃閮ㄦ儏鎶ヨ繘鍖朻 | active_visible | vendor/open-source learning loop |

## Phase 1 Items

| ID | Owner | State | Output | Close Condition |
|---|---|---|---|---|
| A1 | DispatchAgent | completed | `department_dispatch_plan.md` | all departments have scoped work contracts |
| A2 | ContextMemoryAgent | completed_draft | `context_pack.md`, `communication_context_protocol.md` | context layers and refresh rules are sufficient for new conversations |
| A3 | MainAgent + DispatchAgent | completed_draft | `architecture_problem_matrix.md` | main architecture problems are classified with owners |
| A4 | RuntimePlatformAgent | completed_draft | `dynamic_team_decision_rules.md` | Codex conversation/worktree feature use is mapped to CoAgent objects |
| A5 | VerificationAgent | completed_draft | `verification_evaluation_protocol.md` | product and process-quality evidence are separated |
| A6 | SafetyComplianceAgent | completed_draft | `safety_human_intervention_protocol.md` | auth/license/GUI/destructive-action flows have stop/resume rules |
| A7 | DevOpsReleaseAgent | completed_draft | `worktree_git_integration_protocol.md` | large-change and multi-worktree risks have gates |
| A8 | ExternalIntelligenceAgent | completed_draft | `self_evolution_protocol.md` | external ideas become reviewed decisions, not raw summaries |
| A9 | KnowledgeSecretaryAgent | completed_draft | `knowledge_promotion_protocol.md` | accepted decisions have a home and stale docs are identified |
| A10 | ProductStrategyAgent | completed_draft | `product_appetite_and_non_goals.md` | PX4 and UE stress tests have product-level done/non-goals |

## Phase 2 Items

| ID | Owner | State | Output | Close Condition |
|---|---|---|---|---|
| B1 | DispatchAgent + KnowledgeSecretaryAgent | completed_draft | `enterprise_to_coagent_execution_mapping.md` | enterprise-management concepts map to concrete CoAgent objects instead of static bureaucracy |
| B2 | VerificationAgent + DispatchAgent | completed_draft | `operating_metrics_and_anti_drift_cadence.md` | long-task cadence and anti-drift metrics are explicit enough to become a later read-only metrics snapshot |
| B3 | DispatchAgent + VerificationAgent | completed_draft | `minimal_multiconversation_proof_requirements.md` | next proof has concrete conversations, packet chain, metrics, pass/fail rules, and recommended candidate |
| B4 | DispatchAgent + RuntimePlatformAgent | completed_draft | `handoff_mode_and_workflow_graph_design.md` | handoff mode and workflow graph objects make routing decisions explicit instead of prose-only |
| B5 | ExternalIntelligenceAgent + KnowledgeSecretaryAgent | completed_draft | `problem_driven_external_adoption_queue.md` | external sources are routed through problem ids, evidence levels, adoption decisions, and next triggers |
| B6 | DispatchAgent + VerificationAgent + ContextMemoryAgent | completed_draft | `candidate_a_packet_chain_blueprint.md` | Candidate A has exact task id, required conversations, packet outputs, context requirements, review outputs, trace metrics, pass/block criteria, and follow-on decisions |
| B7 | DispatchAgent + RuntimePlatformAgent + VerificationAgent | completed_draft | `candidate_a_proof_package_design.md` | Candidate A has a proof-package shape, required inputs/outputs, preflight checks, post-dispatch checks, negative fixtures, and result interpretation before live execution |
| B8 | ProductStrategyAgent + VerificationAgent + ContextMemoryAgent | completed_draft | `candidate_b_px4_parameter_proof_package.md` | PX4 parameter identification has a proof-package design with log audit, identifiability matrix, estimator/simulation gates, blockers, evidence labels, and acceptance rules |
| B9 | ToolchainMCPAgent + ProductStrategyAgent + VerificationAgent | completed_draft | `candidate_c_ue_scene_truth_proof_package.md` | UE scene truth has a proof-package design with source gate, capability card, truth manifest, planning-readiness rules, manual blockers, and product-scope controls |
| B10 | DevOpsReleaseAgent + SafetyComplianceAgent + VerificationAgent | completed_draft | `candidate_d_git_heavy_change_proof_package.md` | Git-heavy rename/import work has a proof-package design for inventory, worktree binding, integration planning, large-file policy, destructive-action blockers, and rollback |
| B11 | SafetyComplianceAgent + DispatchAgent + VerificationAgent | completed_draft | `candidate_e_auth_license_interruption_proof_package.md` | Auth/license/GUI/manual-review interruption has a proof-package design for blocker packet, user ask, safe parallel work, resume packet, retry policy, and closeout |
| B12 | DispatchAgent + VerificationAgent | completed_draft | `proof_ladder_and_validator_order.md` | A-E proof packages are consolidated into one execution ladder, shared contract, preflight/post-dispatch checks, validator order, and audit questions |
| B13 | VerificationAgent + RuntimePlatformAgent | completed_draft | `common_proof_package_validator_design.md` | Common validator design defines inputs, layout, preflight checks, post-dispatch checks, candidate-specific extensions, JSON output, fixtures, and read-only implementation boundary |
| B14 | DispatchAgent + VerificationAgent | completed_draft | `goal_requirement_audit_map.md` | Active goal requirements are mapped to evidence, strong/weak proof, remaining gaps, audit commands, and next priority without claiming completion |
| B15 | VerificationAgent + DispatchAgent | completed_draft | `candidate_a_fixture_spec.md` | Candidate A has concrete positive/negative fixture specifications, expected stable error codes, validator order, and implementation acceptance before live dispatch |
| B16 | DispatchAgent + ProductStrategyAgent + VerificationAgent | completed_draft | `task_intake_to_proof_ladder_decision_table.md` | User task intake now maps to proof path A-E, first gate, minimum team, secondary risks, and anti-drift checkpoint questions |
| B17 | DispatchAgent + VerificationAgent + MainAgent | completed_draft | `ten_hour_audit_package.md` | 10-hour review has a concentrated verdict table, required commands, requirement-to-audit mapping, forbidden claims, user decision points, and closeout checklist |
| B18 | ExternalIntelligenceAgent + KnowledgeSecretaryAgent + VerificationAgent | completed_draft | `external_adoption_proposal_contract.md` | External ideas now have a structured proposal lifecycle, required fields, evidence levels, accept/reject rules, examples, future validator checks, and promotion closeout |
| B19 | ContextMemoryAgent + DispatchAgent + VerificationAgent | completed_draft | `context_index_and_assembly_design.md` | New conversations now have a context-index and assembly contract covering source indexes, required slices, retrieval manifest, budget classes, stale/rejected filters, fit checks, PX4/UE examples, and future checker scope |
| B20 | RuntimePlatformAgent + DispatchAgent + SafetyComplianceAgent | completed_draft | `codex_visibility_drift_reliability_design.md` | Recurring Codex visible-thread metadata drift now has pre-dispatch invariants, diagnose/repair/blocker flow, evidence records, state machine, and future gate scope |
| B21 | DispatchAgent + VerificationAgent + KnowledgeSecretaryAgent | completed_draft | `mailbox_ledger_and_replay_design.md` | Cross-conversation communication now has a project-owned mailbox ledger design with message schema, state machine, ack records, replay, timeout/retry, contradiction handling, closeout, recovery, and future checker scope |
| B22 | VerificationAgent + RuntimePlatformAgent + DispatchAgent | completed_draft | `result_packet_validator_design.md` | Result packet hardening now has a validator design with required fields, allowed values, structural and semantic rejection rules, output JSON, stable finding codes, fixture matrix, repair policy, and implementation boundary |
| B23 | VerificationAgent + DispatchAgent + RuntimePlatformAgent | completed_draft | `candidate_a_validator_execution_design.md` | Candidate A validator now has an execution design covering CLI modes, package layout, validation pipeline, dependency boundaries, report JSON, finding codes, fixture mode, live-proof gate, post-dispatch closeout gate, and implementation boundary |
| B24 | DispatchAgent + RuntimePlatformAgent + VerificationAgent | completed_draft | `handoff_workflow_validator_design.md` | Handoff/workflow graph validators now have a design contract covering inputs, modes, required fields, cross-object checks, dispatch safety checks, post-dispatch checks, output JSON, stable finding codes, fixtures, Candidate A integration, and implementation boundary |
| B25 | ContextMemoryAgent + DispatchAgent + VerificationAgent | completed_draft | `context_delta_checker_design.md` | Context delta checker now has a design contract covering stricter lifecycle fields, ack records, state model, pre-resume checks, post-result checks, JSON output, stable finding codes, fixtures, and integration with Candidate A, context index, mailbox, and workflow validators |
| B26 | VerificationAgent + DispatchAgent + RuntimePlatformAgent | completed_draft | `operating_metrics_snapshot_design.md` | Operating metrics snapshot now has a design contract covering read-only inputs, metric model, data classification, drift rules, stable `OMS_*` finding codes, negative fixtures, JSON/Markdown output, validator integration, and implementation boundary |
| B27 | RuntimePlatformAgent + DispatchAgent + SafetyComplianceAgent | completed_draft | `transport_timeout_hardening_design.md` | Transport timeout hardening now has a design contract covering dispatch attempt state machine, timeout classes, startup noise classification, closeout records, timeout blockers, late-result reconciliation, cleanup policy, dispatch edge reconciliation, stable `TRN_*` finding codes, fixtures, and implementation boundary |
| B28 | ExternalIntelligenceAgent + KnowledgeSecretaryAgent + VerificationAgent | completed_draft | `external_adoption_store_checker_design.md` | External adoption store checker now has a design contract covering proposal store layout, checker modes, schema fields, lifecycle checks, evidence-level guard, source boundaries, decision rules, JSON output, stable `ADOPT_*` finding codes, fixtures, and implementation boundary |
| B29 | SafetyComplianceAgent + RuntimePlatformAgent + VerificationAgent | completed_draft | `blocker_packet_validator_design.md` | Blocker packet validator now has a design contract covering common fields, allowed blocker types, type-specific requirements, duplicate ask prevention, unsafe retry rejection, stable `BLK_*` finding codes, fixtures, and implementation boundary |
| B30 | ProductStrategyAgent + ToolchainMCPAgent + VerificationAgent | completed_draft | `stress_test_artifact_validator_design.md` | PX4/UE stress-test artifact validators now have a design contract covering identifiability matrix checks, scene capability/truth manifest checks, evidence-label cross-checks, stable `PX4_*`, `UE_*`, and `STRESS_*` finding codes, fixtures, and implementation boundary |
| B31 | VerificationAgent + SafetyComplianceAgent + ProductStrategyAgent | completed_draft | `evidence_label_doctor_design.md` | Evidence label doctor now has a design contract covering allowed provenance labels, label strength, required evidence fields, label inflation rejection, stable `EVD_*` finding codes, fixtures, and implementation boundary |
| B32 | VerificationAgent + DispatchAgent + RuntimePlatformAgent | completed_draft | `validator_dependency_and_rollout_plan.md` | Validator dependency and rollout plan now defines validator layers, dependency graph, rollout order, dependency failure policy, common output envelope, Candidate A/product/operational minimum gate sets, and `needs_dependency` behavior |
| B33 | DispatchAgent + VerificationAgent + ContextMemoryAgent | completed_draft | `candidate_a_minimal_package_contract.md` | Candidate A minimal package contract now defines the exact proof/fixture file layout, shared constants, required YAML/text fields, handoff shape, context delta, review, trace-eval, closeout, preflight validity, and post-dispatch validity |
| B34 | DispatchAgent + VerificationAgent + RuntimePlatformAgent | completed_draft | `candidate_a_fixture_generation_plan.md` | Candidate A fixture generation now has a deterministic plan covering source documents, shared constants, positive build order, controlled negative mutations, fixture expectation files, path safety, dependency behavior, manual stop points, and a future generator slice |
| B35 | DispatchAgent + MainAgent + VerificationAgent | completed_draft | `candidate_a_manual_rehearsal_plan.md` | Candidate A supervised rehearsal now has explicit preconditions, approval record, manual dispatch sequence, stop rules, review checklist, result interpretation, evidence labels, and forbidden claims so manual visible-conversation testing cannot be mistaken for validated automation |
| B36 | DispatchAgent + MainAgent + VerificationAgent | completed_draft | `goal_completion_gate_protocol.md` | Long-run goal completion now has a requirement-by-requirement gate distinguishing design completion from runtime proof and implementation completion, with allowed verdicts, evidence hierarchy, mandatory final audit artifact, and forbidden shortcuts |
| B37 | DispatchAgent + KnowledgeSecretaryAgent + VerificationAgent | completed_draft | `architecture_decision_record_summary.md` | Major CoAgent architecture decisions are now summarized as ADR-style records covering task-first operation, conversation topology, source of truth, subagent boundary, proof ladder, validators, evidence labels, blockers, Git, external learning, completion gate, deferred decisions, and rejected decisions |
| B38 | DispatchAgent + MainAgent + VerificationAgent | active_draft | `final_goal_completion_audit.md` | Final completion audit working draft now maps every active goal requirement to a verdict, evidence, gated follow-up, forbidden claim, implementation queue, user decision, and current non-complete decision pending final refresh |
| B39 | DispatchAgent + MainAgent + VerificationAgent | completed_draft | `goal_authority_and_decomposition_protocol.md` | Goal authority now separates user objective, canonical task goal, task-team goal, department goal, scoped conversation objective, subagent prompt objective, and implementation step goal so setup actions, visible conversations, elapsed time, or document volume cannot replace the real user outcome |
| B40 | KnowledgeSecretaryAgent + DispatchAgent + VerificationAgent | completed_draft | `retrospective_and_improvement_closure_protocol.md` | Retrospective closure now defines mandatory triggers, improvement-action schema, ownership, promotion/rejection gates, stale-action policy, and future `RETRO_*` checker codes so repeated failures become closed learning loops instead of chat memory |
| B41 | ToolchainMCPAgent + SafetyComplianceAgent + VerificationAgent | completed_draft | `tool_capability_health_and_fallback_protocol.md` | Tool capability is now a gated evidence object with route families, health levels, capability-card fields, stop/fallback decisions, evidence-label interaction, and future `TOOL_*` checker codes so UE/MWORKS/Fab/Codex/Git routes cannot be assumed from stale or weak signals |
| B42 | DispatchAgent + RuntimePlatformAgent + VerificationAgent | completed_draft | `implementation_sequence_and_release_plan.md` | Post-design implementation sequencing now has an R0-R8 phase ladder with entry/exit evidence, skip rules, release milestones, approval-packet fields, and forbidden claims so implementation cannot jump from design backlog to high-risk product automation |
| B43 | MainAgent + DispatchAgent + VerificationAgent | completed_draft | `goal_creation_and_recovery_protocol.md` | Goal creation and recovery now has a preflight and recovery path so deleting a wrong goal leads to recreating the real user outcome, not a setup-action placeholder |
| B44 | VerificationAgent + DispatchAgent + MainAgent | completed_draft | `early_drift_detection_experiment_design.md` | Early drift detection now has concrete positive and negative scenarios for wrong goals, missing evidence deltas, fake parallelism, stale context, missing blockers, timeout closeout gaps, unsupported tool claims, repeated review escapes, and completion overclaims |
| B45 | RuntimePlatformAgent + SafetyComplianceAgent + VerificationAgent | completed_draft | `codex_visibility_recovery_experiment_design.md` | Codex visibility recovery now has a bounded experiment design for clean registry, registered single/multi-department drift, unknown thread, missing rollout, Windows sync failure, repeated drift, provider-config, and credential/cache safety scenarios |
| B46 | DevOpsReleaseAgent + SafetyComplianceAgent + VerificationAgent | completed_draft | `worktree_merge_recovery_experiment_design.md` | Worktree/Git recovery now has concrete scenarios for workspace mode selection, same-file conflict handling, broad staging rejection, large-file policy, external path rejection, destructive-action blockers, Git lock/timeout closeout, role separation, rollback, and cleanup |
| B47 | DispatchAgent + MainAgent + VerificationAgent + KnowledgeSecretaryAgent | completed_draft | `end_to_end_task_operating_runbook.md` | Serious user tasks now have an end-to-end operating sequence from intake and canonical charter through proof-path routing, context, workflow graph, execution, mailbox replay, review, integration/hold, knowledge promotion, retrospective, and closeout |
| B48 | MainAgent + SafetyComplianceAgent + DispatchAgent + VerificationAgent | completed_draft | `human_review_intervention_ux_design.md` | Human review and intervention now has a PMO-facing packet design covering one-action asks, allowed decisions, severity, dedupe/rate-limit, redaction, resume mapping, required MWORKS/UE/Fab/visual/Git/transport cases, audit log, and future checker scope |
| B49 | VerificationAgent + RuntimePlatformAgent + DispatchAgent | completed_draft | `validator_shared_envelope_design.md` | Future validators now share one report envelope for schema version, target, decisions, dependencies, findings, evidence paths, side effects, claim boundaries, storage, fixtures, and implementation boundary |
| B50 | DispatchAgent + MainAgent + VerificationAgent | completed_draft | `goal_alignment_checker_design.md` | Goal alignment now has a read-only L0 checker design covering user objective, canonical goal, scoped objective alignment, result goal mutation, checkpoint evidence delta, completion overclaim, recreated-goal scope loss, and `GOAL_*` fixtures |
| B51 | DispatchAgent + VerificationAgent + KnowledgeSecretaryAgent | completed_draft | `runbook_readiness_checker_design.md` | End-to-end runbook readiness now has a read-only checker design covering charter, proof path, context, workflow, mailbox, packets, evidence labels, Git disposition, knowledge decision, closeout readiness, dependencies, and `RUNBOOK_*` fixtures |
| B52 | DispatchAgent + SafetyComplianceAgent + VerificationAgent | completed_draft | `implementation_approval_gate_design.md` | Implementation approval now has a read-only gate design covering explicit approval, phase entry evidence, scope, forbidden actions, dependency reports, exit evidence, claim boundaries, and `APPROVAL_*` fixtures |
| B53 | KnowledgeSecretaryAgent + DispatchAgent + VerificationAgent | completed_draft | `retrospective_closure_checker_design.md` | Retrospective closure now has a read-only checker design covering trigger discovery, record presence, ownership, evidence, action targets, close conditions, promotion/rejection/deferral, stale actions, dependencies, claim boundaries, and `RETRO_*` fixtures |
| B54 | DevOpsReleaseAgent + SafetyComplianceAgent + VerificationAgent | completed_draft | `worktree_git_recovery_validator_design.md` | Worktree/Git recovery now has a read-only validator family design covering worktree binding, change inventory, Git-heavy integration plans, blockers, role separation, rollback, cleanup, safe decisions, and `GIT_*` fixtures |
| B55 | MainAgent + SafetyComplianceAgent + VerificationAgent | completed_draft | `human_review_package_checker_design.md` | Human-review packages now have a read-only checker design covering one-action asks, blocker-specific resume mapping, allowed decisions, dedupe, redaction, safe parallel work, manual evidence boundaries, notification readiness, and `HREV_*` fixtures |
| B56 | ToolchainMCPAgent + SafetyComplianceAgent + VerificationAgent | completed_draft | `tool_capability_health_gate_checker_design.md` | Tool capability health gates now have a read-only checker design covering card discovery, route/health/evidence vocabulary, staleness, health-level claim ceilings, blocker/fallback policy, unsafe write probes, route-specific UE/Fab/MWORKS/Codex/Git/external rules, dependency handling, and `TOOL_*` fixtures |
| B57 | DispatchAgent + ProductStrategyAgent + ToolchainMCPAgent + VerificationAgent | completed_draft | `real_task_execution_walkthroughs.md` | Real task walkthroughs now map PX4/Sunray150 parameter identification and UE/Fab/local scene truth into concrete task goals, initial teams, task-scoped conversations, context packs, workflow graphs, mailbox/result packets, blockers, Git disposition, review gates, and completion criteria |
| B58 | DispatchAgent + VerificationAgent + MainAgent + SafetyComplianceAgent | completed_draft | `task_health_monitoring_and_intervention_design.md` | Task health intervention now has a runtime operating playbook covering health states, triggers, owners, required interventions, critical-path ownership, topology shrinking, human intervention, PX4/UE applications, close-ready criteria, and future `COAGENT-IMPL-NEXT-32` checker scope |

## Review Gates

| Gate | Owner | Required Before |
|---|---|---|
| `goal_alignment` | MainAgent + DispatchAgent | any scoped conversation proposal |
| `context_sufficiency` | ContextMemoryAgent | any worker dispatch |
| `safety_boundary` | SafetyComplianceAgent | any tool/MCP/runtime implementation |
| `worktree_merge_gate` | DevOpsReleaseAgent | any multi-worktree design becomes implementation |
| `evidence_gate` | VerificationAgent | claiming a design decision is settled |
| `knowledge_promotion_gate` | KnowledgeSecretaryAgent | updating skills/hooks/workflows as stable policy |

## Open Blockers

None blocking Phase 1 file-level architecture work.

Known gated items:

- app-server transport implementation;
- automatic conversation creation;
- automatic worktree provisioning;
- unattended scheduler;
- real email sender;
- new permanent departments;
- broad hook/tool/MCP expansion.

## Department Result Packets

| Result | State | Key Finding |
|---|---|---|
| `Results/agent_packets/tasks/coagent_architecture/COAGENT-ARCH-LONGRUN-01-DISPATCH-01.yaml` | imported_done | Topology, communication, and context rules are concrete enough to continue; remaining Dispatch risks are runtime enforcement, transport/recovery, and review-gate operationalization. |
| `Results/agent_packets/tasks/coagent_architecture/COAGENT-ARCH-LONGRUN-01-CONTEXT-01.yaml` | imported_done_needs_review | Context packs are sufficient for scoped handoff only if task packets carry version/hash, acknowledgement state, pause/resume state, and stale-context ownership. Current stale-context handling is procedural, not yet machine-checkable. |
| `Results/agent_packets/tasks/coagent_architecture/COAGENT-ARCH-LONGRUN-01-RUNTIME-01.yaml` | blocked_no_result | RuntimePlatformAgent dispatch reached the visible conversation and read evidence, but did not produce a result packet within the 60s budget. The identified dispatch process was cleaned up. Treat this as a transport reliability risk. |
| `Results/agent_packets/tasks/coagent_architecture/COAGENT-ARCH-LONGRUN-01-VERIFY-01.yaml` | imported_done_needs_review | Verification protocol can detect long-task drift conceptually, but thresholds, required packet fields, evidence templates, and negative drift tests are still required before it becomes an executable gate. |

## Current Risk Register

| Risk | Owner | State | Required Design Response |
|---|---|---|---|
| Context packs can drift across visible conversations without a durable version/hash and acknowledgement record. | ContextMemoryAgent + DispatchAgent | active | Add context lifecycle schema and doctor gate before high-risk resume. |
| Result packets from visible conversations may use unsupported nested YAML or custom statuses. | RuntimePlatformAgent + VerificationAgent | active | Strengthen packet instructions and add router-compatible templates or validation feedback loop. |
| `codex exec resume` transport can spend the 60s budget on plugin sync/MCP startup noise and fail to return a packet. | RuntimePlatformAgent | active | Run transport hardening experiment; keep automatic dispatch gated until timeout/recovery is reliable. |
| Verification metrics are advisory without thresholds and state-transition rules. | VerificationAgent | active | Define metric thresholds, required fields, and negative tests for drifting packets. |
| Codex visible-thread metadata can drift in the WSL alternate DB for DispatchAgent, causing `check_department_visibility.py` to fail until `sync-visible --apply` is rerun. | RuntimePlatformAgent + DispatchAgent | active_recurring | Treat visibility metadata drift as a transport/session-state reliability risk; add a future automatic diagnose/repair-or-blocker check before dispatch. |

## New Protocol Artifacts From Review Findings

| Artifact | Reason |
|---|---|
| `context_lifecycle_schema.md` | Converts ContextMemoryAgent warning into context version, delta, acknowledgement, pause/resume, and doctor-check fields. |
| `context_delta_checker_design.md` | Defines the future read-only checker for context delta fields, acknowledgement records, stale-context resume, result-context freshness, and fixture cases. |
| `verification_gate_hardening.md` | Converts VerificationAgent warning into metric thresholds, required packet extensions, PX4/UE templates, and negative drift tests. |
| `transport_reliability_findings.md` | Records RuntimePlatformAgent timeout and VerificationAgent invalid-packet behavior as transport design evidence. |
| `transport_timeout_hardening_design.md` | Defines the future hardening contract for Codex dispatch timeout, plugin/MCP startup noise, late results, cleanup, blocker packets, edge reconciliation, and `TRN_*` findings. |
| `result_packet_contract_hardening.md` | Defines the flat router-compatible result packet template for department conversations. |
| `result_packet_validator_design.md` | Defines the future read-only validator for result packet fields, statuses, list syntax, evidence, context hash, scope, capability claims, repair notes, stable findings, and fixtures. |
| `blocker_packet_templates.md` | Defines timeout, invalid packet, auth/license, manual review, and destructive-action blocker packets. |
| `blocker_packet_validator_design.md` | Defines the future read-only validator for blocker packet fields, allowed blocker types, duplicate active asks, unsafe retry, destructive-action ambiguity, secret risk, timeout closeout, and `BLK_*` findings. |
| `CoAgent/protocol/templates/px4_parameter_identifiability_matrix.yaml` | Makes PX4 parameter-identification claims auditable by category, signal support, uncertainty, residuals, and evidence label. |
| `CoAgent/protocol/templates/ue_scene_truth_capability_card.yaml` | Makes UE scene-source and MCP capability claims auditable before planning-truth work starts. |
| `CoAgent/protocol/templates/scene_truth_artifact_manifest.yaml` | Makes exported collision/navmesh/occupancy/SDF truth artifacts auditable for planning consumers and Git policy. |
| `stress_test_artifact_validator_design.md` | Defines the future read-only validators for PX4 identifiability matrices and UE scene-truth artifacts, including overclaim rejection and product-evidence limits. |
| `evidence_label_doctor_design.md` | Defines the future evidence-label doctor for distinguishing design-only, offline, manual, GUI, MCP, Git, runtime, and external-reference evidence. |
| `validator_dependency_and_rollout_plan.md` | Defines the gate graph and rollout order tying evidence labels, result packets, blockers, handoffs, context, proof packages, metrics, transport, mailbox, visibility, and external adoption together. |
| `enterprise_to_coagent_execution_mapping.md` | Converts the enterprise-management model into concrete CoAgent objects: charter, team, context, mailbox, packets, worktree, review, integration, and retrospective records. |
| `operating_metrics_and_anti_drift_cadence.md` | Defines checkpoint cadence, operating metrics, drift states, escalation triggers, and retrospective triggers for long-running multi-conversation tasks. |
| `operating_metrics_snapshot_design.md` | Defines the future read-only snapshot checker for long-task health, anti-drift metrics, negative drift fixtures, evidence links, and `OMS_*` finding codes. |
| `minimal_multiconversation_proof_requirements.md` | Defines the smallest useful visible multi-conversation proof, including required packet chain, metrics, pass/fail rules, and recommended Candidate A. |
| `handoff_mode_and_workflow_graph_design.md` | Turns topology routing into `handoff_mode` and `workflow_graph` objects that can later be validated before dispatch. |
| `handoff_workflow_validator_design.md` | Defines the future read-only validator for handoff and workflow graph objects before dispatch and after closeout. |
| `problem_driven_external_adoption_queue.md` | Converts vendor/open-source learning into a problem-driven adoption queue with states, evidence levels, rejection rules, and priority order. |
| `candidate_a_packet_chain_blueprint.md` | Turns Candidate A into an executable proof blueprint with task charter, handoff records, context-pack requirements, result/review/context-delta/trace-eval requirements, pass/block criteria, and explicit non-authorization of gated automation. |
| `candidate_a_proof_package_design.md` | Defines the future Candidate A proof package root, required input/output files, validation checks, negative fixtures, and result interpretation so live dispatch is not improvised. |
| `candidate_a_validator_execution_design.md` | Defines how the future Candidate A validator should run preflight, post-dispatch, and fixture modes without live dispatch or gated automation. |
| `candidate_a_minimal_package_contract.md` | Defines the exact minimal Candidate A proof package and fixture file contract, including task charter, context pack, workflow graph, handoffs, packets, context delta, review, trace metrics, and closeout fields. |
| `candidate_a_fixture_generation_plan.md` | Defines how a future generator should build the valid Candidate A fixture and derive negative fixtures by controlled mutation, with expectation files, path safety, dependency behavior, and manual review stops. |
| `candidate_a_manual_rehearsal_plan.md` | Defines the supervised manual Candidate A rehearsal path, including approval record, preconditions, stop rules, manual review checklist, evidence labels, and forbidden claims before validators exist. |
| `goal_completion_gate_protocol.md` | Defines how the active 10-hour design goal can be closed only through requirement verdicts, authoritative evidence, accepted gated follow-ups, final audit artifact, and explicit separation from runtime or implementation proof. |
| `architecture_decision_record_summary.md` | Consolidates the main architecture decisions, alternatives, deferrals, and rejected approaches into one ADR-style audit surface. |
| `final_goal_completion_audit.md` | Provides the working final audit table for requirement verdicts, gated follow-ups, forbidden claims, remaining implementation queue, user decisions, and the current non-complete decision pending final refresh. |
| `goal_authority_and_decomposition_protocol.md` | Defines the goal hierarchy and non-substitution rules so lower-level task, department, conversation, subagent, or implementation goals cannot silently weaken the user's objective. |
| `goal_creation_and_recovery_protocol.md` | Defines the goal-creation preflight, invalid setup-goal patterns, wrong-goal recovery path, checkpoint fields, and future `GOAL_*` checker additions for active Codex goals. |
| `early_drift_detection_experiment_design.md` | Defines the negative and positive scenario package for proving future operating-metrics checks catch wrong goals, fake progress, fake parallelism, stale context, missing blockers, and completion overclaims before long-running work relies on them. |
| `codex_visibility_recovery_experiment_design.md` | Defines the evidence package and scenario matrix for proving registered Codex visible-thread drift can be checked, repaired, or blocked without claiming root-cause reliability or touching unrelated Codex state. |
| `worktree_merge_recovery_experiment_design.md` | Defines the scenario package for proving future Git/worktree checks handle workspace mode selection, same-file conflicts, broad staging rejection, large binaries, external paths, destructive actions, Git locks/timeouts, rollback, role separation, cleanup, and main-thread Git blockage without executing real Git operations. |
| `end_to_end_task_operating_runbook.md` | Defines the ordered operating sequence for serious user tasks: intake, charter, proof path, context assembly, workflow graph, topology, execution checkpoints, mailbox replay, evidence review, integration/hold, knowledge promotion, retrospective, and closeout. |
| `candidate_b_px4_parameter_proof_package.md` | Defines the future PX4 parameter-identification proof package, including data sufficiency, identifiability, estimator, simulation-tuning, verification, blocker, and evidence-label gates. |
| `candidate_c_ue_scene_truth_proof_package.md` | Defines the future UE scene-truth proof package, including scene-source classification, UE/MCP capability, truth-artifact manifest, planning readiness, manual review, and large-asset policy gates. |
| `candidate_d_git_heavy_change_proof_package.md` | Defines the future Git-heavy change proof package, including inventory, worktree binding, integration plan, large-file/generated-output policy, destructive-action blockers, and rollback. |
| `candidate_e_auth_license_interruption_proof_package.md` | Defines the future auth/license/manual-intervention proof package, including blocker packet, exact PMO user ask, safe parallel work, resume packet, retry/circuit breaker, and closeout. |
| `proof_ladder_and_validator_order.md` | Consolidates Candidate A-E into the default proof ladder, common proof contract, shared checks, validator order, deviation rules, and user audit questions. |
| `common_proof_package_validator_design.md` | Defines the future read-only validator for Candidate A-E proof packages, including error codes, candidate extensions, JSON output, fixture matrix, and implementation boundary. |
| `goal_requirement_audit_map.md` | Maps the active 10-hour goal requirements to current evidence, incomplete areas, audit commands, and next work priority. |
| `candidate_a_fixture_spec.md` | Turns Candidate A validator work into concrete positive and negative fixture specifications so later implementation can fail deterministically before live dispatch. |
| `task_intake_to_proof_ladder_decision_table.md` | Routes real user tasks to Candidate A-E proof paths by task class and first gate, keeping CoAgent task-driven instead of department-count-driven. |
| `ten_hour_audit_package.md` | Concentrates the final review procedure so the user can audit design progress, partial evidence, commands, decision points, and next approvals without relying on chat memory. |
| `external_adoption_proposal_contract.md` | Turns external learning and self-evolution into a structured proposal contract with lifecycle states, required fields, evidence levels, accept/reject rules, examples, and future validator checks. |
| `external_adoption_store_checker_design.md` | Defines the future read-only checker for adoption proposal store records, evidence-level inflation, source boundaries, promotion gates, and `ADOPT_*` findings. |
| `context_index_and_assembly_design.md` | Defines how context is retrieved and assembled for new conversations from task, decision, context, evidence, safety, worktree, tool, external-adoption, and product-scope indexes without transcript bloat. |
| `codex_visibility_drift_reliability_design.md` | Converts recurring DispatchAgent visibility metadata drift into a pre-dispatch reliability design with invariants, bounded repair policy, blocker packet, evidence records, and future gate. |
| `mailbox_ledger_and_replay_design.md` | Defines durable cross-conversation communication through task-local messages, ack records, replay, timeout/retry rules, contradiction handling, closeout, and recovery. |
| `retrospective_and_improvement_closure_protocol.md` | Converts repeated failures, user corrections, review escapes, and incidents into owned improvement actions with evidence, closeout, promotion or rejection decisions, and future `RETRO_*` validation. |
| `tool_capability_health_and_fallback_protocol.md` | Converts MCP/tool availability into auditable capability cards, health gates, evidence labels, fallback/stop decisions, blocker policies, and future `TOOL_*` validation across MWORKS, UE, Fab/manual import, Codex transport, Git, and external-reference routes. |
| `implementation_sequence_and_release_plan.md` | Converts the large post-design backlog into an R0-R8 implementation phase ladder with entry and exit evidence, skip rules, approval-packet requirements, release milestones, and explicit boundaries before product/tool execution. |
| `human_review_intervention_ux_design.md` | Converts manual intervention into a PMO-facing review UX: review packet fields, allowed user decisions, severity, dedupe/rate-limit, redaction, resume mapping, audit log, required cases, notification boundary, and future checker scope. |
| `validator_shared_envelope_design.md` | Defines the shared validator report envelope for `COAGENT-IMPL-NEXT-00`, including decision vocabulary, dependency report shape, finding shape, evidence paths, side-effect declarations, claim boundaries, report storage, fixtures, and integration rules. |
| `goal_alignment_checker_design.md` | Defines the read-only L0 goal-alignment checker for `COAGENT-IMPL-NEXT-25`, including inputs, required fields, alignment checks, modes, `GOAL_*` finding codes, fixture matrix, shared-envelope output, and implementation boundary. |
| `runbook_readiness_checker_design.md` | Defines the read-only runbook readiness checker for `COAGENT-IMPL-NEXT-30`, including readiness levels, required stage checks, dependency handling, `RUNBOOK_*` finding codes, fixture matrix, shared-envelope output, and implementation boundary. |
| `implementation_approval_gate_design.md` | Defines the read-only implementation approval gate for `COAGENT-IMPL-NEXT-31`, including explicit approval, phase-entry checks, scope boundary, dependency evidence, exit evidence, claim boundaries, `APPROVAL_*` finding codes, fixture matrix, shared-envelope output, and implementation boundary. |
| `retrospective_closure_checker_design.md` | Defines the read-only retrospective closure checker for `COAGENT-IMPL-NEXT-26`, including trigger discovery, required record shape, ownership/evidence/action checks, stale-action policy, dependency reporting, fixture matrix, shared-envelope output, and implementation boundary. |
| `worktree_git_recovery_validator_design.md` | Defines the read-only worktree/Git recovery validator family for `COAGENT-IMPL-NEXT-04` and `COAGENT-IMPL-NEXT-18`, including worktree binding, inventory, integration, blocker, rollback, cleanup, evidence-label, and `GIT_*` fixture rules. |
| `human_review_package_checker_design.md` | Defines the read-only human-review package checker for `COAGENT-IMPL-NEXT-29`, including PMO-facing packet fields, blocker-specific resume mapping, dedupe, redaction, safe parallel work, manual evidence boundaries, notification readiness, and `HREV_*` fixtures. |
| `tool_capability_health_gate_checker_design.md` | Defines the read-only tool capability health gate checker for `COAGENT-IMPL-NEXT-27`, including card discovery, required fields, route-specific claim ceilings, stale-card rules, blocker/fallback validation, unsafe probe rejection, dependency behavior, and `TOOL_*` fixtures. |
| `real_task_execution_walkthroughs.md` | Defines scenario-level walkthroughs for PX4/Sunray150 parameter identification and UE/Fab/local scene truth, including how one user task becomes a task team, context pack, workflow graph, mailbox/result chain, blocker flow, Git disposition, review gate, and closeout. |
| `task_health_monitoring_and_intervention_design.md` | Defines the runtime intervention playbook for long tasks: health states, trigger-to-action table, critical-path rule, topology shrink rules, PMO blocker asks, PX4/UE health applications, close-ready gate, and future read-only task-health checker boundary. |

## Next Checkpoints

1. Prepare the Candidate A minimal multi-conversation proof as the next
   experiment proposal, but keep execution gated by proof-package validation,
   transport reliability, and user review.
2. Use `problem_driven_external_adoption_queue.md` for further external
   learning; do not reopen broad "study all projects" work without a problem
   id.
3. Convert handoff mode and workflow graph fields into future validators after
   design review.
4. Convert operating metrics and anti-drift cadence into a later read-only
   metrics snapshot implementation proposal.
5. Use `proof_ladder_and_validator_order.md` as the default bridge from
   design into implementation and live proofs.
6. Use Candidate B and Candidate C proof-package designs as the default
   shape for future PX4 and UE task intake after Candidate A is stable.
7. Treat RuntimePlatformAgent dispatch timeout as an architecture finding and
   create a bounded transport hardening experiment.
8. Add negative packet/drift fixtures after implementation approval.
9. Keep `review_brief.md` current for the 10-hour user audit.
10. Keep `goal_requirement_audit_map.md` current so final review can prove
    scope coverage requirement by requirement.
11. Use `ten_hour_audit_package.md` as the final audit entry before any claim
    that the active goal is complete.
12. Use `external_adoption_proposal_contract.md` before accepting any external
    vendor/open-source idea as a stable CoAgent change.
13. Use `context_index_and_assembly_design.md` before dispatching new scoped
    conversations that need curated history instead of raw transcript.
14. Use `codex_visibility_drift_reliability_design.md` before trusting
    visible-department dispatch readiness after any visibility check failure.
15. Use `mailbox_ledger_and_replay_design.md` before treating peer messages,
    blockers, reviews, or closeout as recoverable cross-conversation state.
16. Use `result_packet_validator_design.md` before trusting department result
    packets as durable communication or spending live multi-conversation
    transport budget.
17. Use `candidate_a_validator_execution_design.md` before implementing or
    running Candidate A validation so preflight, post-dispatch, fixture, and
    dependency behavior are not improvised.
18. Use `handoff_workflow_validator_design.md` before dispatching any
    multi-node graph or handoff so routing, review, return, blocker, and
    closeout semantics are validated from files.
19. Use `context_delta_checker_design.md` before resuming high-risk work after
    context changes or accepting a result that cites context pack state.
20. Use `operating_metrics_snapshot_design.md` before claiming a long-running
    task is healthy, parallel, unblocked, or ready to close based on activity
    rather than evidence-backed metrics.
21. Use `transport_timeout_hardening_design.md` before trusting a live
    department dispatch that times out, produces a late result, leaves a live
    process, or leaves an open runtime edge.
22. Use `external_adoption_store_checker_design.md` before treating an external
    article, open-source project, or local reference as an accepted CoAgent
    architecture change.
23. Use `blocker_packet_validator_design.md` before treating auth/license,
    GUI, timeout, invalid packet, manual review, destructive action, or
    tool-unavailable stops as recoverable durable state.
24. Use `worktree_merge_recovery_experiment_design.md` before approving
    large Git work, multi-worktree implementation, broad imports/renames,
    large assets, same-file conflict resolution, or Git recovery handling.
25. Use `end_to_end_task_operating_runbook.md` as the default composition
    layer before routing a serious new user task into multiple conversations or
    proofs.
24. Use `stress_test_artifact_validator_design.md` before accepting PX4
    parameter-identification or UE scene-truth artifacts as product-adjacent
    proof.
25. Use `evidence_label_doctor_design.md` before promoting design/offline/
    manual/tool evidence into proof-package closeout or report claims.
26. Use `validator_dependency_and_rollout_plan.md` before implementing or
    sequencing validators so missing dependencies are reported as
    `needs_dependency` instead of silently weakening gates.
27. Use `candidate_a_minimal_package_contract.md` before generating Candidate A
    fixtures or a live proof package so the file shape and field requirements
    are deterministic.
28. Use `candidate_a_fixture_generation_plan.md` before implementing Candidate
    A fixture generation so positive and negative fixtures are generated from
    one valid base package, expected codes, and controlled mutations instead
    of hand-written drift.
29. Use `candidate_a_manual_rehearsal_plan.md` before any supervised Candidate
    A visible-conversation rehearsal if validators are still missing, so the
    run is labeled as manual rehearsal with explicit approval, stop rules, and
    forbidden claims.
30. Use `goal_completion_gate_protocol.md` before any claim that
    `COAGENT-ARCH-LONGRUN-01` is complete, so each requirement has a verdict,
    evidence, accepted gated follow-up, and no forbidden runtime claim.
31. Use `architecture_decision_record_summary.md` during user audit to review
    major accepted, deferred, and rejected decisions without rereading every
    detailed protocol file.
32. Use `final_goal_completion_audit.md` as the final refresh target before
    any completion claim; current state remains a working draft, not an
    `update_goal complete` trigger.
33. Use `goal_authority_and_decomposition_protocol.md` before writing task
    charters, scoped conversation packets, or completion audits, so setup
    actions and topology changes are not mistaken for satisfying the user's
    real objective.
34. Use `retrospective_and_improvement_closure_protocol.md` after repeated
    failures, user corrections, review escapes, or incidents so lessons close
    through owned actions, promotion, rejection, or explicit deferral instead
    of remaining scattered notes.
35. Use `tool_capability_health_and_fallback_protocol.md` before any
    product-adjacent task depends on MWORKS, UE, Fab, Codex transport, Git, or
    external-reference routes, so capability claims are gated by current
    health evidence and failed routes stop or downgrade claims instead of
    starting open-ended retries.
36. Use `implementation_sequence_and_release_plan.md` before approving any
    implementation slice, so the work starts from validator foundation and
    packet/blocker atoms before Candidate A, recovery, product-adjacent proofs,
    or tool-backed product execution.
37. Use `human_review_intervention_ux_design.md` before asking the user for
    login, license, GUI, visual-review, destructive-action, Git, invalid-packet,
    or transport-timeout decisions, so asks are specific, deduplicated,
    redacted, resumable, and not confused with automated proof.
38. Use `validator_shared_envelope_design.md` before implementing any validator
    or checker, so missing dependencies, side effects, claim boundaries,
    evidence paths, findings, and decisions are reported consistently across
    result, blocker, context, mailbox, proof, tool, Git, human-review,
    retrospective, and metrics validators.
39. Use `goal_alignment_checker_design.md` before trusting task charters,
    scoped packets, result packets, checkpoints, or completion audits, so
    setup work, topology, elapsed time, document volume, or unapproved
    implementation cannot replace the user's original objective.
40. Use `retrospective_closure_checker_design.md` before closing repeated
    failures, user corrections, incidents, or review escapes as learned, so
    recurrence requires owner, evidence, action target, close condition,
    promotion/rejection/deferral decision, and `RETRO_*` validation instead
    of a status-note memory dependency.
41. Use `worktree_git_recovery_validator_design.md` before multi-conversation
    mutable work, large imports, broad renames, binary/generated batches, or
    DevOps integration, so Git starts from inventory, ownership, rollback,
    cleanup, blocker state, and `GIT_*` checks rather than broad staging.
42. Use `human_review_package_checker_design.md` before asking the user,
    recording a user decision, or resuming from manual intervention, so the
    packet has one concrete action, allowed decision values, dedupe, redaction,
    last safe state, blocker-specific probe, evidence boundaries, and
    notification readiness checks.
43. Use `tool_capability_health_gate_checker_design.md` before implementing
    `COAGENT-IMPL-NEXT-27` or relying on UE/Fab/MWORKS/Codex/Git/external
    route claims, so stale cards, weak evidence, unsafe write probes, fallback
    overclaims, and UI/screenshot/Fab/offline evidence inflation fail with
    stable `TOOL_*` findings.
44. Use `real_task_execution_walkthroughs.md` when reviewing whether the
    architecture really answers concrete PX4/Sunray150 and UE/Fab/local-scene
    tasks, so CoAgent is judged by task flow, context, communication,
    blockers, Git integration, review, and closeout rather than by department
    labels.
45. Use `task_health_monitoring_and_intervention_design.md` during active
    long-running tasks before allowing continued work, topology growth,
    manual asks, review gates, integration, or closeout, so metrics produce a
    concrete intervention decision rather than a passive dashboard.
