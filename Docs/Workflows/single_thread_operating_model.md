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

For a new non-trivial direct request, establish or refresh a same-session Goal
when the client exposes Goal mode. Keep its contract short: outcome,
constraints, and verification. The Hook may bootstrap this reminder and persist
the accepted Goal, but it cannot create a Goal, choose a task, or replace the
direct user instruction.

```text
current user's direct objective
  -> same-session Goal contract when available
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

After compaction, interruption, or resume, recover the newest direct user
request in this conversation and verify the named paths. First inspect the
retained conversation or recovery summary. Use the direct-user recovery pack
first. If it is absent, resume an active Goal from the same in-flight session
only within its stated outcome, constraints, and verification. If exposed,
call `get_goal` to refresh that contract, then use `codex_app__read_thread`
only for the current thread to recover the newest direct instruction and exact
sources. When an exact source identity needed for execution is missing, this
read is mandatory before asking the user for it or marking the task blocked.
The current thread ID may be used only for that bounded read; it never selects
a task. Compaction is not a completion signal: if any recovery source is
sufficient, continue the same task after the startup reads. A Goal cannot
invent missing paths/URLs, widen scope, revive a completed/blocked goal, or
override a newer direct user instruction.

If no pack, active Goal, or current-thread reader is available, preserve
`continuity_unresolved`. Do not report completion or demand a full task
restatement. In the current turn, ask only for the original prompt, active Goal
text, or a named task packet. Do not silently end after the startup reads. Do
not substitute a thread preview, initial prompt, prior
assistant answer, plan, board, `PROGRESS.md`, memory, another conversation, or
a historical result for a current task.

Do not ask for a replacement task or report completion solely because a
lifecycle hook ran or `AGENTS.md` was re-read.

A direct request to explain why execution stopped or to repair continuation
behavior is a self-contained diagnostic task. Inspect the active recovery hook
and task-continuity rules before asking for a source from the interrupted
business task; do not alter that business source merely to diagnose the stop.

A recovered goal, task plan, completion marker, or `get_goal` result is never
a general task selector. The active same-session Goal exception above is a
bounded continuity fallback only; a newer direct user request still wins.

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
