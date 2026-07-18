# Workflow Index

> Index of repeatable project workflows.

---

## 1. Core Workflows

| Task | Workflow File |
|---|---|
| Debug MCP | `Docs/Workflows/debug_mcp.md` |
| Govern plugins, MCP servers, skills, workflows, and reference tooling assets | `Docs/Workflows/tooling_assets_governance.md`, `Docs/Index/capability_index.md`, `Docs/Index/api_index.md` |
| Select native/plugin/MCP/skill/script capability for a task | `Docs/Index/capability_index.md`, `Docs/Index/api_index.md` |
| Operate Codex native hooks and App capability governance | `Scripts/hooks/README.md`, `Docs/Workflows/tooling_assets_governance.md`, `Docs/Index/codex_app_session_research.md` |
| Operate Unreal MCP | `Docs/Skills/Unreal/mosim-unreal/SKILL.md`, `Docs/Workflows/debug_mcp.md#71-unreal-mcp-local-wrapper`, `Docs/Index/api_index.md#5-unreal-mcp-tools` |
| Inspect Epic/Fab/Launcher scene library | `Docs/Skills/Unreal/mosim-epic/SKILL.md`, `Docs/Workflows/debug_mcp.md#73-epicfab-scene-source-mcp`, `Docs/Workflows/unreal_renderer.md`, `Scripts/UE5/epic_library_view.py`, `Scripts/UE5/epic_library_index.py`, `Scripts/UE5/check_epic_library_inventory.py`, `Scripts/UE5/audit_scene_source.py`, `Scripts/UE5/build_scene_source_registry.py`, `Scripts/UE5/plan_scene_truth_export.py`, `Scripts/UE5/run_scene_truth_export.py`, `Scripts/UE5/export_unreal_scene_truth.py` |
| Operate MoSim Unreal Editor MCP | `Docs/Skills/Unreal/mosim-unreal/SKILL.md`, `Docs/Workflows/debug_mcp.md#71-unreal-mcp-local-wrapper`, `Scripts/UE5/probe_unreal_mcp_listener.py`, `Scripts/UE5/probe_unreal_editor_mcp_tools.py` |
| Build Unreal/RflySim renderer and scene workflow | `Docs/Workflows/unreal_renderer.md` for explicit S11 display/frontend enhancement; not the current control-loop authority |
| Design or implement UE one-way rendering mirror bridge | `Docs/Design/架构/04_展示与实验平台/UE渲染镜像桥接方案.md`, `Docs/Design/架构/04_展示与实验平台/展示与实验平台接口.md`, `Docs/Workflows/unreal_renderer.md`; start with T0 replay before T1 live sidecar |
| Import accepted UE scenes into Gazebo Classic static scene bases | `Docs/Workflows/ue_to_gazebo_static_scene_import.md`, `Docs/Skills/Unreal/ue-gazebo-static-scene-import/SKILL.md`; proves static scene-base only, not ROS/PX4/SLAM/planner/controller success |
| Validate the accepted Factory L2 scene as the new full-system environment | `Docs/Workflows/factory_l2_full_system_validation_plan.md`, then `Docs/Workflows/factory_sunray_integration_gate.md`, `Docs/Workflows/sunray_ros1_execution_checklist.md`, and `Docs/Workflows/unreal_renderer.md`; complete Gazebo/PX4/MAVROS/RViz evidence before UE render mirror acceptance |
| Connect accepted Factory L2 scene base to Sunray ROS1/Gazebo runtime gate | `Docs/Workflows/factory_sunray_integration_gate.md`, `Docs/Workflows/sunray_ros1_current_runtime_lane.md`, `Docs/Workflows/sunray_ros1_execution_checklist.md`; FS1 proves bounded single-UAV spawn/sensor/runtime only, FS2 is separate RViz visual review |
| Design Factory L2 static import to Gazebo and UE Global Overview attitude trails | `Docs/Design/架构/04_展示与实验平台/Factory地图导入与全局态势视图.md`, `Docs/Workflows/ue_to_gazebo_static_scene_import.md`, `Docs/Design/架构/04_展示与实验平台/UE渲染镜像桥接方案.md`, `Docs/Workflows/unreal_renderer.md`; Factory L2 is Scene Base only and still needs Data Bridge for runtime display |
| UE/RViz mapping-window research and evidence boundary | `Docs/Workflows/unreal_mapping_window_research.md` |
| Current architecture and execution order | `Docs/Design/架构.md`, `Docs/Design/需求.md`, `Docs/Design/赛题.md`, `Docs/Design/架构/00_架构与任务/任务路线图.md` |
| Design MoSim experiment frontend and end-to-end tuning/fault loop | `Docs/Design/架构/00_架构与任务/MoSim实验前端与闭环架构.md`, `Docs/Design/架构/00_架构与任务/系统集成接口与编排.md` |
| Design low-latency RViz/UE embedding and warm display sessions | `Docs/Design/架构/04_展示与实验平台/RViz与UE低延迟嵌入接口.md`, `Docs/Design/架构/04_展示与实验平台/展示与实验平台接口.md` |
| Implement the two-GUI non-AI system loop and later 3-9 UAV scaling | `Docs/Design/架构/04_展示与实验平台/双GUI与非AI系统闭环实施规划.md`; detailed QGC reuse, UE-centered workspace, Factory mini/expanded mission map, waypoint/boundary/fleet editing, and map command authority are frozen in `Docs/Design/架构/04_展示与实验平台/Flight Console与二维任务地图详细设计.md`; Model Studio is a lightweight native Syslab APP and AI is interface-only in this goal |
| Expand Model Studio offline controller composition and defer model-directory migration until regression freeze | `Docs/Workflows/model_studio_offline_expansion_goal.md`, `Config/control_platform/offline_expansion_inventory.json`, `Scripts/quality/check_offline_expansion_inventory.py` |
| Design MWORKS real-time controller co-simulation with the two GUIs | `Docs/Design/架构/04_展示与实验平台/MWORKS实时联合仿真与双GUI接口设计.md`; generated-C remains the deployment default, while MWORKS Live stays disabled until RT0-RT5 frequency, latency, hover, fallback, and A/B gates pass |
| Design parameter/signal inspection, automatic tuning, operation progress, and Gazebo-to-UE/MWORKS latency | `Docs/Design/架构/04_展示与实验平台/参数信号自动调参与运行可观测性详细设计.md`; tuning algorithm rules remain in `Docs/Design/架构/03_测试调参与证据/调参与参数优化.md`, while runtime/display latency remains outside the control loop |
| Close source/MWORKS/replay work while RACER owns Gazebo/PX4 resources | `Docs/Workflows/non_gazebo_closeout_board_20260715.md`, `Docs/Workflows/competition_gap_inventory_20260715.md` |
| Turn accepted requirements and architecture into executable agent work layers 3-6 | `Docs/Workflows/agent_project_operating_layers.md` |
| Execute current Sunray ROS1/Gazebo/RViz lane and source boundaries | `Docs/Workflows/sunray_ros1_current_runtime_lane.md`, `Docs/Workflows/sunray_ros1_execution_checklist.md`, `Docs/Index/sunray_migration_index.md`, `References/Sunray`, `References/Lab/localization_slam/FAST_LIO` |
| Close out Sunray/PX4/Gazebo baseline toward flight-like deployment | `Docs/Design/架构/03_测试调参与证据/真机化与C++化.md`, `Docs/Design/架构/02_感知定位与规划集群/FASTLIO定位闭环.md`, `Docs/Workflows/sunray_ros1_current_runtime_lane.md`; classify runtime code as T0/T1/T2/T3 before promoting Python nodes as deployable |
| Optimize current single-UAV baseline controller before MWORKS generated-code deployment | `Docs/Design/架构/03_测试调参与证据/调参与参数优化.md`, `Docs/Design/架构/01_控制器平台/统一控制接口.md`, `Docs/Workflows/sunray_ros1_current_runtime_lane.md`; order is freeze frequencies -> compare control interfaces -> algorithm fixes -> parameter tuning |
| Historical/future ROS2 Humble runtime reference only; not current Sunray review lane | `Docs/Workflows/ros2_runtime_setup.md`, `Scripts/UE5/check_ros_mapping_runtime_env.py` |
| Check ROS/RViz/FAST-LIO runtime environment | current ROS1/Sunray lane first; ROS2 checks only after explicit route reopening |
| Validate MoSim RflySim-style four-layer architecture and UAV gates | `Docs/Design/架构/01_控制器平台/控制体系总览.md`, `Docs/Design/架构.md`, `Docs/Design/架构/03_测试调参与证据/真机化与C++化.md`, `Docs/Design/架构/03_测试调参与证据/测试与评价.md`, `Docs/Design/架构/02_感知定位与规划集群/FASTLIO定位闭环.md`, cached absorbed inputs `Docs/Cache/design/historical_snapshots/absorbed_or_superseded_20260614/`, historical replan cache `Docs/Cache/design/historical_snapshots/pre_rebuild_20260610/09_UE_ROS_MWORKS无人机仿真架构重构.md`, `Results/unreal_scene_mapping/factoryenvironmentcollect/REALSTACK_MINILOOP_GATE.md`, `Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_FACTORY_FAILURE_DIAGNOSIS.md`, `Docs/Workflows/mworks_codegen_controller_runtime.md` |
| Design formal generated-controller deployment and future Simulink backend replacement | `Docs/Design/架构/01_控制器平台/代码生成与PX4部署.md`, `Docs/Design/架构/01_控制器平台/统一控制接口.md`, `Docs/Design/架构/03_测试调参与证据/测试与评价.md`, `Docs/Workflows/mworks_codegen_controller_runtime.md`; current execution is selected by the board, generated-code promotion uses ROS1/Sunray reinjection and Gazebo regression, and PX4/ROS2 route stays disabled until explicitly reopened |
| Design multi-UAV formation architecture, identity, metrics, and database boundary | `Docs/Design/架构/02_感知定位与规划集群/规划与编队控制接口.md`, `Docs/Design/架构/02_感知定位与规划集群/planners/README.md`, `Docs/Design/架构/02_感知定位与规划集群/planners/MADER-RMADER.md`, `Docs/Design/架构/02_感知定位与规划集群/planners/Fast-Multi-Robot-Exploration.md`, `Docs/Design/架构/02_感知定位与规划集群/planners/Skybrush.md`, `Docs/Design/架构/01_控制器平台/统一控制接口.md`, `Docs/Design/架构/03_测试调参与证据/测试与评价.md`, `Docs/Index/sunray_migration_index.md#多机编队与避障索引` |
| Project structure refactor toward RflySim-like simulator product | `Docs/Workflows/project_structure_refactor.md` |
| Find simulation model, scenario, runner, and result structure | `Docs/Index/simulation_model_structure_index.md` |
| Translate MathWorks/Simulink patterns to MWORKS | `Docs/Workflows/translate_mathworks_to_mworks.md` |
| Resolve MWORKS model context | `Docs/Skills/Mworks/mworks-model-context/SKILL.md` |
| Produce MWORKS simulation evidence | `Docs/Skills/Mworks/mworks-simulation-evidence/SKILL.md` |
| Port MATLAB/Syslab logic | `Docs/Skills/Mworks/mworks-syslab-porting/SKILL.md` |
| Operate MCP with minimal impact | `Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md` |
| Diagnose runtime/model issues | `Docs/Skills/Mworks/mworks-runtime-diagnostics/SKILL.md` |
| Test and review quality gates | `Docs/Skills/Mworks/mworks-test-quality/SKILL.md` |
| Prepare report and replay assets | `Docs/Skills/Mworks/mworks-report-visualization/SKILL.md` |
| Build graphical Sysblock controller | `Docs/Skills/Mworks/mworks-sysblock-graphical-modeling/SKILL.md`, `Docs/Workflows/build_sysblock_graphical_controller.md` |
| Generate MWORKS/Sysblock C/C++ controller runtime | `Docs/Workflows/mworks_codegen_controller_runtime.md`, active G9 closeout at `Docs/Workflows/g9_mworks_generated_runtime_closeout.md`, `Docs/Design/架构/03_测试调参与证据/真机化与C++化.md`, `Scripts/mworks/check_codegen_runtime.py`, `Scripts/tests/test_mworks_codegen_runtime.py` |
| Consult official Sysplorer modeling rules | `Docs/Skills/Sysplorer/ty-sysplorer-modeling-rules`, `Docs/Skills/Sysplorer/ty-sysblock-diagram-modeling`, `Docs/Skills/Sysplorer/ty-sysblock-signal-modeling`, `Docs/Skills/Sysplorer/modelica-library-workflow` |
| Current single-thread operating model | `Docs/Workflows/single_thread_operating_model.md` |
| PMO mainline operations board | `Docs/Workflows/mainline_operations_board.md` |
| Documentation placement, archive, and legacy migration governance | `Docs/Workflows/documentation_governance.md`, `Docs/Cache/agent_legacy/coagent_internalization_migration_plan_20260624.md` |
| Legacy AgentOS / multi-thread cleanup review | `Docs/Cache/agent_legacy/legacy_coagent_cleanup_plan_20260624.md` |
| External project master index | `Docs/Index/external_learning_index.md` |
| Newest active progress note only; not a recovery transcript | `PROGRESS.md` |
| New conversation recovery context | `Docs/Workflows/new_conversation_context.md` |
| Historical/recovery project work memory index | `Docs/Index/project_work_memory_index.md` |
| Historical/recovery task ledger | `Docs/Workflows/agent_task_ledger.md` legacy trace-back only |
| Long-session memory migration | `Docs/Workflows/session_memory_migration.md`, `Docs/Cache/session_memory_migration/00_index/long_goal_plan_20260604.md`, `Docs/Cache/session_memory_migration/00_index/coverage_matrix_20260604.md`, `Docs/Cache/session_memory_migration/03_round3_disposition/round3_promotion_rejection_map_20260604.md`, `Docs/Cache/session_memory_migration/00_index/completion_audit_20260604.md`, `Docs/Cache/session_memory_migration/` |
| Codex App / WSL session research and handoff | `Docs/Index/codex_app_session_research.md`, `Docs/Workflows/debug_mcp.md#6-codex-app-vscode-wsl-session-policy` |
| Desktop window screenshot evidence | `Docs/Skills/Desktop/window-capture-evidence/SKILL.md`, examples in `Docs/Index/api_index.md#12-desktop-window-screenshot-and-action-helpers` |
| Explicitly authorized desktop window UI actions | `Docs/Skills/Desktop/window-ui-action-control/SKILL.md`, examples in `Docs/Index/api_index.md#12-desktop-window-screenshot-and-action-helpers` |
| External repository audit | `Docs/Workflows/audit_external_repo.md`, `Scripts/reference/audit_external_repo.py` |
| External reference snapshot freshness and promotion | `Docs/Workflows/reference_snapshot_update.md` |
| Validate external project master index | `Docs/Index/external_learning_index.md`, `Scripts/reference/check_reference_index.py`, `Docs/Workflows/audit_external_repo.md` |
| AirSim external repository batch migration | archived legacy note under `Docs/Cache/agent_legacy/legacy_workflows_20260624/agent_orchestration.md`; current external repo work uses `Docs/Workflows/audit_external_repo.md` |
| Docs/Skills/workflow external repo audit | `Docs/Workflows/audit_external_repo.md`, `Docs/Workflows/tooling_assets_governance.md` |
| Three-round learn-and-update audit | `Docs/Workflows/audit_external_repo.md` |
| Recurring external Docs/skills learning | archived legacy note under `Docs/Cache/agent_legacy/legacy_workflows_20260624/agent_orchestration.md`; current reference learning starts from `Docs/Index/external_learning_index.md` |
| Project doctor / self-check | `Scripts/quality/doctor.py`, `Docs/Workflows/pre_submit_check.md`, `Docs/Workflows/debug_mcp.md` |
| Resolve model context workflow | `Docs/Workflows/resolve_model_context.md` |
| Browse current simulation model structure | `Docs/Index/simulation_model_structure_index.md` |
| Produce simulation evidence workflow | `Docs/Workflows/produce_simulation_evidence.md` |
| Run post-simulation task queue | `Docs/Workflows/post_simulation_task_flow.md` |
| Run one simulation | `Docs/Workflows/run_simulation.md` |
| Read simulation results | `Docs/Workflows/read_results.md` |
| Calculate metrics | `Docs/Workflows/calc_metrics.md` |
| Generate report figures | `Docs/Workflows/generate_report_figures.md` |
| Legacy parallel-agent execution notes | `Docs/Cache/agent_legacy/legacy_coagent_cleanup_plan_20260624.md`, archived body at `Docs/Cache/agent_legacy/legacy_workflows_20260624/agent_orchestration.md`; `Docs/Workflows/agent_orchestration.md` is a redirect stub |
| Persistent long-running agent recovery ledger | archived body at `Docs/Cache/agent_legacy/legacy_workflows_20260624/agent_task_ledger.md`; `Docs/Workflows/agent_task_ledger.md` is a redirect stub |
| Review Sunray migration source | `Docs/Index/sunray_migration_index.md` |
| Identify Sunray150 quadrotor parameters from PX4 ULog | `Docs/Workflows/identify_quadrotor_parameters.md` |
| Add a controller | `Docs/Workflows/add_controller.md` |
| Build Sysblock graphical controller | `Docs/Workflows/build_sysblock_graphical_controller.md` |
| Code review | `Docs/Workflows/code_review.md` |
| Run tests | `Docs/Workflows/run_tests.md` |
| Regression test | `Docs/Workflows/regression_test.md` |
| Pre-submit check | `Docs/Workflows/pre_submit_check.md` |

---

Doctor and self-check workflows are cheap preflight gates. They do not replace
WAL review, evidence review, or Git/quality review for long-running delegated
tasks.

MoSim currently uses a single active Codex thread. Former AgentOS /
visible-thread dispatch material is legacy reference and should not be loaded
for ordinary startup. Legacy workflow bodies moved to
`Docs/Cache/agent_legacy/legacy_workflows_20260624/`; `Docs/Workflows/` keeps short redirect
stubs so old references fail closed instead of reviving old procedure text. Do
not delete executable legacy runtime, hook, checker, protocol, skill, or
automation paths until a separate dependency audit proves they are unused or
updates every reference.

## 2. Recommended Development Order

```text
Docs/Design/架构.md
  -> Docs/Workflows/mainline_operations_board.md
  -> use the board Next Action as the execution selector
  -> if the board selects runtime work:
       Docs/Workflows/sunray_ros1_current_runtime_lane.md
       Docs/Workflows/sunray_ros1_execution_checklist.md
       RViz/Gazebo/log/metrics evidence
  -> if the board selects controller/MWORKS work:
       Docs/Workflows/add_controller.md
       Docs/Workflows/mworks_codegen_controller_runtime.md
       Docs/Design/架构/03_测试调参与证据/测试与评价.md
  -> if the board selects enhancement reopening:
       Docs/Design/架构/01_控制器平台/控制增强与容错.md
       Docs/Design/架构/01_控制器平台/modules/
       minimal Gazebo verification before MWORKS/codegen promotion
  -> if the board selects exploration / swarm planning:
       Docs/Design/架构/02_感知定位与规划集群/规划与编队控制接口.md
       Docs/Design/架构/02_感知定位与规划集群/planners/README.md
       key cards such as MADER-RMADER.md,
       Fast-Multi-Robot-Exploration.md, and Skybrush.md
       source-first local README/launch/topic review before implementation
  -> if the board selects final packaging:
       Docs/Workflows/pre_submit_check.md
```

As of the current board state, this index is only a router. Do not infer the
next mainline task from older Goal/G9/G10 wording here. The mainline board is
the current execution selector: G9/G9.5/G9.6 evidence is already recorded there,
G10 remains a scoped enhancement backlog, and any reopened enhancement must
start from the board-declared minimal Gazebo-verified route rather than from
static-only historical notes.

---

## 3. Scenario Development Workflow

For every new scenario:

```text
1. Add scenario config.
2. Generate reference trajectory.
3. Run PID baseline if applicable.
4. Run optimized controller.
5. Export raw results.
6. Compute metrics.
7. Generate figures.
8. Update report table.
```

Related files:

```text
Docs/Workflows/run_simulation.md
Docs/Workflows/calc_metrics.md
Docs/Workflows/generate_report_figures.md
```

Official baseline scenarios are tracked under:

```text
Config/scenarios/official/example1_pid_baseline.yaml
Config/scenarios/official/example2_pid_baseline.yaml
Config/scenarios/official/example3_pid_baseline.yaml
```

These map directly to `QuadrotorModel.Examples.Example1/2/3`. When Sysplorer
MCP is available, run these first before custom controllers so the official PID
baseline is reproducible.

---

## 4. Controller Development Workflow

Current controller expansion uses the G9 single-thread workflow in
`Docs/Workflows/add_controller.md`. For every new G9 controller or bounded
augmentation:

```text
1. Create the source-basis packet from paper/open-source/formula evidence.
2. Update the controller card and ControllerProfile.
3. Add a blocked candidate ExperimentProfile under Config/profiles/candidates/.
4. Prove the planned candidate fails closed with C-CTRL-01 or the matching augmentation gate.
5. Implement C++/MWORKS/Sysblock/CFunction route through the common IController interface.
6. Run interface/offline consistency checks.
7. Run the G8 single-UAV Gazebo A/B regression template.
8. Run Diff-Planner single-UAV, then three-UAV only after single-UAV passes.
9. Assign PASS / REPORT / CANDIDATE and update profile status plus evidence links.
```

Related files:

```text
Docs/Workflows/add_controller.md
Docs/Workflows/build_sysblock_graphical_controller.md
Docs/Workflows/regression_test.md
Docs/Workflows/code_review.md
```

---

## 5. Report Preparation Workflow

```text
1. Confirm all reported scenarios have metrics.
2. Confirm all figures are saved.
3. Confirm captions and references are ready.
4. Confirm screenshots for installation and MCP are collected.
5. Run pre-submit check.
6. Export user manual PDF.
7. Export simulation report PDF.
8. Record demo video.
```

Related file:

```text
Docs/Workflows/pre_submit_check.md
```

---

## 6. MCP Troubleshooting Workflow

If tools are missing:

```text
1. Check /mcp.
2. Check codex mcp list --json.
3. Check wrapper scripts.
4. Check ~/.codex/config.toml.
5. Remove Windows-side conflicting MCP config.
6. Restart Codex.
7. Check logs.
```

Related file:

```text
Docs/Workflows/debug_mcp.md
```

For graphical system model review, use `Docs/Workflows/run_simulation.md` section
"Direct MCP Review For Graphical System Models". It records the required load
order, the `1401` duplicate-definition trap, and the known embedded graphical
Sysblock multi-input-port limitation.

Official Sysplorer skills in `Docs/Skills/Sysplorer/` are reference material. Project execution should still go through `Docs/Skills/Mworks/` and `Docs/Workflows/`; consult the official skills when a Sysblock/Modelica/hybrid modeling route is unclear.

---

## 7. Automation Strategy

Use Codex prompts with:

```text
goal
input file
MCP tool
output path
validation criteria
```

Good example:

```text
按照 Docs/Workflows/run_simulation.md，使用 Sysplorer MCP 运行 figure8 场景，控制器为 pid_baseline，结果保存到 Results/official/example3_figure8/official_example3_pid_baseline/raw/official_example3_pid_baseline.csv。
```

Bad example:

```text
帮我跑一下仿真。
```

---

## 8. Legacy Parallel-Agent Workflow

MoSim currently uses a single active Codex thread. This section is retained
only as historical reference for legacy cleanup or audit.

| Stream | Typical Task | Output |
|---|---|---|
| Scene research | Compare RflySim/Fab/Gazebo/AirSim scene sources, license limits, file-size risk | Ranked source list and migration notes |
| RflySim smoke | Run local map, vehicle, Mid360/lidar, collision, and point-cloud checks | Small tool patch, smoke log, pass/fail notes |
| MWORKS evidence | Run controller or scenario checks through Sysplorer/Syslab MCP | `Results/` evidence and metrics |
| Documentation | Update architecture, workflow, and acceptance text | `Docs/Design/`, `Docs/`, `Docs/Workflows/` edits |
| Git/quality | Scan large files, inspect diff, run targeted tests, commit/push | Clean Git state or exact blocker |

Historical rules:

1. Assign disjoint write sets before spawning agents.
2. Keep only one Git/quality agent active.
3. Research agents should not write files unless explicitly assigned.
4. The main agent must review all returned changes before commit.
5. If an agent finds a license, credential, activation, or destructive-action
   issue, it must stop that stream and report the blocker.

For current execution, use `Docs/Workflows/single_thread_operating_model.md`
and `Docs/Workflows/mainline_operations_board.md`. Do not spawn or coordinate
parallel visible agents unless the user explicitly reopens that architecture.

---

## 9. Doctor / Self-Check Workflow

Use this before long Git/reference-import/MCP work or when the session state is
unclear:

```bash
python3 Scripts/quality/doctor.py
```

The doctor is intentionally cheap: it checks the project-local Git lock/status,
Git LFS availability, active operating docs, tracked files over the selected
size limit, key workflow files, and MCP wrapper file presence. Live MCP health
still belongs to `/mcp` and `Docs/Workflows/debug_mcp.md`.
