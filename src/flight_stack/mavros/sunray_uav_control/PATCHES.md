# MoSim Patch Record

No `sunray_uav_control` source, CMake, package metadata, launch, MAVLink,
configuration, script, mesh, or RViz file was changed while copying this
component into `src/flight_stack/mavros/sunray_uav_control`.

The only migration additions are `.gitattributes`, `UPSTREAM.md`, and this
file. They are outside the 567-file payload represented by the SHA-256 in
`UPSTREAM.md`.

The copy intentionally excludes the 20 historical
`launch/sunray_control_node.launch.bak_mosim_*` files. The live
`sunray_control_node.launch` file and all other source payload files are
retained unchanged.

Before this component can become `canonical_active`, the migration task must:

1. resolve and record the exact Sunray and embedded-MAVLink source revisions
   and license evidence;
2. audit and migrate the required `sunray_common/common_lib` sibling layout;
3. reconcile the local message-generation and `sunray_control_gencpp` target
   contract without silently substituting generated outputs;
4. update only audited overlay and runtime consumers to the canonical path;
5. run the declared static and ROS1 build/preflight checks; and
6. keep `References/Sunray/General_Module/sunray_uav_control` intact as the
   retained legacy source unless a later user-approved archival task says
   otherwise.
