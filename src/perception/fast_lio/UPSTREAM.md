# FAST-LIO Source Provenance

- Upstream repository: `https://github.com/hku-mars/FAST_LIO.git`
- Upstream revision: not recoverable from the retained imported snapshot. Do
  not represent this copy as pinned to a Git commit until a source-to-upstream
  comparison supplies one.
- Imported source: `References/Lab/localization_slam/FAST_LIO`
- Retained raw snapshot: 85 files, tree SHA-256
  `a4931b9ce91f98384a9c785ac7aa5b5103acb056e4cf1c3ec5c3ccb33918aa1d`.
- Imported deliverable payload: 49 files, tree SHA-256
  `6f830a3fbd685e84894e646e29a16222996a7f24743432dc0fee0f04ac5e8bfe`.
  It excludes the upstream `doc/` demonstration media, the `Log/` runtime
  analysis/output directory, and the `PCD/` runtime point-cloud output
  directory. `Log/.gitkeep` and `PCD/.gitkeep` are MoSim metadata placeholders
  so original runtime paths exist without importing historical output.
- Submodule declaration: `.gitmodules` identifies `include/ikd-Tree` as
  `https://github.com/hku-mars/ikd-Tree.git`, branch `fast_lio`; the retained
  source snapshot contains the required submodule files but not its exact
  commit identity.
- Last project commit affecting the retained imported path:
  `c679edfb802cedef723650cc2b7857588445d577`
  (`Reclassify FAST-LIO reference with Sunray tuning`, 2026-07-16).
- License evidence: root `LICENSE` is GPL-2.0 text, while `package.xml`
  declares `BSD`. This discrepancy requires a release-license audit before
  redistribution.

The 49-file deliverable payload is a byte-for-byte copy of the retained source
after the documented non-source exclusions. `.gitattributes`, `UPSTREAM.md`,
`PATCHES.md`, and the two runtime-directory placeholders are migration metadata
outside that payload. Its registry state is `copied_pending_activation`: the
legacy path remains the only active runtime path until the ROS1 workspace,
submodule identity, entrypoints, and license audit are validated.
