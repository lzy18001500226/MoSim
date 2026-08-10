# Gazebo / PX4 / ROS2

Status: reviewed research decision draft, 2026-06-14.

Source raw notes:

- `research/raw/PX4-Autopilot.md`
- `research/raw/ROS2.md`
- `research/raw/RotorS.md`
- `research/raw/XTDrone.md`
- `research/raw/MAV层.md`

External sources:

- PX4 Simulation: https://docs.px4.io/main/en/simulation/
- PX4 Gazebo Simulation: https://docs.px4.io/main/en/sim_gazebo_gz/

## 1. Position

PX4 + Gazebo + ROS2 is the default exported-controller validation route for
CoSim after the current MWORKS-first competition slice. Gazebo supplies the
robotics simulation world and sensor source, PX4 owns flight-control authority
for normal UAV SITL/HIL semantics, and ROS2 supplies algorithm/middleware
integration. Gazebo+ROS2 without PX4 remains useful for point-cloud/map
fixtures and plant debugging, but it is not the formal flight-control
deployment route.

This route is closest to a deployable robotics workflow because it keeps:

```text
plant/world simulation
  != flight-control authority
  != algorithm bus
  != UE rendering
```

## 2. Best-Fit Vehicle Families

| Vehicle family | Fit | Reason |
|---|---|---|
| Multirotor | default | PX4 Gazebo simulation supports quadrotor models, sensor variants, SITL, and multi-vehicle workflows. |
| VTOL | default candidate | PX4 Gazebo lists standard VTOL, tailsitter, and tiltrotor targets; transition-control validation still needs vehicle-specific gates. |
| Fixed-wing | optional | PX4 Gazebo has plane targets, but serious aero model fidelity may favor JSBSim for fixed-wing truth. |
| Ducted model-aircraft | optional/reference | Useful if the vehicle is PX4/ArduPilot-like; less useful if direct actuator/high-speed aero dominates. |

## 3. Authority Classification

| Authority surface | Classification |
|---|---|
| Plant truth | Gazebo may own multirotor/VTOL plant truth in this route. |
| Flight-control authority | Formal route: generated C/C++ through PX4 Offboard or PX4 module/uORB, with PX4 owning mode, safety, estimator, controller/allocation, actuator output, and logs. Behavior-equivalent ROS2/C++ is fixture/pre-acceptance only. |
| ROS2 / algorithm bus | ROS2 owns SLAM/planner/perception/logging transport and algorithm integration, not plant truth. |
| UE / rendering frontend | UE consumes state/events and may produce optional visual sensor observations; it does not decide plant truth. |
| Sensor generation | Gazebo sensors are the default engineering sensor source; UE sensors are a separate optional profile. |
| RL / batch training | Not ideal as the fastest RL backend; use MuJoCo/Isaac/Genesis for high-throughput training, then validate here. |
| SIL / HIL / deployment | Strong route: PX4 supports SITL/HITL and real-hardware migration. |

## 4. Integration Pattern

```text
MWORKS controller evidence
  -> shared controller ABI
  -> generated C/C++ and SIL equivalence
  -> PX4 Offboard adapter or PX4 module/uORB adapter
  -> PX4 SITL/HITL flight stack
  -> Gazebo world / vehicle / sensors
  -> MAVLink / uXRCE-DDS / px4_ros_com where PX4/ROS2 integration is used
  -> ROS2 TF / point cloud / map / planner interfaces
  -> SLAM / local map / planner / mission logic
  -> command/setpoint path into PX4-compatible adapter
  -> logs, bags, ULog, metrics, replay
  -> UE render frontend consumes confirmed state and events
```

UE is not inserted between Gazebo and PX4 for plant truth. If UE generates a
sensor stream, it must be labelled as a UE sensor profile and evaluated
separately from Gazebo-native sensors.

## 5. Strengths

- Fast path to standard point-cloud/map/planner validation using Gazebo
  sensors and ROS2 without hand-rolling UE raycast first.
- Engineering-realistic autopilot route once PX4 is activated.
- PX4 SITL/HITL/real-hardware continuity for later deployment claims.
- ROS2 integration for TF, LiDAR, IMU, point cloud, local map, planner, and
  bags.
- Mature multi-vehicle and offboard-control references.
- Fits the user's intended route: MWORKS controller evidence first, Gazebo
  validation truth and sensors, ROS2 algorithms, UE rendering, and PX4 flight
  control when deployment semantics are needed.

## 6. Gaps And Risks

- Gazebo is not enough by itself for high-fidelity fixed-wing aero; use JSBSim
  when aero coefficient fidelity becomes central.
- PX4 integration can be slower to iterate than fixture-level Gazebo+ROS2
  probes; use fixtures for point-cloud/map and bridge proof, but do not confuse
  them with deployed flight-control evidence.
- Sensor realism must be explicitly profiled; nonzero topics are not evidence.
- Multi-UAV work needs namespaces, time sync, MAVLink system IDs, ROS2 domain
  strategy, and logging identity discipline.
- UE and Gazebo can drift visually/geometrically unless the scene identity and
  coordinate transform are governed by the shared core.

## 7. CoSim Adoption Decision

Decision: default backend route for exported-controller multirotor validation
is PX4+Gazebo+ROS2. PX4 is required for formal deployment, normal SITL/HIL,
mode/failsafe/QGC, and generated-controller runtime claims. Gazebo+ROS2
fixture probes may still be used before PX4 for point-cloud/map and bridge
proof.

It should not replace:

- MWORKS as the current competition evidence backend;
- JSBSim for fixed-wing aero truth;
- MuJoCo/Isaac/Genesis for high-throughput RL research.

## 8. Required Next Evidence

- Run identity schema that binds Gazebo world, controller backend, ROS2
  namespace, UE scene, vehicle ID, and evidence output.
- First validation smoke: PX4+Gazebo vehicle, arm/mode/hover/land, ULog or
  equivalent PX4 evidence, IMU/LiDAR topics, point cloud, and voxel/occupancy
  map.
- Fixture smoke before PX4 is allowed only for Gazebo model/sensor/bridge
  debugging and must be labelled as such.
- Sensor profile: IMU, LiDAR/depth, TF, timestamps, and topic rates.
- UE state mirror: confirmed pose/attitude/rotor/sensor-event sync without
  write-back to plant truth.
- Multi-UAV namespace and system-ID smoke before swarm claims.
