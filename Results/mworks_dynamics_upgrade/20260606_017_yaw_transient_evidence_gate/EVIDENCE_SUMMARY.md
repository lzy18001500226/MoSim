# MWORKS 017 Yaw Transient Evidence Gate

Source: `MWORKS_MCP`.

This task checked existing project-owned models only. It did not edit
`Models/QuadrotorExperiments`, did not edit the official
`References/MWORKS/QuadrotorModel/package.mo`, did not run a full Factory
wrapper, and did not close or restart MWORKS/Sysplorer.

## Gates

- GUI sentinel before MCP: clean.
- Sysplorer MCP health: ok, driver/API ready, dedicated port 49152.
- Targeted `model_manager(load_file, force_reload=true)` for baseline,
  controller dependency, and `QuadrotorExperiments`: ok.
- `check_model` passed for:
  - `QuadrotorExperiments.Sunray150DynamicsWrapperYawStepSmoke`
  - `QuadrotorExperiments.Sunray150PhysicalWrenchYawStepSmoke`
  - `QuadrotorExperiments.FactoryTraceIso30ExternalBodyStateBoundarySmoke`
- 0-0.25 s smoke simulations returned `data=true`, with `GetVarTimes=251`.
- GUI sentinel after MCP: clean.

## Observability Result

| Evidence class | Result |
|---|---|
| Command-side yaw moment | Observable: `wrapper.commanded_yaw_moment_gate@end = 0.061549775999999945 N.m`. |
| Lagged wrapper yaw moment | Observable: `wrapper.yaw_moment_gate@end = 0.06153801695664962 N.m`. |
| Applied physical-wrench yaw torque | Observable: `adapter.applied_yaw_torque_body@end = 0.061540561756854906 N.m`, matching `adapter.wrapper_yaw_moment`. |
| External body yaw-rate response | Observable: `external_body_yaw_rate@end = -0.4531353758463619 rad/s`, with `external_body_yaw_response_gate@end = 0.4531353758463619`. |

## Boundary

The wrapper yaw-step smoke and the Iso30 sidecar bridge use different command
domains, so the positive wrapper yaw-step sign and negative Iso30 sidecar
torque/yaw-rate sign are not classified as a failure here. This is yaw
transient observability evidence only, not full-plant yaw transient acceptance,
Factory trace consumption, controller performance, parameter identification,
planner readiness, live runtime acknowledgement, mission success, or
`closed_loop`.
