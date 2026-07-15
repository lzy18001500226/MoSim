# Fast Multi-Robot Exploration

Status: REFERENCE / unknown-environment multi-robot exploration candidate.

Source: `References/Lab/exploration_coverage/fast_multi_robot_exploration`.

Inputs: per-robot state, local map or point cloud, frontier/exploration map,
communication/shared exploration data, launch and namespace configuration.

Outputs: exploration goals, coverage decisions, path or trajectory references
for each robot.

FAST-LIO dependency: profile-dependent. If used with MoSim Sunray, FAST-LIO
or another declared state/map source must be recorded per UAV and must not be
mixed silently with Gazebo truth.

Control boundary: this reference may select exploration targets or routes, but
does not publish final control commands. MoSim execution still goes through
Planner Adapter, Trajectory Server, controller, MAVROS/PX4 and Gazebo.

MoSim use: candidate for the "unknown map -> explored/frozen map -> task
execution" story. It is useful because it is closer to multi-UAV exploration
than single-UAV SLAM demos, but it must be adapted to the current ROS1/Sunray
namespace, sensor, map and logging contracts.

Gazebo/RViz validation if opened: begin with a small bounded unknown map and
two UAVs, then compare against FUEL/RACER. Evidence must include explored
volume/area, frontier or task allocation logs, per-UAV trajectory, no-collision
status, map snapshots, and RViz screenshots or replay.

Forbidden claims: a source review or demo launch is not MoSim autonomous
exploration success. It does not replace MWORKS controller/codegen evidence
and cannot use fake maps, static point clouds, or UE global truth as planner
input unless the experiment is explicitly marked as oracle/debug-only.
