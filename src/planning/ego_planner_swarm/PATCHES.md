# MoSim Patch Record

No retained EGO planner source, message definition, launch file, package
manifest, or CMake input in the copied payload was changed while creating this
snapshot.

This is a deliberately scoped compatibility-core copy, not a full upstream
workspace migration. It excludes the generated root `CMakeLists.txt`, unused
simulator/demo packages and media, the source copies of `uav_utils` and
`quadrotor_msgs`, and the editor backup `pose_utils/src/pose_utils.cpp~`.
`.gitattributes`, `.gitignore`, `README.md`, `UPSTREAM.md`, and this file are
migration metadata outside the 73-file source payload represented by the
SHA-256 in `UPSTREAM.md`.

Before this component can become `canonical_active`, a later task must:

1. recover or document upstream provenance and resolve the five unresolved
   planner-package licenses;
2. select the compatible `uav_utils` and `quadrotor_msgs` package versions,
   without exposing duplicate ROS package names;
3. audit the EGO single/swarm overlay, launch files, and all script/Profile
   consumers;
4. update only those audited consumers to the canonical path; and
5. run the declared static and controlled ROS1 build/preflight checks while
   keeping `References/Sunray/External_Module/ego-planner-swarm` intact as
   rollback.
