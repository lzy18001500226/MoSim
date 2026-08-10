# Multirotor Family

Status: discussion draft, 2026-06-14.

## 1. Scope

This family covers:

- quadrotor and multirotor control;
- current A8/Sunray-150 style model work;
- SLAM, point cloud, local map, 3D voxel map, and path planning;
- person-following and autonomous obstacle avoidance;
- formation, swarm, and exploration;
- reinforcement learning and end-to-end policies;
- high-speed gate and agile-flight experiments;
- SIL/HIL/real-hardware migration.

## 2. Default Route

| Stage | Plant truth | Flight control | Algorithm bus | Frontend |
|---|---|---|---|---|
| Current A8 competition | MWORKS | MWORKS Sysblock/Equation | optional / later ROS2 | UE replay/review |
| Exported-controller validation | Gazebo | generated C/C++ through PX4 Offboard or PX4 module/uORB; direct ROS2 actuator bridge only as fixture | ROS2 / uXRCE-DDS | UE |
| RL/high-speed research | MuJoCo/Isaac/Genesis/Flightmare | direct policy or controller | optional | UE or backend renderer |

## 3. Capability Tree

```text
multirotor
  nominal single-UAV control
    PID baseline
    improved PID / INDI / MPC / NMPC / L1 / safety filter
    fault allocation and motor-effectiveness degradation

  perception and mapping
    simulated IMU/LiDAR/depth/camera
    ROS2 point cloud
    FAST-LIO or localization backend
    local voxel/ESDF map
    truth-map sandbox for early planning only

  planning and autonomy
    global truth-map planning sandbox
    local map planning
    obstacle avoidance
    dynamic-object/person-following
    trajectory smoothing and command echo

  multi-UAV
    identity and namespace
    per-UAV plant/control/log separation
    formation
    swarm exploration
    decentralized and centralized modes

  RL / end-to-end
    direct actuator training backend
    domain randomization
    policy export
    engineering revalidation in Gazebo/PX4
```

## 4. Key Architecture Decisions

1. MWORKS remains valid for current competition model/control evidence.
2. PX4+Gazebo+ROS2 is the default exported-controller validation route for
   normal multirotor SITL behavior, point cloud, 3D occupancy/voxel map, and
   planner integration after generated controller code has SIL evidence.
   Direct ROS2 actuator control is useful only as a fixture/pre-acceptance
   bridge.
3. UE is the display/review/frontend route and may generate labelled sensor
   observations only after sensor-profile gates.
4. MuJoCo/Isaac/Genesis/Flightmare can train or research controllers faster,
   but their direct-actuator success is not PX4 deployment success.
5. Person-following requires dynamic-object observation, target identity,
   safety distance, occlusion handling, and command-limit rules.

## 5. First Architecture Gaps

- Unified multirotor `VehicleProfile` across MWORKS, Gazebo, PX4, UE, and RL
  backends.
- PX4+Gazebo+ROS2 smoke with one vehicle, one generated-code integration
  level, and one sensor profile; direct Gazebo actuator smoke stays separate as
  fixture evidence.
- UE state/replay mirror with coordinate and scale checks.
- ROS2 local-map and planner handoff gate.
- Multi-UAV namespace/system-ID policy.
