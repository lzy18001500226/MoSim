# sunray_tutorial Source Provenance

- Upstream repository and revision: not recoverable from the retained imported
  Sunray snapshot. Do not represent this copy as pinned to an upstream Git
  commit until a source-to-upstream comparison supplies one.
- Imported source:
  `References/Sunray/General_Module/sunray_tutorial`
- Retained raw snapshot and imported deliverable payload: 61 files, tree
  SHA-256 `6bf007f55c91660154afb4fd22ffbcd6114218b2ee4f907d7f674ef703dd65dc`.
  It contains the generic Sunray demonstration task publishers, including the
  `run_demo.launch` path used by current default-stack scripts. No build, devel,
  install, cache, media, or editor-backup payload was present or copied.
- Last project commit affecting the retained imported path:
  `0bdabf6b0dcf511367ae56c1afeabad22d674c91`
  (`chore: normalize MoSim project structure`, 2026-05-24).
- License evidence: `package.xml` declares `TODO` and the retained component
  has no standalone top-level license file. A package and bundled-code license
  audit is required before redistribution.
- Build-layout constraints: the package requires `sunray_msgs`, Boost, OpenCV,
  and the legacy sibling include path
  `${PROJECT_SOURCE_DIR}/../sunray_common/common_lib`. Its CMake configuration
  invokes `generate_messages()` and declares `sunray_tutorial_gencpp` targets
  despite retaining no local `.msg`, `.srv`, or `.action` files. Those contracts
  must be audited before activation; this copy does not change them.

The 61-file deliverable payload is a byte-for-byte copy of the retained source.
`.gitattributes`, `UPSTREAM.md`, and `PATCHES.md` are migration metadata outside
that payload. Its registry state is `copied_pending_activation`: the legacy path
remains the only active runtime path until its ROS1 overlay, entrypoints, source
revision, license evidence, message-generation contract, and sibling dependency
are validated.
