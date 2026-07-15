# Adaptive MPC

Status: BACKLOG / research candidate.

Layer: MPC variant with online model, weight or constraint adaptation.

Replaces: no current first-stage controller. It can extend LMPC/NMPC after the
nominal MPC template and adaptation safeguards are accepted.

Inputs: state estimate, trajectory reference, model parameters, adaptation law
or estimator output, constraints, solver status, dt, reset and enable.

Outputs: same as selected base MPC profile, preferably `ATTITUDE_THRUST` in the
first implementation route.

PX4 dependency: first version reuses PX4 attitude/rate loops.

MWORKS/codegen route: nominal MPC first -> adaptation module -> bounded update
guards -> deadline and stability checks.

Current gate: blocked on nominal MPC template and parameter identification
profile.

Forbidden claims: online adaptation cannot silently change safety-critical
limits without logging and rollback.
