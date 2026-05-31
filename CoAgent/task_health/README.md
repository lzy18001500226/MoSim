# CoAgent Task Health

## Purpose

This directory owns read-only task-health snapshots for long-running CoAgent
work.

`task_health.py` does not dispatch conversations, send notifications, call MCP
tools, stage Git, or mutate runtime state. It reads durable runtime tasks,
review queue state, runtime event audit, and Git/preflight summary, then emits
a JSON/Markdown snapshot with a recommended health state and next intervention.

## Command

```bash
python CoAgent/task_health/task_health.py \
  --task-id COAGENT-IMPL-LONGRUN-20260531 \
  --output Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.task_health.json \
  --markdown-output Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.task_health.md
```

Default mode checks active tasks only. Use `--include-terminal` for incident
review of closed tasks.

## Health States

The snapshot uses the intervention vocabulary from
`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/task_health_monitoring_and_intervention_design.md`:

- `continue`
- `continue_with_watch`
- `pause_for_review`
- `block_for_user`
- `block_for_safety`
- `close_ready`
- `reject_completion`

The first implementation is deliberately conservative. Broad staged Git work,
stale active tasks, review queue entries, human-needed metadata, and runtime
event drift produce findings. The checker reports them; it does not fix them.

## Continuation Decision

Each snapshot also emits a machine-readable `decision` object. This is the
handoff surface for dispatch/status/review code:

```text
continue_allowed
recommended_action
stop_reason
blocking_task_ids
watch_task_ids
human_task_ids
review_task_ids
safety_task_ids
next_intervention
```

The same continuation fields are also promoted to the snapshot top level. Use
the top-level fields for quick resume decisions and the nested `decision`
object for compatibility with older consumers.

Per-task decisions include `stop_reason`, `required_human_action`,
`required_review_action`, `required_safety_action`, and `watch_reasons`.
`continue` and `continue_with_watch` may proceed. `continue_with_watch` must
carry the watch reason into the next checkpoint and review package.
`pause_for_review`, `block_for_user`, `block_for_safety`, and
`reject_completion` stop autonomous continuation until the recorded
intervention is addressed.
