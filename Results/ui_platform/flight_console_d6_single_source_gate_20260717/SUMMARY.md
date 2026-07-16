# Flight Console D6 Single-UAV Source Gate

Status: `source_ready_live_gate_pending`

The first D6 generated-C route is now explicit and allowlisted. The new
`cascade_pid_figure8_generated_c_v1` ExperimentProfile selects the accepted
MWORKS-generated cascade PID ATTITUDE_THRUST backend and maps through the
Orchestrator to `cascade_pid_figure8_single`. The operation reuses the real
Sunray/PX4/MAVROS/px4ctrl figure-eight runner; it is not an offline substitute.

The project Profile Validator passes, the shell wrapper parses, and 20 targeted
Flight Console, Orchestrator, service, client, and runtime-backend tests pass.
This remains a source gate. Native Flight Console build and same-run Gazebo,
injection, telemetry, metrics, evidence, and model-context return are pending.
