# COAGENT-ARCH-LONGRUN-01 Candidate A Packet Chain Blueprint

Date: 2026-05-30
Status: design blueprint for later proof execution

## Purpose

Candidate A is the next recommended minimal multi-conversation proof. It
exercises CoAgent communication and review mechanics with low tool risk before
PX4, UE, Git-heavy, or MWORKS-heavy tasks.

This blueprint defines the packets and acceptance checks needed to run
Candidate A later. It does not execute the proof and does not authorize
automatic dispatch.

## Proof Goal

```text
Prove that a small visible task team can pass a task through context,
execution, review, context delta, knowledge promotion, and closeout using
durable packets rather than hidden chat.
```

## Conversation Set

Required:

| Conversation | Role |
|---|---|
| MainAgent | PMO and final synthesis |
| DispatchAgent | task charter, handoff modes, board, mailbox, result intake |
| ContextMemoryAgent | context pack review and context delta |
| VerificationAgent | result packet and trace evaluation review |
| KnowledgeSecretaryAgent | promotion candidate and closeout record |

Optional:

| Conversation | Trigger |
|---|---|
| RuntimePlatformAgent | if transport or visibility repair is part of the proof |
| SafetyComplianceAgent | if the proof touches external paths, credentials, or destructive actions |
| DevOpsReleaseAgent | if the proof touches worktrees, staging, or Git integration |

## Task Charter

Task id:

```text
COAGENT-PROOF-CANDIDATE-A
```

Canonical goal:

```text
Complete one low-tool-risk architecture packet-chain proof across the smallest
useful visible conversation set, with valid result packets, review packet,
context delta, closeout, and trace evaluation.
```

Non-goals:

- no app-server transport implementation;
- no automatic conversation creation;
- no automatic worktree creation;
- no email or desktop notification;
- no UE/MWORKS/Fab tool work;
- no broad Git operation.

Definition of done:

- task charter exists;
- handoff mode records exist for each routed conversation;
- each worker has a context pack path;
- at least two non-MainAgent conversations return valid result packets or
  valid blocker packets;
- one review packet accepts, rejects, or requests rework;
- one context delta is produced and acknowledged;
- one knowledge promotion or rejection record exists;
- trace evaluation records process metrics and missing instrumentation;
- closeout states what was proven and what remains gated.

## Handoff Records

### Dispatch To ContextMemoryAgent

Mode:

```text
department_lane
```

Authority transfer:

```text
scoped_execution
```

Expected result:

```text
context sufficiency review plus context delta proposal
```

Required output:

```text
Results/agent_packets/COAGENT-PROOF-CANDIDATE-A-CONTEXT.yaml
```

### Dispatch To VerificationAgent

Mode:

```text
department_lane
```

Authority transfer:

```text
review_gate
```

Expected result:

```text
review of Candidate A packet chain and trace evaluation requirements
```

Required output:

```text
Results/agent_packets/COAGENT-PROOF-CANDIDATE-A-VERIFY.yaml
```

### Dispatch To KnowledgeSecretaryAgent

Mode:

```text
department_lane
```

Authority transfer:

```text
scoped_execution
```

Expected result:

```text
promotion candidate or rejected-idea record for one stable lesson from the proof
```

Required output:

```text
Results/agent_packets/COAGENT-PROOF-CANDIDATE-A-KNOWLEDGE.yaml
```

## Context Pack Requirements

The context pack for every worker must include:

- canonical goal;
- non-goals;
- required flat result packet contract;
- paths to:
  - `minimal_multiconversation_proof_requirements.md`;
  - `enterprise_to_coagent_execution_mapping.md`;
  - `operating_metrics_and_anti_drift_cadence.md`;
  - `handoff_mode_and_workflow_graph_design.md`;
  - `problem_driven_external_adoption_queue.md`;
- forbidden actions;
- expected result packet path;
- stop condition.

The context pack must exclude:

- raw full transcript;
- secrets or private session data;
- unrelated MoSim product tasks;
- UE/MWORKS/Fab tool execution details unless the optional Toolchain lane is
  deliberately added.

## Result Packet Contract

Every worker must use:

```text
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/result_packet_contract_hardening.md
```

Required terminal values:

- `completed`;
- `review_required`;
- `blocked`;
- `failed`;
- `rejected`;
- `superseded`;
- `canceled`.

Conditional completion:

```text
status: completed
canonical_status: completed
review_status: needs_review
acceptance_state: partially_met
```

## Review Packet Requirements

VerificationAgent must check:

- packet validity;
- canonical goal preservation;
- evidence paths;
- context delta and acknowledgement state;
- missing process metrics;
- open blockers;
- whether Candidate A should proceed to actual execution or needs rework.

Review output states:

- `accepted`;
- `accepted_with_concerns`;
- `needs_rework`;
- `rejected`;
- `blocked`.

## Context Delta Requirements

Candidate A must produce at least one context delta that states:

- changed lesson or decision;
- affected future proof or implementation slice;
- superseded assumption if any;
- acknowledgement required or not;
- reviewer;
- resume condition.

If no context delta is needed, the proof should fail because it did not test
context lifecycle.

## Trace Evaluation Requirements

Trace evaluation must report:

- `handoff_failure_count`;
- `invalid_result_packet_count`;
- `transport_timeout_count`;
- `context_refresh_latency`;
- `evidence_gap_count`;
- `blocked_time_without_packet`;
- `fake_parallelism_count`;
- `serial_collapse_count`;
- `review_escape_count`;
- missing instrumentation.

Metrics can be `needs_instrumentation`, but cannot be omitted.

## Pass Criteria

Candidate A passes if:

1. every routed worker produces a valid result packet or valid blocker packet;
2. at least two non-MainAgent packets are imported;
3. review packet accepts or accepts with concerns;
4. context delta is recorded and acknowledged or explicitly marked no-ack;
5. mailbox has no open required response;
6. closeout states what was proven;
7. no worker changes the canonical goal;
8. no implementation-gated feature is executed.

## Block Criteria

Candidate A blocks if:

- transport produces no packet and no blocker packet;
- any worker returns nested YAML or unsupported status without repair path;
- context pack is stale and acknowledgement is missing;
- a worker attempts UE/MWORKS/Fab/Git work not in scope;
- the proof requires user action that was not part of the charter.

## Follow-On Decisions

After Candidate A:

| Outcome | Next step |
|---|---|
| pass without packet repair | proceed to PX4 or UE gate proof |
| pass with packet repair | implement result-packet validator first |
| timeout blocker | implement transport timeout hardening first |
| context stale blocker | implement context delta checker first |
| review rejects evidence | tighten proof charter and repeat |

## Current Recommendation

Do not run Candidate A until the user chooses to move from design into the
proof experiment. The architecture now has enough blueprint detail to execute
Candidate A without inventing routing rules during the run.
