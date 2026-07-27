# sunray_uav_control Source Provenance

- Upstream repository and revision: not recoverable from the retained imported
  Sunray snapshot. Do not represent this copy as pinned to an upstream Git
  commit until a source-to-upstream comparison supplies one.
- Imported source:
  `References/Sunray/General_Module/sunray_uav_control`
- Retained raw snapshot: 587 files, tree SHA-256
  `847699b0a94457610dda738d22cb411a3920c79a1e53ae04cda3cd6dd6c5d3f2`.
- Imported deliverable payload: 567 files, tree SHA-256
  `2d723ac1e96c310b0d9ece1c830d7c9613ea014c9ff3363f15478ad1d9c192d8`.
  It excludes 20 historical `launch/sunray_control_node.launch.bak_mosim_*`
  backup files. The source payload retains the MAVLink C-header snapshot
  directly included by this package's CMake configuration and the `uav.mesh`
  runtime asset.
- Last project commit affecting the retained imported path:
  `3fbd5f4c107176bb9edbfae4cf68ed9823db28f2`
  (`References/Sunray: update control and sensor references`, 2026-07-15).
- License evidence: `package.xml` declares `TODO` and the retained component
  has no standalone top-level license file. A package and embedded-MAVLink
  license audit is required before redistribution.
- Build-layout constraints: `CMakeLists.txt` includes the legacy sibling path
  `${PROJECT_SOURCE_DIR}/../sunray_common/common_lib`; it also invokes
  `generate_messages()` and references `sunray_control_gencpp` while this
  retained component contains no local `.msg`, `.srv`, or `.action` files.
  These contracts must be audited before activation; this copy does not change
  them.

The 567-file deliverable payload is a byte-for-byte copy of the retained source
after the documented backup exclusions. `.gitattributes`, `UPSTREAM.md`, and
`PATCHES.md` are migration metadata outside that payload. Its registry state is
`copied_pending_activation`: the legacy path remains the only active runtime
path until its ROS1 overlay, entrypoints, source revision, license evidence,
message-generation contract, and sibling dependency are validated.
