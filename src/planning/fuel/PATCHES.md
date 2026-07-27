# MoSim Patch Record

No FUEL algorithm, launch, CMake, parameter, resource, or asset file was
changed while copying this component into `src/planning/fuel`.

The only migration additions are `.gitattributes`, `UPSTREAM.md`, and this
file. `.gitattributes` preserves the imported snapshot's pre-existing
whitespace formatting without changing source content. These files are outside
the 785-file deliverable payload represented by the SHA-256 in `UPSTREAM.md`.

The copy intentionally excludes four local `build` trees and their nested
`devel` outputs, three Python bytecode files, three local shared objects, and
the ignored LKH runtime-state files `single.par`, `single.tsp`, and `single.txt`,
plus two prebuilt `odom_visualization` ELF executables. The project-root
`.gitignore` also excludes 76 Catkin/Dynamic Reconfigure generated message and
configuration files while retaining their source `.msg` and `.cfg` definitions,
six editor backup files, and generated `disturbance_ui.cfgc` bytecode. All
excluded files are retained unchanged at the old path but are not source or
required runtime assets.

Before this component can become `canonical_active`, the migration task must:

1. resolve and record the exact upstream commit and bundled dependency licenses;
2. update only the audited FUEL entrypoints to the canonical path;
3. run the declared static and ROS1 preflight/build checks; and
4. keep `References/Lab/exploration_coverage/FUEL` intact as the retained
   legacy source unless a later user-approved archival task says otherwise.
