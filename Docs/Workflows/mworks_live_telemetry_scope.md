# MWORKS Live Telemetry Scope

## Purpose

This route displays telemetry from the currently running ROS1/Gazebo/PX4/
MAVROS flight in the native MWORKS result curve surface. It is a read-only
observer: it does not publish a setpoint and it does not change the active
px4ctrl controller.

```text
ROS1 odometry/reference/target/state
  -> ros1_telemetry_scope_sender.py
  -> UDP telemetry frame
  -> MoSimQuadrotorModel.LiveIntegration.RTTelemetryScope50Hz
  -> MWORKS result curve window
```

The sender also accepts an ACK from MWORKS. `roundTripMs` is a measured sender
monotonic round trip through the MWORKS receiver. It is not a one-way latency
claim. `sourceAgeMs` and `commandAgeMs` remain ROS clock-domain ages.

## Port Ownership

The first review route uses UDP port `49020` because that is the existing
Windows/WSL inbound port already accepted by the current runtime setup. The
telemetry model and the RT1 control model are mutually exclusive: do not run
`RTTelemetryScope50Hz` together with `RT1OfficialPidShadow50Hz` or another
RT1 model using the same port. A future simultaneous route must provision a
separate firewall-allowed port and update the transport contract version.

## Review Run

From WSL Ubuntu-20.04:

```bash
cd /mnt/c/Users/HP/Desktop/MoSim
RUN_ID=telemetry_scope_review_<timestamp> \
  bash Scripts/mworks_live/run_telemetry_scope_review.sh
```

The launcher starts the existing bounded single-UAV takeoff-hover-land gate,
waits for real `/uav1/mavros/local_position/odom`, and then starts the
read-only telemetry sender. In MWORKS, load/check and run:

```text
MoSimQuadrotorModel.LiveIntegration.RTTelemetryScope50Hz
simulation mode: real-time (2)
```

Open the native result curve window and select:

- `actualPosition[1..3]` and `referencePosition[1..3]`
- `actualVelocity[1..3]`
- `targetThrust`
- `positionErrorNorm` and `attitudeErrorRad`
- `sourceAgeMs`, `commandAgeMs`, and `roundTripMs`

## Evidence

For each run, the sender writes:

```text
Results/control_platform/mworks_telemetry_scope_review/<run_id>/
  telemetry_scope/TELEMETRY_SCOPE_SUMMARY.json
  telemetry_scope/telemetry_scope_trace.jsonl
  flight/flight_runtime.log
  screenshots/plot_final/
```

The summary is valid only when `run_id`, nonzero `sent_frames`, nonzero
`processedFrames` from MWORKS, and the native curve window refer to the same
run. This evidence proves live telemetry display. It does not prove MWORKS
control ownership or full bidirectional MWORKS Live closed-loop control.
