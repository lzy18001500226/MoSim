# cmake_utils Source Provenance

- Upstream repository family: Fast-Drone-250 utility package.
- Imported source:
  `References/Lab/planning_local/Fast-Drone-250/src/utils/cmake_utils`.
- Retained source payload: nine CMake/package files copied byte-for-byte.
  The package declares `LGPLv3`; no separate license text is present in the
  retained source tree.
- Relationship: `uav_utils` requires this catkin package during controller
  workspace configuration. The package is a CMake-module distributor and does
  not introduce a planner, simulator, or runtime executable.

Its registry state is `copied_pending_activation` until the local controller
profile configures and builds against this package from `src`.
