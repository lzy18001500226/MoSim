# MoSim Patch Record

No retained Sunray Gazebo source, model description, launch file, world,
plugin, configuration file, or build input was changed while copying this
component into `src/simulation/gazebo/sunray`.

The copy excludes 45 local backup/cache artifacts and all binary runtime assets
listed in `ASSET_MANIFEST.json`. `.gitattributes`, `.gitignore`, `README.md`,
`UPSTREAM.md`, this file, and the generated asset manifest are migration
metadata outside the 594-file source/configuration payload represented by the
SHA-256 in `UPSTREAM.md`.

Before this component can become `canonical_active`, a later task must:

1. choose and publish a versioned asset-pack delivery mechanism, then verify it
   against `ASSET_MANIFEST.json`;
2. recover or document upstream provenance and resolve the package license;
3. audit the sibling Sunray common-library path and all launch/Profile/script
   consumers;
4. update only those audited consumers to the canonical path; and
5. run the declared static and controlled ROS1 build/preflight checks while
   keeping `References/Sunray/simulation/sunray_simulator` intact as rollback.
