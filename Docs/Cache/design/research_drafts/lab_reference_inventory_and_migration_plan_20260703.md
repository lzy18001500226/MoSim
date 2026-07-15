# Lab Reference Inventory And Migration Plan

Status: completed migration cache, 2026-07-03.

This note organizes `References/Lab` after adding the new exploration and
coverage repositories. It is a source/index cleanup plan, not a runtime success
claim.

## Decision

The `References/Lab` repositories have been physically moved into grouped
subdirectories. Active runtime dependencies were moved only after the path
rewrite plan was applied to docs, scripts, and config references.

## Physical Structure

```text
References/Lab/
  localization_slam/
  planning_local/
  exploration_coverage/
  swarm_coordination/
  experiment_platforms/
  visualization/
```

Current index files:

```text
References/Lab/README.md
Docs/Index/reference_project_index.md
Docs/Design/架构/02_感知定位与规划集群/planners/README.md
```

## Inventory

| Repo | Physical group | Primary role | Dependency level | Move risk | Recommendation |
| --- | --- | --- | --- | --- | --- |
| `FAST_LIO` | localization_slam | ROS1 FAST-LIO localization/mapping | active_runtime | high | moved; keep grouped path stable |
| `FASTLIO2_ROS2` | localization_slam | ROS2 FAST-LIO2 reference | reference_only | low | moved |
| `FAST-LIVO2` | localization_slam | LiDAR-visual-inertial reference | design_reference | medium | moved |
| `Point-LIO-point-lio-with-grid-map` | localization_slam | Point-LIO/grid-map reference | design_reference | medium | moved |
| `livox_ros_driver2` | localization_slam | Livox ROS2 driver reference | design_reference | medium | moved |
| `livox_ros_driver_compat` | localization_slam | Livox compatibility driver | active_support | high | moved; keep grouped path stable |
| `Diff-Planner` | planning_local | fixed-goal single/multi-UAV planner | active_runtime | high | moved; keep grouped path stable |
| `Fast-Drone-250` | planning_local | px4ctrl and quadrotor messages | active_runtime | high | moved; keep grouped path stable |
| `ego-planner` | planning_local | EGO-Planner v1 reference | design_reference | medium | moved |
| `EGO-Planner-v2` | planning_local | EGO-Planner v2 reference | design_reference | medium | moved |
| `Fast-Planner` | planning_local | local planning and map env reference | design_reference | medium | moved |
| `GCOPTER` | planning_local | trajectory optimizer reference | design_reference | low | moved |
| `SUPER` | planning_local | perception/planning reference | design_reference | medium | moved |
| `faster` | planning_local | local replanning reference | reference_only | low | moved |
| `far_planner-melodic-noetic` | planning_local | ROS1 planning reference | reference_only | low | moved |
| `Fast-Racing` | planning_local | racing/agile planning reference | reference_only | low | moved |
| `FUEL` | exploration_coverage | single-UAV exploration baseline | active_runtime | high | moved; keep grouped path stable |
| `RACER` | exploration_coverage | multi-UAV exploration baseline | active_runtime | high | moved; keep grouped path stable |
| `FALCON-ros1-noetic` | exploration_coverage | autonomous aerial exploration with coverage-path guidance | candidate_import | low | moved |
| `FC-Planner` | exploration_coverage | known-scene aerial coverage/reconstruction planning | candidate_import | low | moved |
| `SOAR` | exploration_coverage | heterogeneous UAV exploration/photographing/reconstruction | candidate_import | low | moved |
| `gbplanner_ros-gbplanner2` | exploration_coverage | graph-based aerial/legged exploration | active_design | medium | moved |
| `uav_frontier_exploration_3d` | exploration_coverage | multi-resolution 3D frontier exploration | candidate_import | low | moved |
| `nbvplanner` | exploration_coverage | receding-horizon NBV exploration | candidate_import | low | moved |
| `ExplorationRRT` | exploration_coverage | RRT next-best-trajectory UAV exploration | candidate_import | low | moved |
| `exploration-algorithms` | exploration_coverage | exploration algorithm survey/build collection | reference_only | low | moved |
| `tare_planner-melodic-noetic` | exploration_coverage | hierarchical exploration reference | active_design | medium | moved |
| `fast_multi_robot_exploration` | exploration_coverage | FAME/RACER related multi-robot exploration | active_design | medium | moved |
| `3dmr` | exploration_coverage | 3D multi-robot exploration reference | reference_only | low | moved |
| `MGGPlanner` | exploration_coverage | multi-goal/global planning reference | reference_only | low | moved |
| `ego-planner-swarm` | swarm_coordination | multi-UAV EGO planning | design_reference | medium | moved |
| `mader` | swarm_coordination | multi-agent trajectory deconfliction | design_reference | medium | moved |
| `rmader` | swarm_coordination | robust MADER reference | design_reference | medium | moved |
| `Swarm-Formation` | swarm_coordination | formation planning reference | active_runtime_blocked | high | moved; keep grouped path stable |
| `aerostack2` | experiment_platforms | UAV autonomy framework reference | reference_only | low | moved |
| `crazyswarm2` | experiment_platforms | swarm experiment stack | reference_only | low | moved |
| `crazychoir` | experiment_platforms | Crazyflie/choreography reference | reference_only | low | moved |
| `skybrush-server` | experiment_platforms | swarm ground/server reference | reference_only | low | moved |
| `visualize_uav_trajectory` | visualization | trajectory visualization/post-processing | reference_only | low | moved |

## New Eight Repositories

The new exploration/coverage repositories are all assigned to
`exploration_coverage`:

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

Priority for Factory indoor coverage:

```text
1. FALCON-ros1-noetic: first autonomous exploration candidate.
2. FC-Planner: first known-scene coverage/reconstruction fallback.
3. gbplanner_ros-gbplanner2: large-space graph exploration backup.
4. uav_frontier_exploration_3d: simpler frontier fallback.
5. nbvplanner and ExplorationRRT: algorithm references unless
   their old/heavy stacks are proven cheap to bridge.
6. SOAR: later heterogeneous reconstruction/photographing stage.
7. exploration-algorithms: survey/build reference only.
```

## Migration Batches Completed

Completed in this cleanup:

```text
1. Created the six Lab group directories.
2. Moved all 39 Lab repositories into their groups.
3. Rewrote current Docs/Scripts/Config references from
   References/Lab/<repo> to References/Lab/<group>/<repo>.
4. Kept upstream repositories intact; no internal package split was performed.
```

## Checks Required For Any Future Physical Move

For each moved repo:

```text
rg old-repo-name Docs Scripts Config References/Lab/README.md
Move-Item with explicit LiteralPath
rg old-path Docs Scripts Config
python -m py_compile for touched Python scripts
bash -n for touched shell scripts
git diff --check -- touched paths
```
