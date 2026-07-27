# MoSim Patch Record

No `sunray_tutorial` source, CMake, package metadata, launch, configuration, or
script file was changed while copying this component into
`src/planning/mission_adapters/sunray_tutorial`.

The only migration additions are `.gitattributes`, `UPSTREAM.md`, and this file.
They are outside the 61-file payload represented by the SHA-256 in
`UPSTREAM.md`.

Before this component can become `canonical_active`, the migration task must:

1. resolve and record the exact Sunray source revision and license evidence;
2. replace the legacy sibling include assumption only in audited consumers;
3. validate `sunray_msgs`, OpenCV, Boost, and the local message-generation
   target contract;
4. update only audited `run_demo.launch` consumers to the canonical path;
5. run the declared static and ROS1 build/preflight checks; and
6. keep `References/Sunray/General_Module/sunray_tutorial` intact as the
   retained legacy source unless a later user-approved archival task says
   otherwise.
