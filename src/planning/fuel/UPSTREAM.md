# FUEL Source Provenance

- Upstream repository: `https://github.com/HKUST-Aerial-Robotics/FUEL.git`
- Upstream revision: not recoverable from the retained imported snapshot. Do
  not represent this copy as pinned to a Git commit until a source-to-upstream
  comparison supplies one.
- Imported source: `References/Lab/exploration_coverage/FUEL`
- Retained raw snapshot: 1,541 files, tree SHA-256
  `ef7d5ac53f0f9ba98209f0468c49b9130a7965060c768dae123da13e724dcc27`.
- Imported deliverable payload: 785 files, tree SHA-256
  `b43afd26242b170e1b0f249b39d78fa751c0b2d83b320c544bc6e719ae402d25`.
  It excludes four local `build` trees (including their nested `devel`
  outputs), three Python bytecode files, three local shared objects, three
  ignored LKH runtime-state files under `fuel_planner/utils/lkh_tsp_solver`,
  two prebuilt ELF files generated from `odom_visualization` source, 76
  Catkin/Dynamic Reconfigure generated message/configuration files, six editor
  backup files, and the generated `disturbance_ui.cfgc` bytecode. The source
  `disturbance_ui.cfg` definition remains in the payload.
- Last project commit affecting the retained imported path:
  `b3929f4c27005e0470d0d780c1e8c6c064f51b24`
  (`refs(fuel): add remaining odeint examples`, 2026-07-16).
- Root license: GPL-3.0, preserved in `LICENSE`. Individual bundled ROS
  packages and third-party resources require a release-license audit.

The 785-file deliverable payload is a byte-for-byte copy of the retained source
after the documented non-source exclusions. `.gitattributes`, `UPSTREAM.md`,
and `PATCHES.md` are migration metadata outside that payload. Its registry state
is `copied_pending_activation`: the legacy path remains the only active runtime
path until the ROS1 workspace, launch scripts, source revision, and license
audit are validated.
