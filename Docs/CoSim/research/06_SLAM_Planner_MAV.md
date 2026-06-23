# SLAM / Planner / MAV Layer

Status: reviewed research decision draft, 2026-06-14.

Source raw notes:

- `research/raw/Lidar SLAM.md`
- `research/raw/Planner.md`
- `research/raw/MAV层.md`
- `research/raw/Prometheus.md`
- `Docs/Design/MoSim_FASTLIO定位闭环与规划复现基础方案.md`

External sources:

- ROS2 concepts: https://docs.ros.org/en/humble/Concepts/
- MAVLink developer guide: https://mavlink.io/en/

## 1. Position

SLAM, local mapping, planning, MAVLink/MAVSDK/QGC, and autonomous mission
layers sit above the plant and flight-control backends. They should consume
labelled observations and estimates, not hidden plant or UE truth.

For multirotor autonomy, the route is:

```text
sensor observation
  -> localization / SLAM
  -> local map / ESDF / obstacle set
  -> planner / trajectory optimizer
  -> command adapter
  -> flight controller / plant
```

## 2. Best-Fit Vehicle Families

| Vehicle family | Fit | Reason |
|---|---|---|
| Multirotor | default autonomy stack | SLAM, point cloud, local map, planner, multi-UAV exploration, person-following. |
| Fixed-wing | optional | More GPS/mission oriented; local LiDAR SLAM may be less central. |
| VTOL | optional/default by mission | Needs mode-aware planner across hover/cruise/transition. |
| Ducted model-aircraft | limited | Short high-speed routes may use state/mission control more than full SLAM. |

## 3. Authority Classification

| Authority surface | Classification |
|---|---|
| Plant truth | No plant truth authority. |
| Flight-control authority | Sends requests/setpoints through an authority adapter; does not bypass autopilot safety. |
| ROS2 / algorithm bus | ROS2 is the default transport and evidence bus for robotics autonomy. |
| UE / rendering frontend | Displays maps, trajectories, and state; truth-map use must be labelled. |
| Sensor generation | Consumes sensor streams; does not create truth unless in debug/synthetic mode. |
| RL / batch training | May provide planner/policy interfaces for learning, but must export through contracts. |
| SIL / HIL / deployment | Requires replayable bags/logs, estimator quality, and command/echo checks. |

## 4. Integration Pattern

```text
SensorFrame / IMU / LiDAR / depth / camera
  -> ROS2 topics + TF
  -> FAST-LIO / mapping / perception
  -> LocalMapAdapter
  -> PlannerAdapter
  -> TrajectorySetpoint / MissionCommand
  -> PX4 / ArduPilot / controller adapter
  -> command echo + evidence bundle
```

For M0/M1 truth-map planning, UE or scene geometry may produce a labelled
occupancy map. That route is valid for sandbox/global planning, but it cannot
be reported as sensor-based SLAM autonomy.

## 5. Strengths

- ROS2 gives node/topic/service/action/parameter/rosbag/tf tooling.
- FAST-LIO-style pipelines provide established LiDAR-inertial odometry
  evidence routes.
- Planner systems such as Fast-Planner/EGO-style stacks clarify the need for
  local map, ESDF/voxel representation, dynamic constraints, and replanning.
- MAVLink/MAVSDK/QGC provide autopilot ecosystem compatibility and monitoring.

## 6. Gaps And Risks

- Fake transforms, renamed frames, GUI-only RViz displays, and nonzero topics
  are not sufficient evidence.
- Directly feeding UE global truth into planners hides the autonomy problem.
- MAVLink routing and system/component IDs become critical in multi-UAV runs.
- Person-following and obstacle avoidance require dynamic-object tracking and
  safety gating beyond static map planning.

## 7. CoSim Adoption Decision

Decision: default autonomy layer for multirotor and optional mission/autonomy
layer for other vehicle families.

## 8. Required Next Evidence

- Sensor/map artifact separation: truth occupancy map, sensor point cloud,
  local map/ESDF, planner trajectory.
- ROS2 TF/rate/timestamp checker.
- MAVLink system/component ID and routing policy for multi-vehicle runs.
- Planner input contract and command/echo gate.
- Dynamic target/person-following scenario contract before implementing that
  capability.
