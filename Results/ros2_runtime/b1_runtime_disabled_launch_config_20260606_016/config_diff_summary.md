# Runtime-Disabled Launch/Config Diff Summary

Task: `RFLY-MOSIM-ROS2-RUNTIME-B1-RUNTIME-DISABLED-LAUNCH-CONFIG-20260606-016`

Quality status: `runtime_disabled_static_config_only`

## Added Artifacts

- `Results/tmp/ego_planner_ros2_port_ws/src/plan_manage/launch/runtime_disabled_preflight.launch.py`
- `Results/tmp/ego_planner_ros2_port_ws/src/plan_manage/config/runtime_disabled_preflight.yaml`

The task packet names `src/ego_planner`, but the isolated workspace package
directory is `src/plan_manage` and its CMake project name is `ego_planner`.
The launch/config artifacts were therefore created under `src/plan_manage`
and installed under `install/ego_planner/share/ego_planner/`.

## Guard And Remap Summary

- `ego_planner_node_preflight` now has a `runtime_disabled` parameter guard.
  When true, it exits before initializing `EGOReplanFSM`, so planner
  publishers, subscribers, and timers are not created.
- `runtime_disabled_preflight.yaml` sets:
  - `ego_planner_node_preflight.ros__parameters.runtime_disabled: true`
  - `audit_only: true`
  - `evidence_boundary: runtime_disabled_static_config_only`
  - `traj_server_ros2_node.ros__parameters.publish_enabled: false`
- Legacy ROS1 slash-style parameters were translated to ROS2 dotted keys such
  as `fsm.flight_type`, `manager.max_vel`, `optimization.lambda_smooth`, and
  `grid_map.resolution`.
- Required local sensed input remaps were encoded:
  - `/odom_world` -> `/Odometry`
  - `/grid_map/odom` -> `/Odometry`
  - `/grid_map/cloud` -> `/cloud_registered`

## Static Validation

- Python launch syntax compile passed.
- YAML text validation found `runtime_disabled: true`,
  `publish_enabled: false`, and dotted parameter keys.
- Static guard/remap scans found the runtime guard and required remaps.
- Bounded colcon build/install succeeded on retry 2 and installed the launch
  and config artifacts.

## Evidence Boundary

No `ros2 launch` or `ros2 run` runtime was executed. No recorder ran. No
`/position_cmd` or `/planning/bspline` runtime evidence is claimed. This
artifact is ready only for a later PMO-approved runtime-disabled smoke gate.
