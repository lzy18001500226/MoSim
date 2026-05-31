# CoAgent Review Queue

## Purpose

This directory owns the project-local human-review queue view.

The queue does not send messages and does not mutate task state. It reads the
runtime task board plus result-router review files and returns the items a
human should inspect first after receiving a gateway notification or returning
to the project.

## Command

```bash
python CoAgent/review_queue/review_queue.py list --json
```

Use `--include-terminal` when reviewing closed items too.
Use `--include-superseded` for incident review of child tasks whose parent task
is already cancelled, done, or failed. The default queue suppresses those items
so the current human-review list is not polluted by historical architecture or
transport experiments.

After manual review, record the decision:

```bash
python CoAgent/review_queue/review_queue.py closeout \
  --task-id <id> \
  --decision accepted \
  --reason "manual review passed" \
  --next-action none
```

Allowed decisions are `accepted`, `accepted_with_concerns`, `needs_rework`,
and `rejected`. Closeout updates runtime metadata and appends an event; it does
not change source files or automatically resume work.

The queue is intentionally conservative. Any task with `human_needed=yes`,
`requires_human_review=true`, `review_status` other than accepted/not_required,
or terminal blocked/failed/done_with_concerns state appears in the queue.
