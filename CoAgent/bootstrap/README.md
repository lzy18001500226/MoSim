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

`status-task` is read-only. It returns the runtime state, artifact paths,
conversation edge graph, task-health continuation decision, review-queue item
for the task, evidence-manifest summary, and the standard blocker-packet
commands. Use it as the first recovery command when a dedicated long-task
conversation is resumed by another agent.

The recovery decision is also exposed at the response root:

- `continue_allowed`
- `recommended_action`
- `stop_reason`
- `next_intervention`
- `blocking_task_ids`
- `watch_task_ids`
- `human_task_ids`
- `review_task_ids`
- `safety_task_ids`
- `evidence_manifest_summary`

By default `status-task` uses the same Git/preflight threshold as task-health,
status export, and review packages, so broad staged surfaces remain visible as
`continue_with_watch`. Use `--skip-preflight` only for isolated smoke tests or
fixtures where the live Git workspace is intentionally irrelevant.
