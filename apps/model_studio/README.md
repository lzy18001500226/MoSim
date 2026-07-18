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

The source interface does not inherit D4 runtime
acceptance. It does not prove MWORKS simulation/codegen, MWORKS Live timing,
Gazebo/PX4/MAVROS runtime, QGC handoff, fault application, or flight performance.
