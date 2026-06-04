# Project Work Memory Index

> Purpose: recover the important work history of the long MoSim conversation
> without loading the old multi-GB chat/session file.

Status: current recovery index, 2026-06-04 CST.

This index is a routing document. It does not make historical chat facts
authoritative. For each topic, use the linked current docs, manifests, result
files, and cache audits. If a remembered item is not listed here or in a linked
source, route it through `Docs/Workflows/session_memory_migration.md` before
using it as project truth.

## 1. How To Use This Index

Start a fresh conversation with:

```text
1. AGENTS.md
2. Docs/Workflows/new_conversation_context.md
3. Docs/Index/project_work_memory_index.md
4. The one topic-specific source listed below
```

Do not read raw Codex session JSONL files or old chat dumps as routine context.
They contain many superseded parameters, failed attempts, and rejected routes.

When sources disagree, use this order:

```text
1. Current project files, manifests, scripts, model files, and test output.
2. Current formal design/workflow docs.
3. Result/evidence bundles and manual-review packets.
4. Cache audits under Docs/Cache/session_memory_migration/.
5. PROGRESS.md latest entries.
6. Old chat/session memory.
```

## 2. Current Mainline

The current MoSim technical mainline is:

```text
MWORKS/Sysplorer/Syslab
  -> dynamics, controller, generated C/C++ controller runtime, truth, metrics
UE5 / MoSimSceneLibrary
  -> high-quality scene rendering, UAV visual, camera, collision/sensor oracle
ROS2 / RViz2 / FAST-LIO
  -> LiDAR/IMU/TF transport, native point-cloud/map/localization review
CoAgent / WeChat
  -> sparse progress, task coordination, human-intervention channel
```

Do not resume the rejected toy route:

```text
keyboard grid-cell movement
fake/static point cloud
2D-only grid map as product evidence
HTML/browser active point-cloud review
primitive cube/cylinder UAV visual
MWORKS STL/runtime animation as UE vehicle route
```

## 3. Workstream Index

| Workstream | Current Status | First Read | Evidence / Cache | Do Not Resume |
|---|---|---|---|---|
| New conversation recovery and memory migration | Short startup doc exists; full migration is cache-first and three-round-gated | `Docs/Workflows/new_conversation_context.md`, `Docs/Workflows/session_memory_migration.md` | `Docs/Cache/session_memory_migration/coverage_matrix_20260604.md`, `Docs/Cache/session_memory_migration/completion_audit_20260604.md` | raw old session as truth; promoting chat-only numeric claims |
| Codex App / VSCode / WSL session and config repair | Infrastructure history is documented; do not touch external `.codex` state unless user explicitly requests infrastructure repair | `Docs/Index/codex_app_session_research.md`, `Docs/Workflows/debug_mcp.md` | `Docs/Cache/session_memory_migration/round2_infrastructure_memory_20260604.md` | assuming App/VSCode live sync is durable state; normalizing SQLite/JSONL injection |
| CoAgent architecture and multi-dialog task system | Design/implementation history exists but runtime expansion is gated; MoSim technical mainline is not CoAgent implementation now | `CoAgent/README.md`, `CoAgent/STATUS.md`, `CoAgent/docs/architecture/README.md` | `Docs/Cache/session_memory_migration/round2_coagent_operating_memory_20260604.md`, `Results/agent_packets/` | hidden sub-agent as durable department; shadow-home transport as visible communication proof |
| Technical enterprise operating model | Enterprise/project-management philosophy was documented as design input for CoAgent and task governance | `CoAgent/docs/architecture/technical_enterprise_operating_system.md`, `CoAgent/docs/architecture/enterprise_to_agent_mapping.md`, `CoAgent/docs/architecture/task_intake_and_governance.md` | `CoAgent/docs/architecture/coagent_problem_driven_operating_model.md`, `CoAgent/docs/architecture/coagent_dynamic_task_team_v2_design.md` | treating fixed departments as the whole architecture; ignoring task-oriented dynamic teams |
| External agent/project learning | Reference projects are classified and audited for patterns, not wholesale adoption | `Docs/Index/external_learning_index.md`, `CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md`, `Docs/Workflows/audit_external_repo.md` | `Docs/Cache/session_memory_migration/round2_external_reference_memory_20260604.md` | raw tree scanning as first step; importing provider configs/runtimes without approval |
| WeChat progress / cc-connect gateway | Sparse progress and human-intervention channel only; failures must be recorded and diagnosed once | `AGENTS.md#321-wechat-progress-and-intervention-rule`, `CoAgent/docs/status/cc_connect_weixin_smoke_2026_05_31.md` | `Results/coagent_gateway/`, `Docs/Cache/session_memory_migration/round2_infrastructure_memory_20260604.md` | treating message send as engineering proof; tight retry loops |
| Git / DevOps split | Large worktree requires path-limited split batches and GitIntegrator lane | `AGENTS.md#33-git-automation-rule`, `Docs/Workflows/agent_task_ledger.md` | `Results/agent_packets/closeouts/`, DevOps ledger rows | broad `git add -A`, broad full-tree status/add as routine work |
| Competition control-system architecture | Core contribution remains robust quadrotor control, not generic navigation; controller roadmap is PID -> improved PID/AWFF -> INDI/MPC/NMPC -> L1/safety/fault | `Docs/Design/00_系统总体设计.md`, `Docs/Design/03_控制系统架构.md` | `Models/QuadrotorControllerBlocks/`, `Config/controllers/`, `Config/scenarios/official/`, `Config/scenarios/robustness/` | letting UE/ROS work replace the control-system mainline |
| Controller model library | Many Sysblock/equation controller models exist; claims require current check/simulation and graphical counterpart status | `Docs/Workflows/build_sysblock_graphical_controller.md`, `Docs/Workflows/add_controller.md` | `Models/QuadrotorControllerBlocks/AWFF_*.mo`, `Models/QuadrotorExperiments/Example*.mo` | assuming every model file has current verified performance evidence |
| Official/robustness scenario matrix | Scenario YAMLs cover official examples, robustness, rotor-loss, wind gust, mass perturbation, planning, formation, and system faults | `Docs/Workflows/run_simulation.md`, `Docs/Workflows/produce_simulation_evidence.md` | `Config/scenarios/`, `Scripts/mworks/run_mworks_batch.py`, `Scripts/mworks/run_mworks_scenario.py` | reporting scenario completion without source/quality labels |
| Metrics and report evidence | Metrics, figures, replay, and report assets are structured and source-labeled; `quality_status=pass` is required for performance claims | `Docs/Design/08_仿真指标与自动评估.md`, `Docs/Workflows/calc_metrics.md`, `Docs/Workflows/generate_report_figures.md` | `Scripts/results/`, `Scripts/quality/audit_evidence_bundle.py`, `Results/*/*/*/metrics/` | using pretty plots or replay HTML as proof without raw/source/quality bundle |
| Simulation report and evidence audit | Current report contains the historical official, robustness, planning, Sysblock, and quality-gate narrative; re-read result metrics before updating conclusions | `Docs/simulation_report.md`, `Docs/user_manual.md`, `Docs/Workflows/produce_simulation_evidence.md` | `Results/test_reports/evidence_bundle_audit_20260515.md`, `Results/test_reports/evidence_bundle_audit_20260515.json`, `Results/人工审核清单.csv`, `Docs/Cache/session_memory_migration/round2_core_competition_report_docs_memory_20260604.md` | treating old report tables as current after scenario/model changes without re-audit |
| Official MWORKS docs conversion | Converted/scanned local MWORKS docs live under the current `Docs/MworksDocs/` path and should be entered through indexes | `Docs/Index/doc_index.md`, `Docs/Index/api_index.md`, `Docs/MworksDocs/README.md` | `Docs/MworksDocs/scan/relevant_index.md`, `Docs/MworksDocs/converted/转换索引.md`, `Docs/MinerU/mineru_precise_api.md` | using stale `Docs/Mworks/` paths; loading large docs before checking indexes |
| Test and quality gates | Tests are split by result family and script family; quality gates own whether a run is pass, smoke-only, or needs iteration | `Docs/Workflows/run_tests.md`, `Docs/Workflows/regression_test.md`, `Docs/Workflows/pre_submit_check.md`, `Docs/Workflows/code_review.md` | `Scripts/tests/`, `Scripts/quality/`, `Scripts/results/evaluate_result_quality.py`, `Docs/Cache/session_memory_migration/round2_core_competition_report_docs_memory_20260604.md` | calling a runnable script or model check sufficient proof without targeted tests/quality status |
| Planning and trajectory generation | Planning is for task trajectories and must be trackability-aware; global UE truth is validation oracle, not planner input | `Docs/Design/05_路径规划与轨迹生成.md`, `Docs/Workflows/unreal_renderer.md#native-map-and-point-cloud-windows` | `Scripts/planning/`, `Config/planners/`, `Config/scenarios/planning/` | planning from full hidden global truth; geometry-only path success without control tracking |
| Safety, fault, and system-level mission closure | Safety/fault/system scenarios are part of the competition-control story and must remain tied to event logs and MWORKS evidence | `Docs/Design/04_安全故障与容错.md`, `Docs/Design/07_场景扰动与测试矩阵.md` | `Config/scenarios/system/`, `Config/scenarios/robustness/`, `Models/QuadrotorExperiments/*Fault*` | treating failure-mode demos as complete without event/metric evidence |
| Multi-UAV formation | Formation is a later extension after single-UAV control/scene evidence is stable | `Docs/Design/06_多机编队控制.md` | `Models/QuadrotorExperiments/FormationTriangleFigure8LinearMPCSysblockClosedLoop.mo`, `Config/scenarios/formation/` | starting formation before single-UAV model/evidence gates are stable |
| Unreal MCP / Epic/Fab scene tooling | `mosim-unreal` and `mosim-epic` are the current project MCP surfaces for UE/Fab; tool inventory is not scene acceptance | `Docs/Skills/Unreal/mosim-unreal/SKILL.md`, `Docs/Skills/Unreal/mosim-epic/SKILL.md`, `Docs/Workflows/debug_mcp.md` | `Scripts/UE5/epic_library_index.py`, `Scripts/UE5/probe_unreal_mcp_listener.py`, `UE5/MoSimSceneLibrary/Content/MworksData/scene_source_registry.json` | old MCP names; equating Fab inventory visibility with imported editable content |
| UE scene source selection | Factory and Derelict are the main local candidates; registry primary, active links, review target, and final acceptance are separate facts | `Docs/Workflows/unreal_renderer.md` | `Docs/Cache/session_memory_migration/round2_scene_source_renderer_memory_20260604.md`, `UE5/MoSimSceneLibrary/Content/MworksData/active_scene_links.json` | saying "current scene" without naming which state field; resurrecting black/unusable maps |
| Old S0/S1 blockout renderer | Useful historical renderer/bootstrap work; superseded for current product scene work | `Docs/Workflows/agent_task_ledger.md` rows `UE-S0S1-*` | `Scripts/UE5/check_unreal_s0_s1_readiness.py`, old ledger rows | claiming blockout/manual UDP preview is final scene or planner evidence |
| Factory/Derelict MWORKS scene smoke | Real MWORKS/MCP smoke evidence exists, but quality is `smoke_only` | `Docs/Workflows/unreal_renderer.md`, `Docs/Workflows/produce_simulation_evidence.md` | `Results/unreal_scene_mapping/UE_SCENE_CLOSED_LOOP_STATUS.md`, per-scene `mworks_smoke/metrics/*.json` | treating smoke metrics as full controller/navigation performance |
| UAV architecture reset | Current accepted architecture is MWORKS truth/control, UE render/sensor oracle, ROS2/RViz2 robotics review | `Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md` | `Results/agent_runs/UE-UAV-ARCH-REPLAN-20260602/`, `Docs/Cache/session_memory_migration/round2_ue_ros_fastlio_memory_20260604.md` | polishing display parameters before UAV/sensor stack correctness |
| ROS2 / FAST-LIO / RViz2 | Factory Gate B opens manual UE/RViz review only; latest `*_CURRENT` gates outrank older failure/status files | `Docs/Workflows/ros2_runtime_setup.md`, `Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md#00-architecture-validation-gates-2026-06-02-cst` | `Results/unreal_scene_mapping/factoryenvironmentcollect/REALSTACK_MINILOOP_GATE_CURRENT.md`, `Docs/Cache/session_memory_migration/round2_ue_ros_fastlio_memory_20260604.md` | using nonzero topics without truth-error evaluation; using old Factory failure files as latest state |
| MWORKS simulation evidence boundary | Formal claims need `source` and `quality_status`; `check_model`/`simulate_model` are execution evidence only | `Docs/Workflows/produce_simulation_evidence.md`, `Docs/Workflows/run_simulation.md` | `Docs/Cache/session_memory_migration/round2_mworks_controller_evidence_memory_20260604.md` | offline CSV/HTML as MWORKS evidence; smoke-only as final performance |
| Graphical Sysblock counterpart | Formal controller scenarios need behavior-equivalent graphical Sysblock or explicit equation-bridge gap | `Docs/Workflows/build_sysblock_graphical_controller.md`, `AGENTS.md#36-simulation-evidence-rule` | `Docs/Cache/session_memory_migration/round2_mworks_controller_evidence_memory_20260604.md` | screenshot-only or empty graphical model as deliverable |
| MWORKS codegen / generated C runtime / SIL | Correct route is `GenerateModelCode`; PID demo compile/runtime/nonzero constant SIL passed only for demo scope | `Docs/Workflows/mworks_codegen_controller_runtime.md` | `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/`, `Docs/Cache/session_memory_migration/round2_mworks_codegen_runtime_memory_20260604.md` | `translate_model` as code export proof; PID demo SIL as all-controller authority |
| Sunray150 geometry and parameter migration | Rotor/camera/collision geometry migrated from accepted DAE/Blender manifest; mass/inertia/thrust/controller unchanged | `Docs/Workflows/identify_quadrotor_parameters.md`, `Docs/Workflows/new_conversation_context.md#3-current-valid-sunray150-geometry-state` | `Results/unreal_scene_mapping/sunray150_dae_assembly_parameters_20260604.json`, `Docs/Cache/session_memory_migration/round2_parameter_identification_memory_20260604.md` | old SDF rotor seed as current geometry; calling parameters identified without ULog/bench bundle |
| Sunray150 DAE/MID-360/propeller assembly | Source-faithful visual route is DAE-derived assembly plus standalone MID-360; propeller assembly uses reviewed three-blade source route | `Docs/Workflows/unreal_renderer.md`, `Docs/Skills/Unreal/sunray-pbr-material-workflow/SKILL.md` | `Docs/Cache/session_memory_migration/round2_sunray150_asset_memory_20260604.md`, `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/` | proxy MID-360 as final geometry; ad hoc propeller Z/yaw tuning as source truth |
| Sunray150 material / Blender / PBR | Material realism is not final; component-first closeups and manual Blender acceptance are required before UE export | `Docs/Skills/Unreal/sunray-pbr-material-workflow/SKILL.md`, `Docs/Workflows/new_conversation_context.md#6-current-ue-vehicle-visual-state` | `Results/unreal_scene_mapping/SUNRAY150_COMPONENT_MATERIAL_EVIDENCE_20260604.md`, `Results/coagent_gateway/packets/sunray_pbr_propeller_review_20260604.json` | simple whole-aircraft coloring as texture; launching `.blend` through wrong Windows app association |
| RflySim dynamics reference | RflySim is a structure/reference source, not Sunray150 parameter truth | `Docs/Workflows/identify_quadrotor_parameters.md#10-rflysim-dynamics-reference-audit` | `References/RflySim/RflySimAdv3Full/4.HILApps/RflySimAPIs/RflySimAPIsPers.zip` | copying RflySim sample mass/inertia/Ct/Cm directly into Sunray150 |
| Sunray150 dynamics identification | Current values remain `source=SDF_migration`; geometry changes do not imply dynamics identification | `Docs/Workflows/identify_quadrotor_parameters.md` | `Docs/Cache/session_memory_migration/round2_parameter_identification_memory_20260604.md` | changing lift/motor constants because propeller visual speed looks slow |
| PX4/Sunray/EGO/FAST-LIO behavior contracts | Use as architecture and behavior contracts: streamed setpoints, timeouts, Mid360 timing, local map/planner pipeline | `Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md`, `Results/unreal_scene_mapping/REAL_UAV_STACK_REUSE_MATRIX_20260602.md` | `Results/unreal_scene_mapping/REAL_UAV_STACK_SOURCE_AUDIT_20260602.md` | assuming ROS1/MAVROS/Sunray runtime has been adopted by MoSim |
| MWORKS C/C++ controller deployment direction | Target is MWORKS generated C/C++ controller code integrated into MoSim/V6X/PX4-facing adapter after per-controller SIL | `Docs/Workflows/mworks_codegen_controller_runtime.md`, `Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md` | `Results/codegen_probe/` | Python shortcuts as final controller runtime; generated runtime without equivalence gate |
| Project-local skills and MCP routing | MWORKS/Unreal/Sysplorer/Syslab skills are the execution routing layer; upstream skills are references to translate, not blindly execute | `AGENTS.md#5-mcp-and-agent-skill-routing`, `Docs/Index/workflow_index.md`, `Docs/Index/api_index.md` | `Docs/Skills/Mworks/`, `Docs/Skills/Unreal/`, `Docs/Skills/Sysplorer/` | guessing APIs or loading all skills/docs into context |

## 4. Current Accepted Facts That Replace Old Iterations

### 4.1 Sunray150 Geometry

Current accepted geometry source:

```text
Results/unreal_scene_mapping/sunray150_dae_assembly_parameters_20260604.json
```

Current rotor centers in body frame, meters:

```text
rotor_0: ( 0.053745, -0.053740, -0.014052)
rotor_1: (-0.053761,  0.053760, -0.014052)
rotor_2: ( 0.053746,  0.053759, -0.014052)
rotor_3: (-0.053761, -0.053739, -0.014052)
```

These replace earlier manual trial values such as old SDF
`(+/-0.065,+/-0.065,-0.025)` rotor placement and UE visual-only propeller
offset experiments. They do not change mass, inertia, motor constants, thrust
coefficients, controller gains, or identified-parameter status.

### 4.2 MID-360

Keep these separate:

```text
mechanical mount pose
point-cloud coordinate origin
built-in IMU position
FAST-LIO extrinsic_T
Gazebo/Sunray ray-sensor pose
```

Confirmed Livox manual fact currently recorded:

```text
MID-360 built-in IMU position in point-cloud frame:
(11.0, 23.29, -44.12) mm

FAST-LIO LiDAR pose in IMU body frame if axes are aligned:
[-0.011, -0.02329, 0.04412] m
```

Do not use the DAE mechanical mount center as FAST-LIO extrinsic without a
separate frame review.

### 4.3 Factory Gate B

Current Factory Gate B is only:

```text
ready_for_manual_rviz_ue_review
```

It has nonzero FAST-LIO outputs and truth-error metrics in the latest current
gate, but it does not prove final controller integration, planner performance,
scene acceptance, or finished product behavior.

### 4.4 MWORKS Codegen

Current codegen/SIL evidence is:

```text
model: AWFF_PID_Sysblock_Demo
route: GenerateModelCode
sample_time_s: 0.01
status: PID-demo compile/runtime/nonzero constant-input SIL smoke passed
open: time-varying and target-controller SIL
```

Do not generalize it to all controllers.

### 4.5 Control-System Mainline

The original competition project is still centered on robust quadrotor control.
The current design roadmap is:

```text
official PID baseline
-> improved PID / AWFF PID
-> INDI attitude inner loop
-> Linear MPC / NMPC outer loop
-> L1-inspired residual/disturbance compensation
-> Safety Filter
-> fault detection and allocation reconstruction
-> planning/trajectory smoothing
-> formation extension
```

Relevant model/config surfaces:

```text
Models/QuadrotorControllerBlocks/
Models/QuadrotorExperiments/
Config/controllers/
Config/scenarios/official/
Config/scenarios/robustness/
Config/scenarios/planning/
Config/scenarios/formation/
Config/scenarios/system/
```

Do not let UE/ROS/CoAgent work replace this control evidence line. UE and ROS2
are product/sensor/review layers; formal controller conclusions still require
MWORKS/Sysplorer/Syslab evidence with source labels, metrics, and quality gates.

### 4.6 Planning Evidence Boundary

Planning work must remain trackability-aware:

```text
local map / obstacle data
-> planner path
-> smoothed trajectory
-> velocity/acceleration/jerk/tilt/thrust feasibility
-> MWORKS controller tracking
-> metrics and event log
```

Global UE collision/occupancy truth is allowed as a validation oracle only. It
must not be fed to the planner as known global map input.

## 5. Historical Mistakes To Preserve As Anti-Regression Memory

| Mistake | Correct Current Rule |
|---|---|
| Reading the huge old chat as context | Use docs/cache index first. |
| Trusting old numeric values from chat | Re-read current manifest/model/result, then migrate through three rounds. |
| Asking user to review point size/grid color before UAV/sensor stack correctness | Prove MWORKS state, LiDAR/IMU/TF, FAST-LIO, and truth gate first. |
| Treating UE rendering as simulation truth | MWORKS owns dynamics/control/truth; UE is renderer/sensor oracle. |
| Treating RViz display as localization proof | Need selected FAST-LIO runtime, topics, and truth-error evaluation. |
| Treating smoke evidence as final performance | Quote `source` and `quality_status`. |
| Treating CoAgent design docs as approved runtime capability | Check `CoAgent/STATUS.md` and approval gate first. |
| Treating WeChat as proof | WeChat is notification only. |
| Broad Git operations in the huge repo | Path-limited split batches; GitIntegrator lane when needed. |
| Opening Blender assets through Windows file association | Use verified Blender command-line/background route; stop if wrong app appears. |

## 6. What To Do When A New Topic Appears

If a new conversation remembers or discovers a historical item not covered in
this index:

```text
1. Add a round-1 cache entry under Docs/Cache/session_memory_migration/.
2. Verify it against current files/results in round 2.
3. Re-read target docs and current evidence in round 3.
4. Promote narrowly, or mark rejected/superseded/user-review-gated.
```

Do not patch formal design/workflow docs from chat memory alone.
