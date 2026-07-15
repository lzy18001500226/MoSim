# MoSim Lab Reference Index

Status: physical grouped index, 2026-07-03.

This directory stores research repositories used for MoSim planning,
localization, mapping, exploration, formation, and UAV experiment-platform
study. Keep upstream repositories intact. Do not split internal packages into
other `References/` buckets unless a separate dependency audit updates every
script and document reference.

## Sorting Rule

Use the repository's primary MoSim reuse role:

```text
active runtime dependency -> keep its grouped path stable
design/runtime candidate  -> index under its grouped path, then promote through a gate
survey/reference only     -> keep as source reference, not proof of MoSim runtime
```

Mixed repositories are expected. A planner repo may include mapping,
controller, simulator, RViz, and message packages. Record secondary tags in
docs instead of copying those packages out of the upstream tree.

## Physical Layout

```text
References/Lab/
  localization_slam/
  planning_local/
  exploration_coverage/
  swarm_coordination/
  experiment_platforms/
  visualization/
```

## Current Groups

### Active Runtime Dependencies

These paths are already referenced by MoSim scripts, configs, or current
workflow docs. They have been moved into grouped paths and should stay stable
unless a later dependency rewrite updates every reference again.

| Repo | Current path | Primary role | Notes |
| --- | --- | --- | --- |
| `FAST_LIO` | `References/Lab/localization_slam/FAST_LIO` | ROS1 FAST-LIO localization/mapping | Current local FAST-LIO source candidate. |
| `Diff-Planner` | `References/Lab/planning_local/Diff-Planner` | Known-goal single/multi-UAV planning | Current fixed-goal engineering baseline. |
| `Fast-Drone-250` | `References/Lab/planning_local/Fast-Drone-250` | px4ctrl and quadrotor messages | Used by px4ctrl and planner overlays. |
| `FUEL` | `References/Lab/exploration_coverage/FUEL` | Single-UAV exploration baseline | Factory evidence is local coverage only. |
| `RACER` | `References/Lab/exploration_coverage/RACER` | Multi-UAV exploration baseline | Factory evidence is local coverage only. |
| `Swarm-Formation` | `References/Lab/swarm_coordination/Swarm-Formation` | Formation planning reference | Currently blocked as full runtime route, still indexed. |

### Localization, SLAM, And Drivers

| Repo | Primary role | Secondary tags |
| --- | --- | --- |
| `FAST_LIO` | LiDAR-inertial odometry/mapping | ROS1, MID360, point cloud, odometry |
| `FASTLIO2_ROS2` | ROS2 FAST-LIO2 reference | future ROS2 route only |
| `FAST-LIVO2` | LiDAR-visual-inertial reference | Livox headers, visual-inertial reference |
| `Point-LIO-point-lio-with-grid-map` | Point-LIO and grid-map reference | high-rate odometry, mapping comparison |
| `livox_ros_driver2` | Livox ROS2 driver reference | driver/API reference |
| `livox_ros_driver_compat` | Livox compatibility driver | ROS1 compatibility support |

### Local Planning And Trajectory Optimization

| Repo | Primary role | Secondary tags |
| --- | --- | --- |
| `Diff-Planner` | Known-goal planning baseline | local grid map, trajectory, swarm route |
| `ego-planner` | EGO-Planner v1 reference | B-spline, local replanning |
| `EGO-Planner-v2` | EGO-Planner v2 reference | swarm playground, local replanning |
| `Fast-Planner` | Fast-Planner stack | A*, B-spline, plan env |
| `GCOPTER` | Trajectory optimization | polynomial/minco optimization |
| `SUPER` | Perception/planning reference | ROG-map, mission planner |
| `faster` | fast replanning reference | local planner |
| `far_planner-melodic-noetic` | FAR planner reference | ROS1 Noetic/Melodic planning |
| `Fast-Racing` | high-speed/racing planning | agile planning reference |
| `Fast-Drone-250` | px4ctrl and racing stack | controller-adjacent, message packages |

### Exploration And Coverage Candidates

These are the main candidates for the Factory indoor full-coverage problem.
They are not interchangeable. Promote them only after source audit, build
gate, topic bridge check, and bounded Factory runtime evidence.

| Repo | Primary role | Current MoSim judgment |
| --- | --- | --- |
| `FUEL` | Fast UAV frontier exploration | Local baseline only; not full Factory coverage primary. |
| `RACER` | Decentralized multi-UAV exploration | Strong multi-UAV baseline; current coverage stayed local. |
| `FALCON-ros1-noetic` | Fast autonomous aerial exploration using coverage-path guidance | Highest-priority autonomous full-coverage candidate. |
| `FC-Planner` | Skeleton-guided aerial coverage of known complex 3D scenes | Strong known-scene coverage/reconstruction candidate. |
| `SOAR` | Heterogeneous UAV exploration and photographing for reconstruction | Later reconstruction/UE-review candidate. |
| `gbplanner_ros-gbplanner2` | Graph-based exploration for aerial/legged robots | Heavy but relevant large-space backup. |
| `uav_frontier_exploration_3d` | Multi-resolution 3D frontier exploration | Medium-priority UAV frontier fallback. |
| `nbvplanner` | Receding-horizon next-best-view exploration | Classic algorithm reference; old ROS/Rotors stack. |
| `ExplorationRRT` | RRT next-best-trajectory UAV exploration | Useful but heavy Docker/UFOmap/NMPC stack. |
| `exploration-algorithms` | Exploration algorithm survey/build collection | Meta-reference, not direct runtime proof. |
| `tare_planner-melodic-noetic` | Hierarchical exploration reference | Ground-vehicle-oriented local source; backup only. |
| `fast_multi_robot_exploration` | FAME/RACER related multi-robot exploration | RACER/FAME comparison reference. |
| `3dmr` | 3D multi-robot/exploration reference | candidate survey/reference |
| `MGGPlanner` | multi-goal/global planning reference | candidate survey/reference |

### Swarm Coordination And Formation

| Repo | Primary role | Secondary tags |
| --- | --- | --- |
| `ego-planner-swarm` | multi-UAV EGO planning reference | swarm replanning |
| `mader` | multi-agent trajectory deconfliction | communication, collision avoidance |
| `rmader` | robust MADER reference | delay/robust trajectory exchange |
| `Swarm-Formation` | formation planning/reference | known target, formation, not exploration |

### Experiment Platforms And Ground Systems

| Repo | Primary role | Secondary tags |
| --- | --- | --- |
| `aerostack2` | UAV autonomy framework reference | ROS2/future platform reference |
| `crazyswarm2` | Crazyflie swarm stack | swarm experiment organization |
| `crazychoir` | Crazyflie/choreography reference | swarm demo reference |
| `skybrush-server` | swarm ground server reference | UI/operator/system interface reference |

### Visualization And Reporting

| Repo | Primary role | Secondary tags |
| --- | --- | --- |
| `visualize_uav_trajectory` | trajectory visualization/reference | report/video post-processing |

## Physical Move Policy

The 2026-07-03 grouping move is complete. Future moves should be rare and
path-limited. If a repository changes group later, migrate it in this order:

```text
1. inspect old references
2. move one repo or one small batch
3. update all scripts/configs/docs
4. run targeted checks
```

Each batch needs:

```text
rg old-path Docs Scripts Config
move path
update all references
targeted syntax checks for touched scripts
git diff --check -- touched paths
```


