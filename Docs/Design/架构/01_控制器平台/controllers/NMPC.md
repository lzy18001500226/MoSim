# NMPC

Status: IMPLEMENTED / MEASURED for the first short-horizon
`ATTITUDE_THRUST` backend. Static, Gazebo basic trajectory, Diff single-UAV,
and Diff three-UAV runtime evidence are present. User-frozen acceptance is
pending.

Layer: nominal nonlinear optimal controller.

Replaces: outer-loop or lower-level controller depending on output interface.

Inputs: nonlinear plant model, state, reference horizon, constraints, weights,
solver warm start, dt, reset, enable.

Outputs: v1 targets `ATTITUDE_THRUST`. Later releases may target
`BODY_RATE_THRUST`, `WRENCH` or lower levels, but each output layer must be
released as a separate profile.

PX4 dependency: v1 reuses PX4 attitude loop, rate loop and allocation. It does
not silently bypass PX4 inner loops.

MWORKS/codegen route: MWORKS model and solver feasibility -> generated/wrapped
core -> deadline and fallback checks -> Gazebo validation. Historical G9-F C++
backend is a bounded short-horizon surrogate used to prove the G9 interface and
evidence route before a full generated solver is released.

Gazebo/Sunray validation: baseline trajectories, aggressive trajectories,
constraint violation and solver failure recovery.

Current gate: G9-F has a C++ `ATTITUDE_THRUST` backend under
`PX4CTRL_CORE_PROFILE=nmpc_outer`, static source/interface evidence, basic
Gazebo trajectory evidence, Diff-Planner single-UAV evidence, and Diff-Planner
three-UAV evidence. Runtime evidence is measured but not user-frozen accepted.

Current runtime parameter override:

```text
PX4CTRL_CORE_PROFILE=nmpc_outer
PX4CTRL_KP_XY=12
PX4CTRL_KP_Z=5
PX4CTRL_KV_XY=6.5
PX4CTRL_KV_Z=4
PX4CTRL_NMPC_HORIZON_S=0.25
PX4CTRL_NMPC_POSITION_WEIGHT_XY=2.0
PX4CTRL_NMPC_POSITION_WEIGHT_Z=1.0
PX4CTRL_NMPC_VELOCITY_WEIGHT_XY=0.05
PX4CTRL_NMPC_VELOCITY_WEIGHT_Z=0.05
PX4CTRL_NMPC_CONTROL_WEIGHT_XY=0.0002
PX4CTRL_NMPC_CONTROL_WEIGHT_Z=0.001
PX4CTRL_NMPC_ACCEL_LIMIT_XY=4.0
PX4CTRL_NMPC_ACCEL_LIMIT_Z=2.5
PX4CTRL_NMPC_INCREMENT_LIMIT_XY=4.0
PX4CTRL_NMPC_INCREMENT_LIMIT_Z=2.5
```

Current implementation evidence:

```text
Results/g9/nmpc_outer_attitude_thrust_v1/source_audit/controller_source_audit.json
Results/g9/nmpc_outer_attitude_thrust_v1/g9f_static_gate_20260629_193901/RUN_MANIFEST.json
Results/sunray_ros1/g9f_nmpc_outer_takeoff_hover_land_20260629_205737/RUN_MANIFEST.json
Results/sunray_ros1/g9f_nmpc_outer_figure8_pw2_cw0002_20260629_211913/RUN_MANIFEST.json
Results/sunray_ros1/g9f_nmpc_outer_spiral_pw2_cw0002_20260629_212404/RUN_MANIFEST.json
Results/sunray_ros1/g9f_nmpc_outer_step_x_pw2_cw0002_20260629_212747/RUN_MANIFEST.json
Results/sunray_ros1/g9f_nmpc_outer_step_y_pw2_cw0002_20260629_213054/RUN_MANIFEST.json
Results/sunray_ros1/g9f_nmpc_outer_step_z_pw2_cw0002_gatefix_20260629_213934/RUN_MANIFEST.json
Results/sunray_ros1/g9f_nmpc_outer_diff_single_auto123_pw2_cw0002_20260629_214328/RUN_MANIFEST.json
Results/sunray_ros1/g9f_nmpc_outer_diff_swarm_3uav_pw2_cw0002_20260629_214624/RUN_MANIFEST.json
Config/profiles/experiments/g9_nmpc_outer_figure8_v1.json
```

Current measured runtime summary:

```text
takeoff-hover-land: steady hover XY RMSE 0.012694m, Z RMSE 0.017276m.
figure8: XYZ RMSE 0.034195m, p95 0.048834m, max 0.076218m.
spiral: XYZ RMSE 0.035799m, p95 0.049213m, max 0.067100m.
step_x: primary-axis settled RMSE 0.007280m, max 0.029978m.
step_y: primary-axis settled RMSE 0.011024m, max 0.027409m.
step_z: primary-axis settled RMSE 0.015276m, max 0.030999m.
Diff single auto123: interactive_passed; goal errors 0.0708m / 0.0809m / 0.0798m.
Diff three-UAV: passed; execute target errors 0.0209m / 0.0025m / 0.0143m,
minimum inter-UAV distance 0.9870m.
```

G9-F v1 mapping:

```text
predict p_h = p + v * T
predict p_ref_h = p_ref + v_ref * T + 0.5 * a_ref * T^2
predict v_ref_h = v_ref + a_ref * T
solve per-axis constant acceleration from a diagonal weighted
  position/velocity/control-increment surrogate cost
clamp acceleration by nmpc_accel_limit
clamp command increment by nmpc_increment_limit
force = mass * (a_cmd + gravity * e3)
output = desired attitude quaternion + normalized thrust through px4ctrl adapter
```

Forbidden claims: do not claim full nonlinear online NMPC solver, rotor-level
NMPC, hard real-time solver feasibility, user-frozen G9-F acceptance,
MWORKS-generated acceptance, or PX4-native deployment from the historical G9-F
evidence. NMPC with INDI/L1 is a composite profile, not the same as standalone
NMPC.
