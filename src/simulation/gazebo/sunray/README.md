# Sunray Gazebo Source Snapshot

This directory is a source-and-configuration snapshot of the retained ROS1
`sunray_simulator` package. It is deliberately inactive: existing launch
scripts and Profiles continue to use
`References/Sunray/simulation/sunray_simulator` until a separate activation
task audits the path, Catkin layout, sibling `sunray_common` dependency, and a
controlled ROS1 preflight.

## External assets

Gazebo meshes, textures, scan-pattern CSV files, and the Blender source are not
stored in this ordinary Git snapshot. They total 487 files and 1,005,559,590
bytes, including individual files larger than GitHub's ordinary Git limit.
`ASSET_MANIFEST.json` records every required path, byte count, and SHA-256.

An eventual versioned asset pack must be extracted into this directory while
preserving the manifest paths. Verify its files against the manifest before
using this tree as a runtime source. The asset-pack hosting mechanism remains a
separate delivery decision; until it is made, this snapshot is source-complete
but not a standalone runnable Gazebo package.

## Migration boundary

No controller, launch, world, model, plugin, or configuration behavior was
changed during this copy. The retained legacy directory stays intact and is the
only active runtime path.
