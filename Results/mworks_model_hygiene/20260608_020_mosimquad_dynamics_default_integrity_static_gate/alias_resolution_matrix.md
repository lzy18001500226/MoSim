# Alias Resolution Matrix

Task: `PMO-MWORKS-R1-MOSIMQUAD-DYNAMICS-DEFAULT-INTEGRITY-STATIC-GATE-20260608-020`

Scope: static-only source/package audit. No MWORKS/Sysplorer/Syslab GUI, MCP,
`check_model`, `SimulateModel`, Smart Layout, screenshot, or result viewer was
used.

## Result

All 12 formal `MoSimQuadrotorModel.Dynamics` entries resolve statically through
`QuadrotorExperiments.DynamicsUpgrade` compatibility aliases to concrete
project-owned implementation files under
`Models/QuadrotorExperiments/DynamicsUpgrade/`.

| Formal entry | Compatibility alias | Implementation file | Static result |
|---|---|---|---|
| `RotorActuatorCore` | `RotorDynamicsCore` | `Sunray150RflyStyleRotorDynamics.mo` | resolved |
| `HoverSmoke` | `RotorHoverSmoke` | `Sunray150DynamicsUpgradeHoverSmoke.mo` | resolved |
| `YawStepSmoke` | `RotorYawStepSmoke` | `Sunray150DynamicsUpgradeYawStepSmoke.mo` | resolved |
| `WrapperSurface` | `WrapperSurface` | `Sunray150DynamicsWrapperSurface.mo` | resolved |
| `ActuatorCommandMapper` | `ActuatorCommandMapper` | `Sunray150ActuatorCommandMapper.mo` | resolved |
| `ActuatorMappedWrapperSurface` | `ActuatorMappedWrapperSurface` | `Sunray150ActuatorMappedWrapperSurface.mo` | resolved |
| `OptionalDampingGyroLayer` | `OptionalDampingGyroLayer` | `Sunray150OptionalDampingGyroLayer.mo` | resolved |
| `WrapperHoverSmoke` | `WrapperHoverSmoke` | `Sunray150DynamicsWrapperHoverSmoke.mo` | resolved |
| `WrapperYawStepSmoke` | `WrapperYawStepSmoke` | `Sunray150DynamicsWrapperYawStepSmoke.mo` | resolved |
| `PhysicalWrenchAdapter` | `PhysicalWrenchAdapter` | `Sunray150PhysicalWrenchFrameAdapter.mo` | resolved |
| `PhysicalWrenchHoverSmoke` | `PhysicalWrenchHoverSmoke` | `Sunray150PhysicalWrenchHoverSmoke.mo` | resolved |
| `PhysicalWrenchYawStepSmoke` | `PhysicalWrenchYawStepSmoke` | `Sunray150PhysicalWrenchYawStepSmoke.mo` | resolved |

## Boundary

This matrix does not prove live Modelica translation, equation balance,
simulation, package-browser display, graphical layout, or runtime behavior.
Those require a future live MWORKS validation task.
