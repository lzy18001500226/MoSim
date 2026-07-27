# MoSim Patch Record

No `livox_ros_driver_compat` source, CMake, package metadata, or message
definition was changed while copying this component into
`src/perception/livox_ros_driver_compat`.

The only migration additions are `.gitattributes`, `UPSTREAM.md`, and this
file. They are outside the 4-file payload represented by the SHA-256 in
`UPSTREAM.md`.

Before this component can become `canonical_active`, the migration task must:

1. audit the package name and ROS1 message contract against FAST-LIO consumers;
2. update only audited FAST-LIO and runtime entrypoints to the canonical path;
3. regenerate messages and run the declared ROS1 build/preflight checks; and
4. keep `References/Lab/localization_slam/livox_ros_driver_compat` intact as
   the retained legacy source unless a later user-approved archival task says
   otherwise.
