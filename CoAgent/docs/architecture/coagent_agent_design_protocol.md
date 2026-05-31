# CoAgent Agent Design Protocol V1

Date: 2026-05-28

Status: design baseline. This does not approve runtime, transport,
automation, app-server, or new permanent department implementation.

Task id: `COAGENT-DESIGN-08`

## Purpose

This document translates the closed technical-enterprise management baseline
into an Agent-system design protocol.

The enterprise layer answers how MoSim should manage work. This protocol
answers how that work is represented across Codex conversations, durable task
state, context packs, packets, and short-lived workers.

The goal is a high-quality long-task operating system, not a large agent swarm
and not a fixed seven-department bureaucracy.

## Core Decision

CoAgent V1 uses a centralized, auditable, packet-based control plane:

```text
PMO/main
  -> DispatchCenter
    -> department conversation or task team
      -> one or more scoped task conversations
        -> optional short-lived subagent
```

Durable authority belongs to project-owned task state and packet records, not
to hidden chat memory or peer-to-peer conversation side effects.

For large objectives, the execution unit is a task team:

```text
one canonical task goal
  -> one task team
  -> multiple scoped task conversations when needed
  -> optional subagents inside each conversation
  -> optional worktrees for isolation
```

Current department threads are visible routing channels. They are not the
architectural ceiling.

## Design Invariants

1. One durable task has one canonical task goal.

   Project, phase, conversation, and subagent objectives may frame or scope
   work, but they must not silently replace the canonical task goal.

2. Conversation creation is a cost.

   A new visible conversation is justified only when continuity, visibility,
   recovery, or independent review is worth the synchronization burden.

3. Context is curated, not copied.

   New conversations receive compact context packs with task intent, scope,
   evidence links, stop conditions, and output contract. They do not receive raw
   full transcripts by default.

4. Communication is packet-first.

   Task packets, context packs, checkpoint packets, result packets, review
   notes, and event logs are the durable communication units.

5. Subagents are disposable workers.

   A subagent may answer one bounded question or inspect one source slice. It
   must return evidence to its parent and must not own durable Git, review,
   test, safety, or documentation queues.

6. Workers do not self-route.

   If a worker finds scope drift, missing context, or a better owner, it returns
   a checkpoint or result packet with an escalation. DispatchCenter changes
   owner or goal only with a recorded event.

7. Review is a state transition.

   Human review, test review, security review, docs review, and DevOps release
   review must appear as task state or result review metadata. A prose sentence
   is not enough to accept a durable task.

## Goal Stack

V1 keeps one writable goal layer: the canonical task goal.

| Layer | Owner | Purpose | Can change canonical task goal? |
|---|---|---|---|
| Project Goal | User + PMO | Long-term MoSim direction and priority filter | No |
| Phase / Strategic Objective | PMO | Temporary focus such as CoAgent, UE scene truth, or MWORKS evidence | No; it tags and prioritizes tasks |
| Canonical Task Goal | DispatchCenter | The official objective for one durable task | Yes, only with PMO/user record |
| Conversation Objective | Department or dedicated task conversation | Scoped work order derived from the canonical task | No; may request change |
| Subagent Objective | Parent conversation | One-shot bounded question | No |

If the task goal is wrong, the correct action is:

```text
return checkpoint/result with evidence
  -> DispatchCenter records review_required or blocked
  -> PMO/user decides whether to revise the canonical task goal
```

## Conversation Types

V1 recognizes five execution surfaces:

| Type | Durable? | Use When | Authority |
|---|---:|---|---|
| Main / PMO conversation | yes | user alignment, final integration, accepted decisions | project direction and final report |
| DispatchCenter conversation or lane | yes | task tickets, routing, state, owner, result intake | canonical task state |
| Department conversation | yes, sparse | repeated responsibility or governance/service lane such as Engineering, Verification, Security, Docs, DevOps | scoped execution or gate |
| Task team | yes, temporary | one long task that needs multiple scoped conversations under one canonical task | scoped multi-conversation execution only |
| Scoped task conversation | yes, temporary | one conversation inside a task team with one local execution slice | no independent canonical authority |
| Short-lived subagent | no | bounded read/review/execution slice | local evidence only |

Tool calls, MCP calls, scripts, and hooks are not conversations. They are
capabilities invoked under a task owner and logged as evidence.

## Worktree Layer

Codex App worktrees map naturally to CoAgent's execution isolation layer.

A worktree answers:

```text
where this task may edit files
which branch/index state it owns
how its changes will be reviewed and merged
```

It does not answer:

```text
what the canonical task goal is
who owns the integrated outcome
whether the result is accepted
how other conversations receive authority
```

Therefore a worktree is attached to a task team, scoped task conversation, or
explicit ephemeral subagent slice, not to an independent agent identity.

V1 rule:

```text
conversation = working surface
worktree = file isolation surface
packet/event log = durable communication and authority
```

Use a separate worktree when:

- the task may produce many file changes,
- Git state must be isolated from the main line,
- a long-running task needs repeated manual review,
- DevOps needs staged integration,
- Verification/Security needs a clean comparison boundary.
- a scoped task conversation needs an isolated file surface.
- a parent conversation authorizes an ephemeral subagent experiment with an
  explicit cleanup rule.

Do not create a separate worktree for:

- a simple answer,
- read-only research,
- a one-file low-risk documentation patch,
- work that has no task id or owner,
- hiding broad edits from review.

Required worktree metadata:

```text
task_id:
owner_conversation:
worktree_path:
branch_or_base:
read_scope:
write_scope:
merge_owner:
review_gate:
close_condition:
```

## Conversation Creation Rule

Create a task team only when at least three conditions hold:

- the work spans multiple turns or manual reviews,
- the task needs stable technical context separate from the main thread,
- user-visible progress matters,
- independent evidence or checkpointing matters,
- one conversation would create too much mixed context or role confusion,
- the team can be closed with result packets and review notes,
- the task has a parent department, task id, context pack, and stop condition,
- keeping it in the main thread would raise context drift or review risk.

Inside one approved task team, create a new scoped task conversation only when:

- it owns one bounded slice,
- it can start from a compact context pack,
- it has a local stop condition,
- it returns one result packet or checkpoint stream,
- it does not redefine the canonical task goal.

Do not create a durable task team for:

- one small question,
- one read-only source slice,
- work that can be represented by one result packet,
- a specialty name that has no recurring queue pressure,
- an attempt to make hidden subagent work look visible.

## Required Packet Flow

Normal durable task:

```text
PMO/main frames request
DispatchCenter creates or updates task packet
target owner receives task packet
owner executes or requests support
owner emits checkpoints when needed
owner emits result packet
Verification/Security/Docs/DevOps gates review when relevant
PMO/main reports integrated result
```

Task team:

```text
task packet
  -> task-team registration
  -> one or more scoped context packs
  -> one or more conversation linked events
  -> per-conversation checkpoints
  -> per-conversation result packets
  -> review/import
  -> task-team integration result
  -> conversation close events
  -> recovery summary
```

Support request:

```text
accountable owner needs support
  -> DispatchCenter records child/support request
  -> support lane returns result packet
  -> accountable owner integrates or escalates
```

Peer-to-peer department chat is not the source of truth in V1. Multiple
conversations inside one task team may exist, but they still communicate
through recorded packets, checkpoints, review notes, and task state.

## Context Pack Rule

Every scoped task conversation inside a task team starts from a compact context
pack.

It must include:

- task id,
- canonical task goal,
- conversation objective,
- accountable owner,
- definition of done,
- non-goals,
- read/write scope,
- required evidence,
- appetite and circuit breaker,
- checkpoint plan,
- escalation conditions,
- relevant decisions and evidence paths,
- forbidden actions,
- expected result-packet path and format.

It must not include:

- raw full transcript,
- private Codex App databases,
- account cache material,
- credentials or tokens,
- browser/session state,
- unrelated old tasks,
- large source dumps,
- unreviewed speculative memory.

If a context pack cannot be made compact and sufficient, that scoped
conversation is not ready for execution. Mark the slice `disordered_task`,
`complex_task`, or `input_required` instead of forcing one overloaded thread.

## State And Review Rule

Every durable task must be recoverable from:

- task packet,
- event log,
- latest checkpoint,
- evidence paths,
- result packet,
- review metadata,
- ledger/status-board row.

Terminal task state requires one of:

- `completed` with accepted evidence,
- `rejected` with reason,
- `failed` with evidence,
- `blocked` with blocker and next unblock condition,
- `superseded` with replacement task or decision,
- `canceled` with reason.

`done_with_concerns` remains a runtime alias, but design documents should use
`review_required` until acceptance is explicit.

## V1 Non-Goals

Do not implement or approve the following under `COAGENT-DESIGN-08`:

- new permanent departments,
- department-internal durable agent swarms,
- peer-to-peer worker communication as durable authority,
- app-server transport,
- unattended write automation,
- automatic Codex App state surgery,
- automatic Git/release actions,
- broad runtime schema migration.

## Acceptance

`COAGENT-DESIGN-08` is complete when the following documents exist and reference
one coherent model:

- `CoAgent/docs/architecture/coagent_agent_design_protocol.md`
- `CoAgent/protocol/conversation_protocol.md`
- `CoAgent/context/context_pack_contract.md`
- `CoAgent/dispatch/communication_contract.md`

The documents must answer:

- which goal layer owns what,
- when a conversation is created,
- what context a new conversation receives,
- how task/checkpoint/result communication flows,
- what workers may and may not do,
- how review and acceptance are represented,
- what remains gated for later implementation.

## Next Implementation Gate

The next implementation item should not expand automation or transport first.
It should prove one minimal protocol-conformant lifecycle against the current
file/CLI transport path, or add a small doctor check that detects protocol
violations in existing task/context/result packets.
