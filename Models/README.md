# MWORKS Model Library

`MoSimQuadrotorModel/` is the only project-owned Modelica package root. Load
`Models/MoSimQuadrotorModel/package.mo`; no other directory under `Models/` is
a second project or a required dependency root.

## Current Architecture Lock (2026-08-21)

The current source tree is already on the new architecture. This section is the
source-navigation rule for new work:

- `Control/<family>/<controller>/` owns the reusable controller core and its
  typed interface boundary.
- `Experiment/SingleUav/<family>/` owns the 46 single-aircraft graphical
  review runners. The runner-to-core mapping is recorded in
  `Results/architecture_verification_20260821/preflight/singleuav_runner_control_map.md`.
- The parallel `Experiment/<Family>/` runner files are thin compatibility
  shells that extend the `SingleUav` runners; they are not a second controller
  implementation and must not be rebuilt as independent routes.
- `Experiment/Baselines`, `Experiment/Formation`, and `Experiment/OpenBlocks`
  are separate current entry families with their own boundaries.
- `Experiment/Runners` is not part of the current package tree. Do not restore
  or copy archived `Experiment.Runners.*` sources into the active tree.

The structural CheckModel evidence for the current representative routes is in
`Results/architecture_verification_20260821/CHECKMODEL_MWORKS_MCP.json`.
It proves model structure only; it does not prove simulation, closed-loop,
planner, or robotics-runtime success.

## Normal Entry Points

| Need | Open this class | Purpose |
|---|---|---|
| Physical airframe | `MoSimQuadrotorModel.Vehicle.Sunray150Assembly` | Sunray150 whole-aircraft plant assembly |
| Graphical system review | `MoSimQuadrotorModel.Experiment.Templates.Architecture.CompleteSystemGraphical` | Direct graphical whole-system architecture entry |
| Controller closed loop | `MoSimQuadrotorModel.Experiment.SingleUav.<Family>.<Controller>GraphicalRunner` | Current single-aircraft review Runner; top-level family wrappers only preserve FQN compatibility |
| PID legacy example review | `MoSimQuadrotorModel.Control.LegacyExamples.PidVariants.<Example>` | Original Example1/2/3 PID variants retained for report and demo review |
| Reference trajectory | `MoSimQuadrotorModel.Guidance.Trajectories.<Trajectory>` | Replaceable reference used by current review runners |
| Three-aircraft formation prototype | `MoSimQuadrotorModel.Experiment.Formation.Px4Ctrl.ThreeUavPx4CtrlFormationRunner` | MWORKS prototype only; separate from the ROS/Gazebo deployment route |
| OpenBlocks single-aircraft route | `MoSimQuadrotorModel.Experiment.OpenBlocks.Px4Ctrl.SingleUav.Sunray150OpenBlocksStaticRunner` | Frozen OpenBlocks reference review entry |
| OpenBlocks formation route | `MoSimQuadrotorModel.Experiment.OpenBlocks.Px4Ctrl.Formation.ThreeUavPx4CtrlOpenBlocksRunner` | Dynamic OpenBlocks formation review entry |

The APP/manual route catalog is
`Config/control_platform/model_studio_task_routes_v1.toml`. It is the authority
for named Model Studio handoff routes and their declared output boundaries. The
48-entry `Config/control_platform/formal_closed_loop_harness_map.json` is a
separate D2 formal-harness mapping and measured-winner selection contract; it is
not proof that a route is available, simulated, or accepted. Both files remain
subordinate to the `MoSimQuadrotorModel` package root, and neither replaces
native MWORKS `CheckModel` or simulation evidence.

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

The formal seven-scenario work is composed through a current review runner plus
a trajectory and injection parameters. It does not require selecting one of the
hidden historical scenario graphs or restoring an archived Runner package.

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
