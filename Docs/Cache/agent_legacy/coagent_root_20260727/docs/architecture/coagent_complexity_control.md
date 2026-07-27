# CoAgent Complexity Control

Date: 2026-05-28

Status: approved V1 boundary source for `COAGENT-IMPL-01`; runtime expansion
outside the protocol freeze remains gated.

## Purpose

CoAgent can become unmanageable if enterprise structure is translated directly
into many persistent agents, nested goals, and peer-to-peer chat.

This document defines the complexity limits for the first implementation
phases.

The rule is:

```text
centralized first, limited distribution later.
```

## Complexity Risks

The risky areas are:

- too many durable conversations,
- multiple goal layers that drift apart,
- departments spawning internal agents without ownership,
- raw transcript copying causing context bloat,
- hidden peer-to-peer communication,
- unclear distinction between subagent and dedicated conversation,
- hooks, skills, MCPs, memory, and runtime all changing at once,
- accepting work because a chat says it is done rather than because evidence
  exists.

These risks compound. A design that is individually reasonable at each layer
can still fail as a system.

## Version Boundaries

### V0: Design And Manual Operation

Allowed:

- enterprise-to-agent mapping,
- task intake rules,
- documentation and review briefs,
- manual visible conversation tests,
- read-only research,
- design gate validation.

Forbidden:

- runtime expansion,
- automatic new conversation creation,
- unattended task execution,
- schema migration,
- app-server transport dependency,
- broad hook rewrites.

### V1: Minimal Centralized Control Plane

Allowed after approval:

- canonical task-state and intake vocabulary,
- task packet / result packet schemas,
- one owner per task,
- DispatchCenter-mediated routing,
- context packs for dedicated task conversations,
- one small visible communication lifecycle,
- one dedicated long-task lifecycle.

Forbidden in V1:

- department-internal durable agent swarms,
- peer-to-peer department communication as source of truth,
- multiple active canonical goals for one task,
- automatic Git/release actions,
- long-running autonomous loops without checkpoint and review.

The protocol form of this boundary is recorded in
`CoAgent/protocol/README.md`. If implementation behavior conflicts with this
document, stop and update the protocol or decision record before continuing.

### V2: Controlled Distribution

Allowed only after V1 evidence:

- department-owned child tasks,
- limited durable task conversations under parent departments,
- scheduled dry-run automation,
- richer result routing,
- replay/recovery experiments,
- transport improvements.

Still forbidden:

- autonomous cross-department goal changes,
- unreviewed destructive actions,
- secret/account-state handling in project files,
- uncontrolled conversation spawning.

### V3: Advanced Agent Organization

Only consider after repeated real task pressure:

- department-local dispatchers,
- parallel specialist task conversations,
- partial peer coordination through recorded packets,
- automatic task suggestion from recurring audits,
- productivity/recovery dashboards.

V3 is not a near-term target.

## Goal Control

Only DispatchCenter owns the canonical durable task goal.

Other layers receive scoped objectives:

```text
Project Goal: stable direction
Canonical Task Goal: official task objective
Conversation Objective: scoped work order
Subagent Objective: local disposable question
```

Rules:

- one task has one canonical goal,
- conversation objectives must reference the canonical task id,
- subagent objectives must be smaller than the parent objective,
- goal changes require an event and decision record,
- a worker that finds goal drift must escalate rather than continue.

## Conversation Creation Budget

Creating a new durable conversation has a cost. It adds state, context,
recovery, and synchronization burden.

Create a durable conversation only when the task needs at least three of:

- multi-turn technical continuity,
- user-visible progress,
- independent review or checkpointing,
- dedicated context that would pollute the main thread,
- recovery across sessions,
- high-risk work that should not be hidden in a subagent,
- repeated work under the same parent task.

Use a short-lived subagent when the task is:

- read-only or low-risk,
- bounded to one source slice,
- summarizable into a result,
- cheap to retry,
- not requiring visible continuity.

## Nesting Limit

V1 maximum nesting:

```text
PMO/main
  -> DispatchCenter
    -> department or dedicated task conversation
      -> short-lived subagent
```

Do not allow this in V1:

```text
department conversation
  -> durable child conversation
    -> durable grandchild conversation
      -> subagents
```

If a task appears to need deeper nesting, the correct action is to stop and
write a design note.

## Context Budget Rule

Context should be enough to preserve intent, not enough to reproduce every
conversation.

Each context pack should include:

- canonical task goal,
- definition of done,
- non-goals,
- read/write scope,
- key decisions,
- current evidence links,
- open questions,
- stop conditions,
- required output format.

It should not include:

- full raw transcript,
- unrelated prior tasks,
- large reference dumps,
- duplicate docs,
- secrets or account cache material.

If the context pack becomes large, split it into:

- required brief,
- optional evidence index,
- retrieval queries,
- artifact paths.

## Communication Control

Allowed durable communication units:

- task packet,
- context pack,
- checkpoint packet,
- result packet,
- review note,
- event log entry,
- after-action review.

Plain chat can explain or discuss, but it is not the system of record for
handoff, ownership, acceptance, or goal change.

## Stop Conditions

Stop and escalate when:

- the goal is ambiguous,
- the current task class is wrong,
- context is too large to trust,
- a worker needs to create another durable worker,
- two conversations disagree on ownership,
- evidence contradicts the current plan,
- the task crosses a safety, Git, path, credential, or account boundary,
- the appetite or checkpoint interval is exceeded.

The system should prefer an early stop with evidence over a late completion of
the wrong task.

## Minimal First Closed Loop

The first implementation proof should be small:

```text
PMO states a clear task
DispatchCenter creates task packet
one department receives scoped objective
department returns result packet
Verification or PMO accepts with evidence
Documentation records only durable lesson if needed
```

No internal department swarm is needed for this proof.

## Expansion Rule

Add complexity only when a real repeated failure justifies it.

Examples:

- repeated Git bottlenecks justify stronger DevOps workflow,
- repeated context loss justifies better context packs,
- repeated verification delay justifies verification queue improvements,
- repeated architecture drift justifies stronger design review gates.

Do not add a mechanism because it is impressive. Add it because it reduces a
measured failure mode.

## Current Decision

CoAgent remains in design-gated mode.

These complexity limits should be treated as constraints for the first runtime
implementation after approval.
