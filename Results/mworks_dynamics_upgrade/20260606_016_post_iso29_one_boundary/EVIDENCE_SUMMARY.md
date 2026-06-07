# MWORKS 016 Evidence Summary

Task: `RFLY-MOSIM-MWORKS-POST-ISO29-ONE-BOUNDARY-20260606-016`

Result: completed one narrow post-Iso29 boundary. `QuadrotorExperiments.FactoryTraceIso30ExternalBodyStateBoundarySmoke` extends Iso29 and adds only read-only external test-body state response aliases/gates. It does not add a new force path, QuadChassis, full plant, actuator flange, speedSensor, Factory trace consumption, controller tuning, or runtime transport.

## Gates

- P0 GUI pre-sentinel: clean, `error_kind=null`, `window_count=387`.
- Sysplorer MCP health: `ok=true`, `driver_ready=true`, `api_ready=true`, dedicated port `49153`.
- Targeted load: official `QuadrotorModel`, controller Sysblock dependency, and project `QuadrotorExperiments/package.mo`; no `reload_mo_path`, `ClearAll`, or `ChangeDirectory`.
- `check_model`: pass for Iso29 and Iso30.
- `simulate_model`: pass, `data=true`, 0.0 to 0.25 s, verification variable `external_body_state_boundary_gate_error@end=0.0`.
- `GetVarTimes`: 251 points, 0.0 to 0.25 s.
- P0 GUI post-sentinel: clean, `error_kind=null`, `window_count=480`.

## Sampled End State

At `t=0.25`, the external body state aliases were readable and nonzero:

- `external_body_z=-0.24021172119186007`
- `external_body_vz=-1.5165349951279292`
- `external_body_yaw_rate=-0.4531353758463619`
- `external_body_vertical_response_gate=1.7567467163197894`
- `external_body_yaw_response_gate=0.4531353758463619`
- `external_body_state_boundary_gate_error=0.0`

## Claim Boundary

This is only minimal external body state response evidence for the standalone Iso29 external MultiBody test body. It is not Factory trace consumption, QuadChassis/full plant closure, actuator flange/speedSensor closure, controller performance, plant tracking, mission success, parameter identification, planner readiness, live runtime ack, or closed loop.
