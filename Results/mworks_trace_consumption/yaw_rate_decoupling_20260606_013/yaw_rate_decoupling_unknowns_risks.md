# Yaw/Rate Decoupling 013 Unknowns And Risks

## Evidence

- `QuadrotorExperiments.FactoryTraceIso20RollPitchYawEstimatorSmoke`
  passed `check_model`.
- 0-2 s `SimulateModel` returned `data=true`.
- `GetVarTimes` returned 1001 samples from 0.0 to 2.0 s.
- `x_ref/y_ref/z_ref/yaw_ref` and yaw extraction aliases were nonzero.
- Error 6140 was absent.

## Unknowns

- Rate feedback was not tested because yaw attitude extraction passed first.
- Full Factory wrapper, full sensor bus, and rate bus remain untested.
- This probe does not validate trace tracking, controller performance, plant
  tracking, or long-horizon stability.

## Risks

- `attitude_extraction_T=0.03` is a probe bridge, not an approved controller
  or identified dynamics parameter.
- Yaw wrapping and frame conventions require a separate semantic check.
- Later rate feedback or full sensor bus reconnection may still break result
  context.

## Next Validation

- Preserve Iso20 as the passing yaw attitude extraction baseline.
- Add one narrow rate feedback isolation group next, with the same
  `check_model` -> 0-2 s `SimulateModel` -> `GetVarTimes` -> alias-probe gate.
- Do not retry full Factory wrapper until each narrow group has passed.
