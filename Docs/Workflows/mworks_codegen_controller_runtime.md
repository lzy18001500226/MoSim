# MWORKS Controller Code Generation Workflow

Date: 2026-06-02

Purpose: verify and reuse MWORKS/Sysplorer/Sysblock controller code generation
for the MoSim controller deployment path: first through the current
ROS1/Sunray/MAVROS regression lane, and later through the gated PX4-native
deployment branch.

Current-mainline boundary: this workflow is retained for MWORKS
code-generation, generated-runtime promotion, and later PX4-native deployment
design. The execution selector is
`Docs/Workflows/mainline_operations_board.md`. The current active runtime
evidence lane remains ROS1 Noetic / Sunray / Gazebo Classic / PX4 / MAVROS /
px4ctrl / RViz. The G9 family has passed `GenerateModelCode`, generated-C
offline equivalence, and static ROS/Sunray adapter gates. Its six-controller
generated-runtime route is being revalidated under
`Docs/Workflows/g9_mworks_generated_runtime_closeout.md` because older runtime
manifests identify controller profiles but do not uniquely prove the compiled
generated-C backend and executable identity. G10-B/D/E L1/AWFF, safety filter, and
fault allocation have also passed state-isolated MWORKS/codegen promotion and
the reversible ROS/Sunray runtime reinjection gates through Diff single-UAV and
Diff three-UAV. PX4-native uORB/module deployment is a later gated route and
must not displace the current
Sunray/ROS1/MAVROS regression lane. ROS2, x500, and direct Gazebo motor-control
fixture routes remain historical or diagnostic unless explicitly reopened by
the user.

2026-06-30 G9 family static/codegen status:

```text
MWORKS GenerateModelCode:
  Results/g9/controller_family_attitude_thrust_v1/g9_family_mworks_codegen_20260630_work
  status: passed

generated-C offline equivalence:
  Results/g9/controller_family_attitude_thrust_v1/g9_family_generated_c_gate_20260630_195728/RUN_MANIFEST.json
  status: passed
  controllers: official_pid, se3_basic, dfbc_basic, smc_boundary_layer, pid_indi, nmpc_outer
  cases: 450
  tolerance: 1e-12

static ROS/Sunray adapter shape:
  Results/g9/controller_family_attitude_thrust_v1/g9_family_ros_sunray_adapter_gate_20260630_200721/RUN_MANIFEST.json
  status: passed
  controllers: official_pid, se3_basic, dfbc_basic, smc_boundary_layer, pid_indi, nmpc_outer
  cases: 450
  attitude_target_type_mask: 7
```

These gates are still static/offline evidence. They prove generated source,
same-input numerical equivalence, finite/unit attitude target, bounded
normalized thrust, and the px4ctrl/MAVROS attitude-plus-thrust command shape.
They did not by themselves prove ROS node replacement, PX4 Offboard behavior,
Gazebo motion, Diff-Planner compatibility, or flight metrics. The current board
records later reversible Sunray/ROS wrapper and Gazebo/Diff runs for the named
profiles. Those runs remain regression evidence, but they are not final
generated-runtime closure until the provenance contract in the G9 closeout
workflow passes. Future uses of this workflow should apply the same evidence
chain and provenance contract to every selected controller or enhancement.

2026-07-01 G10-B/D/E state-isolated static/codegen status:

```text
review packet:
  Results/g10/min_enhancements_v1/g10bde_mworks_codegen_stateiso_20260701_work/SUMMARY.md

MWORKS GenerateModelCode:
  Results/g10/min_enhancements_v1/g10bde_mworks_codegen_stateiso_20260701_work/generate_model_code_result.json
  status: passed
  model: G10_BDE_Family_CFunction_Sysblock_StateIso
  state_isolation_present: true
  codegen precision intent: real_as_float=false, DoublePrecision=true

generated-C offline equivalence:
  Results/g10/min_enhancements_v1/g10bde_mworks_codegen_stateiso_20260701_work/g10_bde_family_generated_c_gate_strict/RUN_MANIFEST.json
  status: passed
  controllers: G9-A..F plus accepted G10-B/D/E ids 7..9
  cases: 702
  failures: 0
  tolerance: 1e-12
  max_normalized_thrust_abs_diff: 1.1102230246251565e-16
  max_desired_acc_abs_diff: 3.552713678800501e-15

static ROS/Sunray adapter shape:
  Results/g10/min_enhancements_v1/g10bde_mworks_codegen_stateiso_20260701_work/g10_bde_family_ros_sunray_adapter_gate_strict/RUN_MANIFEST.json
  status: passed
  cases: 702
  failures: 0
  nonfinite_command_count: 0
  thrust_range_failure_count: 0
  attitude_target_type_mask: 7
```

The state-isolation fix is important: the generated Sysblock CFunction scalar
entry keeps a separate controller state slot per controller id. Earlier
single-static-state wrappers could contaminate one controller's internal state
with another controller's test case and create false numerical failures in
G10-B/D/E special cases. This fix proves offline codegen equivalence and
static adapter shape. The runtime ROS/Sunray replacement and Diff-Planner
compatibility claims are now covered by the G10-B/D/E runtime evidence below.
It still does not prove PX4-native deployment, full nonlinear online NMPC,
G10-C translational INDI, or final competition performance improvement.

2026-07-01 G10-B/D/E ROS/Sunray runtime reinjection closeout:

```text
Diff single-UAV:
  l1_awff:
    Results/sunray_ros1/g10_bde_l1_awff_diff_single_20260701_024916
    status: passed
    mission_exit_code: 0
    execute_target_error_m: 0.027689
    z_audit: passed
    waypoint_audit: passed
  safety_filter:
    Results/sunray_ros1/g10_bde_safety_filter_diff_single_20260701_025540
    status: passed
    mission_exit_code: 0
    execute_target_error_m: 0.015052
    z_audit: passed
    waypoint_audit: passed
  fault_allocation:
    Results/sunray_ros1/g10_bde_fault_allocation_diff_single_20260701_030032
    status: passed
    mission_exit_code: 0
    execute_target_error_m: 0.034522
    z_audit: passed
    waypoint_audit: passed

Diff three-UAV:
  transition guard:
    EGO_CMD_SAFETY_MAX_POSITION_JUMP_M=0.80
    reason: accepted hover-hold -> planner-takeover transition envelope for
            Goal5; not controller tuning.
  l1_awff:
    Results/sunray_ros1/g10_bde_l1_awff_diff_swarm_3uav_jump08_20260701_031015
    status: passed
    mission_exit_code: 0
    min_inter_uav_distance_m: 0.977825
  safety_filter:
    Results/sunray_ros1/g10_bde_safety_filter_diff_swarm_3uav_jump08_20260701_031532
    status: passed
    mission_exit_code: 0
    min_inter_uav_distance_m: 0.971109
  fault_allocation:
    Results/sunray_ros1/g10_bde_fault_allocation_diff_swarm_3uav_jump08_20260701_032031
    status: passed
    mission_exit_code: 0
    min_inter_uav_distance_m: 0.977347

negative/intermediate run:
  Results/sunray_ros1/g10_bde_l1_awff_diff_swarm_3uav_20260701_030404
  exit: 14
  blocker: uav1_position_cmd_discontinuous
  classification: guard false block on hover-hold -> planner takeover; all
                  UAVs reached and min inter-UAV distance was 0.992265 m.
```

Claim boundary: this closes the accepted G10-B/D/E minimal enhancement route
through the current ROS1/Sunray/Gazebo/PX4/MAVROS/px4ctrl/Diff gates. It does
not make G10-C `ATTITUDE_THRUST` translational INDI acceptable, does not promote
G10-A DOB/ESO beyond its static/profile evidence, and does not claim PX4-native
uORB/module deployment.

2026-06-20 architecture correction for the deferred PX4-native branch: the
formal PX4-native target is not a standalone ROS2 controller that writes Gazebo
motor topics. That branch follows the normal PX4/Gazebo/Simulink-style flow:
MWORKS generates controller C/C++, the generated code is wrapped for PX4
Offboard or PX4 module/uORB integration, PX4 owns flight mode, estimator,
failsafe, control allocation, and actuator pipeline, and Gazebo remains the
plant/sensor simulator. This branch is not the current execution surface.
Current work follows the mainline board; use this workflow only when a
board-selected controller or enhancement needs generated-code promotion through
ROS1/Sunray/MAVROS reinjection and Gazebo regression.

The old `ControllerOutput -> Gazebo actuator` path is retained only as a
fixture for plant, mixer, and bridge debugging. It is not the formal
deployment route.

2026-06-20 runtime correction for the deferred PX4-native branch: EGO /
FAST-LIO / RViz evidence must follow the same boundary. EGO may publish a
planned trajectory or `PositionCommand`, but a PX4-native competition-style
closed-loop run is accepted only when that command is consumed by a real
flight-control backend, either PX4 Offboard or a later generated-code PX4/uORB
adapter. A run where EGO output is converted into a project Python
truth-feedback controller and then directly writes Gazebo motor topics is
diagnostic/pre-acceptance only, even if RViz shows point cloud, occupancy grid,
and a planned path. The next gate in that deferred branch therefore has to
prove:

```text
Gazebo sensors / FAST-LIO or truth odom for planner input
  -> EGO bspline / PositionCommand
  -> MoSim PlannerSetpoint conversion
  -> PX4 Offboard TrajectorySetpoint or generated-code PX4 adapter
  -> PX4 SITL flight-control loop
  -> Gazebo plant motion and landing metrics
```

Use the old direct-actuator bridge only to isolate plant parameters, motor
order, topic transport, or visual review issues. Do not tune it as if it were
the final flight-control architecture.

## 1. Key Result

MWORKS/Sysplorer supports Sysblock model code generation through the official
Python API:

```text
GetModelCodeGenerationOptions(modelName)
SetModelCodeGenerationOptions(modelName, options)
GenerateModelCode(modelName)
```

This is separate from `TranslateModel(modelName)`. The current Sysplorer MCP
`translate_model` wrapper only calls `TranslateModel(modelName)` and ignores
`code_folder`, `code_type`, `build_type`, `run_to`, and `config_json`; it is not
the right proof for project-local C/C++ export.

## 2. Verified Probe

Probe model:

```text
Models/MoSimQuadrotorModel/Controllers/Sysblocks/AWFF_PID_Sysblock_Demo.mo
```

Output:

```text
Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/AWFF_PID_Sysblock_Demo/
```

Generated files:

```text
AWFF_PID_Sysblock_Demo.c
AWFF_PID_Sysblock_Demo.h
AWFF_PID_Sysblock_Demo_data.c
AWFF_PID_Sysblock_Demo_extern_include.h
AWFF_PID_Sysblock_Demo_private.h
ExternalCResource.json
ExternalResources.xml
motrace.json
mwb_main.c
mwb_runtime.h
mwb_types.h
```

Observed generated runtime shape:

```text
Init()
Step()
global input struct:  awff_pid_sysblock_demoGbIn
global output struct: awff_pid_sysblock_demoGbOut
sample time:          0.01 s
```

The generated C sources compiled with:

```bash
gcc -std=c99 -Wall -Wextra -pedantic -c \
  AWFF_PID_Sysblock_Demo.c \
  AWFF_PID_Sysblock_Demo_data.c \
  mwb_main.c
```

Temporary `.o` files were removed after the compile probe. The generated C/H
files and `motrace.json` remain as local evidence.

The reusable project check is:

```bash
python3 Scripts/mworks/check_codegen_runtime.py \
  --code-dir Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/AWFF_PID_Sysblock_Demo \
  --model-name AWFF_PID_Sysblock_Demo \
  --compile \
  --expect-sample-time 0.01 \
  --json-out Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/runtime_check.json
```

This check records:

```text
schema:                  mosim.mworks_codegen_runtime_check.v1
runtime adapter shape:   global_struct_input_output_init_step
functions:               Init, Step
input fields:            z_error
output fields:           thrust_cmd
sample_time_s:           0.01
compile status:          gcc C99 compile ok
SIL requirement:         true
```

With `--run-smoke`, the check also builds a temporary C harness that includes
the generated headers, calls `Init()`, writes one input field, calls `Step()`,
and records the output field plus generated runtime time. For the current PID
probe, the smoke sequence verifies:

```text
input global/field:   awff_pid_sysblock_demoGbIn.z_error
output global/field:  awff_pid_sysblock_demoGbOut.thrust_cmd
input sequence:       0.1, 0.2, -0.1
runtime times:        0.01, 0.02, 0.03
```

The compile and runtime-smoke probes run in temporary directories so generated
evidence folders are not polluted by `.o`, `.obj`, `.exe`, or harness files.

## 3. Minimal Script Pattern

Use `mcp__sysplorer.call_code(mode="run_script")` or a future dedicated MCP
tool. Do not use `ClearAll` or `ChangeDirectory`.

```python
import os
import mworks.sysplorer as ModelingPy

model_name = "AWFF_PID_Sysblock_Demo"
model_path = r"C:\Users\HP\Desktop\MoSim\Models\QuadrotorControllerBlocks\AWFF_PID_Sysblock_Demo.mo"
out_dir = r"C:\Users\HP\Desktop\MoSim\Results\codegen_probe\AWFF_PID_Sysblock_Demo_api"

os.makedirs(out_dir, exist_ok=True)

ModelingPy.LoadLibrary("SysplorerEmbeddedCoder")
ModelingPy.OpenModelFile(model_path)
assert ModelingPy.CheckModel(model_name)

options = ModelingPy.GetModelCodeGenerationOptions(model_name)
options["CodePlatform.OutPath"] = {"output": out_dir}
assert ModelingPy.SetModelCodeGenerationOptions(model_name, options)
assert ModelingPy.GenerateModelCode(model_name)
```

## 4. MoSim Runtime Policy

The generated code is accepted as a controller-runtime candidate only after a
SIL equivalence gate:

```text
same input sequence
  -> MWORKS/Sysblock output
  -> generated C/C++ output
  -> sample-by-sample tolerance check
```

Required evidence for every exported controller:

```text
model_name
model_source_path
codegen_api_version or MWORKS version
generated_code_hash
codegen_options_snapshot
adapter_type
compile_status
sil_equivalence_status
external_runtime_status
```

Before equivalence passes, generated or external C/C++ results cannot replace
MWORKS/Sysplorer simulation evidence.

Each controller owns its own codegen/SIL gate. Passing this workflow for the
PID demo proves the route and harness shape only. It does not certify INDI,
MPC/NMPC, L1/adaptive, safety-filter, allocation, planner, or fault logic. For
every new controller, record a separate model source, generated code hash,
input/output schema, sample time, compile result, and SIL equivalence result.

Pre-SIL gate:

```text
generated files present
  -> check_codegen_runtime.py summary ok
  -> generated C compiles without temp artifacts
  -> temporary Init/Step harness runs on a small input sequence
  -> interface/sample-time snapshot saved
  -> only then build ControllerRuntime wrapper
```

Zero-input SIL smoke gate:

```bash
python3 Scripts/mworks/check_codegen_sil_equivalence.py \
  --code-dir Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/AWFF_PID_Sysblock_Demo \
  --model-name AWFF_PID_Sysblock_Demo \
  --input-sequence 0,0,0 \
  --tolerance 1e-12 \
  --json-out Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/sil_zero_input_check.json
```

Current status: `zero_input_sil_smoke` passes for the PID demo. This is useful
as a startup/reference check but not a complete SIL proof. The Sysplorer result
variable discovery for this model exposes internal variables such as
`cmd_sum.y`, not the outport name `AWFF_PID_Sysblock_Demo.thrust_cmd`.

Nonzero constant-input SIL gate:

```text
MWORKS/Sysblock constant reference model
  -> z_error = 0.1
  -> result variable cmd_sum.y
  -> generated C runtime input sequence 0.1,0.1,0.1,0.1
  -> output-order sample comparison
```

Reference model:

```text
Models/MoSimQuadrotorModel/Controllers/Sysblocks/AWFF_PID_Sysblock_Demo_SIL_Constant.mo
```

Evidence:

```text
Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/mworks_constant_0p1_reference.json
Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/runtime_constant_0p1_check.json
Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/sil_constant_0p1_check.json
```

Command:

```bash
python3 Scripts/mworks/check_codegen_sil_equivalence.py \
  --code-dir Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/AWFF_PID_Sysblock_Demo \
  --model-name AWFF_PID_Sysblock_Demo \
  --input-sequence 0.1,0.1,0.1,0.1 \
  --mworks-reference-json Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/mworks_constant_0p1_reference.json \
  --tolerance 1e-5 \
  --json-out Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/sil_constant_0p1_check.json
```

Current result: `nonzero_input_sil_smoke` passes for the PID demo with
`max_abs_error = 8.934736470678217e-07`, below the `1e-5` tolerance. The
tolerance accounts for the current generated-code option `real_as_float=true`.
MWORKS reports the first Sysblock output at `t=0`; the generated C harness
records outputs after `Step()`, so runtime timestamps are one sample later while
output order matches.

Remaining stronger SIL gate:

```text
MWORKS/Sysblock time-varying input injection
  -> same input sequence as generated C runtime
  -> compare output sample-by-sample
  -> save input trace, MWORKS output, generated C output, tolerance, max error
```

Do not claim a generated controller is MoSim runtime-authoritative until the
target controller's own nonzero/time-varying SIL gate passes. The current
constant-input PID demo proves the architecture path is viable; it does not
finish SIL for all controllers.

Current generated-runtime checker status:

```text
Scripts/mworks/check_codegen_runtime.py
  -> supports generated C runtime discovery for any Init/Step global-struct
     model
  -> supports schema-driven single-input/single-output and multi-input/
     multi-output temporary runtime harnesses

Scripts/mworks/check_codegen_sil_equivalence.py
  -> supports field-by-field comparison for named multi-output rows
  -> still requires a real MWORKS/Sysblock reference trace before SIL can pass
```

The current codegen-compatible AWFF controller model has this interface:

```text
model:
  Models/MoSimQuadrotorModel/Controllers/Sysblocks/AWFF_FullController_Sysblock.mo

sample time:
  0.01 s

inputs:
  x_error
  y_error
  z_error
  z_ref_rate
  roll_mea
  pitch_mea
  yaw_mea
  yaw_ref

outputs:
  y
  y1
  y2
  y3
```

2026-06-20 correction: `AWFF_FullControllerEquation_Sysblock` is a useful
equation bridge for behavior review, but it is not the current codegen target:
`CheckModel` reports unsupported `der()` use inside Sysblock and blocks
`GenerateModelCode`. The active codegen target is
`MoSimQuadrotorModel.Controllers.Sysblocks.AWFF_FullController_Sysblock`, which has passed
Gate A/B/C below. Gate D has now passed the first real MWORKS nonzero
constant-input SIL check; the stronger time-varying-input SIL check remains a
future hardening gate before claiming complete controller equivalence.

## 5. Gazebo Deployment Boundary

2026-06-20 deployment correction:

```text
Python wrapper / static simulation / behavior-equivalent replay
  -> allowed only for automation, diagnostics, smoke checks, temporary
     reference comparisons, and bridge validation
  -> must not be reported as deployed controller runtime

formal controller deployment
  -> MWORKS Sysblock controller
  -> GenerateModelCode
  -> generated C/C++ controller
  -> SIL / generated-code runtime checks
  -> PX4 Offboard adapter or PX4 module/uORB adapter
  -> PX4 SITL
  -> Gazebo plant, sensors, and actuator feedback
  -> same-run PX4+Gazebo closed-loop gates
```

Do not claim `deployed controller`, `generated controller runtime`,
`competition controller performance`, or `final closed_loop` from Python ports,
open-loop MWORKS CSV replay, static/offline plots, or behavior-equivalent
reimplementations. Those artifacts remain useful, but only as reference or
debug evidence until the target controller's own generated C/C++ path passes
compile, SIL, PX4 adapter, and PX4+Gazebo gates.

PX4-native deployment levels for the later gated branch:

| Level | Generated-code host | PX4 role | Current use |
|---|---|---|---|
| L1 | External C/C++ or ROS2 node | Sends continuous Offboard setpoints into PX4; PX4 keeps estimator, inner loops, allocation, failsafe | Fastest first PX4-integrated validation |
| L2 | PX4 module/uORB adapter | Replaces a PX4 control level such as position or attitude/rate controller | Formal competition/innovation route |
| L3 | PX4 low-level actuator/motor integration | Generated code outputs actuator-level commands | Later high-risk research, not the first route |

When the later PX4-native branch is explicitly opened, its priority is L1 or
L2. Do not start from L3 unless the user explicitly chooses direct
actuator-level replacement after L1/L2 evidence exists. This does not override
the current board-selected path; do not repeat an already closed G9
generated-family reinjection gate just because this workflow describes that
evidence chain.

### 5.1 Deprecated Fixture Routes

The following routes are retained only for diagnosis and regression fixtures:

```text
MWORKS result CSV
  -> Scripts/ros/mworks_csv_to_controller_output_replay.py
  -> mosim_msgs/msg/ControllerOutput
  -> Scripts/ros/controller_output_to_gazebo_actuators_node.py
  -> actuator_msgs/msg/Actuators
  -> Gazebo motor plugins
```

```text
Gazebo truth pose
  -> Python truth-feedback or behavior-equivalent controller
  -> mosim_msgs/msg/ControllerOutput
  -> Scripts/ros/controller_output_to_gazebo_actuators_node.py
  -> actuator_msgs/msg/Actuators
  -> Gazebo motor plugins
```

These paths are accepted only as actuator-interface, plant-sanity, coordinate,
visualization, or regression fixtures. A MWORKS closed-loop CSV already
contains decisions made against the MWORKS plant state. Replaying that trace as
open-loop motor commands in Gazebo does not recreate the original feedback
loop. A Python behavior-equivalent wrapper does not prove generated C/C++
deployment. Neither route may be used as final controller deployment evidence.

Current 2026-06-18 bridge status:

```text
converter: Scripts/ros/mworks_csv_to_controller_output_replay.py
converter test: Scripts/tests/test_mworks_csv_to_controller_output_replay.py
runtime gate: Scripts/gazebo/run_mworks_controller_output_replay_gate.sh
latest runtime evidence: Results/gazebo_ros2/mworks_controller_output_replay_gate_20260618_r4/
adapter result: 41 ControllerOutput samples published and converted to Gazebo actuator velocities
plant result: blocked; Gazebo plant lost altitude under open-loop replay
blockers:
  - plant_z_response_below_min:-0.099775<0.020000
  - plant_max_z_response_below_min:0.000000<0.020000
claim: interface bridge passed far enough to drive actuator commands; closed-loop flight did not pass
```

### 5.2 Deferred PX4-Native Route

Inside the deferred PX4-native deployment branch, the valid controller route
is:

```text
Gazebo sensors / PX4 state estimate
  -> PX4 SITL
  -> generated C/C++ controller through Offboard or uORB adapter
  -> PX4 control/allocation/actuator pipeline
  -> Gazebo plant
  -> same-run PX4+Gazebo response gate
```

The first target inside that branch is L1 Offboard because it gets generated
C/C++ into a PX4-controlled flight loop without replacing PX4 inner loops
first:

```text
MWORKS Sysblock
  -> GenerateModelCode
  -> generated C/C++ controller runtime wrapper
  -> MoSim PlannerSetpoint / PX4 TrajectorySetpoint adapter
  -> /fmu/in/offboard_control_mode and /fmu/in/trajectory_setpoint
  -> PX4 commander / estimator / native control loops / allocation
  -> Gazebo x500 or accepted Sunray-compatible plant
```

PX4 Offboard-specific hard requirements:

```text
1. Publish OffboardControlMode and setpoint continuously before mode switch.
2. Keep publish rate safely above PX4's offboard proof-of-life threshold.
3. Convert coordinates explicitly: MoSim ENU/up is not PX4 local NED/down.
4. Warm up setpoints before VehicleCommand mode/arm requests.
5. Record VehicleCommandAck, vehicle_status, local_position/odometry,
   land_detected, trajectory_setpoint, offboard_control_mode, and Gazebo truth.
6. Any stale setpoint, frame mismatch, timestamp problem, or failsafe is a
   blocker, not a controller-performance pass.
```

For L2, the generated code must be compiled into PX4 SITL as a module/uORB
adapter before it can claim controller replacement.

Current 2026-06-20 PX4-native baseline evidence:

```text
takeoff-hover-land:
  Results/px4_gazebo/px4_offboard_takeoff_hover_land_20260620_003/PX4_OFFBOARD_TAKEOFF_HOVER_LAND.json
  status: passed
  hover_z_rmse_m: 0.055743
  hover_xy_max_m: 0.044550
  post_land_xy_span_m: 0.089347

figure-8:
  Results/px4_gazebo/px4_offboard_figure8_gate_20260620_004/PX4_OFFBOARD_FIGURE8_GATE.json
  status: passed
  figure8_xy_rmse_m: 0.204333
  figure8_xy_max_error_m: 0.471914
  figure8_z_rmse_m: 0.007930
  final_altitude_m: 0.035524
  post_land_xy_span_m: 0.062837
```

This proves the PX4 Offboard/Gazebo baseline can fly the required shape with
explicit setpoints. It does not prove that the MWORKS generated controller has
been deployed.

Current 2026-06-20 generated AWFF shadow evidence:

```text
shadow gate:
  Results/px4_gazebo/px4_offboard_figure8_gate_20260620_004/mworks_awff_codegen_shadow/MWORKS_AWFF_CODEGEN_SHADOW_GATE.json
  status: passed_position_loop_shadow
  generated C samples: 938/938
  root outports y/y1/y2/y3: not_l1_setpoint_ready
  position-loop pitch/roll/thrust: candidate_for_next_export_or_adapter_gate
```

Interpretation:

```text
AWFF_FullController_Sysblock root outputs are motor-mixer outputs.
They must not be fed into PX4 L1 Offboard trajectory setpoints.
The generated code's internal position-loop outputs are bounded and continuous
on the PX4/Gazebo figure-8 trace, so the next valid integration target is a
separate position-loop export or an adapter that exposes pitch_ref, roll_ref,
and thrust_ref explicitly.
```

#### 5.2.1 Rejected L1-Attitude Shortcut

The generated position-outer-loop-to-PX4-attitude shortcut was tested and must
not remain the main competition route:

```text
generated MWORKS position outer loop
  -> ROS2 attitude Offboard adapter
  -> /fmu/in/vehicle_attitude_setpoint_v1
  -> PX4 attitude/rate/allocation path
```

Findings:

```text
topic bug:
  old adapter default published /fmu/in/vehicle_attitude_setpoint
  current PX4 bridge consumes /fmu/in/vehicle_attitude_setpoint_v1
  fix: adapter now accepts attitude_setpoint_topic and defaults to the
       versioned topic

first topic-fixed run:
  Results/px4_gazebo/px4_position_outer_loop_attitude_takeoff_hover_land_20260620_004_topicfix/PX4_POSITION_OUTER_LOOP_ATTITUDE_TAKEOFF_HOVER_LAND.json
  result: vehicle lifted, but XY diverged badly
  max_xy_distance_m: 278.565081
  hover_xy_max_m: 198.989360
  post_land_xy_span_m: 30.669287

later damped/arm-first run:
  Results/px4_gazebo/px4_position_outer_loop_attitude_takeoff_hover_land_20260620_008_armfirst/PX4_POSITION_OUTER_LOOP_ATTITUDE_TAKEOFF_HOVER_LAND.json
  result: PX4 entered Offboard but arm was rejected
  rejected command: 400
  rejected result: 1
  max_altitude_m: 0.002109
```

Decision:

```text
This shortcut is demoted to diagnostic-only.
Do not tune it as the main night-long execution path.
Do not use it as proof that the MWORKS generated controller is deployed.
In the historical 2026-06-20 PX4-native branch, the accepted diagnostic
continuation was PX4 trajectory setpoint control for baseline plant/flight
evidence, plus generated MWORKS C/C++ SIL and shadow evidence until a designed
L1 trajectory-setpoint or L2 uORB module adapter existed. Current work is
selected by the mainline board; MWORKS/codegen, offline equivalence,
ROS1/Sunray/MAVROS reinjection, and Gazebo regression apply to the
board-selected controller or enhancement promotion step.
```

Reasoning:

```text
PX4 attitude Offboard bypasses PX4's native position-loop behavior and exposes
coordinate/sign/thrust/health-gate risks before the generated controller has a
validated PX4 integration contract. A normal Simulink/PX4-style workflow first
proves the PX4/Gazebo plant and Offboard trajectory route, then replaces or
augments a clearly selected control layer with generated code.
```

### 5.3 Historical AWFF Fixture Evidence

Current 2026-06-19 AWFF behavior-wrapper gate:

```text
source model:
  Models/MoSimQuadrotorModel/Controllers/Sysblocks/AWFF_FullControllerEquation_Sysblock.mo

runtime wrapper:
  Scripts/ros/mworks_awff_takeoff_hover_land_controller.py

gate runner:
  Scripts/gazebo/run_mworks_awff_takeoff_hover_land_gate.sh

latest passed same-run evidence:
  Results/gazebo_ros2/mworks_awff_formal_deploy_gate_pass_20260619_001/RUN_MANIFEST.json
  Results/gazebo_ros2/mworks_awff_formal_deploy_gate_pass_20260619_001/GAZEBO_TAKEOFF_HOVER_LAND_EVAL.json

fresh rerun and GUI-review evidence:
  Results/gazebo_ros2/mworks_awff_formal_deploy_gate_rerun_20260619_001/RUN_MANIFEST.json
  Results/gazebo_ros2/mworks_awff_takeoff_hover_land_animation_review_20260619_live_001/AWFF_ANIMATION_REVIEW_REQUEST.json
  Results/gazebo_ros2/mworks_awff_takeoff_hover_land_animation_review_long_hover_20260619_live_001/AWFF_ANIMATION_REVIEW_REQUEST.json

GUI review runner:
  Scripts/gazebo/run_mworks_awff_takeoff_hover_land_animation_review.sh
```

The passed route is:

```text
Gazebo truth pose
  -> AWFF_FullControllerEquation behavior-equivalent Python wrapper
  -> gazebo_ref_adapter plant adapter
  -> mosim_msgs/msg/ControllerOutput
  -> controller_output_to_gazebo_actuators_node.py
  -> actuator_msgs/msg/Actuators
  -> Gazebo sunray150_assembled motor plugins
```

This route is now explicitly classified as a temporary behavior-equivalent
bridge. It is useful because it proves the accepted Gazebo plant, the
ControllerOutput ABI, and the actuator adapter can carry AWFF-like control
signals through a same-run takeoff-hover-land loop. It is not generated
C/C++ deployment, not SIL equivalence, and not the final competition controller
runtime.

Do not continue the current mainline from this gate. If a later task needs a
visual plant sanity check, use this route only after labeling it as fixture
evidence and then return to the board-selected ROS1/Sunray reinjection or
enhancement validation gate, or to the deferred PX4-native gates only when that
branch is explicitly opened.

The `gazebo_ref_adapter` boundary is intentional. The AWFF equation model
produces MWORKS-plant-oriented references and internal control axes; the
adapter maps those references into the accepted Gazebo normalized motor command
scale with small plant damping. Directly replaying old MWORKS closed-loop CSV
or directly projecting AWFF internal axes into Gazebo motor deltas is not a
valid final closed-loop deployment proof.

Current passed metrics:

```text
13s rerun:
  duration_s: 13.02
  max_z_m: 0.656293
  final_z_m: 0.032899
  hover_settled_max_abs_z_error_m: 0.164013
  max_xy_distance_m: 0.328021
  max_airborne_tilt_rad: 0.068927
  adapter_published: 242

69s GUI long-hover review run:
  duration_s: 69.02
  max_z_m: 1.0177
  final_z_m: 0.035997
  hover_settled_max_abs_z_error_m: 0.241948
  max_xy_distance_m: 0.201183
  max_airborne_tilt_rad: 0.02211
  adapter_published: 1144
  camera_follow_status: published
```

The GUI review run records `gazebo_ogre_shutdown_segfault_observed=true` on
Gazebo teardown. Treat this as a Gazebo GUI shutdown/rendering risk, not as a
controller failure, because the same-run control gate, controller trace,
adapter trace, and truth-pose evaluation all passed before teardown. Human
visual acceptance is still a review decision; the evidence above proves only
the temporary AWFF behavior-wrapper bridge and camera-follow request, not final
manual animation acceptance or formal generated-controller deployment.

Evaluation policy:

```text
takeoff/hover transition error is recorded as hover_max_abs_z_error_m;
hover pass/fail uses hover_settled_max_abs_z_error_m after the declared
settled fraction, because the first part of the hover phase includes ramp
settling from takeoff.

airborne tilt is evaluated separately from low-altitude/contact tilt.
```

Do not overclaim this result:

```text
accepted:
  temporary MWORKS AWFF equation behavior-wrapper same-run Gazebo
  takeoff-hover-land response through ControllerOutput and Gazebo actuator
  adapter.

not accepted yet:
  generated C/C++ PX4-native controller deployment
  full SIL equivalence for AWFF_FullController_Sysblock
  PX4 Offboard or PX4 module/uORB adapter
  PX4+Gazebo takeoff-hover-land driven by generated AWFF C/C++ runtime
  final competition controller performance
  planner_ready
  final closed_loop acceptance
  multi-UAV readiness
```

For the plant-only baseline, the stable shell remains
`Scripts/ros/gazebo_truth_takeoff_hover_land_controller.py`. It proves the
accepted Gazebo plant and actuator interface can perform bounded
takeoff-hover-land independently of the MWORKS/AWFF wrapper. It is not final
competition controller-performance evidence.

Formal PX4-native implementation gates:

```text
Gate 0: PX4+Gazebo baseline
  input: official PX4/Gazebo or YunZong-compatible baseline model
  evidence: PX4 SITL starts, Gazebo model exists, sensors publish, actuator
  loop is controlled by PX4, takeoff-hover-land baseline is reproducible

Gate A: generate AWFF code
  input: Models/MoSimQuadrotorModel/Controllers/Sysblocks/AWFF_FullController_Sysblock.mo
  status: passed for run Results/generated_mworks/AWFF_FullController_Sysblock_20260620_032747/
  evidence: CODEGEN_MANIFEST.json, generated file list, source hash

Gate B: compile generated AWFF C
  status: passed for AWFF_FullController_Sysblock_20260620_032747
  evidence: runtime_schema_smoke_check.json, WSL gcc C99 compile command, no generated-folder pollution

Gate C: AWFF generated-runtime schema
  status: passed for AWFF_FullController_Sysblock_20260620_032747
  evidence: discovered input/output global structs, eight input fields, four
  output fields, 0.01 s sample time, explicit field-order manifest at
  runtime_schema.json

Gate D: AWFF SIL equivalence
  status: constant-input pass; time-varying hardening pending
  evidence:
    Results/generated_mworks/AWFF_FullController_Sysblock_20260620_032747/mworks_awff_fullcontroller_constant_reference.json
    Results/generated_mworks/AWFF_FullController_Sysblock_20260620_032747/runtime_schema_constant_positive.json
    Results/generated_mworks/AWFF_FullController_Sysblock_20260620_032747/sil_constant_input_check.json
  result:
    real MWORKS reference plus generated C runtime, nonzero 8-input/4-output
    constant row, tolerance 1e-5, max_abs_error about 1.23e-8, pass
  note: sil_synthetic_multi_output_checker_gate.json proves only checker
  capability against a synthetic reference, not MWORKS equivalence.

Gate E: choose PX4 integration level
  evidence: explicit decision between L1 Offboard setpoint, L2 PX4 controller
  module/uORB replacement, or deferred L3 actuator-level route; input/output
  uORB or ROS2/PX4 message schema recorded

Gate F1: L1 Offboard adapter, if chosen
  evidence: generated C/C++ wrapper produces PX4-compatible setpoints, publishes
  continuous OffboardControlMode/setpoint stream above the PX4 offboard
  proof-of-life threshold, handles coordinate conversion, mode, arming, stale
  command, and failsafe policy

Gate F2: L2 PX4 module/uORB adapter, if chosen
  evidence: generated C/C++ wrapper is compiled into PX4 SITL, reads declared
  uORB inputs, writes declared setpoint/control outputs, respects PX4 timing,
  parameter, reset, mode, and failsafe boundaries

Gate G: PX4+Gazebo takeoff-hover-land
  evidence: same-run PX4 logs/uORB or ROS2 bridge traces, Gazebo truth, actuator
  echo, motor response, stable takeoff/hover/landing metrics

Gate H: PX4+Gazebo 8字 and static-obstacle scenario
  evidence: same-run PX4/Gazebo animation/review surfaces plus metrics. This
  gate is still single-UAV only; do not enter multi-UAV implementation from
  this path.

Gate I: sensor-localization closure
  evidence: Gazebo MID360/IMU -> FAST-LIO or accepted estimator -> odom/pose
  feeds the chosen PX4/Offboard state path. Point cloud is localization input,
  not a substitute for the PX4 control loop.
```

Python may still orchestrate these gates, generate manifests, compare traces,
plot figures, and run checkers. Python must not sit in the control loop for a
result claimed as formal generated-controller deployment, except as a temporary
fixture explicitly labeled outside the PX4-native route.

## 6. Required MCP Improvement

Add a project MCP tool for code generation instead of overloading
`translate_model`.

Minimum tool surface:

```text
get_code_generation_options(model_name)
set_code_generation_options(model_name, options)
generate_model_code(model_name, output_dir)
summarize_generated_code(output_dir)
```

The tool must expose whether `GenerateModelCode` succeeded and list generated
files under the requested project-local output directory.

## 7. Architecture Implication

MoSim should reuse the RflySim/Simulink/PX4 role split, but replace the
controller code-generation source with MWORKS:

```text
MWORKS/Sysblock
  -> controller design, MIL/SIL, formal metrics, code generation

PX4 SITL / future hardware PX4
  -> flight mode, estimator, failsafe, uORB, control allocation, actuator pipeline

Generated C/C++ adapter
  -> Offboard setpoint adapter or PX4 module/uORB wrapper around MWORKS code

UE / MoSimSceneLibrary
  -> rendering, camera, collision and sensor oracle

Current ROS1 Sunray lane
  -> Gazebo Classic, PX4, MAVROS, px4ctrl-compatible controller wrapper,
     FAST-LIO/local map/planner review, RViz evidence

Historical/future ROS2 / RViz2 lane
  -> LiDAR/IMU/TF, FAST-LIO, local 3D map, planner, Offboard setpoint bridge,
     review, only when explicitly reopened
```

Do not resume hand-built point-cloud/grid demos or ROS2-direct-to-Gazebo motor
control as the product route. The current implementation path is whatever the
mainline board selects: at present, bounded L1/AWFF, safety-filter, and
fault-allocation enhancement reopening through minimal Gazebo evidence,
followed by MWORKS/codegen promotion only for accepted enhancements. PX4
Offboard or PX4 module/uORB integration is a later gated branch.

## 8. 2026-06-02 Source Check

External and local checks support this route:

- MathWorks Simulink Coder officially generates and executes C/C++ code from
  Simulink models, Stateflow charts, and MATLAB functions for real-time,
  non-real-time, rapid-prototyping, and HIL-style workflows:
  `https://www.mathworks.com/products/simulink-coder.html`.
- RflySim's documented split is CopterSim for kinematic simulation,
  Unreal/RflySim3D for high-fidelity scene simulation, QGroundControl for
  mission/monitoring, PX4PSP for MATLAB/Simulink-based firmware-level automatic
  code generation, and Python/ROS interface libraries for upper-layer AI
  validation: `https://rflysim.com/doc/en/1/Intro.html`.
- PX4 ROS2 Offboard is a continuous streamed-control contract. PX4 requires
  repeated `OffboardControlMode`/setpoint traffic and drops out of offboard
  mode if the proof-of-life stream falls below about 2Hz:
  `https://docs.px4.io/main/en/ros2/offboard_control`.
- AirSim is a C++/Unreal simulator with PX4/ArduPilot SIL/HIL support and
  ROS/ROS2 wrappers. This is useful as a bridge/API reference, but it should
  not replace MWORKS as MoSim's controller and plant-solver authority:
  `https://github.com/microsoft/AirSim` and
  `https://microsoft.github.io/AirSim/airsim_ros_pkgs/`.

MoSim decision: copy the architecture pattern, not the solver. MWORKS owns
controller design, MIL/SIL, metrics, and code generation. Current runtime
plant/control evidence is ROS1/Sunray/Gazebo Classic/PX4/MAVROS/px4ctrl with
RViz review. UE owns rendering and optional scene/sensor oracle work only
after the control/codegen lane is stable. ROS2/RViz2 remains historical or
future reference unless explicitly reopened.
