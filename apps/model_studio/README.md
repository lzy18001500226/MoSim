# MoSim Model Studio

MoSim Model Studio is a lightweight native MWORKS.Syslab APP. Its source of
truth is the `TyAppDesigner` implementation in `src/app.jl`.

The APP owns experiment Profile design, capability gating, offline model
operations, and preparation for QGC handoff. QGC owns flight operations and the
Orchestrator remains the only runtime command arbiter. The APP does not replace
Sysplorer graphical modeling, the native MWORKS result viewer, or runtime flight
control.

## Current D4 proof

The current `0.5.0` UI-review baseline includes:

- three execution modes: offline model validation, MWORKS Live, and generated-C
  deployment;
- layered mission, position-loop, attitude-loop, augmentation, safety, and
  output-boundary controls;
- a locked PX4 attitude/rate inner loop for `ATTITUDE_THRUST v1`;
- fixed-direction wind and four independent motor-effectiveness sliders;
- separate requested and applied injection values;
- separate offline MWORKS actions and QGC flight handoff actions;
- explicit RT0 candidate timing values and unavailable-state explanation;
- no synthetic response plot, direct arm/takeoff action, or runtime command in
  the UI-review build.

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

The `0.5.0` interface is a new UI-review baseline and does not inherit D4 runtime
acceptance. It does not prove MWORKS simulation/codegen, MWORKS Live timing,
Gazebo/PX4/MAVROS runtime, QGC handoff, fault application, or flight performance.
