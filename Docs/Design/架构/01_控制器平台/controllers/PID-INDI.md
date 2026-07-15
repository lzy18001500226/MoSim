# PID-INDI

Status: IMPLEMENTED / MEASURED. Runtime Gazebo tasks and Diff single/three-UAV
regression evidence are present, but user-frozen acceptance is still pending.

Layer: augmentation on top of the official PID outer loop, not a standalone
nominal controller in the first release.

Replaces: nothing by itself. It modifies the PID acceleration command before
the common `ATTITUDE_THRUST` projection.

Inputs: position, velocity, attitude, angular velocity, p/v/a reference, yaw,
PID gains, finite-difference velocity history, measured-acceleration filter,
INDI gain, residual clamp, increment clamp, dt, reset, enable.

Outputs: v1 targets `ATTITUDE_THRUST` through the same px4ctrl adapter as PID.

PX4 dependency: v1 reuses PX4 attitude loop, rate loop and allocation. It does
not own actuator effectiveness, motor delay compensation, body-rate command,
torque command, or rotor allocation.

MWORKS/codegen route: PID + bounded INDI augmentation model -> generated C/C++
-> IController wrapper -> same Adapter as px4ctrl.

Gazebo/Sunray validation: takeoff/hover/land first, then figure-8, spiral,
step-x/y/z, Diff-Planner single-UAV and Diff-Planner three-UAV.

Current gate: G9-E has a C++ `ATTITUDE_THRUST` backend under
`PX4CTRL_CORE_PROFILE=pid_indi`, static source/interface evidence, single-UAV
Gazebo task evidence, Diff-Planner single-UAV evidence, and Diff-Planner
three-UAV evidence. Runtime evidence is not user-frozen yet.

The fixed core was revalidated under the unified control-platform Wave C gate
at `Results/control_platform/g5_wave_c_indi_20260716/RUN_MANIFEST.json`; the
existing generated-C equivalence remains indexed by
`Results/control_platform/g3_current_family_20260716/G3_SUMMARY.json`.

Current runtime parameter override:

```text
PX4CTRL_CORE_PROFILE=pid_indi
PX4CTRL_KP_XY=12
PX4CTRL_KP_Z=5
PX4CTRL_KV_XY=6.5
PX4CTRL_KV_Z=4
PX4CTRL_INDI_GAIN_XY=0.12
PX4CTRL_INDI_GAIN_Z=0.06
PX4CTRL_INDI_INCREMENT_LIMIT_XY=0.35
PX4CTRL_INDI_INCREMENT_LIMIT_Z=0.15
PX4CTRL_INDI_MEASURED_ACCEL_LIMIT_XY=6.0
PX4CTRL_INDI_MEASURED_ACCEL_LIMIT_Z=4.0
PX4CTRL_INDI_ACCEL_LPF_ALPHA=0.25
```

Current implementation evidence:

```text
Results/g9/pid_indi_v1/source_audit/controller_source_audit.json
Results/g9/pid_indi_v1/g9e_static_gate_20260629_193806/RUN_MANIFEST.json
Results/g9/pid_indi_v1/g9e_static_gate_recheck_20260629_194535/RUN_MANIFEST.json
Results/sunray_ros1/g9e_pid_indi_takeoff_hover_land_20260629_194818/RUN_MANIFEST.json
Results/sunray_ros1/g9e_pid_indi_figure8_disarm_20260629_195644/RUN_MANIFEST.json
Results/sunray_ros1/g9e_pid_indi_spiral_tunez_disarm_20260629_200342/RUN_MANIFEST.json
Results/sunray_ros1/g9e_pid_indi_step_x_stepgate_gainz006_20260629_202648/RUN_MANIFEST.json
Results/sunray_ros1/g9e_pid_indi_step_y_stepgate_gainz006_20260629_202324/RUN_MANIFEST.json
Results/sunray_ros1/g9e_pid_indi_step_z_stepgate_gainz006_retry_20260629_203358/RUN_MANIFEST.json
Results/sunray_ros1/g9e_pid_indi_diff_single_auto123_gainz006_20260629_203850/RUN_MANIFEST.json
Results/sunray_ros1/g9e_pid_indi_diff_swarm_3uav_gainz006_retry_20260629_204715/RUN_MANIFEST.json
Config/profiles/experiments/g9_pid_indi_figure8_v1.json
```

Measured runtime summary:

```text
takeoff-hover-land steady hover: XY RMSE 0.016638 m, Z RMSE 0.014881 m
spiral: XYZ RMSE 0.034815 m, p95 0.045882 m, max 0.059336 m
step-x primary RMSE/max: 0.009221 / 0.019718 m
step-y primary RMSE/max: 0.019607 / 0.048478 m
step-z primary RMSE/max: 0.016368 / 0.036124 m
Diff single target errors: 0.0821 / 0.0189 / 0.0130 m
Diff three-UAV execute target errors: uav1 0.0185 m, uav2 0.0119 m, uav3 0.0140 m
Diff three-UAV minimum inter-UAV distance: 0.9894 m
```

PID-INDI mapping used in G9-E:

```text
e_p = p_ref - p
e_v = v_ref - v
a_pid = a_ref + Kp * e_p + Kv * e_v + Ki * integral(e_p)
a_meas = LPF(clamp((v - v_prev) / dt, measured_accel_limit))
r = a_cmd_prev - a_meas
delta_a = clamp(indi_gain * r, indi_increment_limit)
a_cmd = a_pid + delta_a
force = mass * (a_cmd + gravity * e3)
output = desired attitude quaternion + normalized thrust through px4ctrl adapter
```

Runtime limitation: this is a bounded translational acceleration residual
augmentation. It is useful for the current `ATTITUDE_THRUST` template, but it
is not full INDI. Full INDI needs angular acceleration or acceleration feedback,
actuator effectiveness, actuator delay/filter alignment and a lower-level
output interface.

Forbidden claims: do not claim user-frozen G9-E acceptance, standalone INDI,
body-rate/torque/rotor-level INDI, actuator-effectiveness INDI, MWORKS-generated
acceptance, or PX4-native deployment from the current G9-E evidence.
