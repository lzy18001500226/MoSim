# MoSim Studio

MoSim Studio is a lightweight native MWORKS.Syslab APP. Its source of
truth is the `TyAppDesigner` implementation in `src/app.jl`.

The APP owns experiment Profile authoring, capability gating, offline model
operations, and MWORKS model/result/code-project entry points. QGC selects a
published compatible Profile, owns native flight operations, and provides the
operator surface for discrete fault application and recovery. The APP does not
replace Sysplorer graphical modeling, the native MWORKS result viewer, or
runtime flight control.

## Current D4 proof

The current source UI baseline includes:

- four workspaces: offline model validation, MWORKS Live, generated-C
  model entry, and the local-context `MoSim 助手`;
- `MoSim 助手` reads the current Profile/control-chain selections and provides
  local MWORKS, QGC, fault, and result-viewing guidance only; it does not start
  MWORKS, export code, or send flight/runtime commands;
- an eight-task single-UAV model-validation selector: one `ClimbPath 50 s`
  baseline plus hover, step, Figure8, spiral, wind, parameter mismatch, and
  motor-efficiency-fault tasks;
- dynamic controller-family and controller-instance selection, with fixed
  FormalRunner interface layers shown as read-only on the model page;
- a fixed +X external-force slider, synchronized mass/all-inertia mismatch
  slider, and four motor-effectiveness sliders whose model-task fault starts
  at 15 s;
- a real frozen task-configuration handoff rather than a log-only apply action;
- separate offline MWORKS actions and QGC flight handoff actions;
- editable MWORKS/ROS target host, RT1 UDP port, ROS Master URI and local advertised IP;
- a real ROS Master plus RT1 request-response connection preflight;
- a 50/100/200 Hz capability selector with 50 Hz as the accepted baseline and
  200 Hz explicitly blocked until a new RT0/profile gate passes;
- connection RTT and measured payload/wire-rate status returned by the backend;
- no synthetic response plot, direct arm/takeoff action, or runtime command in
  the UI-review build.

## Legacy offline profile binding

The older offline Profile selector remains source/history for the legacy batch
workflow. It is not exposed as a quick preset on the current single-UAV model
validation page:

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

The earlier D4 native APP/Orchestrator gate passed on 2026-07-17. Its
`MoSim Model Studio` installable artifact remains historical evidence for the
older wired baseline; it is not the current `MoSim Studio` installation:

```text
apps/model_studio/dist/MoSim Model Studio.slappinstall
```

The next `MoSim Studio.slappinstall` package may be produced only after a
separately authorized Syslab packaging run.

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

The `在线建模验证` workspace has three explicit actions. `写入配置` freezes the
selected task, controller, and permitted scenario values to
`Results/ui_platform/model_studio_task_handoffs/latest.json`, and writes a
hash-bound temporary Modelica harness beside it. `打开仿真模型` opens exactly
that frozen harness and runs native `CheckModel`; it does not start a solver.
`重置` restores the selected task's standard values. The formal seven-scenario
route is limited to `official_pid` and `px4ctrl`, because those are the only
two registered FormalRunners in the v2 contract. A nonstandard slider value is
recorded as a task parameter variant, not as existing formal evidence.

The `实时联合仿真` workspace retains its separate controls and opens its own
MWORKS Live model. Neither workspace starts, stops, or opens a result; after
the model is open, run the simulation from MWORKS itself.

The `代码生成` workspace uses the same manual boundary. It filters the active
controller catalog by family, opens the selected MWORKS graphical model, and
does not call `GenerateModelCode`, compile generated files, or open a result.
After the model is visible, use MWORKS's native `代码生成` ribbon action and
inspect the generated artifacts there.

The model-opening path is `Scripts/ui/open_model_studio_model.py`. It starts a
dedicated Sysplorer session through the official
`ModelingPy.StartSysplorer(start_mode="-gui", processPath=...)` API, loads the
official quadrotor package and the three project packages in the
same order used by profile certification, then opens the selected class. An
offline model must also pass `CheckModel` before the APP reports success. A
custom combination opens the qualified mother Runner for its selected output
boundary; a certified Profile loads its frozen generated wrapper after the
packages. A lightweight ModelingPy worker remains connected while that
dedicated Sysplorer session is open so the loaded package context is retained
for manual simulation. The selected model window is restored and brought to the foreground.
This action does not simulate the model, open a result, start a flight task, or
change solver lifecycle. It writes its last bounded operation record to
`Results/ui_platform/model_studio_open_model/latest.json`.
