# MoSimQuadrotorModel Formal Smoke Target Matrix

Request: `PMO-MWORKS-R1-MOSIMQUAD-FORMAL-SMOKE-SURFACE-STATIC-PREP-20260608-023`

Static-only artifact. It prepares future live MWORKS check/smoke work and does not claim live load, check_model, SimulateModel, or result evidence.

| Order | Formal target | Implementation file | Role | Future simulate order |
| --- | --- | --- | --- | --- |
| 1 | `MoSimQuadrotorModel.Dynamics.RotorActuatorCore` | `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150RflyStyleRotorDynamics.mo` | core_dynamics_check | check only |
| 2 | `MoSimQuadrotorModel.Dynamics.ActuatorCommandMapper` | `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150ActuatorCommandMapper.mo` | normalized_command_mapper_check | check only |
| 3 | `MoSimQuadrotorModel.Dynamics.WrapperSurface` | `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150DynamicsWrapperSurface.mo` | wrapper_force_moment_surface_check | check only |
| 4 | `MoSimQuadrotorModel.Dynamics.ActuatorMappedWrapperSurface` | `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150ActuatorMappedWrapperSurface.mo` | mapper_to_wrapper_surface_check | check only |
| 5 | `MoSimQuadrotorModel.Dynamics.OptionalDampingGyroLayer` | `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150OptionalDampingGyroLayer.mo` | default_disabled_optional_layer_check | check only |
| 6 | `MoSimQuadrotorModel.Dynamics.PhysicalWrenchAdapter` | `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150PhysicalWrenchFrameAdapter.mo` | physical_wrench_boundary_check | check only |
| 7 | `MoSimQuadrotorModel.Dynamics.HoverSmoke` | `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150DynamicsUpgradeHoverSmoke.mo` | core_hover_smoke | 1 |
| 8 | `MoSimQuadrotorModel.Dynamics.YawStepSmoke` | `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150DynamicsUpgradeYawStepSmoke.mo` | core_yaw_step_smoke | 2 |
| 9 | `MoSimQuadrotorModel.Dynamics.WrapperHoverSmoke` | `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150DynamicsWrapperHoverSmoke.mo` | wrapper_hover_smoke | 3 |
| 10 | `MoSimQuadrotorModel.Dynamics.WrapperYawStepSmoke` | `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150DynamicsWrapperYawStepSmoke.mo` | wrapper_yaw_step_smoke | 4 |
| 11 | `MoSimQuadrotorModel.Dynamics.PhysicalWrenchHoverSmoke` | `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150PhysicalWrenchHoverSmoke.mo` | physical_wrench_hover_smoke | 5 |
| 12 | `MoSimQuadrotorModel.Dynamics.PhysicalWrenchYawStepSmoke` | `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150PhysicalWrenchYawStepSmoke.mo` | physical_wrench_yaw_step_smoke | 6 |

## Parameter Provenance Target

- `MoSimQuadrotorModel.Parameters.Sunray150ParameterProvenance` is phase 0 for future `check_model` and remains provenance-only.
- DAE/Blender rotor centers are geometry assembly evidence only.
- Mass, inertia, Ct, Cm, motor lag, drag, damping, gyro, and command mapping values remain source-labeled seeds, not identified Sunray150 truth.
