# MoSim Patch Record

No `px4ctrl` source, CMake, package metadata, launch, configuration, or script
file was changed while copying this component into
`src/control/runtime_adapters/px4ctrl`.

The imported payload deliberately includes the two pre-existing, uncommitted
MoSim working-tree changes present at capture time:

1. `CMakeLists.txt`: P10 generated-backend selectors and generated-code paths.
2. `src/controller.cpp`: P10 L1/AWFF, DFBC, and H-infinity generated-backend
   dispatch, observability, and command-adaptation logic.

They are part of the frozen current-source snapshot, not migration edits. The
only migration additions are `.gitattributes`, `UPSTREAM.md`, and this file;
they are outside the 17-file payload represented by the SHA-256 in
`UPSTREAM.md`.

Before this component can become `canonical_active`, the migration task must:

1. resolve and record the exact Fast-Drone-250 source revision and GPL
   redistribution obligations;
2. review and commit the retained P10 working-tree patch as an explicit
   controller/runtime change, independently from this copy-only migration;
3. update only audited scripts, Profiles, and ROS overlays to the canonical
   path;
4. validate all required generated C/C++ directories and the backend selector;
5. run the declared static and ROS1 build/preflight checks; and
6. keep `References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl`
   intact as the retained legacy source unless a later user-approved archival
   task says otherwise.
