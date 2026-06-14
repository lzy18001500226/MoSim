# MoSimQuadrotorModel Live Gate Runner Plan

Request: `PMO-MWORKS-R1-MOSIMQUAD-LIVE-GATE-RUNNER-STATIC-HARDENING-20260608-024`

Static-only contract. This artifact does not call or prove MWORKS load, `check_model`, `SimulateModel`, result variables, graphical acceptance, controller performance, runtime ack, or closed loop.

## Future Load

- 1. `model_manager.load_file` `Models/MoSimQuadrotorModel/package.mo` force_reload=True
- 2. `dependency_package_available` `Models/QuadrotorExperiments/package.mo` force_reload=False

## Future Check Model Order

- 1. `MoSimQuadrotorModel.Parameters.Sunray150ParameterProvenance` (parameter_provenance_record)
- 2. `MoSimQuadrotorModel.Dynamics.RotorActuatorCore` (formal_dynamics_alias)
- 3. `MoSimQuadrotorModel.Dynamics.ActuatorCommandMapper` (formal_dynamics_alias)
- 4. `MoSimQuadrotorModel.Dynamics.RotorEffectivenessSmoke` (formal_dynamics_alias)
- 5. `MoSimQuadrotorModel.Dynamics.WrapperSurface` (formal_dynamics_alias)
- 6. `MoSimQuadrotorModel.Dynamics.ActuatorMappedWrapperSurface` (formal_dynamics_alias)
- 7. `MoSimQuadrotorModel.Dynamics.OptionalDampingGyroLayer` (formal_dynamics_alias)
- 8. `MoSimQuadrotorModel.Dynamics.PhysicalWrenchAdapter` (formal_dynamics_alias)
- 9. `MoSimQuadrotorModel.Dynamics.HoverSmoke` (formal_dynamics_alias)
- 10. `MoSimQuadrotorModel.Dynamics.YawStepSmoke` (formal_dynamics_alias)
- 11. `MoSimQuadrotorModel.Dynamics.WrapperHoverSmoke` (formal_dynamics_alias)
- 12. `MoSimQuadrotorModel.Dynamics.WrapperYawStepSmoke` (formal_dynamics_alias)
- 13. `MoSimQuadrotorModel.Dynamics.PhysicalWrenchHoverSmoke` (formal_dynamics_alias)
- 14. `MoSimQuadrotorModel.Dynamics.PhysicalWrenchYawStepSmoke` (formal_dynamics_alias)

## Future Simulate Model Order

- 1. `MoSimQuadrotorModel.Dynamics.HoverSmoke` after all checks pass; probe 5 variables
- 2. `MoSimQuadrotorModel.Dynamics.YawStepSmoke` after all checks pass; probe 6 variables
- 3. `MoSimQuadrotorModel.Dynamics.RotorEffectivenessSmoke` after all checks pass; probe 6 variables
- 4. `MoSimQuadrotorModel.Dynamics.WrapperHoverSmoke` after all checks pass; probe 8 variables
- 5. `MoSimQuadrotorModel.Dynamics.WrapperYawStepSmoke` after all checks pass; probe 8 variables
- 6. `MoSimQuadrotorModel.Dynamics.PhysicalWrenchHoverSmoke` after all checks pass; probe 9 variables
- 7. `MoSimQuadrotorModel.Dynamics.PhysicalWrenchYawStepSmoke` after all checks pass; probe 9 variables

## Stop Conditions

- target resolution status is not passed_static
- license/login/authorization/GUI/preflight state is blocking or unknown in a future live task
- any check_model target fails
- any simulate target fails
- any expected result variable is absent from the future native result/.msr output
- a future repair would change dynamics behavior or tune parameters
