# LQR-LQG

Status: BACKLOG.

Layer: nominal linear state-feedback controller and optional estimator-coupled
controller.

Replaces: selected linearized control layer only after the state vector and
measurement model are frozen.

Inputs: state estimate, reference state, model matrices, gain matrices, optional
estimator covariance, dt, reset, enable.

Outputs: first MoSim candidate is LQR/LQI-style `ATTITUDE_THRUST`: desired
attitude quaternion, physical collective thrust, status and diagnostics. LQG
may add estimator diagnostics only after the measurement model and observer
contract are frozen.

PX4 dependency: first version should reuse PX4 attitude/rate loops.

MWORKS/codegen route: model linearization -> gain/observer design -> generated
C/C++ core -> same test harness.

Gazebo/Sunray validation: hover and small-signal trajectories before aggressive
tracking.

Current gate: LQR remains a small-signal comparison candidate; LQG remains
research/backlog until an explicit estimator contract exists.

Forbidden claims: LQG cannot be claimed without an explicit estimator contract;
PX4 EKF is not automatically the LQG observer.
