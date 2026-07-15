# G9 MWORKS Generated Runtime Closeout

Date: 2026-07-15

Purpose: close the six G9 `ATTITUDE_THRUST` controllers through the actual
MWORKS-generated C backend in the current ROS1/Sunray/Gazebo/PX4/MAVROS/
px4ctrl lane. This is a task-specific acceptance plan. Durable code-generation
rules remain in `Docs/Workflows/mworks_codegen_controller_runtime.md`.

## 1. Scope And Current State

Controller mapping is frozen:

| Id | Profile |
|---:|---|
| 1 | `official_pid` |
| 2 | `se3_basic` |
| 3 | `dfbc_basic` |
| 4 | `smc_boundary_layer` |
| 5 | `pid_indi` |
| 6 | `nmpc_outer` |

Accepted inputs already exist:

```text
model: G9_Family_CFunction_Sysblock
GenerateModelCode: passed
generated-C offline equivalence: 450 cases / 0 failures
static ROS/Sunray adapter: 450 cases / 0 failures
frozen plant/planner baseline: G8 plus current Diff single/three-UAV baselines
```

These inputs prove code generation and offline equivalence. Existing G9
Gazebo/Diff runs prove that named controller profiles flew, but their manifests
do not uniquely identify the compiled generated-code backend. They therefore
remain useful regression evidence, not final generated-runtime provenance.

## 2. Closure Levels

`competition_minimum` requires, for all six controllers:

```text
unambiguous generated-C build/load provenance
  -> static/codegen/offline gates pass
  -> takeoff-hover-land pass
  -> representative trajectory pass
```

`full_project` additionally requires, for all six controllers:

```text
Diff single-UAV pass
  -> Diff three-UAV pass
```

Do not call all six controllers fully closed unless `full_project` passes. A
controller that passes only `competition_minimum` must be labeled exactly at
that level.

## 3. Frozen Architecture

The accepted runtime path is:

```text
G9_Family_CFunction_Sysblock generated C
  -> px4ctrl generated-family wrapper
  -> MAVROS attitude-plus-thrust setpoint
  -> PX4 SITL
  -> Gazebo Classic Sunray150 plant
  -> RViz/log/metric evidence
```

The build must select:

```text
MOSIM_PX4CTRL_GENERATED_BACKEND=g9_family
```

The runtime profile then selects controller id 1 through 6. The equivalent
project C++ core is an oracle and fallback implementation only; it is not an
accepted runtime backend for this closeout.

During validation, do not retune the plant, controller parameters, state
source, planner, safety thresholds, or frozen mission targets. Do not touch
FUEL, RACER, UE, G9.5/G9.6, G10, or the deferred PX4-native/uORB branch.

## 4. Runtime Provenance Contract

Every accepted run must write a machine-readable provenance record containing:

```text
schema
backend=mworks_generated_c
controller_id
controller_name
generated_model_name=G9_Family_CFunction_Sysblock
generated_code_path
generated_code_sha256
codegen_manifest
runtime_loaded_symbol
build_backend_definition=MOSIM_PX4CTRL_GENERATED_BACKEND_G9_FAMILY
px4ctrl_executable_path
px4ctrl_executable_sha256
build_timestamp_utc
source_commit_or_tree_identity
```

Minimum runtime-loaded symbol evidence is the generated model `Step()` path and
the selected controller id. A profile name, ROS parameter dump, source-file
presence, CMake cache entry, or generic `use_mosim_generated_core=true` log is
not sufficient by itself.

The checker must fail closed when:

- the backend is missing, unknown, or not `mworks_generated_c`;
- the build definition is missing or selects another generated family;
- the generated source hash differs from the accepted codegen manifest;
- the executable hash is absent;
- the runtime symbol/controller-id acknowledgement is absent or inconsistent;
- fallback to the equivalent C++ core is possible without an explicit failure.

## 5. Fail-Fast Gate Sequence

Run one controller at a time in this order:

```text
official_pid provenance baseline
se3_basic
dfbc_basic
smc_boundary_layer
pid_indi
nmpc_outer
```

For each controller:

1. Verify generated artifacts, hashes, CMake backend, executable identity, and
   runtime acknowledgement.
2. Reuse or rerun the generated-C offline and static adapter checks only when
   their recorded hashes no longer match the selected generated source.
3. Run `takeoff_hover_land` with bounded timeout and preserve logs/metrics.
   Before publishing TAKEOFF, require the MAVROS/PX4 control odometry to hold
   the declared speed and roll/pitch limits continuously. The current strict
   gate uses 3 s stable time, a 20 s bounded wait, and 0.5 deg maximum absolute
   roll/pitch. Record `pre_takeoff_state_gate` in the mission metrics and stop
   before takeoff when it fails.
4. Run a representative trajectory. Prefer the existing figure-eight mission;
   use spiral or XYZ step only when needed to exercise a controller-specific
   axis or state.
5. For `full_project`, run Diff single-UAV, then Diff three-UAV.
6. Stop that controller at its first failed gate. Preserve the failed result
   and do not hide it with a later retry.

The next controller may proceed only if the failure is controller-local and
does not invalidate shared build provenance or the frozen runtime baseline.

## 6. Evidence Layout

Use one immutable root:

```text
Results/sunray_ros1/g9_mworks_generated_runtime_closeout_<timestamp>/
  BUILD_PROVENANCE.json
  CONTROLLER_MATRIX.json
  SUMMARY.md
  official_pid/
  se3_basic/
  dfbc_basic/
  smc_boundary_layer/
  pid_indi/
  nmpc_outer/
```

Each controller directory must link or contain the provenance check, mission
manifest, runtime log acknowledgement, trajectory metrics, and any Diff
metrics required by the claimed closure level. Existing result directories may
be referenced, but ambiguous old provenance cannot be promoted to a pass.

## 7. Stop Conditions

Stop and record a blocker when any of these occurs:

- MWORKS login, license, authorization, or unknown GUI state blocks a required
  regeneration or model check;
- generated source or accepted manifest drift is detected;
- the build cannot prove `g9_family` selection;
- runtime acknowledgement or executable identity is ambiguous;
- PX4/Gazebo baseline fails under `official_pid` before controller comparison;
- the pre-takeoff state gate cannot obtain continuously stable connection,
  speed, and roll/pitch evidence inside its bounded wait;
- a live process exceeds its bounded timeout;
- a proposed fix changes controller/plant/planner tuning or the architecture.

Do not switch to ROS2/x500, a Python-equivalent controller, direct Gazebo motor
control, or the project C++ oracle to turn a blocker into a pass.

## 8. Final Acceptance Matrix

`CONTROLLER_MATRIX.json` and `SUMMARY.md` must report these columns for every
controller:

```text
controller_id
controller_name
provenance
generated_c_offline
static_adapter
takeoff_hover_land
representative_trajectory
diff_single
diff_three_uav
closure_level
result_paths
first_blocker
```

Only after the matrix is complete may
`Docs/Workflows/mainline_operations_board.md` and the permanent code-generation
workflow state that the six-controller generated-runtime route is closed.
