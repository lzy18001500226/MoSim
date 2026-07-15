# Robust MPC

Status: BACKLOG.

Layer: optimization-based controller candidate for bounded uncertainty and
disturbance profiles.

Replaces: nominal outer-loop or full `ATTITUDE_THRUST` controller core only
after model, constraints and solver timing are frozen.

Inputs: state estimate, trajectory reference, model, uncertainty/disturbance
bounds, constraints, warm start, dt, reset and enable.

Outputs: first practical output should be `ATTITUDE_THRUST` or a reference
correction passed through the same adapter and SafetySupervisor.

PX4 dependency: first version reuses PX4 attitude/rate loops.

MWORKS/codegen route: fixed-horizon formulation -> solver/codegen feasibility
check -> deadline test -> offline and Gazebo A/B.

Current gate: backlog; not released before baseline NMPC/LMPC timing evidence.

Forbidden claims: robust MPC must not be claimed if uncertainty sets and
constraint violation metrics are absent.
