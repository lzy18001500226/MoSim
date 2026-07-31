# MoSim QGC Extension Provenance

- Canonical source: `src/ground_station/qgc/mosim_extension/custom`.
- Retained compatibility snapshot: `apps/flight_console/mosim/custom`.
- This is project-owned QGroundControl custom-build source, not a separately
  cloned third-party repository. It owns MoSim QML/C++ pages, map assets,
  custom-build CMake inputs, and bridge declarations used to materialize the
  canonical QGroundControl `custom/` overlay.
- The generated overlay is materialized into
  `src/ground_station/qgc/qgroundcontrol/custom`.
- The source has no independent license file. Its own redistribution terms and
  its interaction with QGroundControl's dual-license source must be audited
  before external delivery or canonical activation.
- The old `apps/flight_console/mosim/custom` tree remains unchanged as an
  explicit rollback reference and must not be edited as a second source of
  truth.
- The QGroundControl source snapshot is `canonical_active`; this promotion does
  not resolve its upstream provenance or redistribution license status.
