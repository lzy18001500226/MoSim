# MoSim QGC Extension Provenance

- Imported source: `apps/flight_console/mosim`.
- This is project-owned QGroundControl custom-build source, not a separately
  cloned third-party repository. It owns MoSim QML/C++ pages, map assets,
  custom-build CMake inputs, and bridge declarations used to materialize the
  legacy QGroundControl `custom/` overlay.
- Imported payload: 15 files, 12,086,470 bytes, tree SHA-256
  `2b98e1588ef5636000cb6f310ce13c16d1079448a11d3a60f720f77bfa79d857`.
- The source has no independent license file. Its own redistribution terms and
  its interaction with QGroundControl's dual-license source must be audited
  before external delivery or canonical activation.
- Capture note: five tracked QML/C++ files and three Factory map data files
  were local worktree changes at capture time. They are intentionally retained
  byte-for-byte and are listed in `PATCHES.md`.

The registry state is `copied_pending_activation`. The legacy
`apps/flight_console/mosim` directory remains the only active extension source
until the materializer, build wiring, license decision, and controlled QGC
build check are audited.
