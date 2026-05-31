# COAGENT-ARCH-LONGRUN-01 Minimal Multi-Conversation Proof Requirements

Date: 2026-05-30
Status: design draft

## Purpose

The current design already has a file-level closed loop and several visible
department dispatch experiments. The next architecture proof must show that
CoAgent can run one task through multiple visible conversations without
depending on hidden chat memory or manual interpretation.

This document defines the minimal proof requirement. It does not authorize
automatic conversation creation, app-server transport, automatic worktrees,
email, broad hooks, or unattended execution.

## What This Proof Must Demonstrate

The proof must demonstrate one complete task slice with:

```text
PMO/Dispatch task charter
  -> context pack
  -> handoff mode record
  -> visible department or scoped conversation execution
  -> result packet
  -> review packet
  -> context delta
  -> integration or closeout record
  -> trace evaluation
```

The proof can be design-only or file/CLI-assisted, but it must use current
state as evidence and it must record failures as packets rather than hiding
them in chat.

## Minimum Conversations

Use the smallest visible set that proves the control loop:

| Conversation | Required role |
|---|---|
| MainAgent | user-facing PMO, final synthesis |
| DispatchAgent | task board, handoff mode, result intake |
| ContextMemoryAgent | context pack and context delta |
| VerificationAgent | review packet and trace evaluation |
| KnowledgeSecretaryAgent | closeout and promotion candidate |

Optional only if the test content requires it:

| Conversation | Use when |
|---|---|
| RuntimePlatformAgent | testing transport/session behavior |
| DevOpsReleaseAgent | testing worktree or Git integration |
| SafetyComplianceAgent | testing blocker/manual approval path |
| ToolchainMCPAgent | testing tool/MCP capability card |

Do not include all 11 permanent conversations just to show scale.

## Proof Candidate A: Architecture Packet Chain

Use when the goal is to prove communication mechanics without tool risk.

Flow:

1. Dispatch creates a small architecture review task.
2. ContextMemoryAgent receives a context pack and returns a context review.
3. VerificationAgent reviews the result packet and checks required fields.
4. KnowledgeSecretaryAgent records one promotion candidate or rejected idea.
5. Dispatch closes the board and PMO reports the evidence.

Acceptance:

- at least two non-MainAgent visible conversations produce result packets;
- every result packet validates without manual repair, or invalid packets
  produce an `invalid_result_packet` blocker;
- at least one context delta is written and acknowledged;
- trace evaluation records handoff clarity, evidence quality, and recovery
  readiness.

## Proof Candidate B: PX4 Parameter Identification Gate

Use when the goal is to anchor the proof to a real MoSim task.

Flow:

1. Dispatch charters a PX4 log parameter-identification discovery task.
2. ContextMemoryAgent builds a log-analysis context pack.
3. A scoped or department conversation completes the log audit and
   identifiability matrix only.
4. VerificationAgent reviews whether the matrix is enough to proceed to
   estimator implementation.
5. KnowledgeSecretaryAgent records the reusable workflow delta.

Acceptance:

- no estimator implementation starts before data sufficiency and
  identifiability pass;
- missing log fields produce `input_required`, not guessed parameters;
- result uses
  `CoAgent/protocol/templates/px4_parameter_identifiability_matrix.yaml`;
- evidence labels distinguish `design_only`, `offline_script`, and
  `MWORKS_MCP`.

## Proof Candidate C: UE Scene Truth Capability Gate

Use when the goal is to anchor the proof to UE/Fab/MCP product work.

Flow:

1. Dispatch charters a scene-truth capability gate.
2. ToolchainMCPAgent or a scoped conversation fills the scene-source capability
   card.
3. VerificationAgent checks whether the evidence supports planning-truth work.
4. SafetyComplianceAgent reviews Fab/license/manual import/large asset risk if
   triggered.
5. KnowledgeSecretaryAgent promotes the chosen route or records a stop rule.

Acceptance:

- rendering screenshots are not accepted as planning truth;
- Fab-only unknowns produce a manual-import blocker or local-project fallback;
- result uses
  `CoAgent/protocol/templates/ue_scene_truth_capability_card.yaml`;
- no UE write operation is attempted without tool capability evidence.

## Required Packet Chain

The proof must include these artifacts:

| Artifact | Required content |
|---|---|
| task charter | canonical goal, DoD, appetite, non-goals, stop condition |
| handoff mode | mode, authority transfer, input filter, return path |
| context pack | relevant accepted decisions, excluded stale assumptions |
| result packet | flat router-compatible packet or explicit invalid-packet blocker |
| review packet | acceptance, rework, or rejection with evidence checked |
| context delta | changed decision/fact, affected slices, ack state |
| closeout summary | what was proven, what remains gated |
| trace evaluation | process metrics and anti-drift findings |

## Required Metrics

The proof must report:

- `critical_path_age`;
- `checkpoint_age`;
- `handoff_failure_count`;
- `context_refresh_latency`;
- `evidence_gap_count`;
- `fake_parallelism_count`;
- `serial_collapse_count`;
- `blocked_time_without_packet`;
- `transport_timeout_count`.

Missing instrumentation must be reported as `needs_instrumentation`.

## Pass/Fail Rules

Pass when:

- the packet chain is complete;
- the canonical task goal is unchanged;
- no high-risk work resumes from stale context;
- no required response remains open in the mailbox;
- review accepts the output or accepts it with explicit follow-up;
- closeout names the next implementation or experiment.

Fail or block when:

- a worker changes the canonical goal;
- a result packet is invalid and no blocker is recorded;
- context is stale and acknowledgement is missing;
- a blocker is retried without a blocker packet;
- implementation begins before required review gate;
- the proof depends on raw chat as the only evidence.

## Recommended Next Proof

The recommended next proof is Candidate A first.

Reason:

- it exercises Dispatch, Context, Verification, and Knowledge Secretary with
  low tool risk;
- it can verify the packet format problem discovered in the current run;
- it does not depend on UE/MWORKS/Fab availability;
- it creates evidence before attempting the higher-risk PX4 or UE task proofs.

Candidate B and C should follow only after Candidate A can complete without
manual packet repair.

## Current Known Risk

The current `codex exec resume` route can time out because plugin sync and MCP
startup noise consume the 60 second budget. Therefore this proof must accept
either:

- valid result packets within the budget; or
- timeout blocker packets with stdout/stderr evidence and closed dispatch
  edges.

It must not treat silent missing result files as acceptable.
