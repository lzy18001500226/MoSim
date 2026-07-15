# TARE / GBPlanner2

Status: REFERENCE / large-environment exploration and backup comparison route.

Sources:

```text
References/Lab/exploration_coverage/tare_planner-melodic-noetic
References/Lab/exploration_coverage/gbplanner_ros-gbplanner2
```

Role: both projects are strong exploration references. FUEL and RACER were the
first MoSim implementation targets because they matched the current UAV,
frontier/B-spline and multi-UAV exploration line directly. After the 2026-07-03
Factory L2 indoor evidence, TARE is promoted from passive backup to the next
source-first candidate for full indoor coverage mapping. GBPlanner2 remains a
larger backup route unless TARE cannot be built or bridged.

## TARE Observations

Observed local source entry:

```text
References/Lab/exploration_coverage/tare_planner-melodic-noetic/README.md
References/Lab/exploration_coverage/tare_planner-melodic-noetic/src/tare_planner/launch/explore_*.launch
References/Lab/exploration_coverage/tare_planner-melodic-noetic/src/tare_planner/config/*.yaml
```

Upstream notes:

```text
tested on Ubuntu 18.04/ROS Melodic and Ubuntu 20.04/ROS Noetic
uses a local dense planning horizon plus sparse global exploration layer
uses OR-Tools for optimization
expects CMU autonomous exploration development environment / vehicle_simulator
```

MoSim use:

```text
Factory L2 indoor full-coverage mapping candidate
large complex world comparison
forest, tunnel, indoor, garage, campus, matterport style scenes
fallback if FUEL/RACER exploration quality or map size becomes insufficient
```

TARE has coverage-specific source surfaces that FUEL/RACER do not expose as
cleanly in the current MoSim Factory route:

```text
coverage_boundary / navigation_boundary
uncovered_cloud
uncovered_frontier_cloud
frontier_cloud / filtered_frontier_cloud
grid_world visualization
global_path / local_path / exploration_path
exploration_finish
/way_point
```

Factory L2 adoption starts with source-first gates, not a blind Gazebo run:

```text
TARE-F0 source audit:
  README, explore_indoor.launch, explore.launch, indoor.yaml,
  planning_env and sensor_coverage_planner_ground source.

TARE-F1 isolated build:
  rospack find tare_planner must pass in a MoSim-isolated workspace.

TARE-F2 bridge dry-run:
  /uav1/livox_world -> /registered_scan
  odom/pose -> /state_estimation_at_scan
  Factory indoor boundary -> coverage/navigation boundary topic
  /way_point -> MoSim Planner Adapter / Trajectory Server

TARE-F3 Factory single-UAV runtime:
  clean Factory world, online sensor input, fixed-z policy first,
  coverage packet plus uncovered/frontier/finish evidence.
```

Primary integration risk:

```text
the upstream development environment and vehicle simulator are a separate
runtime stack; adapting it to Sunray/PX4/MAVROS requires a larger interface
audit than FUEL/RACER.
```

## GBPlanner2 Observations

Observed local source entry:

```text
References/Lab/exploration_coverage/gbplanner_ros-gbplanner2/README.md
References/Lab/exploration_coverage/gbplanner_ros-gbplanner2/gbplanner/launch
References/Lab/exploration_coverage/gbplanner_ros-gbplanner2/planner_msgs
References/Lab/exploration_coverage/gbplanner_ros-gbplanner2/gbplanner/config
```

Upstream notes:

```text
ROS Melodic/Noetic support
requires catkin_tools, glog, octomap, voxblox-style mapping components
contains aerial and ground robot demos
exposes planner services such as planner_go_to_waypoint, planner_global,
planner_search, planner_set_global_bound and planner_set_exp_mode
```

MoSim use:

```text
graph-based exploration comparison
planner service/interface reference
large-scale or mixed-robot exploration architecture reference
possible UI/service-command inspiration for later QGC or experiment platform
```

Primary integration risk:

```text
the stack is broader than the current UAV-only Sunray lane and may pull in
mapping, control-interface and simulator assumptions that do not match MoSim's
current FAST-LIO/Sunray/PX4 contracts.
```

## Adoption Rule

Open TARE/GBPlanner2 only after at least one of these is true:

```text
FUEL single-UAV exploration cannot satisfy the required map size or coverage;
RACER multi-UAV exploration cannot satisfy coordination/coverage needs;
the user explicitly asks for large-scale/subterranean/forest exploration;
the project needs a second independent exploration baseline for comparison.
```

This condition is now met for Factory L2 indoor full coverage: FUEL is accepted
only as a local single-UAV baseline, and RACER single-/three-UAV Factory runs
remain local coverage evidence rather than full-boundary coverage proof.

Any adoption must preserve the same control boundary:

```text
exploration output
  -> Planner Adapter
  -> Trajectory Server
  -> controller
  -> MAVROS/PX4/Gazebo
```

TARE/GBPlanner2 must not own final MAVROS control publication, and their
native simulators cannot replace the current Sunray/Gazebo/PX4 proof unless
the run is explicitly marked as upstream-only smoke evidence.
