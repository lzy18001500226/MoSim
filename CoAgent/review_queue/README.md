# CoAgent Review Queue

## Purpose

This directory owns the project-local human-review queue view and the narrow
review-queue notification path.

The default queue list is read-only. It reads the runtime task board plus
result-router review files and returns the items a human should inspect first
after receiving a gateway notification or returning to the project.

## Command

```bash
python CoAgent/review_queue/review_queue.py list --json
```

Use `--include-terminal` when reviewing closed items too.
Use `--include-superseded` for incident review of child tasks whose parent task
is already cancelled, done, or failed. The default queue suppresses those items
so the current human-review list is not polluted by historical architecture or
transport experiments.

To generate a gated Weixin notification packet for a queued human-review item:

```bash
python CoAgent/review_queue/review_queue.py notify --task-id <id>
```

This creates a blocker notification packet under
`Results/agent_packets/notifications/`, runs the cc-connect Weixin adapter in
dry-run mode by default, writes an audit record under ignored
`Results/coagent_gateway/`, and attempts to record the notification path in
runtime metadata. Real sending still requires `--send-weixin` and an explicit
`--weixin-session`.

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
not change source files or automatically resume work. Each closeout also writes
a JSON evidence artifact under `Results/agent_packets/closeouts/` and stores
`review_closeout_path` in runtime metadata, so later status exports and recovery
runs can see exactly what the human decision was based on.

Before resuming from a manual review decision, verify the closeout effect:

```bash
python CoAgent/review_queue/review_queue.py verify-closeout \
  --task-id <id> \
  --output Results/agent_packets/closeouts/<id>.closeout_verification.json \
  --markdown-output Results/agent_packets/closeouts/<id>.closeout_verification.md \
  --json
```

`verify-closeout` is read-only except for optional report files. It checks that
runtime metadata, the closeout artifact, the review queue, and task-health
continuation decision agree. It reports whether the decision actually unblocks
review, whether runtime continuation is still blocked, and the exact closeout
command to run when the decision or artifact is missing. Accepted-with-concerns
is considered continuable only with an explicit watch finding that must be
carried into the next checkpoint.

By default, `verify-closeout` uses the standard preflight staged-file warning
threshold from `CoAgent/hooks/preflight.py`. This keeps broad Git surfaces
visible as `continue_with_watch` instead of weakening them to a plain continue
decision. `--skip-preflight` and custom staged-file thresholds are only for
isolated fixtures or tests that intentionally avoid the live workspace.

The queue is intentionally conservative. Any task with `human_needed=yes`,
`requires_human_review=true`, `review_status` other than accepted/not_required,
or terminal blocked/failed/done_with_concerns state appears in the queue.
