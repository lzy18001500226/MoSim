# CoAgent Task Surface Model V1

Date: 2026-05-28

Status: design baseline. This does not approve app-server transport,
automatic worktree provisioning, unattended automation, or new permanent
department implementation.

Task id: `COAGENT-DESIGN-09`

## Purpose

This document defines where a task lives while it is being executed.

CoAgent already defines:

- who owns the goal,
- how packets move,
- how context is packed,
- how departments and subagents differ.

This document closes the next design gap:

```text
which work surface should carry the task
which file-isolation surface should carry the edits
which review surface should accept the outcome
```

The point is to stop ambiguous execution layouts such as:

- a long task with no dedicated work surface,
- a large edit stream in the shared main workspace,
- a reviewer working in the same mutable surface as the implementer,
- a task that has a worktree but no accountable owner,
- a visible conversation that looks authoritative but has no packet or review gate.

For the complete multi-conversation team model, also read
`CoAgent/docs/architecture/coagent_task_team_architecture.md`.

## Surface Vocabulary

CoAgent V1 uses five surface types:

| Surface | Meaning | Durable? | Owns authority? |
|---|---|---:|---:|
| Task surface | The conversation/lane where task progress is executed and discussed | yes or no | only when backed by task packet and state |
| File surface | The workspace or worktree where files are edited | yes | no |
| Review surface | The lane that accepts, rejects, or requests changes | yes | yes for review outcome only |
| Packet surface | The task/checkpoint/result/review artifact path | yes | yes |
| State surface | Runtime queue, ledger, event log, status board | yes | yes |

Rule:

```text
conversation shows work
worktree isolates edits
review lane accepts or rejects
packet records the handoff
runtime state records the truth
```

## Canonical Surface Tuple

Every durable task should be representable as this tuple:

```text
task_id
canonical_task_goal
accountable_owner
owner_conversation
task_surface_class
file_surface_class
review_owner
packet_paths
state_paths
close_condition
```

If one element is unknown, the task is not fully shaped yet.

## Task Surface Classes

### 1. Main-Thread Task

Use when:

- the task is short,
- continuity is low,
- user dialogue and execution can stay together,
- no heavy Git isolation is needed.

Characteristics:

- owner conversation is `MoSim｜主线总控`,
- no dedicated task conversation,
- file surface is usually the main workspace,
- result may still need a result packet if the task is durable.

### 2. Department Task

Use when:

- the responsibility is recurrent,
- the task belongs to one standing lane,
- user visibility matters,
- the task does not justify its own dedicated conversation.

Characteristics:

- owner conversation is one department thread,
- file surface may be main workspace or department worktree,
- review often happens in another lane.

### 3. Task Team

Use when:

- the task is long-running,
- one conversation would mix too many subproblems,
- multiple scoped conversations need shared context,
- checkpoints and review are expected,
- the task has one parent department and one canonical task goal.

Characteristics:

- one parent task team under one canonical task,
- one or more scoped visible conversations,
- shared team-level context rules plus per-conversation context packs,
- result packets from each scoped conversation,
- one integrated team-level closeout.
- optional worktree strategy across task, review, integration, and ephemeral
  subagent worktrees.

### 4. Scoped Task Conversation

Use when:

- the task team needs one bounded execution slice,
- technical context for that slice must stay separate,
- the slice has its own stop condition,
- the slice returns its own result packet or checkpoint stream.

Characteristics:

- one dedicated visible conversation,
- one scoped context pack,
- result packet required,
- local close condition required,
- file surface may be main workspace or a dedicated task worktree.

### 5. One-Shot Subagent Slice

Use when:

- the work is bounded,
- the result can be summarized immediately,
- no durable visibility is needed.

Characteristics:

- no durable conversation identity,
- no independent file surface by default,
- optional ephemeral worktree only when the parent conversation owns cleanup,
- parent task surface remains accountable.

## File Surface Classes

### 1. Shared Main Workspace

Use when:

- the task is small,
- write scope is narrow,
- conflict risk is low,
- rollback is easy,
- no parallel large edit stream exists.

### 2. Dedicated Task Worktree

Use when:

- the task may generate many file changes,
- the task will run over many turns,
- isolated Git status is required,
- manual review needs a clean branch/diff boundary.

### 3. Review Worktree

Use when:

- verification or security needs clean reproduction,
- the reviewer must inspect a branch without inheriting unrelated mutable state,
- DevOps needs controlled merge preparation.

This worktree is ideally read-mostly.

### 4. Integration Worktree

Use when:

- DevOps is batching reviewed changes,
- multiple accepted task branches must be staged,
- the merge owner must control the final Git surface.

## Default Mapping By Task Class

| Task class | Default task surface | Default file surface | Review surface |
|---|---|---|---|
| `simple_message` | current main conversation | none | none |
| `clear_task` | main or department lane | main workspace | PMO or direct check |
| `complicated_task` | department lane | main workspace or dedicated worktree | verification/docs/security as needed |
| `complex_task` | main or department discovery lane first | usually no dedicated worktree until task is shaped | PMO checkpoint before delivery |
| `chaotic_incident` | stabilization lane | frozen/minimal write surface until stable | PMO/security/DevOps |
| `disordered_task` | PMO/DispatchCenter | none until shaped | PMO |
| `long_running_task` | task team with one or more scoped task conversations, or stable department lane | dedicated worktree if writes are material | explicit review owner required |

## Binding Rules

### Conversation Binding

- One durable task has one accountable owner at a time.
- A durable task may have one owner conversation or one task team.
- A durable task may also use an operating department as sponsor or gate.
- A task team may have multiple scoped task conversations.
- Department conversations do not become peer authorities just because they are
  visible in Codex App.

Within one task team:

- all scoped task conversations share one canonical task goal,
- each scoped task conversation has its own local objective,
- DispatchCenter or the accountable owner must maintain the team-level routing,
- cross-conversation coordination must be recoverable from packets or review notes.

### Worktree Binding

- A task may have zero or one active writable worktree in V1.
- If the task has a writable worktree, the packet must record:
  `worktree_path`, `branch_or_base`, `merge_owner`, `close_condition`.
- A review worktree may exist separately, but it must not silently become the
  writer's active task worktree.
- A worktree never implies authority to change scope or goal.

### Review Binding

- Every durable task has at most one review owner at a time.
- Multiple reviewers may contribute findings, but one review owner decides the
  acceptance state.
- Merge owner and review owner may be different.
- Close owner may also be different when DispatchCenter is responsible for
  recording final terminal state after review and Git disposition are known.

Use `CoAgent/docs/architecture/coagent_review_merge_protocol.md` for the detailed
review-owner / merge-owner / close-owner contract.

At the task-surface level, closeout metadata should still be visible in compact
form:

```text
review_owner:
merge_owner:
close_owner:
git_disposition:
close_condition:
```

## Recommended Surface Patterns

### Pattern A: Small Docs Fix

```text
task surface: main conversation
file surface: main workspace
review surface: PMO/main
packet weight: low; durable only if task must be recoverable
```

### Pattern B: Department Execution Without Dedicated Thread

```text
task surface: department conversation
file surface: main workspace or department worktree
review surface: verification or docs/security as needed
packet weight: task packet + result packet
```

### Pattern C: Long Technical Stream

```text
task surface: one task team with multiple scoped task conversations
file surface: one or more dedicated task worktrees as needed
review surface: assigned verification/security/docs/DevOps lane
packet weight: task packet + per-slice context packs + checkpoints + per-slice result packets + integration result + review notes
```

### Pattern D: Git Integration

```text
task surface: DevOps lane
file surface: integration worktree
review surface: PMO plus verification/security if relevant
packet weight: result packet with git_status and merge/discard decision
```

## Closeout Rules

A task surface may close only when:

- result packet exists,
- review state is known,
- file surface outcome is known,
- merge/discard decision is recorded when a worktree was used,
- follow-up task is created if needed,
- conversation edge can be closed without losing state.

Review and merge decisions must be recoverable before closeout. Use
`CoAgent/docs/architecture/coagent_review_merge_protocol.md` as the detailed closeout
baseline.

Minimum closeout record:

```text
review_status:
acceptance_state:
git_disposition:
close_owner:
close_condition:
```

A worktree may close only when:

- merge owner is known,
- Git state is summarized,
- remaining untracked/generated artifacts are explained,
- reviewer has accepted or rejected the task outcome.

## Anti-Patterns

Do not allow:

- one visible conversation per tiny specialty,
- one worktree per short answer,
- one long-running task with no review owner,
- one review owner working inside the writer's unisolated mutable surface,
- packet-free “I already told another thread” coordination,
- a worktree with no task id,
- a scoped task conversation that still relies on raw transcript memory,
- a task that keeps one huge shared worktree across unrelated objectives.

## Current V1 Constraints

Still out of scope:

- automatic worktree creation,
- automatic branch naming,
- automatic merge queues,
- app-server-driven thread/worktree orchestration,
- multiple active writable worktrees for one task,
- department-internal durable worker hierarchies,
- peer-to-peer department authority outside DispatchCenter records.

## Next Gate

After this design closes, the next safe design or implementation step should be
one of:

1. a worktree registry and lifecycle note that records creation/closeout without
   mutating Codex private state, or
2. a transport/session-state repair design that makes visible-thread lifecycle
   more reliable, or
3. a reviewer/merge-owner protocol for DevOps integration worktrees.
