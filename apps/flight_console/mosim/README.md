# MoSim Custom Layer

This directory is a retained compatibility snapshot of MoSim-specific
QGroundControl pages, resources, adapters, and custom-build inputs. It is not
the active source of truth.

Initial pages:

- Experiment
- Run Control
- Telemetry
- Injection
- Displays
- Evidence

All commands go through the MoSim Orchestrator. QML must not directly launch
ROS commands, publish MAVROS setpoints, or decide controller availability.

`custom/` is a retained compatibility snapshot. The canonical MoSim
custom-build source is `src/ground_station/qgc/mosim_extension/custom`; the
generated QGC overlay is materialized from that path into
`src/ground_station/qgc/qgroundcontrol/custom` by
`Scripts/ui/materialize_qgc_custom_overlay.py`. Keep this snapshot unchanged
as an explicit rollback reference.
