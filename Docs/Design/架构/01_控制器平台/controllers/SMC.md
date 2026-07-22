# SMC

Status: IMPLEMENTED / MEASURED. Static ATTITUDE_THRUST backend, single-UAV
Gazebo tasks, Diff-Planner single-UAV, and Diff-Planner three-UAV regression
evidence are present. User-frozen acceptance is still pending.

Layer: nominal robust controller, first as outer-loop `ATTITUDE_THRUST`.

Replaces: position/velocity outer-loop in v1; attitude/body-rate SMC is a later
interface release.

Inputs: state error, reference derivatives required by the selected surface,
boundary layer or saturation parameters, model limits, dt, reset, enable.

Outputs: v1 targets `ATTITUDE_THRUST`. Super-twisting, terminal or attitude SMC
must declare their own output layer.

PX4 dependency: v1 reuses PX4 attitude loop, rate loop and allocation.

MWORKS/codegen route: Classical or boundary-layer SMC -> MWORKS model -> generated
C/C++ -> same controller host.

Gazebo/Sunray validation: hover, step, figure-8, spiral and wind/parameter
disturbance tests; chattering and saturation must be logged.

Current gate: G9-D Boundary-layer SMC has a C++ `ATTITUDE_THRUST` backend under
`PX4CTRL_CORE_PROFILE=smc_boundary_layer`, static source/interface evidence,
single-UAV Gazebo evidence, Diff single-UAV evidence, and Diff three-UAV
evidence.

Current runtime parameter override:

```text
PX4CTRL_CORE_PROFILE=smc_boundary_layer
PX4CTRL_KP_XY=12
PX4CTRL_KP_Z=5
PX4CTRL_KV_XY=6.5
PX4CTRL_KV_Z=4
PX4CTRL_SMC_LAMBDA_XY=2.0
PX4CTRL_SMC_LAMBDA_Z=2.0
PX4CTRL_SMC_ETA_XY=0.1
PX4CTRL_SMC_ETA_Z=0.05
PX4CTRL_SMC_PHI_XY=0.4
PX4CTRL_SMC_PHI_Z=0.35
PX4CTRL_SMC_SURFACE_LIMIT_XY=3.0
PX4CTRL_SMC_SURFACE_LIMIT_Z=2.5
```

These gains are SMC-specific runtime overrides. They are not global px4ctrl
defaults and must not be silently applied to the frozen G8, PID, SE3, or DFBC
baselines.

Current implementation and runtime evidence:

```text
Results/g9/smc_boundary_layer_attitude_thrust_v1/source_audit/controller_source_audit.json
Results/g9/smc_boundary_layer_attitude_thrust_v1/g9d_static_gate_20260629_182921/RUN_MANIFEST.json
Results/sunray_ros1/g9d_smc_boundary_takeoff_hover_land_eta010_z005_20260629_182522/RUN_MANIFEST.json
Results/sunray_ros1/g9d_smc_boundary_figure8_serial_20260629_183551/RUN_MANIFEST.json
Results/sunray_ros1/g9d_smc_boundary_spiral_serial_20260629_183932/RUN_MANIFEST.json
Results/sunray_ros1/g9d_smc_boundary_step_x_g7_20260629_184307/RUN_MANIFEST.json
Results/sunray_ros1/g9d_smc_boundary_step_y_g7_20260629_184607/RUN_MANIFEST.json
Results/sunray_ros1/g9d_smc_boundary_step_z_g7_20260629_184920/RUN_MANIFEST.json
Results/sunray_ros1/g9d_smc_boundary_diff_single_auto123_20260629_185211/RUN_MANIFEST.json
Results/sunray_ros1/g9d_smc_boundary_diff_swarm_3uav_rerun_20260629_190503/RUN_MANIFEST.json
Config/profiles/experiments/g9_smc_boundary_layer_figure8_v1.json
```

Boundary-layer SMC mapping used in G9-D:

```text
e_p = p_ref - p
e_v = v_ref - v
s = e_v + lambda * e_p
s = clamp(s, smc_surface_limit)
a_switch = eta * sat(s / phi)
a_cmd = a_ref + Kp * e_p + Kv * e_v + a_switch
force = mass * (a_cmd + gravity * e3)
output = desired attitude quaternion + normalized thrust through px4ctrl adapter
```

Measured runtime summary:

```text
takeoff-hover-land steady XY RMSE: 0.0124 m
takeoff-hover-land steady Z RMSE:  0.0183 m
figure-8 trajectory XYZ RMSE:      0.0336 m
figure-8 trajectory P95:           0.0480 m
figure-8 trajectory max:           0.0688 m
spiral trajectory XYZ RMSE:        0.0349 m
spiral trajectory P95:             0.0448 m
spiral trajectory max:             0.0564 m
step-X / step-Y / step-Z:          G7 settled-response gates passed
Diff-Planner single-UAV auto123:   probe and Z audit passed
Diff-Planner three-UAV:            passed, min separation 0.9921 m
```

Runtime limitation: the first aggressive SMC tuning failed hover with about
0.18 m steady Z RMSE. The measured G9-D route uses a conservative boundary
layer to avoid chattering and PX4 inner-loop excitation. This is a robust
outer-loop comparison point, not proof that terminal, super-twisting,
body-rate, torque-level, or rotor-level SMC variants are implemented.

Forbidden claims: do not claim user-frozen G9-D acceptance, terminal SMC,
super-twisting SMC, attitude/body-rate/torque-level SMC, MWORKS-generated
acceptance, or PX4-native deployment from the historical G9-D evidence.
