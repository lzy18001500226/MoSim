# Distributed MPC

Status: RESEARCH / swarm candidate.

Layer: multi-UAV planning/control optimization candidate for formation,
collision avoidance or cooperative tracking.

Replaces: no first-stage single-UAV controller. It belongs to the swarm/control
coordination layer, not the low-level px4ctrl core.

Inputs: own state, neighbor states or predictions, formation objective,
collision constraints, communication delay/loss profile, solver state and dt.

Outputs: per-UAV trajectory/reference updates or constrained control references
that still pass through each UAV's local Trajectory Server and Controller Core.

PX4 dependency: each UAV still uses its own PX4/MAVROS/adapter instance.

MWORKS/codegen route: swarm MIL study first, then bounded coordinator or
reference generator. Low-level control remains separately verified.

Current gate: research until Diff-Planner swarm三机工程基线和local controller
templates are accepted.

Forbidden claims: distributed MPC cannot be counted as EGO-Swarm reproduction or
as low-level attitude controller evidence.
