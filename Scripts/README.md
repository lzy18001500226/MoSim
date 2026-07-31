# Project Scripts

`Scripts/` contains reusable automation, validation, analysis, and runtime
entry helpers. Human double-click launchers belong in `cmd/`; evidence belongs
in `../Results/`.

| Area | Responsibility |
|---|---|
| `mworks/`, `mworks_live/`, `control_platform/` | MWORKS execution, code generation, controller integration, and analysis helpers |
| `sunray/`, `gazebo/`, `px4/`, `ros/`, `runtime/` | ROS1/Sunray/Gazebo/PX4 runtime and bounded diagnostics |
| `planning/`, `analysis/`, `results/` | planner helpers, metrics, plotting, extraction, and report-ready outputs |
| `quality/`, `tests/`, `hooks/` | deterministic checks, test coverage, preflight and safety guardrails |
| `UE5/`, `ui/` | UE bridge/display and application-support tools |
| `cmd/` | Curated Windows C99 baseline, Ground Control, and managed-stop entrypoints |
| `agent/`, `reference/`, `docs/`, `tools/`, `bat/`, `rflysim/` | notification, reference audit, documentation helpers, small utilities, compatibility, and external integration support |

Before adding a script, check whether an existing script, quality checker, or
workflow owns the same job. A one-off command belongs in the task log or an
existing runner, not as a new permanent project tool.
