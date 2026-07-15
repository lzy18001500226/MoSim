# Factory L2 Indoor Coverage Requirements And Planner Survey

Status: draft decision cache, 2026-07-03.

This note freezes the requirement clarification before any further Factory L2
full-coverage runtime work. It is intentionally placed in cache first. Promote
only the accepted conclusion into formal design docs.

## 1. Core Correction

TARE must not be treated as the default Factory indoor answer.

TARE is valuable because it exposes coverage-oriented concepts such as
coverage boundary, navigation boundary, uncovered cloud, frontier cloud,
exploration finish, global path, local path, and waypoint output. However, the
local implementation is explicitly a ground-vehicle planner. Its assumptions
around terrain map, viewpoint height, and ground-style navigation do not match
the MoSim UAV requirement directly.

For MoSim, the primary requirement is:

```text
online UAV sensor input
  -> unknown-space exploration or coverage planning
  -> executable UAV trajectory / waypoint stream
  -> Planner Adapter / Trajectory Server
  -> px4ctrl / PX4 / MAVROS / Gazebo
  -> cumulative point cloud / occupancy / coverage packet
```

TARE may remain a reference or backup, but it cannot be promoted until a
specific UAV-adaptation audit proves how its ground-vehicle assumptions are
removed or contained.

## 2. Requirement Split

Factory L2 indoor full coverage is not one single requirement. It must be
split into four different claims:

| Claim | Meaning | Required proof |
| --- | --- | --- |
| Local autonomous exploration | The UAV can start from an unknown local area and keep producing safe exploration commands. | Online cloud/odom input, planner output, safe flight, local map growth. |
| Full indoor coverage mapping | The accepted indoor envelope is sufficiently observed and accumulated. | Quantitative coverage packet over `Config/gazebo/scene_profiles/factory_l2_exploration_envelope.json`. |
| UAV trajectory executability | Planner output can be followed by our control chain without unsafe Z/attitude/velocity behavior. | px4ctrl/PX4/MAVROS/Gazebo logs and trajectory metrics. |
| Display/review acceptance | RViz/UE shows coherent point cloud, occupancy/grid, UAV pose, and trajectory. | Visual review after backend metrics pass. |

Do not use one claim to prove another. For example, a local RACER run with
nonempty frontier does not prove full indoor coverage; a UE display screenshot
does not prove Gazebo/PX4 planning success.

## 3. Current Factory Boundary

Use the accepted indoor wall/fence envelope:

```text
x: [-98.40496, 77.25491] m
y: [-51.36291, 12.63665] m
size: about 175.7 m x 64.0 m
first z policy: fixed target z=1.2 m, command band [0.9, 1.6] m
pointcloud review band: [0.2, 4.0] m
```

This is a large indoor UAV task. A planner that was originally designed for
small pillar maps or a ground robot cannot be assumed to cover it without a
source and interface audit.

## 4. Candidate Families

| Candidate | Type | Fit for MoSim Factory | Current judgment |
| --- | --- | --- | --- |
| FUEL | Single-UAV fast UAV exploration using frontier information and minimum-time trajectories. | Strong UAV fit, already locally integrated, but current Factory evidence stayed local. | Keep as local single-UAV exploration baseline; do not claim full indoor coverage without new coverage strategy. |
| RACER | Decentralized multi-UAV exploration for quadrotor fleets. | Strong multi-UAV fit, already locally integrated, but current Factory evidence stayed local. | Keep for multi-UAV autonomous exploration and collision/coordination gates. |
| FALCON | Fast autonomous aerial exploration using coverage-path guidance. | Very relevant: explicitly aerial, online exploration, coverage guidance, ROS1 Noetic branch exists. | First external candidate for autonomous full-coverage exploration, but dependency cost must be audited before import. |
| CERLAB UAV Autonomy | Modular UAV autonomy framework from CMU CERLAB, including simulator, perception, map manager, global planner, trajectory planner, tracking controller, navigation, exploration, and inspection demos. | Strong UAV fit and ROS Noetic/PX4 relevance; broader than FUEL because it includes the autonomy glue, but likely higher integration cost because it may expect RGB-D/depth image and its own simulator/controller assumptions. | High-priority source audit candidate for single-UAV unknown exploration; first classify interfaces before any runtime import. |
| HighStar | High-speed online exploration for UAVs, with ROS Noetic/catkin source and launch/config sets for maze, forest, city, indoor, pillars, and powerplant demos. | Strong UAV fit and newer than FUEL; potentially useful if Factory failure is caused by weak exploration expansion rather than runtime plumbing. Integration risk: upstream demo uses modified RotorS, so MoSim proof requires an adapter to the current Sunray/PX4/MAVROS/px4ctrl evidence chain. | High-priority local source-audit candidate for single-UAV unknown exploration after FUEL issue review. |
| C2-Explorer | Contiguous and collaborative de-centralized multi-UAV exploration. | Strong conceptual fit for the later multi-UAV full-coverage gap because it explicitly targets collaboration and contiguous task allocation. | High-priority external multi-UAV candidate; audit after single-UAV route is chosen or in parallel as a source-only review. |
| EPIC | Exploration planning with implicit coordination, from the same recent exploration-planning ecosystem. | Potential bridge between single/multi-agent exploration policy and our multi-UAV coverage blocker, but source/runtime fit must be verified. | Medium-priority external candidate; keep behind HighStar/C2-Explorer. |
| FC-Planner | Fast aerial coverage planner for complex 3D scenes. | Very relevant to full-coverage mapping; README says it accepts surface point cloud input, so it is closer to known-scene coverage/reconstruction than unknown online exploration. | First candidate for coverage-mapping fallback if we can derive a clean Factory surface cloud. |
| SOAR | Heterogeneous multi-UAV exploration and photographing for reconstruction. | Relevant for later reconstruction/UE review, heavier than current single-UAV coverage gate. | Later-stage candidate, not first implementation. |
| GBPlanner2 | Graph-based exploration for subterranean environments with aerial and legged robots. | More UAV-relevant than TARE for large 3D spaces; heavier stack. | Better backup than TARE if FALCON/FC-Planner are unavailable or too costly. |
| NBVPlanner | Receding-horizon next-best-view planner for 3D exploration. | Classic MAV exploration reference, but README targets old ROS Indigo/Jade and RotorS-style stack. | Use as algorithm/interface reference, not first implementation. |
| UAV Frontier Exploration 3D | Multi-resolution frontier-based planner for autonomous 3D exploration. | UAV-specific and conceptually simple frontier route; repo activity and ROS version need audit. | Medium-priority candidate if FALCON/GBPlanner are too heavy. |
| ExplorationRRT | Tree-based next-best-trajectory method for 3D UAV exploration using UFOmap and NMPC. | UAV-specific, outputs pose reference or trajectory, but Docker/RotorS/NMPC stack is heavy. | Good research candidate, high integration cost. |
| exploration-algorithms | Survey/build repo for many exploration algorithms with Docker. | Useful as a meta-reference for NBVP/GBP/GBP2/MBP/AEP/UFOExplorer/FUEL/DSVP/TARE/OIPP/PredRecon. | Use for route survey and reproducibility hints, not direct MoSim proof. |
| TARE | Hierarchical exploration framework with strong coverage semantics. | Current code is ground-vehicle oriented; needs terrain/state/height adaptation. | Reference/back-up only until UAV-adaptation audit passes. |
| Scripted lawnmower / tiling | Engineering coverage route over the accepted indoor boundary. | Can prove cumulative mapping and display/load capacity, but not unknown autonomous exploration. | Valid fallback; must be labeled scripted coverage mapping. |

## 5. Source Notes

The candidate pool is not limited to local references. Use local code when it
already exists, but online open-source projects must be surveyed before
choosing an implementation route.

Local references already present:

```text
References/Lab/exploration_coverage/FUEL
References/Lab/exploration_coverage/RACER
References/Lab/exploration_coverage/FALCON-ros1-noetic
References/Lab/exploration_coverage/CERLAB-UAV-Autonomy
References/Lab/exploration_coverage/HighStar
References/Lab/exploration_coverage/FC-Planner
References/Lab/exploration_coverage/SOAR
References/Lab/exploration_coverage/gbplanner_ros-gbplanner2
References/Lab/exploration_coverage/uav_frontier_exploration_3d
References/Lab/exploration_coverage/nbvplanner
References/Lab/exploration_coverage/ExplorationRRT
References/Lab/exploration_coverage/exploration-algorithms
References/Lab/exploration_coverage/tare_planner-melodic-noetic
References/Lab/exploration_coverage/fast_multi_robot_exploration
References/Lab/swarm_coordination/Swarm-Formation
References/Lab/planning_local/Fast-Planner
References/Lab/planning_local/GCOPTER
```

The same candidates were originally identified by online/source survey. The
local copies above are now the first source to inspect before any new download.
Upstream URLs are retained for provenance:

```text
FALCON: https://github.com/HKUST-Aerial-Robotics/FALCON, branch `ros1-noetic`;
  README states Ubuntu 20.04 / ROS Noetic testing and dependencies including
  CMake 3.20+, NLopt 2.7.1, and Open3D 0.18.0.
CERLAB UAV Autonomy: https://github.com/Zhefan-Xu/CERLAB-UAV-Autonomy;
  README states ROS Melodic/Noetic testing, PX4 simulation support, and
  dependencies including octomap, MAVROS, and vision_msgs. The current local
  copy under `References/Lab/exploration_coverage/CERLAB-UAV-Autonomy` is a
  top-level skeleton with empty submodule directories, so build/runtime audit
  requires a recursive source refresh before use.
FC-Planner: https://github.com/HKUST-Aerial-Robotics/FC-Planner, branch
  `master`; README states ROS Noetic/Melodic support and surface point cloud
  as application input.
SOAR: https://github.com/Robotics-STAR-Lab/SOAR
GBPlanner ROS: https://github.com/ntnu-arl/gbplanner_ros
NBVPlanner: https://github.com/ethz-asl/nbvplanner
UAV Frontier Exploration 3D: https://github.com/larics/uav_frontier_exploration_3d
ExplorationRRT: https://github.com/LTU-RAI/ExplorationRRT
Exploration Algorithms survey/build repo:
  https://github.com/engcang/exploration-algorithms
FUEL: https://github.com/HKUST-Aerial-Robotics/FUEL
RACER: https://github.com/Robotics-STAR-Lab/RACER
HighStar: https://github.com/NKU-MobFly-Robotics/HighStar;
  local copy exists at `References/Lab/exploration_coverage/HighStar`.
  README states Ubuntu 20.04 / ROS Noetic, dependencies including octomap,
  MAVROS, protobuf, glog, and control_toolbox, and a modified RotorS
  simulation environment.
C2-Explorer: https://github.com/Robotics-STAR-Lab/C2-Explorer
EPIC: https://github.com/Robotics-STAR-Lab/EPIC
```

External candidates still worth fetching, in priority order:

```text
1. C2-Explorer: multi-UAV collaborative exploration with contiguous allocation.
2. EPIC: related recent implicit-coordination exploration planner.
```

HighStar is already present locally:

```text
References/Lab/exploration_coverage/HighStar
```

Do not prioritize reconstruction/inspection-only planners such as PredRecon,
FC-Vision, or FlyCo as the current unknown-exploration mainline. Keep them for
later UE review, reconstruction, or known-scene scanning/photographing work.

## 6. Recommended Route

Do not continue with blind TARE build/runtime work.

Use this route instead:

```text
R0 requirement freeze:
  Freeze the four claims above and define coverage metric.

R1 UAV planner source survey:
  Inspect FALCON, CERLAB UAV Autonomy, HighStar, C2-Explorer, EPIC,
  FC-Planner, GBPlanner2, NBVPlanner, UAV Frontier Exploration 3D,
  ExplorationRRT, and the exploration-algorithms survey repo.
  Check license, ROS version, build burden, expected map input, output type,
  whether it needs prior global mesh/PCD, and whether output can enter
  Planner Adapter / Trajectory Server.

R2 choose implementation branch:
  If FALCON is buildable and accepts online map/cloud from MoSim:
    use it as single-UAV autonomous full-coverage candidate.
  Else if CERLAB UAV Autonomy can consume MoSim odometry plus lidar/depth-derived map
  and publish bridgeable goal/trajectory/control commands:
    use it as a single-UAV autonomy-framework candidate before writing new
    supervisor code.
  Else if HighStar has a smaller bridgeable ROS Noetic interface:
    use it as the next single-UAV unknown-exploration candidate.
  Else if FC-Planner can generate a safe coverage path over a Factory surface cloud:
    use it for scripted/known-scene coverage mapping, not unknown exploration.
  Else if GBPlanner2 is buildable enough:
    use it as large-space exploration backup.
  Else if UAV Frontier / NBVPlanner / ExplorationRRT provides a smaller
  bridgeable UAV interface:
    use that as the autonomous exploration candidate.
  Else:
    use scripted coverage mapping over the accepted indoor envelope.

R3 runtime gate:
  Run bounded single-UAV Factory gate first.
  Only after single-UAV coverage grows beyond the local 4 percent baseline,
  open three-UAV or long-run gates.

R4 claim boundary:
  Autonomous exploration and scripted coverage mapping must be reported as
  different capabilities.
```

## 7. Acceptance Metrics

Minimum quantitative metrics for Factory indoor coverage:

```text
coverage_ratio >= 0.80 over accepted indoor envelope;
all sampled truth/odom/command XY inside envelope;
command z inside [0.9, 1.6] m unless a terrain-aware gate is approved;
no roll/pitch/velocity safety violation;
cumulative point cloud and occupancy/grid counts increase coherently;
planner trajectory is nonempty and executable through current control chain;
runtime logs have no fatal Gazebo/PX4/MAVROS/planner errors.
```

If no open-source planner can satisfy the autonomous full-coverage route within
reasonable integration cost, the correct decision is not to hand-write a new
exploration system. The correct fallback is scripted coverage mapping for the
Factory review, clearly labeled, while keeping FUEL/RACER as autonomous local
exploration evidence.
