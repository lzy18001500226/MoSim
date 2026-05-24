# Documentation Index

> Entry point for project documentation and converted MWORKS reference materials.

## Project Documents

| Topic | File | Purpose |
|---|---|---|
| Project overview | `README.md` | Repository entry point |
| Agent rules | `AGENTS.md` | Codex/MCP usage, project conventions, implementation rules |
| Design documents | `Docs/Design/00_系统总体设计.md` to `Docs/Design/08_仿真指标与自动评估.md` | Architecture, scope, interfaces, control design, scenarios, and metrics |
| User manual | `Docs/user_manual.md` | Usage guide and reproducible command entry points |
| Simulation report | `Docs/simulation_report.md` | Current evidence, metrics, figures, and experiment gaps |
| API/tool index | `Docs/Index/api_index.md` | Available MCP tools, scripts, and API references |
| Workflow index | `Docs/Index/workflow_index.md` | Repeatable development workflows |
| Variable mapping | `Docs/Index/variable_mapping.md` | Standard raw CSV names vs Sysplorer result variables |
| MathWorks to MWORKS migration | `Docs/Index/mathworks_to_mworks_migration.md` | How to translate MATLAB/Simulink skills into MWORKS workflows |
| Sunray migration index | `Docs/Index/sunray_migration_index.md` | Sunray code/model/config index for Sysplorer migration |
| PX4 reference index | `Docs/Index/px4_reference_index.md` | PX4 source map for flight modes, failsafe, setpoints, battery, ESC, and actuator interfaces |

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
| Build Sysblock graphical controller | `Docs/Workflows/build_sysblock_graphical_controller.md` | Create or repair behavior-equivalent graphical Sysblock controllers |

## MWORKS Reference Docs

| Topic | File | Notes |
|---|---|---|
| MWORKS docs entry | `Docs/Mworks/README.md` | How to use scanned and converted local resource docs |
| Scan summary | `Docs/Mworks/scan/scan_summary.md` | Relevant file counts and next steps |
| Ranked relevant index | `Docs/Mworks/scan/relevant_index.md` | Top project-related source files |
| Machine-readable index | `Docs/Mworks/scan/relevant_files.csv` | CSV for scripts and filtering |
| PDF preview review | `Docs/Mworks/scan/pdf_review.md` | PDF first-page content relevance evidence |
| Sysplorer category | `Docs/Mworks/scan/categories/sysplorer_modeling.md` | Sysplorer, Modelica, modeling examples |
| Syslab category | `Docs/Mworks/scan/categories/syslab_analysis.md` | Syslab, Julia, control analysis |
| Challenge category | `Docs/Mworks/scan/categories/quadrotor_uav.md` | Intelligent unmanned systems challenge materials |
| Converted PDF index | `Docs/Mworks/converted/转换索引.md` | Current curated converted PDF list |
| MinerU precise API | `Docs/Mworks/mcp/mineru_precise_api.md` | Token-based precise parsing, batch upload, polling, errors |
| MATLAB compatibility plan | `Docs/Mworks/matlab_compat_plan.md` | Plan for converting official MWORKS/MATLAB comparison materials |

## Converted PDF Topics

| Topic | File |
|---|---|
| Syslab/Sysplorer integration 2024a | `Docs/Mworks/converted/sysplorer/Syslab与Sysplorer双向集成_2024a.md` |
| Syslab/Sysplorer integration 2025b | `Docs/Mworks/converted/sysplorer/Syslab与Sysplorer双向集成_2025b.md` |
| Modelica behavior syntax | `Docs/Mworks/converted/sysplorer/Modelica语法详解_模型行为描述.md` |
| Modelica reuse syntax | `Docs/Mworks/converted/sysplorer/Modelica语法详解_模型重用.md` |
| Syslab control toolbox | `Docs/Mworks/converted/syslab/MWORKS.Syslab控制系统工具箱.md` |
| Syslab control APP | `Docs/Mworks/converted/syslab/MWORKS.Syslab控制系统工具箱APP.md` |
| Parameter estimation | `Docs/Mworks/converted/optimization/MWORKS.Sysplorer参数估计工具箱应用.md` |
| System identification | `Docs/Mworks/converted/control/Syslab系统辨识工具箱.md` |
| Robust control | `Docs/Mworks/converted/control/Syslab鲁棒控制工具箱.md` |
| Sysplorer external functions | `Docs/Mworks/converted/api/MWORKS.Sysplorer外部接口_外部函数.md` |
| Sysplorer Python scripts | `Docs/Mworks/converted/api/MWORKS.Sysplorer工具箱运行脚本_Python.md` |
| Syslab external functions | `Docs/Mworks/converted/api/MWORKS.Syslab外部函数调用.md` |
| MWORKS and other scientific software | `Docs/Mworks/converted/matlab_compat/MWORKS与其他科学计算软件对比.md` |
| MWORKS intro and MATLAB comparison | `Docs/Mworks/converted/matlab_compat/MWORKS简介及与MATLAB的对比.md` |
| MATLAB compatibility online links | `Docs/Mworks/converted/matlab_compat/MWORKS与MATLAB在线链接.md` |
| Challenge rules | `Docs/Mworks/converted/challenge/智能无人系统应用挑战赛_无人车避障竞赛规则.md` |
| Challenge training 1 | `Docs/Mworks/converted/challenge/智能无人系统应用挑战赛_专项培训一.md` |
| Challenge training 2 | `Docs/Mworks/converted/challenge/智能无人系统应用挑战赛_专项培训二.md` |

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
| System overview | `Docs/Design/00_系统总体设计.md` |
| Scope and acceptance | `Docs/Design/01_需求范围与验收.md` |
| Model interfaces and runtime flow | `Docs/Design/02_模型接口与运行流程.md` |
| Control architecture | `Docs/Design/03_控制系统架构.md` |
| Safety, fault, and tolerance | `Docs/Design/04_安全故障与容错.md` |
| Planning and trajectory generation | `Docs/Design/05_路径规划与轨迹生成.md` |
| Formation control | `Docs/Design/06_多机编队控制.md` |
| Scenarios and test matrix | `Docs/Design/07_场景扰动与测试矩阵.md` |
| Metrics and automated evaluation | `Docs/Design/08_仿真指标与自动评估.md` |

## Maintenance Rules

1. List only files that exist in the repository.
2. Store high-value converted references under `Docs/Mworks/converted/`.
3. Keep noisy one-off extraction output out of the default docs tree.
4. Put repeatable procedures in `Docs/Workflows/`.
5. Do not duplicate long official documents into `AGENTS.md`.
