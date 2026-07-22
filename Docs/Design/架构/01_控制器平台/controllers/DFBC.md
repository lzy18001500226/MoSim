# DFBC

Status: IMPLEMENTED / MEASURED. Static ATTITUDE_THRUST backend, single-UAV
Gazebo tasks, Diff-Planner single-UAV, and Diff-Planner three-UAV regression
evidence are present. User-frozen acceptance is still pending.

Layer: nominal differential-flatness based controller.

Replaces: trajectory tracking controller; full performance may require lower
interface levels than first-stage `ATTITUDE_THRUST`.

Inputs: Basic version needs p/v/a/yaw. Full version may require jerk, snap,
yaw rate and yaw acceleration.

Outputs: Basic target is `ATTITUDE_THRUST`; full DFBC may output body-rate,
angular-acceleration or wrench-like targets and needs a separate release gate.

PX4 dependency: Basic version reuses PX4 inner loops. Full version may replace
or bypass part of the PX4 inner-loop abstraction.

MWORKS/codegen route: start with Basic, then add jerk/snap only when Trajectory
Server provides validated high-order references.

Gazebo/Sunray validation: minimum snap, figure-8, spiral and Diff-Planner or
EGO-reference B-spline tracking after reference continuity checks.

Current gate: G9-C Basic has a C++ `ATTITUDE_THRUST` backend under
`PX4CTRL_CORE_PROFILE=dfbc_basic`, static source/interface evidence, single-UAV
Gazebo evidence, Diff single-UAV evidence, and Diff three-UAV evidence.

Current implementation and static evidence:

```text
Results/g9/dfbc_basic_attitude_thrust_v1/source_audit/controller_source_audit.json
Results/g9/dfbc_basic_attitude_thrust_v1/g9c_static_gate_20260629_154935/RUN_MANIFEST.json
Results/sunray_ros1/g9c_dfbc_basic_takeoff_hover_land_kpxy12_kpz5_20260629_155515/RUN_MANIFEST.json
Results/sunray_ros1/g9c_dfbc_basic_figure8_disarm_kpxy12_kpz5_20260629_155844/RUN_MANIFEST.json
Results/sunray_ros1/g9c_dfbc_basic_spiral_disarm_kpxy12_kpz5_20260629_160231/RUN_MANIFEST.json
Results/sunray_ros1/g9c_dfbc_basic_step_x_g7_kpxy12_kpz5_20260629_160549/RUN_MANIFEST.json
Results/sunray_ros1/g9c_dfbc_basic_step_y_g7_kpxy12_kpz5_20260629_160850/RUN_MANIFEST.json
Results/sunray_ros1/g9c_dfbc_basic_step_z_g7_kpxy12_kpz5_20260629_161142/RUN_MANIFEST.json
Results/sunray_ros1/g9c_dfbc_basic_diff_single_auto123_kpxy12_kpz5_20260629_162158/RUN_MANIFEST.json
Results/sunray_ros1/g9c_dfbc_basic_diff_swarm_3uav_kpxy12_kpz5_20260629_162547/RUN_MANIFEST.json
Config/profiles/experiments/g9_dfbc_basic_figure8_v1.json
Scripts/sunray/px4ctrl_golden_slice/px4ctrl_g9c_dfbc_basic_gate.cpp
Scripts/sunray/px4ctrl_golden_slice/run_px4ctrl_g9c_dfbc_basic_gate.py
```

Basic DFBC mapping used in G9-C:

```text
flat output: p_d, v_d, a_d, yaw_d
feedback:    Kp * (p_d - p) + Kv * (v_d - v)
force:       m * (a_d + feedback + g e3)
attitude:    b3 = normalize(force), b1 from yaw, b2 = b3 x b1
output:      desired attitude quaternion + normalized thrust through px4ctrl adapter
```

This first-stage Basic route is intentionally close to the SE3 Basic
`ATTITUDE_THRUST` interface because both are constrained to p/v/a/yaw and reuse
PX4 attitude/rate loops. The full DFBC distinction is released only by a later
jerk/snap/body-rate or angular-acceleration gate.

Measured runtime summary:

```text
takeoff-hover-land steady XYZ RMSE: 0.0201 m
figure-8 XYZ RMSE: 0.0336 m
spiral XYZ RMSE: 0.0388 m
step_x / step_y / step_z: G7 trajectory gates passed
Diff single-UAV auto123: probe and Z audit passed
Diff three-UAV execute target errors: 0.0291 / 0.0165 / 0.0153 m
```

Forbidden claims: do not mechanically require jerk/snap for every controller;
only DFBC-Full and related high-dynamic variants require it. Do not claim
user-frozen G9-C acceptance, body-rate/torque-level DFBC, MWORKS-generated
acceptance, or PX4-native deployment from the historical G9-C Basic evidence.
