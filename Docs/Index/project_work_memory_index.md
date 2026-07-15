# Project Work Memory Index

> Purpose: recover the important work history of the long MoSim conversation
> without loading the old multi-GB chat/session file.

Status: recovery routing index, reviewed after the single-thread reset,
2026-06-30 CST.

This index is a routing document. It does not make historical chat facts
authoritative. For each topic, use the linked current docs, manifests, result
files, and cache audits. If a remembered item is not listed here or in a linked
source, route it through `Docs/Workflows/session_memory_migration.md` before
using it as project truth.

## 1. How To Use This Index

This file is not part of ordinary startup. Start ordinary MoSim work with:

```text
1. AGENTS.md
2. Docs/Workflows/new_conversation_context.md
3. Docs/Workflows/mainline_operations_board.md
4. Docs/Workflows/single_thread_operating_model.md when operating mode is unclear
5. The topic-specific workflow, skill, design doc, source file, or result bundle
```

Use this index only when a task explicitly needs historical recovery, old
context disambiguation, or a pointer from memory/cache to the current source of
truth.

Do not read raw Codex session JSONL files or old chat dumps as routine context.
They contain many superseded parameters, failed attempts, and rejected routes.

When sources disagree, use this order:

```text
1. Current project files, manifests, scripts, model files, and test output.
2. Current formal design/workflow docs.
3. Result/evidence bundles and manual-review packets.
4. Current `mainline_operations_board.md` and newest active `PROGRESS.md`
   entries. `PROGRESS.md` is not a full transcript or recovery ledger.
5. Cache audits under Docs/Cache/session_memory_migration/.
6. Old chat/session memory.
```

## 2. Current Mainline

The current MoSim technical mainline is:

```text
MWORKS/Sysplorer/Syslab
  -> formal dynamics, controller design, generated C/C++ controller runtime,
     truth, metrics, and report evidence
Sunray ROS1 / Gazebo Classic / RViz
  -> current single-thread runtime review lane for assembled Sunray150,
     PX4/MAVROS/px4ctrl, MID360, project-local FAST-LIO, Diff-Planner,
     point-cloud/local-map review, and MWORKS-generated controller regression
PX4 + Gazebo
  -> later gated external SITL deployment route for generated controllers
     after the current baseline/interface gates are stable: PX4 flight-control
     authority, Gazebo plant/sensors
UE5 / MoSimSceneLibrary
  -> high-quality scene rendering, UAV visual, camera, collision/sensor oracle
ROS2 / RViz2 / PX4 x500
  -> historical/future robotics integration reference unless explicitly
     reopened; do not use as current Sunray ROS1 runtime evidence
```

Legacy agent runtime and WeChat/gateway material are not current technical
mainline layers. They are historical/reference only; current notification is
sparse Chinese email, and current task coordination is the single active Codex
thread.

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
| Current MoSim architecture boundary | Compact active boundary for MWORKS, Sunray ROS1/PX4/MAVROS/px4ctrl/RViz, project-local FAST-LIO, UE support/display, RflySim reference use, gate matrix, implementation streams, and anti-regression list. Legacy agent runtime is reference only. | `Docs/Design/架构/01_控制器平台/控制体系总览.md`, `Docs/Design/架构.md`, `Docs/Design/架构/03_测试调参与证据/测试与评价.md`, cached old ADR `Docs/Cache/design/historical_snapshots/absorbed_or_superseded_20260614/10_架构边界与当前状态ADR.md` | Sunray SDF, `References/MWORKS/QuadrotorModel/package.mo`, `Results/unreal_scene_mapping/REAL_UAV_STACK_REUSE_MATRIX_20260602.md`, `Results/unreal_scene_mapping/REAL_UAV_STACK_SOURCE_AUDIT_20260602.md` | reconstructing architecture from old chat or isolated `PROGRESS.md` entries |
| New conversation recovery and memory migration | Short startup doc exists; full migration is cache-first and three-round-gated | `Docs/Workflows/new_conversation_context.md`, `Docs/Workflows/session_memory_migration.md` | `Docs/Cache/session_memory_migration/00_index/coverage_matrix_20260604.md`, `Docs/Cache/session_memory_migration/00_index/completion_audit_20260604.md` | raw old session as truth; promoting chat-only numeric claims |
| Codex App / VSCode / WSL session and config repair | Infrastructure history is documented; do not touch external `.codex` state unless user explicitly requests infrastructure repair | `Docs/Index/codex_app_session_research.md`, `Docs/Workflows/debug_mcp.md` | `Docs/Cache/session_memory_migration/02_round2_review/round2_infrastructure_memory_20260604.md` | assuming App/VSCode live sync is durable state; normalizing SQLite/JSONL injection |
| legacy agent architecture and multi-dialog task system | Design/implementation history exists but runtime expansion is gated; MoSim technical mainline is not legacy agent runtime implementation now | archived legacy runtime docs, cache migration notes | `Docs/Cache/session_memory_migration/02_round2_review/round2_coagent_operating_memory_20260604.md`, `Results/agent_packets/` | hidden sub-agent as durable department; shadow-home transport as visible communication proof |
| Technical enterprise operating model | Enterprise/project-management philosophy was documented as design input for legacy agent runtime and task governance | archived legacy architecture docs | archived legacy problem-driven and dynamic-team design docs | treating fixed departments as the whole architecture; ignoring task-oriented dynamic teams |
| External agent/project learning | Reference projects are classified and audited for patterns, not wholesale adoption | `Docs/Index/external_learning_index.md`, `Docs/Index/reference_project_index.md`, `Docs/Workflows/audit_external_repo.md` | `Docs/Cache/session_memory_migration/02_round2_review/round2_external_reference_memory_20260604.md` | raw tree scanning as first step; importing provider configs/runtimes without approval |
| Email notification / cc-connect gateway diagnosis | Sparse Chinese email is the default completion/blocker/review-required human notification channel. WeChat/gateway material is historical or explicitly requested diagnostic context only, and failures must be recorded without tight retries. | `AGENTS.md`, archived gateway status notes | `Results/coagent_gateway/`, `Docs/Cache/session_memory_migration/02_round2_review/round2_infrastructure_memory_20260604.md` | treating message send as engineering proof; tight retry loops |
| Git / DevOps split | Large worktree requires path-limited review, explicit staged-file ownership, and temporary-ignore drain to final durable class rules | `AGENTS.md`, `Docs/Workflows/documentation_governance.md`, `Docs/Index/capability_index.md` | path-limited diff/status output, `git diff --check`, reviewed staged-file list; legacy packet/ledger evidence is trace-back only | broad staging, broad full-tree status/add as routine work, treating quiet untracked output or broad ignore throttles as completion |
| Competition control-system architecture | Core contribution remains robust quadrotor control inside the larger MoSim simulation system; current runtime order is px4ctrl baseline -> basic trajectories and error closure -> FAST-LIO independent evaluation plus EGO/EGOv2/Diff/EGO-Swarm engineering baseline -> representative controller template -> MWORKS Golden Slice and generated-code controller cores -> improved PID/INDI/MPC/NMPC -> L1/safety/fault; after G9.5/G9.6 have an explicit closeout that separates accepted, candidate, failed, and blocked paths, the active control family sequence may move to G10 then G11, where G11 covers all implemented/accepted controllers and augmentation combinations through MWORKS/codegen plus ROS1/Sunray reinjection and Gazebo regression | `Docs/Design/赛题.md`, `Docs/Design/架构/01_控制器平台/控制体系总览.md`, `Docs/Design/架构/01_控制器平台/统一控制接口.md`, `Docs/Design/架构/03_测试调参与证据/调参与参数优化.md`, `Docs/Design/架构/03_测试调参与证据/真机化与C++化.md`, `Docs/Workflows/sunray_ros1_current_runtime_lane.md`, cached old detail under `Docs/Cache/design/historical_snapshots/pre_rebuild_20260610/` | `Models/QuadrotorControllerBlocks/`, `Config/controllers/`, `Config/scenarios/official/`, `Config/scenarios/robustness/`, `Results/sunray_ros1/` | letting UE/ROS work replace the control-system mainline; tuning first before interface-level error isolation; treating Python realtime controllers/state adapters as deployable evidence |
| Controller model library | Many Sysblock/equation controller models exist; claims require current check/simulation and graphical counterpart status | `Docs/Workflows/build_sysblock_graphical_controller.md`, `Docs/Workflows/add_controller.md` | `Models/QuadrotorControllerBlocks/AWFF_*.mo`, `Models/QuadrotorExperiments/Example*.mo` | assuming every model file has current verified performance evidence |
| Official/robustness scenario matrix | Scenario YAMLs cover official examples, robustness, rotor-loss, wind gust, mass perturbation, planning, formation, and system faults | `Docs/Workflows/run_simulation.md`, `Docs/Workflows/produce_simulation_evidence.md` | `Config/scenarios/`, `Scripts/mworks/run_mworks_batch.py`, `Scripts/mworks/run_mworks_scenario.py` | reporting scenario completion without source/quality labels |
| Metrics and report evidence | Metrics, figures, replay, and report assets are structured and source-labeled; evidence bundles are required for performance claims | `Docs/Design/架构/03_测试调参与证据/测试与评价.md`, `Docs/Design/架构/01_控制器平台/控制体系总览.md`, `Docs/Workflows/calc_metrics.md`, `Docs/Workflows/generate_report_figures.md` | `Scripts/results/`, `Scripts/quality/audit_evidence_bundle.py`, `Results/*/*/*/metrics/` | using pretty plots or replay HTML as proof without raw/source/quality bundle |
| Simulation report and evidence audit | Current report contains the historical official, robustness, planning, Sysblock, and quality-gate narrative; re-read result metrics before updating conclusions | `Docs/simulation_report.md`, `Docs/user_manual.md`, `Docs/Workflows/produce_simulation_evidence.md` | `Results/test_reports/evidence_bundle_audit_20260515.md`, `Results/test_reports/evidence_bundle_audit_20260515.json`, `Results/人工审核清单.csv`, `Docs/Cache/session_memory_migration/02_round2_review/round2_core_competition_report_docs_memory_20260604.md` | treating old report tables as current after scenario/model changes without re-audit |
| Official MWORKS docs conversion | Converted/scanned local MWORKS docs live under the current `Docs/MworksDocs/` path and should be entered through indexes | `Docs/Index/doc_index.md`, `Docs/Index/api_index.md`, `Docs/MworksDocs/README.md` | `Docs/MworksDocs/scan/relevant_index.md`, `Docs/MworksDocs/converted/转换索引.md`, `Docs/MinerU/mineru_precise_api.md` | using stale legacy Docs/Mworks paths; loading large docs before checking indexes |
| Test and quality gates | Tests are split by result family and script family; quality gates own whether a run is pass, smoke-only, or needs iteration | `Docs/Workflows/run_tests.md`, `Docs/Workflows/regression_test.md`, `Docs/Workflows/pre_submit_check.md`, `Docs/Workflows/code_review.md` | `Scripts/tests/`, `Scripts/quality/`, `Scripts/results/evaluate_result_quality.py`, `Docs/Cache/session_memory_migration/02_round2_review/round2_core_competition_report_docs_memory_20260604.md` | calling a runnable script or model check sufficient proof without targeted tests/quality status |
| Planning and trajectory generation | Planning is for task trajectories and must be trackability-aware; global UE truth is validation oracle, not planner input | `Docs/Design/架构/02_感知定位与规划集群/规划与编队控制接口.md`, `Docs/Design/架构/02_感知定位与规划集群/FASTLIO定位闭环.md`, `Docs/Workflows/unreal_renderer.md#native-map-and-point-cloud-windows` | `Scripts/planning/`, `Config/planners/`, `Config/scenarios/planning/` | planning from full hidden global truth; geometry-only path success without control tracking |
| Safety, fault, and system-level mission closure | Safety/fault/system scenarios are part of the competition-control story and must remain tied to event logs and MWORKS evidence | `Docs/Design/架构/01_控制器平台/控制增强与容错.md`, `Docs/Design/架构/03_测试调参与证据/测试与评价.md` | `Config/scenarios/system/`, `Config/scenarios/robustness/`, `Models/QuadrotorExperiments/*Fault*` | treating failure-mode demos as complete without event/metric evidence |
| Multi-UAV formation | Formation is a later extension after single-UAV control/scene evidence is stable | `Docs/Design/架构/02_感知定位与规划集群/规划与编队控制接口.md` | `Models/QuadrotorExperiments/FormationScenarios/FormationTriangleFigure8LinearMPCSysblockClosedLoop.mo`, `Config/scenarios/formation/` | starting formation before single-UAV model/evidence gates are stable |
| Unreal MCP / Epic/Fab scene tooling | `mosim-unreal` and `mosim-epic` are the current project MCP surfaces for UE/Fab; tool inventory is not scene acceptance | `Docs/Skills/Unreal/mosim-unreal/SKILL.md`, `Docs/Skills/Unreal/mosim-epic/SKILL.md`, `Docs/Workflows/debug_mcp.md` | `Scripts/UE5/epic_library_index.py`, `Scripts/UE5/probe_unreal_mcp_listener.py`, `UE5/MoSimSceneLibrary/Content/MworksData/scene_source_registry.json` | old MCP names; equating Fab inventory visibility with imported editable content |
| UE scene source selection | Factory and Derelict are the main local candidates; registry primary, active links, review target, and final acceptance are separate facts | `Docs/Workflows/unreal_renderer.md` | `Docs/Cache/session_memory_migration/02_round2_review/round2_scene_source_renderer_memory_20260604.md`, `UE5/MoSimSceneLibrary/Content/MworksData/active_scene_links.json` | saying "current scene" without naming which state field; resurrecting black/unusable maps |
| Old S0/S1 blockout renderer | Useful historical renderer/bootstrap work; superseded for current product scene work | archived legacy ledger trace-back via `Docs/Workflows/agent_task_ledger.md` rows `UE-S0S1-*` only | `Scripts/UE5/check_unreal_s0_s1_readiness.py`, old ledger rows | claiming blockout/manual UDP preview is final scene or planner evidence |
| Factory/Derelict MWORKS scene smoke | Real MWORKS/MCP smoke evidence exists, but quality is `smoke_only` | `Docs/Workflows/unreal_renderer.md`, `Docs/Workflows/produce_simulation_evidence.md` | `Results/unreal_scene_mapping/UE_SCENE_CLOSED_LOOP_STATUS.md`, per-scene `mworks_smoke/metrics/*.json` | treating smoke metrics as full controller/navigation performance |
| UAV architecture reset | Current accepted architecture is MWORKS for model/control evidence, ROS1/Sunray/Gazebo/PX4/MAVROS/RViz for current robotics/perception/planning validation, PX4+Gazebo/PX4-native as a later generated-controller deployment branch, and UE render/sensor oracle as a post-control display/enhancement route | `Docs/Design/架构/01_控制器平台/控制体系总览.md`, `Docs/Design/架构/02_感知定位与规划集群/FASTLIO定位闭环.md`, `Docs/Design/架构/01_控制器平台/统一控制接口.md`, `Docs/Design/架构/03_测试调参与证据/测试与评价.md`, cached old ADR/ROS2 notes under `Docs/Cache/design/historical_snapshots/absorbed_or_superseded_20260614/` | `Results/agent_runs/UE-UAV-ARCH-REPLAN-20260602/`, `Docs/Cache/session_memory_migration/02_round2_review/round2_ue_ros_fastlio_memory_20260604.md`, cached old replan under `Docs/Cache/design/historical_snapshots/pre_rebuild_20260610/09_UE_ROS_MWORKS无人机仿真架构重构.md` | polishing display parameters before UAV/sensor stack correctness; treating ROS2 direct actuator bridges as deployment |
| CoSim future platform blueprint | Future platform design is now vehicle-family-first: multirotor, fixed-wing, VTOL, and benign ducted model-aircraft lines share a common core and select backend adapters from reviewed research decisions; raw research is preserved separately | `Docs/CoSim/README.md`, `Docs/CoSim/00_platform/00_CoSim总体蓝图.md`, `Docs/CoSim/10_shared_core/01_共享内核与数据契约.md`, `Docs/CoSim/20_vehicle_families/README.md`, `Docs/CoSim/30_backend_adapters/README.md`, `Docs/CoSim/research/README.md` | `Docs/Cache/cosim/cosim_rebuild_plan_20260614.md`, `Docs/Cache/cosim/source_migration_manifest_20260614.md`, `Docs/Cache/cosim/architecture_draft_audit_20260614.md`, raw preserved under `Docs/CoSim/research/raw/` | treating simulator names as the product tree; deleting raw research before reviewed conclusions are accepted; presenting CoSim architecture draft as runtime evidence |
| ROS / FAST-LIO / RViz | Current executable review is Sunray ROS1/Gazebo/RViz. ROS2 remains future/reference unless explicitly reopened. Localization claims need TF/static-TF, topic-rate, extrinsic, timing, and quality gates. | `Docs/Design/架构/02_感知定位与规划集群/FASTLIO定位闭环.md`, `Docs/Design/架构/01_控制器平台/统一控制接口.md`, `Docs/Design/架构/03_测试调参与证据/测试与评价.md`, `Docs/Workflows/ros2_runtime_setup.md`, cached trace `Docs/Cache/design/historical_snapshots/absorbed_or_superseded_20260614/14_ROS2正式接入与控制器后端迁移设计.md` | `Results/unreal_scene_mapping/factoryenvironmentcollect/REALSTACK_MINILOOP_GATE_CURRENT.md`, `Docs/Cache/session_memory_migration/02_round2_review/round2_ue_ros_fastlio_memory_20260604.md`, `Results/sunray_ros1/` | using nonzero topics without truth-error evaluation; using old Factory failure files as latest state; treating visible point cloud as planner readiness |
| MWORKS simulation evidence boundary | Formal claims need `source` and `quality_status`; `check_model`/`simulate_model` are execution evidence only | `Docs/Workflows/produce_simulation_evidence.md`, `Docs/Workflows/run_simulation.md` | `Docs/Cache/session_memory_migration/02_round2_review/round2_mworks_controller_evidence_memory_20260604.md` | offline CSV/HTML as MWORKS evidence; smoke-only as final performance |
| Graphical Sysblock counterpart | Formal controller scenarios need behavior-equivalent graphical Sysblock or explicit equation-bridge gap | `Docs/Workflows/build_sysblock_graphical_controller.md`, `AGENTS.md#36-simulation-evidence-rule` | `Docs/Cache/session_memory_migration/02_round2_review/round2_mworks_controller_evidence_memory_20260604.md` | screenshot-only or empty graphical model as deliverable |
| MWORKS codegen / generated C runtime / SIL | Correct route is `GenerateModelCode`; PID demo compile/runtime/nonzero constant SIL passed only for demo scope | `Docs/Workflows/mworks_codegen_controller_runtime.md` | `Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/`, `Docs/Cache/session_memory_migration/02_round2_review/round2_mworks_codegen_runtime_memory_20260604.md` | `translate_model` as code export proof; PID demo SIL as all-controller authority |
| Sunray150 geometry and parameter migration | Rotor/camera/collision geometry migrated from accepted DAE/Blender manifest; mass/inertia/thrust/controller unchanged | `Docs/Workflows/identify_quadrotor_parameters.md`, `Docs/Workflows/new_conversation_context.md#3-current-valid-sunray150-geometry-state` | `Results/unreal_scene_mapping/sunray150_dae_assembly_parameters_20260604.json`, `Docs/Cache/session_memory_migration/02_round2_review/round2_parameter_identification_memory_20260604.md` | old SDF rotor seed as current geometry; calling parameters identified without ULog/bench bundle |
| Sunray150 DAE/MID-360/propeller assembly | Source-faithful visual route is DAE-derived assembly plus standalone MID-360; propeller assembly uses reviewed three-blade source route | `Docs/Workflows/unreal_renderer.md`, `Docs/Skills/Unreal/sunray-pbr-material-workflow/SKILL.md` | `Docs/Cache/session_memory_migration/02_round2_review/round2_sunray150_asset_memory_20260604.md`, `UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/` | proxy MID-360 as final geometry; ad hoc propeller Z/yaw tuning as source truth |
| Sunray150 material / Blender / PBR | Material realism is not final; component-first closeups and manual Blender acceptance are required before UE export | `Docs/Skills/Unreal/sunray-pbr-material-workflow/SKILL.md`, `Docs/Workflows/new_conversation_context.md#6-current-ue-vehicle-visual-state` | `Results/unreal_scene_mapping/SUNRAY150_COMPONENT_MATERIAL_EVIDENCE_20260604.md`, `Results/coagent_gateway/packets/sunray_pbr_propeller_review_20260604.json` | simple whole-aircraft coloring as texture; launching `.blend` through wrong Windows app association |
| RflySim dynamics reference | RflySim is a structure/reference source, not Sunray150 parameter truth | `Docs/Workflows/identify_quadrotor_parameters.md#10-rflysim-dynamics-reference-audit` | `References/RflySim/RflySimAdv3Full/4.HILApps/RflySimAPIs/RflySimAPIsPers.zip` | copying RflySim sample mass/inertia/Ct/Cm directly into Sunray150 |
| Sunray150 dynamics identification | Current values remain `source=SDF_migration`; geometry changes do not imply dynamics identification | `Docs/Workflows/identify_quadrotor_parameters.md` | `Docs/Cache/session_memory_migration/02_round2_review/round2_parameter_identification_memory_20260604.md` | changing lift/motor constants because propeller visual speed looks slow |
| MoSimQuadrotorModel formal package | Project-owned formal quadrotor package is now `Models/MoSimQuadrotorModel`; `QuadrotorModel` stays official baseline and `QuadrotorExperiments` stays legacy compatibility/migration pool | `Docs/Design/架构/03_测试调参与证据/真机化与C++化.md`, `Docs/Design/架构/01_控制器平台/控制体系总览.md`, `Docs/Index/simulation_model_structure_index.md`, cached migration plan `Docs/Cache/design/historical_snapshots/absorbed_or_superseded_20260614/12_MoSimQuadrotorModel模型归档与迁移计划.md`, `Docs/Workflows/new_conversation_context.md#5-current-mworks-dynamics-state`, `Docs/Workflows/identify_quadrotor_parameters.md#102-2026-06-07-mosimquadrotormodel-formal-package-migration-rule` | `Models/MoSimQuadrotorModel/package.mo`, `Models/QuadrotorExperiments/package.mo`, `PROGRESS.md` latest entries | dumping all new experiments into flat `QuadrotorExperiments`; destructive all-at-once renames without check_model/reference updates |
| PX4/Sunray/EGO/FAST-LIO behavior contracts | Use as architecture and behavior contracts: streamed setpoints, timeouts, Mid360 timing, local map/planner pipeline. Current executable review is Sunray ROS1/Gazebo; PX4/ROS2 direct routes require explicit reopening. FAST-LIO state-source promotion must follow the dedicated localization and C++ closeout plans. | `Docs/Workflows/sunray_ros1_current_runtime_lane.md`, `Docs/Design/架构/02_感知定位与规划集群/FASTLIO定位闭环.md`, `Docs/Design/架构/03_测试调参与证据/真机化与C++化.md`, `Docs/Design/架构/01_控制器平台/控制体系总览.md`, `Docs/Design/架构/01_控制器平台/统一控制接口.md`, `Docs/Design/架构/03_测试调参与证据/测试与评价.md`, cached ROS2/backend note `Docs/Cache/design/historical_snapshots/absorbed_or_superseded_20260614/14_ROS2正式接入与控制器后端迁移设计.md`, `Results/unreal_scene_mapping/REAL_UAV_STACK_REUSE_MATRIX_20260602.md` | `Results/unreal_scene_mapping/REAL_UAV_STACK_SOURCE_AUDIT_20260602.md`, `Results/sunray_ros1/` | treating historical ROS2/PX4/x500 evidence as current; using fake/static point clouds or direct Gazebo actuator fixtures as final proof; treating RViz-visible FAST-LIO maps as localization/control proof |
| MWORKS C/C++ controller deployment direction | Target is MWORKS generated C/C++ controller code integrated into the shared Controller ABI after per-controller SIL. Current G11 first closes MWORKS/codegen through ROS1/Sunray/MAVROS reinjection and Gazebo regression; PX4 Offboard or PX4 module/uORB in PX4+Gazebo SITL is a later gated branch. Future Simulink codegen should target the same PX4-compatible adapter surfaces. Runtime adapters that affect control state or PX4 messages should be C++/compiled before flight-like claims. | `Docs/Design/架构/01_控制器平台/统一控制接口.md`, `Docs/Design/架构/03_测试调参与证据/测试与评价.md`, `Docs/Workflows/mworks_codegen_controller_runtime.md`, `Docs/Design/架构/03_测试调参与证据/真机化与C++化.md`, `Docs/Design/架构/01_控制器平台/控制体系总览.md`, `Docs/Design/架构/01_控制器平台/代码生成与PX4部署.md`, cached trace `Docs/Cache/design/historical_snapshots/absorbed_or_superseded_20260614/14_ROS2正式接入与控制器后端迁移设计.md` | `Results/codegen_probe/` | Python shortcuts as final controller runtime; generated runtime without equivalence gate; ROS2 direct-to-Gazebo actuator control as formal deployment; exposing backend-internal variable names as the public ROS2/controller contract |
| Project-local skills and MCP routing | MWORKS/Unreal/Sysplorer/Syslab skills are the execution routing layer; upstream skills are references to translate, not blindly execute | `AGENTS.md#5-mcp-and-agent-skill-routing`, `Docs/Workflows/tooling_assets_governance.md`, `Docs/Index/workflow_index.md`, `Docs/Index/api_index.md` | `Docs/Skills/Mworks/`, `Docs/Skills/Unreal/`, `Docs/Skills/Sysplorer/`, `References/`, Codex plugin cache | guessing APIs, loading all skills/docs into context, or moving crawled projects directly into active skills |

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

Do not let UE/ROS/legacy agent runtime work replace this control evidence line. UE and ROS2
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
| Treating legacy agent design docs as approved runtime capability | Check current MoSim workflow/board approval first. |
| Treating WeChat as proof | WeChat is notification only. |
| Broad Git operations in the huge repo | Path-limited split batches; GitIntegrator lane when needed. |
| Treating `.gitignore` as the finish line for crawled repositories | Temporary ignores are only throttles; drain them project by project and leave only durable class/exact-risk rules. |
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
