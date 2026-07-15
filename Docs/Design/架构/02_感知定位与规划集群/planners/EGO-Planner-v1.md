# EGO-Planner v1

Status: REFERENCE / later comparison target, not current Goal 3 hard gate.

Source: `References/Lab/planning_local/ego-planner`.

Inputs: point cloud or local map, odometry/state, goal, dynamic limits.

Outputs: time-parameterized trajectory or B-spline reference through Planner
Adapter and Trajectory Server.

FAST-LIO dependency: can run on current baseline state for engineering smoke;
FAST-LIO state-source replacement is a separate experiment group.

Control boundary: must not publish final MAVROS control commands.

Gazebo/RViz validation: point cloud/map visible, trajectory produced, controller
tracks trajectory, no topic interruption, metrics recorded.

Forbidden claims: EGO reproduction is not self-developed formation control and
does not prove FAST-LIO closed-loop state replacement by itself.
