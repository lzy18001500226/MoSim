# Sunray Gazebo Plugin Source Provenance

- Imported source: `References/Sunray/simulation/gazebo_plugin`.
- Component identity: four ROS1 Catkin/Gazebo packages:
  `livox_laser_simulation`, `random_cylinder_plugin`,
  `realsense_gazebo_plugin`, and `wind_zone_plugin`.
- Upstream revision: the retained import has no recoverable nested Git metadata
  or upstream URL. Do not represent this snapshot as pinned to an external
  commit until a source-to-upstream audit supplies one.
- Last project commit affecting the retained source before this snapshot:
  `0bdabf6b0dcf511367ae56c1afeabad22d674c91`
  (`chore: normalize MoSim project structure`, 2026-05-24).
- License evidence: `realsense_gazebo_plugin/package.xml` declares Apache 2.0.
  The other three package manifests declare `TODO`, and the retained component
  has no standalone license file. A release-license audit is required before
  redistribution or canonical activation.
- Retained package snapshot excluding the generated Catkin workspace-root
  `CMakeLists.txt`: 33 files, 156,781,128 bytes.
- Imported source/configuration payload: 27 files, 260,098 bytes, tree
  SHA-256 `d3064a1bb015c1b627db02f15608273ec1effeec8afd79d5ea376662e82033f1`.
  The digest is computed over sorted relative path, byte count, and per-file
  SHA-256 records. The payload excludes the generated root CMake file and the
  external Livox scan-pattern CSV assets.
- External runtime assets: 6 files, 156,521,030 bytes, tree SHA-256
  `acd4ff7500c83d1f6b6e02192faafaffc7f43960b787c2aa81b849ecb79f7593`.
  Their per-file paths and hashes are frozen in `ASSET_MANIFEST.json`.
- Build-layout constraint: current scripts copy the legacy
  `livox_laser_simulation` package into an isolated Catkin overlay. This copy
  is not independently activatable until that overlay, its Livox message
  dependency, and all plugin consumers are audited.

The registry state is `copied_pending_activation`. The legacy source remains
the only active runtime path until asset delivery, provenance/license review,
path activation, and controlled ROS1 validation are completed.
