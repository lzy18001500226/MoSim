# SO3 Attitude

Status: BACKLOG.

Layer: geometric attitude or attitude-rate controller on SO(3). It is a lower
control-layer candidate than the first-stage SE3 outer-loop template.

Replaces: PX4 attitude/rate inner-loop only after a lower-level interface is
explicitly released. It does not replace trajectory generation or position
control by itself.

Inputs: attitude, angular velocity, desired attitude or attitude trajectory,
inertia, gains, torque/thrust limits, dt, reset and enable.

Outputs: future candidate may output `BODY_RATE_THRUST`, torque/wrench or a
PX4-native module command. It is not released in the first-stage
`ATTITUDE_THRUST` route.

PX4 dependency: first-stage MoSim keeps PX4 attitude/rate loops; SO(3) attitude
control is therefore a later comparison candidate.

MWORKS/codegen route: attitude-only MIL/SIL -> generated C/C++ core -> lower
interface gate -> Gazebo A/B against PX4 inner-loop baseline.

Current gate: backlog until BODY_RATE or PX4-module route is opened.

Forbidden claims: SO(3) attitude control cannot be claimed from SE3 outer-loop
tracking unless the inner-loop implementation and output layer are explicit.
