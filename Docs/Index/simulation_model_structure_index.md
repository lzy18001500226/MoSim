# Simulation Model Structure Index

> Maintained map for MoSim simulation models, scenario configs, runner scripts,
> and result locations.

Status: current structure snapshot, 2026-06-12 CST.

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
| `Models/MoSimQuadrotorModel/` | Formal project-owned quadrotor package surface | New accepted MoSim/Sunray150 model entries should become visible here after checks. |
| `Models/QuadrotorExperiments/` | Legacy/current implementation and compatibility pool | Still contains many executable scenario implementations and migration sources. Do not treat every legacy entry as final accepted surface. |
| `Models/QuadrotorControllerBlocks/` | Sysblock/controller block library | Controller source blocks used by closed-loop scenarios and formal controller wrappers. |
| `Config/scenarios/` | Scenario YAML configs | Configs connect a named scenario to model class, controller choice, runner settings, and result paths. |
| `Scripts/mworks/` | MWORKS/Sysplorer runner, check, extraction, and validation scripts | Use these for repeatable checks before claiming simulation evidence. |
| `Scripts/tests/` | Scripted regression and quality tests | Use for non-GUI validation and repeated evidence checks. |
| `Results/` | Reproducible outputs, metrics, logs, figures, packets, screenshots, and evidence bundles | Stable result locations should be recorded here; scratch output should not become a claim source without review. |
| `References/MWORKS/QuadrotorModel/` | Official/upstream MWORKS quadrotor baseline | Baseline/reference only. Do not silently modify as project-owned model work. |

## 3. Formal Package: `Models/MoSimQuadrotorModel/`

This is the user-facing target package for accepted MoSim quadrotor model
surfaces. It is currently partly an alias/wrapper layer over
`QuadrotorExperiments`; that is intentional during migration.

```text
Models/MoSimQuadrotorModel/
  package.mo
  package.order
  Baseline/
  Controllers/
  Dynamics/
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

`Models/MoSimQuadrotorModel/Dynamics/package.mo` is now a package shell. The
13 formal Dynamics entries listed in `package.order` are dedicated extends-only
`.mo` source files, with implementation provenance under
`Models/QuadrotorExperiments/DynamicsUpgrade/`.

## 4. Implementation Pool: `Models/QuadrotorExperiments/`

This package contains current and legacy implementation entries. It remains
important because many executable scenarios still live here.

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
| `FormationScenarios/` | Multi-UAV formation scenario implementations. Follow `Docs/Design/09_多机编队架构与数据设计.md` for identity, per-UAV result layout, and database boundaries before adding new formation entries. |
| `SystemArchitecture/` | Complete system graphical Sysblock and system-level failure scenarios. |
| `TraceIsolation/` | Diagnostic trace-isolation ladder; not a primary mission surface. |
| `SupportModels/` | Support and smoke models for trace/MCP/reference behavior. |

Do not delete or rename legacy entries casually. A formal migration needs:
source mapping, `check_model` plan, scenario/script reference update, and a
compatibility decision.

## 5. Controller Blocks: `Models/QuadrotorControllerBlocks/`

This directory contains reusable controller block models, including:

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

Backup/upgrade folders are historical artifacts. They are not the preferred
public controller surface unless a task explicitly reviews and promotes them.

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

Current 2026-06-11 live blocker:

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
`Docs/Design/09_多机编队架构与数据设计.md`:

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
  MoSimQuadrotorModel/
  QuadrotorExperiments/
  QuadrotorControllerBlocks/
```

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
Docs/Design/12_MoSimQuadrotorModel模型归档与迁移计划.md
Docs/Design/13_RflySim四旋翼模型对标与MoSim优化路线.md
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

## 11. Single-UAV Control Batch Before Formation

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
PID quality: needs_iteration, health=35.6257817116079
AWFF Sysblock quality: needs_iteration, health=36.043895052437605
AWFF vs PID RMSE improvement: 5.881%
worst phase for both scenarios: startup
fault-window AWFF RMSE improvement: 8.608%
```

This profile narrows the next single-UAV engineering focus to startup vertical
tracking plus rotor-loss recovery/fault-window behavior. It is not a new live
simulation and must not be used to claim controller improvement. Current live
AWFF/L1 full-rerun evidence is preserved as `needs_iteration`, not hidden.

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

## 12. Formation Structure Entry Point

The architecture entry point for future multi-UAV work is:

```text
Docs/Design/09_多机编队架构与数据设计.md
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
`Docs/Design/08_赛题闭环实现证据矩阵.md`. That evidence does not remove the
current engineering rule above: do not start new formation implementation work
until the selected single-UAV and MWORKS live gates needed for the next claim
are clean.
