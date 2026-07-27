# MoSim Patch Record

No retained Sunray Gazebo plugin source, package manifest, CMake input, world,
or configuration file was changed while copying this component into
`src/simulation/gazebo/plugins/sunray`.

The copy excludes the generated Catkin workspace-root `CMakeLists.txt` and the
six Livox scan-pattern CSV assets listed in `ASSET_MANIFEST.json`.
`.gitattributes`, `.gitignore`, `README.md`, `UPSTREAM.md`, this file, and the
asset manifest are migration metadata outside the 27-file source/configuration
payload represented by the SHA-256 in `UPSTREAM.md`.

Before this component can become `canonical_active`, a later task must:

1. choose and publish a versioned Livox scan-asset delivery mechanism, then
   verify it against `ASSET_MANIFEST.json`;
2. recover or document upstream provenance and resolve the three unresolved
   package licenses;
3. audit the isolated Livox overlay, message dependency, and every current
   script/Profile consumer;
4. update only those audited consumers to the canonical path; and
5. run the declared static and controlled ROS1 build/preflight checks while
   keeping `References/Sunray/simulation/gazebo_plugin` intact as rollback.
