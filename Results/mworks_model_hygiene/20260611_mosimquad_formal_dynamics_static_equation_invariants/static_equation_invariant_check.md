# Formal Dynamics Static Equation Invariants

Status: `passed`

Static-only source-anchor check for future live smoke variables.

## Anchor Groups

- `rotor_core` -> `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150RflyStyleRotorDynamics.mo` anchors=12
- `wrapper_surface` -> `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150DynamicsWrapperSurface.mo` anchors=11
- `physical_wrench_adapter` -> `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150PhysicalWrenchFrameAdapter.mo` anchors=10
- `rotor_effectiveness_smoke` -> `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150RotorEffectivenessSmoke.mo` anchors=6

## Model Sources

- `MoSimQuadrotorModel.Dynamics.HoverSmoke` -> `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150DynamicsUpgradeHoverSmoke.mo` variables=5
- `MoSimQuadrotorModel.Dynamics.PhysicalWrenchHoverSmoke` -> `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150PhysicalWrenchHoverSmoke.mo` variables=9
- `MoSimQuadrotorModel.Dynamics.PhysicalWrenchYawStepSmoke` -> `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150PhysicalWrenchYawStepSmoke.mo` variables=9
- `MoSimQuadrotorModel.Dynamics.RotorEffectivenessSmoke` -> `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150RotorEffectivenessSmoke.mo` variables=6
- `MoSimQuadrotorModel.Dynamics.WrapperHoverSmoke` -> `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150DynamicsWrapperHoverSmoke.mo` variables=8
- `MoSimQuadrotorModel.Dynamics.WrapperYawStepSmoke` -> `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150DynamicsWrapperYawStepSmoke.mo` variables=8
- `MoSimQuadrotorModel.Dynamics.YawStepSmoke` -> `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150DynamicsUpgradeYawStepSmoke.mo` variables=6

## Findings

- none
