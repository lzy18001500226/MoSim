# New Conversation Context

> Task-neutral startup orientation for a fresh or resumed MoSim conversation.
> This file is not a task ledger, status board, authorization, or runtime
> history dump.

Status: task-local startup rules, 2026-08-04 CST.

## 1. Read Order

```text
1. AGENTS.md
2. Docs/Workflows/new_conversation_context.md
3. Only the topic-specific workflow, skill, design file, source, or result
   required by the current user's direct request
```

Do not read `Docs/Workflows/mainline_operations_board.md` as part of startup.
It is a retired compatibility path containing historical project status. It
does not select work, identify a current P0, or grant permission. Read it only
for an explicit status or historical audit request.

## 2. Current Conversation Owns Its Task

- There is no global MoSim conversation mainline or shared active task.
- Each conversation starts from its newest direct user instruction.
- A task ID, thread ID, owner label, board entry, `PROGRESS.md` line, memory
  note, or prior conversation is background only and never an execution route.
- After context compaction or resume, recover the current user's latest request
  first. Inspect the retained conversation or recovery summary before doing
  anything else.
- Recover in this order: direct-user recovery pack; active same-session Goal;
  then, when exposed, `get_goal` and a bounded `codex_app__read_thread` for the
  current thread. When an exact source identity needed for execution is missing,
  this read is mandatory before asking the user for it or marking the task
  blocked. Thread history adds detail but cannot override a newer direct user
  message. An active Goal may resume only its own outcome, constraints, and
  verification; it cannot invent missing sources, expand scope, select another
  conversation's work, or revive a completed/blocked goal.
- If every recovery source is unavailable, record `continuity_unresolved`.
  Do not report completion or demand a full task restatement. In the current
  turn, ask only for one minimum recovery input: the original prompt, current
  goal text, or a named task packet. Do not silently end after the startup
  reads.
- A recovered goal, plan, completion marker, thread preview, board, memory, or
  historical result is never a general task selector. The newest direct user
  instruction always wins.
- Context compaction is not task completion. When the latest user objective is
  recoverable, keep it active and continue it after the required startup reads;
  do not ask for a replacement task or report completion solely because
  `AGENTS.md` was re-read or a lifecycle hook added context.
- A direct request to explain why execution stopped or to repair continuation
  behavior is a self-contained diagnostic task. Inspect the active recovery
  hook and task-continuity rules before asking for a source from the interrupted
  business task; do not alter that business source merely to diagnose the stop.
- Do not read, message, dispatch to, or modify another conversation unless the
  current user explicitly asks for that exact operation.
- Do not put a live assignment, blocker, next gate, or conversation ID into
  this startup file. Those belong in a task-local document or result packet.

## 3. Project Orientation

MoSim is the A8 quadrotor control and simulation project. MWORKS/Sysplorer/
Syslab is the formal controller/model evidence authority. The declared runtime
evidence lane is ROS1 Noetic / Sunray / Gazebo Classic / PX4 / MAVROS / px4ctrl
with RViz review. UE, QGC, Flight Console, and Model Studio are display or
operation surfaces and do not replace those authorities.

`Docs/Cache/cosim/blueprint_20260614/` preserves the future multi-vehicle
platform blueprint. It is reference material, not a task assignment for a new
conversation.

## 4. Structure Rules

- Load the project-owned Modelica root only from
  `Models/MoSimQuadrotorModel/package.mo`.
- Put new evidence in `Results/`, stable design in `Docs/Design/`, and
  repeatable procedures in `Docs/Workflows/`.
- Keep historical plans, migration notes, and old task ledgers under
  `Docs/Cache/`; they are not ordinary startup context.
- Do not create a new workflow, package root, smoke test, or progress document
  merely to narrate routine work.

## 5. Task-Local Work Method

For non-trivial work: create a concise Goal contract when the client exposes
Goal mode, then inspect the smallest relevant owner set, perform the smallest
meaningful check, preserve evidence in its normal project path, and update
documentation only when a reusable rule or entry point changes. Never pass
`token_budget` unless the current direct user explicitly requests a numeric
budget. The Goal holds the active task's outcome, constraints, and verification;
it is not a global queue or cross-conversation handoff.

Topic workflows describe procedures and stop conditions. They do not create
priority, assign another conversation, or authorize work by themselves.
