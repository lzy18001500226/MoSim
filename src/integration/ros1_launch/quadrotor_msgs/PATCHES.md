# MoSim Patch Record

No `quadrotor_msgs` source, CMake, package metadata, message definition, or
library file was changed while copying this component into
`src/integration/ros1_launch/quadrotor_msgs`.

The only migration additions are `.gitattributes`, `UPSTREAM.md`, and this
file. They are outside the 34-file payload represented by the SHA-256 in
`UPSTREAM.md`.

The copy intentionally excludes Catkin-generated Python message output under
`src/quadrotor_msgs/` and the two `*.msg~` editor backups. The CMake generation
rules and all retained `.msg` definitions are copied, so the excluded output
must be regenerated in a validated ROS1 workspace rather than delivered as
source.

Before this component can become `canonical_active`, the migration task must:

1. resolve and record the exact upstream revision and license evidence;
2. update only audited overlay and runtime consumers to the canonical path;
3. regenerate messages and run the declared static and ROS1 build/preflight
   checks; and
4. keep `References/Lab/planning_local/Fast-Drone-250/src/utils/quadrotor_msgs`
   intact as the retained legacy source unless a later user-approved archival
   task says otherwise.
