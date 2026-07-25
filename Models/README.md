# MWORKS Model Library

`MoSimQuadrotorModel/` is the only project-owned Modelica package root. Open
and load:

```text
Models/MoSimQuadrotorModel/package.mo
```

Nested `package.mo` files define Modelica namespaces. They are required for
modularity and are not separate projects or duplicate package roots.

## Package Map

| Namespace | Responsibility |
|---|---|
| `Parameters`, `Plant`, `Dynamics`, `System` | vehicle parameters, plant, actuator/dynamics, system modules and architecture |
| `Controllers` | baselines, graphical MIL controllers, Sysblocks, and integrated control chains |
| `ExperimentRunner` | typed adapters, formal runners, shared plant/result contracts, and test composition |
| `Missions`, `Robustness`, `Planning`, `Formation` | official tasks and scenario-specific compositions |
| `LiveIntegration` | controlled MWORKS Live bridge entry; disabled unless its explicit gates pass |
| `SceneTrace`, `Support` | diagnostics, supporting models, fixtures, and reusable helpers |

## Rules

- Do not create a second top-level Modelica root for a controller, experiment,
  screenshot, or temporary workaround.
- Put a new reusable model in the owning namespace and give it a clear runner
  or scenario relationship.
- Preserve parameter provenance. SDF, Gazebo, Blender, and reference values do
  not become real-aircraft truth without corresponding evidence.
- Before moving or deleting a model, audit Modelica imports, scripts,
  configuration, documentation, and result-manifest references.

See `../Docs/Index/simulation_model_structure_index.md` for model-to-scenario,
runner, and result routing.
