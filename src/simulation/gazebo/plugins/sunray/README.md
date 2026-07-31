# Sunray Gazebo Plugin Snapshot

This directory is a source-and-configuration snapshot of the retained ROS1
Gazebo plugin packages:

- `livox_laser_simulation`
- `random_cylinder_plugin`
- `realsense_gazebo_plugin`
- `wind_zone_plugin`

It is registered as the project-owned canonical source path in
`Config/project_paths.json`, and the source-local ROS1 preflight/overlay uses
it. Some asset manifests, UE helpers, and historical runtime consumers still
name `References/Sunray/simulation/gazebo_plugin`; those direct consumers must
be migrated or explicitly retained before that legacy tree is archived.

## External assets

The six Livox scan-pattern CSV files are not stored in this ordinary Git
snapshot. They total 156,521,030 bytes and are required by
`livox_laser_simulation`. `ASSET_MANIFEST.json` records every expected path,
byte count, and SHA-256. A future versioned asset pack must be extracted into
this directory while preserving those paths, then verified against the
manifest before this snapshot is used as a runtime source.

## Migration boundary

No plugin source, package manifest, CMake input, world, or configuration was
changed during the copy. The legacy directory remains a compatibility/source
reference until every direct consumer is replaced. Presence of this directory
does not prove a complete standalone Gazebo runtime.
