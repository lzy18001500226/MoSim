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
snapshot because `apps/flight_console/mosim/README.md` defines it as generated
output of the MoSim custom-build source:

```text
apps/flight_console/vendor/qgroundcontrol/custom/
```

Its authoritative source, including current QML/C++ changes and Factory map
assets, is copied separately to `src/ground_station/qgc/mosim_extension`.
`android/.gradle/` is also excluded as Gradle cache. Neither exclusion modifies
or removes the retained legacy directory.

Before this component can become `canonical_active`, the migration task must:

1. recover or intentionally pin a QGroundControl upstream revision and record
   the applicable Apache/GPL distribution terms;
2. materialize the MoSim extension from its canonical source without editing
   the upstream snapshot directly;
3. replace the current Git-derived QGroundControl version behavior with an
   explicit reproducible build-version contract;
4. update only audited build and launcher references to the canonical paths;
5. run the declared static path checks and controlled QGC build/preflight; and
6. retain `apps/flight_console/vendor/qgroundcontrol` unchanged unless a later
   user-approved archival task says otherwise.
