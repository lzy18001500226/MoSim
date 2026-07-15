# EGO-Planner v2

Status: REFERENCE / later comparison target, not current Goal 3 hard gate.

Source: `References/Lab/planning_local/EGO-Planner-v2`.

Inputs: planner map/point cloud, state or odometry, goal, configuration profile.

Outputs: trajectory reference to Trajectory Server.

FAST-LIO dependency: same grouping rules as EGO v1; do not mix state-source
replacement claims into planner reproduction.

Control boundary: planner output must pass through Trajectory Server and
Controller Core.

Gazebo/RViz validation: single-UAV map, trajectory, tracking and metrics.

Forbidden claims: EGO v2 success is a planning-link result, not controller
optimization evidence.
