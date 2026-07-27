# MoSim Patch Record

No `uav_utils` source, CMake, package metadata, or script file was changed
while copying this component into `src/common/utilities/ros1/uav_utils`.

The only migration additions are `.gitattributes`, `UPSTREAM.md`, and this
file. They are outside the 11-file payload represented by the SHA-256 in
`UPSTREAM.md`.

No Python compatibility port was performed. In particular,
`scripts/tf_assist.py` retains its legacy Python 2 exception syntax so the
copied source remains byte-for-byte identical to the retained snapshot.

Before this component can become `canonical_active`, the migration task must:

1. resolve and record the exact upstream revision and license evidence;
2. update only audited consumers to the canonical path;
3. run the declared static and ROS1 build/preflight checks; and
4. keep `References/Lab/planning_local/Fast-Drone-250/src/utils/uav_utils`
   intact as the retained legacy source unless a later user-approved archival
   task says otherwise.
