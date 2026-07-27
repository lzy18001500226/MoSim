# Documentation Governance

> Current MoSim rule for document placement, context hygiene, workflow updates,
> and archive boundaries. This replaces legacy agent-OS documentation governance
> for active project work.

## 1. Authority Order

When sources conflict, use this order:

```text
current user instruction
-> AGENTS.md hard boundary
-> native hook/checker/script result
-> current source file, model, result, log, screenshot, or metric
-> current workflow / skill / design / index
-> reviewed cache or migration record
-> memory, old chat, or historical ledger
```

Memory, old chat, and cache are retrieval hints. They do not become project
truth until checked against current files or evidence.

## 2. Where Things Belong

| Content | Location | Rule |
|---|---|---|
| hard project boundary and startup chain | `AGENTS.md` | compact only; no detailed procedure |
| fresh startup context | `Docs/Workflows/new_conversation_context.md` | short, current, no history dump |
| current operating state | `Docs/Workflows/mainline_operations_board.md` | current action, next gate, stopping/handoff condition, and blocker only |
| repeatable procedure | `Docs/Workflows/` | executable steps, stop triggers, evidence |
| task-family tool procedure | `Docs/Skills/` | when to load, tool sequence, forbidden actions |
| architecture / algorithm / interface design | `Docs/Design/` | stable design, not runtime status |
| routing/index/reference table | `Docs/Index/` | pointer only; index does not grant permission |
| migration note, review cache, old research, archive body | `Docs/Cache/` | not startup context |
| deterministic helper/checker | `Scripts/` | enforceable behavior belongs in code/tests |
| generated evidence and outputs | `Results/` | proof, logs, packets, figures, manifests |

If a document is not meant to be loaded during normal work, put it under
`Docs/Cache/` or make the active file a short redirect stub.

An active document may be removed rather than left as a redirect stub when its
historical body is already preserved in `Docs/Cache/`, no current executable or
human-facing path requires the old filename, and all active references have
been updated. Use redirect stubs only for externally referenced paths that
must fail closed during a transition.

## 3. When To Update Docs

Update documentation when a task discovers a reusable fact:

- a command sequence that should be repeated;
- a failure mode and stop condition;
- an evidence requirement;
- an API/tool/MCP usage rule;
- a project structure decision;
- a correction that prevents future wrong execution.

For runtime integration utilities, do not default to hand-written glue when a
standard implementation exists. Before writing or changing project-owned
adapters for frames, point clouds, occupancy maps, timing, logging, codegen, or
controller interfaces, first inspect local upstream examples, installed
ROS/PCL/tf/tf2/PX4/MAVROS/MWORKS tooling, official documentation, open-source
implementations, papers when the issue is algorithmic, and targeted community
notes. Hand-written code is acceptable only when it is a thin compatibility
adapter around the accepted stack, or when no suitable maintained tool exists.
When hand-written code remains in the runtime path, record the external
references considered, the reason for not using them directly, and the bounded
validation that proves the adapter preserves the intended semantics.

Do not update docs just to record ordinary progress. Progress belongs in
`PROGRESS.md`, result files, logs, metrics, or the current board when state
actually changes.

## 4. Workflow Shape

A current workflow should answer:

```text
when to use it
required inputs
allowed actions
forbidden actions
stop triggers
evidence required
commands or tool sequence
output paths
what to do when blocked
```

Avoid long essays, repeated hotfix paragraphs, and old incident history inside
active workflows. Put historical material in `Docs/Cache/`.

## 4.1 Avoid Process Inflation

Do not create a workflow, smoke test, script, model root, task plan, or progress
document merely because ordinary work has started or encountered a routine
failure. Before adding a persistent artifact, identify its reader or executable
consumer, the exact responsibility it owns, and why the existing owner cannot
hold that responsibility.

When a focused inspection stops producing new facts, do not widen the reading
set indefinitely. Select one bounded next action: inspect the owner source,
run a small observable probe, consult targeted official/reference material, use
the documented recovery step, or move to an independent task. Record only the
resulting reusable fact, evidence, or blocker.

Use the canonical model root, profile/configuration path, and result layout for
new experiments. A temporary experiment must not introduce another top-level
package, project root, or permanent process document.

## 4.2 Board Shape

The current board is a short task selector, not an open-ended work queue. Each
current action must state its next executable gate and explicit stopping/handoff
conditions: what proves completion, what becomes a blocker, and which later
gates remain out of scope. Update the board when any of those facts changes.

## 5. Skill Shape

A skill should answer:

```text
trigger condition
minimum context to read
tool sequence
preflight check
forbidden actions
expected artifacts
acceptance or smoke check
common blockers
```

A skill describes how to act. It does not authorize the action by itself.

## 6. Intake And Stop Rules

Before non-trivial work, classify the request:

| Class | Handling |
|---|---|
| small clear task | do it directly with targeted verification |
| unclear task | restate objective and ask or run a small read-only probe |
| runtime/debug task | add logs/checkpoints, inspect source, then run narrow proof |
| architecture-changing task | report the decision and affected boundaries; wait for user confirmation before selecting or changing the architecture, then record the accepted design |
| blocked task | report exact blocker and required decision |

Stop and ask the user before:

- choosing an architecture, interface, or scope boundary not already decided by
  the current board or a design document;
- changing the agreed runtime architecture;
- substituting a different simulator, stack, model, dataset, or source tree;
- deleting/moving large structures;
- touching login/license-sensitive UI;
- making broad/high-risk Git or runtime changes;
- continuing after the relevant source boundary cannot be found.

## 7. Legacy Agent-OS Migration Rule

Legacy agent-OS content is being internalized into MoSim project paths.

Current rules:

- useful current material moves into `Docs/`, `Scripts/`, `Config`, or
  `Results/`;
- legacy workflow bodies stay in `Docs/Cache/agent_legacy/legacy_workflows_20260624/`;
- active `Docs/Workflows/` files may remain as short redirect stubs;
- active hooks, protocol templates, capability index, desktop skills, and
  reference index now use MoSim-owned paths under `Scripts/`, `Config/`,
  `Docs/Skills/`, and `Docs/Index/`;
- remaining executable legacy runtime/gateway/checker code is not moved or
  deleted until a dependency audit updates all references;
- no new active workflow should point to retired agent-OS internals as source
  of truth.

Migration plan:

```text
Docs/Cache/agent_legacy/coagent_internalization_migration_plan_20260624.md
```

## 8. Completion Check

A documentation cleanup is complete only when:

- the active startup chain stays short;
- indexes point to the owning workflow, skill, design, checker, or cache;
- old rules moved to cache do not silently remain active;
- useful legacy material has a MoSim-owned landing path;
- `git diff --check` passes for touched docs;
- no runtime or engineering success is claimed from documentation changes.
