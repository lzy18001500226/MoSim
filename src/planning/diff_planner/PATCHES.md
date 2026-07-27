# MoSim Patch Record

No Diff-Planner algorithm, launch, CMake, parameter, or asset file was changed
while copying this component into `src/planning/diff_planner`.

The only migration additions are `.gitattributes`, `UPSTREAM.md`, and this
file. `.gitattributes` preserves the imported snapshot's pre-existing
whitespace formatting without changing source content. These files are outside
the 608-file deliverable payload represented by the SHA-256 in `UPSTREAM.md`.

Four local `.vscode` configuration files and
`src/Utils/odom_visualization/OgreMeshUpgrade.log` were intentionally excluded
from the new copy. They are retained unchanged at the old path but are not
source or required runtime assets.

Before this component can become `canonical_active`, the migration task must:

1. resolve and record the exact upstream commit and submodule identities;
2. update only the audited Diff-Planner entrypoints to the canonical path;
3. run the declared static and ROS1 preflight/build checks; and
4. keep `References/Lab/planning_local/Diff-Planner` intact as the retained
   legacy source unless a later user-approved archival task says otherwise.
