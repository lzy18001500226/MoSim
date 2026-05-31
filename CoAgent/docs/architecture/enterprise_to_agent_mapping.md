# Enterprise To Agent Mapping

Date: 2026-05-28

Status: approved mapping source for `COAGENT-IMPL-01`; runtime expansion
outside the protocol freeze remains gated.

## Purpose

This document maps the technical-enterprise operating model into CoAgent's
agent system design.

The enterprise model answers how a technical organization should operate. This
document answers what each enterprise concept becomes when implemented with
Codex conversations, task packets, context packs, skills, hooks, memory, and
MCP tools.

## Core Translation Rule

Do not translate the enterprise model literally into more agents.

Translate it into controlled responsibilities, durable state, explicit
communication, and bounded context.

```text
enterprise responsibility
  -> CoAgent responsibility lane
  -> task packet / context pack / result packet
  -> visible conversation only when durable continuity is needed
  -> short-lived subagent only when the work is bounded and disposable
```

The goal is task completion with evidence, not organizational simulation.

## Mapping Table

| Enterprise concept | CoAgent construct | Durable truth | Notes |
|---|---|---|---|
| Company mission | Project goal | roadmap docs, PMO summaries | Stable, broad direction such as MoSim simulation platform |
| Strategic objective | Breakthrough objective | design docs, task ledger | Few active objectives; used to reject low-value work |
| Department | Visible department conversation or logical owner lane | department registry, task ledger | Durable only when repeated responsibility justifies cost |
| Manager / DRI | Accountable owner | task packet, ledger | One owner for integrated outcome |
| Worker | Department conversation, task-team conversation, or subagent | result packet if durable | Worker type depends on context and duration |
| Project team / task team | One or more scoped task conversations under a parent department and one canonical task | context packs, task packet, checkpoints, review notes | Used for long high-context tasks that need more than one visible execution surface |
| Meeting | Checkpoint packet or review note | event log, result packet | Chat is UI; packet is the durable artifact |
| Status report | Checkpoint / result packet | task ledger, result archive | Must contain evidence, blocker, next step |
| Policy | Hook / preflight / AGENTS rule | code/config/docs | Enforced; not optional skill text |
| Procedure | Skill | `SKILL.md`, docs | Loaded selectively when relevant |
| Tooling | MCP / shell / project scripts | tool config, evidence logs | Capability surface, not authority |
| Knowledge base | Docs, indexes, summaries | `CoAgent/learning/`, `Docs/`, `Results/` | Retrieved by source, not pasted wholesale |
| Audit / QA | Verification lane and review gate | test output, evidence path | Independent from implementer |
| Security / compliance | Security lane and hard gates | preflight, review notes | Can block or require human approval |
| Release management | DevOps lane | Git state, release notes | Separate because state is high-risk |
| Postmortem | After-action review | audit, skill, hook, docs update | Converts failures into system changes |

## Goal Hierarchy

This hierarchy is now canonical for the V1 protocol. The same terms appear in
`CoAgent/protocol/README.md`, `CoAgent/protocol/task_packet_schema.json`, and
`CoAgent/protocol/result_packet_schema.json`.

CoAgent must not allow every layer to freely set its own independent goal.
That would create drift.

Use four goal levels:

| Level | Owner | Meaning | May change task goal? |
|---|---|---|---:|
| Project Goal | User + PMO | Long-term MoSim direction | No, only frames priorities |
| Canonical Task Goal | DispatchCenter | The one official goal for a durable task | Yes, with user/PMO record |
| Conversation Objective | Department, task-team conversation, or scoped task conversation | Scoped work order for this conversation | No, may request change |
| Subagent Objective | Parent conversation | One-shot local question | No, must return evidence |

The canonical task goal lives in the task packet and task ledger. Department
and task conversations may have scoped objectives, but they do not redefine the
canonical task goal.

If a worker finds that the goal is wrong, it escalates with evidence. It does
not silently rewrite the task.

## Department And Internal Agent Pattern

Departments are durable responsibility lanes, not containers that freely spawn
unbounded autonomous systems.

First version pattern:

```text
PMO / main
  -> DispatchCenter
    -> one accountable department or task team
      -> one or more scoped task conversations
        -> optional short-lived subagent for bounded local work
```

Do not start with this pattern:

```text
department
  -> many durable internal conversations
    -> peer-to-peer agent communication
      -> independent goals
```

Task-team conversations under one accountable task are allowed only when all are true:

- the task is long-running,
- the context must be visible to the user,
- the work has a parent task id,
- the parent department remains accountable,
- the new conversation has a context pack and stop condition,
- there is a result packet path and review gate.

## Communication Topology

Communication should be hub-and-spoke first.

```text
PMO <-> DispatchCenter <-> Department / task team
```

Peer-to-peer communication between department conversations is not the default.
If two departments need to coordinate, the coordination should be represented
as one of:

- DispatchCenter creates a child task,
- the accountable owner requests a supporting result packet,
- PMO escalates a decision point,
- a review gate records acceptance or rejection.

This prevents hidden side conversations from becoming untracked authority.
Task teams may contain multiple visible conversations, but those conversations
must still communicate through recorded packets, checkpoints, review notes, and
task state rather than informal peer authority.

## Context Hierarchy

New conversations must not receive raw full chat history by default.

Use layered context:

| Context layer | Contents | Loaded by default? |
|---|---|---:|
| Mission Context | project goal, user constraints, current strategic objective | yes, compact |
| Department Context | department role, allowed tools, current relevant policy | yes, compact |
| Task Context | objective, scope, DoD, evidence, stop condition, risks | yes |
| Evidence Context | source snippets, files, logs, search results | selective |
| Working Context | local scratch, failed attempts, intermediate reasoning | no; summarize only if useful |

The context pack should be enough to prevent drift, but small enough to avoid
model capability degradation from irrelevant context.

## Context Promotion Rule

Only promote information into durable context when it changes future behavior.

Promote:

- user decisions,
- accepted architecture decisions,
- task outcomes with evidence,
- repeated failure modes,
- reusable procedures,
- source-linked research conclusions.

Do not promote:

- raw exploratory chatter,
- irrelevant tool output,
- duplicate summaries,
- speculative ideas with no current trigger,
- secrets, account state, or private credentials.

## Agent Type Selection

| Need | Use | Reason |
|---|---|---|
| One direct answer | Main conversation | No durable state needed |
| Small bounded file/task analysis | Short-lived subagent or direct work | Cheap context isolation |
| Repeated responsibility | Department conversation | Stable owner lane |
| Long high-context technical task | Task team with one or more scoped task conversations | Visible continuity, recovery, and bounded cross-conversation coordination |
| Safety/release/test gate | Security, DevOps, or Verification lane | Independent review |
| Enforced rule | Hook/preflight | Must not depend on model choice |
| Repeatable procedure | Skill | Load only when relevant |

The default should be the lightest construct that preserves correctness,
evidence, and recovery.

## Authority Boundaries

| Decision | Authority |
|---|---|
| Change project direction | User + PMO |
| Change canonical task goal | PMO / DispatchCenter with record |
| Assign task owner | DispatchCenter |
| Choose local execution tactic | Accountable owner |
| Accept implementation evidence | Verification or PMO, depending risk |
| Block unsafe action | Security / hook / policy |
| Commit or release | DevOps |
| Promote durable knowledge | Documentation / PMO review |

Workers can recommend authority changes. They do not self-approve them.

## Failure Modes This Mapping Must Prevent

- A department creates internal durable agents without task ownership.
- Multiple conversations believe they each own the same task goal.
- A task-team conversation starts from raw transcript and drifts.
- A short-lived subagent performs work that should have been visible and
  reviewable.
- Context grows until the model becomes less reliable.
- A worker changes the goal instead of escalating evidence.
- Peer-to-peer chat becomes hidden authority outside the task ledger.

## Design Consequence

CoAgent should first implement a small, centralized, auditable control plane.

Distributed agent behavior can be added later only when the task packet,
context pack, result packet, event log, review gate, and recovery path have
already worked on real tasks.
