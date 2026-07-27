# Sunray Gazebo Plugin Snapshot

This directory is a source-and-configuration snapshot of the retained ROS1
Gazebo plugin packages:

- `livox_laser_simulation`
- `random_cylinder_plugin`
- `realsense_gazebo_plugin`
- `wind_zone_plugin`

It is deliberately inactive. Existing scripts and runtime profiles continue
to use `References/Sunray/simulation/gazebo_plugin` until a separate
activation task audits the Catkin overlay, source provenance, licenses, and
all consumers.

## External assets

The six Livox scan-pattern CSV files are not stored in this ordinary Git
snapshot. They total 156,521,030 bytes and are required by
`livox_laser_simulation`. `ASSET_MANIFEST.json` records every expected path,
byte count, and SHA-256. A future versioned asset pack must be extracted into
this directory while preserving those paths, then verified against the
manifest before this snapshot is used as a runtime source.

## Migration boundary

No plugin source, package manifest, CMake input, world, or configuration was
changed during the copy. The retained legacy directory remains intact and is
the only active runtime path.
