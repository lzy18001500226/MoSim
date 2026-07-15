# PID

Status: MEASURED / first replacement template.

Layer: nominal outer-loop controller.

Replaces: external position/velocity/height controller when used through
`ATTITUDE_THRUST`.

Inputs: position, velocity, attitude, angular velocity, p/v/a reference, yaw,
mass, gravity, PID gains, anti-windup limits, dt, reset, enable.

Outputs: `ATTITUDE_THRUST`; optional diagnostics for integral state, saturation
and stage status.

PX4 dependency: reuses PX4 attitude loop, rate loop and control allocation in
the first stage.

MWORKS/codegen route: official PID model -> unified interface -> generated C/C++
-> IController wrapper -> same Adapter as px4ctrl.

Gazebo/Sunray validation: takeoff/hover/land first, then step, figure-8 and
spiral.

Current gate: first simple controller proving that the controller template is
not px4ctrl-specific. G9-A has passed static C++ gate, takeoff-hover-land,
figure-8, spiral, step-x/y/z, Diff-Planner single-UAV auto goal chain, and
Diff-Planner three-UAV regression through the `official_pid` px4ctrl core
profile. It is measured evidence, not a user-frozen accepted baseline yet.

Runtime evidence:

```text
takeoff_hover_land: Results/sunray_ros1/g9a_official_pid_takeoff_hover_land_20260629_133037
figure8: Results/sunray_ros1/g9a_official_pid_figure8_disarm_20260629_134038
spiral: Results/sunray_ros1/g9a_official_pid_spiral_hover20_disarm_20260629_134810
step_x: Results/sunray_ros1/g9a_official_pid_step_x_g7_20260629_135217
step_y: Results/sunray_ros1/g9a_official_pid_step_y_g7_20260629_135514
step_z: Results/sunray_ros1/g9a_official_pid_step_z_g7_20260629_135813
Diff single-UAV: Results/sunray_ros1/g9a_official_pid_diff_single_auto123_20260629_140509
Diff three-UAV: Results/sunray_ros1/g9a_official_pid_diff_swarm_3uav_20260629_140943
```

Forbidden claims: PID variants are separate profiles; improved PID, fuzzy PID
and gain-scheduled PID cannot inherit baseline PID evidence automatically.
