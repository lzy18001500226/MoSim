# CBF

Status: BACKLOG / safety module candidate.

Layer: safety and constraint filter. CBF is not a nominal tracking controller.

Replaces: no controller core. It modifies, rejects or constrains reference or
candidate commands through `safety_profile`.

Inputs: current state, candidate command or reference, obstacle/formation
constraints, geofence, control limits, relative state if multi-UAV, dt and
validity flags.

Outputs: filtered command, filtered reference, reject/fallback request and
diagnostics.

PX4 dependency: complements PX4 failsafe; does not replace arming/offboard or
PX4 failsafe logic.

MWORKS/codegen route: scalar/low-dimensional constraint examples first ->
bounded QP or analytical filter -> offline constraint tests -> Gazebo safety
scenarios.

Current gate: after baseline controller and basic Safety-Filter gates.

Forbidden claims: CBF success must report how much the nominal controller or
planner violated constraints before filtering.
