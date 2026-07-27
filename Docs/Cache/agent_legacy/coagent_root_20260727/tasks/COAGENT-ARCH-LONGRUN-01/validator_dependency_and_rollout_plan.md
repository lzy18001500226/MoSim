# COAGENT-ARCH-LONGRUN-01 Validator Dependency And Rollout Plan

Date: 2026-05-30
Status: design contract for validator sequencing

## Purpose

CoAgent now has many validator designs. If they are implemented independently,
future task execution can still bypass the important checks. This document
defines the dependency graph, rollout order, and failure routing for the
validator layer.

This is design-only. It does not implement validators, execute proof packages,
dispatch conversations, create worktrees, call MCP tools, or stage Git.

## Core Rule

```text
validators are a gate graph, not a checklist
```

A later gate may depend on earlier gate outputs. If a dependency is missing,
the later gate must report `needs_dependency` or `blocked`, not silently weaken
its decision.

## Validator Layers

| Layer | Validator Design | Main Backlog Item | Purpose |
|---|---|---|---|
| L0 | `goal_authority_and_decomposition_protocol.md` | `COAGENT-IMPL-NEXT-25` | prevent derived goals from weakening the user objective |
| L0 | `evidence_label_doctor_design.md` | `COAGENT-IMPL-NEXT-07` | classify evidence provenance and reject label inflation |
| L1 | `result_packet_validator_design.md` | `COAGENT-IMPL-NEXT-11` | make department result packets durable |
| L1 | `blocker_packet_validator_design.md` | `COAGENT-IMPL-NEXT-05` | make blocked states resumable |
| L1 | `tool_capability_health_and_fallback_protocol.md` | `COAGENT-IMPL-NEXT-27` | gate tool/MCP/Fab/Codex/Git route claims before product or dispatch work depends on them |
| L2 | `handoff_workflow_validator_design.md` | `COAGENT-IMPL-NEXT-13` | validate routing and workflow graph before dispatch |
| L2 | `context_delta_checker_design.md` | `COAGENT-IMPL-NEXT-02` | validate context freshness and acknowledgement |
| L2 | `mailbox_ledger_and_replay_design.md` | `COAGENT-IMPL-NEXT-23` | validate communication replay and open responses |
| L3 | `common_proof_package_validator_design.md` | `COAGENT-IMPL-NEXT-20` | validate common proof package contract |
| L3 | `candidate_a_validator_execution_design.md` | `COAGENT-IMPL-NEXT-15` | validate Candidate A package and closeout |
| L3 | `stress_test_artifact_validator_design.md` | `COAGENT-IMPL-NEXT-06` | validate PX4/UE product-adjacent artifacts |
| L3 | `worktree_git_recovery_validator_design.md` | `COAGENT-IMPL-NEXT-04`, `COAGENT-IMPL-NEXT-18` | validate worktree binding, Git-heavy inventory, integration plan, blockers, rollback, and cleanup |
| L3 | `human_review_package_checker_design.md` | `COAGENT-IMPL-NEXT-29` | validate one-action user asks, blocker resume mapping, dedupe, redaction, manual evidence boundaries, and notification readiness |
| L4 | `operating_metrics_snapshot_design.md` | `COAGENT-IMPL-NEXT-09` | measure long-task health and drift |
| L4 | `transport_timeout_hardening_design.md` | `COAGENT-IMPL-NEXT-12` | reconcile dispatch timeout, late result, cleanup, and edge state |
| L4 | `codex_visibility_drift_reliability_design.md` | `COAGENT-IMPL-NEXT-22` | gate visible conversation dispatch readiness |
| L4 | `external_adoption_store_checker_design.md` | `COAGENT-IMPL-NEXT-10` | gate external-learning proposal lifecycle |
| L4 | `retrospective_and_improvement_closure_protocol.md`, `retrospective_closure_checker_design.md` | `COAGENT-IMPL-NEXT-26` | ensure repeated failures close through owned actions, promotion, rejection, or deferral |
| L5 | `runbook_readiness_checker_design.md` | `COAGENT-IMPL-NEXT-30` | compose task-package readiness before dispatch, manual rehearsal, integration, or closeout |
| L5 | `implementation_approval_gate_design.md` | `COAGENT-IMPL-NEXT-31` | prevent backlog or phase order from becoming implicit implementation approval |

## Dependency Graph

### Evidence And Packet Base

```text
goal_alignment_checker
  -> evidence_label_doctor
evidence_label_doctor
  -> result_packet_validator
  -> blocker_packet_validator
  -> tool_capability_health_gate
```

Rationale:

- goal alignment decides whether the packet or evidence is trying to prove the
  right thing;
- result packets and blocker packets both cite evidence;
- evidence labels must be checked before packet claims are accepted;
- blocker packets often include result-packet or transport findings.
- tool capability cards cite evidence labels and often produce blocker packets,
  so the tool gate depends on both evidence provenance and blocker semantics.

### Dispatch Preflight

```text
goal_alignment_checker
  -> evidence_label_doctor
  -> context_delta_checker
  -> handoff_workflow_validator
  -> common_proof_package_validator
  -> candidate_a_validator
```

Rationale:

- a handoff is invalid if its local objective weakens the canonical task goal;
- context freshness must be known before a handoff can be safe;
- workflow graph and handoff objects must be valid before a proof package is
  dispatchable;
- Candidate A should compose the common proof contract instead of inventing
  its own preflight.

### Post-Dispatch Closeout

```text
goal_alignment_checker
  -> result_packet_validator
  -> blocker_packet_validator
  -> mailbox_ledger_replay_checker
  -> common_proof_package_validator
  -> operating_metrics_snapshot
```

Rationale:

- result and blocker packets cannot close a task if they prove a substituted
  goal;
- result/blocker packets are the communication atoms;
- mailbox replay determines open responses, contradictions, and duplicate
  blockers;
- proof closeout cannot pass with invalid packets or open required responses;
- metrics snapshot should measure accepted durable state, not raw chat.

### Product-Adjacent Proofs

```text
evidence_label_doctor
  -> tool_capability_health_gate
  -> stress_test_artifact_validator
  -> common_proof_package_validator
  -> Candidate B / Candidate C package validators
```

Rationale:

- PX4/UE artifacts rely on evidence provenance;
- product-adjacent artifacts also rely on current route health rather than
  stale MCP, GUI, launcher, or inventory assumptions;
- Candidate B/C validators should check proof-package structure plus artifact
  truth, not one or the other.

### Transport Readiness

```text
codex_visibility_drift_gate
  -> tool_capability_health_gate
  -> handoff_workflow_validator
  -> transport_timeout_hardening
  -> blocker_packet_validator
  -> mailbox_ledger_replay_checker
```

Rationale:

- visible conversation dispatch should not start from known visibility drift;
- Codex transport is also a tool route with health levels and stale-card
  policy;
- timeout hardening must produce a valid blocker or accepted late result;
- mailbox replay should see the timeout or result as recoverable state.

### External Learning

```text
evidence_label_doctor
  -> external_adoption_store_checker
  -> knowledge_promotion_gate
  -> context_index_and_assembly_checker
```

Rationale:

- external references are evidence, not policy;
- adoption decisions must be accepted/rejected/deferred before promotion;
- future context packs should cite accepted proposals and rejected assumptions.

### Retrospective Closure

```text
operating_metrics_snapshot
  -> retrospective_closure_checker
retrospective_closure_checker
  -> knowledge_promotion_gate
  -> implementation_backlog_review
  -> external_adoption_store_checker
  -> goal_completion_gate
```

Rationale:

- metrics and incidents identify recurrence, stale actions, and review escapes;
- retrospective records decide whether the response is implementation,
  promotion, rejection, or deferral;
- accepted lessons must pass through knowledge promotion or external adoption;
- unresolved mandatory retrospective actions should block a clean goal closeout.

### Runbook Readiness

```text
goal_alignment_checker
  -> evidence_label_doctor
  -> context_delta_checker
  -> handoff_workflow_validator
  -> result_packet_validator
  -> blocker_packet_validator
  -> mailbox_ledger_replay_checker
  -> tool_capability_health_gate
  -> worktree_git_validators
  -> retrospective_closure_checker
  -> runbook_readiness_checker
```

Rationale:

- serious task packages are the composition point for charter, proof path,
  context, workflow, mailbox, packets, evidence, Git, knowledge, and closeout;
- runbook readiness should report missing dependencies rather than weakening
  the operating sequence;
- live dispatch, manual rehearsal, integration, or closeout should not start
  when the next safe action exists only in chat.

### Implementation Approval

```text
goal_alignment_checker
  -> runbook_readiness_checker
  -> implementation_approval_gate
```

Rationale:

- approval should be for the right objective, not a weakened setup action;
- serious implementation slices need a ready task package or an explicit
  waiver;
- backlog order, phase ladder, or design acceptance must not authorize runtime
  mutation, tool/MCP expansion, Git work, notification, scheduler, or
  automation by themselves.

## Rollout Order

Recommended implementation order after design approval:

1. Goal alignment checker.
2. Evidence label doctor.
3. Result packet validator.
4. Blocker packet validator.
5. Tool capability health gate.
6. Handoff/workflow validator.
7. Context delta checker.
8. Common proof package validator.
9. Candidate A validator.
10. Transport timeout hardening.
11. Operating metrics snapshot.
12. Mailbox ledger/replay checker.
13. Stress-test artifact validators.
14. External adoption store checker.
15. Codex visibility drift gate.
16. Context index and assembly checker.
17. Retrospective closure checker.
18. Runbook readiness checker.
19. Implementation approval gate.

Reasoning:

- goal alignment must run first because proving the wrong goal is still
  failure;
- labels, result packets, and blockers are the smallest reusable primitives;
- tool capability health is needed before product-adjacent tools or transport
  routes can become proof dependencies;
- workflow/context/proof validators are the minimum preflight set for Candidate
  A;
- timeout and metrics convert known live-dispatch failures into durable state;
- mailbox replay becomes more valuable once packets/blockers exist;
- PX4/UE and external-learning validators should build on the common evidence
  and packet layer;
- visibility and context-assembly gates can remain manual until dispatch
  volume increases, unless drift continues to block work.
- retrospective closure can run after metrics and packet/checker primitives
  exist, but should move earlier if repeated failures keep recurring without
  owned closeout.
- runbook readiness composes many previous reports and therefore should not be
  the first checker, but it must exist before serious task packages are routed
  repeatedly or closed as done.
- implementation approval can be implemented once the shared envelope and goal
  alignment exist; it is especially important before any runtime, transport,
  schema, MCP/tool, Git, scheduler, notification, or automation slice.

## Dependency Failure Policy

If a validator depends on another validator that is not implemented or has no
report:

| Situation | Required Decision |
|---|---|
| dependency absent in design-only audit | `needs_dependency` |
| dependency absent before live dispatch | `fail_before_dispatch` |
| dependency failed with errors | `blocked` or `reject` |
| dependency passed with warnings | `needs_review` unless warning is declared non-blocking |
| dependency report stale | `blocked` for high-risk work |
| dependency report missing evidence paths | `needs_review` or `reject` by claim type |

No validator may downgrade a missing dependency to `pass`.

## Shared Output Envelope

Every validator should emit a common envelope:

```json
{
  "ok": false,
  "validator": "result_packet_validator",
  "validator_version": "0.1",
  "task_id": "COAGENT-ARCH-LONGRUN-01",
  "mode": "preflight",
  "decision": "fail_before_dispatch",
  "dependency_reports": [],
  "finding_codes": [],
  "findings": [],
  "evidence_paths": [],
  "next_action": "fix_package_before_dispatch"
}
```

Candidate-specific validators may add fields, but must preserve the common
envelope so operating metrics and audit tools can consume reports uniformly.

## Stable Cross-Validator Decisions

Allowed common decisions:

- `pass`
- `pass_with_warnings`
- `needs_dependency`
- `needs_review`
- `fail_before_dispatch`
- `blocked`
- `reject`

Do not use local synonyms such as `ok_but`, `accepted_with_conditions`, or
`done_needs_review`. Conditional success should use `pass_with_warnings` or
`needs_review` with explicit findings.

## Report Storage

Default report root:

```text
Results/coagent_validators/<task-id>/<validator-name>/<timestamp>.json
```

For proof packages, a copy or pointer should also live under:

```text
Results/coagent_proofs/<proof-id>/validator_reports/
```

Reports are evidence artifacts. They should not include secrets, raw full chat,
private Codex database dumps, or unapproved external paths.

## Candidate A Minimum Gate Set

Before Candidate A live proof is trusted, either implement or manually emulate
these checks:

1. evidence label doctor for all evidence manifests;
2. result packet validator for returned packets;
3. blocker packet validator for timeout or invalid-packet cases;
4. handoff/workflow validator for graph and handoffs;
5. context delta checker for stale-context and acknowledgement state;
6. Candidate A proof-package validator for preflight and closeout.

If any of these are not implemented, the live proof may still be run only as a
manual experiment, and the missing checks must be listed in closeout as
`needs_dependency`.

## Product Proof Minimum Gate Set

Candidate B requires:

- evidence label doctor;
- tool capability health gate for MWORKS/Sysplorer route if simulation tuning
  or MWORKS evidence is claimed;
- PX4 artifact validator;
- common proof package validator;
- blocker packet validator for missing log/spec/tool;
- result packet validator for worker returns.

Candidate C requires:

- evidence label doctor;
- tool capability health gate for UE/Fab/manual-import route;
- UE artifact validator;
- common proof package validator;
- blocker packet validator for Fab/UE/MCP/manual import;
- result packet validator for worker returns.

## Operational Proof Minimum Gate Set

Candidate D requires:

- blocker packet validator;
- tool capability health gate for Git/worktree/integration route;
- common proof package validator;
- worktree/Git proof-package validator from
  `worktree_git_recovery_validator_design.md`;
- evidence label doctor for Git/test/evidence claims.

Candidate E requires:

- blocker packet validator;
- tool capability health gate for the route that triggered the interruption;
- evidence label doctor for manual/GUI/tool claims;
- common proof package validator;
- operating metrics snapshot for duplicate asks and unsafe retry.

Retrospective closure requires:

- operating metrics snapshot or incident/review records;
- blocker/result packet validators when the trigger references packets;
- external adoption checker when the action cites vendor/open-source lessons;
- knowledge promotion gate when the closeout claims durable project learning.

Implementation approval requires:

- explicit user or PMO approval for the named backlog item;
- goal alignment when the slice changes task, goal, or closeout behavior;
- runbook readiness or an explicit waiver for serious task packages;
- tool capability health gate for MCP/tool/Git/Codex/Fab/MWORKS/UE routes;
- worktree/Git validators before Git-heavy or multi-worktree implementation;
- human-review package checker from `human_review_package_checker_design.md`
  before notification, manual review, or external intervention
  implementation.

## Open Design Questions

1. Should result packet validation or evidence label validation run first when
   a result packet itself is malformed?
   Default: run structural result packet validation first, then evidence label
   validation only if evidence fields can be parsed.
2. Should mailbox replay be required before Candidate A live proof?
   Default: not required for the first manual experiment, required before any
   unattended or repeated multi-conversation dispatch.
3. Should Codex visibility drift gate move earlier?
   Default: keep as pre-dispatch manual/doctor check unless drift recurs during
   the next live proof.
4. Should validator reports be committed?
   Default: design reports and fixtures may be committed; live runtime reports
   under `Results/` stay local unless explicitly selected as lightweight
   evidence.
5. Should retrospective closure checker move earlier?
   Default: keep after operating metrics snapshot, but move earlier if the same
   user correction, visibility drift, packet failure, or unsafe retry recurs
   without clear owner and closeout evidence.
6. Should implementation approval gate move into R1?
   Default: yes for any slice that changes runtime, transport, schema, tool,
   MCP, Git, scheduler, notification, automation, or permanent conversation
   design; otherwise it can be manually checked from the approval packet until
   implemented.

## Design Decision

The validator layer should be rolled out from reusable evidence and packet
primitives upward to workflow, context, proof, metrics, and product-specific
validators. A future implementation may choose a different order only if it
records the dependency risk and keeps missing dependencies visible as
`needs_dependency`, not as a pass.
