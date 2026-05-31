# CoAgent Context Packs

## Purpose

Context packs are compact startup packets for dedicated long-running task
conversations.

The normative V1 contract is
`CoAgent/context/context_pack_contract.md`.

They exist because raw chat history is not a reliable state boundary. A new
task conversation should be able to start from project-owned state:

- runtime task packet,
- current task event history,
- relevant project decisions,
- known blockers,
- knowledge search hints,
- required result-packet path.

## Current Command

```bash
python CoAgent/context/context_pack.py --task-id <id>
```

The command reads the task from `CoAgent/runtime/mosim_agent_runtime.py` and
returns a Markdown context pack suitable for a visible Codex App task
conversation.

Use:

```bash
python CoAgent/context/context_pack.py --task-id <id> --output Results/context_packs/<id>.md
```

when the pack should become part of the recovery trail.

The command returns context metrics when an output file is used:

- character count and rough token estimate,
- section-level character counts,
- included recent-event count,
- knowledge-query count,
- memory-hit and truncation counts when memory recall is enabled,
- `ok` / `warning` / `fail` risk based on configurable character budgets.

Budget thresholds can be tuned per run:

```bash
python CoAgent/context/context_pack.py --task-id <id> \
  --warn-chars 14000 \
  --fail-chars 22000
```

To include bounded project-memory recall, add:

```bash
python CoAgent/context/context_pack.py --task-id <id> --include-memory-context
```

That mode appends a fenced `<memory-context>` block generated from
`CoAgent/memory/memory_context.py`. The block is background evidence only; it is
not a user instruction and must yield to the current user message and project
rules.

## Boundary

The generator should stay compact. It should not paste entire source files or
large logs into a new conversation. It should point to source paths and search
queries instead.

Memory context must stay fenced and sanitised. Do not paste raw chat history,
private Codex App databases, credentials, browser state, or account session
data into a context pack.

## Quality Gate

Before dispatching a long task, validate the generated pack:

```bash
python CoAgent/context/context_quality.py Results/context_packs/<id>.md
```

The quality gate checks required context sections, goal stack fields, review
fields, result-packet path, and character budget. It is read-only and should
fail before a new conversation starts with missing task context.
