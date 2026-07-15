# Reference Governor

Status: BACKLOG.

Layer: pre-controller reference safety module.

Replaces: no controller. It shapes or delays references before Trajectory
Server or Controller Core when constraints would otherwise be violated.

Inputs: requested reference, current state, plant/controller envelope,
constraints, safety margin, dt, reset and enable.

Outputs: admissible reference, hold command, fallback request and diagnostics.

PX4 dependency: independent of PX4 inner loops; final commands still pass
through controller, SafetySupervisor and Adapter.

MWORKS/codegen route: reference envelope model -> admissibility check ->
generated C/C++ shaper -> offline trajectory continuity and Gazebo tests.

Current gate: backlog after basic trajectory continuity and Safety-Filter
interfaces are stable.

Forbidden claims: slowing or clipping a reference is not controller improvement
unless reported separately from nominal controller tracking performance.
