# Backend Decision Matrix

Status: reviewed research decision draft, 2026-06-14.

This matrix summarizes current CoSim backend decisions. It is a design guide,
not implementation evidence.

| Backend / ecosystem | Primary CoSim role | Default vehicle family | Do not use it as |
|---|---|---|---|
| Gazebo / gz-sim | Robotics world, sensors, collision, multirotor/VTOL engineering simulation | Multirotor, VTOL | High-fidelity fixed-wing aero truth by default |
| PX4 | Flight-control stack, SITL/HIL/real route | Multirotor, VTOL | Simulator, renderer, SLAM/planner |
| ROS2 | Algorithm bus, TF, topics, bags, SLAM/planner integration | Multirotor autonomy, multi-UAV | Plant truth or flight-controller replacement |
| UE | Rendering, review, replay, experiment console, optional sensor frontend | All vehicle families | Default plant truth or hidden planner map |
| Simulink | Controller design, code generation, SIL/PIL/HIL | All vehicle families | World simulator or renderer |
| MWORKS | Current competition/modeling backend | Current A8 slice | Long-term single-platform lock-in |
| JSBSim | Fixed-wing/aircraft six-DOF FDM | Fixed-wing, ducted model-aircraft, VTOL cruise candidate | General robotics world or LiDAR/SLAM simulator |
| ArduPilot / ArduPlane | Fixed-wing autopilot route | Fixed-wing | Gazebo/PX4 replacement for multirotor by default |
| MuJoCo / MJX | Fast control/RL/direct actuator backend | Multirotor research, high-speed, future robotics | PX4/ArduPilot-equivalent deployment proof |
| Isaac Sim / Isaac Lab | GPU/sensor/RL robotics simulation | RL, perception, synthetic sensors | Lightweight default engineering route |
| Genesis | Future GPU/multi-physics/RL candidate | Research | Current default |
| Bullet / PyBullet | Lightweight physics/prototyping, reference RL examples | Research/prototyping | Final flight dynamics authority |
| Flightmare | Fast quadrotor dynamics + decoupled rendering reference | Multirotor RL/reference | Full engineering autopilot route |
| AirSim / Project AirSim | UE vehicle/sensor API architecture reference | UE frontend/reference | Default long-term plant without compatibility audit |
| Webots | General simulator/reference/education | Optional | Primary UAV engineering backbone |
| CARLA | Ground vehicle/traffic reference | Future ground vehicle | UAV flight dynamics backbone |

## Vehicle-Family Defaults

| Vehicle family | Plant truth default | Flight-control default | Algorithm bus | Frontend |
|---|---|---|---|---|
| Multirotor | Gazebo after competition; MWORKS for current A8 slice | PX4; Simulink/generated controller as replaceable backend | ROS2 | UE |
| Fixed-wing | JSBSim | ArduPlane or Simulink-generated controller | ROS2 optional | UE |
| VTOL | Gazebo/PX4 for engineering; JSBSim candidate for aircraft cruise studies | PX4 VTOL / ArduPilot QuadPlane / generated controller | ROS2 | UE |
| Ducted model-aircraft | JSBSim or custom six-DOF backend | ArduPilot/custom/generated controller depending on airframe | optional ROS2 | UE |
| RL/high-speed research | MuJoCo/Isaac/Genesis/Flightmare | direct policy/actuator, then exported controller | optional | UE or backend renderer |

## Open Design Questions

1. Which exact Simulink deployment target should be first: PX4 module, ROS2
   external controller, or direct C++ adapter?
2. Should UE sensors be allowed as autonomy input in formal gates, or only as
   visual/synthetic-data profiles?
3. For VTOL, should the first truth backend be PX4+Gazebo or JSBSim-based aero
   model?
4. For ducted model-aircraft, what fidelity level is needed first: animation,
   control-law research, or flight-envelope research?

