# SE3

Status: MEASURED / static and ROS1 runtime gates passed; user acceptance pending.

Layer: nominal geometric outer-loop controller.

Replaces: position/velocity outer-loop; may optionally produce body-rate targets
in later stages.

Inputs: position, velocity, attitude, angular velocity, p/v/a reference, yaw,
mass, gravity, geometric gains, dt, reset, enable.

Outputs: first-stage `ATTITUDE_THRUST`; future variants may require
`BODY_RATE_THRUST`.

PX4 dependency: first version reuses PX4 attitude and rate loops.

MWORKS/codegen route: MWORKS SE3 model -> generated C/C++ -> IController wrapper
-> same Adapter.

Gazebo/Sunray validation: takeoff/hover/land, step, figure-8, spiral, then
Diff-Planner trajectory tracking. EGO is a reference comparison route.

Current gate: second replacement controller after PID to prove the template
supports structurally different control laws.

Current runtime parameter override:

```text
PX4CTRL_CORE_PROFILE=se3_basic
PX4CTRL_KP_XY=12
PX4CTRL_KP_Z=5
PX4CTRL_KV_XY=6.5
PX4CTRL_KV_Z=4
```

These gains are SE3-specific runtime overrides. They are not global px4ctrl
defaults and must not be silently applied to the frozen G8 or PID baselines.

Current implementation and runtime evidence:

```text
Results/g9/se3_basic_attitude_thrust_v1/source_audit/controller_source_audit.json
Results/g9/se3_basic_attitude_thrust_v1/g9b_static_gate_20260629_142902/RUN_MANIFEST.json
Results/g9/se3_basic_attitude_thrust_v1/g9b_static_gate_20260629_153356/RUN_MANIFEST.json
Results/sunray_ros1/g9b_se3_basic_takeoff_hover_land_kpz5_20260629_144656/RUN_MANIFEST.json
Results/sunray_ros1/g9b_se3_basic_figure8_disarm_kpxy12_kpz5_20260629_150206/RUN_MANIFEST.json
Results/sunray_ros1/g9b_se3_basic_spiral_disarm_kpxy12_kpz5_20260629_150549/RUN_MANIFEST.json
Results/sunray_ros1/g9b_se3_basic_step_x_g7_kpxy12_kpz5_20260629_151214/RUN_MANIFEST.json
Results/sunray_ros1/g9b_se3_basic_step_y_g7_kpxy12_kpz5_20260629_151509/RUN_MANIFEST.json
Results/sunray_ros1/g9b_se3_basic_step_z_g7_kpxy12_kpz5_20260629_151806/RUN_MANIFEST.json
Results/sunray_ros1/g9b_se3_basic_diff_single_auto123_kpxy12_kpz5_20260629_152133/RUN_MANIFEST.json
Results/sunray_ros1/g9b_se3_basic_diff_swarm_3uav_kpxy12_kpz5_20260629_152421/RUN_MANIFEST.json
Config/profiles/experiments/g9_se3_basic_figure8_v1.json
```

Runtime result summary:

```text
takeoff-hover-land steady XY RMSE: 0.01630 m
takeoff-hover-land steady Z RMSE:  0.01039 m
figure-8 trajectory XYZ RMSE:      0.03319 m
figure-8 trajectory P95:           0.04995 m
figure-8 trajectory max:           0.06416 m
spiral trajectory XYZ RMSE:        0.03743 m
spiral trajectory P95:             0.04871 m
spiral trajectory max:             0.05512 m
step-X settled XYZ RMSE:           0.02113 m
step-Y settled XYZ RMSE:           0.03284 m
step-Z settled XYZ RMSE:           0.02420 m
Diff-Planner single-UAV:           goal switch chain passed
Diff-Planner three-UAV:            passed, min separation 0.99195 m
```

Step evidence uses the G7 settled-response gate, not a full-window trajectory
tracking gate, because the commanded step intentionally creates a discontinuity.
This is the same evaluation rule used for the official PID G9-A step evidence.

Forbidden claims: SE3 Basic and SE3 with integral/action/body-rate feedforward
must be separated in profiles and evidence. G9-B is not accepted until the user
explicitly freezes it.
