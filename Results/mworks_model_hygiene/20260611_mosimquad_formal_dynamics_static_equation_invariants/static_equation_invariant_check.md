# Formal Dynamics Static Equation Invariants

Status: `passed`

Static-only source-anchor check for future live smoke variables.

## Anchor Groups

- `rotor_core` -> `Models/MoSimQuadrotorModel/Dynamics/RotorActuatorCore.mo` anchors=12
- `wrapper_surface` -> `Models/MoSimQuadrotorModel/Dynamics/WrapperSurface.mo` anchors=11
- `physical_wrench_adapter` -> `Models/MoSimQuadrotorModel/Dynamics/PhysicalWrenchAdapter.mo` anchors=10
- `rotor_effectiveness_smoke` -> `Models/MoSimQuadrotorModel/Dynamics/RotorEffectivenessSmoke.mo` anchors=6

## Model Sources

- `MoSimQuadrotorModel.Dynamics.HoverSmoke` -> `Models/MoSimQuadrotorModel/Dynamics/HoverSmoke.mo` variables=9
- `MoSimQuadrotorModel.Dynamics.PhysicalWrenchHoverSmoke` -> `Models/MoSimQuadrotorModel/Dynamics/PhysicalWrenchHoverSmoke.mo` variables=7
- `MoSimQuadrotorModel.Dynamics.PhysicalWrenchYawStepSmoke` -> `Models/MoSimQuadrotorModel/Dynamics/PhysicalWrenchYawStepSmoke.mo` variables=10
- `MoSimQuadrotorModel.Dynamics.RotorEffectivenessSmoke` -> `Models/MoSimQuadrotorModel/Dynamics/RotorEffectivenessSmoke.mo` variables=6
- `MoSimQuadrotorModel.Dynamics.WrapperHoverSmoke` -> `Models/MoSimQuadrotorModel/Dynamics/WrapperHoverSmoke.mo` variables=8
- `MoSimQuadrotorModel.Dynamics.WrapperYawStepSmoke` -> `Models/MoSimQuadrotorModel/Dynamics/WrapperYawStepSmoke.mo` variables=9
- `MoSimQuadrotorModel.Dynamics.YawStepSmoke` -> `Models/MoSimQuadrotorModel/Dynamics/YawStepSmoke.mo` variables=12

## Findings

- none
