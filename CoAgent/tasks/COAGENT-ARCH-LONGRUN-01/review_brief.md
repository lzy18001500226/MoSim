# COAGENT-ARCH-LONGRUN-01 Review Brief

Date: 2026-05-30
Status: active review entry

## What The User Should Audit After 10 Hours

Audit whether CoAgent architecture was actually advanced, not whether a task
shell was created.

## Primary Review Question

Can CoAgent now explain and operate a long-running task-first workflow where:

```text
one user task
  -> one canonical task goal
  -> a dynamic task team
  -> multiple visible conversations when useful
  -> short-lived subagents only inside bounded slices
  -> curated context packs
  -> packet/mailbox communication
  -> explicit review and Git integration
  -> clear human intervention
  -> knowledge promotion and self-evolution
```

## Required Evidence To Inspect

Start here:

- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/task_charter.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/shared_task_board.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/context_pack.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/architecture_problem_matrix.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/architecture_decision_record_summary.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/department_dispatch_plan.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/goal_requirement_audit_map.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/goal_completion_gate_protocol.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/goal_authority_and_decomposition_protocol.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/goal_creation_and_recovery_protocol.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/retrospective_and_improvement_closure_protocol.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/final_goal_completion_audit.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/ten_hour_audit_package.md`

Then inspect changed architecture and decision docs under:

- `CoAgent/docs/architecture/`
- `CoAgent/docs/decisions/`
- `CoAgent/docs/status/`
- `PROGRESS.md`

Runtime task state:

- `Results/agent_runtime/tasks.sqlite3`
- `Results/agent_runtime/events.jsonl`

Protocol drafts added during this run:

- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/dynamic_team_decision_rules.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/communication_context_protocol.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/mailbox_ledger_and_replay_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/context_lifecycle_schema.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/context_delta_checker_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/context_index_and_assembly_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/result_packet_contract_hardening.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/result_packet_validator_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/blocker_packet_templates.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/blocker_packet_validator_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/worktree_git_integration_protocol.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/verification_evaluation_protocol.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/verification_gate_hardening.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/evidence_label_doctor_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/validator_dependency_and_rollout_plan.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/safety_human_intervention_protocol.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/self_evolution_protocol.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/product_appetite_and_non_goals.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/knowledge_promotion_protocol.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/transport_reliability_findings.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/transport_timeout_hardening_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/codex_visibility_drift_reliability_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/codex_visibility_recovery_experiment_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/enterprise_to_coagent_execution_mapping.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/operating_metrics_and_anti_drift_cadence.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/operating_metrics_snapshot_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/early_drift_detection_experiment_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/task_health_monitoring_and_intervention_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/minimal_multiconversation_proof_requirements.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/handoff_mode_and_workflow_graph_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/handoff_workflow_validator_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/problem_driven_external_adoption_queue.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/external_adoption_proposal_contract.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/external_adoption_store_checker_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/task_intake_to_proof_ladder_decision_table.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_packet_chain_blueprint.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_proof_package_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_minimal_package_contract.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_fixture_generation_plan.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_manual_rehearsal_plan.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_validator_execution_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_fixture_spec.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/goal_authority_and_decomposition_protocol.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/goal_creation_and_recovery_protocol.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/retrospective_and_improvement_closure_protocol.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/worktree_merge_recovery_experiment_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/end_to_end_task_operating_runbook.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/human_review_intervention_ux_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/validator_shared_envelope_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/goal_alignment_checker_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/runbook_readiness_checker_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/implementation_approval_gate_design.md`

Stress-test walkthroughs:

- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/stress_test_px4_parameter_identification.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/stress_test_ue_scene_truth_product.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_b_px4_parameter_proof_package.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_c_ue_scene_truth_proof_package.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_d_git_heavy_change_proof_package.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_e_auth_license_interruption_proof_package.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/stress_test_artifact_validator_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/proof_ladder_and_validator_order.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/common_proof_package_validator_design.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/goal_requirement_audit_map.md`
- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/goal_completion_gate_protocol.md`

Implementation backlog draft:

- `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/post_design_implementation_backlog.md`

Stress-test templates:

- `CoAgent/protocol/templates/px4_parameter_identifiability_matrix.yaml`
- `CoAgent/protocol/templates/ue_scene_truth_capability_card.yaml`
- `CoAgent/protocol/templates/scene_truth_artifact_manifest.yaml`

Department review packets:

- `Results/agent_packets/COAGENT-ARCH-LONGRUN-01-DISPATCH-01.yaml`
- `Results/agent_packets/COAGENT-ARCH-LONGRUN-01-CONTEXT-01.yaml`
- `Results/agent_packets/COAGENT-ARCH-LONGRUN-01-VERIFY-01.yaml`

Runtime/transport failure evidence:

- `Results/coagent_transport/runs/COAGENT-ARCH-LONGRUN-01-RUNTIME-01.summary.md`
- `Results/coagent_transport/runs/COAGENT-ARCH-LONGRUN-01-RUNTIME-01.stderr.log`

## What Counts As Real Progress

Real progress includes:

- problems converted into decisions, experiments, or explicit deferrals;
- stress-test workflows refined with concrete conversation topology;
- packet/mailbox/context/worktree rules made more precise;
- contradictions or unresolved questions made visible;
- cross-conversation transport failures recorded as architecture findings, not
  hidden retries;
- gated implementation backlog split into small reviewable tasks;
- checks run and failures recorded honestly;
- documentation updated so a future conversation can continue without hidden
  transcript memory.

## What Does Not Count

The following do not count as completion:

- only creating this task directory;
- only saying the work will take 10 hours;
- only listing departments;
- broad external summaries with no mapping to CoAgent problems;
- opening many conversations without result packets or context packs;
- implementing gated runtime features without approval;
- claiming Fab/UE/MWORKS capabilities without tool evidence.

## Expected Residual Questions

It is acceptable if these remain open after 10 hours, but they must have clear
next experiments or approval gates:

- exact context-size threshold for best model performance;
- reliable automated cross-conversation transport beyond current file/CLI path;
- automatic conversation creation;
- automatic worktree provisioning;
- email or desktop notification sender;
- app-server transport;
- durable department-internal worker pools.

## Known Findings Before Final Audit

These are current findings, not final failures:

1. Context handoff is conceptually designed but needs machine-checkable
   version/hash, context delta, acknowledgement, and pause/resume records.
2. Result packets must use a flat router-compatible format. Nested YAML and
   custom statuses caused real department result import failures.
3. Visible Codex conversation transport is real but not reliable enough for
   unattended default use. The RuntimePlatformAgent review exceeded the 60s
   result-packet budget and was recorded as blocked.
4. Verification detects the right failure modes but still needs validators,
   thresholds, template fixtures, and negative drift-packet tests.
5. PX4 and UE templates now exist as design drafts, but validators are still
   implementation backlog work.
6. Enterprise-management ideas are now mapped to concrete CoAgent objects, but
   the mapping still needs proof through a minimal multi-conversation closed
   loop.
7. Operating metrics and anti-drift cadence are now designed, but the metrics
   snapshot and negative drift fixtures remain implementation backlog work.
8. The recommended next proof is Candidate A, a low-tool-risk architecture
   packet chain across the smallest useful visible conversation set.
9. Handoff mode and workflow graph are now design objects, but runtime
   validation and graph execution remain gated future work.
10. External learning is now problem-driven through an adoption queue and an
    adoption proposal contract. The next learning work should choose one open
    problem and one minimal source slice, then produce an auditable accept,
    reject, defer, or probe decision rather than summarizing all reference
    projects again.
11. Candidate A is now specified as a concrete proof blueprint with task id
    `COAGENT-PROOF-CANDIDATE-A`, required conversations, handoff records,
    packet paths, context requirements, review states, trace metrics,
    pass/block criteria, and explicit non-goals. This still does not authorize
    executing the proof or gated automation.
12. Candidate A now also has a proof-package design: required inputs,
    required outputs, workflow graph shape, preflight checks, post-dispatch
    checks, negative fixtures, and result interpretation. Default next step is
    proof-package validation before live dispatch.
13. Candidate B now maps the PX4 log parameter-identification task into a
    proof-package design with log audit, identifiability matrix, estimator and
    simulation gates, blocker packets, evidence labels, uncertainty/residual
    requirements, and honest non-identifiable parameter handling.
14. Candidate C now maps the UE scene-truth/product-mainline task into a
    proof-package design with scene-source gate, UE/MCP capability card, truth
    artifact manifest, planning-readiness rules, Fab/manual blockers, manual
    review separation, and large-asset Git policy gates.
15. Candidate D now maps Git-heavy rename/import/large-asset work into a
    proof-package design with change inventory, worktree binding, integration
    plan, verification plan, destructive-action blockers, rollback, and a hard
    rejection of broad `git add -A` as a strategy.
16. Candidate E now maps login/license/GUI/manual-review interruption into a
    proof-package design with durable blocker packet, exact PMO user ask, safe
    parallel work, resume packet, retry/circuit breaker policy, and closeout.
17. A-E are now consolidated in `proof_ladder_and_validator_order.md`, which
    defines the default proof order, common proof package contract,
    shared preflight/post-dispatch checks, validator implementation order,
    deviation rules, and user audit questions.
18. `goal_authority_and_decomposition_protocol.md` now defines the hierarchy
    from user objective to canonical task goal, task-team goal, department
    goal, scoped conversation objective, subagent prompt objective, and
    implementation step goal. It explicitly rejects substituting setup work,
    visible conversations, elapsed time, or document volume for the real user
    outcome.
19. `goal_creation_and_recovery_protocol.md` now defines the operational
    preflight for creating or recreating active Codex goals, including wrong
    goal deletion/recreation, invalid setup-goal patterns, checkpoint fields,
    and future `GOAL_*` checker additions.
20. `early_drift_detection_experiment_design.md` now defines concrete positive
    and negative scenarios for proving a future metrics/checker layer catches
    wrong goals, missing evidence deltas, fake parallelism, stale context,
    missing blockers, timeout closeout gaps, unsupported tool claims, repeated
    review escapes, and completion overclaims before long-running work relies
    on it.
21. `common_proof_package_validator_design.md` now defines the shared
    read-only validator contract for all proof packages, including preflight
    error codes, post-dispatch error codes, candidate-specific extensions,
    JSON output, negative fixtures, and implementation boundary.
22. `goal_requirement_audit_map.md` now maps the full active goal to current
    evidence, strong evidence, weak/incomplete evidence, verification commands,
    and next work priority. It explicitly states the goal is not complete yet.
23. `candidate_a_fixture_spec.md` now makes the Candidate A validator path
    deterministic by defining a valid minimal fixture, negative fixtures,
    stable error codes, validator order, and implementation acceptance before
    live dispatch.
24. `task_intake_to_proof_ladder_decision_table.md` now maps incoming user
    tasks to proof path A-E, first gate, minimum team, secondary risks, and
    checkpoint questions so dynamic teams are task-driven rather than
    department-count-driven.
25. `ten_hour_audit_package.md` now provides the final review procedure:
    verdict table, required commands, primary evidence set, forbidden claims,
    user decision points, recommended next approval queue, and closeout
    checklist.
26. `context_index_and_assembly_design.md` now defines how new scoped
    conversations receive compact but sufficient context through index
    families, slice types, retrieval manifest, budget classes, stale/rejected
    filters, fit checks, and PX4/UE examples. This remains design-only until a
    retrieval-manifest checker exists.
27. `codex_visibility_drift_reliability_design.md` now treats recurring
    DispatchAgent visible-thread metadata drift as a pre-dispatch reliability
    risk with invariants, diagnose/repair/blocker flow, evidence records,
    state machine, and future gate. This remains design-only until the gate is
    implemented.
28. `codex_visibility_recovery_experiment_design.md` now defines the bounded
    recovery experiment for visible Codex state: clean registry, registered
    single/multi-department drift, unknown thread, missing rollout, Windows sync
    failure, repeated drift, provider-config request, and credential/cache
    safety scenarios. It explicitly limits the claim to registered metadata
    repair, not root-cause reliability.
29. `mailbox_ledger_and_replay_design.md` now defines the durable source of
    truth for cross-conversation messages: task-local message files, ack
    records, state transitions, replay, timeout/retry, contradiction
    handling, closeout, and recovery. This remains design-only until the
    mailbox checker exists.
27. `result_packet_validator_design.md` now defines the missing validator
    layer for department result packets: required fields, allowed values,
    structural and semantic rejections, stable finding codes, fixture matrix,
    repair policy, output JSON, and implementation boundary. This remains
    design-only until `COAGENT-IMPL-NEXT-11` is implemented.
28. `candidate_a_validator_execution_design.md` now defines how the future
    Candidate A validator should execute: CLI modes, required package layout,
    validation pipeline, dependency boundaries, JSON report, finding codes,
    fixture mode, live-proof gate, post-dispatch closeout gate, and forbidden
    implementation scope. This remains design-only until
    `COAGENT-IMPL-NEXT-15` is implemented.
29. `handoff_workflow_validator_design.md` now defines the validator contract
    for handoff and workflow graph objects: inputs, modes, required fields,
    cross-object checks, dispatch safety checks, post-dispatch checks, JSON
    report, stable finding codes, fixtures, Candidate A integration, and
    implementation boundary. This remains design-only until
    `COAGENT-IMPL-NEXT-13` is implemented.
30. `context_delta_checker_design.md` now defines the checker contract for
    context freshness: strict delta fields, acknowledgement records,
    pre-resume checks, post-result checks, derived state, JSON report, stable
    finding codes, fixture matrix, and integration with Candidate A, context
    index, mailbox, and workflow validators. This remains design-only until
    `COAGENT-IMPL-NEXT-02` is implemented.
31. `operating_metrics_snapshot_design.md` now defines the checker contract
    for long-running task health: read-only inputs, metric states, evidence
    classifications, drift rules, stable `OMS_*` finding codes, negative
    fixtures, JSON/Markdown output, and integration with packet, context,
    handoff, mailbox, visibility, and proof validators. This remains
    design-only until `COAGENT-IMPL-NEXT-09` is implemented.
32. `transport_timeout_hardening_design.md` now defines the hardening contract
    for Codex visible-conversation dispatch: attempt state machine, timeout
    classes, startup noise classification, closeout records, timeout blocker
    fields, late-result reconciliation, cleanup policy, dispatch-edge
    reconciliation, stable `TRN_*` finding codes, fixtures, and forbidden
    implementation scope. This remains design-only until
    `COAGENT-IMPL-NEXT-12` is implemented.
33. `external_adoption_store_checker_design.md` now defines the checker
    contract for problem-driven external learning: proposal store layout,
    checker modes, schema rules, lifecycle/store checks, evidence-level guard,
    source boundaries, accepted/rejected/probe decision rules, JSON output,
    stable `ADOPT_*` finding codes, fixtures, and promotion gate. This remains
    design-only until `COAGENT-IMPL-NEXT-10` is implemented.
34. `blocker_packet_validator_design.md` now defines the checker contract for
    durable blockers: common fields, allowed blocker types, timeout/invalid
    packet/auth/manual/destructive/tool requirements, duplicate ask prevention,
    unsafe retry rejection, `BLK_*` finding codes, fixtures, and no-execution
    boundary. This remains design-only until `COAGENT-IMPL-NEXT-05` is
    implemented.
35. `stress_test_artifact_validator_design.md` now defines the checker
    contract for PX4 and UE stress-test artifacts: identifiability matrix,
    capability card, truth manifest, evidence-label cross-checks, overclaim
    rejection, `PX4_*`, `UE_*`, and `STRESS_*` finding codes, fixtures, and
    no-tool boundary. This remains design-only until `COAGENT-IMPL-NEXT-06`
    is implemented.
36. `evidence_label_doctor_design.md` now defines the doctor contract for
    evidence provenance: allowed labels, label strength, required fields,
    design/offline/manual/runtime/Git/tool/external evidence separation,
    label-inflation rejection, `EVD_*` finding codes, fixtures, and read-only
    boundary. This remains design-only until `COAGENT-IMPL-NEXT-07` is
    implemented.
36. `validator_dependency_and_rollout_plan.md` now defines the validator gate
    graph: layers, dependency graph, rollout order, dependency failure policy,
    shared output envelope, Candidate A/product/operational minimum gate sets,
    and `needs_dependency` behavior. This remains design-only until validator
    implementations emit compatible reports.
37. `candidate_a_minimal_package_contract.md` now defines the exact minimal
    Candidate A proof/fixture package: directory layout, shared constants,
    task charter, context pack, workflow graph, handoffs, result packet
    placeholders, context delta, verification review, trace eval, closeout,
    and preflight/post-dispatch validity. This remains design-only until a
    fixture generator or validator implementation exists.
38. `candidate_a_fixture_generation_plan.md` now defines how a future fixture
    generator should build one valid Candidate A base package, derive negative
    fixtures by controlled mutation, write expectation files, enforce path
    safety, handle missing validator dependencies as `needs_dependency`, and
    stop for manual review when fixture generation would expand into private
    paths, live dispatch, product tools, or multiple primary failures.
39. `candidate_a_manual_rehearsal_plan.md` now defines the supervised fallback
    if the user wants to inspect Candidate A before validators exist:
    preconditions, approval record, manual dispatch sequence, stop rules,
    review checklist, result interpretation, evidence labels, and forbidden
    claims that prevent manual rehearsal from being presented as validated
    automation.
40. `goal_completion_gate_protocol.md` now defines the final closeout gate for
    this 10-hour design goal: allowed requirement verdicts, evidence strength
    rules, accepted gated follow-up fields, required final audit artifact,
    completion decision rules, and forbidden shortcuts such as using document
    volume, elapsed time, or visible conversations as completion proof.
41. `architecture_decision_record_summary.md` now consolidates the main
    architecture decisions into an ADR-style audit surface: accepted design
    baselines, accepted gates, deferred items, rejected approaches, rationale,
    alternatives, and source files.
42. `final_goal_completion_audit.md` now exists as a working draft. It maps
    each active goal requirement to a verdict, evidence, gated follow-up, and
    forbidden claim, but its current decision is
    `needs_final_refresh_before_completion_claim`.
43. `retrospective_and_improvement_closure_protocol.md` now defines how
    repeated failures, user corrections, review escapes, and incidents become
    owned improvement actions with evidence, closeout criteria, promotion,
    rejection, deferral, stale-action policy, and future `RETRO_*` checker
    codes. This remains design-only until `COAGENT-IMPL-NEXT-26` is approved.
44. `tool_capability_health_and_fallback_protocol.md` now defines how
    MWORKS, UE, Fab/manual import, Codex transport, Git, and external-reference
    routes become capability cards with health levels, evidence labels,
    stop/fallback decisions, blocker policy, stale-card criteria, and future
    `TOOL_*` checker codes. This closes P13 at the design level, but no live
    tool reliability, Fab automation, UE map mutation, MWORKS simulation
    execution, Codex dispatch, Git staging, or automatic repair is approved by
    it.
44a. `tool_capability_health_gate_checker_design.md` now turns P13/NEXT-27
    into a concrete read-only checker contract: required card discovery,
    route/health/evidence vocabulary, staleness rules, health-level claim
    ceilings, blocker/fallback validation, unsafe write-probe rejection,
    route-specific UE/Fab/MWORKS/Codex/Git/external-reference rules,
    dependency behavior, and `TOOL_*` positive/negative fixtures.
45. `implementation_sequence_and_release_plan.md` now closes P23 at the
    design level by turning the large post-design backlog into an R0-R8 phase
    ladder: review baseline, validator foundation, packet/blocker atoms,
    Candidate A preflight, supervised Candidate A proof, communication
    recovery, product-adjacent proofs, tool-backed product execution, and
    operating evolution. It defines entry evidence, exit evidence, skip rules,
    approval-packet fields, release milestones, and forbidden claims, but it
    does not approve implementation by itself.
46. `worktree_merge_recovery_experiment_design.md` now closes the missing
    Git/worktree recovery design gap at the scenario level. It defines
    workspace mode choice, same-file conflict handling, broad staging
    rejection, large-file policy, external path rejection, destructive-action
    blockers, Git lock/timeout closeout, role separation, rollback, cleanup,
    user-change reconciliation, third-party reformat risk, and main-thread Git
    blockage. This remains design-only and does not approve staging, commit,
    push, worktree creation, cleanup, destructive repair, or automatic DevOps
    dispatch.
47. `end_to_end_task_operating_runbook.md` now composes the architecture into
    one ordered task operating sequence. It specifies intake, canonical
    charter, proof-path classification, context assembly, workflow graph,
    topology selection, execution checkpoints, mailbox replay, evidence review,
    integration/hold, knowledge promotion, retrospective, and closeout. It is
    design-only and does not approve live dispatch, conversation creation,
    worktree creation, Git operation, MCP/tool calls, notification, scheduler,
    or automatic goal mutation.
47a. `real_task_execution_walkthroughs.md` now applies that operating sequence
    to concrete MoSim tasks: PX4/Sunray150 parameter identification and
    UE/Fab/local scene truth. It names canonical goals, invalid weakened goals,
    initial departments, task-scoped conversations, context pack contents,
    workflow graphs, mailbox/result packet boundaries, contradiction handling,
    PMO asks, Git disposition, evidence boundaries, and completion criteria.
    It is design-only and does not run product proofs.
47b. `task_health_monitoring_and_intervention_design.md` now defines how
    active long-running work turns health signals into action: continue,
    continue-with-watch, shrink topology, pause for context, pause for review,
    block for user, block for safety, close-ready, or reject completion. It
    adds critical-path ownership, topology intervention rules, one-action PMO
    blocker asks, PX4/UE health applications, and close-ready criteria.
48. `human_review_intervention_ux_design.md` now turns human intervention into
    a PMO-facing review UX. It defines one-action asks, allowed user decisions,
    severity, dedupe/rate-limit, redaction, blocker-specific resume mapping,
    required MWORKS license/login, UE/Fab manual import, visual review,
    destructive-action, invalid-packet, and transport-timeout cases, audit log,
    notification boundary, and future checker scope. It is design-only and
    does not approve email, desktop notification, GUI automation, credential
    handling, conversation creation, MCP/tool calls, or live dispatch.
49. `validator_shared_envelope_design.md` now defines the shared validator
    report contract for `COAGENT-IMPL-NEXT-00`: schema version, target,
    allowed modes, shared decisions, dependency report shape, finding shape,
    evidence path rules, side-effect declarations, claim boundaries, storage,
    fixture set, and integration rules. It is design-only and does not
    implement validators or approve live dispatch, tool/MCP calls, Git,
    worktrees, notifications, GUI automation, credential handling, external
    fetch, or runtime transport changes.
50. `goal_alignment_checker_design.md` now defines the L0 goal-alignment
    checker contract for `COAGENT-IMPL-NEXT-25`: user objective, canonical
    task goal, scoped objective alignment, result goal mutation, checkpoint
    evidence delta, completion overclaim, recreated-goal scope loss, recovery
    records, `GOAL_*` fixtures, and shared-envelope output. It is design-only
    and does not create, mutate, complete, or block Codex goals; dispatch
    conversations; call tools/MCP; create worktrees; stage Git; send
    notifications; edit Codex state; or rewrite task documents automatically.
51. `runbook_readiness_checker_design.md` now defines the end-to-end runbook
    readiness checker contract for `COAGENT-IMPL-NEXT-30`: readiness levels,
    intake, proof path, context, workflow, mailbox, packet, evidence, Git,
    knowledge, retrospective, closeout, dependency reports, `RUNBOOK_*`
    fixtures, and shared-envelope output. It is design-only and does not
    dispatch conversations; create conversations or worktrees; call MCP/tools;
    stage Git; send notifications; mutate goals; edit Codex state; inspect
    credentials/account caches; or rewrite task documents automatically.
52. `implementation_approval_gate_design.md` now defines the implementation
    approval gate contract for `COAGENT-IMPL-NEXT-31`: explicit approval,
    phase entry, scope boundary, forbidden actions, dependency reports, exit
    evidence, claim boundaries, `APPROVAL_*` fixtures, and shared-envelope
    output. It is design-only and does not approve or implement any slice,
    mutate runtime state, dispatch conversations, create worktrees, call
    MCP/tools, stage Git, send notifications, edit Codex state, inspect
    credentials/account caches, or rewrite task documents automatically.

## Minimum Next Approval Candidates

If the design direction is accepted, the smallest useful implementation slices
are:

1. `COAGENT-IMPL-NEXT-11`: result packet contract hardening and invalid-packet
   fixtures.
2. `COAGENT-IMPL-NEXT-02`: context delta template/checker with acknowledgement
   gate.
3. `COAGENT-IMPL-NEXT-12`: transport timeout and plugin-sync hardening.
4. `COAGENT-IMPL-NEXT-05`: blocker packet validator for resumable stops,
   duplicate user asks, and unsafe retry prevention.
5. `COAGENT-IMPL-NEXT-06`: validators for PX4 and UE stress-test templates.
6. `COAGENT-IMPL-NEXT-07`: evidence label doctor for design/offline/manual/
   GUI/MCP/Git/runtime/external provenance.
7. `COAGENT-IMPL-NEXT-09`: read-only operating metrics snapshot and negative
   drift detection.
8. New candidate: handoff mode and workflow graph validators.
9. New candidate: Candidate A minimal multi-conversation proof execution.
10. New candidate: structured external adoption proposal store/checker.
11. New candidate: Candidate A proof-package validator or fixture generator
   before running the live multi-conversation proof.
12. New candidate: proof ladder/common package validator that checks shared
    preflight and post-dispatch requirements across A-E.
13. New candidate: context index and assembly checker that rejects oversized,
    stale, source-less, or high-risk packs missing rejected assumptions.
14. New candidate: Codex visibility drift gate that repairs only registered
    department metadata or emits a blocker before dispatch.
15. New candidate: mailbox ledger and replay checker that validates message
    states, acknowledgements, expected responses, duplicate blocker dedupe
    keys, contradictions, and next safe action before replaying or dispatching
    cross-conversation work.
16. New candidate: Candidate A fixture generator that produces the positive
    and negative fixture set from one base package plus controlled mutations
    before the live proof spends transport budget.
17. New candidate: supervised Candidate A manual rehearsal only if the user
    explicitly accepts missing-validator risk and the output is labeled as
    manual rehearsal, not validated live proof.
18. New candidate: final goal completion audit using
    `goal_completion_gate_protocol.md` before any `update_goal complete`
    action.
19. New candidate: retrospective closure checker that rejects mandatory
    repeated-failure triggers without owner, evidence, action target, closeout,
    or justified rejection; `retrospective_closure_checker_design.md` now
    fixes the concrete record shape, trigger scan, dependencies, `RETRO_*`
    codes, fixtures, and read-only implementation boundary.
20. New candidate: tool capability health gate checker that rejects stale,
    weak, missing, or overclaimed tool-route evidence before product-adjacent
    PX4/UE/Fab/MWORKS/Codex/Git work depends on it;
    `tool_capability_health_gate_checker_design.md` now fixes the card
    discovery rules, route-specific claim ceilings, dependency behavior,
    `TOOL_*` fixtures, and read-only implementation boundary.
21. New candidate: worktree binding and Git-heavy recovery validators that
    cover `GIT_*` fixture scenarios before any large rename/import/binary
    batch or multi-worktree implementation; `worktree_git_recovery_validator_design.md`
    now fixes the shared read-only validator family for worktree binding,
    inventory, integration plans, blocker state, rollback, cleanup, role
    separation, evidence labels, decisions, and `GIT_*` fixtures.
22. New candidate: end-to-end runbook readiness checker that validates serious
    task packages before routing them into multiple conversations or proofs.
23. New candidate: human-review and intervention package checker that validates
    PMO review packets, dedupe, redaction, resume probes, safe parallel-work
    claims, allowed decisions, and notification readiness without sending
    notifications or automating external tools; `human_review_package_checker_design.md`
    now fixes blocker-specific resume mapping, manual evidence boundaries,
    `HREV_*` findings, fixtures, and the read-only implementation boundary.
24. First validator implementation candidate: `COAGENT-IMPL-NEXT-00`, the
    shared validator envelope, so all later checkers use one schema and cannot
    pass missing dependencies.
25. Next approval should cite the implementation phase from
    `implementation_sequence_and_release_plan.md`, normally R1 validator
    foundation or R2 packet/blocker atoms before Candidate A or product work.
26. New candidate: `COAGENT-IMPL-NEXT-25`, the goal alignment checker, if the
    next priority is preventing task charters, scoped packets, checkpoints, and
    completion audits from proving weakened setup/activity goals.
27. New candidate: `COAGENT-IMPL-NEXT-30`, the runbook readiness checker, if
    the next priority is proving serious task packages are ready before
    multi-conversation dispatch, proof validation, manual rehearsal,
    integration, or closeout.
28. New candidate: `COAGENT-IMPL-NEXT-31`, the implementation approval gate,
    if the next priority is preventing backlog entries, phase order, broad
    design acceptance, or vague continuation messages from authorizing
    implementation.

## Human Review Outcome Options

After review, choose one:

- `accept_design_direction`: continue to implementation backlog.
- `accept_with_rework`: keep direction but fix listed design gaps first.
- `reject_direction`: stop and redesign architecture assumptions.
- `approve_experiment`: run a bounded proof for one unresolved mechanism.
- `approve_implementation_slice`: implement one small gated backlog item.
