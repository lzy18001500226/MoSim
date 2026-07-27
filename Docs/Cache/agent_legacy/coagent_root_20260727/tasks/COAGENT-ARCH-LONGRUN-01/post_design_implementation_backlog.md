# COAGENT-ARCH-LONGRUN-01 Post-Design Implementation Backlog

Date: 2026-05-30
Status: draft for later approval

## Purpose

Break the architecture into small implementation slices. This document does not
approve implementation by itself.

## Gate Rule

Before implementation, the user or PMO must approve the specific backlog item.
Do not use this long-running design task to silently implement gated runtime
features.

## Candidate Implementation Slices

### COAGENT-IMPL-NEXT-00: Validator Dependency Envelope

Scope:

- implement the shared validator output envelope described in
  `validator_shared_envelope_design.md`;
- define shared constants for schema version, allowed modes, allowed
  decisions, dependency statuses, finding severities, target kinds, and
  side-effect names;
- make missing dependency behavior explicit as `needs_dependency` for
  design-only audit and `fail_before_dispatch` before live dispatch;
- add sample reports for result packet, blocker packet, evidence label,
  proof-package, and human-review validators;
- provide fixture checks for valid envelope, warning pass, missing dependency,
  stale dependency, unsupported decision synonym, inconsistent `ok`, unsafe
  evidence path, forbidden side effect, and claim-boundary overclaim;
- follow `validator_dependency_and_rollout_plan.md`;
- do not implement every domain validator in this slice.

Acceptance:

- sample validator reports use the common envelope and can be consumed by
  downstream examples;
- `ok=true` is accepted only for `pass`, `pass_with_warnings`, or
  `not_applicable`;
- missing required dependency in design audit reports `needs_dependency`;
- missing required dependency before live dispatch reports
  `fail_before_dispatch`;
- stale high-risk dependency reports `blocked`;
- unsupported decision synonyms such as `accepted_with_conditions`,
  `done_needs_review`, or `ok_but` fail;
- evidence paths outside the project without approved exception fail;
- read-only reports that declare forbidden side effects fail;
- schema validation cannot claim product behavior, live dispatch reliability,
  MCP/tool execution, Git correctness, notification delivery, or GUI state;
- no live dispatch, conversation creation, tool/MCP calls, GUI automation,
  credential handling, Git staging/commit/push, worktree creation,
  notification, external fetch, or runtime transport change is implemented.

### COAGENT-IMPL-NEXT-01: Mailbox Schema And Validator

Scope:

- define mailbox JSON/YAML schema;
- validate message type, owner, task id, response requirement;
- reject forbidden message types.

Acceptance:

- unit tests for valid and invalid mailbox messages;
- no app-server transport change.

### COAGENT-IMPL-NEXT-02: Context Delta Template And Checker

Scope:

- add context-delta template;
- require changed decision, affected conversations, superseded docs;
- add doctor check for stale context fields.
- require `context_pack_id`, `context_pack_version_or_hash`,
  `context_delta_id`, `supersedes`, `affected_slices`,
  `acknowledgement_required`, `acknowledgement_state`,
  `pause_until_refresh`, `reviewer`, and `resume_condition`.
- follow the checker contract in `context_delta_checker_design.md`.

Acceptance:

- context delta validates;
- sample delta updates one task context pack.
- stale context blocks high-risk resume until acknowledgement is recorded.
- missing ack, stale hash, missing resume condition, missing reviewer, stale
  result context, or promotion from stale context fails with stable `CTX_*`
  codes.

### COAGENT-IMPL-NEXT-03: Scoped Conversation Packet Generator

Scope:

- generate a scoped task packet from task charter and context pack;
- do not auto-create conversations;
- produce copy/paste or file packet for manual/transport dispatch.

Acceptance:

- one sample packet for PX4 or UE stress test;
- result path and stop condition included.

### COAGENT-IMPL-NEXT-04: Worktree Binding Record

Scope:

- add worktree binding schema;
- validate read/write scope and merge owner;
- no automatic worktree creation.
- follow the mode-selection and recovery scenario contract in
  `worktree_merge_recovery_experiment_design.md` and
  `worktree_git_recovery_validator_design.md`;
- validate workspace mode, owner roles, base ref, cleanup plan, shared
  workspace waiver, and same-file conflict policy.

Acceptance:

- sample worktree binding passes validation;
- conflict policy is explicit.
- small low-conflict docs work may pass as shared workspace with a recorded
  waiver;
- missing task/slice/review/integration worktree binding fails when the
  scenario requires isolation;
- same-file overlap without sequencing, section ownership, or integration
  owner fails with `GIT_SAME_FILE_OWNER_MISSING`;
- missing cleanup plan, missing merge owner, missing review owner, role
  collapse without waiver, or worktree identity used as task authority fails
  with stable `GIT_*` codes;
- no Git worktree is created and no file state is changed.

### COAGENT-IMPL-NEXT-05: Blocker Packet Templates

Scope:

- implement templates for `auth_required`, `gui_required`,
  `tool_unavailable`, `approval_required`, and `manual_review_required`.
- include `transport_timeout` and `invalid_result_packet` based on
  COAGENT-ARCH-LONGRUN-01 department review failures.
- follow the validator contract in
  `blocker_packet_validator_design.md`;
- validate common fields, allowed blocker types, type-specific evidence,
  duplicate active asks, unsafe retries, destructive-action precision, and
  secret-risk boundaries.

Acceptance:

- each template includes last safe state, user action, resume condition, and
  dedupe key.
- timeout blocker records stdout/stderr logs, expected result path, and process
  cleanup outcome.
- valid transport, invalid-packet, auth/license, manual-review, and
  destructive-action blockers pass with stable decisions;
- missing resume condition, missing last safe state, blind retry, duplicate
  user ask, external evidence path, secret risk, ambiguous destructive target,
  vague manual-review ask, timeout without cleanup, and invalid-packet blocker
  without finding codes fail with stable `BLK_*` codes.

### COAGENT-IMPL-NEXT-06: Stress-Test Artifact Templates

Scope:

- parameter identifiability matrix;
- method selection table;
- scene-source capability card;
- truth artifact manifest.

Acceptance:

- templates live under protocol/templates or task examples;
- docs reference them.
- current design drafts exist for:
  `px4_parameter_identifiability_matrix.yaml`,
  `ue_scene_truth_capability_card.yaml`, and
  `scene_truth_artifact_manifest.yaml`;
- implementation should add validators and fixtures, not only template files;
- follow the artifact validator contract in
  `stress_test_artifact_validator_design.md`;
- share evidence-label rules with
  `evidence_label_doctor_design.md`.

Acceptance additions:

- a valid matrix-only PX4 package can pass with explicit limitations;
- all-identifiable PX4 overclaim, estimated row without uncertainty, behavior
  match without residual, and offline result mislabeled as MWORKS evidence fail
  with stable `PX4_*` codes;
- a capability-only UE package can pass with planning readiness false;
- screenshot-as-truth, missing coordinate frame, unrecorded manual Fab import,
  and large asset without policy fail with stable `UE_*` codes;
- unsupported or inflated evidence labels fail with stable `STRESS_*` or
  `EVD_*` codes.

### COAGENT-IMPL-NEXT-07: Evidence Label Doctor Check

Scope:

- check evidence labels distinguish MWORKS_MCP, MWORKS_GUI, offline_script,
  manual_review, and design_only.
- follow the doctor contract in `evidence_label_doctor_design.md`;
- include labels for UE_MCP, UE_GUI, Fab_manual_import, git_metadata,
  runtime_metadata, and external_reference.

Acceptance:

- sample pass/fail fixtures;
- no simulation execution required.
- missing label, unsupported label, offline output labeled MWORKS_MCP,
  screenshot-as-truth, design-only implementation claim, runtime metadata used
  as product evidence, Git metadata used as test proof, unadopted external
  reference promoted as policy, and missing tool probe fail with stable
  `EVD_*` codes;
- the doctor is read-only and does not rewrite labels automatically.

### COAGENT-IMPL-NEXT-08: Department Dispatch Dry-Run Proof

Scope:

- dispatch one bounded packet to one active department conversation;
- import one result packet;
- update task board.
- record plugin sync/MCP startup overhead and timeout cleanup outcome.

Acceptance:

- no automatic conversation creation;
- timeout bounded to 60 seconds;
- result packet imported or blocker recorded.
- open dispatch edge is closed on timeout cleanup.

### COAGENT-IMPL-NEXT-25: Goal Alignment Checker

Scope:

- implement the read-only checker implied by
  `goal_alignment_checker_design.md`,
  `goal_authority_and_decomposition_protocol.md`, and
  `goal_creation_and_recovery_protocol.md`;
- compare user objective excerpts, task charter goal fields, scoped
  conversation objectives, result packet summaries, review brief entries, and
  final audit requirement rows;
- validate goal-creation preflight fields when a task has an active or
  recreated runtime goal;
- detect forbidden substitutions such as turning outcomes into setup steps,
  visible conversations, elapsed time, document volume, or implementation
  backlog items;
- produce stable `GOAL_*` finding codes;
- output the shared envelope from `validator_shared_envelope_design.md`;
- do not change goals automatically.

Acceptance:

- a valid task charter and scoped packet set passes with concrete
  `alignment_to_canonical_goal` fields;
- missing user objective fails with `GOAL_USER_OBJECTIVE_MISSING`;
- a canonical goal weaker than the user objective fails with
  `GOAL_CANONICAL_WEAKENED`;
- a local objective without concrete alignment fails with
  `GOAL_LOCAL_UNALIGNED`;
- a completion audit that passes a requirement from weak evidence fails with
  `GOAL_COMPLETION_OVERCLAIM`;
- a checkpoint that records activity without evidence delta fails with
  `GOAL_CHECKPOINT_NO_DELTA`;
- creating a task, opening a conversation, spending time, or writing documents
  cannot satisfy a user outcome without requirement-level evidence;
- a recreated goal that omits a required scope component fails with
  `GOAL_SCOPE_COMPONENT_LOST_ON_RECREATE`;
- a wrong goal replaced without a recovery record fails with
  `GOAL_RECOVERY_UNRECORDED`;
- no conversation creation, dispatch, tool/MCP call, worktree creation, Git
  staging, goal mutation, or task completion update is performed.

### COAGENT-IMPL-NEXT-30: Runbook Readiness Checker

Scope:

- implement the read-only checker implied by
  `runbook_readiness_checker_design.md` and
  `end_to_end_task_operating_runbook.md`;
- validate serious task packages for charter, proof path, first gate, context
  pack, retrieval manifest, workflow graph, handoff records, mailbox state,
  result/blocker/review packets, evidence labels, Git disposition, knowledge
  decision, retrospective requirements, and closeout readiness;
- consume shared-envelope dependency reports where they exist;
- report stable `RUNBOOK_*` finding codes;
- output the shared envelope from `validator_shared_envelope_design.md`.

Acceptance:

- valid Candidate A, PX4 matrix-only, UE capability-only, and Git
  inventory-only packages reach the correct readiness level without claiming
  product proof or automation;
- setup-only goals fail through dependency or `RUNBOOK_GOAL_NOT_ALIGNED`;
- missing first gate, unjustified all-department topology, raw transcript
  context, missing result path, open mailbox response at closeout, inflated
  evidence label, missing Git disposition, missing knowledge decision, and
  repeated incident without retrospective action fail with stable
  `RUNBOOK_*` codes;
- missing required dependency reports produce `needs_dependency` in design
  audit mode, `fail_before_dispatch` before live dispatch, and `blocked` when
  closeout could be wrong;
- no conversation creation, live dispatch, app-server transport, worktree
  creation, Git operation, MCP/tool call, notification, scheduler, goal
  mutation, Codex state edit, account-cache inspection, or automatic document
  rewriting is performed.

### COAGENT-IMPL-NEXT-31: Implementation Approval Gate

Scope:

- implement the read-only checker implied by
  `implementation_approval_gate_design.md`;
- validate implementation approval packets for backlog id, phase, explicit
  user/PMO approval, objective, non-goals, read/write scope, forbidden
  actions, entry evidence, dependency reports, expected exit evidence,
  rollback/stop rule, review owner, integration owner, and claim boundaries;
- reject backlog-as-authority, broad design approval as execution approval,
  vague "continue" approval, invalid phase jumps, broad scope, unapproved
  external paths, secret-risk routes, missing dependency evidence, weak exit
  evidence, missing claim boundaries, and tool/Git/MCP overreach;
- output the shared envelope from `validator_shared_envelope_design.md`;
- do not implement the approved slice.

Acceptance:

- a valid R1 shared-envelope implementation approval passes with narrow scope,
  fixture exit evidence, and explicit claim boundaries;
- a valid R2 packet-validator approval passes only when dependency evidence is
  present or reported as an accepted gap;
- manual Candidate A rehearsal approval passes with warnings only when
  missing-validator risk is explicitly accepted;
- backlog item without approval packet fails with
  `APPROVAL_PACKET_MISSING`;
- "continue" or broad design acceptance as implementation approval fails with
  `APPROVAL_EXPLICIT_TEXT_MISSING`;
- R4 without R1-R3 evidence or waiver fails with
  `APPROVAL_PHASE_DEPENDENCY_MISSING`;
- broad write scope, unapproved external path, secret-risk route, missing
  forbidden action, weak exit evidence, missing claim boundary, and Git/tool
  overreach fail with stable `APPROVAL_*` codes;
- no runtime mutation, conversation creation, live dispatch, app-server
  transport, worktree creation, Git operation, MCP/tool call, notification,
  scheduler, goal mutation, Codex state edit, account-cache inspection, or
  automatic document rewriting is performed.

### COAGENT-IMPL-NEXT-09: Operating Metrics Snapshot

Scope:

- compute task board metrics from runtime events;
- include blocked time, checkpoint count, open edges, stale tasks.
- implement the read-only subset of
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/operating_metrics_and_anti_drift_cadence.md`;
- follow the execution contract in
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/operating_metrics_snapshot_design.md`;
- include the early-drift positive and negative scenarios from
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/early_drift_detection_experiment_design.md`;
- report progress, coordination, quality, organization, safety, and reliability
  metrics where data exists;
- classify missing data as `needs_instrumentation` rather than inventing
  values.

Acceptance:

- read-only report;
- no dashboard implementation.
- at least one negative drift case is detected as `review_required`,
  `blocked`, or `rejected`.
- output links back to task board, result packets, blocker packets, and
  checkpoint events used as evidence.
- stable `OMS_*` finding codes are covered by fixtures for stale checkpoint,
  completion overclaim, missing context acknowledgement, timeout without
  blocker, WIP limit excess, unmapped research, unsupported claim, fake
  parallelism, and missing data.
- first fixture package covers at least `healthy_design_checkpoint`,
  `goal_setup_shell`, `goal_scope_loss_on_recreate`, `checkpoint_no_delta`,
  `fake_parallelism`, `stale_context_resume`, `blocked_without_packet`, and
  `completion_overclaim`;
- wrong-goal and completion-overclaim fixtures must fail before live
  long-running task orchestration can depend on the metrics snapshot.

### COAGENT-IMPL-NEXT-11: Result Packet Contract Hardening

Scope:

- add a router-compatible result packet template with only supported statuses
  and JSON-list fields;
- add validation feedback instructions for visible department conversations;
- document repair handling for nested YAML or unsupported status values.
- point department task packets to
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/result_packet_contract_hardening.md`.
- implement the read-only validator and fixture set designed in
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/result_packet_validator_design.md`.

Acceptance:

- a valid packet imports as `accepted` or `needs_review`;
- an invalid nested YAML packet is rejected with a clear schema finding;
- worker task packets point to the compatible template.
- unsupported statuses, missing evidence, missing next action, stale context,
  scope violation, blocker incompleteness, missing review owner, capability
  overclaim, raw transcript evidence, duplicate fields, and missing repair
  note fail with stable finding codes;
- no conversation creation, dispatch, router semantic expansion, notification,
  Git staging, or tool/MCP execution.

### COAGENT-IMPL-NEXT-12: Transport Timeout And Plugin-Sync Hardening

Scope:

- investigate whether Codex resume can disable remote plugin sync or use a
  lean local Codex home for department dispatch;
- define default timeout classes for quick review, long review, and
  implementation tasks;
- create timeout blocker and cleanup records when result file is missing.
- follow the execution contract in
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/transport_timeout_hardening_design.md`;
- reconcile late result packets without deleting original timeout evidence;
- record dispatch edge closeout and process cleanup state.

Acceptance:

- one controlled dispatch either imports a packet within budget or records a
  blocker without leaving a live process or open dispatch edge;
- no automatic conversation creation.
- fixtures cover missing result, late result, invalid result, live process,
  open edge, plugin/MCP startup overhead, retry without changed condition, and
  missing blocker with stable `TRN_*` finding codes.

### COAGENT-IMPL-NEXT-10: External Learning Adoption Queue

Scope:

- store adoption proposals with source/problem/risk/decision fields;
- no scheduled crawler.
- implement the structured form implied by
  `problem_driven_external_adoption_queue.md`;
- implement the proposal lifecycle and required fields defined in
  `external_adoption_proposal_contract.md`;
- follow the checker design in
  `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/external_adoption_store_checker_design.md`;
- preserve evidence levels: source_seen, mapped, designed, templated,
  validated, proved_in_loop, promoted.

Acceptance:

- one proposal from an existing local reference project;
- one rejected idea example.
- proposal must link to `architecture_problem_matrix.md` problem id.
- accepted proposals must name a promotion target and verification method;
- rejected proposals must name rejection reason and reopen trigger;
- no proposal may claim `validated`, `proved_in_loop`, or `promoted` without
  a matching artifact/check reference.
- fixtures cover valid accepted, valid rejected, missing problem, unbounded
  source slice, accepted without verification, rejected without reopen trigger,
  evidence inflation, direct runtime import, and code copy without
  license/security review with stable `ADOPT_*` finding codes.

### COAGENT-IMPL-NEXT-13: Handoff Mode And Workflow Graph Validators

Scope:

- validate `CoAgent/protocol/templates/handoff_mode.yaml`-compatible packets;
- validate `CoAgent/protocol/templates/workflow_graph.yaml`-compatible task
  graphs;
- follow the design contract in `handoff_workflow_validator_design.md`;
- check owner, context pack, result path, review gate, return path, and close
  condition before dispatch.

Acceptance:

- valid handoff and graph fixtures pass;
- missing canonical goal, result path, review owner, or return path fails;
- high-risk tool/human/merge nodes without capability, blocker, review,
  integration, or rollback gates fail with stable `HWFLOW_*` codes;
- Candidate A preflight can consume the validator result as a hard gate;
- no graph execution, app-server transport, or automatic conversation creation.

### COAGENT-IMPL-NEXT-14: Candidate A Minimal Multi-Conversation Proof

Scope:

- run the architecture packet-chain proof from
  `minimal_multiconversation_proof_requirements.md` and
  `candidate_a_packet_chain_blueprint.md`;
- if validators are still missing and the user explicitly chooses a supervised
  run, follow `candidate_a_manual_rehearsal_plan.md` and label the output
  `manual_rehearsal`;
- use the smallest useful visible set: MainAgent, DispatchAgent,
  ContextMemoryAgent, VerificationAgent, and KnowledgeSecretaryAgent;
- accept timeout or invalid packet only through blocker packets.

Acceptance:

- at least two non-MainAgent visible conversations return valid result packets
  without manual repair, or produce valid blocker packets;
- context delta and acknowledgement are recorded;
- review packet and trace evaluation exist;
- closeout names remaining gated implementation work.
- manual rehearsal output does not claim validator, fixture, unattended
  transport, product workflow, or automated dispatch proof.

### COAGENT-IMPL-NEXT-15: Candidate A Proof Package Validator

Scope:

- validate the proof package implied by
  `candidate_a_packet_chain_blueprint.md` and
  `candidate_a_proof_package_design.md` before live dispatch;
- consume the exact package shape and required fields in
  `candidate_a_minimal_package_contract.md`;
- use `candidate_a_fixture_spec.md` as the fixture source of truth;
- follow the execution contract in
  `candidate_a_validator_execution_design.md`;
- check task charter, handoff records, context-pack pointers, result paths,
  review owner, trace metrics, closeout requirement, and forbidden actions;
- generate fixtures for valid proof package, missing context pack, missing
  review packet, canonical-goal mutation, and forbidden tool action.

Acceptance:

- a complete Candidate A proof package passes validation without dispatching
  any conversation;
- missing packet path, stale context acknowledgement, unsupported status, or
  forbidden gated action fails with a clear finding;
- every fixture listed in `candidate_a_fixture_spec.md` fails or passes with
  the expected stable code and decision;
- validator outputs the required JSON report and honors `preflight`,
  `post_dispatch`, and `fixture` modes;
- missing dependency validators report `needs_dependency` rather than
  weakening the gate silently;
- no app-server transport, automatic conversation creation, automatic worktree
  creation, email, UE/MWORKS/Fab execution, or broad Git operation.

### COAGENT-IMPL-NEXT-24: Candidate A Fixture Generator

Scope:

- generate the fixture directories implied by
  `candidate_a_fixture_generation_plan.md`;
- create one valid Candidate A base fixture from shared constants;
- derive negative fixtures by controlled mutation from that valid base;
- write `fixture_expectation.yaml` for every fixture;
- keep generated fixture paths under
  `CoAgent/tests/fixtures/proof_packages/candidate_a/`;
- run only local self-checks and validators that already exist.

Acceptance:

- `valid_minimal`, `missing_context_pack`, `goal_mismatch`,
  `external_result_path`, `no_review_node`, `raw_transcript_context`,
  `forbidden_tool_node`, `invalid_flat_result_status`,
  `missing_context_delta`, and `timeout_without_blocker` are generated;
- each fixture expectation names mode, expected decision, expected codes,
  primary mutation, and forbidden side effects;
- generated contents match `candidate_a_minimal_package_contract.md` and
  `candidate_a_fixture_spec.md`;
- missing validator dependencies are reported as `needs_dependency`;
- fixtures contain no private paths, account caches, raw transcript,
  credentials, live Codex session ids, or external writes;
- no live dispatch, automatic conversation creation, app-server transport,
  worktree creation, Git stage/commit/push, MCP, UE, MWORKS, Fab, email, or
  desktop notification is invoked.

### COAGENT-IMPL-NEXT-28: End-To-End Runbook Readiness Checker

Scope:

- implement the read-only checker implied by
  `end_to_end_task_operating_runbook.md`;
- validate that a serious task package has intake, canonical task charter,
  proof-path decision, first gate, context pack, workflow graph, handoff
  records, mailbox expectations, result/review/blocker packet contracts,
  evidence-label policy, integration or hold policy, knowledge-promotion
  decision, retrospective trigger handling, and closeout condition;
- consume the shared validator envelope from `COAGENT-IMPL-NEXT-00`;
- do not execute the graph or dispatch conversations.

Acceptance:

- a complete design-only task package passes as `ready_for_review` or
  `ready_for_manual_dispatch` depending on evidence;
- missing canonical goal, weakened goal, missing proof path, missing context
  pack, missing review owner, missing return path, missing blocker policy,
  missing Git disposition for mutable work, or missing knowledge decision fails
  with stable finding codes;
- ordinary small tasks can pass with a documented simplified path;
- mixed PX4/UE/Git/auth tasks fail unless the highest-risk first gate is
  selected;
- output links to the authoritative files and classifies missing validators as
  `needs_dependency`;
- no conversation creation, live dispatch, app-server transport, worktree
  creation, Git operation, MCP/tool call, notification, scheduler, or goal
  mutation is performed.

### COAGENT-IMPL-NEXT-29: Human Review And Intervention Package Checker

Scope:

- implement the read-only checker implied by
  `human_review_intervention_ux_design.md` and
  `human_review_package_checker_design.md`;
- validate PMO-facing review packets for one specific action, blocker type,
  severity, owner, review owner, allowed decision values, last safe state,
  changed files, evidence paths, redaction summary, dedupe key, safe parallel
  work, resume condition, post-resume probe, verification after resume,
  forbidden actions while waiting, and closeout condition;
- cross-check blocker packets, Candidate E packages, manual rehearsal records,
  mailbox records, tool capability cards, evidence labels, and notification
  readiness fields where those files exist;
- report stable `HREV_*` finding codes;
- treat notification fields as readiness metadata only.

Acceptance:

- a valid MWORKS license/login review packet passes with exact user ask,
  last safe state, resume phrase, and smallest health probe;
- a valid UE/Fab manual import packet passes only when planning truth remains
  blocked until capability card and truth manifest are refreshed;
- a valid visual review packet passes only when manual acceptance is labeled
  `manual_review` and not inflated into planning truth or tool evidence;
- a destructive-action packet fails unless exact path/action/scope, rollback
  or preflight policy, and explicit approval requirement are present;
- duplicate active dedupe keys fail with `HREV_DUPLICATE_ACTIVE_ASK`;
- vague user asks, missing resume condition, unsupported decision value,
  missing redaction summary, unsafe secret/path content, unsafe retry after
  login/license blocker, safe-parallel work that promotes blocked claims, and
  notification-ready claims without opt-in/rate-limit/audit fields fail with
  stable `HREV_*` codes;
- output uses the shared validator envelope and reports missing dependencies
  as `needs_dependency`;
- no email, desktop notification, GUI automation, credential handling,
  conversation creation, live dispatch, runtime mutation, Git operation,
  MCP/tool call, UE/Fab import, MWORKS execution, or account-cache inspection
  is implemented.

### COAGENT-IMPL-NEXT-16: Candidate B PX4 Proof Package Validator

Scope:

- validate the package implied by
  `candidate_b_px4_parameter_proof_package.md`;
- check log inventory, identifiability matrix, uncertainty/residual fields,
  evidence labels, MWORKS health gate, blocker packets, and review output;
- provide fixtures for overclaiming identifiability, missing signals, missing
  uncertainty, offline output mislabeled as MWORKS evidence, and simulation
  tuning without tool health.

Acceptance:

- a matrix-only PX4 proof package can pass with explicit limitations;
- overclaiming all parameters as identifiable fails;
- offline evidence cannot be promoted as MWORKS evidence;
- missing log/spec/tool conditions produce blocker packets instead of hidden
  retries.

### COAGENT-IMPL-NEXT-17: Candidate C UE Scene Truth Proof Package Validator

Scope:

- validate the package implied by
  `candidate_c_ue_scene_truth_proof_package.md`;
- check scene-source inventory, UE/MCP capability card, truth-artifact
  manifest, coordinate frames, planning readiness, manual review, and Git/LFS
  policy;
- provide fixtures for rendering-as-truth, missing coordinate frame, manual
  Fab import not recorded, unsupported engine without fallback, and large
  asset without policy.

Acceptance:

- a capability-only package can pass with planning readiness explicitly false;
- planning readiness fails without collision/navmesh/occupancy/SDF/semantic or
  equivalent truth artifacts;
- Fab/UE/MCP blockers produce resumable blocker packets;
- visual review cannot substitute for planning truth.

### COAGENT-IMPL-NEXT-18: Candidate D Git Heavy Change Proof Package Validator

Scope:

- validate the package implied by
  `candidate_d_git_heavy_change_proof_package.md`;
- follow the recovery experiment and scenario matrix in
  `worktree_merge_recovery_experiment_design.md` and
  `worktree_git_recovery_validator_design.md`;
- check change inventory, path-family classification, worktree binding,
  integration plan, large-file/generated-output policy, destructive-action
  blockers, same-file conflict policy, and rollback plan;
- provide fixtures for broad `git add -A`, large binary without policy,
  external path staging, same-file overlap without integration owner, missing
  rollback, missing cleanup, Git lock/timeout without closeout, high-risk role
  collapse, user changes during active slice, third-party reformat risk, and
  main-thread Git blockage.

Acceptance:

- inventory-only Git proof can pass without staging or committing;
- broad unsafe staging fails;
- destructive or large-file actions become blocker packets;
- Git lock, slow Git, or timeout states produce blocker/recovery records
  rather than repeated commands;
- external paths and broad destructive moves fail before approval;
- integration readiness fails without review owner, merge owner, close owner,
  rollback, cleanup, and safe parallel-work decision;
- no actual stage, commit, push, delete, move, or worktree creation is
  performed by the validator.

### COAGENT-IMPL-NEXT-19: Candidate E Auth/License Interruption Validator

Scope:

- validate the package implied by
  `candidate_e_auth_license_interruption_proof_package.md`;
- check blocker packet, last safe state, exact PMO user ask, safe parallel
  work decision, resume packet, retry/circuit breaker, dedupe key, trace
  metrics, and closeout;
- provide fixtures for duplicate user asks, retry loop after suspected license
  blocker, missing resume condition, unsafe secret echo, and blocked tool claim
  presented as valid.

Acceptance:

- simulated blocker proof can pass with `design_only` or `dry_run` evidence;
- missing resume condition fails;
- unsafe retry and duplicate ask fail;
- no email/desktop notification, GUI/login automation, or credential handling
  is implemented.

### COAGENT-IMPL-NEXT-20: Common Proof Package Validator

Scope:

- implement the shared preflight and post-dispatch checks described in
  `proof_ladder_and_validator_order.md` and
  `common_proof_package_validator_design.md`;
- validate proof package root, task charter, context pack, workflow graph,
  handoff records, result paths, review owner, trace evaluation, closeout,
  forbidden actions, blocker classes, and evidence-label rules;
- provide a generic fixture harness that Candidate A-E validators can reuse.

Acceptance:

- common valid package passes;
- missing canonical goal, missing context pack, missing review node, missing
  result path, external output path, forbidden action omission, raw transcript
  context, and missing closeout fail;
- no live dispatch, tool/MCP execution, automatic conversation creation,
  automatic worktree creation, email, Git staging, commit, or push.

### COAGENT-IMPL-NEXT-21: Context Index And Assembly Checker

Scope:

- implement the read-only checker implied by
  `context_index_and_assembly_design.md`;
- define a retrieval manifest schema for assembled context packs;
- validate context pack source paths, slice reasons, excluded stale material,
  budget class, review owner, result path, and close condition;
- add PX4 and UE high-risk fixtures that require rejected assumptions to be
  included explicitly;
- do not implement vector search, automatic context generation, automatic
  conversation creation, or runtime dispatch.

Acceptance:

- a compact valid context pack with retrieval manifest passes;
- an oversized pack fails with a split recommendation;
- stale context without acknowledgement fails;
- a high-risk PX4 pack fails if it omits the rejected assumption that one log
  can identify all simulator parameters;
- a high-risk UE pack fails if it omits the rejected assumption that rendering
  proves planning truth;
- context output must not include private Codex SQLite/JSONL, credentials,
  account cache, or raw full transcript content.

### COAGENT-IMPL-NEXT-22: Codex Visibility Drift Gate

Scope:

- implement the pre-dispatch gate implied by
  `codex_visibility_drift_reliability_design.md`;
- implement the experiment evidence shape and scenario coverage implied by
  `codex_visibility_recovery_experiment_design.md`;
- run `check_department_visibility.py` before visible department dispatch;
- run bounded diagnosis for the affected registered department on failure;
- optionally repair registered department metadata through the existing
  `sync-visible --apply` path when the failure matches approved drift policy;
- write before/after evidence records under `Results/coagent_transport/`;
- emit `codex_visibility_drift` blocker packets when repair is unsafe,
  unsupported, or still failing;
- do not create conversations, delete sessions, change global Codex provider
  config, touch credentials, or dispatch after a failed gate.

Acceptance:

- clean registry passes without repair;
- simulated DispatchAgent alternate-DB drift is detected;
- simulated multi-department registered drift is repaired only when every
  department matches the approved pattern;
- approved repair restores visibility and records evidence;
- unknown thread id produces blocker, not repair;
- missing rollout, Windows sync failure, provider-config requirement, and
  credential/account-cache risk produce blockers instead of repair;
- repeated drift for the same department requires a retrospective action;
- failed repair blocks dispatch;
- no unrelated Codex history, credentials, provider config, or project files are
  modified.

### COAGENT-IMPL-NEXT-23: Mailbox Ledger And Replay Checker

Scope:

- implement the read-only checker implied by
  `mailbox_ledger_and_replay_design.md`;
- define message, ack, and replay schemas for project-owned mailbox files;
- validate message ids, allowed message types, sender/receiver, task id,
  context hash, payload path, evidence paths, review owner, close condition,
  and status transitions;
- detect missing acknowledgement records, missing expected responses,
  duplicate blocker dedupe keys, forbidden message types, unsupported state
  jumps, and closed tasks with open expected responses;
- generate a replay summary for one task from mailbox files plus runtime state.

Acceptance:

- a valid Candidate A mailbox chain replays to one next safe action;
- missing ack fails when `requires_ack=true`;
- contradictory result messages create review-required state;
- duplicate blocker dedupe keys do not create repeated user asks;
- closed task with open expected response fails;
- no app-server transport, automatic conversation creation, automatic message
  delivery, email, Git staging, or tool/MCP execution is implemented.

### COAGENT-IMPL-NEXT-26: Retrospective Closure Checker

Scope:

- implement the read-only checker implied by
  `retrospective_and_improvement_closure_protocol.md` and
  `retrospective_closure_checker_design.md`;
- validate retrospective records for mandatory triggers, owners, review owners,
  evidence paths, problem ids, action targets, close conditions, promotion or
  rejection decisions, stale-action state, duplicate records, and unsafe action
  proposals;
- cross-check records against the problem matrix, implementation backlog,
  knowledge promotion protocol, external adoption proposal contract, operating
  metrics snapshot, blocker packets, and proof closeout where those files
  exist;
- report stable `RETRO_*` finding codes;
- do not create issues, edit skills, send notifications, create conversations,
  dispatch work, mutate runtime task state, stage Git, or call MCP/tools.

Acceptance:

- a valid retrospective record with evidence, owner, review owner, action
  target, and close condition passes;
- a mandatory repeated-failure trigger without a record fails with
  `RETRO_RECORD_MISSING`;
- missing owner, missing evidence, untestable close condition, unlinked
  promotion, unjustified rejection, stale open action, unsafe automation
  proposal, duplicate unresolved record, and closeout without evidence fail
  with stable `RETRO_*` codes;
- records that defer automation include trigger, owner, and revisit condition;
- checker output uses the shared validator envelope and reports missing
  dependencies as `needs_dependency`;
- all reads remain inside project scope except explicitly approved
  infrastructure evidence references; no secrets, raw full transcript, Codex
  database dumps, account cache, or credentials are emitted.

### COAGENT-IMPL-NEXT-27: Tool Capability Health Gate Checker

Scope:

- implement the read-only checker implied by
  `tool_capability_health_and_fallback_protocol.md`;
- validate tool capability cards for route family, route name, owner,
  required downstream claim, health level, evidence label, evidence paths,
  probe timestamp, timeout, allowed/forbidden operations, fallback routes,
  blocker policy, review owner, and stale-card criteria;
- cross-check capability cards against evidence label doctor, blocker packet
  validator, stress-test artifact validators, Candidate B/C/D/E package
  validators, and proof-package closeout where those reports exist;
- report stable `TOOL_*` finding codes;
- do not open UE/MWORKS/Fab, inspect account caches, repair MCP servers,
  create conversations, dispatch work, run simulations, mutate maps, download
  assets, stage Git, send notifications, or rewrite capability cards.

Acceptance:

- a valid MWORKS execution-safe card with evidence path and allowed
  simulation-smoke claim passes;
- a valid UE read-only card with planning readiness explicitly false passes;
- a valid Fab manual-import card with user/manual record and downgraded claim
  passes;
- missing card for a tool-dependent proof fails with `TOOL_CARD_MISSING`;
- stale card, unsupported route, missing evidence, evidence-label mismatch,
  screenshot-as-truth, Fab visibility overclaim, offline-as-MWORKS overclaim,
  unsafe write probe, UI-state-overclaim, missing blocker/resume policy, and
  undeclared fallback fail with stable `TOOL_*` codes;
- checker output uses the shared validator envelope and reports missing
  dependencies as `needs_dependency`;
- all reads remain inside project scope except explicitly approved
  infrastructure evidence references; no secrets, account cache bodies, raw
  full transcript, private Codex database dumps, or credentials are emitted.

## Deferred Until Separate Approval

- app-server transport;
- automatic conversation creation;
- automatic worktree creation;
- email/desktop notification sender;
- unattended scheduled execution;
- new permanent departments;
- broad MCP/tool expansion.
- automatic tool capability repair, Fab download/import automation, UE map
  mutation, MWORKS simulation execution, or Codex transport dispatch beyond
  separately approved proof tasks.
