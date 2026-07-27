# Diff-Planner Source Provenance

- Upstream repository: `https://github.com/DifferentialRobotics/Diff-Planner.git`
- Upstream revision: not recoverable from the retained imported snapshot. Do
  not represent this copy as pinned to a Git commit until a source-to-upstream
  comparison supplies one.
- Imported source: `References/Lab/planning_local/Diff-Planner`
- Retained raw snapshot: 613 files, tree SHA-256
  `60f3ae2837c8b42f71c5e9892807ab5d40993fd50cb37053c86a496a7195daf1`.
- Imported deliverable payload: 608 files, tree SHA-256
  `bd9f049290b4ad38b7021869dad98a4be3a132fdd9c75d6f367f2222f65ffe62`.
  It excludes only four local `.vscode` files and
  `src/Utils/odom_visualization/OgreMeshUpgrade.log`; these are editor-local
  configuration or a generated tool log, not source or required runtime assets.
- Last project commit affecting the retained imported path:
  `ad8a3f31736cd700afc3d194698416047cc427da`
  (`refs(diff-planner): add odeint examples and tests`, 2026-07-16).
- Root license: GPL-3.0, preserved in `LICENSE`. Individual bundled ROS
  packages declare additional licenses or incomplete `TODO` metadata in their
  own `package.xml` files. A release-license audit remains required.

The 608-file deliverable payload is a byte-for-byte copy of the retained source
after the documented non-source exclusions. `.gitattributes`, `UPSTREAM.md`,
and `PATCHES.md` are migration metadata outside that payload. Its registry
state is `copied_pending_activation`: the legacy path remains the only active
runtime path until the ROS1 overlay, launch scripts, source revision, and
license audit are validated.
