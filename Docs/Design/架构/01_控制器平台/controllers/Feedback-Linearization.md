# Feedback Linearization

Status: BACKLOG.

Layer: nonlinear model-based controller candidate. It may replace the nominal
outer-loop force/attitude generation when the plant model and singularity
guards are frozen.

Replaces: controller core force and attitude generation, not PX4 mode,
arming, EKF or MAVROS wrapper logic.

Inputs: position, velocity, attitude, angular velocity if required, trajectory
reference, mass/inertia/gravity/model parameters, dt, reset and enable.

Outputs: first candidate uses `ATTITUDE_THRUST`: desired attitude quaternion,
physical collective thrust, status and diagnostics.

PX4 dependency: first version reuses PX4 attitude/rate loops.

MWORKS/codegen route: equation-form model -> singularity/saturation guards ->
Sysblock/C++ core -> offline tests -> Gazebo A/B.

Current gate: backlog until model assumptions and envelope limits are explicit.

Forbidden claims: cancellation-based tracking cannot be claimed robust without
model-error and disturbance tests.
