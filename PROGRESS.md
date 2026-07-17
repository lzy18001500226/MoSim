# Project Progress

> Current active-progress note only. This file is not a transcript and must not
> be used for historical recovery. For current operating state, read
> `Docs/Workflows/mainline_operations_board.md` first. For historical
> multi-thread or packet trace-back, use `Docs/Workflows/agent_task_ledger.md`
> only when explicitly auditing legacy material.

## 2026-07-18 CST - Current Active Context

Active long goal: finish all competition engineering except frontend. P2-P8
implementation/evidence batches are committed and pushed through
`842b2ff793`. The Wave A LQR/LQI/SO(3)/Backstepping generated-C Gazebo
reconciliation has been executed and is pending exact-path publication. The
67-row authority at
`Results/control_platform/classic_controller_closeout_20260717/CLASSIC_CONTROLLER_FINAL_MATRIX.json`
is generator-stable at `accepted=27`, `executed_blocked=25`, `not_run=15`, and
canonical coverage is 22/22 with zero findings. Current work is bounded
not-run triage, the official-PID versus recommended-controller seven-scenario
A/B, then final evidence/report/manual/demo/submission packaging. Frontend,
UE/RViz embedding and further FUEL/RACER coverage tuning are excluded.

2026-07-17 P9 learning-control closeout: bounded Neural Residual and RL Gain
Scheduler have complete frozen-artifact -> fixed-size C -> MWORKS MIL -> official
codegen -> 19-column SIL -> px4ctrl -> Gazebo/PX4/MAVROS 3x3 evidence at
`Results/control_platform/p9_learning_gazebo_r4_20260717/`. Execution and
provenance passed, but strict performance acceptance is blocked; both profiles
remain `implemented/selectable=false`. Wind XYZ RMSE improved 9.81% and 8.80%
versus Cascade, while nominal/parameter-mismatch superiority was not stable.

- Operating mode: single active Codex thread. Legacy visible-thread dispatch,
  R1/R2/R3 department routing, CoAgentOps patrol dispatch, dispatch-ticket SLOs,
  and dead-thread automation are not current project workflow.
- Current board authority:
  `Docs/Workflows/mainline_operations_board.md`.
- Current architecture authority:
  `Docs/Design/需求.md`, `Docs/Design/赛题.md`, `Docs/Design/架构.md`, and the
  relevant topic document under `Docs/Design/架构/`.
- Current runtime/evidence lane:
  ROS1 Noetic / Sunray / Gazebo Classic / PX4 / MAVROS / px4ctrl, with RViz as
  the point-cloud, trajectory, map, and frame review surface.
- Current frozen baseline:
  G8/G9 generated-controller and controller-family evidence is already recorded
  on the mainline board. Do not infer next work from old Goal or G9 wording in
  historical notes.
- Current next-work principle:
  follow the mainline board. Finish the remaining 15 `not_run` row triage,
  preserve bounded blockers, then complete the official-PID versus recommended
  controller seven-scenario A/B and final packaging. FUEL/RACER coverage tuning
  and frontend work remain excluded from this goal.

## How To Update This File

Keep only the newest active context and the smallest useful note for the next
turn. Move durable rules to workflows, skills, checkers, schemas, or design
docs. Do not append long packet histories or old thread logs here.
