# Reference Repository Organization Draft

Status: draft cache, 2026-07-03.

This note records the current repository organization rule before doing any
large `References/` reshuffle. Promote only after user review.

## Current Confirmed Moves

The following paths are current and should be used by docs/scripts:

```text
References/Control/Quadrotor_SE3_Control
References/UAVStacks/Prometheus
References/UAVStacks/XTDrone
```

The old nested paths are no longer current:

```text
References/Control/geometric/Quadrotor_SE3_Control
References/UAVStacks/ros_px4_gazebo/Prometheus
References/UAVStacks/ros_px4_gazebo/XTDrone
```

## Organization Principle

Classify a reference repository by its primary reuse role in MoSim, not by every
module it contains.

Many UAV repositories are mixed stacks. For example, Diff/FUEL/RACER/EGO-style
projects may include planner, controller, simulator, mapping, visualization,
and message adapters in one source tree. Do not split such repositories into
subdirectories by copying internal packages unless there is a concrete
dependency audit and a reproducible build reason.

Use cross-index docs to record secondary capabilities instead:

```text
primary path: where the repository lives
secondary tags: controller, planner, simulator, mapping, swarm, UI, dataset
reuse boundary: source reference, runtime candidate, codegen seed, report ref
claim boundary: what it can and cannot prove in MoSim
```

## Proposed Top-Level Buckets

| Bucket | Primary meaning | Examples |
| --- | --- | --- |
| `References/Control/` | Controller algorithms, control theory implementations, and controller-focused examples. | `Quadrotor_SE3_Control`, NMPC/SMC/DFBC/LQI references when controller-first. |
| `References/UAVStacks/` | Full UAV engineering stacks with launch files, simulators, flight-control integration, or multi-package workflows. | `Prometheus`, `XTDrone`. |
| `References/Lab/` | Research planner, mapping, exploration, formation, SLAM, and trajectory optimization repositories used for algorithm study or runtime experiments. | `Diff-Planner`, `FUEL`, `RACER`, `FAST_LIO`, `Fast-Planner`, `GBPlanner2` candidates. |
| `References/PX4/` | PX4 firmware/source, PX4 interface contracts, uORB, module, and SITL/HITL references. | `PX4-Autopilot` material. |
| `References/Sunray/` | Current ROS1/Sunray/Gazebo/PX4/MAVROS runtime baseline source. | Sunray runtime, models, plugins, control utilities. |
| `References/Gazebo/`, `References/Simulation/`, `References/UnrealScenes/` | Simulator engines, world/model assets, scene conversion, rendering and environment references. | Gazebo/gz-sim, Factory assets, UE scene sources. |

## Mixed Repository Rule

For mixed repositories:

```text
Keep the original repo intact under one primary bucket.
Do not copy one internal controller/planner package into another bucket.
Add index entries that point to internal packages when needed.
If a script needs one internal file, reference the repo's current primary path.
If a repo becomes an active runtime dependency, create a small MoSim adapter
under Scripts/ or project source paths instead of editing the reference repo.
```

Examples:

```text
Diff-Planner:
  primary bucket: References/Lab
  secondary tags: planner, local mapping, trajectory, controller-adjacent code
  rule: keep intact; do not move because it contains controller-like pieces.

FUEL/RACER:
  primary bucket: References/Lab
  secondary tags: UAV exploration, mapping, trajectory, swarm
  rule: keep intact; runtime adapters live in MoSim scripts/source, not inside
  the reference tree.

Prometheus / XTDrone:
  primary bucket: References/UAVStacks
  secondary tags: PX4/Gazebo/ROS UAV stack, launch workflow, simulator examples
  rule: keep as full stacks; use as engineering workflow references.

Quadrotor_SE3_Control:
  primary bucket: References/Control
  secondary tags: SE3 geometric controller, Python implementation, theory ref
  rule: controller-first, so it belongs under Control even if examples include
  simulation helpers.
```

## Current Recommendation

`References/Lab` has now been physically grouped, but upstream repositories
remain intact. Future cleanup should not split internal packages out of those
repositories. If another repository changes bucket later:

```text
1. Fix broken paths first.
2. Update the reference inventory with primary bucket and secondary tags.
3. Move only the repository whose bucket is clearly misleading.
4. After any move, update scripts/docs/configs with path-limited search and checks.
```

## Lab Substructure

`References/Lab` now uses these physical groups:

```text
localization_slam
planning_local
exploration_coverage
swarm_coordination
experiment_platforms
visualization
```

The eight new exploration/coverage repositories belong under the physical
`exploration_coverage` group:

```text
gbplanner_ros-gbplanner2
uav_frontier_exploration_3d
SOAR
nbvplanner
FC-Planner
FALCON-ros1-noetic
ExplorationRRT
exploration-algorithms
```

The active runtime dependencies were moved only after scripts/configs/docs were
rewritten. Use
`Docs/Cache/design/research_drafts/lab_reference_inventory_and_migration_plan_20260703.md`
and `References/Lab/README.md` as the current source of truth for the grouped
paths.
