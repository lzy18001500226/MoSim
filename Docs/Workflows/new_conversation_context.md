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
  first. If it is missing or unclear, stop and ask rather than selecting a
  different task from the repository.
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

`Docs/CoSim/` is a future multi-vehicle platform blueprint. Its roadmap is
reference material, not a task assignment for a new conversation.

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

For non-trivial work: state the local goal from the user's request, inspect the
smallest relevant owner set, perform the smallest meaningful check, preserve
evidence in its normal project path, and update documentation only when a
reusable rule or entry point changes.

Topic workflows describe procedures and stop conditions. They do not create
priority, assign another conversation, or authorize work by themselves.
