# Agent Concept Boundaries

Last updated: 2026-05-27

## Purpose

This document records the current CoAgent vocabulary after the first official
multi-agent learning pass. It is meant to prevent design drift when future
agents discuss skills, hooks, subagents, departments, handoffs, and long-running
task state.

Primary sources are recorded in
`CoAgent/learning/audits/2026-05-27_official_multi_agent_principles_round8.md`.

## Core Rule

CoAgent is not a collection of clever chat prompts.

It is a project-owned control system for long-running work:

```text
user intent
  -> PMO / dispatch decision
  -> task packet
  -> bounded context pack
  -> visible department or short-lived worker
  -> result packet
  -> review gate
  -> durable project state update
```

Codex App and VSCode are useful interaction surfaces. They are not the durable
source of truth.

## Concept Definitions

| Concept | CoAgent meaning | Durable? | Model-selected? | Correct use |
|---|---|---:|---:|---|
| Rule / policy | Always-on project requirement, usually in AGENTS.md, config, hook, or preflight | Yes | No | Path boundaries, safety policy, required evidence, review gates |
| Skill | Selectively loaded procedural package with instructions and optional scripts/templates | Usually file-backed | Yes or explicit | Repeatable workflows, domain procedures, tool recipes |
| Hook | Lifecycle-triggered command, endpoint, or check | Yes | No | Blocking risky actions, validating tool calls, enforcing stop/review behavior |
| Tool | Callable capability exposed to an agent | Runtime-dependent | Yes | File reads, shell commands, MCP tools, APIs |
| MCP | Protocol/server surface exposing tools or context | Runtime-dependent | Yes | UE control, Epic/Fab library visibility, filesystem/git/tool integration |
| Subagent | Bounded worker with separate context | Usually no | Yes or explicit | Search, audit, read-only analysis, narrow implementation slices |
| Agent team / department | Visible durable task conversation with a stable responsibility | Yes | PMO-routed | DevOps, verification, documentation, security, research, long tasks |
| Handoff | Explicit transfer of ownership or execution from one agent to another | Yes when recorded | Model or code routed | Moving a task packet from PMO to a department or specialist |
| Task packet | Structured work order | Yes | No | Defines owner, scope, context, stop condition, evidence, review |
| Result packet | Structured return package | Yes | No | Reports status, files changed, evidence, blockers, next action |
| Context pack | Bounded startup context for a task | Yes | No | Lets a new conversation resume without raw chat memory |
| Memory | Durable project knowledge, decisions, summaries, and indexes | Yes | Retrieval-selected | Reconstructing context across sessions |
| Transcript | Chat history | Evidence only | No | Debugging and recovery, not authoritative task state |

## Skills Versus Hooks

Skills and hooks solve different problems.

Skills are for reusable know-how. They should answer: "When I choose this
workflow, what steps, scripts, examples, and references should I use?"

Hooks are for enforced behavior. They should answer: "What must happen before
or after this lifecycle event, regardless of what the model chooses?"

Correct split:

| Requirement | Use |
|---|---|
| Run UE map-import checklist | Skill |
| Summarize git diff and risk | Skill |
| Load PX4 log parameter-identification workflow | Skill |
| Block destructive shell commands | Hook |
| Prevent writes outside project boundary | Hook / preflight |
| Require human review before deleting large directories | Hook / policy |
| Record task result after worker finishes | Hook or deterministic runtime |
| Check result packet schema | Hook / validation script |

Do not put safety-critical constraints only in skills. A model can fail to load
or obey a skill; a hook should fire because the event happened.

## Skills And Context Budget

Skills should use progressive disclosure:

1. Small metadata tells the model when the skill is relevant.
2. `SKILL.md` contains the normal procedure.
3. Supporting files, examples, and references are loaded only when needed.
4. Large reference corpora remain indexed by path/query rather than injected
   into every conversation.

Bad pattern:

```text
Load every UE, MWORKS, MATLAB, Simulink, Agent, MCP, and reference skill into
every task.
```

Good pattern:

```text
Expose minimal skill names/descriptions.
Load only the selected skill.
Use file paths, indexes, and search queries for deeper context.
Write the consumed result back as a summary or audit.
```

## Subagents Versus Departments

Subagents are disposable context isolation.

Use a subagent when:

- the task is read-heavy,
- outputs can be summarized,
- the worker does not need durable identity,
- the details would pollute the main context,
- failure can be retried cheaply.

Examples:

- inspect a project and classify it,
- compare two official docs,
- search references for one design pattern,
- review one bounded code change.

Departments are durable responsibility boundaries.

Use a visible department conversation when:

- the task is long-running,
- the worker needs continuity across sessions,
- user review may be needed,
- the output affects project history or release state,
- the state must be observable in Codex App.

Examples:

- DevOps/Git department for large rename/commit sequences,
- verification department for repeated simulation/test evidence,
- documentation department for durable knowledge updates,
- security department for boundary and credential review,
- research/engineering department for UE/Fab/MCP/CoAgent architecture studies.

## Agent Team Design Rule

The number of durable department conversations should stay small.

Default departments:

| Department | Responsibility |
|---|---|
| PMO / dispatch | Own task packets, owner assignment, state board, stop conditions, result routing |
| Research/engineering | Investigate architecture, UE/Fab/MCP, controller/planning, and implementation options |
| DevOps/Git | Git status, rename fallout, ignore/LFS, staged commits, release hygiene |
| Verification | Tests, simulation evidence, UE run checks, reproducibility |
| Documentation/knowledge | User instructions, learning records, indexes, summaries |
| Safety/security | Path boundaries, credentials, destructive actions, prompt/tool injection, licensing |

Temporary groups are allowed only when a task justifies the coordination cost:

| Temporary group | Trigger |
|---|---|
| Architecture review | MCP architecture, UE communication, whole-system simulation architecture |
| Technical research | Official docs, papers, high-value open-source systems |
| Incident review | Git explosion, MCP repeated failures, stale context, broken sync |
| Specialized test group | Very large test scope needing separation, such as UE runtime versus simulation validation |

## Handoff Contract

A handoff is not "telling another chat something informally".

A valid CoAgent handoff needs:

```text
task_id:
parent_goal:
source_conversation:
target_owner:
objective:
read_scope:
write_scope:
context_pack:
required_tools:
stop_condition:
review_gate:
result_packet_path:
```

The source conversation should not rely on hidden memory. The target owner must
be able to start from the packet and local project files.

## Long-Running Task Requirements

Every long-running task needs these artifacts before execution:

| Artifact | Purpose |
|---|---|
| task packet | Defines the work and owner |
| context pack | Reconstructs required state without full transcript |
| status entry | Makes progress observable |
| evidence path | Stores logs, screenshots, reports, or command output summaries |
| result packet | Returns status and next action |
| review gate | Defines who must approve continuation/completion |

The worker should not try to finish a large project in one pass. It should make
incremental progress, leave the project in a clean state, and write enough
evidence for the next session.

## Current CoAgent Design Consequences

1. Keep Codex App as UI/review surface, not durable state.
2. Keep PMO/dispatch as the workflow authority.
3. Keep skills small and procedural.
4. Keep hooks/policies responsible for hard constraints.
5. Keep subagents disposable and bounded.
6. Keep department conversations sparse, visible, and task-packet driven.
7. Keep memory in files, indexes, summaries, and artifacts.
8. Prefer synchronous task/result packet flow until async recovery is reliable.
9. Do not import a full third-party multi-agent framework before CoAgent's
   local contracts are stable.

## Open Questions

- What context-pack size works best for MoSim's real tasks?
- Which department boundaries are justified by evidence rather than analogy?
- When should a task become a durable department conversation instead of a
  disposable worker?
- Whether CoAgent needs A2A-compatible transport later.
- Whether Codex App session sync is stable enough for real department handoffs.
