# sunray_common Source Provenance

- Upstream repository and revision: not recoverable from the retained imported
  Sunray snapshot. Do not represent this copy as pinned to an upstream Git
  commit until a source-to-upstream comparison supplies one.
- Imported source:
  `References/Sunray/General_Module/sunray_common`
- Retained raw snapshot and imported deliverable payload: 40 files, tree
  SHA-256 `25fdafec215f7fdd5d023dd8383b39f22d2eda43125afa91ada1d922123bb213`.
  It contains the `common_lib` headers and the nested `sunray_msgs` ROS message
  package. No build, devel, install, cache, media, or editor-backup payload was
  present or copied.
- Last project commit affecting the retained imported path:
  `0bdabf6b0dcf511367ae56c1afeabad22d674c91`
  (`chore: normalize MoSim project structure`, 2026-05-24).
- License evidence: `sunray_msgs/package.xml` declares `TODO` and the retained
  component has no standalone top-level license file. A package and header
  license audit is required before redistribution.
- Build-layout constraints: retained `sunray_uav_control` and
  `sunray_planner_utils` directly include the legacy sibling path
  `${PROJECT_SOURCE_DIR}/../sunray_common/common_lib`. The nested `sunray_msgs`
  package also requires normal Catkin message generation. Those contracts must
  be audited before activation; this copy does not change them.

The 40-file deliverable payload is a byte-for-byte copy of the retained source.
`.gitattributes`, `UPSTREAM.md`, and `PATCHES.md` are migration metadata outside
that payload. Its registry state is `copied_pending_activation`: the legacy path
remains the only active runtime path until the ROS1 overlay, entrypoints,
source revision, license evidence, message-generation contract, and sibling
dependency are validated.
