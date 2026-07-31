# QGroundControl Source Provenance

- Upstream project: `https://github.com/mavlink/qgroundcontrol`.
- Imported source: `apps/flight_console/vendor/qgroundcontrol`.
- The retained source is an in-tree snapshot, not a nested Git checkout. Its
  exact upstream revision cannot be recovered from this directory; do not
  represent this copy as a pinned QGroundControl release. The last project
  baseline commit affecting the retained path before this copy was
  `22224f94079bb85a5de6f6856d5fd157bb68eee6`
  (`chore(ui): freeze QGroundControl flight console baseline`, 2026-07-17).
- License evidence: the retained tree contains both `LICENSE-APACHE` and
  `LICENSE-GPL`. The redistribution/build license selection must be audited
  before this component is delivered or activated.
- Imported payload: 2,638 files, 325,541,737 bytes, tree SHA-256
  `a8c7231105f1469ed703d45e33498c91562daa48f09755f07f6903bcc7a8e29c`.
  It is a byte-for-byte copy of the retained QGroundControl source after
  excluding `android/.gradle/` build cache and `custom/`, which is a generated
  MoSim overlay. `custom-example/` remains in the payload as QGroundControl
  source.
- The generated overlay is represented by the separate project-owned source
  snapshot at `src/ground_station/qgc/mosim_extension`. Its active materialized
  output is `src/ground_station/qgc/qgroundcontrol/custom`; the legacy output
  remains at `apps/flight_console/vendor/qgroundcontrol/custom` as rollback.
- Capture note: the retained QGroundControl worktree included a local change to
  `src/UI/MainWindow.qml`. It is retained byte-for-byte in this snapshot and is
  described in `PATCHES.md`.
- Build-layout contract: `cmake/Git.cmake` now accepts the explicit
  `QGC_APP_VERSION_OVERRIDE=0.0.0` and
  `QGC_SOURCE_SNAPSHOT_ID=mosim-source-snapshot` values. This prevents the
  source snapshot from inheriting the enclosing MoSim Git revision.
- Build preflight: the canonical source configured successfully on 2026-08-01
  through `Scripts/ui/build_flight_console.ps1 -ConfigureOnly`. It is not a
  full executable-build or runtime claim.

The registry state is `canonical_active`; the legacy vendor tree is retained
unchanged for provenance and rollback. The original upstream revision and
redistribution license choice remain unresolved external-delivery constraints.
