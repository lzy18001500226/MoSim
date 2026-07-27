# px4ctrl Source Provenance

- Upstream repository: `https://github.com/ZJU-FAST-Lab/Fast-Drone-250`.
  The retained imported snapshot cannot recover the exact upstream revision;
  do not represent this copy as pinned until a source-to-upstream comparison
  supplies one.
- Imported source:
  `References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl`
- Retained raw snapshot and imported deliverable payload: 17 files, tree
  SHA-256 `c293274d4f02168e22a682bba6243aa255a6ff6a5f5f4c1f2831327ceed86dcd`.
  No build, devel, install, cache, media, or editor-backup payload was present
  or copied.
- Last project commit affecting the retained imported path before this copy:
  `1eb7342956fbc477da0985387bbd588d5585d2f5`
  (`chore(sunray): lock virtual PX4 Classic parameters`, 2026-07-25).
- License evidence: the retained component carries GPL-3.0 text in `LICENSE`,
  and `package.xml` declares `GPLv3`.
- Snapshot note: at capture time the legacy worktree had uncommitted MoSim P10
  generated-backend additions in `CMakeLists.txt` and `src/controller.cpp`.
  They are intentionally retained byte-for-byte in this delivery snapshot and
  are described in `PATCHES.md`; migration did not alter either file.
- Build-layout constraints: the package depends on `uav_utils`,
  `quadrotor_msgs`, MAVROS, and MoSim-generated C/C++ directories under
  `Results/`. Current scripts still name the legacy path, and must be audited
  before activation.

The 17-file deliverable payload is a byte-for-byte copy of the retained source.
`.gitattributes`, `UPSTREAM.md`, and `PATCHES.md` are migration metadata outside
that payload. Its registry state is `copied_pending_activation`: the legacy path
remains the only active runtime path until source provenance, active scripts,
generated-code contracts, licenses, and a controlled ROS1 build/preflight are
validated.
