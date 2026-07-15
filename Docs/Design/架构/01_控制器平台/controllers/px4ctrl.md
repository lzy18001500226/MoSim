# px4ctrl

Status: DESIGNED / baseline in current Sunray lane.

Layer: nominal outer-loop controller.

Replaces: PX4 position/velocity outer loop only.

Inputs: position, velocity, attitude, angular velocity, reference position,
reference velocity, reference acceleration, yaw, mass, gravity, dt, reset, enable.

Outputs: `ATTITUDE_THRUST`, specifically desired attitude quaternion and physical
collective thrust in N.

PX4 dependency: reuses PX4 attitude loop, rate loop and control allocation.

MWORKS/codegen route: upstream/Sunray lineage audit -> extract `px4ctrl_core` ->
offline equivalence -> MWORKS model -> generated C/C++ -> IController wrapper.

Gazebo/Sunray validation: takeoff, hover, land, step, figure-8, spiral,
Diff-Planner single-UAV and Diff-Planner swarm after the engineering loop is stable.
EGO/EGO-Swarm are reference comparison routes.

Current gate: must remain the first system baseline and fallback for later
controllers.

Forbidden claims: do not claim MWORKS generated px4ctrl is complete until
offline equivalence and Gazebo A/B reinjection both pass.
