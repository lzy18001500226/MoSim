# MoSim Custom Layer

This directory owns MoSim-specific QGroundControl pages, resources, adapters,
and custom-build generation inputs. The active QGroundControl source host is
`src/ground_station/qgc/qgroundcontrol`; it is treated as an imported source
snapshot, so this extension remains separate from upstream files.

Initial pages:

- Experiment
- Run Control
- Telemetry
- Injection
- Displays
- Evidence

All commands go through the MoSim Orchestrator. QML must not directly launch
ROS commands, publish MAVROS setpoints, or decide controller availability.

`custom/` is the authoritative MoSim custom-build source. The generated QGC
overlay is materialized by `Scripts/ui/materialize_qgc_custom_overlay.py` into
`src/ground_station/qgc/qgroundcontrol/custom` and is excluded from the source
snapshot digest. Do not edit the generated overlay. The legacy vendor overlay
is retained only as a rollback snapshot.
