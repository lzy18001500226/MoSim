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
| `Parameters` | vehicle parameters and source provenance |
| `Vehicle` | Sunray150 assembly, physical plant, actuators, sensors, and dynamics |
| `Control` | baselines, graphical MIL controllers, Sysblocks, adapters, bridges, and allocation |
| `Experiment` | formal runners, scenario composition, result contracts, and test fixtures |
| `Guidance` | trajectories, planning, formation, and task guidance |
| `Deployment` | controlled MWORKS Live and code-generation integration entries |
| `Visualization` | scene trace, review, and visualization support |
| `Common` | reusable helpers and shared model types |

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
