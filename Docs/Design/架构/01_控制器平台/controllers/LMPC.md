# LMPC

Status: BACKLOG / existing model candidates need audit.

Layer: nominal optimal controller.

Replaces: outer-loop controller or trajectory tracking optimization layer.

Inputs: state vector, reference horizon, linear model, constraints, weights,
solver status, dt, reset, enable.

Outputs: target first-stage output should be `ATTITUDE_THRUST` or acceleration
reference converted by the standard Adapter; other outputs need release gates.

PX4 dependency: first version should reuse PX4 inner loops.

MWORKS/codegen route: audit existing `linear_mpc_sysblock` entries -> freeze ABI
-> generated C/C++ or solver wrapper -> offline and Gazebo tests.

Gazebo/Sunray validation: step, figure-8, spiral, constraint/saturation metrics.

Current gate: second-batch optimization controller.

Forbidden claims: an existing model directory is not evidence of closed-loop
acceptance without metrics and run packets.
