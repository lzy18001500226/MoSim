# CoAgent

MoSim's project-owned agent-system workspace.

This directory is not a third-party runtime copy. It holds the architecture,
decision records, bounded research, protocol/runtime modules, tests, and
health checks for MoSim's task-first multi-conversation agent system.

## Start Here

Read these first in a new conversation:

1. `CoAgent/STATUS.md`
2. `CoAgent/docs/README.md`
3. `CoAgent/docs/architecture/coagent_architecture_issue_register.md`
4. `CoAgent/docs/architecture/coagent_problem_driven_operating_model.md`
5. `CoAgent/docs/architecture/COMPONENT_MAP.md`

Do not infer the current CoAgent direction from old chat history alone.

## Current Gate

The first implementation checkpoint is complete through `COAGENT-IMPL-08`.
Current design work is still resolving the task-first, multi-conversation
architecture. Later app-server transport, unattended automation, new permanent
departments, broad hook rewrites, tool/MCP expansion, and durable internal
agent swarms remain gated.

Gate anchors:

```text
decision_record: CoAgent/docs/decisions/coagent_design_decision_record.md
review_entry: CoAgent/docs/decisions/coagent_design_review_brief.zh.md
implementation_allowed: true
first_allowed_task: COAGENT-IMPL-01
```

## Directory Map

| Path | Purpose |
|---|---|
| `docs/` | Human-facing architecture, decision, research, and status documents |
| `learning/` | Structured audit database and learning indexer only |
| `runtime/` | Local task queue, event stream, and conversation graph seed |
| `protocol/` | Task/result packet schemas and conversation protocol |
| `context/` | Context-pack generation and contract |
| `dispatch/` | Conversation registry, task dispatch text, transport-facing helpers |
| `transport/` | Visible-conversation transport adapter boundary |
| `result_router/` | Result packet validation, review gate, import, archive, summary |
| `bootstrap/` | Long-task handoff and recovery helpers |
| `memory/` | Fenced project-memory recall used as background evidence |
| `knowledge/` | Project-owned source index and search |
| `hooks/` | Preflight and safety guardrails |
| `automation/` | Guarded automation definitions and runner |
| `doctor/` | Recoverability and protocol health checks |
| `tests/` | CoAgent smoke and unit tests |

## Document Map

Use `CoAgent/docs/README.md` for the detailed document map. The short version:

- `docs/architecture/` is for system design and unresolved architecture issues.
- `docs/decisions/` is for approvals, backlogs, review briefs, and completion audits.
- `docs/research/` is for external-source learning strategy and source indexes.
- `docs/status/` is for migration/status snapshots.
- `learning/audits/` is the structured source-to-decision audit corpus.

## Validation

Run the smallest useful checks after restructuring or editing CoAgent docs:

```bash
python3 CoAgent/learning/learning_indexer.py validate --strict
python3 CoAgent/doctor/check_design_gate.py
python3 CoAgent/tests/test_design_surface_docs.py
git diff --check -- CoAgent
```

Use the full doctor when runtime health also matters:

```bash
python3 CoAgent/doctor/coagent_doctor.py
```
