# MoSim Patch Record

No `sunray_planner_utils` source, CMake, package metadata, launch, config, or
script file was changed while copying this component into
`src/integration/ros1_launch/sunray_planner_utils`.

The only migration additions are `.gitattributes`, `UPSTREAM.md`, and this
file. They are outside the 40-file payload represented by the SHA-256 in
`UPSTREAM.md`.

Before this component can become `canonical_active`, the migration task must:

1. resolve and record the exact upstream revision and license evidence;
2. audit and migrate the required `sunray_common/common_lib` sibling layout;
3. update only audited overlay and runtime consumers to the canonical path;
4. run the declared static and ROS1 build/preflight checks; and
5. keep `References/Sunray/General_Module/sunray_planner_utils` intact as the
   retained legacy source unless a later user-approved archival task says
   otherwise.
