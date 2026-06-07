# Rate Feedback Isolation 014 Unknowns And Risks

## Evidence

- `QuadrotorExperiments.FactoryTraceIso21ControllerRateAliasSmoke` passed
  `check_model`.
- 0-2 s `SimulateModel` returned `data=true`.
- `GetVarTimes` returned 1001 samples from 0.0 to 2.0 s.
- `x_ref/y_ref/z_ref/yaw_ref`, project-owned rate aliases, and controller
  internal rate aliases were nonzero.
- Error 6140 was absent.

## Unknowns

- The current controller surface has no external `roll_rate`, `pitch_rate`, or
  `yaw_rate` inports, so no true external gyro/rate signal was wired.
- Full sensor bus and full Factory wrapper remain untested.
- The large extraction-derived rate values are not interpreted as physical-rate
  validation or controller performance.

## Risks

- The extraction derivative can create large transient rates and needs design
  review before becoming a formal sensor interface.
- Controller internal rate estimates are derived from attitude filtering, not a
  real gyro model.
- A future controller with explicit rate inports or a full sensor bus may still
  reveal result-context or semantic failures.

## Next Validation

- Decide whether the next step is a controller interface revision with explicit
  rate inports or a narrow full-sensor-bus/component reconnect.
- Preserve Iso21 as the passing rate-alias baseline.
- Continue using `check_model` -> 0-2 s `SimulateModel` -> `GetVarTimes` ->
  alias probes before any full Factory retry.
