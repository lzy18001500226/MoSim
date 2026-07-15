# EGO-Swarm

Status: REFERENCE / later multi-UAV comparison target, not current Goal 3 hard gate.

Source: `References/Lab/swarm_coordination/ego-planner-swarm`.

Inputs: per-UAV state, map/point cloud, goals, neighbor trajectories and namespace
configuration.

Outputs: per-UAV trajectory references through Planner Adapter and Trajectory
Server.

FAST-LIO dependency: if reopened, the engineering baseline may use the accepted
state-source baseline; FAST-LIO replacement must be marked as a separate group.

Control boundary: each UAV still uses its own controller instance and MAVROS/PX4
instance. Swarm planner does not own final control publication.

Gazebo/RViz validation if reopened: 2-UAV and 3-UAV startup, namespace
isolation, trajectory topic isolation, no collision, logs and metrics per UAV.

Forbidden claims: EGO-Swarm official engineering baseline is not MoSim
self-developed formation control.
