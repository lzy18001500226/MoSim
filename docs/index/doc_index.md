# Documentation Index

> Entry point for project documentation and converted MWORKS reference materials.

## Project Documents

| Topic | File | Purpose |
|---|---|---|
| Project overview | `README.md` | Repository entry point |
| Agent rules | `AGENTS.md` | Codex/MCP usage, project conventions, implementation rules |
| Design documents | `Design/00_系统总体设计.md` to `Design/08_仿真指标与自动评估.md` | Architecture, scope, interfaces, control design, scenarios, and metrics |
| User manual | `docs/user_manual.md` | Usage guide and reproducible command entry points |
| Simulation report | `docs/simulation_report.md` | Current evidence, metrics, figures, and experiment gaps |
| API/tool index | `docs/index/api_index.md` | Available MCP tools, scripts, and API references |
| Workflow index | `docs/index/workflow_index.md` | Repeatable development workflows |
| Variable mapping | `docs/index/variable_mapping.md` | Standard raw CSV names vs Sysplorer result variables |
| MathWorks to MWORKS migration | `docs/index/mathworks_to_mworks_migration.md` | How to translate MATLAB/Simulink skills into MWORKS workflows |
| Sunray migration index | `docs/index/sunray_migration_index.md` | Sunray code/model/config index for Sysplorer migration |

## Project-Local Skills

| Skill | File | Purpose |
|---|---|---|
| MWORKS model context | `Skills/Mworks/mworks-model-context/SKILL.md` | Resolve Sysplorer model/component/port/parameter context before edits |
| MWORKS simulation evidence | `Skills/Mworks/mworks-simulation-evidence/SKILL.md` | Produce and label reproducible MWORKS simulation evidence |
| MWORKS Syslab porting | `Skills/Mworks/mworks-syslab-porting/SKILL.md` | Translate MATLAB/Simulink patterns into project-local MWORKS workflows |
| MWORKS MCP operations | `Skills/Mworks/mworks-mcp-operations/SKILL.md` | Keep MCP usage targeted, quiet, and project-local |
| MWORKS runtime diagnostics | `Skills/Mworks/mworks-runtime-diagnostics/SKILL.md` | Diagnose failed, slow, unstable, or suspicious simulations |
| MWORKS test quality | `Skills/Mworks/mworks-test-quality/SKILL.md` | Run/review tests, targeted simulation checks, regressions, and pre-submit quality gates |
| MWORKS report visualization | `Skills/Mworks/mworks-report-visualization/SKILL.md` | Prepare figures, replay assets, report sections, and video evidence |
| MWORKS Sysblock graphical modeling | `Skills/Mworks/mworks-sysblock-graphical-modeling/SKILL.md` | Build, repair, and validate graphical Sysblock controller diagrams |

## High-Value Workflows

| Workflow | File | Purpose |
|---|---|---|
| Resolve model context | `workflows/resolve_model_context.md` | Confirm model/component/interface before editing |
| Produce simulation evidence | `workflows/produce_simulation_evidence.md` | Build a labeled evidence bundle for report claims |
| Build Sysblock graphical controller | `workflows/build_sysblock_graphical_controller.md` | Create or repair behavior-equivalent graphical Sysblock controllers |

## MWORKS Reference Docs

| Topic | File | Notes |
|---|---|---|
| MWORKS docs entry | `docs/mworks/README.md` | How to use scanned and converted local resource docs |
| Scan summary | `docs/mworks/scan/scan_summary.md` | Relevant file counts and next steps |
| Ranked relevant index | `docs/mworks/scan/relevant_index.md` | Top project-related source files |
| Machine-readable index | `docs/mworks/scan/relevant_files.csv` | CSV for scripts and filtering |
| PDF preview review | `docs/mworks/scan/pdf_review.md` | PDF first-page content relevance evidence |
| Sysplorer category | `docs/mworks/scan/categories/sysplorer_modeling.md` | Sysplorer, Modelica, modeling examples |
| Syslab category | `docs/mworks/scan/categories/syslab_analysis.md` | Syslab, Julia, control analysis |
| Challenge category | `docs/mworks/scan/categories/quadrotor_uav.md` | Intelligent unmanned systems challenge materials |
| Converted PDF index | `docs/mworks/converted/转换索引.md` | Current curated converted PDF list |
| MinerU precise API | `docs/mworks/mcp/mineru_precise_api.md` | Token-based precise parsing, batch upload, polling, errors |
| MATLAB compatibility plan | `docs/mworks/matlab_compat_plan.md` | Plan for converting official MWORKS/MATLAB comparison materials |

## Converted PDF Topics

| Topic | File |
|---|---|
| Syslab/Sysplorer integration 2024a | `docs/mworks/converted/sysplorer/Syslab与Sysplorer双向集成_2024a.md` |
| Syslab/Sysplorer integration 2025b | `docs/mworks/converted/sysplorer/Syslab与Sysplorer双向集成_2025b.md` |
| Modelica behavior syntax | `docs/mworks/converted/sysplorer/Modelica语法详解_模型行为描述.md` |
| Modelica reuse syntax | `docs/mworks/converted/sysplorer/Modelica语法详解_模型重用.md` |
| Syslab control toolbox | `docs/mworks/converted/syslab/MWORKS.Syslab控制系统工具箱.md` |
| Syslab control APP | `docs/mworks/converted/syslab/MWORKS.Syslab控制系统工具箱APP.md` |
| Parameter estimation | `docs/mworks/converted/optimization/MWORKS.Sysplorer参数估计工具箱应用.md` |
| System identification | `docs/mworks/converted/control/Syslab系统辨识工具箱.md` |
| Robust control | `docs/mworks/converted/control/Syslab鲁棒控制工具箱.md` |
| Sysplorer external functions | `docs/mworks/converted/api/MWORKS.Sysplorer外部接口_外部函数.md` |
| Sysplorer Python scripts | `docs/mworks/converted/api/MWORKS.Sysplorer工具箱运行脚本_Python.md` |
| Syslab external functions | `docs/mworks/converted/api/MWORKS.Syslab外部函数调用.md` |
| MWORKS and other scientific software | `docs/mworks/converted/matlab_compat/MWORKS与其他科学计算软件对比.md` |
| MWORKS intro and MATLAB comparison | `docs/mworks/converted/matlab_compat/MWORKS简介及与MATLAB的对比.md` |
| MATLAB compatibility online links | `docs/mworks/converted/matlab_compat/MWORKS与MATLAB在线链接.md` |
| Challenge rules | `docs/mworks/converted/challenge/智能无人系统应用挑战赛_无人车避障竞赛规则.md` |
| Challenge training 1 | `docs/mworks/converted/challenge/智能无人系统应用挑战赛_专项培训一.md` |
| Challenge training 2 | `docs/mworks/converted/challenge/智能无人系统应用挑战赛_专项培训二.md` |

## External Migration References

| Topic | File |
|---|---|
| Sunray Sysplorer migration index | `docs/index/sunray_migration_index.md` |
| Sunray source tree | `references/Sunray/` |
| CUAV/PX6C/V6X/Mid360/ORIN visual references | Source images: `references/CUAV/`; normalized model icons: `QuadrotorModel/Resources/Images/` |

## Design Docs

| Topic | File |
|---|---|
| System overview | `Design/00_系统总体设计.md` |
| Scope and acceptance | `Design/01_需求范围与验收.md` |
| Model interfaces and runtime flow | `Design/02_模型接口与运行流程.md` |
| Control architecture | `Design/03_控制系统架构.md` |
| Safety, fault, and tolerance | `Design/04_安全故障与容错.md` |
| Planning and trajectory generation | `Design/05_路径规划与轨迹生成.md` |
| Formation control | `Design/06_多机编队控制.md` |
| Scenarios and test matrix | `Design/07_场景扰动与测试矩阵.md` |
| Metrics and automated evaluation | `Design/08_仿真指标与自动评估.md` |

## Maintenance Rules

1. List only files that exist in the repository.
2. Store high-value converted references under `docs/mworks/converted/`.
3. Keep noisy one-off extraction output out of the default docs tree.
4. Put repeatable procedures in `workflows/`.
5. Do not duplicate long official documents into `AGENTS.md`.
