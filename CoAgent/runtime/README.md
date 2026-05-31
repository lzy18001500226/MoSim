# CoAgent Runtime

## Purpose

This directory contains MoSim-owned agent runtime code.

Rule:

- agent-specific runtime implementation belongs here,
- `Scripts/` keeps project task scripts, checks, exporters, and compatibility
  launchers,
- `Scripts/agent/` should not remain the long-term home of core CoAgent logic.

## Current Components

| File | Purpose |
|---|---|
| `mosim_agent_runtime.py` | durable queue, event stream, and conversation-graph runtime seed |

## Current Commands

```bash
python CoAgent/runtime/mosim_agent_runtime.py create ...
python CoAgent/runtime/mosim_agent_runtime.py claim ...
python CoAgent/runtime/mosim_agent_runtime.py checkpoint ...
python CoAgent/runtime/mosim_agent_runtime.py update-metadata \
  --task-id <id> \
  --actor <owner> \
  --claim-token <token-if-claimed> \
  --summary "record files, commands, evidence, or review fields" \
  --metadata '{"evidence":["..."],"commands_run":["..."]}'
python CoAgent/runtime/mosim_agent_runtime.py complete ...
python CoAgent/runtime/mosim_agent_runtime.py task-packet --task-id <id>
python CoAgent/runtime/mosim_agent_runtime.py task-packet-text --task-id <id>
python CoAgent/runtime/mosim_agent_runtime.py result-packet --task-id <id>
python CoAgent/runtime/mosim_agent_runtime.py result-packet-text --task-id <id>
python CoAgent/runtime/mosim_agent_runtime.py status-board
python CoAgent/runtime/mosim_agent_runtime.py status-board --active-only
python CoAgent/runtime/mosim_agent_runtime.py link-conversation \
  --parent-task-id <id> \
  --department ProjectOwner \
  --thread-id <thread_id>
python CoAgent/runtime/mosim_agent_runtime.py conversation-graph --include-tasks
python CoAgent/runtime/mosim_agent_runtime.py close-conversation \
  --edge-id <edge_id> \
  --summary "task conversation closed"
```

The runtime does not send packets itself.
That responsibility starts in `CoAgent/dispatch/`.

The conversation graph records which visible department or dedicated task
conversation belongs to which durable task. It stores only project routing
metadata: parent task id, department, thread id, thread name, role, open/closed
status, timestamps, and JSON metadata. It does not mutate Codex App databases.

`CoAgent/dispatch/codex_transport.py start-dispatch` opens a dispatch edge.
`poll-dispatch` and `reconcile-result` close that edge after the declared
result packet is imported into runtime state.

Run `CoAgent/hooks/preflight.py` before risky or wide-scope CoAgent work.

Use `update-metadata` instead of manual SQLite edits when a task needs to record
result-packet fields such as `files_changed`, `commands_run`, `evidence`,
`risks`, `blockers`, `review_status`, `acceptance_state`, or
`next_recommended_action`. If the task is claimed, the claim token is required.

## Compatibility

Existing workflows may still call:

```bash
python Scripts/agent/mosim_agent_runtime.py ...
```

That path should remain a thin compatibility entrypoint only.
