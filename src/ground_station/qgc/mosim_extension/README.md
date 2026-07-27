# MoSim Custom Layer

This directory owns MoSim-specific QGroundControl pages, resources, adapters,
and custom-build generation inputs. Upstream source under `vendor/` is treated
as immutable.

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
overlay is materialized by `Scripts/ui/materialize_qgc_custom_overlay.py` and is
excluded from the immutable upstream digest. Do not edit the generated overlay.
