# Package / Order Integrity

Task: `PMO-MWORKS-R1-MOSIMQUAD-DYNAMICS-DEFAULT-INTEGRITY-STATIC-GATE-20260608-020`

## MoSimQuadrotorModel Top Level

`Models/MoSimQuadrotorModel/package.order` contains the current package
sequence:

`Baseline`, `Dynamics`, `Parameters`, `Missions`, `Controllers`, `Robustness`,
`Planning`, `SceneTrace`, `System`, `Formation`, `Support`,
`LegacyCompatibility`.

All corresponding child package directories are present under
`Models/MoSimQuadrotorModel/`.

## Formal Dynamics Package

`Models/MoSimQuadrotorModel/Dynamics/package.mo` defines 12 model entries, and
`Models/MoSimQuadrotorModel/Dynamics/package.order` lists exactly the same 12
entries in the same order:

`RotorActuatorCore`, `HoverSmoke`, `YawStepSmoke`, `WrapperSurface`,
`ActuatorCommandMapper`, `ActuatorMappedWrapperSurface`,
`OptionalDampingGyroLayer`, `WrapperHoverSmoke`, `WrapperYawStepSmoke`,
`PhysicalWrenchAdapter`, `PhysicalWrenchHoverSmoke`,
`PhysicalWrenchYawStepSmoke`.

## Compatibility Dynamics Package

`Models/QuadrotorExperiments/DynamicsUpgrade/package.mo` defines 12 visible
compatibility aliases, and
`Models/QuadrotorExperiments/DynamicsUpgrade/package.order` lists exactly the
same 12 entries in the same order:

`RotorDynamicsCore`, `RotorHoverSmoke`, `RotorYawStepSmoke`, `WrapperSurface`,
`ActuatorCommandMapper`, `ActuatorMappedWrapperSurface`,
`OptionalDampingGyroLayer`, `WrapperHoverSmoke`, `WrapperYawStepSmoke`,
`PhysicalWrenchAdapter`, `PhysicalWrenchHoverSmoke`,
`PhysicalWrenchYawStepSmoke`.

## Parameters Package

`Models/MoSimQuadrotorModel/Parameters/package.mo` defines record
`Sunray150ParameterProvenance`, and
`Models/MoSimQuadrotorModel/Parameters/package.order` contains exactly
`Sunray150ParameterProvenance`.

## Static Decision

No `package.mo` or `package.order` source repair was required for 020. Live
`check_model` remains unproven by this static gate.
