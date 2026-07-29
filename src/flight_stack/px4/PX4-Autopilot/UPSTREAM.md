# PX4 Autopilot Source Provenance

- Canonical local source path:
  `src/flight_stack/px4/PX4-Autopilot`.
- Runtime snapshot source before migration:
  `/opt/mosim_work/sunray_px4` in `Ubuntu-20.04`.
- PX4 package version: `1.14.0`.
- Snapshot commit: `3c0f1446ec13fa199dcbfc5cf4bd6c24176806df`.
- License: BSD 3-Clause, retained in `LICENSE`.
- The snapshot includes the initialized MAVLink and Gazebo Classic submodule
  trees required by the existing Sunray SITL route.
- Migration excludes the top-level `.git`, `build`, `Documentation`, CI/editor
  metadata, and other generated or documentation-only payloads. Initialized
  nested submodule source trees, including their relative `.git` pointer files,
  are retained as frozen source provenance and do not point to the previous WSL
  source root. No PX4 flight source file was edited during the copy. The later
  source-activation compatibility patch is recorded separately in `PATCHES.md`.

This source is `copied_pending_activation`. Build output must be generated
under the project `build/` tree; no runtime path may depend on the previous
WSL source root or on `References/PX4/PX4`.
