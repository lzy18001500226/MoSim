# Tube MPC

Status: RESEARCH.

Layer: robust MPC research candidate using nominal trajectory plus invariant
tube/error feedback.

Replaces: no current flight loop. It may become a robust MPC variant after
constraint sets, disturbance bounds and terminal sets are defined.

Inputs: nominal state, error state, disturbance bounds, tube feedback gain,
constraints, reference and solver state.

Outputs: nominal control plus bounded correction; first release would still
need mapping to `ATTITUDE_THRUST` or reference shaping.

PX4 dependency: not released yet.

MWORKS/codegen route: research specification -> invariant set computation ->
real-time feasibility -> offline/Gazebo gates.

Current gate: research only.

Forbidden claims: tube feasibility on paper does not prove controller timing or
tracking quality in Gazebo.
