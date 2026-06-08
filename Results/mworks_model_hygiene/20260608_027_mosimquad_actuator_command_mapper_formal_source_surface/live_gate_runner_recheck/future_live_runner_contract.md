# Static Live Gate Runner Contract

Request: `PMO-MWORKS-R1-MOSIMQUAD-LIVE-GATE-RUNNER-STATIC-HARDENING-20260608-024`

## Static Rejection Rules

- Reject if any target in future_live_validation_surface is absent from formal_smoke_target_matrix.
- Reject if expected_result_variables target lists drift from formal_smoke_target_matrix.
- Reject if MoSimQuadrotorModel.Dynamics/package.mo or package.order no longer exposes the formal target.
- Reject if QuadrotorExperiments.DynamicsUpgrade alias or implementation source anchors are missing.
- Reject if the future SimulateModel queue contains a non-smoke/check-only target.

## Claim Boundary

- 024 may claim only static live-gate runner/checker hardening.
- 024 does not claim live MWORKS load, `check_model`, `SimulateModel`, native result, `.msr`, graphical/layout acceptance, controller performance, planner readiness, runtime ack, identified parameter truth, mission success, or closed loop.
- Future live work must preserve the 023 target order and stop on missing or renamed targets.
