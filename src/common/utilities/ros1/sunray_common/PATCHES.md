# MoSim Patch Record

No `sunray_common` header, message definition, CMake, package metadata, launch,
configuration, or script file was changed while copying this component into
`src/common/utilities/ros1/sunray_common`.

The only migration additions are `.gitattributes`, `UPSTREAM.md`, and this file.
They are outside the 40-file payload represented by the SHA-256 in
`UPSTREAM.md`.

Before this component can become `canonical_active`, the migration task must:

1. resolve and record the exact Sunray source revision and license evidence;
2. replace the legacy sibling include assumptions only in audited consumers;
3. validate the `sunray_msgs` Catkin message-generation contract;
4. update only audited overlay and runtime consumers to the canonical path;
5. run the declared static and ROS1 build/preflight checks; and
6. keep `References/Sunray/General_Module/sunray_common` intact as the retained
   legacy source unless a later user-approved archival task says otherwise.
