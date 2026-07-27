# EGO Planner Swarm Core Source Provenance

- Imported source: `References/Sunray/External_Module/ego-planner-swarm`.
- Component identity: retained EGO/EGO-Swarm planner compatibility core; the
  imported directory has no recoverable nested Git metadata or upstream URL.
  Do not represent this snapshot as pinned to an external repository or commit
  until a source-to-upstream audit supplies one.
- Last project commit affecting the retained source before this snapshot:
  `e0ed73e908b8c9858708fe678fb65af9284f3d79`
  (`references: add sunray simulation assets`, 2026-06-07).
- Retained raw tree: 553 files, 31,086,003 bytes. It contains simulator/demo
  packages and media outside the current compatibility overlay.
- Imported core payload: 73 files, 631,925 bytes, tree SHA-256
  `efebe790d2db433a8ccbb79686a2ebf97daeba3713880f411d25cab0bd3e09eb`.
  The digest is computed over sorted relative path, byte count, and per-file
  SHA-256 records. It consists only of the seven packages listed in `README.md`
  after excluding `pose_utils/src/pose_utils.cpp~`.
- License evidence: `cmake_utils` declares LGPLv3 and `pose_utils` declares
  BSD. `traj_utils`, `plan_env`, `path_searching`, `bspline_opt`, and
  `ego_planner` declare `TODO`; no standalone license file is present in the
  retained root. A release-license audit is required before redistribution or
  canonical activation.
- Build-layout constraint: `ego_planner` requires `quadrotor_msgs`, while the
  copied planner packages use `uav_utils`; the retained overlay currently
  selects versions outside this payload. The snapshot is therefore not
  independently activatable until those package choices, Catkin overlay, and
  every consumer are audited.

The registry state is `copied_pending_activation`. The legacy source remains
the only active runtime path until provenance/license review, dependency
selection, path activation, and controlled ROS1 validation are completed.
