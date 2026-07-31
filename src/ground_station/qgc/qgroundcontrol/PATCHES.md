# MoSim Patch Record

No QGroundControl source, build, packaging, resource, configuration, or test
file was changed while copying this component into
`src/ground_station/qgc/qgroundcontrol`.

The imported payload deliberately includes the pre-existing local working-tree
change in:

1. `src/UI/MainWindow.qml`

It is a retained MoSim UI snapshot, not a migration edit. A later activation
task must extract and review it as an explicit patch against a known upstream
QGroundControl revision.

The following legacy directory is intentionally not part of this upstream
snapshot because it is the retained rollback output of the MoSim custom-build
source:

```text
apps/flight_console/vendor/qgroundcontrol/custom/
```

Its authoritative source, including current QML/C++ changes and Factory map
assets, is copied separately to `src/ground_station/qgc/mosim_extension`; the
active generated overlay is materialized under this canonical QGC source tree.
`android/.gradle/` is also excluded as Gradle cache. Neither exclusion modifies
or removes the retained legacy directory.

On 2026-08-01, the QGC source was activated at
`src/ground_station/qgc/qgroundcontrol`: the overlay materialization path,
source manifest, build entrypoint, and version fallback were switched to the
canonical snapshot. The source manifest and configure-only build preflight
passed. `apps/flight_console/vendor/qgroundcontrol` remains unchanged as a
rollback and provenance snapshot.

Remaining external-delivery boundaries are upstream revision recovery, license
selection, full executable build on the target machine, and separately owned
QGC/ROS/Gazebo runtime validation.
