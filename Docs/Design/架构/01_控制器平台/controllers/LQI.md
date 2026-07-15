# LQI

Status: BACKLOG / DESIGNED interface placeholder.

Layer: nominal outer-loop or linearized state-feedback controller.

Replaces: position/velocity outer-loop controller only after the operating point,
state vector and integral states are frozen.

Inputs: state vector, integral error state, reference state, model parameters,
linearization profile, dt, reset, enable.

Outputs: first-stage target should be `ATTITUDE_THRUST`; lower-level outputs
require a separate adapter decision.

PX4 dependency: first version should reuse PX4 attitude loop, rate loop and
control allocation.

MWORKS/codegen route: linearized model -> LQI gain design -> MWORKS/Sysblock ->
generated C/C++ -> offline and Gazebo validation.

Gazebo/Sunray validation: hover, step, figure-8 and disturbance/steady-state
error tests.

Current gate: blocked behind px4ctrl/PID/SE3 template validation.

Forbidden claims: do not present LQI as accepted until its linearization profile,
integral reset and saturation behavior are measured.
