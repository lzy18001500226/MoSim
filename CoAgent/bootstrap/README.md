# CoAgent Bootstrap

## Purpose

This directory owns reusable bootstrap and recovery helpers for dedicated
long-running task conversations.

It turns one durable runtime task into:

- a context pack,
- a department dispatch packet,
- a handoff text file for the visible conversation,
- context budget/quality metrics,
- a runtime conversation edge,
- a recovery summary after the result packet is written.

## Boundary

Bootstrap does not create Codex App conversations and does not edit Codex
private state.

Visible conversation delivery remains under:

```bash
CoAgent/dispatch/codex_transport.py
CoAgent/transport/
```

Bootstrap writes only project-local ignored artifacts under:

```text
Results/coagent_bootstrap/
Results/context_packs/
Results/agent_packets/
```

## Basic Flow

Create a task and handoff packet:

```bash
python3 CoAgent/bootstrap/task_bootstrap.py bootstrap-task \
  --department ProjectOwner \
  --task-id example_long_task \
  --objective "Do one bounded long-running task" \
  --read-scope CoAgent \
  --write-scope Results/agent_packets \
  --acceptance "result packet imported" \
  --stop-condition "runtime task terminal"
```

Create the same handoff plus a dry-run Codex transport plan:

```bash
python3 CoAgent/bootstrap/task_bootstrap.py bootstrap-task \
  --department ProjectOwner \
  --task-id example_long_task \
  --objective "Do one bounded long-running task" \
  --read-scope CoAgent \
  --write-scope Results/agent_packets \
  --acceptance "result packet imported" \
  --stop-condition "runtime task terminal" \
  --include-transport-plan
```

The generated transport packet sends the full handoff, including the context
pack and department dispatch packet, not just the bare runtime task.

Start visible-conversation delivery only after reviewing the generated command:

```bash
python3 CoAgent/dispatch/codex_transport.py start-dispatch \
  --department ProjectOwner \
  --task-id example_long_task \
  --packet-file Results/coagent_bootstrap/example_long_task.handoff.txt
```

After the target conversation writes the declared result packet, recover:

```bash
python3 CoAgent/bootstrap/task_bootstrap.py recover-task \
  --department ProjectOwner \
  --task-id example_long_task
```

Inspect current state:

```bash
python3 CoAgent/bootstrap/task_bootstrap.py status-task \
  --department ProjectOwner \
  --task-id example_long_task
```
