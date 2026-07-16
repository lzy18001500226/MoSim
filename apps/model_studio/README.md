# MoSim Model Studio

MoSim Model Studio is a lightweight native MWORKS.Syslab APP. Its source of
truth is the `TyAppDesigner` implementation in `src/app.jl`.

The APP owns experiment selection, capability gating, compact parameter input,
result summaries, and submission to the MoSim Orchestrator. It does not replace
Sysplorer graphical modeling, the native MWORKS result viewer, or runtime flight
control.

## Current D1 proof

The first capability proof includes:

- native `TyAppDesigner` window and callbacks;
- controller and UAV-count dropdowns;
- visible unavailable options with hard request rejection;
- numeric parameter input;
- native plot area;
- local, auditable Orchestrator request creation;
- dedicated buttons reserved for Sysplorer and result-viewer requests.

Run the source inside Syslab:

```julia
include(raw"C:\Users\HP\Desktop\MoSim\apps\model_studio\src\app.jl")
```

The D1 native APP Designer gate passed on 2026-07-17. The installable artifact is:

```text
apps/model_studio/dist/MoSim Model Studio.slappinstall
```

Machine-readable evidence is stored at:

```text
Results/ui_platform/model_studio_d1_gate_20260717/GATE.json
```

This gate proves the native APP, capability rejection, request creation, and
packaging path. Orchestrator request consumption and runtime integration remain
D3-D7 work.
