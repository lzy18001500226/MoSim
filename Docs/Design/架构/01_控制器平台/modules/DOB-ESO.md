# DOB-ESO

Status: G10-A static/profile gate passed; runtime A/B pending.

Layer: disturbance observer / extended state observer augmentation.

Inputs: state, control command, model estimate, observer gains, measurement
quality and dt.

Outputs: disturbance estimate or compensation term.

PX4 dependency: depends on host controller; first release should not replace
PX4 estimator or inner-loop control.

MWORKS/codegen route: observer design -> stability and saturation checks ->
generated C/C++ -> A/B tests.

Gazebo/Sunray validation: wind, load, drag and model-mismatch tests.

Current implementation note, 2026-06-30: the first G10-A route reuses the
G9.6 `dfbc_smooth_robust` low-frequency acceleration-residual disturbance
observer as a bounded DOB/ESO candidate. The static gate is recorded at
`Results/g10/dfbc_dob_eso_v1/g10a_static_gate_20260630_143601/RUN_MANIFEST.json`.
It proves ablation wiring, compensation limiting, and repeated-stamp
protection only. Runtime acceptance still requires paired Gazebo A/B evidence
against `dfbc_dob_eso_disabled_v1`.

Forbidden claims: DOB/ESO is not a state-source replacement for PX4 EKF or
FAST-LIO.
