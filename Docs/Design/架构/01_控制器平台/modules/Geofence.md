# Geofence

Status: DESIGNED / mandatory safety boundary.

Layer: safety boundary and experiment lifecycle gate.

Replaces: no controller. It rejects or modifies commands/references that would
leave the configured flight volume.

Inputs: state, predicted short-horizon state where available, geofence profile,
candidate reference or command, mode, dt and validity flags.

Outputs: pass, reject, clipped reference, fallback request, emergency stop or
land request.

PX4 dependency: complements PX4 geofence/failsafe settings; MoSim must still
record its own experiment geofence profile for evidence and replay.

MWORKS/codegen route: deterministic boundary check -> generated or C++ safety
module -> timeout and boundary tests.

Current gate: should exist before aggressive trajectory, planner and swarm
experiments are accepted.

Forbidden claims: geofence-triggered fallback is a safety success, not proof
that the nominal controller or planner was valid.
