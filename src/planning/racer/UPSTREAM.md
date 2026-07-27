# RACER Source Provenance

- Upstream repository: `https://github.com/SYSU-STAR/RACER.git` (declared by
  the retained README).
- Upstream revision: not recoverable from the retained imported snapshot. Do
  not represent this copy as pinned to a Git commit until a source-to-upstream
  comparison supplies one.
- Imported source: `References/Lab/exploration_coverage/RACER`.
- Retained raw source payload: 1,081 Git-tracked files, 49,292,647 bytes, tree
  SHA-256 `4b700014f7e12c52097d8e69e45f0680bf576cbba780a9555f3993f36d6e0c2b`.
- Imported deliverable payload: the same 1,081 files and the same tree
  SHA-256. Local `build`, `devel`, logs, Python bytecode, and other untracked
  generated output under the retained source directory are intentionally not
  part of this snapshot.
- Last project commit affecting the retained imported path:
  `3746bf19ac10c6d11f639e24d63240c274cf2bed`
  (`refs(racer): add exploration source batch 06`, 2026-07-16).
- No root `LICENSE`, `COPYING`, or `NOTICE` file was present in the retained
  tracked payload. The 26 bundled ROS packages declare `BSD`, `GPLv3`,
  `LGPLv3`, or `TODO`; an upstream and package-level license audit is required
  before redistribution.
- The retained README declares external dependencies on NLopt 2.7.1, LKH
  3.0.6, Armadillo, and a ROS1 Catkin workspace. None was installed or tested
  by this snapshot task.

The registry state is `copied_pending_activation`: the legacy path remains the
only active runtime path until the ROS1 workspace, launch scripts, source
revision, package collisions, and license audit are validated.
