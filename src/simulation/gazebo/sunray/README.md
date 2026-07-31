# Sunray Gazebo Source Snapshot

This directory is the project-owned active source-and-configuration tree of the
ROS1 `sunray_simulator` package. It is registered as `canonical_active` in
`Config/project_paths.json`; the source-only foundation profile consumes this
path. `References/Sunray/simulation/sunray_simulator` remains intact as source
provenance, rollback material, and the retained source for asset
re-materialization. It is not the active project source route.

## External assets

Gazebo meshes, textures, scan-pattern CSV files, and the Blender source total
487 files and 1,005,559,590 bytes, including files larger than ordinary Git
limits. They were materialized into this directory and verified on 2026-08-01
against `ASSET_MANIFEST.json`; the verification record is
`Results/static_audits/local_source_activation_20260801/SUNRAY_ASSET_VERIFY.json`.
They remain Git-ignored because of size. A portable delivery must include these
materialized files or a separate pack that verifies against the same manifest.

## Migration boundary

No controller, launch, world, model, plugin, or configuration behavior was
changed by asset materialization. The retained legacy directory remains a
compatibility/source reference. The verified asset tree and source selection do
not prove a complete Gazebo/PX4/ROS runtime.
