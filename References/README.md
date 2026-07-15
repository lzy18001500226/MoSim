# MoSim References

This directory stores local upstream/reference projects. These repositories are
reference material, not current runtime evidence by themselves.

Current MoSim runtime claims must still follow the active workflow and evidence
gates under `Docs/Workflows/` and `Docs/Design/`.

## Current Reference Groups

| Directory | Purpose |
| --- | --- |
| `Sunray/` | Current ROS1/Sunray/Gazebo Classic runtime baseline source. |
| `Lab/` | Planning, localization, and UAV research projects already used by MoSim. |
| `Control/` | Controller-specific reference implementations and papers' code. |
| `UAVStacks/` | End-to-end UAV engineering stacks such as XTDrone and Prometheus. |
| `PX4/` | PX4, MAVLink, MAVROS, PX4 messages, QGC, and related flight-control references. |
| `Gazebo/` | Gazebo/GZ source references and transport/simulation components. |
| `Simulation/` | External simulators, physics engines, RL/cosim environments, and comparison platforms. |
| `MWORKS/` | MWORKS reference material. |
| `RflySim/` | RflySim reference material. |
| `AirSim/` | AirSim reference material. |

## Organized Subgroups

| Directory | Purpose |
| --- | --- |
| `Control/geometric/` | Geometric and differential-flatness-style quadrotor control references. |
| `UAVStacks/ros_px4_gazebo/` | ROS/PX4/Gazebo full-stack UAV engineering references. |
| `Simulation/physics/` | General physics engines and differentiable/modern simulator backends. |
| `Simulation/rl/` | RL-oriented drone/control simulation environments. |
| `Simulation/mpc/` | MPC and optimal-control simulator references. |
| `Simulation/assets/` | Robot/vehicle model asset libraries used by simulators. |
| `Simulation/aviation/` | Flight dynamics and aerial robotics simulator references. |
| `Simulation/webots/` | Webots ROS2 integration references. |

## 2026-06-24 Intake

The following local repositories were moved from `C:\Users\HP\Desktop\新建文件夹`
into this reference tree:

```text
References/Control/geometric/Quadrotor_SE3_Control
References/UAVStacks/ros_px4_gazebo/XTDrone-master
References/UAVStacks/ros_px4_gazebo/Prometheus-main
References/PX4/PX4-Autopilot-main
References/Gazebo/gz-transport-main
References/Gazebo/gz-sim-main
References/Simulation/webots/webots_ros2-master
References/Simulation/physics/mujoco-main
References/Simulation/rl/mujoco_playground-main
References/Simulation/mpc/mujoco_mpc-main
References/Simulation/assets/mujoco_menagerie-main
References/Simulation/aviation/jsbsim-master
References/Simulation/rl/gym-pybullet-drones-main
References/Simulation/physics/genesis-world-main
References/Simulation/aviation/flightmare-master
References/Simulation/rl/dm_control-main
References/Simulation/physics/bullet-main
```

## Boundary

- `Simulation/` is primarily for simulator, RL, cosim, and comparison research.
  It is not the current Sunray ROS1 runtime lane.
- `UAVStacks/` is for engineering-pattern study. Adoption requires a separate
  architecture decision.
- `Control/` can inform controller design, but every controller must still be
  mapped to a MoSim/PX4 control-chain insertion point before implementation.
