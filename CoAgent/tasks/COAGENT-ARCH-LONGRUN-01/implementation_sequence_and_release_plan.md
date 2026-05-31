# Implementation Sequence And Release Plan

Date: 2026-05-30
Status: design contract, not implementation
Owner: DispatchAgent + RuntimePlatformAgent + VerificationAgent
Problem covered: P23

## Purpose

The post-design backlog contains many valid slices. That is not enough to
guide execution. CoAgent needs an implementation sequence that says which
slice is safe to approve first, what each phase proves, what must not be
skipped, and what evidence allows the next phase to start.

This document closes the P23 design gap:

```text
What is the smallest safe implementation sequence after design is accepted?
```

It is design-only. It does not approve implementation, create conversations,
run dispatch, create worktrees, call MCP tools, stage Git, send notifications,
or change runtime schemas.

## Core Rule

```text
implementation order follows risk dependency, not feature appetite
```

CoAgent must implement primitives before orchestration, orchestration before
product automation, and evidence gates before claims.

## Phase Ladder

| Phase | Name | Purpose | Default State |
|---|---|---|---|
| R0 | Review Baseline | freeze accepted design, scope, and approval packet | current design task |
| R1 | Validator Foundation | implement reusable read-only gate envelope and claim guards | next safest implementation |
| R2 | Packet And Blocker Atoms | make result/blocker packets durable enough for delegation | before live multi-conversation proof |
| R3 | Candidate A Preflight | validate architecture packet-chain package before dispatch | before visible proof |
| R4 | Supervised Candidate A Proof | run the smallest visible multi-conversation proof | after preflight or explicit manual-risk approval |
| R5 | Communication Recovery | harden mailbox, transport timeout, visibility drift, and context refresh | before repeated or product dispatch |
| R6 | Product-Adjacent Proofs | validate PX4, UE, Git-heavy, and auth/license packages | after shared packet/recovery gates |
| R7 | Tool-Backed Product Execution | run actual MWORKS/UE/Fab/Git product tasks through proven gates | separate task approval |
| R8 | Operating Evolution | automate metrics, retrospectives, external learning, and promotion loops | after manual loop proves value |

## Phase R0: Review Baseline

Goal:

```text
The user can audit the architecture without reading every file linearly.
```

Entry condition:

- active design task exists;
- `review_brief.md`, `goal_requirement_audit_map.md`,
  `ten_hour_audit_package.md`, and `architecture_decision_record_summary.md`
  exist.

Exit evidence:

- design checks pass;
- 11 registered permanent conversations are visible or a blocker is recorded;
- final audit says design goal is either ready for user review or still
  requires specified design work.

Forbidden in R0:

- implementing runtime behavior under a design-only task;
- marking the long goal complete without final requirement audit;
- using elapsed time, document count, or visible conversations as completion.

## Phase R1: Validator Foundation

Default backlog item:

```text
COAGENT-IMPL-NEXT-00: Validator Dependency Envelope
```

Companion gate:

```text
COAGENT-IMPL-NEXT-25: Goal Alignment Checker
```

Why first:

- every later checker needs a common report envelope;
- goal alignment prevents implementation slices from proving the wrong
  objective;
- dependency failure must become `needs_dependency`, not a silent pass.

Exit evidence:

- common validator envelope exists and has sample pass/fail reports;
- a goal-substitution fixture fails;
- a missing dependency fixture reports `needs_dependency`;
- no live dispatch or product tools are invoked.

Do not start R2 if:

- validator output decisions are not stable;
- local objectives can weaken the canonical user goal;
- missing dependencies are still represented as pass or warning-only.

## Phase R2: Packet And Blocker Atoms

Default backlog items:

```text
COAGENT-IMPL-NEXT-11: Result Packet Contract Hardening
COAGENT-IMPL-NEXT-05: Blocker Packet Templates
```

Why before Candidate A:

- multi-conversation work cannot be durable if results and blockers are not
  machine-checkable;
- timeout, invalid packet, auth/license, GUI, manual-review, destructive, and
  tool-unavailable stops must be resumable before live delegation expands.

Exit evidence:

- valid result packet fixture passes;
- invalid nested YAML, unsupported status, missing evidence, and capability
  overclaim fail with stable codes;
- valid blocker fixtures pass;
- duplicate ask, unsafe retry, missing resume condition, missing last safe
  state, and secret-risk blockers fail with stable codes.

Do not start R3 if:

- a worker result can close a task without review owner;
- a blocker can omit resume condition or dedupe key;
- packet validators rewrite or silently repair worker outputs.

## Phase R3: Candidate A Preflight

Default backlog items:

```text
COAGENT-IMPL-NEXT-15: Candidate A Proof Package Validator
COAGENT-IMPL-NEXT-24: Candidate A Fixture Generator
COAGENT-IMPL-NEXT-13: Handoff Mode And Workflow Graph Validators
COAGENT-IMPL-NEXT-02: Context Delta Template And Checker
```

Why before live proof:

- the first visible multi-conversation proof should test coordination, not
  improvise package shape;
- handoff/workflow/context errors should fail before transport budget is
  spent;
- fixtures prove negative cases before a live conversation can mask them.

Exit evidence:

- valid Candidate A package validates;
- negative fixtures fail for expected reasons;
- workflow graph requires review, result paths, return paths, and closeout;
- context delta and acknowledgement rules block stale high-risk resume.

Do not start R4 if:

- Candidate A package can include product tool nodes without explicit approval;
- raw transcript can pass as context pack;
- result paths can point outside approved roots;
- review node or closeout node is optional.

## Phase R4: Supervised Candidate A Proof

Default backlog item:

```text
COAGENT-IMPL-NEXT-14: Candidate A Minimal Multi-Conversation Proof
```

Allowed modes:

| Mode | When Allowed | Claim |
|---|---|---|
| `validated_live_proof` | R1-R3 gates pass | Candidate A communication mechanics tested |
| `manual_rehearsal` | user explicitly accepts missing-validator risk | supervised rehearsal only |
| `blocked` | transport or visibility fails | blocker/resume state tested if packet valid |

Minimum useful team:

- MainAgent;
- DispatchAgent;
- ContextMemoryAgent;
- VerificationAgent;
- KnowledgeSecretaryAgent.

Exit evidence:

- at least two non-MainAgent visible conversations return valid result packets
  or valid blocker packets;
- context delta and acknowledgement are recorded;
- review packet and trace evaluation exist;
- closeout names next gated implementation work;
- transport timeout, if any, has cleanup and blocker evidence.

Do not use R4 to claim:

- unattended multi-conversation execution;
- product automation;
- app-server messaging;
- automatic conversation creation;
- Git or tool capability reliability.

## Phase R5: Communication Recovery

Default backlog items:

```text
COAGENT-IMPL-NEXT-12: Transport Timeout And Plugin-Sync Hardening
COAGENT-IMPL-NEXT-23: Mailbox Ledger And Replay Checker
COAGENT-IMPL-NEXT-22: Codex Visibility Drift Gate
COAGENT-IMPL-NEXT-21: Context Index And Assembly Checker
COAGENT-IMPL-NEXT-09: Operating Metrics Snapshot
```

Why after Candidate A:

- Candidate A exposes the concrete failure modes worth hardening;
- mailbox replay and context assembly become more meaningful after packet
  atoms exist;
- visibility drift and transport timeout must be bounded before repeated
  dispatch becomes normal.

Exit evidence:

- timed-out dispatch produces valid blocker and closed edge;
- late result reconciliation preserves both timeout evidence and late packet;
- registered visibility drift repairs or blocks safely;
- mailbox replay can compute next safe action;
- context assembly rejects stale, oversized, source-less, and high-risk packs;
- operating metrics flag fake parallelism, stale checkpoint, WIP excess, and
  unsupported claims.

Do not start R6 if:

- repeated dispatch still relies on chat memory;
- visibility repair is attempted on unknown threads;
- context packs can include raw transcript or private Codex state;
- metrics can classify missing data as healthy.

## Phase R6: Product-Adjacent Proofs

Default backlog items:

```text
COAGENT-IMPL-NEXT-06: Stress-Test Artifact Templates And Validators
COAGENT-IMPL-NEXT-07: Evidence Label Doctor Check
COAGENT-IMPL-NEXT-27: Tool Capability Health Gate Checker
COAGENT-IMPL-NEXT-16: Candidate B PX4 Proof Package Validator
COAGENT-IMPL-NEXT-17: Candidate C UE Scene Truth Proof Package Validator
COAGENT-IMPL-NEXT-18: Candidate D Git Heavy Change Proof Package Validator
COAGENT-IMPL-NEXT-19: Candidate E Auth/License Interruption Validator
```

Candidate D and any multi-worktree mutable route also require the
`COAGENT-IMPL-NEXT-04` worktree binding validator contract in
`worktree_git_recovery_validator_design.md`.

Trigger order:

| Trigger | Move Earlier |
|---|---|
| user provides PX4 logs or parameter task | Candidate B |
| UE maps or scene truth block product work | Candidate C |
| large imports/renames/assets appear | Candidate D |
| MWORKS/UE/Fab/Codex login/license/manual review blocks work | Candidate E |
| weak or stale tool claim blocks proof | Tool capability checker |
| evidence-label confusion blocks proof | Evidence label doctor |

Exit evidence:

- PX4 overclaims fail before simulator parameters are accepted;
- UE rendering-as-truth fails before planning readiness is accepted;
- Git-heavy broad staging fails before integration;
- auth/license/manual blockers produce exact PMO asks and resume conditions;
- tool-route claims cannot exceed current health level;
- evidence labels cannot be inflated from design/offline/manual/Git/runtime
  metadata into product proof.

Do not start R7 if:

- Candidate B/C/D/E validators are missing for the product route in use;
- tool capability card is missing, stale, or below required health level;
- evidence label doctor is missing for a product correctness claim;
- unresolved blocker has no resume condition.

## Phase R7: Tool-Backed Product Execution

This is not approved by the architecture design task. It requires a separate
task approval tied to a real product objective, such as:

- PX4 parameter identification and simulator tuning;
- UE scene truth export and planning integration;
- large Git integration of imported assets;
- auth/license/manual-review proof;
- MWORKS or UE execution evidence for report claims.

Entry condition:

- relevant R6 proof package and validators pass or user explicitly approves a
  bounded manual route;
- tool capability health level satisfies the requested claim;
- blocker policy and fallback route are known.

Exit evidence:

- product-specific result artifacts exist;
- evidence labels match production mechanism;
- review owner accepts the claim;
- Git integration follows Candidate D policy if files enter version control.

Forbidden:

- treating design-only protocols as product proof;
- using screenshots as UE planning truth;
- labeling offline scripts as MWORKS evidence;
- calling Fab inventory automated import proof;
- broad Git staging without inventory.

## Phase R8: Operating Evolution

Default backlog items:

```text
COAGENT-IMPL-NEXT-10: External Learning Adoption Queue
COAGENT-IMPL-NEXT-26: Retrospective Closure Checker
```

Later gated features:

- scheduled external learning;
- automatic issue creation;
- automatic skill/workflow promotion;
- email or desktop notifications;
- app-server transport;
- unattended scheduler.

Entry condition:

- manual proposal/rejection/promotion flow has at least one accepted and one
  rejected example;
- retrospective records close through owner, evidence, action target, and
  review owner;
- no automation expands the safety boundary before checkers exist.

Exit evidence:

- accepted external ideas promote to docs/skills/checkers/backlog with
  validation plan;
- rejected ideas have reopen triggers;
- repeated failures generate closed retrospective actions;
- stale retrospective actions block completion instead of becoming notes.

## Global Skip Rules

Skip is forbidden when the skipped phase is the only evidence for:

- goal alignment;
- result packet durability;
- blocker resumability;
- context freshness;
- handoff/workflow correctness;
- transport timeout recovery;
- mailbox replay;
- tool capability health;
- evidence-label integrity;
- product-proof truth.

Skip is allowed only when:

1. the task is an ordinary small task;
2. the skipped phase is irrelevant to the task class;
3. the reason is recorded in a task charter or proof package;
4. the review owner accepts the risk.

## Approval Packet For Each Implementation Slice

Before implementing any backlog item, create or cite an approval packet with:

```yaml
implementation_approval:
  backlog_id: COAGENT-IMPL-NEXT-XX
  phase: R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8
  user_or_pmo_approval: explicit approval text or task id
  scope:
    read_paths: []
    write_paths: []
    forbidden_actions: []
  entry_evidence:
    - path or command result
  expected_exit_evidence:
    - validator report, fixture result, proof closeout, or blocker packet
  rollback_or_stop_rule: exact condition
  review_owner: VerificationAgent | SafetyComplianceAgent | MainAgent
```

Future `COAGENT-IMPL-NEXT-31` should implement a read-only implementation
approval gate for this packet. The gate must reject backlog-as-authority,
implicit approval, invalid phase jumps, broad write scope, unapproved external
paths, secret-risk routes, missing dependency reports, weak exit evidence, and
missing claim boundaries. The gate must not implement the approved slice.

## Release Milestones

| Milestone | Contents | Release Claim |
|---|---|---|
| `M0-design-audit-ready` | R0 complete | architecture is reviewable, not implemented |
| `M1-validator-atoms` | R1-R2 complete | packets/blockers/goal gates are checkable |
| `M2-candidate-a-ready` | R3 complete | first visible proof can run without improvised package repair |
| `M3-candidate-a-proven` | R4 complete | supervised multi-conversation packet chain proved |
| `M4-recovery-ready` | R5 complete | repeated dispatch has recovery and replay gates |
| `M5-product-proof-ready` | R6 complete | PX4/UE/Git/auth proof packages can gate product work |
| `M6-product-execution-ready` | R7 approved and route-specific proof passes | selected product route can execute under CoAgent |
| `M7-evolution-loop-ready` | R8 complete | external learning and retrospectives can improve the system safely |

No release milestone may imply a later milestone. For example, `M3` does not
mean UE, Fab, MWORKS, Git, or notification automation is reliable.

## Current Design Decision

P23 is now design-baselined:

```text
The implementation path is a phase ladder from review baseline to validator
foundation, packet/blocker atoms, Candidate A preflight, supervised Candidate A
proof, communication recovery, product-adjacent proofs, tool-backed product
execution, and operating evolution. Each phase has entry evidence, exit
evidence, skip rules, and forbidden claims.
```

Implementation remains gated by explicit approval of each backlog item.
