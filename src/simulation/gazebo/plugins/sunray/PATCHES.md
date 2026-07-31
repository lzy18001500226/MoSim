# MoSim Patch Record

No retained Sunray Gazebo plugin source, package manifest, CMake input, world,
or configuration file was changed while copying this component into
`src/simulation/gazebo/plugins/sunray`.

The copy excludes the generated Catkin workspace-root `CMakeLists.txt` and the
six Livox scan-pattern CSV assets listed in `ASSET_MANIFEST.json`.
`.gitattributes`, `.gitignore`, `README.md`, `UPSTREAM.md`, this file, and the
asset manifest are migration metadata outside the 27-file source/configuration
payload represented by the SHA-256 in `UPSTREAM.md`.

On 2026-08-01, the six manifest-listed Livox scan assets were materialized into
this directory and SHA-256 verified. The source tree is now `canonical_active`
for project-local source selection. The retained
`References/Sunray/simulation/gazebo_plugin` directory was not modified.

Remaining external-delivery boundaries are provenance/license review, portable
distribution of Git-ignored assets, the optional vendor Livox driver feature,
and separately authorized Gazebo/ROS/PX4 runtime validation.
