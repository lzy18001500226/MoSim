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
