# MWORKS Model Library

`MoSimQuadrotorModel/` is the only project-owned Modelica package root. Load
`Models/MoSimQuadrotorModel/package.mo`; no other directory under `Models/` is
a second project or a required dependency root.

## Normal Entry Points

| Need | Open this class | Purpose |
|---|---|---|
| Physical airframe | `MoSimQuadrotorModel.Vehicle.Sunray150Assembly` | Sunray150 whole-aircraft plant assembly |
| Graphical system review | `MoSimQuadrotorModel.Experiment.CompleteSystemGraphical` | Direct graphical whole-system architecture entry |
| Controller closed loop | `MoSimQuadrotorModel.Experiment.Runners.<Controller>FormalRunner` | One formal whole-aircraft runner per controller route |
| PID legacy example review | `MoSimQuadrotorModel.Control.LegacyExamples.PidVariants.<Example>` | Original Example1/2/3 PID variants retained for report and demo review |
| Reference trajectory | `MoSimQuadrotorModel.Guidance.Trajectories.<Trajectory>` | Replaceable reference used by formal runners |
| Three-aircraft formation prototype | `MoSimQuadrotorModel.Guidance.Formation.TriangleFigure8LinearMPC` | MWORKS prototype only; separate from the ROS/Gazebo deployment route |

The active controller route catalog is the 48-entry matrix in
`Config/control_platform/formal_closed_loop_harness_map.json`. It contains the
px4ctrl route, official PID baseline, and the project controller routes. The
catalog is the authority for route names and semantic grouping; folders are not
used to invent extra controller families.

## Package Responsibilities

| Namespace | Responsibility |
|---|---|
| `Parameters` | Sunray150 parameter records and source provenance |
| `Vehicle` | Airframe assembly, physics, actuation, sensing, and physical support blocks |
| `Control` | Controllers, graphical Sysblocks, equation bridges, adapters, and allocation |
| `Experiment` | Formal runners and direct system-review entry points |
| `Guidance` | Trajectories, planning, and formation references |
| `Deployment` | Explicit MWORKS Live and code-generation integration boundary |
| `Visualization` | Visualization and trace-review support |
| `Common` | Shared types and reusable helpers |

Nested `package.mo` files define Modelica namespaces. They are not independent
projects. A package is nested only when it owns a reusable subsystem or a
large collection of peer models, such as the controller-route runner collection.

## Browser Visibility

The normal MWORKS browser hides lower-level support packages and retained
historical diagnostics. New models and active configuration may depend on their
public classes, but they are not primary model-library entry points:

- `Vehicle.Blocks`, `Vehicle.Electricals`, `Vehicle.GroundModel`, `Vehicle.Mechanics`,
  `Vehicle.Sensors`, and `Vehicle.Utilities`: implementation support packages.
- `Vehicle.LegacyDiagnostics`: fixed-input plant smoke models.
- `Control.LegacyExamples.PidVariants`: retained original PID example variants;
  direct review only, not the formal closed-loop experiment route.
- `Experiment.Probes`, `Experiment.Scenarios`, and `Experiment.Templates`: retained
  diagnostic, historical scenario, and implementation-template sources.
- `Guidance.Formation.Scenarios` and `Visualization.Diagnostics`: historical
  prototype and trace diagnostics.

`Vehicle.Dynamics` remains visible as the production actuator, rotor-dynamics,
and physical-wrench package. `Vehicle.Examples` also remains visible so the
original graphical examples can be opened directly for report and demo review.

The formal seven-scenario work is composed through a formal runner plus a
trajectory and injection parameters. It does not require selecting one of the
hidden historical scenario graphs.

## Maintenance Rules

- Do not create a second top-level Modelica root for a controller, experiment,
  screenshot, or temporary workaround.
- Put reusable production code in its owning namespace, and add a runner only
  when it is a real whole-aircraft execution boundary.
- Preserve fully-qualified-name compatibility through a hidden alias before
  moving a referenced class; remove it only after a dependency audit.
- Preserve parameter provenance. SDF, Gazebo, Blender, and reference values do
  not become real-aircraft truth without corresponding evidence.
- Before moving or deleting a model, audit Modelica imports, scripts,
  configuration, documentation, and result-manifest references.
