# MoSim Model Studio

MoSim Model Studio is a lightweight native MWORKS.Syslab APP. Its source of
truth is the `TyAppDesigner` implementation in `src/app.jl`.

The APP owns experiment Profile design, capability gating, offline model
operations, and preparation for QGC handoff. QGC owns flight operations and the
Orchestrator remains the only runtime command arbiter. The APP does not replace
Sysplorer graphical modeling, the native MWORKS result viewer, or runtime flight
control.

## Current D4 proof

The current source UI baseline includes:

- three execution modes: offline model validation, MWORKS Live, and generated-C
  deployment;
- layered mission, position-loop, attitude-loop, augmentation, safety, and
  output-boundary controls;
- a locked PX4 attitude/rate inner loop for `ATTITUDE_THRUST v1`;
- fixed-direction wind and four independent motor-effectiveness sliders;
- separate requested and applied injection values;
- separate offline MWORKS actions and QGC flight handoff actions;
- editable MWORKS/ROS target host, RT1 UDP port, ROS Master URI and local advertised IP;
- a real ROS Master plus RT1 request-response connection preflight;
- a 50/100/200 Hz capability selector with 50 Hz as the accepted baseline and
  200 Hz explicitly blocked until a new RT0/profile gate passes;
- connection RTT and measured payload/wire-rate status returned by the backend;
- no synthetic response plot, direct arm/takeoff action, or runtime command in
  the UI-review build.

## Offline profile binding

The offline selector now mirrors the current accepted evidence catalog:

- 8 single-UAV Certified Profiles;
- 1 three-UAV Certified Profile;
- 2 Custom Profile end-to-end proofs;
- QP/NMPC Safety remains visible but disabled because both the shared-runner
  and dedicated-model current runs were numerically unstable.

The APP exposes Profile names rather than backend model names. A Profile may
use a shared Runner, a dedicated Runner with the shared Plant/Animation, or a
dedicated full model as the final fallback. Every route keeps the same native
result and numeric acceptance contract. Batch certification uses
`--gui-reset-windows --shutdown-session` so model, plot, result, animation, and
dedicated Sysplorer windows do not accumulate after a run.

## Batch execution and routine regression

The offline MIL action starts the batch backend asynchronously. While a batch
is active, the action changes to a cancellation request; cancellation is
cooperative and takes effect only after the active Profile has finished its
normal result recording and session/window cleanup. It must not terminate the
shared Sysplorer process.

The backend is the authoritative automation surface for routine regression:

```powershell
python Scripts/mworks/run_offline_profile_batch.py --profile-id <profile_id>
python Scripts/mworks/run_offline_profile_batch.py --retry-batch-id <batch_id>
python Scripts/mworks/run_offline_profile_batch.py --request-cancel <batch_id>
```

Certified Profiles are rerun by catalog ID. Custom Profiles are rerun from
their frozen request JSON with `--request-json`, so a generated wrapper and its
inputs remain attributable. Terminal manifests rebuild
`Results/control_platform/offline_batches/BATCH_INDEX.json`, including
accepted, blocked, and cancelled counts.

Routine APP regression should call these command-line/backend surfaces and
inspect manifests, the result index, tests, and background window captures.
It does not require repeated foreground clicking. A real Syslab source load is
still required when the APP source or layout changes, because TyAppDesigner
depends on the Syslab GUI service; one bounded load and window-level capture is
sufficient unless the change specifically affects interactive UI behavior.

Run the source inside Syslab:

```julia
include(raw"C:\Users\HP\Desktop\MoSim\apps\model_studio\src\app.jl")
```

The earlier D4 native APP/Orchestrator gate passed on 2026-07-17. Its installable
artifact remains historical evidence for the older wired baseline:

```text
apps/model_studio/dist/MoSim Model Studio.slappinstall
```

Machine-readable evidence is stored at:

```text
Results/ui_platform/model_studio_d4_gate_20260717/GATE.json
```

The current P7 source/runtime and orchestration closeout is stored at:

```text
Results/ui_platform/model_studio_p7_runtime_20260719/GATE.json
```

It validates current-source loading, the three UI modes, offline Profile
binding, asynchronous batch execution, safe cancellation, Custom request-based
rerun, command-line regression, and a window-level layout capture. No new full
MWORKS batch was run for this APP closeout; the existing Profile-specific P7
MWORKS acceptance records remain the simulation authorities.

The source interface does not inherit D4 runtime
acceptance. It does not prove MWORKS simulation/codegen, MWORKS Live timing,
Gazebo/PX4/MAVROS runtime, QGC handoff, fault application, or flight performance.

## Current workspace actions

The `在线建模验证` workspace has two primary actions: `应用配置` records the
current layer selection without starting a solver, and `打开仿真模型` loads the
selected model into the existing MWORKS session. The `实时联合仿真` workspace
uses the same two actions, with `打开联合仿真模型` loading the MWORKS Live
model. Neither workspace starts, stops, or opens a result; after the model is
open, run the simulation from MWORKS itself.

The model-opening path is `Scripts/ui/open_model_studio_model.py`. It is
restricted to `model_manager.load_file` followed by `model_manager.open` and
does not call model checking, simulation, result, flight, or solver-lifecycle
operations. It writes its last bounded operation record to
`Results/ui_platform/model_studio_open_model/latest.json`.
