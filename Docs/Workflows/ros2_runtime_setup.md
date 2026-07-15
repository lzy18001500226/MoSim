# ROS2 Runtime Setup

> Fail-closed stub for historical/future ROS2 work. The former full workflow is
> archived at `Docs/Cache/legacy_workflows/ros2_runtime_setup_full_20260624.md`.

Status: historical/future reference only, 2026-06-24 CST.

## Current Rule

ROS2 is not the active MoSim runtime lane. Current executable review work uses:

```text
Ubuntu-20.04 / ROS1 Noetic
-> References/Sunray
-> Sunray150 + MID360
-> Gazebo Classic
-> PX4 + MAVROS
-> px4ctrl
-> RViz point-cloud, trajectory, map, and frame review
```

For current work, use:

```text
Docs/Design/架构.md
Docs/Workflows/mainline_operations_board.md
Docs/Workflows/sunray_ros1_current_runtime_lane.md
Docs/Workflows/sunray_ros1_execution_checklist.md
Docs/Index/sunray_migration_index.md
```

## Stop Conditions

If a task says Sunray, ROS1, Gazebo Classic, PX4/MAVROS, px4ctrl, RViz,
MID360, takeoff-hover-land, figure-8, spiral, trajectory gate, or current
runtime review, stop here and use the current ROS1/Sunray lane.

Do not run or cite these routes as current MoSim evidence:

```text
Ubuntu-22.04 / ROS2 Humble
PX4 x500 or x500_mid360
old Gazebo/ROS2 fixture runs
ROS2 direct actuator bridges
downloaded replacement FAST-LIO
old ROS2/RViz2 point-cloud display as active-lane acceptance
```

## Reopen Requirements

Read the archived full workflow only after all of the following are true:

```text
the user explicitly reopens ROS2/PX4/RViz2 work
Docs/Workflows/mainline_operations_board.md is updated for that route
Docs/Design/架构.md or a scoped design note states the new authority boundary
the task names whether it is source-static, diagnostic-only, or live runtime
```

Until then, ROS2 material is reference history and cannot be used to bypass a
blocked ROS1/Sunray task.
