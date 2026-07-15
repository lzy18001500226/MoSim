# INDI

Status: BLOCKED for current first-stage `ATTITUDE_THRUST` translational
augmentation; BACKLOG for later inner-loop/body-rate/torque-level INDI.

Layer: augmentation or inner-loop enhancement, not a normal outer-loop
controller replacement.

Inputs: measured acceleration or angular acceleration where available, angular
velocity, control increment history, actuator effectiveness, dt.

Outputs: incremental correction to body-rate, attitude, acceleration or thrust
command depending on the released interface.

PX4 dependency: first-stage `ATTITUDE_THRUST` can only expose attitude and
collective thrust. Runtime G10-C evidence shows that adding acceleration
residual INDI as a translational correction on this path is not accepted.
True INDI should be reopened only as a later body-rate, torque, or actuator
effectiveness task with explicit timing and feedback signals.

MWORKS/codegen route: define signal point -> implement bounded correction ->
offline tests -> Gazebo A/B with host controller.

Gazebo/Sunray validation: current G10-C `dfbc_smooth_robust_indi` runtime
variants failed takeoff-hover-land while the G9.6 base controller passed.
Evidence packet:
`Results/sunray_ros1/g10c_indi_blocker_review_20260630_141530/SUMMARY.md`.

Forbidden claims: INDI must not be listed as an accepted standalone controller
or accepted G10 augmentation without declaring which loop it replaces. The
current `ATTITUDE_THRUST` translational G10-C implementation is audit/research
only and must not enter active batches unless explicitly reopened.
