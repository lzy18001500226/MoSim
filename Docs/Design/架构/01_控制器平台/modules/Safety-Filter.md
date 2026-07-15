# Safety Filter

Status: DESIGNED / mandatory system layer.

Layer: safety and constraint layer after controller output and before Adapter.

Inputs: candidate control command, state validity, reference validity, limits,
geofence, obstacle/formation constraints where available.

Outputs: pass, reject, clipped command, safe reference or fallback request.

PX4 dependency: complements PX4 failsafe; it does not replace PX4 failsafe.

MWORKS/codegen route: basic limiter first; CBF/Reference Governor later as
separate profiles.

Gazebo/Sunray validation: timeout, saturation, geofence and emergency-stop
cases before complex CBF demos.

Forbidden claims: safety-filtered success must still report whether the nominal
controller violated constraints.

Current reopen gate: start with one explicit constraint class, such as thrust,
tilt, acceleration, geofence, obstacle distance, command timeout, or emergency
stop. Run the same controller/profile with the filter disabled and enabled,
then record accepted, clipped, rejected, and fallback counts plus whether the
nominal controller violated the constraint. Passing this gate means the filter
behavior is observable and auditable; it does not prove controller performance
improvement or replace PX4 failsafe.
