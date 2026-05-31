# COAGENT-ARCH-LONGRUN-01 Architecture Decision Record Summary

Date: 2026-05-30
Status: active decision summary

## Purpose

The task now has many detailed design files. This summary records the main
architecture decisions in one place so the 10-hour audit can review decisions
and tradeoffs without reading every artifact linearly.

This file summarizes decisions. The detailed contracts remain in the referenced
source files.

## Decision Vocabulary

| Status | Meaning |
|---|---|
| `accepted_design` | current design baseline unless user rejects it |
| `accepted_with_gate` | accepted design, but implementation/live use needs a named gate |
| `deferred` | useful but outside current approved scope |
| `rejected` | explicitly not used |
| `needs_user_choice` | requires user decision before execution |

## ADR-001: Task-First Operating Model

Decision: `accepted_design`

Use one canonical task goal as the top-level organizing unit. Departments and
conversations are capability surfaces that serve the task, not static owners of
work.

Rationale:

- prevents a fixed org chart from driving task shape;
- gives every conversation a parent goal and close condition;
- lets one task dynamically use one conversation, many conversations, or
  short-lived subagents based on risk and context load.

Rejected alternative:

- route every task through all permanent departments.

Source:

- `task_charter.md`
- `dynamic_team_decision_rules.md`
- `task_intake_to_proof_ladder_decision_table.md`

## ADR-002: Eleven Permanent Conversations, Conditional Capability Expansion

Decision: `accepted_design`

Keep 11 active visible permanent conversations as governance/review surfaces:
Main, Dispatch, Product Strategy, Runtime Platform, Context Memory, Toolchain
MCP, Knowledge Secretary, Verification, Safety Compliance, DevOps Release, and
External Intelligence.

Do not add more permanent departments by default. Additional capabilities stay
hosted or conditional until a task proves they need permanent visibility.

Rationale:

- the user can currently see and audit these conversations;
- more permanent conversations increase coordination failure risk;
- task-scoped conversations remain available for high-context temporary work.

Rejected alternative:

- create a permanent conversation for every capability in the enterprise model.

Source:

- `shared_task_board.md`
- `department_dispatch_plan.md`
- `product_appetite_and_non_goals.md`
- `CoAgent/docs/architecture/coagent_conversation_mapping.md`

## ADR-003: Codex App Is Review Surface, Project Files Are Source Of Truth

Decision: `accepted_design`

Codex App and VSCode can show conversation state, but durable coordination must
live in project-owned files: task charter, board, mailbox, packets, context
packs, runtime state, blockers, reviews, and closeout records.

Rationale:

- App/VSCode sync behavior can differ by local/WSL config;
- Codex visibility metadata has already drifted;
- future conversations must recover from files, not hidden UI state.

Rejected alternative:

- treat visible chat history as the durable task ledger.

Source:

- `mailbox_ledger_and_replay_design.md`
- `codex_visibility_drift_reliability_design.md`
- `communication_context_protocol.md`

## ADR-004: Subagents Are Bounded Calls, Not Durable Departments

Decision: `accepted_design`

Use short-lived subagents only for bounded research, review, or execution
slices whose output can be consumed by a parent conversation. Long-running Git,
review, test, secretary, safety, and coordination work should use durable task
state and visible conversations.

Rationale:

- subagents cannot reliably communicate with each other over time;
- they are useful for one-shot bounded analysis;
- durable roles need recoverable context, packets, and review gates.

Rejected alternative:

- use subagents as standing departments for Git, testing, review, or secretary
  duties.

Source:

- `dynamic_team_decision_rules.md`
- `enterprise_to_coagent_execution_mapping.md`

## ADR-005: Candidate A Before Product Automation

Decision: `accepted_with_gate`

Run Candidate A, the architecture packet-chain proof, before PX4, UE, Git-heavy
or auth/license product-adjacent proofs unless a higher-priority blocker forces
a deviation.

Rationale:

- Candidate A tests communication, context, review, result packets, blockers,
  trace evaluation, and closeout with low product/tool risk;
- product work should not depend on unstable packet or transport mechanics.

Deviation allowed when:

- Git-heavy work is imminent;
- auth/license blocks all progress;
- UE scene truth or PX4 data sufficiency becomes the immediate product
  bottleneck and user accepts the risk.

Source:

- `minimal_multiconversation_proof_requirements.md`
- `candidate_a_packet_chain_blueprint.md`
- `proof_ladder_and_validator_order.md`

## ADR-006: Validate Packages Before Live Dispatch By Default

Decision: `accepted_with_gate`

Prefer fixture generation and read-only validators before live Candidate A
dispatch. Manual rehearsal is allowed only with explicit user approval and must
be labeled as manual rehearsal.

Rationale:

- earlier live dispatch exposed invalid packet and timeout problems;
- preflight errors should be caught cheaply;
- live proof should test coordination, not improvised package repair.

Rejected alternative:

- keep running live dispatch attempts without fixture or validator discipline.

Source:

- `candidate_a_proof_package_design.md`
- `candidate_a_minimal_package_contract.md`
- `candidate_a_fixture_generation_plan.md`
- `candidate_a_manual_rehearsal_plan.md`
- `candidate_a_validator_execution_design.md`

## ADR-007: Dependency-Aware Validators

Decision: `accepted_design`

Validators must report `needs_dependency` when upstream checks are missing
instead of silently weakening gates. Validator results should use a shared
output envelope.

Rationale:

- prevents later validators from passing by ignoring missing evidence labels,
  result packet checks, blockers, context, mailbox, or workflow validation;
- makes proof-package readiness auditable.

Source:

- `validator_dependency_and_rollout_plan.md`
- `common_proof_package_validator_design.md`

## ADR-008: Evidence Labels Are Mandatory For Product-Adjacent Claims

Decision: `accepted_design`

Distinguish `design_only`, offline demos, manual review, GUI evidence, MCP
evidence, Git/runtime metadata, and external references. Design/offline/runtime
metadata cannot be promoted into product correctness proof.

Rationale:

- PX4 and UE tasks can easily overclaim from weak evidence;
- screenshots do not prove planning truth;
- Git/runtime metadata does not prove product behavior.

Source:

- `evidence_label_doctor_design.md`
- `stress_test_artifact_validator_design.md`
- `candidate_b_px4_parameter_proof_package.md`
- `candidate_c_ue_scene_truth_proof_package.md`

## ADR-009: Human Intervention Is A Blocker/Resume Protocol

Decision: `accepted_design`

Auth, license, GUI, manual review, destructive action, and tool-unavailable
cases must produce durable blocker packets with last safe state, exact user
action, resume condition, retry policy, and dedupe key.

Rationale:

- prevents repeated vague user asks;
- prevents unsafe automatic retries;
- lets work continue safely on independent slices.

Source:

- `safety_human_intervention_protocol.md`
- `blocker_packet_templates.md`
- `blocker_packet_validator_design.md`
- `candidate_e_auth_license_interruption_proof_package.md`

## ADR-010: Git Work Must Be Inventory-First

Decision: `accepted_design`

Large renames, imports, generated outputs, large assets, or broad Git state
must start with change inventory and path-family classification before staging,
committing, deleting, moving, or creating worktrees.

Rationale:

- prevents `git add -A` over large uncontrolled imports;
- lets DevOps own integration without blocking the main thread;
- supports rollback and review gates.

Source:

- `worktree_git_integration_protocol.md`
- `candidate_d_git_heavy_change_proof_package.md`
- `worktree_merge_recovery_experiment_design.md`
- `worktree_git_recovery_validator_design.md`

## ADR-019: Git Recovery Is A Designed State Machine, Not Main-Thread Trial And Error

Decision: `accepted_design`

Git-heavy tasks must be recoverable through explicit states: inventory,
workspace mode selection, integration plan, review, merge disposition, blocker
or rollback, and closeout. Slow Git, lock residue, same-file conflicts,
external paths, large binaries, broad staging proposals, and user changes
during active slices are not reasons for the main conversation to keep trying
commands. They become DevOps-owned recovery or blocker states.

Rationale:

- large Git work can consume the main thread and hide task drift;
- broad staging and broad cleanup can corrupt unrelated work;
- worktree identity must not become task authority;
- human review should receive one concrete decision, not a vague Git problem;
- later validators need deterministic negative scenarios, not only policy
  prose.

Rejected alternative:

- let the main agent keep running Git until status is understandable, then
  decide staging/commit scope from memory.

Source:

- `worktree_merge_recovery_experiment_design.md`
- `candidate_d_git_heavy_change_proof_package.md`
- `worktree_git_integration_protocol.md`
- `worktree_git_recovery_validator_design.md`

## ADR-020: Serious Tasks Follow One End-To-End Runbook

Decision: `accepted_design`

Use `end_to_end_task_operating_runbook.md` as the composition layer for serious
tasks. Individual protocols are necessary but insufficient unless they are
ordered into intake, canonical charter, proof-path classification, context
assembly, workflow graph, topology selection, execution checkpoints, mailbox
replay, evidence review, integration or hold, knowledge promotion,
retrospective, and closeout.

Rationale:

- prevents a future conversation from selecting one protocol and ignoring the
  rest;
- keeps task routing outcome-driven instead of department-driven;
- makes proof-path first gates explicit before conversations are spawned;
- gives users and reviewers one place to audit why a task stopped, split,
  delegated, merged, or stayed blocked;
- sets up a later read-only runbook readiness checker.

Rejected alternative:

- rely on the agent to remember how to combine task charter, proof ladder,
  context, mailbox, blockers, Git, review, and knowledge-promotion rules at
  runtime.

Source:

- `end_to_end_task_operating_runbook.md`
- `task_flow_design.md`
- `task_intake_to_proof_ladder_decision_table.md`
- `handoff_mode_and_workflow_graph_design.md`
- `goal_completion_gate_protocol.md`

## ADR-011: External Learning Is Problem-Driven

Decision: `accepted_design`

External articles, vendor docs, and open-source projects enter CoAgent through
problem-linked adoption proposals, not broad summaries. Each proposal must
record source, problem id, evidence level, adoption decision, promotion target,
and validation plan.

Rationale:

- avoids source-study drift;
- makes lessons portable and rejectable;
- keeps context packs compact.

Source:

- `problem_driven_external_adoption_queue.md`
- `external_adoption_proposal_contract.md`
- `external_adoption_store_checker_design.md`
- `self_evolution_protocol.md`

## ADR-012: Goal Completion Requires Requirement Verdicts

Decision: `accepted_design`

Do not mark `COAGENT-ARCH-LONGRUN-01` complete until
`goal_completion_gate_protocol.md` is applied and
`final_goal_completion_audit.md` exists. Completion must be a design-goal
completion claim, not a runtime or implementation completion claim.

Rationale:

- prevents document volume or elapsed time from being treated as success;
- separates design readiness from live proof and implementation readiness;
- gives the user a concrete audit artifact.

Source:

- `goal_requirement_audit_map.md`
- `ten_hour_audit_package.md`
- `goal_completion_gate_protocol.md`

## ADR-013: Goal Authority Is Layered And Non-Substitutable

Decision: `accepted_design`

The user's objective is the top-level authority. The canonical task goal,
task-team goal, department goal, scoped conversation objective, subagent prompt
objective, and implementation step goal are decomposition layers. They may make
work executable, but they may not weaken, rename, or replace the user outcome.

Rationale:

- prevents setup actions from becoming fake success;
- makes multi-conversation delegation auditable;
- catches the failure mode where "do 10 hours of design work" becomes "create
  a 10-hour task";
- gives future validators a concrete target for semantic drift checks.

Source:

- `goal_authority_and_decomposition_protocol.md`
- `goal_creation_and_recovery_protocol.md`

## ADR-014: Retrospectives Must Close As Actions Or Rejections

Decision: `accepted_design`

Repeated failures, user corrections, review escapes, and incidents must become
retrospective records with owners, evidence, action targets, close conditions,
and promotion, rejection, or deferral decisions. A note in chat, status, or
review text is not sufficient learning.

Rationale:

- prevents recurring failures from depending on agent memory;
- turns local incidents into durable skills, hooks, doctor checks, workflow
  updates, backlog items, or rejected-idea records;
- gives the final audit a way to distinguish "problem noticed" from "problem
  closed or intentionally deferred";
- keeps self-evolution problem-driven instead of broad source study.

Source:

- `retrospective_and_improvement_closure_protocol.md`
- `retrospective_closure_checker_design.md`
- `knowledge_promotion_protocol.md`
- `operating_metrics_and_anti_drift_cadence.md`

## ADR-015: Tool Capability Is A Gated Evidence Object

Decision: `accepted_design`

MWORKS, UE, Fab, Codex transport, Git, and external-reference routes must be
represented by capability cards with health levels, evidence labels,
stop/fallback rules, blocker policies, and stale-card criteria before a task
depends on them for product, runtime, or coordination claims.

Rationale:

- prevents stale tool memory from becoming product evidence;
- separates discoverability, read-only access, safe write probes, bounded
  execution, and product evidence readiness;
- turns Fab/UE/MWORKS failures into blocker or downgrade decisions instead of
  open-ended retries;
- makes visual rendering, inventory visibility, runtime metadata, and Git
  metadata insufficient for stronger product claims unless the relevant proof
  artifacts exist.

Rejected alternative:

- assume tool routes are usable because they were installed, visible in a
  launcher/library, or previously worked in another task.

Source:

- `tool_capability_health_and_fallback_protocol.md`
- `evidence_label_doctor_design.md`
- `blocker_packet_validator_design.md`
- `candidate_b_px4_parameter_proof_package.md`
- `candidate_c_ue_scene_truth_proof_package.md`

## ADR-016: Implementation Uses A Phase Ladder

Decision: `accepted_design`

Post-design implementation should proceed through an explicit R0-R8 phase
ladder: review baseline, validator foundation, packet/blocker atoms,
Candidate A preflight, supervised Candidate A proof, communication recovery,
product-adjacent proofs, tool-backed product execution, and operating
evolution.

Rationale:

- prevents the backlog from becoming an unordered feature menu;
- keeps primitives before orchestration and orchestration before product
  automation;
- makes skip decisions reviewable instead of implicit;
- gives each release milestone a narrow claim that cannot imply later
  milestones.

Rejected alternative:

- approve whichever backlog item looks useful next without checking dependency,
  phase, entry evidence, exit evidence, skip rules, or forbidden claims.

Source:

- `implementation_sequence_and_release_plan.md`
- `post_design_implementation_backlog.md`
- `proof_ladder_and_validator_order.md`
- `validator_dependency_and_rollout_plan.md`

## ADR-017: Early Drift Detection Requires Negative Scenarios

Decision: `accepted_design`

Operating metrics are not sufficient if they only produce a health report.
Before long-running orchestration can rely on them, the checker must prove it
catches negative scenarios: setup-only goals, scope loss during goal recovery,
checkpoints with no evidence delta, fake parallelism, stale-context resume,
blocked work without blocker packet, timeout without closeout, unsupported
tool claims, repeated review escapes, and completion overclaims.

Rationale:

- the most expensive failures look productive until late human review;
- wrong goals must be rejected before other metrics are interpreted;
- a checker that passes every active task is worse than no checker;
- negative fixtures make future implementation deterministic instead of
  prose-driven.

Rejected alternative:

- implement only a dashboard-style activity snapshot without drift fixtures.

Source:

- `early_drift_detection_experiment_design.md`
- `operating_metrics_snapshot_design.md`
- `goal_creation_and_recovery_protocol.md`
- `verification_gate_hardening.md`

## ADR-018: Visible Codex Recovery Is Bounded And Evidence-Backed

Decision: `accepted_design`

CoAgent may rely on visible Codex department conversations only after a
pre-dispatch visibility gate proves registered thread metadata is healthy or
after a bounded repair succeeds for registered department threads. Recovery
must write before/after evidence and must block on unknown threads, missing
rollouts without source, provider-config edits, credentials/account-cache
access, or failed Windows/WSL synchronization.

Rationale:

- visible conversation metadata has drifted repeatedly after prior successful
  checks;
- a repaired state is useful for bounded dispatch but does not prove root-cause
  reliability;
- repair is acceptable only for registered department sessions, not arbitrary
  Codex state;
- repeated drift must become an incident/retrospective signal, not hidden
  maintenance work.

Rejected alternative:

- treat `sync-visible --apply` success as proof that visible transport is now
  reliable.

Source:

- `codex_visibility_drift_reliability_design.md`
- `codex_visibility_recovery_experiment_design.md`
- `codex_visible_thread_sop.md`

## ADR-019: Git And Worktree Recovery Needs Fixtures Before Real Actions

Decision: `accepted_design`

Git-heavy work is not safe as a main-thread trial-and-error loop. Before
large imports, renames, multi-worktree implementation, large-asset handling,
or recovery operations are approved, CoAgent needs fixture-backed checks for
workspace mode choice, same-file conflict handling, broad staging rejection,
large-file policy, external path rejection, destructive-action blockers, Git
locks/timeouts, rollback, cleanup, role separation, and user-change
reconciliation.

Rationale:

- broad Git state can destroy reviewability faster than ordinary code bugs;
- conversation/worktree mapping must be explicit before multi-agent
  implementation;
- the main thread should not block on slow or locked Git operations when a
  DevOps-owned proof package can inventory and gate the work;
- large assets and generated outputs need policy before staging.

Rejected alternative:

- let the main agent handle large Git changes with ad-hoc `git status`, broad
  staging, and repeated retries.

Source:

- `worktree_merge_recovery_experiment_design.md`
- `candidate_d_git_heavy_change_proof_package.md`
- `worktree_git_integration_protocol.md`
- `worktree_git_recovery_validator_design.md`

## ADR-020: Serious Tasks Follow One End-To-End Runbook

Decision: `accepted_design`

Serious user tasks should follow one composed operating sequence: intake,
canonical charter, proof-path classification, context assembly, workflow
graph, topology selection, execution checkpoints, mailbox replay, evidence
review, integration or hold, knowledge promotion, retrospective, and closeout.

Rationale:

- selecting protocols ad hoc recreates the same drift the architecture is
  meant to prevent;
- dynamic teams need one shared closeout contract even when boundaries shift;
- review, Git, blockers, context, and knowledge promotion must be sequenced
  before a task can be called done.

Rejected alternative:

- choose conversations, validators, proof packages, and reviews case by case
  without a runbook.

Source:

- `end_to_end_task_operating_runbook.md`
- `task_intake_to_proof_ladder_decision_table.md`
- `goal_authority_and_decomposition_protocol.md`

## ADR-021: Human Intervention Requires PMO Review Packets

Decision: `accepted_design`

Manual review and external intervention must use PMO-facing review packets
with one specific action, reason, last safe state, allowed decision values,
resume condition, safe parallel-work decision, timeout/default, dedupe key,
redaction boundary, and post-resume verification. Worker conversations may
propose review packets, but only MainAgent/PMO asks the user.

Rationale:

- long tasks commonly block on MWORKS license/login, UE/Fab manual import,
  visual review, destructive approvals, invalid packets, and transport
  timeouts;
- vague user asks and duplicate prompts waste the user's review budget;
- blocker state must survive context compaction and conversation changes;
- manual acceptance must not be inflated into automated proof, planning truth,
  MWORKS evidence, or UE evidence.

Rejected alternative:

- ask the user informal questions directly from whichever worker encounters a
  blocker, then rely on chat memory to resume.

Source:

- `human_review_intervention_ux_design.md`
- `human_review_package_checker_design.md`
- `safety_human_intervention_protocol.md`
- `blocker_packet_templates.md`
- `candidate_e_auth_license_interruption_proof_package.md`

## ADR-022: Validators Share One Report Envelope

Decision: `accepted_design`

All future validators and doctor-style checks must emit one shared report
envelope. The envelope records schema version, target, decision, dependency
reports, findings, evidence paths, side-effect declarations, claim boundaries,
and next action. Domain validators may add fields, but cannot invent local
decision synonyms or treat missing dependencies as pass.

Rationale:

- CoAgent now has many validator designs, and local report semantics would
  make downstream composition unreliable;
- operating metrics and final audits need one decision vocabulary;
- missing dependencies should be visible as `needs_dependency` or
  `fail_before_dispatch`, not hidden warnings;
- read-only validators must not imply that dispatch, Git, MCP, email, GUI, or
  runtime mutation occurred;
- claim boundaries prevent schema checks from being inflated into product
  evidence.

Rejected alternative:

- let each validator choose its own JSON shape, decisions, dependency handling,
  and side-effect language.

Source:

- `validator_shared_envelope_design.md`
- `validator_dependency_and_rollout_plan.md`
- `common_proof_package_validator_design.md`

## ADR-023: Goal Alignment Is A Level-Zero Gate

Decision: `accepted_design`

Goal alignment must run before downstream validators, proof packages,
checkpoints, and completion audits are trusted. A task cannot satisfy the user
by proving a weakened substitute such as creating a task shell, opening
conversations, spending time, writing documents, or producing a backlog item.

Rationale:

- the current project already hit a wrong-goal failure mode where the task was
  narrowed into "establish a 10-hour task";
- downstream validators can pass while proving the wrong objective;
- recreated goals, scoped conversation objectives, result packets, and
  checkpoints all need a shared non-substitution rule;
- completion audits must fail if they pass requirements from weak evidence or
  pending implementation.

Rejected alternative:

- rely on human memory or final review to notice goal weakening after hours of
  work have already been spent.

Source:

- `goal_alignment_checker_design.md`
- `goal_authority_and_decomposition_protocol.md`
- `goal_creation_and_recovery_protocol.md`
- `final_goal_completion_audit.md`

## ADR-024: Runbook Readiness Is Required Before Serious Task Execution

Decision: `accepted_design`

Serious task packages must pass a runbook readiness gate before
multi-conversation dispatch, proof validation, manual rehearsal, integration,
or closeout. The next safe action must be recoverable from project-owned files,
not hidden in chat.

Rationale:

- the end-to-end runbook is currently a process document; a future checker is
  needed so packages cannot skip charter, proof path, context, workflow,
  mailbox, evidence, Git, knowledge, or closeout state;
- dynamic task teams can only remain task-first if routing and readiness are
  validated before execution;
- readiness must compose dependency reports from goal, evidence, context,
  handoff, packet, blocker, mailbox, tool, Git, and retrospective validators;
- closeout overclaims should fail before the user is asked to accept a task as
  done.

Rejected alternative:

- let each serious task decide readiness informally from chat history and
  manual judgment.

Source:

- `runbook_readiness_checker_design.md`
- `end_to_end_task_operating_runbook.md`
- `validator_shared_envelope_design.md`
- `goal_alignment_checker_design.md`

## ADR-025: Implementation Requires A Slice-Specific Approval Gate

Decision: `accepted_design`

Every implementation slice needs explicit user or PMO approval for that named
slice, valid phase entry evidence, bounded scope, declared forbidden actions,
dependency reports, testable exit evidence, and claim boundaries before work
starts.

Rationale:

- a backlog item, phase ladder, or broad design acceptance can otherwise be
  misread as permission to mutate runtime, transport, schemas, tools, MCP,
  Git, scheduler, notification, automation, or permanent conversations;
- implementation safety depends on exact read/write scope and forbidden
  actions, not general architecture approval;
- exit evidence must be testable before the slice begins;
- manual-risk routes need explicit acceptance rather than implied consent.

Rejected alternative:

- treat the post-design backlog or R0-R8 phase order as implementation
  authority.

Source:

- `implementation_approval_gate_design.md`
- `implementation_sequence_and_release_plan.md`
- `post_design_implementation_backlog.md`
- `validator_shared_envelope_design.md`

## Deferred Decisions

| Decision | Current State | Reason |
|---|---|---|
| app-server transport | deferred | file/CLI route and validators must stabilize first |
| automatic conversation creation | deferred | visible conversation bootstrap works but transport/recovery is not proven |
| automatic worktree creation | deferred | worktree binding and Git-heavy proof must exist first |
| real email/desktop notification | deferred | Candidate E blocker/resume semantics must be proven first |
| unattended scheduler | deferred | operating metrics, blockers, and transport hardening are prerequisites |
| new permanent departments | deferred | current 11 visible conversations are sufficient for V1 governance |
| automatic retrospective issue creation | deferred | retrospective records and read-only checker must exist before automation |
| automatic tool capability repair or expansion | deferred | capability cards and read-only `TOOL_*` checker must exist before repair or broad MCP/tool expansion |
| tool-backed product execution | deferred | R6 product-adjacent proof and route-specific approval must pass before R7 execution |
| automatic Git recovery or worktree provisioning | deferred | `GIT_*` fixtures, worktree-binding validation, Candidate D validator, and user-approved execution scope must exist first |
| automatic end-to-end workflow execution | deferred | runbook readiness checker, packet/blocker/context validators, and Candidate A proof must exist first |

## Rejected Decisions

| Decision | Reason |
|---|---|
| use raw full transcript as context pack | causes context bloat and stale assumption drift |
| use hidden subagent chains as durable departments | no recoverable cross-turn state or communication |
| claim screenshots as UE planning truth | rendering is not collision/navmesh/occupancy/SDF truth |
| claim offline script output as MWORKS/UE evidence | violates evidence provenance |
| broad Git staging for large imports | unsafe without inventory and large-file policy |
| main-thread Git trial-and-error for large or locked work | blocks orchestration and risks unrelated state; route through DevOps-owned inventory, blocker, or recovery record |
| choose protocols opportunistically per task without a runbook | recreates ad-hoc judgment and loses cross-protocol invariants |
| assume Fab visibility means automatic import | inventory visibility does not prove download, import, UE compatibility, map modification, or truth export |
| assume a previous MCP success proves current health | tool health is task-local, time-bounded, and claim-specific |
| treat backlog order as implementation approval | each implementation slice still needs explicit approval and phase entry evidence |

## Audit Use

At 10-hour review, use this file to ask:

1. Does any accepted design decision contradict current evidence?
2. Does any deferred decision need to move earlier because of current project
   bottlenecks?
3. Does any rejected decision appear in implementation, packets, or summaries?
4. Are the accepted gates specific enough for the next implementation slice?
5. Are runtime, proof, and implementation claims separated from design claims?
6. Do any derived goals weaken the original user objective into setup work,
   topology changes, elapsed time, or document volume?
7. Did repeated failures close through owned retrospective actions, or are they
   still only scattered notes?
8. Do tool-dependent claims cite capability cards and health levels, or are
   they relying on stale memory, inventory visibility, screenshots, or
   unchecked MCP assumptions?
9. Does the requested next implementation slice belong to the earliest safe
   phase, or does it need an explicit skip/deviation record?
10. Does a serious task cite the end-to-end runbook, or did it select
    conversations/proofs/checks ad hoc?
