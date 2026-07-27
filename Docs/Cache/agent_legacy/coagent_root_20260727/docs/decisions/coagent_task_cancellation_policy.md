# CoAgent Task Cancellation Policy

Date: 2026-05-30

## Decision

CoAgent task cancellation is controlled by the project runtime, not by Codex UI
goal deletion.

The Codex thread goal is a conversation-level convenience. It can become stale
or malformed. Current goal tools available to this agent can read, create when
no goal exists, and mark an existing goal complete or blocked under strict
conditions; they cannot edit or clear a paused/stale goal directly. A manual
`/goal clear`, client-side reset, or future verified app-server primitive may
be needed for the current visible conversation. That action must not be treated
as the durable task control plane.

Durable task state lives in CoAgent runtime events and packets. Internal
dispatch should use:

```bash
python3 CoAgent/runtime/mosim_agent_runtime.py cancel \
  --task-id <TASK_ID> \
  --actor <OWNER> \
  --summary "<why the task is intentionally stopped>"
```

## Policy

1. Prefer `cancel`, `block`, `fail`, `complete`, or `supersede` over physical
   deletion.
2. Cancellation writes an auditable terminal state and keeps enough history to
   explain who canceled the task, why, and what replaced it.
3. Physical deletion is reserved for test fixtures, duplicate bootstrap
   artifacts, or explicit user-approved cleanup.
4. Deleting a Codex goal or a Codex UI conversation is not the same as canceling
   a CoAgent task.
5. A worker conversation may request cancellation, but the accountable owner or
   dispatcher records the runtime event unless the task charter gives the worker
   explicit cancellation authority.
6. If a canceled task has downstream messages, worktrees, or result packets,
   those artifacts are marked canceled or superseded rather than silently
   removed.
7. Do not claim that a department conversation can automatically delete its own
   Codex goal until a tested transport path proves it can call the relevant
   Codex goal primitive and the user can observe the result.

## When Human Approval Is Required

Human approval is still required before:

- deleting, moving, or rewriting real project files outside a test fixture;
- deleting external resources, account assets, Codex sessions, or GUI state;
- canceling work because credentials, license activation, account login, or GUI
  permission is missing;
- converting cancellation into broad Git cleanup, force push, history rewrite,
  or external-path modification.

Human approval is not required merely because an internal runtime task needs to
be canceled with an audit trail.

## Operating Rule

If the current Codex goal blocks a new objective and cannot be edited by
available tools, ask the user to clear that visible goal only as a UI recovery
step. Then create or continue the correct CoAgent task in runtime state.

For future dispatch, do not create an architecture dependency on deleting or
editing Codex thread goals. Treat Codex goals as optional display metadata;
runtime task lifecycle is authoritative.

## Current Limitation

This policy does not solve automatic Codex goal deletion. It prevents CoAgent
from depending on that unsolved capability.

Before any future design may rely on automatic goal clearing, it must pass a
small proof:

1. create a visible test conversation with a stale goal;
2. clear or replace that goal from a project-owned command or verified
   app-server API without manual UI action;
3. verify from both the runtime state and the visible Codex front end that the
   goal changed;
4. record the exact command/API, failure modes, and rollback behavior.

Until that proof exists, stale Codex goals are a manual UI recovery case, not an
automated dispatch capability.
