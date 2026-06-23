# CoSim 总体蓝图

Status: discussion draft, 2026-06-14.

## 1. Product Position

CoSim is a future simulation software platform for model-aircraft, UAV, and
autonomous-system research. It is broader than the current A8 competition
implementation, but it must remain compatible with the current MoSim evidence
discipline.

CoSim should support:

- multirotor control, SLAM, planning, swarm, person-following, obstacle
  avoidance, reinforcement learning, and end-to-end experiments;
- fixed-wing model-aircraft simulation;
- VTOL / quadplane / transition-flight simulation;
- ducted model-aircraft and benign test-body simulation;
- controller design in MWORKS now and Simulink after competition;
- generated C/C++, SIL, HIL, and real-hardware migration;
- high-quality UE rendering and review;
- reproducible logs, metrics, replay, and evidence bundles.

CoSim should not become a monolithic simulator that tries to replace Gazebo,
JSBSim, PX4, ArduPilot, ROS2, Simulink, or UE. It should be a composable
platform that binds them with stable contracts.

## 2. Product Tree

```text
CoSim
  shared core
    experiment manager
    scenario/world registry
    vehicle registry
    clock and synchronization
    typed data contracts
    logging/evidence/replay
    backend adapter lifecycle
    safety and authority gates

  vehicle families
    multirotor
      single-UAV control
      SLAM / point cloud / local map
      planning / obstacle avoidance
      person-following
      swarm / formation / exploration
      reinforcement learning / end-to-end
      high-speed gate tasks

    fixed-wing
      aero model and six-DOF plant
      ArduPlane / generated controller
      GPS mission and route planning
      control surfaces, propulsion, landing gear
      UE flight visualization

    VTOL
      hover mode
      transition mode
      cruise mode
      transition-control and envelope protection
      PX4 VTOL / ArduPilot QuadPlane / generated controller paths

    ducted model-aircraft
      benign test-body simulation
      propulsion and attitude stabilization
      short-duration high-speed flight
      RC/autopilot/generated-controller adapters
```

## 3. Authority Model

Each run must declare one authority per surface:

| Surface | Examples | Rule |
|---|---|---|
| Plant truth | MWORKS, Gazebo, JSBSim, MuJoCo, Isaac | One vehicle entity has one plant-truth backend in a run. |
| Flight-control authority | PX4, ArduPilot, Simulink generated code, MWORKS controller, RL policy | Commands must go through an adapter and echo path. |
| Algorithm bus | ROS2, direct in-process API, training loop | Middleware does not automatically own truth. |
| Rendering frontend | UE, Gazebo GUI, RViz, Isaac renderer | Rendering does not prove controller/planner success. |
| Sensor source | Gazebo sensor, UE sensor, backend-native sensor, real replay | Sensor profile must be labelled. |
| Evidence source | logs, bags, ULog, screenshots, metrics, packets | Claims must point to reproducible evidence. |

Rejected architecture:

```text
UE hidden truth -> planner final evidence
Gazebo and JSBSim both integrating one aircraft state
RL direct motor success -> PX4 deployment success
visual pass -> controller or planner pass
```

## 4. Backend Defaults

| Vehicle family | Default plant route | Default flight-control route | Default algorithm route | Default frontend |
|---|---|---|---|---|
| Current A8 slice | MWORKS | MWORKS/Sysblock/Equation | optional ROS2 later | UE replay/review |
| Multirotor exported-controller validation | Gazebo | generated C/C++ through PX4 Offboard or PX4 module/uORB; direct ROS2 actuator bridge only as fixture | ROS2 / uXRCE-DDS | UE |
| Fixed-wing | JSBSim | ArduPlane + generated-controller adapters | ROS2 optional | UE |
| VTOL | Gazebo/PX4 first; JSBSim candidate for aero studies | PX4 VTOL / ArduPilot QuadPlane | ROS2 | UE |
| Ducted model-aircraft | JSBSim or custom six-DOF backend | custom/ArduPilot/generated controller | optional | UE |
| RL/high-speed research | MuJoCo/Isaac/Genesis/Flightmare | direct policy/actuator, then export | optional | UE or backend renderer |

## 5. Staged Roadmap

```text
Stage 0: current A8 competition closure
  -> MWORKS model/control evidence
  -> UE replay/review
  -> Syslab metrics

Stage 1: exported-controller multirotor validation
  -> MWORKS controller ABI
  -> generated C/C++ and SIL equivalence
  -> PX4 Offboard adapter or PX4 module/uORB adapter
  -> PX4 SITL + Gazebo + ROS2 + UE
  -> point cloud, 3D occupancy/voxel map, planner, command/echo
  -> single-UAV first; ROS2 direct-to-Gazebo actuator bridge remains fixture only

Stage 2: multirotor autonomy expansion
  -> deeper PX4/SITL/HIL and QGC workflows
  -> swarm, formation, exploration
  -> person-following and dynamic obstacle avoidance
  -> RL/end-to-end research backend with engineering revalidation

Stage 3: Simulink-generated controller migration
  -> controller ABI
  -> generated C/C++ SIL/PIL
  -> PX4/ArduPilot/external-controller wrappers

Stage 4: fixed-wing and VTOL families
  -> JSBSim/ArduPlane fixed-wing
  -> PX4 VTOL / ArduPilot QuadPlane / transition control
  -> UE aircraft visualization

Stage 5: ducted model-aircraft and special airframes
  -> benign simulation only
  -> propulsion/aero/control fidelity levels
  -> HIL and real-hardware migration only after safety review
```

## 6. Relation To Current MoSim Design

`Docs/Design` remains the source for current A8 quadrotor competition and
near-term implementation gates. `Docs/CoSim` is the future platform blueprint.

Current competition evidence is not blocked by CoSim's full Gazebo/PX4/ROS2
route unless a task explicitly claims those surfaces.

For current MoSim design, Gazebo should be treated as the default
system-validation plant/sensor backend after a controller has been exported or
wrapped behind the shared ABI. It should not replace MWORKS as the competition
controller-design, Sysblock integration, Syslab metric, or report-evidence
platform. UE remains the high-quality render/review frontend unless a separate
sensor-authority gate explicitly promotes UE raycast output into the autonomy
input path.

## 7. Open Questions For Review

1. Should the product name remain `MoSim` with `CoSim` as a future layer, or
   should `CoSim` become a separate platform name?
2. For the first Simulink migration, should generated code target PX4 Offboard
   first or a PX4 module/uORB adapter first?
3. Should UE sensors be formal autonomy inputs, or only visual/synthetic-data
   profiles until a later gate?
4. For VTOL, should the first serious route be PX4+Gazebo or JSBSim-based aero?
5. For ducted model-aircraft, what fidelity level is first: visual animation,
   control-law research, or flight-envelope research?
