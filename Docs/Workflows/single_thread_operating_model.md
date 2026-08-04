# Task-Local Operating Model

> Compatibility path for the former single-thread document. The operating
> model is now task-local: each conversation works only from its own direct
> user request.

## 1. Ownership

The current conversation owns only the scope explicitly stated by the current
user. There is no project-wide coordinating thread, integration queue, default
owner, or automatic handoff between conversations.

An official temporary subagent may be used only for an independent bounded
slice that the current user request permits. It cannot become a hidden owner,
write shared paths in parallel without coordination, or select work for any
other conversation.

Thread IDs, labels, task boards, and old dispatch records are trace metadata.
They are never permission to execute or route work.

## 2. Normal Work Loop

```text
current user's direct objective
  -> task-local scope and stop condition
  -> smallest relevant source/design/workflow/result context
  -> one bounded edit, check, or runtime gate
  -> evidence or precise blocker
  -> update only the task-owned document when a reusable fact changed
```

The retired `mainline_operations_board.md` is not part of this loop. Topic
workflows explain how to act after the current user has selected a task; they
do not create priority or authorize unrelated work.

## 3. Context Recovery

After compaction, interruption, or resume, re-read the newest direct user
request in this conversation and verify the named paths. Compaction is not a
completion signal: if the request is recoverable, continue the same task after
the startup reads. If the request cannot be recovered, stop and ask. Never
infer a replacement task from a board, `PROGRESS.md`, memory, another
conversation, or a historical result.

Do not ask for a replacement task or report completion solely because a
lifecycle hook ran or `AGENTS.md` was re-read.

## 4. Avoid Process Inflation

Do not turn a straightforward task into a chain of new plans, smoke tests,
packages, scripts, or progress documents. Before creating an artifact, identify
its reader, the decision or evidence gap it owns, and why an existing task-local
file cannot own it.

## 5. Quality And Stop Rules

- Use the narrowest relevant check before broad changes.
- Separate source/static, GUI/review, fixture, result-context smoke, and live
  runtime claims.
- Stop for architecture changes, unapproved broad deletion/moves, unknown
  license/login/authorization state, or a live action outside the current
  user's scope.
- For a recoverable tool/UI issue, use the documented bounded recovery first;
  report a blocker when that path produces evidence of the block.
- Record durable evidence in `Results/`, not in a growing cross-task narrative.

## 6. Completion

For a changed project path: inspect the scoped diff, run relevant checks, stage
exact files, commit, push, and verify publication when the current user permits
that closeout. Documentation cleanup does not imply runtime, controller,
planner, simulation, or flight acceptance.
