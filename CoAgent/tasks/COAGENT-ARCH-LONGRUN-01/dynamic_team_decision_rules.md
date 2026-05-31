# COAGENT-ARCH-LONGRUN-01 Dynamic Team Decision Rules

Date: 2026-05-30
Status: phase 2 draft

## Purpose

Define how CoAgent decides the number and type of execution surfaces for one
user task.

The central rule:

```text
The task chooses the team shape. The department chart does not choose it.
```

## Decision Inputs

Before creating any scoped conversation, Dispatch must have:

- canonical task goal;
- task intake class and proof path when the task is not ordinary/small;
- task appetite;
- non-goals;
- first checkpoint;
- acceptance evidence;
- read/write scope;
- review owner;
- integration owner;
- context pack path;
- result packet path;
- close condition.

If any of these are missing, stay in main thread or return `decision_required`.

Task intake classes and proof-path selection are defined in:

```text
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/task_intake_to_proof_ladder_decision_table.md
```

The topology selector must not bypass that table for PX4 parameter work, UE
scene truth, Git-heavy work, auth/license interruption, or CoAgent
architecture-mechanics proofs.

## Topology Selector

### Use Main Thread Only

Use when all are true:

- task is small;
- no durable handoff is needed;
- context fits comfortably;
- no independent review lane is required;
- no file isolation is needed;
- user can audit the result from the main response and changed files.

Examples:

- answer a direct design question;
- inspect one file;
- update one small documentation paragraph.

### Use Main Thread Plus Short-Lived Subagents

Use when:

- the main owner remains clear;
- sub-work is bounded and one-shot;
- subagent output can be returned as evidence;
- no follow-up memory, Git ownership, or task queue is needed.

Good subagent tasks:

- read-only comparison of a few source files;
- independent review of one design doc;
- search for examples in one reference repo;
- run a bounded static check.

Bad subagent tasks:

- Git integration;
- long test campaign;
- ongoing documentation ownership;
- safety supervision;
- multi-turn implementation;
- anything requiring user-visible progress over time.

### Use One Scoped Conversation

Use when:

- the task is long enough to need its own context history;
- one owner can complete it end to end;
- work does not need independent parallel slices;
- a context pack can fit the whole task;
- result and closeout are clear.

Examples:

- one focused design document;
- one isolated MCP capability investigation;
- one bounded algorithm prototype with known input/output.

### Use A Dynamic Task Team

Use when at least three are true:

- multiple independent slices can make real progress in parallel;
- context would overload one conversation;
- different slices need different tools or expertise;
- independent review is required;
- different blockers are likely;
- file write scopes differ;
- one slice should not inherit another slice's assumptions;
- the task is expected to last multiple hours or require manual review.

Examples:

- PX4 log parameter identification;
- UE scene truth and navigation simulation;
- large Git rename/import cleanup;
- multi-layer architecture redesign.

### Use A Review Board

Use when:

- the decision changes architecture or safety boundaries;
- result correctness is not directly proven by tests;
- multiple departments have legitimate veto power;
- the cost of a wrong decision is high.

Review board members are selected by risk, not by department seniority.

### Use Incident Response

Use when:

- Codex session state is inconsistent;
- MCP/tool repeatedly fails;
- Git index/worktree state is unsafe;
- activation/license/login blocks execution;
- a worker repeats the same wrong assumption;
- a command may have partially executed during interruption.

Incident response suspends normal feature/design work until the safe state is
recorded.

## Spawn Criteria For Scoped Conversations

Create a scoped conversation only if:

1. it owns one named slice;
2. the slice has a distinct context shard;
3. the slice has a local stop condition;
4. the result can be represented by a packet;
5. it does not change the canonical goal;
6. it can close cleanly;
7. integration owner is known.

## Do Not Spawn When

Do not create a new conversation when:

- the owner is unclear;
- the only goal is to look parallel;
- the work is mostly sequential;
- two conversations would edit the same files without merge plan;
- no context pack exists;
- no result packet path exists;
- no one will review the result;
- the task is in an incident state.

## Task-Team Size Rules

Start with:

```text
1 PMO surface
1 Dispatch surface
1 integration owner
1-3 scoped execution conversations
0-1 independent review lane
```

Expand only when:

- the critical path has a real parallel branch;
- the current conversations are blocked on different dependencies;
- a slice requires a different context or tool boundary;
- review independence is necessary.

Shrink when:

- a slice finishes;
- two slices require constant negotiation;
- context deltas exceed refresh budget;
- handoff failures increase;
- the work becomes sequential again.

## Goal Ownership

Canonical task goal owner:

```text
DispatchAgent, accepted by MainAgent/user
```

Scoped conversation owner may only adjust:

- local approach;
- local evidence;
- local stop condition;
- proposed scope change.

If a worker believes the canonical goal is wrong, it must emit:

```text
decision_required
```

with:

- evidence;
- proposed revised goal;
- risk of continuing;
- what work should stop until the decision.

## Conversation Close Criteria

A scoped conversation can close only after:

- result packet exists;
- review disposition exists or waiver is recorded;
- context delta is accepted or rejected;
- worktree is merged, discarded, or archived;
- mailbox items are closed;
- final state is recorded on the shared task board.

## Anti-Patterns

- Permanent department count equals conversation count.
- Every task creates all 11 departments.
- Dispatch writes implementation code as hidden worker.
- A task-scoped conversation turns into a new permanent department.
- Raw chat is used as the only handoff.
- Peer conversations change each other's scope without coordinator-visible
  packet records.
- A worktree becomes the de facto source of task authority.
