# EGO Planner Swarm Core Snapshot

This directory contains the minimal source packages used by the retained
EGO/EGO-Swarm compatibility overlay:

- `src/uav_simulator/Utils/cmake_utils`
- `src/uav_simulator/Utils/pose_utils`
- `src/planner/traj_utils`
- `src/planner/plan_env`
- `src/planner/path_searching`
- `src/planner/bspline_opt`
- `src/planner/plan_manage` (ROS package `ego_planner`)

It is deliberately inactive. Existing scripts still resolve
`References/Sunray/External_Module/ego-planner-swarm`; this source snapshot
does not change their overlay, launch, or runtime behavior.

## Scope

This is not a full upstream EGO-Planner workspace. It excludes unused simulator
and demo packages, presentation media, the generated Catkin workspace-root
`CMakeLists.txt`, and one editor backup. The retained `src/` hierarchy matches
the Catkin package paths expected by the compatibility overlay.

The overlay also needs `uav_utils` and `quadrotor_msgs`. They are intentionally
not duplicated here: same-named imports already exist elsewhere in MoSim, but
their compatibility has not been audited. In particular, the retained EGO
overlay currently links its own `uav_utils` source and a px4ctrl workspace
`quadrotor_msgs` package. A future activation must select and validate one
compatible package set rather than exposing duplicate ROS package names.

## Migration boundary

No planner source, message definition, launch file, package manifest, or CMake
input in the copied payload was changed. The retained legacy directory is the
only active runtime path.
