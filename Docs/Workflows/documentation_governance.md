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
| current operating state | `Docs/Workflows/mainline_operations_board.md` | next action and blocker only |
| repeatable procedure | `Docs/Workflows/` | executable steps, stop triggers, evidence |
| task-family tool procedure | `Docs/Skills/` | when to load, tool sequence, forbidden actions |
| architecture / algorithm / interface design | `Docs/Design/` | stable design, not runtime status |
| routing/index/reference table | `Docs/Index/` | pointer only; index does not grant permission |
| migration note, review cache, old research, archive body | `Docs/Cache/` | not startup context |
| deterministic helper/checker | `Scripts/` | enforceable behavior belongs in code/tests |
| generated evidence and outputs | `Results/` | proof, logs, packets, figures, manifests |

If a document is not meant to be loaded during normal work, put it under
`Docs/Cache/` or make the active file a short redirect stub.

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
| architecture-changing task | write or update design first, then ask before broad change |
| blocked task | report exact blocker and required decision |

Stop and ask the user before:

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
