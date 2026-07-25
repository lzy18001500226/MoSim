# Mainline Operations Board

> Current task selector for MoSim. Keep this file short: it records only the
> active work, the next decision, and blockers. It is not a history ledger or
> a result archive.

Status: documentation and workflow cleanup is ready for user review,
2026-07-26 CST.

## 1. Current Action

Review the cleaned project information architecture before starting the next
MWORKS or runtime experiment:

1. make project, model, configuration, script, result, and document entry
   points understandable to a new reviewer;
2. merge duplicate active rules and remove legacy workflow redirects from the
   normal reading path;
3. preserve the CoSim three-phase blueprint, model evidence, results, and
   frozen directory-migration boundary;
4. verify links and loading roots, then return the cleaned structure for user
   review.

This cleanup does not mark any controller, code-generation, planning,
formation, UE, or runtime task as complete.

## 2. Current Engineering Boundaries

```text
Formal MWORKS package root:
  Models/MoSimQuadrotorModel/package.mo

Current runtime evidence lane:
  Ubuntu-20.04 / ROS1 Noetic / Sunray / Gazebo Classic
  / PX4 / MAVROS / px4ctrl / RViz

Display and operator surfaces:
  UE, QGC, Flight Console and Model Studio are support layers.
  They do not replace MWORKS, Gazebo, PX4, MAVROS, logs, or metrics.
```

The current competition architecture is owned by `Docs/Design/架构.md`. The
future CoSim three-phase platform roadmap is owned by
`Docs/CoSim/research/raw/CoSim设计.md`; do not rewrite it as a statement of
current completion.

## 3. Next Engineering Selection

After the documentation cleanup passes review, select the next executable gate
from `Docs/Design/架构/00_架构与任务/任务路线图.md` and the user-approved
controller-evidence plan. Do not infer the next task from historical runs.

Before a live MWORKS, Gazebo, ROS, UE, or desktop action, load the relevant
topic workflow and declare the evidence path under `Results/`.

## 4. Board Update Rule

Update this board only when one of these changes:

- current task or next executable gate;
- declared architecture/runtime authority;
- terminal blocker and its required resolution;
- accepted evidence pointer.

Put detailed run history in `Results/`, stable design in `Docs/Design/`, and
historical plans in `Docs/Cache/`. Do not append progress narration here.

## 5. Historical Board

The pre-cleanup board, including prior controller, Factory, FUEL, and
closeout history, is preserved at:

```text
Docs/Cache/workflow_history/mainline_operations_board_20260726_pre_cleanup.md
```
