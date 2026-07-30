# New Conversation Context

> Compact orientation for a fresh MoSim task. It is not a task ledger, a
> runtime-history dump, or an authorization to start a simulator.

Status: current startup context, 2026-07-27 CST.

## 1. Read Order

```text
1. AGENTS.md
2. Docs/Workflows/new_conversation_context.md
3. Docs/Workflows/mainline_operations_board.md
4. Only the topic-specific workflow, skill, design file, source, or result
   needed for the requested action
```

Do not bulk-load legacy AgentOS material, raw chat/session dumps, reference
corpora, or old result narratives during ordinary work.

## 2. What This Repository Is

MoSim is the current A8 quadrotor control and simulation project. Its formal
controller/model evidence is MWORKS; its current runtime evidence lane is
ROS1/Sunray/Gazebo Classic/PX4/MAVROS/px4ctrl with RViz review. UE, QGC, Flight
Console, and Model Studio are display or operation surfaces, not control-loop
truth.

`Docs/CoSim/` is a future, multi-vehicle platform blueprint. Its three-phase
roadmap remains valid future work and must not be collapsed into the current
competition milestone.

### 2.1 User-Assigned Work Ownership

The current user assignment is intentionally split across conversations:

```text
This coordinating thread:
  MWORKS controller/model/evidence work
  -> later MoSim Studio APP work

Separate QGC/Gazebo conversation:
  QGC, ROS1/Gazebo/PX4/MAVROS runtime, Factory maps, sensors, and live runs
```

Do not infer ownership from a technology's authority boundary. A MWORKS/APP
thread may read a completed runtime record for a factual handoff, but must not
start, modify, diagnose, or extend the QGC/Gazebo line unless the user explicitly
reassigns it. A direct user scope assignment overrides an older broad
"current runtime lane" statement.

## 3. Current Structure Rules

- The atomic Modelica-root migration is complete: load only
  `Models/MoSimQuadrotorModel/package.mo` as the project-owned root. Nested
  `package.mo` files are namespaces, not independent project roots.
- The broad directory refactor in
  `Docs/Workflows/project_structure_refactor.md` remains a user-frozen design
  reference. Do not move models, configs, scripts, results, UE projects, or
  references unless the user explicitly reopens that refactor. The root-level
  `cmd/` launcher organization is a scoped entrypoint cleanup and does not
  execute the frozen plan.
- Put new evidence in `Results/`; put stable design in `Docs/Design/`; put
  repeatable operating procedures in `Docs/Workflows/`.
- Do not create a new workflow, package root, smoke test, or progress document
  merely to record routine work.

## 4. Work Method

For a non-trivial task: name the local goal, inspect the smallest owner set,
perform the smallest meaningful check, keep evidence in its normal project
path, and update documentation only when a reusable rule or entry point changes.
Use the current board for the next action and `Docs/Design/架构.md` for authority
boundaries.

## 5. Legacy Material

Historical AgentOS, old task ledgers, one-off plans, and session migration
records live under `Docs/Cache/`. Consult them only for explicit trace-back or
cleanup work; they are not routine startup context.
