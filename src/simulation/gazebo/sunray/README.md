# Sunray Gazebo Source Snapshot

This directory is the project-owned source-and-configuration copy of the ROS1
`sunray_simulator` package. It is registered as the canonical source path in
`Config/project_paths.json`, and source-local preflight/overlay scripts consume
it. Some owner/runtime profiles and historical diagnostics still contain
explicit `References/Sunray/simulation/sunray_simulator` paths; those consumers
must be migrated independently before the legacy tree can be archived.

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
changed during the copy. The legacy directory remains a compatibility/source
reference until every direct consumer is replaced. Presence of this directory
does not prove a complete standalone Gazebo runtime.
