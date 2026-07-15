# Skybrush

Status: REFERENCE / swarm management, ground-station, and experiment-platform
candidate; not a planner authority.

Source: `References/Lab/experiment_platforms/skybrush-server`.

Inputs: mission/trajectory definitions, vehicle registry, telemetry, status
events, operator commands and server configuration.

Outputs: swarm management state, operator-facing mission status, visualization
or coordination messages, and possible launch/orchestration references.

FAST-LIO dependency: none. Skybrush is a management/display reference, not a
localization source.

Control boundary: Skybrush concepts must not bypass MoSim's Orchestrator,
ExperimentProfile, Planner Adapter, Trajectory Server, controller or PX4/MAVROS
gates. It is a reference for UI/server organization and cluster status, not a
replacement for runtime control evidence.

MoSim use: reference for QGC secondary development, experiment launcher, swarm
status board, trajectory preview, mission import/export and operator review.
If a separate frontend is built, use Skybrush to study how a swarm server
separates mission state, telemetry, UI updates and safety limits.

Validation if opened: first build a source-level UI/server concept map, then
connect only to recorded MoSim logs or dry-run ExperimentProfiles. Live vehicle
or simulator command forwarding requires an explicit user-approved runtime
gate.

Forbidden claims: Skybrush server review is not autonomous exploration, not
multi-UAV planning success, not Gazebo/PX4 runtime success and not controller
evidence. It cannot make UE/QGC/frontend the authority for map, localization,
planner or controller success.
