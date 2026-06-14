# Source Anchor Materialization Rationale

023 inspected the formal `MoSimQuadrotorModel.Dynamics` alias package, `package.order`, the `MoSimQuadrotorModel.Parameters` provenance record, and the concrete project-owned `QuadrotorExperiments.DynamicsUpgrade` implementation files.

The current formal source-surface rule is:

- All formal Dynamics entries should be dedicated extends-only `.mo` files.
- Dedicated formal sources must not duplicate equations from `QuadrotorExperiments.DynamicsUpgrade`.

Current materialized dedicated surfaces:

- `RotorActuatorCore.mo`
- `HoverSmoke.mo`
- `YawStepSmoke.mo`
- `RotorEffectivenessSmoke.mo`
- `WrapperSurface.mo`
- `ActuatorCommandMapper.mo`
- `ActuatorMappedWrapperSurface.mo`
- `OptionalDampingGyroLayer.mo`
- `WrapperHoverSmoke.mo`
- `WrapperYawStepSmoke.mo`
- `PhysicalWrenchAdapter.mo`
- `PhysicalWrenchHoverSmoke.mo`
- `PhysicalWrenchYawStepSmoke.mo`

Static acceptance basis:

- The 13 formal Dynamics entries are present and ordered in `Models/MoSimQuadrotorModel/Dynamics/package.order`.
- All formal Dynamics entries exist as extends-only formal source files.
- `Dynamics/package.mo` is a package shell and does not duplicate model definitions.
- Each compatibility alias extends a concrete project-owned implementation model under `Models/QuadrotorExperiments/DynamicsUpgrade/`.
- The formal smoke surface can be prepared as a target matrix, expected variable manifest, and future live validation queue without duplicating dynamics behavior.

This rationale remains static-only. Live `check_model` and `SimulateModel` acceptance are still future gates.
