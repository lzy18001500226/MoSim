# Documentation Index

> Entry point for project documentation and converted MWORKS reference materials.

## Project Documents

| Topic | File | Purpose |
|---|---|---|
| Project overview | `README.md` | Repository entry point |
| Agent rules | `AGENTS.md` | Codex/MCP usage, project conventions, implementation rules |
| Design documents | `Docs/Design/README.md` | Current system-design source set, architecture, interfaces, gates, and cache/ADR routing |
| CoSim future platform blueprint | `Docs/CoSim/README.md` | Future vehicle-family-first simulation platform research, reviewed backend decisions, shared core, and architecture drafts |
| User manual | `Docs/user_manual.md` | Usage guide and reproducible command entry points |
| Simulation report | `Docs/simulation_report.md` | Current evidence, metrics, figures, and experiment gaps |
| API/tool index | `Docs/Index/api_index.md` | Available MCP tools, scripts, and API references |
| Workflow index | `Docs/Index/workflow_index.md` | Repeatable development workflows |
| Simulation model structure index | `Docs/Index/simulation_model_structure_index.md` | Maintained map of model packages, scenario configs, runner scripts, and result locations |
| Post-simulation task flow | `Docs/Workflows/post_simulation_task_flow.md` | Total queue after simulation: inventory, raw extraction, metrics, quality, figures, evidence, report, and UE transition |
| Variable mapping | `Docs/Index/variable_mapping.md` | Standard raw CSV names vs Sysplorer result variables |
| MathWorks to MWORKS migration | `Docs/Index/mathworks_to_mworks_migration.md` | How to translate MATLAB/Simulink skills into MWORKS workflows |
| Sunray migration index | `Docs/Index/sunray_migration_index.md` | Sunray code/model/config index for current ROS1/Gazebo review and Sysplorer migration |
| PX4 reference index | `Docs/Index/px4_reference_index.md` | PX4 source map for flight modes, failsafe, setpoints, battery, ESC, and actuator interfaces |
| FAST-LIO localization closed-loop foundation | `Docs/Design/MoSim_FASTLIO定位闭环与规划复现基础方案.md` | Sunray ROS1 FAST-LIO -> PX4 EKF -> MAVROS local position state-source plan and EGO/EGOv2/Diff-Planner rerun gates |

## Project-Local Skills

| Skill | File | Purpose |
|---|---|---|
| MWORKS model context | `Docs/Skills/Mworks/mworks-model-context/SKILL.md` | Resolve Sysplorer model/component/port/parameter context before edits |
| MWORKS simulation evidence | `Docs/Skills/Mworks/mworks-simulation-evidence/SKILL.md` | Produce and label reproducible MWORKS simulation evidence |
| MWORKS Syslab porting | `Docs/Skills/Mworks/mworks-syslab-porting/SKILL.md` | Translate MATLAB/Simulink patterns into project-local MWORKS workflows |
| MWORKS MCP operations | `Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md` | Keep MCP usage targeted, quiet, and project-local |
| MWORKS runtime diagnostics | `Docs/Skills/Mworks/mworks-runtime-diagnostics/SKILL.md` | Diagnose failed, slow, unstable, or suspicious simulations |
| MWORKS test quality | `Docs/Skills/Mworks/mworks-test-quality/SKILL.md` | Run/review tests, targeted simulation checks, regressions, and pre-submit quality gates |
| MWORKS report visualization | `Docs/Skills/Mworks/mworks-report-visualization/SKILL.md` | Prepare figures, replay assets, report sections, and video evidence |
| MWORKS Sysblock graphical modeling | `Docs/Skills/Mworks/mworks-sysblock-graphical-modeling/SKILL.md` | Build, repair, and validate graphical Sysblock controller diagrams |

## High-Value Workflows

| Workflow | File | Purpose |
|---|---|---|
| Resolve model context | `Docs/Workflows/resolve_model_context.md` | Confirm model/component/interface before editing |
| Produce simulation evidence | `Docs/Workflows/produce_simulation_evidence.md` | Build a labeled evidence bundle for report claims |
| Post-simulation task flow | `Docs/Workflows/post_simulation_task_flow.md` | Connect simulation completion to result reading, metrics, quality, figures, evidence audit, report candidates, and UE replay readiness |
| Build Sysblock graphical controller | `Docs/Workflows/build_sysblock_graphical_controller.md` | Create or repair behavior-equivalent graphical Sysblock controllers |

## MWORKS Reference Docs

| Topic | File | Notes |
|---|---|---|
| MWORKS docs entry | `Docs/MworksDocs/README.md` | How to use scanned and converted local resource docs |
| Scan summary | `Docs/MworksDocs/scan/scan_summary.md` | Relevant file counts and next steps |
| Ranked relevant index | `Docs/MworksDocs/scan/relevant_index.md` | Top project-related source files |
| Machine-readable index | `Docs/MworksDocs/scan/relevant_files.csv` | CSV for scripts and filtering |
| PDF preview review | `Docs/MworksDocs/scan/pdf_review.md` | PDF first-page content relevance evidence |
| Sysplorer category | `Docs/MworksDocs/scan/categories/sysplorer_modeling.md` | Sysplorer, Modelica, modeling examples |
| Syslab category | `Docs/MworksDocs/scan/categories/syslab_analysis.md` | Syslab, Julia, control analysis |
| Challenge category | `Docs/MworksDocs/scan/categories/quadrotor_uav.md` | Intelligent unmanned systems challenge materials |
| Converted PDF index | `Docs/MworksDocs/converted/转换索引.md` | Current curated converted PDF list |
| MinerU precise API | `Docs/MinerU/mineru_precise_api.md` | Token-based precise parsing, batch upload, polling, errors |
| MATLAB compatibility plan | `Docs/MworksDocs/matlab_compat_plan.md` | Plan for converting official MWORKS/MATLAB comparison materials |

## Converted PDF Topics

| Topic | File |
|---|---|
| Syslab/Sysplorer integration 2024a | `Docs/MworksDocs/converted/sysplorer/Syslab与Sysplorer双向集成_2024a.md` |
| Syslab/Sysplorer integration 2025b | `Docs/MworksDocs/converted/sysplorer/Syslab与Sysplorer双向集成_2025b.md` |
| Modelica behavior syntax | `Docs/MworksDocs/converted/sysplorer/Modelica语法详解_模型行为描述.md` |
| Modelica reuse syntax | `Docs/MworksDocs/converted/sysplorer/Modelica语法详解_模型重用.md` |
| Syslab control toolbox | `Docs/MworksDocs/converted/syslab/MWORKS.Syslab控制系统工具箱.md` |
| Syslab control APP | `Docs/MworksDocs/converted/syslab/MWORKS.Syslab控制系统工具箱APP.md` |
| Parameter estimation | `Docs/MworksDocs/converted/optimization/MWORKS.Sysplorer参数估计工具箱应用.md` |
| System identification | `Docs/MworksDocs/converted/control/Syslab系统辨识工具箱.md` |
| Robust control | `Docs/MworksDocs/converted/control/Syslab鲁棒控制工具箱.md` |
| Sysplorer external functions | `Docs/MworksDocs/converted/api/MWORKS.Sysplorer外部接口_外部函数.md` |
| Sysplorer Python scripts | `Docs/MworksDocs/converted/api/MWORKS.Sysplorer工具箱运行脚本_Python.md` |
| Syslab external functions | `Docs/MworksDocs/converted/api/MWORKS.Syslab外部函数调用.md` |
| MWORKS and other scientific software | `Docs/MworksDocs/converted/matlab_compat/MWORKS与其他科学计算软件对比.md` |
| MWORKS intro and MATLAB comparison | `Docs/MworksDocs/converted/matlab_compat/MWORKS简介及与MATLAB的对比.md` |
| MATLAB compatibility online links | `Docs/MworksDocs/converted/matlab_compat/MWORKS与MATLAB在线链接.md` |
| Challenge rules | `Docs/MworksDocs/converted/challenge/智能无人系统应用挑战赛_无人车避障竞赛规则.md` |
| Challenge training 1 | `Docs/MworksDocs/converted/challenge/智能无人系统应用挑战赛_专项培训一.md` |
| Challenge training 2 | `Docs/MworksDocs/converted/challenge/智能无人系统应用挑战赛_专项培训二.md` |

## External Migration References

| Topic | File |
|---|---|
| Sunray Sysplorer migration index | `Docs/Index/sunray_migration_index.md` |
| Sunray source tree | `References/Sunray/` |
| PX4 source reference index | `Docs/Index/px4_reference_index.md` |
| PX4 source tree | `References/PX4/` |
| CUAV/PX6C/V6X/Mid360/ORIN visual references | Source images: `References/CUAV/`; normalized model icons: `References/MWORKS/QuadrotorModel/Resources/Images/` |

## Design Docs

| Topic | File |
|---|---|
| Design entrypoint | `Docs/Design/README.md` |
| Competition task scope | `Docs/Design/赛题.md` |
| Control-system architecture root | `Docs/Design/MoSim控制体系总览.md` |
| High-level architecture narrative | `Docs/Design/架构.md` |
| Unified controller interface and ABI | `Docs/Design/MoSim统一控制接口规范.md` |
| Single-UAV controller implementation | `Docs/Design/MoSim单机控制器实现规范.md` |
| Code generation and PX4 deployment | `Docs/Design/MoSim控制器代码生成与PX4部署规范.md` |
| Controller tuning and parameter optimization | `Docs/Design/MoSim控制器调参与参数优化规范.md` |
| Controller management and configuration | `Docs/Design/MoSim控制器管理与配置规范.md` |
| Controller testing and evaluation | `Docs/Design/MoSim控制系统测试与评价规范.md` |
| Control enhancement and fault tolerance | `Docs/Design/MoSim控制增强与容错规范.md` |
| Planning and formation interfaces | `Docs/Design/MoSim规划与编队控制接口规范.md` |
| FAST-LIO localization and planner reproduction foundation | `Docs/Design/MoSim_FASTLIO定位闭环与规划复现基础方案.md` |
| Flight-like closeout and C++ refactor | `Docs/Design/MoSim真机化收尾与C++化重构方案.md` |
| Agent workflow and task orchestration | `Docs/Design/MoSim研发工作流与Agent任务编排规范.md` |
| Legacy numbered design archive | `Docs/Design/旧架构/` |
| CoSim future platform entrypoint | `Docs/CoSim/README.md` |
| CoSim platform blueprint | `Docs/CoSim/00_platform/00_CoSim总体蓝图.md` |
| CoSim shared core and data contracts | `Docs/CoSim/10_shared_core/01_共享内核与数据契约.md` |
| CoSim vehicle family tree | `Docs/CoSim/20_vehicle_families/README.md` |
| CoSim backend adapter matrix | `Docs/CoSim/30_backend_adapters/README.md` |
| CoSim research decision index | `Docs/CoSim/research/README.md` |
| CoSim raw research preservation manifest | `Docs/CoSim/cache/source_migration_manifest_20260614.md` |
| Simulation model structure index | `Docs/Index/simulation_model_structure_index.md` |
| Cached absorbed/superseded design inputs | `Docs/Design/cache/absorbed_or_superseded_20260614/` |
| Design rebuild audit | `Docs/Design/cache/design_rebuild_audit_20260610.md` |
| Cached pre-rebuild design inputs | `Docs/Design/cache/pre_rebuild_20260610/README.md` |

## Maintenance Rules

1. List only files that exist in the repository.
2. Store high-value converted references under `Docs/MworksDocs/converted/`.
3. Keep noisy one-off extraction output out of the default docs tree.
4. Put repeatable procedures in `Docs/Workflows/`.
5. Do not duplicate long official documents into `AGENTS.md`.
