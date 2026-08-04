# AGENTS.md

> Project constitution for Codex and other assistants working in MoSim.

This file contains durable project boundaries only. Repeatable procedures,
topic-specific checks, and task evidence belong in the relevant workflow,
skill, source, or `Results/` path.

## 1. Task Isolation

MoSim has no global conversation mainline, current P0, PMO queue, default
owner thread, or automatic task handoff.

Every conversation is an independent task surface by default. The newest
direct user instruction in the current conversation is the only authority for
the current task's scope, priority, allowed actions, and stopping condition.

Never select work from another conversation, a thread ID, a pinned task, a
board, `PROGRESS.md`, memory, a cached transcript, a screenshot, or a dated
status paragraph. Those sources can provide background only after the user
explicitly asks for that background; they never authorize execution.

After context compaction, interruption, or resume:

1. Re-anchor to the newest direct user instruction in this conversation.
2. Re-check the files and paths named by that instruction.
3. If the instruction or scope is unavailable or ambiguous, stop and ask the
   user. Do not choose a replacement task from repository documents.

Context compaction is an internal continuation boundary, not task completion.
When the newest user objective is present in the retained conversation or
recovery summary, continue that objective immediately after loading the
required context. Do not ask for a replacement task, emit a completion
response, or treat hook output as a new user task merely because `AGENTS.md`
was re-read. Ask only when no recoverable user objective exists.

A task ID or conversation ID in any project file is historical metadata, not a
routing instruction. Do not inspect, message, dispatch to, or modify another
conversation unless the current user explicitly requests that exact action.

This file must not contain a dated task assignment, live blocker, next action,
thread ID, or cross-conversation handoff. Put those facts in task-local
artifacts only.

## 2. Startup Context

For a new or resumed conversation, load only:

```text
1. AGENTS.md
2. Docs/Workflows/new_conversation_context.md
3. The topic-specific workflow, skill, design file, source, or result named or
   required by the current user's request
```

Do not load `Docs/Workflows/mainline_operations_board.md` during ordinary
startup. That path is retained as a read-only historical status archive for
compatibility; it is not a task selector or permission source. Read it only
when the user explicitly requests a project-status or historical audit.

Do not routinely load raw Codex session JSONL, old chat dumps, legacy AgentOS
ledgers, or broad reference trees. Historical claims must be checked against
current source or evidence before being used.

## 3. Workspace And Change Boundaries

1. Work inside `C:\Users\HP\Desktop\MoSim` unless the current user explicitly
   approves a named infrastructure action outside the repository.
2. Preserve unrelated user changes. Inspect scoped status and diff before
   editing; never reset, clean, force-push, or broadly stage the worktree.
3. Use `apply_patch` for manual edits. Keep changes limited to the paths owned
   by the current request.
4. Do not delete or move executable runtime, hook, checker, protocol, skill, or
   automation code without a dependency audit and an explicit current scope.
5. A shared worktree does not merge task ownership. Treat unowned changes as
   user or another-task state and do not rewrite them to make a clean status.
6. Read-only inspection may run in parallel. A given path has at most one
   active writer in a shared worktree. Parallel code edits require an
   independent repository worktree and branch, followed by parent review and
   integration.

## 4. Execution And Evidence

- Name a local goal for non-trivial work and inspect the smallest relevant
  context before changing files.
- Use project-owned workflows and helper APIs; do not guess model, MCP, or
  runtime interfaces.
- Keep source/static checks, GUI/review evidence, fixtures, result-context
  smoke, and live runtime acceptance clearly separate.
- MWORKS/Sysplorer/Syslab is the formal model, controller, and simulation
  evidence authority.
- The declared robotics runtime evidence lane is Ubuntu 20.04 / ROS1 Noetic /
  Sunray / Gazebo Classic / PX4 / MAVROS / px4ctrl / RViz. UE, QGC, Flight
  Console, and Model Studio are display or operation surfaces and do not
  replace formal or runtime evidence.
- Do not claim controller, planner, localization, closed-loop, flight, or
  final scene success without the evidence required by the relevant workflow.
- MWORKS login, license, authorization, unknown GUI errors, and unknown runtime
  states are blockers. Do not continue solver/model work through them.
- Desktop observation and desktop action are separate permissions. A screenshot
  does not authorize clicking, typing, closing, or restarting a window.
- Keep live/runtime waits bounded and preserve partial evidence on timeout.

### Unreal Mapping Window Rule

Active point-cloud and map review belongs to RViz/RViz2 or an equivalent native robotics viewer. Browser HTML is not an accepted active point-cloud/map review surface. Global UE collision/occupancy truth is a validation oracle only; it is not a substitute for runtime map, localization, planner, or controller evidence.

## 5. Documentation Roles

| Need | Source |
|---|---|
| Hard boundaries and startup rules | `AGENTS.md` |
| Task-neutral fresh context | `Docs/Workflows/new_conversation_context.md` |
| Task-local work loop | `Docs/Workflows/single_thread_operating_model.md` |
| Repeatable procedure | `Docs/Workflows/` or `Docs/Skills/` |
| Stable architecture and interfaces | `Docs/Design/` |
| Navigation only | `Docs/Index/` |
| Historical status and migration records | `Docs/Cache/` and the retired board archive |
| Evidence, logs, metrics, figures, and packets | `Results/` |

An index or workflow explains where to work and how to check it; it does not
create a task, assign an owner, or authorize an unrelated action. A project
technical direction may describe architecture, but it is not a conversation
execution queue.

Words such as "control mainline" or "runtime lane" in a design document
describe technical evidence boundaries only. They never choose today's task or
override the current user's direct request.

For a named current task that reaches completion, a blocker, or review-required
state, send at most one concise Chinese notification through
`Scripts/agent/send_gateway_email_alert.py`. Do not send notifications for
ordinary turns, and do not send a notification for another conversation's task.

## 6. Git Closeout

For a task that changes project files:

```text
inspect scoped status and diff
-> run targeted checks
-> stage exact task paths
-> git diff --cached --check
-> commit and push when authorized and available
-> verify the upstream state
```

Do not include unrelated user changes. If a lock, ownership ambiguity, check
failure, authentication issue, or publication failure prevents closeout,
report it precisely instead of claiming completion.

## 7. Uncertainty Policy

When uncertain, prefer the current user's words and current source/evidence
over memory or historical documents. Make the smallest reversible change. If
the next step would change architecture, scope, runtime authority, or a
destructive boundary not already specified by the current user, stop and ask.
