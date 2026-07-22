# Simulation Model Structure Index

> Maintained map for MoSim simulation models, scenario configs, runner scripts,
> and result locations.

Status: current structure snapshot, 2026-07-22 CST.

Current authority rule:

```text
Models/MoSimQuadrotorModel/       sole active Modelica implementation and public entry root
Models/QuadrotorExperiments/      hidden compatibility aliases only
Models/QuadrotorControllerBlocks/ hidden compatibility aliases only
Models/MworksLive/                hidden compatibility aliases only
Docs/Cache/model_legacy/MworksLive_backup_20260722/  archived historical snapshot
```

All active Modelica implementations, scenario packages, controller Sysblocks,
dynamics, and realtime bridge resources now resolve under
`Models/MoSimQuadrotorModel/`. The three legacy roots remain only to preserve
existing callers while they are retired deliberately; no new source, scenario,
or formal entry may be added there. Later legacy paths in historical evidence
records remain provenance, not current opening instructions. The retirement
sequence is owned by the post-G7 R1 gate in
`Docs/Workflows/controller_evidence_closeout.md`: do not archive these three
facades before new-root experiment evidence, active-reference audit, and
post-archive smoke validation all pass.
This file answers two practical questions:

1. Where are the simulation files?
2. Which file should be updated when a model or simulation task changes the
   structure?

## 1. Update Rule

Every completed model or simulation task must update this file when it adds,
removes, renames, promotes, deprecates, or changes the meaning of any of these
items:

- MWORKS/Modelica package, class, or `.mo` model entry;
- scenario YAML under `Config/scenarios/`;
- repeatable simulation/check runner under `Scripts/mworks/` or
  `Scripts/tests/`;
- accepted result/evidence directory under `Results/`;
- formal-vs-legacy routing for a model entry point.

Do not update this index for transient logs, one-off scratch output, or raw
packet traffic unless they become a stable simulation evidence location.

## 2. Top-Level Storage Map

| Path | Role | Notes |
|---|---|---|
| `Models/MoSimQuadrotorModel/` | Sole active project-owned Modelica root | Contains controller, dynamics, missions, robustness, planning, formation, system, scene trace, `ExperimentRunner`, and `LiveIntegration`. New formal entries target this root only. |
| `Models/QuadrotorControllerBlocks/` | Hidden legacy Sysblock facade | Preserves prior flat class names through `extends` aliases; it contains no active source implementation. |
| `Models/QuadrotorExperiments/` | Hidden legacy scenario facade | Preserves prior experiment/scenario names through `extends` aliases; it contains no active source implementation. |
| `Models/MworksLive/` | Hidden legacy realtime facade | Preserves RT0/RT1 names through `extends` aliases; canonical live assets are under `MoSimQuadrotorModel.LiveIntegration`. |
| `Docs/Cache/model_legacy/MworksLive_backup_20260722/` | Dated MWORKS upgrade backup | Hash-verified historical copy; it is outside `Models/` and must not be loaded as a package. |
| `Config/scenarios/` | Scenario YAML configs | Configs connect a named scenario to model class, controller choice, runner settings, and result paths. |
| `Config/gazebo/` | Project-owned Gazebo validation scaffold | Single-UAV exported-controller validation world/model/sensor configs. Gazebo evidence is system-validation evidence, not MWORKS/Syslab competition metric evidence. |
| `Scripts/mworks/` | MWORKS/Sysplorer runner, check, extraction, and validation scripts | Use these for repeatable checks before claiming simulation evidence. |
| `Scripts/gazebo/` | Gazebo runner scripts | WSL-side bounded launch/preflight scripts for the current single-UAV Gazebo validation lane. |
| `Scripts/ros/` | ROS/bridge/local-map scripts and helpers | Includes replay publishers, setpoint adapters, and the first PointCloud2-to-voxel/local-grid adapter. ROS2-specific material is historical unless the route is explicitly reopened. |
| `Scripts/tests/` | Scripted regression and quality tests | Use for non-GUI validation and repeated evidence checks. |
| `Results/` | Reproducible outputs, metrics, logs, figures, packets, screenshots, and evidence bundles | Stable result locations should be recorded here; scratch output should not become a claim source without review. |
| `References/MWORKS/QuadrotorModel/` | Official/upstream MWORKS quadrotor baseline | Baseline/reference only. Do not silently modify as project-owned model work. |

## 2.1 G4 Current Model Entry Mapping and Non-destructive Refactor Contract

Status: G3 contract frozen and G4 static mapping completed. This section does
not claim a MWORKS run, graphical acceptance, or simulation result.

The planned G4 deliverable is:

```text
Config/control_platform/current_model_entry_map.json
```

It must contain exactly the 49 `scheme_id` values from
`Config/control_platform/control_scheme_catalog.json`, using the G1 inventory
only as source-candidate and blocker input. Its rows must retain the catalog
`entry_type` and declare one of these explicit states:

| Mapping state | Required meaning |
|---|---|
| `resolved_current_model` | `current_model_file` is a project-owned path below `Models/`, its Modelica class/name is recorded, and the G4 compatibility decision is recorded. This mapping alone does not authorize a MWORKS run. |
| `blocked_missing_current_model` | No current model entry is available. Record a stable blocker code and the source candidates inspected. |
| `not_applicable_runtime_baseline` | Reserved only for `px4ctrl`; it is a ROS1/PX4 engineering baseline, not an MWORKS graphical scheme. |

`Results/` files, including the existing model-operation catalog copies, are
historical evidence or source candidates only. They must never become the
`current_model_file` of a `resolved_current_model` row. The
`model_operation_catalog.json` remains an allowlisted Model Studio operation
catalog; it is not the 49-scheme current-model-entry registry and cannot grant
G4/G5 MWORKS eligibility by itself.

G4 is non-destructive: do not move, delete, overwrite, or silently rename an
existing `.mo` file. Preserve source paths and hashes, add a formal wrapper or
compatibility alias only when needed, update `package.order` and references in
the same change, then record the old-to-new decision in the mapping row. G4
does not open MWORKS, generate code, run Gazebo/ROS/UE, or claim a simulation
result. G5 starts only after the mapping checker and the existing G1 inventory
checker both pass.

The formal import surface for archived graphical controller cores is
`Models/MoSimQuadrotorModel/Controllers/GraphicalMIL/`. It is grouped by the
six nominal controller families and contains non-destructive package-context
copies only. A `GraphicalMIL` entry is a controller-core inspection target, not
a whole-aircraft model, not a runtime backend, and not automatic MWORKS run
authorization. Its source-derived package copy is generated as UTF-8 LF text
without line-end whitespace; only those formatting bytes may be canonicalized,
while declarations, equations, annotations and G5 layout changes remain
protected. Its exact source hash and import text are checked by:

```text
Scripts/quality/import_current_graphical_mil_models.py --check
Scripts/quality/build_current_model_entry_map.py --check
Scripts/quality/check_current_model_entry_map.py
```

G4 static mapping result: the checked map currently has 49 rows with
`46 resolved_current_model`, `2 blocked_missing_current_model` (`mu_synthesis`
and `neural_smc`), and one `not_applicable_runtime_baseline` (`px4ctrl`). It
contains 41 imported controller cores and five existing fixed integrated
whole-aircraft entries. All 49 rows remain `mworks_run_eligible=false`. D2 generates
`Config/control_platform/formal_closed_loop_harness_map.json`: 41 `GraphicalMIL` cores
remain `missing_closed_loop_harness` and may only receive an `internal_graphical_probe`,
while 5 fixed integrated chains are `resolved_canonical_whole_aircraft_harness` and may
enter a named formal whole-aircraft minimum closure. A bare `GraphicalMIL` core does not
gain an aircraft harness merely because its source file exists or opens. After G5 chooses a
nominal-family champion, its formal-root whole-aircraft harness must be added and validated
before seven-scenario A/B; a fixed integrated chain or historical result cannot substitute
for that champion-specific core/Adapter/plant binding. The active sequence is defined by
`Docs/Workflows/controller_evidence_closeout.md`.

## 3. Formal Package: `Models/MoSimQuadrotorModel/`

This is the sole formal project-owned package for active MoSim quadrotor model
surfaces, offline experiment entry points, and realtime bridge assets. Its
children hold the active implementations; the three old roots are hidden
compatibility facades only.
```text
Models/MoSimQuadrotorModel/
  package.mo
  package.order
  Baseline/
  Controllers/
  Dynamics/
  ExperimentRunner/
  Formation/
  LegacyCompatibility/
  Missions/
  Parameters/
  Planning/
  Robustness/
  SceneTrace/
  Support/
  System/
```

The current formal package responsibilities are:

| Namespace | Responsibility | Entry rule |
|---|---|---|
| `Baseline/` | Official example/chassis baseline aliases | Use for baseline comparison and plant identity. |
| `Controllers/` | Canonical controller-family and Sysblock namespaces | Holds the active controller source and graphical MIL entries. |
| `Dynamics/` | Canonical dynamics/actuator/wrench surfaces and diagnostic smoke models | Use these names for all new dynamics checks. |
| `ExperimentRunner/` | Typed offline controller interfaces, adapters, shared plant animation, and output-boundary runners | This is the current reusable offline execution surface; it is not a claim of runtime/PX4 equivalence. |
| `Formation/`, `Missions/`, `Planning/`, `Robustness/`, `SceneTrace/`, `System/` | Canonical scenario and system namespaces | Active scenario implementations live in these subpackages. |
| `LegacyCompatibility/` | Compatibility metadata | No executable primary implementation may be added here. |

Current high-priority dynamics entry surface:

```text
Models/MoSimQuadrotorModel/Dynamics/
  ActuatorCommandMapper.mo
  ActuatorMappedWrapperSurface.mo
  HoverSmoke.mo
  OptionalDampingGyroLayer.mo
  PhysicalWrenchHoverSmoke.mo
  PhysicalWrenchAdapter.mo
  PhysicalWrenchYawStepSmoke.mo
  RotorActuatorCore.mo
  RotorEffectivenessSmoke.mo
  WrapperSurface.mo
  WrapperHoverSmoke.mo
  WrapperYawStepSmoke.mo
  YawStepSmoke.mo
  package.mo
  package.order
```

Use this package when a task needs the formal MoSim model structure. Use
`Models/MoSimQuadrotorModel/package.order` and child `package.order` files to
inspect package-browser order.

`Models/MoSimQuadrotorModel/Dynamics/package.mo` is the active Dynamics package
shell. The 13 entries listed in `package.order` are canonical implementations;
`Models/QuadrotorExperiments/DynamicsUpgrade/` retains hidden compatibility
aliases only.
## 4. Legacy Scenario Compatibility: `Models/QuadrotorExperiments/`

This package contains hidden `extends` aliases for the former scenario and
dynamics names. It is retained only for compatibility with older calls and
historical records; no active implementation, new scenario source, or new
formal entry belongs in this tree.
```text
Models/QuadrotorExperiments/
  package.mo
  package.order
  ControllerBaselines/
  DynamicsUpgrade/
  FormationScenarios/
  OfficialScenarios/
  PlanningScenarios/
  RobustFaultScenarios/
  SceneTraceScenarios/
  SupportModels/
  SystemArchitecture/
  SystemModules/
  TraceIsolation/
```

Important subpackage roles:

| Subpackage | Role |
|---|---|
| `ControllerBaselines/` | PID, improved PID, enhanced PID, AWFF baseline controllers and comparison entries. |
| `DynamicsUpgrade/` | Sunray150/RflySim-style dynamics wrappers, actuator mapping, rotor-effectiveness smoke entries, and physical-wrench adapters. |
| `OfficialScenarios/` | Example1/2/3 official-route closed-loop scenario implementations with AWFF, INDI, L1, LinearMPC, and related variants. |
| `RobustFaultScenarios/` | Mass perturbation, wind gust, rotor-loss, safety, and return/land robustness scenarios. |
| `PlanningScenarios/` | Planning, navigation display, corridor/open-blocks, UE trace-table, and review/smoke entries. |
| `FormationScenarios/` | Multi-UAV formation scenario implementations. Follow `Docs/Design/架构/02_感知定位与规划集群/规划与编队控制接口.md` for identity, per-UAV result layout, and database boundaries before adding new formation entries. |
| `SystemArchitecture/` | Complete system graphical Sysblock and system-level failure scenarios. |
| `TraceIsolation/` | Diagnostic trace-isolation ladder; not a primary mission surface. |
| `SupportModels/` | Support and smoke models for trace/MCP/reference behavior. |

Do not delete legacy aliases casually. Any future retirement requires a
compatibility-reference audit, an explicit replacement decision, and targeted
`check_model` validation before the alias can be removed.

## 5. Legacy Controller Compatibility: `Models/QuadrotorControllerBlocks/`

This directory preserves hidden aliases for formerly flat controller block models, including:

```text
AWFF_AttitudeInnerLoop_Sysblock.mo
AWFF_FullController_Sysblock.mo
AWFF_FullControllerEquation_Sysblock.mo
AWFF_INDIControllerEquation_Sysblock.mo
AWFF_L1ResidualControllerEquation_Sysblock.mo
AWFF_LinearMPCOuterLoopControllerEquation_Sysblock.mo
AWFF_MotorMixer_Sysblock.mo
AWFF_PositionOuterLoop_Sysblock.mo
AWFF_QPNMPCSafetyController_Sysblock.mo
package.mo
package.order
```

The dated realtime upgrade backup is archived at
`Docs/Cache/model_legacy/MworksLive_backup_20260722/`; it is not a controller
or Modelica entry surface.

### 5.1 Canonical package boundary and opening decision

```text
Model Studio / offline profile
  -> MoSimQuadrotorModel.ExperimentRunner.Runners.*
  -> typed Adapter
  -> MoSimQuadrotorModel.Controllers.*
  -> MoSimQuadrotorModel.{Missions,Robustness,Planning,Formation,System}.*
  -> shared plant / result contract

MWORKS Live probe
  -> MoSimQuadrotorModel.LiveIntegration.RT0RealtimeProbe* or RTTelemetryScope50Hz
  -> native bridge resources under LiveIntegration/Resources
  -> realtime evidence only
```

Use the following decision rule when opening a model:

| User intent | First namespace to inspect | Do not infer |
|---|---|---|
| Open an offline model or scenario | `MoSimQuadrotorModel` | That source/static structure proves simulation success. |
| Inspect a reusable controller graph | `MoSimQuadrotorModel.Controllers` | That a graph has full-plant closed-loop evidence. |
| Run a named mission/scenario | `MoSimQuadrotorModel.Missions`, `Planning`, `Robustness`, or `Formation` | That a legacy alias is an alternative active implementation. |
| Inspect realtime MWORKS capability | `MoSimQuadrotorModel.LiveIntegration` | That an RT probe is an offline controller or flight acceptance. |
`Models/MoSimQuadrotorModel.ExperimentRunner` is a Modelica namespace, so the
filesystem path is `Models/MoSimQuadrotorModel/ExperimentRunner/`. The dot form
is used only when naming a class, for example
`MoSimQuadrotorModel.ExperimentRunner.Runners.AttitudeThrustRunner`.

## 6. Scenario Configs: `Config/scenarios/`

Scenario YAMLs are grouped by simulation intent:

```text
Config/scenarios/
  diagnostics/
  official/
  robustness/
  planning/
  formation/
  system/
```

Use these config directories to find runnable scenario identities before
opening model files. A valid simulation claim should connect:

```text
scenario YAML
  -> model class
  -> runner command
  -> raw output
  -> metrics/figures/report evidence
```

Current diagnostic scenario bindings:

```text
Config/scenarios/diagnostics/
  mosimquad_dynamics_hover_smoke.yaml
  mosimquad_dynamics_yaw_step_smoke.yaml
  mosimquad_dynamics_rotor_effectiveness_smoke.yaml
  mosimquad_dynamics_wrapper_hover_smoke.yaml
  mosimquad_dynamics_wrapper_yaw_step_smoke.yaml
  mosimquad_dynamics_physical_wrench_hover_smoke.yaml
  mosimquad_dynamics_physical_wrench_yaw_step_smoke.yaml
```

These YAML files are future-live smoke entry contracts for
`MoSimQuadrotorModel.Dynamics`. They are not controller-performance scenarios
and do not prove live MWORKS `check_model`, `SimulateModel`, result variables,
or closed-loop behavior until run under an authorized live MWORKS task.

Current live-load strategy for these diagnostics:

```text
model.live_load_strategy: minimal_dynamics_only
generated load tree:
  Results/generated_mworks/minimal_dynamics_only/QuadrotorExperiments/package.mo
  Results/generated_mworks/minimal_dynamics_only/MoSimQuadrotorModel/package.mo
```

The generated tree is a runner-created live-load surface used only to avoid
re-entering the full `Models/MoSimQuadrotorModel/package.mo` dependency graph
while smoke-checking the formal Dynamics entries. It must not replace the
formal source tree under `Models/`.

Current postprocess strategy for these diagnostics:

```text
postprocess_profile: diagnostics_smoke
runner variable profile: diagnostics_declared
runner metrics profile: diagnostics_smoke
```

The formal Dynamics smoke outputs are actuator/dynamics/wrench diagnostic
series, not trajectory-control series. The runner therefore exports only
`time` plus scenario-declared `result.extra_variables`, writes
`claim_role=dynamics_smoke_only` metrics, and creates a diagnostics smoke
postprocess summary instead of trajectory figures/replay. Do not route these
outputs through tracking RMSE, controller-performance, or replay acceptance
logic unless a later scenario explicitly adds the required trajectory columns
and changes the profile.

Historical 2026-06-11 live blocker:

```text
evidence:
  Results/mworks_model_hygiene/20260611_mosimquad_formal_dynamics_live_preflight/current_gui_sentinel_after_upgrade_classifier_20260611_234725.json

classification:
  status=incident_detected
  error_kind=gui_blocked
  license_state_hint=upgrade_model_surface_blocked
  upgrade_model_window_count=1
  all_window_license_gate=blocked
```

Do not run the live smoke batch while this blocker remains present. The
`[教育版]` main-window title is not enough to override an active `升级模型`
surface, and no automatic click/confirm/close/restart action is authorized.

Superseding live-gate note: the 2026-06-12 closeout gate records clean
preflight evidence, and the 2026-06-14 sentinel records `status=clean` with
`license_state_hint=no_mworks_window_observed`. That current no-window state
removes the old `升级模型` blocker as a current claim, but it is not proof of a
loaded reusable MWORKS session. Before any new live MWORKS execution, collect a
fresh bounded preflight and keep GUI result viewer/open flags disabled.

Executable-preparation guard:

```text
command:
  python Scripts/quality/check_mosimquad_formal_dynamics_live_smoke_readiness.py

outputs:
  Results/mworks_model_hygiene/20260611_mosimquad_formal_dynamics_live_smoke_readiness/live_smoke_readiness.json
  Results/mworks_model_hygiene/20260611_mosimquad_formal_dynamics_live_smoke_readiness/live_smoke_readiness.md

current expected status:
  ready_but_blocked_by_gui
```

This guard validates the future live smoke execution surface: seven scenario
YAMLs, deterministic raw/metrics/log paths, `extra_variables` coverage,
`minimal_dynamics_only` runner support, diagnostics-only result profiles,
`--no-gui-result-viewer`, `--no-gui-open`, and the current GUI blocker gate.
It does not run MWORKS or prove `check_model` / `SimulateModel`.

Future result-acceptance guard:

```text
command:
  python Scripts/quality/check_mosimquad_formal_dynamics_smoke_result_acceptance.py

outputs:
  Results/mworks_model_hygiene/20260611_mosimquad_formal_dynamics_smoke_result_acceptance/result_acceptance.json
  Results/mworks_model_hygiene/20260611_mosimquad_formal_dynamics_smoke_result_acceptance/result_acceptance.md

current expected status before live run:
  passed
current live result summary:
  scenario_count: 7
  present_result_count: 7
  missing_result_count: 0
  claim_role: dynamics_smoke_only
  metrics_profile: diagnostics_smoke
  row_count_per_smoke: 126
  non_finite_count: 0
```

After the 2026-06-12 authorized live smoke run, all seven formal Dynamics
diagnostic scenarios have MWORKS_MCP raw CSV, metrics JSON/CSV, and MCP JSONL
logs under `Results/diagnostics/mosimquad_formal_dynamics_smoke/`. This is
only actuator/dynamics/wrench smoke evidence. It validates `check_model`,
`SimulateModel`, readable scalar diagnostic exports, finite values, and the
automation/result path for those smoke surfaces. It does not prove trajectory
tracking, controller performance, mission success, or closed-loop acceptance.
The checker rejects leaked tracking/performance keys such as
`position_rmse_m` and `total_health_score`; smoke-local
`quality_status=smoke_only` / `quality_pass=true` metadata is allowed.

Live-unblock checklist:

```text
command:
  python Scripts/quality/build_mosimquad_formal_dynamics_live_unblock_checklist.py
current output:
  Results/mworks_model_hygiene/20260611_mosimquad_formal_dynamics_live_unblock_checklist/live_unblock_checklist.json
  Results/mworks_model_hygiene/20260611_mosimquad_formal_dynamics_live_unblock_checklist/live_unblock_checklist.md
current status:
  blocked_needs_user_or_pmo_ui_decision
```

This checklist is the handoff gate between the current `升级模型` GUI blocker
and a future bounded live smoke run. It requires fresh clean MWORKS evidence
before the prepared smoke command may run, and it explicitly forbids automatic
GUI click, close, restart, save, login, authorization, or model-upgrade
confirmation from an engineering task.

Static equation-invariant guard:

```text
command:
  python Scripts/quality/check_mosimquad_formal_dynamics_static_equation_invariants.py

outputs:
  Results/mworks_model_hygiene/20260611_mosimquad_formal_dynamics_static_equation_invariants/static_equation_invariant_check.json
  Results/mworks_model_hygiene/20260611_mosimquad_formal_dynamics_static_equation_invariants/static_equation_invariant_check.md
```

This guard verifies source anchors for the future-live smoke variables:
rotor-core thrust/moment equations, wrapper command-side gates, physical-wrench
adapter force/torque application, and single-rotor effectiveness monitors. It
explains variable meaning before live execution but still does not prove
runtime solvability.

## 7. MWORKS Runner And Validation Scripts

Primary MWORKS runner entry points:

```text
Scripts/mworks/run_mworks_scenario.py
Scripts/mworks/run_mworks_batch.py
Scripts/mworks/extract_mcp_timeseries.py
```

Current formal-package validation helpers include:

```text
Scripts/mworks/validate_mosimquad_rotor_actuator_core_surface.py
Scripts/mworks/validate_mosimquad_wrapper_surface.py
Scripts/mworks/validate_mosimquad_actuator_command_mapper_surface.py
Scripts/mworks/validate_mosimquad_actuator_mapped_wrapper_surface.py
Scripts/mworks/validate_mosimquad_physical_wrench_adapter_surface.py
Scripts/mworks/validate_mosimquad_optional_damping_gyro_surface.py
Scripts/mworks/validate_mosimquad_formal_smoke_surface.py
Scripts/mworks/validate_mosimquad_dynamics_batch_a_source_migration.py
Scripts/quality/check_mosimquad_formal_dynamics_smoke_scenarios.py
Scripts/quality/build_mosimquad_formal_dynamics_smoke_batch_manifest.py
```

Use project-local MWORKS skills and workflows before inventing new runner
logic:

```text
Docs/Skills/Mworks/mworks-model-context/SKILL.md
Docs/Skills/Mworks/mworks-simulation-evidence/SKILL.md
Docs/Skills/Mworks/mworks-runtime-diagnostics/SKILL.md
Docs/Workflows/run_simulation.md
Docs/Workflows/produce_simulation_evidence.md
```

## 8. Result And Evidence Locations

Stable result directories most relevant to simulation work:

```text
Results/official/
Results/robustness/
Results/planning/
Results/formation/
Results/system/
Results/model_checks/
Results/mworks_simulation/
Results/mworks_dynamics_upgrade/
Results/mworks_model_hygiene/
Results/mworks_model_hygiene/20260611_mosimquad_formal_dynamics_smoke_scenario_bindings/
Results/mworks_model_hygiene/20260611_mosimquad_formal_dynamics_smoke_batch_manifest/
Results/mworks_trace_consumption/
Results/identification/
Results/tuning/
Results/test_reports/
```

Use `Results/agent_packets/` only for task control-plane packets. It is not a
substitute for model files, simulation logs, metrics, figures, or screenshots.

Formation result directories must keep per-UAV evidence inspectable by
`uav_id`. New formation runs should follow the layout in
`Docs/Design/架构/02_感知定位与规划集群/规划与编队控制接口.md`:

```text
Results/formation/<scenario_id>/<run_id>/
  RUN_MANIFEST.json
  CONFIG_SNAPSHOT.yaml
  formation_reference.csv
  formation_metrics.json
  safety_events.json
  uav_<id>/
    raw.csv
    controller_trace.csv
    plant_truth.csv
    metrics.json
```

Do not accept a new formation result from animation, a merged trace without
`uav_id`, ROS2 topic presence alone, or a database row without raw trace and
manifest references.

## 9. How To Browse The Structure In The File Explorer

You can inspect the current model structure directly in the folder tree:

```text
Models/
  MoSimQuadrotorModel/       # sole active implementation root
  QuadrotorExperiments/      # hidden compatibility aliases
  QuadrotorControllerBlocks/ # hidden compatibility aliases
  MworksLive/                # hidden compatibility aliases
Docs/Cache/model_legacy/
  MworksLive_backup_20260722/ # archived; never load as a package
```

Open `Models/MoSimQuadrotorModel/` for all new work. The three sibling
compatibility roots exist only for old callers and should not be selected as
independent model libraries.
What the folder tree shows well:

- package grouping;
- visible `.mo` model files;
- formal vs legacy/current package split;
- scenario families and controller-block files.

What the folder tree does not show by itself:

- whether a model has passed `check_model` or `SimulateModel`;
- whether a legacy entry is accepted, deprecated, or only diagnostic;
- whether a result directory is report-ready evidence;
- whether a wrapper is an alias, an executable implementation, or a migration
  compatibility layer.

For those meanings, use this index plus:

```text
Docs/Design/架构/03_测试调参与证据/真机化与C++化.md
Docs/Cache/design/historical_snapshots/absorbed_or_superseded_20260614/12_MoSimQuadrotorModel模型归档与迁移计划.md
Docs/Cache/design/historical_snapshots/absorbed_or_superseded_20260614/13_RflySim四旋翼模型对标与MoSim优化路线.md
Docs/Index/project_work_memory_index.md
Docs/Workflows/new_conversation_context.md
```

## 10. Current Priority Model Thread

The current model-optimization line should start from:

```text
Models/MoSimQuadrotorModel/Dynamics/
```

and its implementation provenance in:

```text
Models/QuadrotorExperiments/DynamicsUpgrade/
```

Immediate smoke or validation candidates:

```text
MoSimQuadrotorModel.Dynamics.RotorActuatorCore
MoSimQuadrotorModel.Dynamics.WrapperSurface
MoSimQuadrotorModel.Dynamics.ActuatorMappedWrapperSurface
MoSimQuadrotorModel.Dynamics.PhysicalWrenchAdapter
MoSimQuadrotorModel.Dynamics.RotorEffectivenessSmoke
```

These names are candidate entry points, not accepted performance claims. Any
runtime success or controller-performance claim still requires the evidence
gate declared by the current workflow and task packet.

Current 2026-06-11 static status for the rotor-effectiveness line:

```text
source:
  Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150RflyStyleRotorDynamics.mo
  Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150DynamicsWrapperSurface.mo
  Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150ActuatorMappedWrapperSurface.mo
  Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150RotorEffectivenessSmoke.mo

validated static surfaces:
  Scripts/mworks/validate_mosimquad_rotor_actuator_core_surface.py
  Scripts/mworks/validate_mosimquad_wrapper_surface.py
  Scripts/mworks/validate_mosimquad_actuator_mapped_wrapper_surface.py
  Scripts/mworks/validate_mosimquad_formal_smoke_surface.py

formal source materialization:
  All 13 MoSimQuadrotorModel.Dynamics package-order entries are dedicated
  extends-only formal source surfaces. package.mo no longer carries inline
  model definitions.

claim boundary:
  static source and checker consistency only;
  no live MWORKS check_model, SimulateModel, GUI, result, or controller
  performance acceptance yet.
```

## 11. Gazebo + ROS2 Single-UAV Validation Lane (historical / bounded)

This section is retained as historical / bounded validation material. The
current executable review lane is Sunray ROS1 / Gazebo Classic / PX4 / MAVROS /
px4ctrl / RViz; use this section only when a task explicitly reopens the
ROS2/Gazebo validation branch.

Historical project-owned Gazebo+ROS2 smoke entry:

```text
Config/scenarios/system/sunray150_gazebo_ros2_smoke.yaml
Config/gazebo/worlds/yunzong_planning_test_sunray150_assembled.sdf
Config/gazebo/worlds/sunray150_takeoff_hover_land_plant_sanity.sdf
Config/gazebo/models/sunray150_assembled/model.sdf
Config/gazebo/models/sunray150_assembled/model.config
Config/gazebo/models/sunray150_assembled/meshes/sunray150_with_mid360_textured.obj
Config/gazebo/models/sunray150_assembled/meshes/sunray150_with_mid360_textured.mtl
Config/gazebo/sensors/mid360_lidar_imu.sdf
Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh
Scripts/gazebo/run_sunray150_takeoff_hover_land_gate.sh
Scripts/gazebo/run_sunray150_figure8_obstacle_gate.sh
Scripts/gazebo/check_gazebo_ros2_dependencies.sh
Scripts/gazebo/setup_gazebo_ros2_dependencies.sh
Scripts/ros/pointcloud_to_local_voxel_map_ros2.py
Scripts/ros/controller_output_to_gazebo_actuators.py
Scripts/ros/controller_output_to_gazebo_actuators_node.py
Scripts/ros/gazebo_fastlio_planner_input_adapter.py
Scripts/ros/gazebo_truth_hover_hold_controller.py
Scripts/ros/gazebo_truth_takeoff_hover_land_controller.py
Scripts/ros/publish_controller_output_fixture.py
Scripts/ros/mosim_msgs/msg/ControllerOutput.msg
Scripts/quality/audit_gazebo_sunray150_parameters.py
Scripts/quality/build_ue_truth_local_voxel_map_fixture.py
Scripts/quality/check_gazebo_ros2_smoke_contract.py
Scripts/quality/build_gazebo_ros2_runtime_status.py
Scripts/quality/evaluate_fastlio_truth_error.py
Scripts/quality/evaluate_gazebo_hover_hold_closed_loop.py
Scripts/quality/evaluate_gazebo_takeoff_hover_land.py
Scripts/quality/evaluate_figure8_obstacle_gate.py
Scripts/quality/evaluate_uav_dynamic_quality.py
Scripts/tests/test_gazebo_ros2_smoke_contract.py
Scripts/tests/test_pointcloud_to_local_voxel_map_core.py
Scripts/tests/test_ue_truth_local_voxel_map_fixture.py
Scripts/tests/test_controller_output_to_gazebo_actuators.py
Scripts/tests/test_fastlio_truth_error_eval.py
Scripts/tests/test_gazebo_hover_hold_closed_loop.py
```

Role:

```text
YunZong Gazebo obstacle world + MoSim assembled Sunray150 visible model
  -> Gazebo plant/world/sensors
  -> ros_gz_bridge
  -> ROS2 IMU + PointCloud2
  -> pointcloud_to_local_voxel_map_ros2.py
  -> /mosim/local_occupancy_voxels + /mosim/local_occupancy_grid
  -> ControllerOutput -> actuator_msgs/Actuators -> ros_gz_bridge
  -> FAST-LIO/planner input adapter for topic/frame/rate/input-shape gates
  -> later RViz2/planner/local-map review
  -> UE render/replay only for presentation
```

This lane has two distinct meanings and the distinction is mandatory:

| Surface | Current role | Claim boundary |
|---|---|---|
| Gazebo truth-feedback / ROS2 ControllerOutput fixtures | Plant, actuator, trajectory, point-cloud, local-map, and GUI/RViz pre-acceptance | Useful for debugging and runtime review; not generated MWORKS/PX4 deployment. |
| PX4-native generated-controller route | Formal external deployment validation target | Pending until generated C/C++, SIL, PX4 Offboard/uORB adapter, and same-run PX4+Gazebo gates pass. |

This lane therefore does not replace MWORKS/Syslab competition control metrics.
It also must not overclaim the Python/ROS2 fixture route as PX4 deployment.
Current scenario claim boundary explicitly forbids final `planner_ready`,
final `closed_loop`, generated-controller competition performance,
`fast_lio_localization_success` as a controller authority, and
`multi_uav_readiness` until the declared gates pass.
The UE truth/local-voxel fixture is retained as offline adapter-core evidence
only; it is not the main Gazebo world route and must not be used as a
replacement for Gazebo/RViz point-cloud or local-map runtime evidence.

Current 2026-06-20 accepted Gazebo pre-acceptance baselines:

| Gate | Evidence | Current accepted metrics | Boundary |
|---|---|---|---|
| Takeoff-hover-land dynamic quality | `Results/gazebo_ros2/longrun_takeoff_hover_land_xy_tight_20260620_0304/UAV_DYNAMIC_QUALITY_EVAL.json` | settled-hover XY displacement `0.03177m`; settled-hover max Z error `0.067371m`; landed-settle XY slide `0.000002m`; landed yaw delta `0.0rad` | Gazebo plant/controller pre-acceptance only. |
| Two-loop 8字/static-obstacle gate | `Results/gazebo_ros2/default_figure8_period32_same_run_map_20260620_0425/FIGURE8_STATIC_OBSTACLE_GATE.json` | figure-8 phase RMSE `0.096349m`; phase max XY error `0.215082m`; truth path-length ratio `1.150537`; center crossings `3`; truth clearance `0.459859m`; landing-window XY displacement `0` | Uses truth-feedback tracker; not generated MWORKS/PX4 deployment. |
| Same-run LiDAR/local occupancy review | `Results/gazebo_ros2/default_figure8_period32_same_run_map_20260620_0425/map_review/GAZEBO_ROS2_MAP_REVIEW.json` | raw LiDAR `20000` points/frame, finite sample `5306`; local voxels `464`; local grid `120x120`, occupied `354` | Runtime point-cloud/map review only; not planner_ready or localization closure. |

Formal generated-controller/PX4 artifacts:

```text
target model:
  Models/QuadrotorControllerBlocks/AWFF_FullController_Sysblock.mo
workflow:
  Docs/Workflows/mworks_codegen_controller_runtime.md
current passed codegen artifacts:
  Results/generated_mworks/AWFF_FullController_Sysblock_20260620_032747/CODEGEN_MANIFEST.json
  Results/generated_mworks/AWFF_FullController_Sysblock_20260620_032747/runtime_schema.json
  Results/generated_mworks/AWFF_FullController_Sysblock_20260620_032747/runtime_schema_smoke_check.json
  Results/generated_mworks/AWFF_FullController_Sysblock_20260620_032747/runtime_schema_constant_positive.json
  Results/generated_mworks/AWFF_FullController_Sysblock_20260620_032747/mworks_awff_fullcontroller_constant_reference.json
  Results/generated_mworks/AWFF_FullController_Sysblock_20260620_032747/sil_constant_input_check.json
blocked equation bridge:
  Models/QuadrotorControllerBlocks/AWFF_FullControllerEquation_Sysblock.mo
  reason: unsupported der() in Sysblock code generation path
missing before formal deployment claim:
  AWFF time-varying SIL equivalence report
  PX4+Gazebo baseline gate
  L1 Offboard or L2 PX4 module/uORB adapter evidence
  same-run PX4+Gazebo takeoff-hover-land and 8字/static-obstacle gates
```

Current assembled MID360 approximation:

```text
sensor config: Config/gazebo/models/sunray150_assembled/model.sdf
sensor fragment: Config/gazebo/sensors/mid360_lidar_imu.sdf
sensor type: Gazebo gpu_lidar, not Livox scan-mode plugin
topic: /mosim/gazebo/lidar_points -> /mosim/gazebo/lidar_points/points
rate: 10Hz
shape: 500 x 40 = 20,000 points/frame
horizontal FOV: 360 deg
vertical FOV: approximately -7 deg to 52 deg
scan range: 0.1 m to 40 m
claim boundary: density/FOV/range transport review only; no non-repetitive
Livox scan realism and no reflectivity-dependent range claim
```

Current plant parameter audit and plant-sanity gate:

```text
audit command:
  python Scripts/quality/audit_gazebo_sunray150_parameters.py
audit output:
  Results/gazebo_ros2/sunray150_assembled_parameter_audit_20260618/gazebo_parameter_consistency_audit.json
  Results/gazebo_ros2/sunray150_assembled_parameter_audit_20260618/GAZEBO_PARAMETER_CONSISTENCY_AUDIT.md
audit summary:
  row_count: 13
  adopted reviewed-assembly geometry rows: 6
  geometry_mismatches: []
  held_for_review: base_link.mid360_lidar.pose
  SDF total link mass: 0.69kg
  theoretical normalized hover command: 0.0556055205

accepted SDF geometry parameters:
  rotor centers: match Results/unreal_scene_mapping/sunray150_dae_assembly_parameters_20260604.json:sdf_rotor_mapping
  body collision pose: [0, 0.001574, 0.044965, 0, 0, 0]
  body collision size: [0.211502, 0.214651, 0.16193]

separate-source/runtime-validation rows:
  base_link.mass
  rotor_links.total_mass
  base_link.inertia
  MulticopterMotorModel rotor_set

plant sanity command:
  RESULT_DIR=Results/gazebo_ros2/sunray150_takeoff_hover_land_plant_sanity_20260618_004 bash Scripts/gazebo/run_sunray150_takeoff_hover_land_gate.sh
plant sanity world:
  Config/gazebo/worlds/sunray150_takeoff_hover_land_plant_sanity.sdf
plant sanity output:
  Results/gazebo_ros2/sunray150_takeoff_hover_land_plant_sanity_20260618_004/RUNTIME_STATUS.json
  Results/gazebo_ros2/sunray150_takeoff_hover_land_plant_sanity_20260618_004/GAZEBO_TAKEOFF_HOVER_LAND_EVAL.json
  Results/gazebo_ros2/sunray150_takeoff_hover_land_plant_sanity_20260618_004/RUN_MANIFEST.json
plant sanity status: passed
plant sanity metrics:
  duration_s: 13.032
  max_z_m: 0.836887
  final_z_m: 0.048684
  hover_mean_abs_z_error_m: 0.140992
  hover_max_abs_z_error_m: 0.234829
  max_xy_distance_m: 0.165252
  max_tilt_rad: 0.004286
claim boundary:
  proves only bounded Gazebo plant sanity: simple-controller takeoff, hover,
  and landing. Does not prove MWORKS controller deployment, competition
  controller performance, planner_ready, final closed_loop acceptance, UE
  acceptance, or multi-UAV readiness.
```

Static contract check:

```text
python Scripts/quality/check_gazebo_ros2_smoke_contract.py
python -m pytest Scripts/tests/test_gazebo_ros2_smoke_contract.py -q
python -m pytest Scripts/tests/test_pointcloud_to_local_voxel_map_core.py -q
python Scripts/quality/build_ue_truth_local_voxel_map_fixture.py
python -m pytest Scripts/tests/test_ue_truth_local_voxel_map_fixture.py -q
python Scripts/ros/controller_output_to_gazebo_actuators.py --command 0.5 0.5 0.5 0.5
python -m pytest Scripts/tests/test_controller_output_to_gazebo_actuators.py -q
```

Offline UE-truth local-map fixture:

```text
Results/gazebo_ros2/offline_ue_truth_local_voxel_map_fixture/UE_TRUTH_LOCAL_VOXEL_MAP_FIXTURE.json
Results/gazebo_ros2/offline_ue_truth_local_voxel_map_fixture/UE_TRUTH_LOCAL_VOXEL_MAP_FIXTURE.md
Results/gazebo_ros2/offline_ue_truth_local_voxel_map_fixture/factoryenvironmentcollect/local_voxel_map_fixture_frames.jsonl
Results/gazebo_ros2/offline_ue_truth_local_voxel_map_fixture/derelictcorridormegascans/local_voxel_map_fixture_frames.jsonl
```

This fixture translates existing UE scene-truth LiDAR points into each local
known-map frame by subtracting `local_known_map_frame.origin_m`, then exercises
the `pointcloud_to_local_voxel_map_ros2.py` core voxel/grid logic. It is
offline/core-only evidence. It does not prove ROS2 `PointCloud2`, Gazebo
runtime, TF, RViz, FAST-LIO, planner handoff, closed-loop behavior, controller
performance, or multi-UAV readiness.

WSL-side runner:

```bash
bash Scripts/gazebo/check_gazebo_ros2_dependencies.sh
DRY_RUN=1 bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh
bash Scripts/gazebo/setup_gazebo_ros2_dependencies.sh
RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_ACTUATOR_BRIDGE=1 RUN_LOCAL_MAP=1 RUN_TOPIC_CHECK=1 RUN_RATE_CHECK=1 RUN_STATIC_TF=1 RUN_TF_CHECK=1 TIMEOUT_SECONDS=20 bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh
RESULT_DIR=Results/gazebo_ros2/sunray150_gazebo_ros2_actuator_handoff RUNTIME_GATE_PROFILE=actuator_handoff RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_ACTUATOR_BRIDGE=1 RUN_CONTROLLER_COMMAND=1 RUN_ACTUATOR_COMMAND_CHECK=1 RUN_LOCAL_MAP=0 RUN_TOPIC_CHECK=0 RUN_RATE_CHECK=0 RUN_STATIC_TF=0 RUN_TF_CHECK=0 TIMEOUT_SECONDS=20 bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh
RESULT_DIR=Results/gazebo_ros2/sunray150_gazebo_ros2_controller_output_node_handoff RUNTIME_GATE_PROFILE=controller_output_node_handoff RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_ACTUATOR_BRIDGE=1 RUN_CONTROLLER_OUTPUT_NODE=1 RUN_CONTROLLER_OUTPUT_FIXTURE=1 RUN_ACTUATOR_COMMAND_CHECK=1 RUN_LOCAL_MAP=0 RUN_TOPIC_CHECK=0 RUN_RATE_CHECK=0 RUN_STATIC_TF=0 RUN_TF_CHECK=0 BUILD_MOSIM_ROS2_MSGS=0 TIMEOUT_SECONDS=20 bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh
RESULT_DIR=Results/gazebo_ros2/sunray150_gazebo_ros2_fastlio_planner_input RUNTIME_GATE_PROFILE=fastlio_planner_input RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_FASTLIO_PLANNER_INPUT_ADAPTER=1 RUN_TOPIC_CHECK=1 RUN_RATE_CHECK=1 RUN_STATIC_TF=1 RUN_TF_CHECK=1 bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh
RESULT_DIR=Results/gazebo_ros2/sunray150_gazebo_ros2_spark_fastlio_truth_eval RUNTIME_GATE_PROFILE=spark_fastlio_localization RUN_GAZEBO=1 RUN_ROS2_BRIDGE=1 RUN_FASTLIO_PLANNER_INPUT_ADAPTER=1 RUN_SPARK_FASTLIO=1 RUN_FASTLIO_TRUTH_EVAL=1 RUN_GAZEBO_TRUTH_POSE=1 RUN_TOPIC_CHECK=1 RUN_RATE_CHECK=0 RUN_STATIC_TF=1 RUN_TF_CHECK=1 TIMEOUT_SECONDS=20 bash Scripts/gazebo/run_sunray150_gazebo_ros2_smoke.sh
bash Scripts/gazebo/run_sunray150_hover_hold_closed_loop.sh
RESULT_DIR=Results/gazebo_ros2/gazebo_map_review_manual START_PAUSED=1 BACKGROUND=1 bash Scripts/gazebo/launch_gazebo_map_review.sh
```

Gazebo WSL GUI/runtime rules:

- `Scripts/gazebo/setup_gazebo_wsl_env.sh` is the shared WSL Gazebo environment
  wrapper. It defaults to WSLg NVIDIA D3D12 OpenGL and project-local
  `Config/gazebo/models` lookup only.
- `LIBGL_ALWAYS_SOFTWARE=1` is no longer the normal Gazebo GUI/runtime path.
  Use `MOSIM_GAZEBO_SOFTWARE_RENDERING=1` only for bounded fallback
  diagnostics.
- Do not inherit global `GZ_SIM_RESOURCE_PATH` or `IGN_GAZEBO_RESOURCE_PATH`
  unless a task explicitly sets `MOSIM_GAZEBO_INHERIT_RESOURCE_PATHS=1`.

Current output:

```text
Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_sensor_local_map/RUNTIME_STATUS.json
Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_sensor_local_map/RUN_MANIFEST.json
Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_map_review/RUNTIME_STATUS.json
Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_map_review/RUN_MANIFEST.json
Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_map_review/map_review/GAZEBO_ROS2_MAP_REVIEW.json
Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_map_review/map_review/figures/gazebo_lidar_pointcloud_3d.png
Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_map_review/map_review/figures/gazebo_local_occupancy_voxels_3d.png
Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_map_review/map_review/figures/gazebo_local_occupancy_grid_2d.png
Results/gazebo_review/yunzong_assembled_gui_capture/gazebo_full_world_20260615_175647.png
Results/gazebo_ros2/gazebo_map_review_20260615_gpu_path_003/launch_env.json
Results/gazebo_ros2/gazebo_map_review_20260615_gpu_path_003/glx_renderer.txt
Results/gazebo_ros2/gazebo_map_review_20260615_gpu_path_003/screenshots/gazebo_window_close_printwindow_1781531516.png
Results/gazebo_ros2/sunray150_gazebo_ros2_smoke/PREFLIGHT.json
Results/gazebo_ros2/sunray150_gazebo_ros2_smoke/TOPIC_CONTRACT.json
Results/gazebo_ros2/sunray150_gazebo_ros2_smoke/RUNTIME_STATUS.json
Results/gazebo_ros2/sunray150_gazebo_ros2_smoke/RUN_MANIFEST.json
Results/gazebo_ros2/sunray150_single_uav_competition_light_sensor_local_map_truth_20260618_007/RUNTIME_STATUS.json
Results/gazebo_ros2/sunray150_single_uav_competition_light_sensor_local_map_truth_20260618_007/RUN_MANIFEST.json
Results/gazebo_ros2/sunray150_gazebo_ros2_actuator_handoff/RUNTIME_STATUS.json
Results/gazebo_ros2/sunray150_gazebo_ros2_actuator_handoff/RUN_MANIFEST.json
Results/gazebo_ros2/sunray150_gazebo_ros2_controller_output_node_handoff/RUNTIME_STATUS.json
Results/gazebo_ros2/sunray150_gazebo_ros2_controller_output_node_handoff/RUN_MANIFEST.json
Results/gazebo_ros2/sunray150_gazebo_ros2_fastlio_planner_input/RUNTIME_STATUS.json
Results/gazebo_ros2/sunray150_gazebo_ros2_fastlio_planner_input/RUN_MANIFEST.json
Results/gazebo_ros2/sunray150_gazebo_ros2_fastlio_planner_input/fastlio_planner_input_adapter.json
Results/gazebo_ros2/sunray150_gazebo_ros2_spark_fastlio_truth_eval/RUNTIME_STATUS.json
Results/gazebo_ros2/sunray150_gazebo_ros2_spark_fastlio_truth_eval/RUN_MANIFEST.json
Results/gazebo_ros2/sunray150_gazebo_ros2_spark_fastlio_truth_eval/FASTLIO_TRUTH_ERROR_EVAL.json
Results/gazebo_ros2/sunray150_gazebo_ros2_spark_fastlio_truth_eval/fastlio_runtime/FASTLIO_RUNTIME_RECORDING.json
Results/gazebo_ros2/sunray150_gazebo_ros2_hover_hold_closed_loop_pre_acceptance_005/RUNTIME_STATUS.json
Results/gazebo_ros2/sunray150_gazebo_ros2_hover_hold_closed_loop_pre_acceptance_005/RUN_MANIFEST.json
Results/gazebo_ros2/sunray150_gazebo_ros2_hover_hold_closed_loop_pre_acceptance_005/GAZEBO_HOVER_HOLD_CLOSED_LOOP_EVAL.json
Results/gazebo_ros2/sunray150_gazebo_ros2_hover_hold_closed_loop_pre_acceptance_005/hover_hold_controller.json
Results/gazebo_ros2/dependency_check/DEPENDENCY_STATUS.json
Results/gazebo_ros2/dependency_check/DEPENDENCY_SETUP_PLAN.json
Results/gazebo_ros2/dependency_check/DEPENDENCY_SETUP_RESULT.json
Results/gazebo_ros2/single_uav_evidence_bundle_20260618/SINGLE_UAV_EVIDENCE_BUNDLE.json
Results/gazebo_ros2/single_uav_evidence_bundle_20260618/README.md
Results/gazebo_ros2/single_uav_evidence_bundle_20260618/figures/
```

`BLOCKER.json` appears only for blocked or dry-run attempts in a result
directory and is removed after a later successful gate in that directory.

Current 2026-06-15 dependency and runtime status:

```text
DEPENDENCY_STATUS.status: ready
gazebo_sim_cli_command: ign gazebo
gazebo_cli_version: 6.16.0
ros_gz_bridge_prefix: /opt/ros/humble
RUNTIME_STATUS.status: runtime_smoke_passed
RUN_MANIFEST.quality_status: runtime_smoke_passed
assembled YunZong sensor/local-map evidence: Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_sensor_local_map/RUNTIME_STATUS.json
assembled Gazebo GUI evidence: Results/gazebo_review/yunzong_assembled_gui_capture/gazebo_full_world_20260615_175647.png
assembled vehicle_id: sunray150_assembled
assembled LiDAR frame: sunray150_assembled/base_link/mid360_lidar
assembled LiDAR sample_point_count: 11520
assembled local voxels: /mosim/local_occupancy_voxels frame=map point_count=1213
assembled local grid: /mosim/local_occupancy_grid frame=map size=120x120
assembled static TF: map -> sunray150_assembled/base_link/mid360_lidar
assembled measured rates: IMU about 200.451Hz, LiDAR about 9.991Hz, local voxels about 3.837Hz
assembled map-review evidence: Results/gazebo_ros2/yunzong_planning_test_sunray150_assembled_map_review/map_review/GAZEBO_ROS2_MAP_REVIEW.json
assembled map-review preview point cloud: 11520 raw points, 7469 finite points
assembled map-review preview local voxels: 1222 finite occupied voxel points
assembled map-review preview local grid: 120x120, occupied_count=402
sensor/local-map immutable refresh: Results/gazebo_ros2/sunray150_single_uav_competition_light_sensor_local_map_truth_20260618_007/RUNTIME_STATUS.json
LiDAR PointCloud2 topic: /mosim/gazebo/lidar_points/points
LiDAR frame: sunray150/base_link/mid360_lidar
LiDAR sample_point_count: 11520
local voxels: /mosim/local_occupancy_voxels frame=map point_count=557 in the immutable refresh
local grid: /mosim/local_occupancy_grid frame=map size=120x120
static TF: map -> sunray150/base_link/mid360_lidar
measured rates in the immutable refresh: IMU about 191.742Hz, LiDAR about 9.568Hz, local voxels about 4.795Hz
actuator handoff: gate_profile=actuator_handoff, gate_passed=true
actuator expected velocity: [4000, 4000, 4000, 4000]
actuator ROS2 echo match: true
actuator Gazebo echo match: true
controller output node handoff: gate_profile=controller_output_node_handoff, gate_passed=true
controller output topic: /mosim/sunray150/controller_output
controller output command: [0.5, 0.5, 0.5, 0.5]
controller output adapter node status: published
controller output ROS2/Gazebo echo match: true
FAST-LIO/planner input gate: gate_profile=fastlio_planner_input, gate_passed=true
FAST-LIO outputs: /mosim/fastlio/livox/lidar, /mosim/fastlio/livox/imu
Sunray-compatible outputs: /uav1/livox/lidar, /uav1/livox/imu
planner input-shape outputs: /uav1/global_points, /mosim/planner/global_points, /uav1/sunray/gazebo_pose, /mosim/planner/odom
FAST-LIO input rates: IMU about 198.533Hz, LiDAR about 9.931Hz
adapter tf_lookup_failures: 0
FAST-LIO truth-error: gate_passed=true, matched_count=53, direct RMSE=0.042778m, origin-aligned RMSE=0.004144m, origin-aligned p95=0.006891m
FAST-LIO truth-error warning: absolute_timestamp_overlap_missing
hover-hold pre-acceptance: gate_passed=true, controller_samples=275, adapter_published=275, truth_samples=912, duration=15.48s
hover-hold altitude: final z error=0.353641m, max z error=0.705901m, min z=0.494099m, max z=1.002534m
hover-hold horizontal/attitude: max XY=0m, max tilt=0rad
single-UAV evidence bundle: status=single_uav_evidence_bundle_ready, drifted_gates=[], not_passed_gates=[]
```

These are bounded Gazebo+ROS2 validation results. The sensor/local-map profile
proves the Gazebo process, ros_gz bridge, PointCloud2 sample, same-run static
TF, local voxel output, local grid output, and measured topic rates for the
current lane. The actuator-handoff profile proves only bounded
ControllerOutput payload visibility on both the ROS2 actuator topic and the
Gazebo transport actuator topic. The controller-output node handoff profile
adds the ROS2 `mosim_msgs/msg/ControllerOutput` publisher-to-adapter-node path
before that same actuator echo check. The FAST-LIO/planner input-shape profile
adds bounded republishing of Gazebo MID360 LiDAR/IMU into MoSim and
Sunray-compatible FAST-LIO/planner input topics. They do not prove FAST-LIO
localization. The FAST-LIO truth-error profile adds estimator odometry versus
same-run Gazebo pose truth quality evidence for a bounded stationary smoke; it
does not prove planner handoff, setpoint publication, or flight authority. The
hover-hold profile adds a bounded single-UAV Gazebo truth-feedback
ControllerOutput-to-actuator loop pre-acceptance; it does not prove trajectory
tracking, final closed-loop acceptance, competition controller performance,
final command acknowledgement, or multi-UAV readiness.

YunZong/Sunray reference boundary:

```text
References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/
References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/sunray150_with_mid360.sdf
References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/meshes/150.dae
References/Sunray/simulation/sunray_simulator/models/sensor_models/livox_mid360/
References/Sunray/simulation/sunray_simulator/models/sensor_models/livox_mid360/livox_mid360.sdf
References/Sunray/simulation/sunray_simulator/models/sensor_models/livox_mid360/scan_mode/mid360.csv
References/Sunray/simulation/sunray_simulator/worlds/
References/Sunray/General_Module/sunray_planner_utils/
References/Sunray/External_Module/ego-planner-swarm/
References/Sunray/External_Module/FUEL/
References/Sunray/sunray_formation/
```

These paths can guide Sunray150 geometry, MID360 scan conventions, Gazebo
worlds, RViz layouts, EGO/FUEL parameters, formation patterns, and topic
contracts. Many YunZong/Sunray Gazebo assets are directly reusable as reference
structure, but they must enter through MoSim-owned adapter contracts. They are
reference material for the MoSim Fortress/ROS2 lane, not a license to
wholesale-copy the ROS1 launch/MAVROS/PX4/Gazebo Classic stack.

Current reuse rule:

```text
directly reusable after local verification:
  SDF/model/world/mesh/sensor fragments, scan patterns, RViz display layouts,
  planner/formation parameters, topic naming references

adapter-required before use:
  command topics, setpoint topics, controller nodes, planner outputs,
  FAST-LIO inputs/outputs, formation-control outputs

not authority for current MoSim claims:
  ROS1 launch stack, MAVROS/PX4 ownership, Gazebo Classic runtime status,
  upstream demo success, controller acceptance, planner readiness, closed loop
```

## 12. Single-UAV Control Batch Before Formation

The current pre-formation control batch is declared by:

```text
Results/mworks_model_hygiene/20260611_single_uav_control_batch_contract/single_uav_control_batch_contract.json
Results/mworks_model_hygiene/20260611_single_uav_control_batch_contract/single_uav_control_batch_contract.md
```

It covers 13 single-UAV scenarios:

- official step, helix, and figure-8 tracking;
- PID baseline, improved PID, AWFF Sysblock, AWFF+INDI, and linear MPC
  Sysblock controllers;
- single-rotor efficiency degradation and wind-gust robustness;
- no formation or multi-UAV scenarios.

Current read-only result acceptance is recorded by:

```text
Scripts/quality/check_single_uav_control_batch_result_acceptance.py
Scripts/tests/test_single_uav_control_batch_result_acceptance.py
Results/mworks_model_hygiene/20260611_single_uav_control_batch_result_acceptance/single_uav_control_batch_result_acceptance.json
Results/mworks_model_hygiene/20260611_single_uav_control_batch_result_acceptance/single_uav_control_batch_result_acceptance.md
```

Current result state:

```text
status: needs_iteration
present_result_count: 13
accepted_result_count: 11
needs_iteration_count: 2
iteration targets:
  Config/scenarios/robustness/example1_rotor1_loss15_pid_baseline.yaml
  Config/scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml
```

This means the single-UAV evidence chain is structurally consumable, but the
single-rotor 15% efficiency-loss robustness slice remains the next engineering
optimization target. Existing raw/metrics/log artifacts may be historical
evidence; this read-only checker does not prove that the current turn ran live
MWORKS.

The smallest current pre-formation rerun/iteration entry is:

```text
Scripts/quality/build_rotor1_loss15_iteration_plan.py
Scripts/tests/test_rotor1_loss15_iteration_plan.py
Results/mworks_model_hygiene/20260611_rotor1_loss15_iteration_plan/rotor1_loss15_iteration_plan.json
Results/mworks_model_hygiene/20260611_rotor1_loss15_iteration_plan/rotor1_loss15_iteration_plan.md
```

Current plan status no longer depends on the stale 2026-06-11 upgrade-model
sentinel. The current post-simulation preflight sentinel is clean:

```text
Results/mworks_model_hygiene/20260612_post_simulation_preflight/current_gui_sentinel.json
status: clean
live gate: clean_preflight_available
blocking_mworks_window_count: 0
upgrade_model_window_count: 0
```

The current AWFF/L1 direct-actuator smoke reruns fixed the initial
roll/pitch-divergence topology problem, but the full 50 s AWFF Sysblock and
L1 fault-allocation reruns still classify as `needs_iteration`. Do not use
those two reruns as accepted robustness evidence.

If report wording needs a refreshed baseline comparison, rerun only:

```text
Config/scenarios/robustness/example1_rotor1_loss15_pid_baseline.yaml
Config/scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml
```

with `--no-gui-result-viewer`, `--no-gui-open`, `--continue-on-failure`, and
`--allow-needs-iteration`, then rerun the result acceptance checker before
changing controller parameters or entering formation work.

The current offline error-profile diagnostic for the same two scenarios is:

```text
Scripts/quality/profile_rotor1_loss15_error.py
Scripts/tests/test_rotor1_loss15_error_profile.py
Results/mworks_model_hygiene/20260611_rotor1_loss15_error_profile/rotor1_loss15_error_profile.json
Results/mworks_model_hygiene/20260611_rotor1_loss15_error_profile/rotor1_loss15_error_profile.md
```

Current profile summary:

```text
status: diagnostic_profile_ready
source: existing historical raw/metrics artifacts only
live_mworks_touched: false
PID quality: needs_iteration, health=18.80013043497445
AWFF Sysblock quality: needs_iteration, health=0.0
AWFF vs PID RMSE improvement: -380160.329%
PID worst phase: startup
AWFF Sysblock worst phase: late_tracking
fault-window AWFF RMSE improvement: -129053.802%
```

This profile narrows the next single-UAV engineering focus to startup vertical
tracking for the baseline and a severe plain AWFF Sysblock failure that grows
through the fault-window, recovery, and late-tracking phases. It is not a new
live simulation and must not be used to claim controller improvement. Current
plain PID/AWFF/L1-style rows remain preserved as `needs_iteration`, not hidden.

The broader pure rotor1_loss15 controller candidate matrix is:

```text
Scripts/quality/build_rotor1_loss15_candidate_matrix.py
Scripts/tests/test_rotor1_loss15_candidate_matrix.py
Results/mworks_model_hygiene/20260611_rotor1_loss15_candidate_matrix/rotor1_loss15_candidate_matrix.json
Results/mworks_model_hygiene/20260611_rotor1_loss15_candidate_matrix/rotor1_loss15_candidate_matrix.md
```

Current matrix summary after 2026-06-12 current-rerun refresh:

```text
status: ready_with_accepted_candidates
scenario_count: 11
accepted_candidate_count: 1
needs_iteration_or_unverified_count: 10
best_rmse_candidate:
  controller_id: linear_mpc_online_fault_allocation_sysblock
  scenario: Config/scenarios/robustness/example1_rotor1_loss15_linear_mpc_online_fault_allocation_sysblock.yaml
  position_rmse_m: 0.1675687242474305
  steady_state_error_m: 0.1309865010516861
  disturbance_recovery_time_s: 2.490000000000002
  total_health_score: 62.536015057605155
  quality_rmse_improvement_pct: 46.64112813132643
```

Use this matrix to select the current single-UAV rotor-loss robustness
direction. Plain PID/AWFF rotor1_loss15 rows remain useful baseline/negative
evidence but must not be promoted as passing robustness evidence. Current
direct-actuator reruns of AWFF/L1-style candidates remain preserved as
`needs_iteration`. The current accepted candidate is the LinearMPC online fault
allocation Sysblock branch, which was rerun under the clean 2026-06-12
MWORKS/preflight evidence path and produced current raw, metrics, figures, and
replay artifacts.

Current accepted candidate evidence:

```text
scenario:
  Config/scenarios/robustness/example1_rotor1_loss15_linear_mpc_online_fault_allocation_sysblock.yaml
controller:
  Models/QuadrotorControllerBlocks/AWFF_LinearMPCOnlineFaultAllocationController_Sysblock.mo
raw:
  Results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_linear_mpc_online_fault_allocation_sysblock/raw/robust_rotor1_loss15_example1_linear_mpc_online_fault_allocation_sysblock.csv
metrics:
  Results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_linear_mpc_online_fault_allocation_sysblock/metrics/robust_rotor1_loss15_example1_linear_mpc_online_fault_allocation_sysblock.json
figures:
  Results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_linear_mpc_online_fault_allocation_sysblock/figures/
replay:
  Results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_linear_mpc_online_fault_allocation_sysblock/replay/robust_rotor1_loss15_example1_linear_mpc_online_fault_allocation_sysblock.json
source:
  MWORKS_MCP
quality:
  pass
row_count:
  25001
quality_checked_at:
  2026-06-12T05:32:10
```

The current pre-multi-UAV single-UAV closeout gate is:

```text
Scripts/quality/build_single_uav_pre_multi_uav_closeout_gate.py
Scripts/tests/test_single_uav_pre_multi_uav_closeout_gate.py
Results/mworks_model_hygiene/20260611_single_uav_pre_multi_uav_closeout_gate/single_uav_pre_multi_uav_closeout_gate.json
Results/mworks_model_hygiene/20260611_single_uav_pre_multi_uav_closeout_gate/single_uav_pre_multi_uav_closeout_gate.md
Results/mworks_model_hygiene/20260612_single_uav_pre_multi_uav_closeout_gate/single_uav_pre_multi_uav_closeout_gate.json
Results/mworks_model_hygiene/20260612_single_uav_pre_multi_uav_closeout_gate/single_uav_pre_multi_uav_closeout_gate.md
```

Current gate state after 2026-06-12 current-rerun refresh:

```text
status: single_uav_gate_ready_for_ue_prep
decision: prepare_ue_replay_inputs_directly_when_user_authorized
reason:
  MWORKS live gate uses the current clean post-simulation sentinel.
  13-scenario batch has 11 accepted rows and 2 plain rotor1_loss15 rows needing iteration.
  Rotor1-loss candidate matrix has 1 current accepted allocation/isolation candidate.
  The selected accepted candidate has current MWORKS_MCP raw/metrics evidence after the clean sentinel.
  Formal Dynamics smoke has 7/7 MWORKS_MCP diagnostics-smoke results accepted.
```

This MWORKS closeout gate allowed source-static UE replay/render input
preparation for the selected accepted run. By itself it did not authorize UE
editor/runtime/build work, did not claim UE runtime success, and did not start
multi-UAV formation. Later UE build-only and bounded runtime replay ingest
evidence is recorded separately below.
PMO/report review still decides whether this current candidate is enough for
design transition language. If report wording needs refreshed baseline
comparison, rerun only the two plain PID/AWFF rotor1_loss15 baseline rows and
refresh acceptance before writing comparative conclusions.

Current source-static UE replay input preparation for this accepted run is:

```text
Scripts/UE5/build_mworks_accepted_run_ue_replay_input_bundle.py
Scripts/tests/test_mworks_accepted_run_ue_replay_input_bundle.py
Scripts/UE5/smoke_mworks_accepted_run_ue_state_stream_loopback.py
Scripts/tests/test_mworks_accepted_run_ue_state_stream_loopback.py
Scripts/quality/check_ue_truth_replay_contract.py
Scripts/tests/test_ue_truth_replay_contract.py
Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_replay_input_bundle.json
Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_replay_input_bundle.md
Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_state_stream_loopback.json
Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_state_stream_loopback.md
Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/received_ue_state_packets.jsonl
Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_stage_progress_summary.json
Results/ue_build/20260612_102452_mosim_scene_library_editor_build/build_manifest.json
Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/sunray150_runtime_static_mesh_import_20260612_1100.json
Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_runtime_probe_20260612_1105/ue_runtime_replay_probe_summary.json
Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_runtime_probe_20260612_1105/screenshots/capture_manifest.json
Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_runtime_probe_20260612_1105/screenshots_after_stream/capture_manifest.json
Results/unreal_scene_mapping/UE_TRUTH_REPLAY_CONTRACT_CHECK.json
Results/unreal_scene_mapping/UE_TRUTH_REPLAY_CONTRACT_CHECK.md
```

Current UE input bundle, local state-stream loopback, build-only, and bounded
runtime replay status:

```text
bundle_status: ready_for_source_static_ue_replay_input
source_static_only: true
bundle_ue_editor_opened: false
bundle_ue_runtime_started: false
bundle_udp_sent: false
scene_id: robust_rotor1_loss15_example1
map_id: local_factoryenvironmentcollect
stream dry-run packet types:
  hello
  frame
  end
loopback_ok: true
loopback_udp_sent_to_local_socket: true
loopback_received_packets: 10
loopback_received_frames: 8
mworks_started_by_loopback: false
ros2_started_by_loopback: false
not_runtime_ue_ack: true
build_only_status: build_passed
build_only_ue_runtime_started: false
runtime_replay_probe_status: runtime_ingest_and_visual_uav_visible_pass
runtime_replay_frames_sent: 120
runtime_replay_factory_scene_visible: true
runtime_replay_udp_first_frame_received: true
runtime_replay_sunray_first_frame_applied: true
runtime_replay_sunray_visible: true
runtime_replay_sunray_hidden_in_game: false
runtime_replay_sunray_bounds_nonzero: true
ue_truth_replay_contract_status: ue_truth_replay_static_ready_runtime_blocked_or_degraded
ue_truth_replay_contract_factory_path_cells: 34
ue_truth_replay_contract_factory_lidar_points: 1934
ue_truth_replay_contract_derelict_path_cells: 45
ue_truth_replay_contract_derelict_lidar_points: 2068
ue_truth_replay_runtime_ready: false
ue_truth_replay_runtime_blocker: unreal_editor_listener_unavailable
```

The bundle validates the replay input contract for
`Scripts/UE5/stream_unreal_udp.py`; the loopback smoke proves those
`quadrotor.unreal_state.v1` packets can pass through a real local UDP socket.
The build-only manifest proves the renderer project compiled for this gate
without starting UE runtime. The bounded runtime replay probe proves UE runtime
ingested the accepted MWORKS state stream and UE logs report the imported
Sunray150 StaticMesh as visible with nonzero bounds. It is not authoritative
command-echo acknowledgement, not final/manual visual acceptance, not
ROS2/FAST-LIO evidence, not controller performance from UE, not final material
acceptance, and not multi-UAV readiness.

`Scripts/quality/check_ue_truth_replay_contract.py` is the current aggregate
file-level gate for UE truth/replay prep. It checks Factory and Derelict
scene truth occupancy, render replay, local known-map frames, local plan frames,
LiDAR point frames, FAST-LIO replay input handoff, MWORKS-vs-UE scene-truth
collision, and the accepted MWORKS run's UE replay/loopback/runtime-ingest
evidence. A pass
means the file contract is ready for downstream UE/ROS2/Gazebo preparation; it
does not start UE/MWORKS/ROS2/Gazebo/RViz/FAST-LIO and does not prove runtime
success, `planner_ready`, `closed_loop`, controller performance from UE,
material acceptance, or multi-UAV readiness.

## 13. Formation Structure Entry Point

The architecture entry point for future multi-UAV work is:

```text
Docs/Design/架构/02_感知定位与规划集群/规划与编队控制接口.md
```

It defines these stable formation contracts:

- `SwarmRunManager` for run-level and member-level identity binding;
- `FormationManager` for leader-follower, virtual-structure, or later
  decentralized references;
- `InterUAVSafetyLayer` for minimum-distance, geofence, stale-reference, and
  emergency status labels;
- `FormationMetrics` for post-run per-UAV and formation-level evaluation;
- no runtime database dependency for the first MWORKS-hosted formation route.

Current accepted historical C2 evidence is recorded separately in
`Docs/Design/赛题.md`. That evidence does not remove the
current engineering rule above: do not start new formation implementation work
until the selected single-UAV and MWORKS live gates needed for the next claim
are clean.
