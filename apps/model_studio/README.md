# MoSim Model Studio

MoSim Model Studio is a lightweight native MWORKS.Syslab APP. Its source of
truth is the `TyAppDesigner` implementation in `src/app.jl`.

The APP owns experiment selection, capability gating, compact parameter input,
result summaries, and submission to the MoSim Orchestrator. It does not replace
Sysplorer graphical modeling, the native MWORKS result viewer, or runtime flight
control.

## Current D4 proof

The current MVP includes:

- native `TyAppDesigner` window and callbacks packaged as version `0.2.0`;
- Registry/Profile Catalog driven profile, controller, and UAV-count dropdowns;
- visible unavailable options with hard rejection by both the APP and Orchestrator;
- numeric parameter input;
- native plot area;
- persistent Orchestrator request/response integration;
- preparation of one- and three-UAV `px4ctrl` runs with a stable `run_id` and
  profile hash;
- bounded model-context and result-packet requests.

Run the source inside Syslab:

```julia
include(raw"C:\Users\HP\Desktop\MoSim\apps\model_studio\src\app.jl")
```

The D4 native APP/Orchestrator gate passed on 2026-07-17. The installable
artifact is:

```text
apps/model_studio/dist/MoSim Model Studio.slappinstall
```

Machine-readable evidence is stored at:

```text
Results/ui_platform/model_studio_d4_gate_20260717/GATE.json
```

This gate proves the native APP, clean packaging, capability rejection, run
preparation, model-context request, and correct unavailable-result boundary. It
does not prove MWORKS simulation/codegen, Gazebo/PX4/MAVROS runtime, RViz/UE
attachment, or flight performance; those remain D6-D7 integration gates.
