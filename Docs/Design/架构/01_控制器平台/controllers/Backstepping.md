# Backstepping

Status: BACKLOG.

Layer: nominal nonlinear controller.

Replaces: outer-loop or cascaded nonlinear tracking layer depending on the
chosen model.

Inputs: state, reference and model parameters required by the recursive design;
adaptive variants also need estimator states and reset semantics.

Outputs: first candidate should target `ATTITUDE_THRUST`; deeper variants need
explicit body-rate/wrench release.

PX4 dependency: first version should reuse PX4 inner loops.

MWORKS/codegen route: derive stable state set -> implement in MWORKS -> generate
C/C++ -> offline and Gazebo tests.

Gazebo/Sunray validation: hover, step and robustness before aggressive paths.

Current gate: backlog after SE3/SMC/LMPC/NMPC representative routes are clearer.

Forbidden claims: adaptive or neural Backstepping must be separated from the
base Backstepping profile.
