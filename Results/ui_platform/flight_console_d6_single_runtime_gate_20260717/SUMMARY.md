# Flight Console D6 single-runtime gate

Status: `blocked_shared_runtime_busy`.

The bounded D6 attempt prepared and started Orchestrator run
`run-20260717-055004-819a3654` with
`cascade_pid_figure8_generated_c_v1`. The runtime wrapper exited with code 11
before Gazebo/PX4 startup because P8 run
`p8_formation_mode1_gazebo_r5_20260717` owned the project Sunray ROS1 runtime
lock.

This result proves the shared-runtime lock rejected a competing launch. It does
not validate or reject controller tracking, physical injection, telemetry,
RViz, UE, or the D6 closed loop.

Evidence remains in:

- `Results/ui_platform/orchestrator_runs/run-20260717-055004-819a3654/`
- `Results/ui_platform/orchestrator_runs/run-20260717-055004-819a3654/runtime.stderr.log`
- `Results/ui_platform/orchestrator_runs/run-20260717-055004-819a3654/RESULT_PACKET.json`

Next gate: wait for the P8 owner to release the runtime lock, then create a new
D6 run and require `running`, fresh telemetry, successful wind and motor
effectiveness ACKs, restore ACKs, completed flight evidence, and cleanup.
