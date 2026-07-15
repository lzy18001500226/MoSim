# Tube MPC

Status: DROPPED FROM CURRENT WAVE / research reference only.

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

Current gate: the selected MIT source at commit
`45cf558366d55cd6d603f151afce2e1982ba8290` requires CasADi/IPOPT, MPT3 and
YALMIP. Its online optimizer, invariant-set computation and simulation are
coupled, and the local MATLAB R2025b environment has none of the required
entry points. It therefore fails the current fixed-size deterministic-core and
controlled-dependency gates.

The source remains useful for disturbance-bound experiments, tube equations
and LQR comparison design. Reopening requires an approved solver/distribution
policy, an isolated deterministic solver boundary, a worst-case timing gate
and a typed command mapping. Audit evidence:
`Results/control_platform/g5_wave_b_tube_mpc_audit_20260716/G5_WAVE_B_TUBE_MPC_AUDIT.json`.

Forbidden claims: tube feasibility on paper does not prove controller timing or
tracking quality in Gazebo.
