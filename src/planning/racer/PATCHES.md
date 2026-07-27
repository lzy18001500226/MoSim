# MoSim Patch Record

No RACER algorithm, launch, CMake, parameter, source, or tracked asset file
was changed while copying this component into `src/planning/racer`.

The only migration additions are `.gitattributes`, `UPSTREAM.md`, and this
file. `.gitattributes` preserves the imported snapshot's pre-existing
whitespace formatting without changing source content. These files are outside
the 1,081-file deliverable payload represented by the SHA-256 in `UPSTREAM.md`.

The copy is deliberately limited to the retained source directory's 1,081
Git-tracked files. Local build products, Catkin `devel` output, logs, Python
bytecode, and generated files remain untouched at the legacy path and are not
source or required delivery assets.

Before this component can become `canonical_active`, the migration task must:

1. resolve and record the exact upstream revision and bundled dependency
   licenses;
2. audit RACER's ROS1 package/dependency boundary, including duplicated
   message and utility packages, against the selected MoSim runtime;
3. update only the audited RACER entrypoints to the canonical path; and
4. run the declared static and ROS1 preflight/build checks while keeping
   `References/Lab/exploration_coverage/RACER` intact unless a later
   user-approved archival task says otherwise.
