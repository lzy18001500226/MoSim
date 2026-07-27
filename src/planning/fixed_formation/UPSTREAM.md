# Swarm-Formation Source Provenance

- Upstream repository: `https://github.com/ZJU-FAST-Lab/Swarm-Formation.git`.
  The retained imported snapshot cannot recover the exact upstream revision;
  do not represent this copy as pinned until a source-to-upstream comparison
  supplies one.
- Imported source:
  `References/Lab/swarm_coordination/Swarm-Formation`
- Retained raw snapshot: 534 files, tree SHA-256
  `8269c172068e8d9dc41ea9a654f34e9dede12659ca5cd795e847069213caea6d`.
- Imported deliverable payload: 525 files, tree SHA-256
  `c3950cc62a2063243997dc4b7e7897a783f512f5682e9178c47aa148d91cf605`.
  It excludes the `fig/` documentation/demo media and all `.vscode/` local
  editor settings; no build, devel, install, cache, log, or generated payload
  was present or copied.
- Last project commit affecting the retained imported path before this copy:
  `65e4fcaa03012964a3c14374ffcc7fbcbbdf4d95`
  (`fix Factory Swarm-Formation obstacle crossing`, 2026-07-16).
- License evidence: the retained component carries GPL-3.0 text in `LICENSE`.
- Snapshot note: at capture time the legacy worktree had uncommitted MoSim
  collision/replanning changes in six planner source/header files. They are
  intentionally retained byte-for-byte in this delivery snapshot and are
  described in `PATCHES.md`; migration did not alter them.
- Build-layout constraints: this is a Catkin workspace with multiple nested
  planner packages. Current Factory scripts prepare a dedicated workspace and
  apply source audits/patches around the legacy path; those consumers must be
  audited before activation.

The 525-file deliverable payload is a byte-for-byte copy of the retained source
after the documented exclusions. `.gitattributes`, `UPSTREAM.md`, and
`PATCHES.md` are migration metadata outside that payload. Its registry state is
`copied_pending_activation`: the legacy path remains the only active runtime
path until source provenance, active scripts, local patch ownership, licenses,
and a controlled ROS1 build/preflight are validated.
