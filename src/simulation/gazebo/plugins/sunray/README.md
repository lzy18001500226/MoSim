# Sunray Gazebo Plugin Snapshot

This directory is a source-and-configuration snapshot of the retained ROS1
Gazebo plugin packages:

- `livox_laser_simulation`
- `random_cylinder_plugin`
- `realsense_gazebo_plugin`
- `wind_zone_plugin`

It is registered as the project-owned `canonical_active` source path in
`Config/project_paths.json`, and the source-only foundation profile consumes
it. `References/Sunray/simulation/gazebo_plugin` remains intact as provenance,
rollback material, and the retained source for asset re-materialization; it is
not the active project source route.

## External assets

The six Livox scan-pattern CSV files total 156,521,030 bytes and are required
by `livox_laser_simulation`. They were materialized into this directory and
verified on 2026-08-01 against `ASSET_MANIFEST.json`; the verification record is
`Results/static_audits/local_source_activation_20260801/SUNRAY_ASSET_VERIFY.json`.
They remain Git-ignored because of size. A portable delivery must include these
materialized files or a separate pack that verifies against the same manifest.

## Migration boundary

No plugin source, package manifest, CMake input, world, or configuration was
changed by asset materialization. The retained legacy directory remains a
compatibility/source reference. The verified asset tree and source selection do
not prove a complete Gazebo/PX4/ROS runtime.
