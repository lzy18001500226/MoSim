# CoAgent Review Package

## Purpose

This directory owns compact human-review packages for a long-running CoAgent
task.

The package builder is read-only apart from writing the requested package. It
does not dispatch work, send Weixin messages, change task state, stage Git,
commit, or push. It summarizes the current task checkpoint, review queue,
runtime event audit, and already generated status/resume/doctor/task-health/Git
handoff/evidence-manifest/blocker artifacts.

## Command

```bash
python3 CoAgent/review_package/review_package.py \
  --task-id COAGENT-IMPL-LONGRUN-20260531 \
  --output Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.review_package.json \
  --markdown-output Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.review_package.md
```

Use this before a long manual review window so the reviewer can inspect one
package instead of searching runtime, status, doctor, and packet folders.

The package embeds the current task-health continuation decision. Reviewers can
see whether the long task may continue, must continue with watch, must pause
for review, must ask the user, must stop for safety, or must rework/reject the
current implementation path. It also includes the standard blocker-packet
command, so a reviewer or resumed agent can regenerate a
`blocker_notification` packet without relying on chat memory.
The review package exposes `continue_allowed`, `recommended_action`,
`blocking_task_ids`, and `watch_task_ids` at the task-health summary level so a
reviewer does not need to infer the continuation state from nested per-task
entries.
By default, the package uses the same staged-file warning threshold as
task-health and status exports. This keeps broad Git surfaces visible as a
`continue_with_watch` condition in the human-review packet. Tests may pass a
larger threshold explicitly when they need a clean fixture.

The package also embeds `review_queue verify-closeout` output. That section
answers the post-review question explicitly: whether the recorded human
decision has a valid closeout artifact, whether it removed the task from the
active review queue, and whether task-health still blocks continuation for
another reason. Use this before resuming after manual review instead of
inferring closeout state from chat history.

The package also summarizes evidence freshness. Stale evidence does not make
the package human-required by itself, but `evidence_refresh.recommended=true`
means a resumed agent should run the listed refresh commands before using old
status, review, doctor, or evidence packages as current state.
Those commands refresh both quick and full doctor outputs because either can be
registered as current recovery evidence in runtime metadata.
The command list is generated centrally by
`CoAgent/evidence/refresh_commands.py`; the review package step is last so it
summarizes the newest evidence manifest.

`evidence_refresh.critical_stale_count` counts current recovery artifacts that
should be refreshed before relying on them. `archival_stale_count` counts older
support files that stay visible for audit but are not a review blocker.
The evidence manifest deliberately treats review-package files as downstream
outputs rather than freshness inputs, avoiding a refresh loop where each
artifact marks the other stale.
