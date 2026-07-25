# Configuration

`Config/` stores machine-readable project configuration. It is not a location
for generated logs, experiment-specific source copies, or informal notes.

| Path | Responsibility |
|---|---|
| `controllers/`, `control_platform/`, `codegen/` | controller profiles, platform contracts, and code-generation configuration |
| `profiles/`, `scenarios/` | selectable ExperimentProfiles and scenario definitions |
| `planners/`, `plant/`, `gazebo/` | planning, vehicle/plant, and Gazebo-specific configuration |
| `capabilities/`, `protocol/`, `schemas/` | machine-readable capability, interface, and validation contracts |
| `rviz/` | current ROS1 review configuration |
| `ros2/`, `rviz2/` | future/reference routes; not the current Sunray ROS1 evidence lane |
| `legacy/` | compatibility and historical metadata; do not make it a new active dependency |

Keep configuration declarative. Scripts consume it, models implement it, and
`Results/` records its execution. Do not hard-code a new configuration copy
into a runner when an existing profile or scenario can be extended.
