# Coordinating-Thread Operating Model

> Current MoSim operating rule, 2026-07-24. This replaces the former
> multi-visible-thread dispatch model for active project work.

## 1. Current Rule

MoSim now uses one active coordinating Codex thread. The coordinating thread
owns:

- reading the compact project entry;
- selecting the next engineering step;
- running local tools and checks;
- updating project docs when a reusable rule changes;
- producing evidence, blocker notes, figures, scripts, and report materials;
- asking the user before changing architecture or taking high-risk runtime
  actions.

### Official Temporary Subagents

Official temporary subagents are a current bounded delegation surface, not the
retired visible-thread system. Use them for independent work with a clear return
point when parallelism materially improves speed or confidence, such as focused
research, review, inspection, or disjoint verification.

The coordinating thread defines the scope, integrates every returned finding,
and owns user communication and final claims. Do not use temporary subagents as
durable departments, a project backlog, PMO authority, a hidden acceptance
owner, or a visible-thread dispatch route. Parallel writes, Git mutations, GUI,
MCP, or live runtime work require explicit ownership and coordination in the
parent task.

Former visible-thread dispatch concepts are legacy for current work:

- no R1/R2/R3 department routing;
- no visible-thread dispatch queue;
- no patrol-owner bounded dispatch;
- no dispatch ticket SLO as an active PMO control loop;
- no routine thread patrol, recovery, or restart policy inside project docs.

## 2. Startup Chain

Use this startup chain for ordinary MoSim work:

```text
1. AGENTS.md
2. Docs/Workflows/new_conversation_context.md
3. Docs/Workflows/mainline_operations_board.md
4. Topic-specific workflow / skill / design docs only as needed
```

Do not load retired agent-OS internals, retired dispatch internals, or
`Docs/Workflows/agent_task_ledger.md` during normal startup unless the task is
explicitly about legacy cleanup, packet audit, or historical recovery.

## 3. Current Engineering Priority

Follow the current board. As of this rule, the active runtime lane is:

```text
Docs/Design/架构.md
Docs/Workflows/mainline_operations_board.md
Docs/Workflows/sunray_ros1_current_runtime_lane.md
References/Sunray
References/Lab/localization_slam/FAST_LIO
```

This means Ubuntu-20.04 / ROS1 Noetic / Sunray / Gazebo Classic / PX4 / MAVROS
/ px4ctrl with RViz point-cloud, trajectory, map, and frame evidence. Do not
substitute the old ROS2/PX4/x500 route, downloaded replacement FAST-LIO, fake
point clouds, headless-only evidence, or UE screenshots for the current review
target.

## 4. How The Coordinating Thread Works

For each task:

1. State the local goal when the task is non-trivial.
2. Inspect the smallest relevant docs/source/evidence set.
3. Run the narrowest useful check before broad changes.
4. Add logs/prints/checkpoints when debugging runtime behavior.
5. If an API, tool behavior, or runtime issue is unclear, consult local docs
   first, then official docs or targeted web/community sources when needed.
6. Stop and ask the user before changing the agreed architecture, switching
   to an equivalent substitute, deleting large structures, or performing
   disruptive GUI/runtime actions.
7. Record durable evidence in the normal project locations.
8. When a named small task, goal, gate, or review packet reaches completion,
   blocker, or review-required state, send one short Chinese email through
   `Scripts/agent/send_gateway_email_alert.py`. Use a unique task/gate
   `--cooldown-key`; for explicit terminal notices, use
   `--cooldown-minutes 0` when the default cooldown could suppress a distinct
   small-task result. Do not send email for ordinary chat replies or
   intermediate observations.

## 5. Legacy Boundaries

Legacy multi-thread documents may still be useful as research history, but
they are not active project instructions unless the current task explicitly
says so.

Keep executable hook/checker/script paths untouched until a separate cleanup
pass proves they are unused or replaces their references.
