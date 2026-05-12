# AGENTS.md

> Project agent instructions for Codex / AI assistants working on the A8 quadrotor attitude and position control project.

---

## 1. Project Overview

This project is for the **A8 四旋翼无人机位姿控制系统设计优化** competition.

The goal is to build a complete simulation-based quadrotor control system on **MWORKS.Sysplorer / Sysblock / Syslab**, starting from the official PID-controlled quadrotor example and extending it into a modular, testable, and report-ready engineering project.

Core technical direction:

```text
Official PID baseline
    ↓
Improved PID / PID-INDI
    ↓
NMPC outer loop
    ↓
INDI attitude inner loop
    ↓
L1-inspired adaptive disturbance compensation
    ↓
Safety filter
    ↓
Fault injection and control allocation reconstruction
    ↓
Path planning and trajectory smoothing
    ↓
Leader-Follower multi-UAV formation control
    ↓
Syslab / MCP automated simulation, metrics, plotting, and report assets
```

Primary project objective:

```text
复杂任务场景
  → 路径/轨迹生成
  → 鲁棒位姿控制
  → 扰动/故障验证
  → 多机编队扩展
  → 自动化指标评估
  → 报告与视频展示
```

---

## 2. Core Principles

When working on this project, always follow these principles:

1. **Control is the main line.**
   The main technical contribution is robust quadrotor attitude and position control, not a general robotics navigation stack.

2. **Modules must be decoupled.**
   Path planning, formation control, MCP automation, safety filtering, fault injection, and metrics evaluation must be replaceable modules.

3. **Every claim needs evidence.**
   Report conclusions must be supported by simulation curves, metrics tables, screenshots, source modules, or experiment logs.

4. **Prefer reproducible workflows.**
   Every experiment should save its scenario configuration, controller parameters, raw results, metrics, and figures.

5. **Use MCP first when working with MWORKS.**
   Use Sysplorer MCP for model-level operations and Syslab MCP for computation, metrics, plotting, and document lookup.

6. **Do not guess APIs.**
   If an API, tool, parameter, or model component is unclear, first search the documentation or query MCP documentation tools.

7. **Keep the deliverables report-ready.**
   Any generated figure, table, or metric should be saved in a location that can be used directly in the final report.

---

## 3. Automation and Safety Boundary

All Codex / AI-agent work in this project must follow the boundary below.

### 3.1 Filesystem Boundary

Before each operation, explicitly treat the following sentence as active:

```text
操作权限仅限 C:\Users\HP\Desktop\Quadrotor
```

The WSL path equivalent is:

```text
/mnt/c/Users/HP/Desktop/Quadrotor
```

Rules:

1. All reads, writes, deletes, moves, searches, Git commands, tests, scripts, and MCP file operations must stay inside this project directory.
2. Do not read or modify files under `/mnt/c/Users/HP`, `/mnt/c/Users/HP/Desktop`, `/home/linux`, `/home/lzy18001500226`, other drives, SSH folders, token files, browser profiles, or personal data directories.
3. The only exception is when the user explicitly requests project infrastructure setup outside the repository, such as SSH authentication, MCP wrapper repair, or environment-variable verification.
4. For exceptions, state the exact external path and reason before acting.
5. Do not run broad destructive commands such as `rm -rf`, `git clean -fd`, or bulk file moves unless the target path is explicitly inside the project and the operation has been summarized first.

### 3.2 Autonomous Execution Rule

Default behavior is to continue working automatically until the requested task is complete.

Do not stop only to ask whether to continue when the next step is clear. Continue through:

- file inspection,
- implementation,
- documentation updates,
- tests,
- smoke simulations,
- result checks,
- Git status / diff review,
- commit,
- push when authentication is already available.

Stop and ask for user intervention only when one of the following occurs:

1. Credentials, tokens, SSH keys, GitHub login, VPN, or GUI permissions are required.
2. A destructive or irreversible action is required, including history rewrite, force push, deleting untracked source materials, or resetting user changes.
3. A command fails and the next fix could risk data loss or affect files outside the project.
4. The task requirement is ambiguous enough that a wrong assumption would change project direction.
5. A license, copyright, privacy, or secret-management concern appears.

Waiting for a long-running command, simulation, MCP response, Git operation, or file conversion is not a reason to stop. Poll until completion or timeout, then continue.

### 3.3 Git Automation Rule

For normal project changes, use this workflow automatically:

```text
git status
  → inspect relevant diff
  → run targeted checks
  → git add
  → git diff --cached --check
  → git commit
  → git push
```

Rules:

1. Commit completed, verified work without asking for a separate "continue" confirmation.
2. Push automatically if Git authentication works.
3. If push fails because authentication is missing, stop and report the exact command and error.
4. Do not force push or rewrite history unless the user explicitly approves that specific action.
5. Never commit secrets, private tokens, local credentials, or generated files larger than GitHub limits.
6. Before commit, check for large files when binary outputs or official materials may have changed.

### 3.4 MCP Minimal-Impact Rule

MCP calls should be minimal, targeted, and non-disruptive.

Rules:

1. Prefer command-line, headless, or background MCP operations when available.
2. Avoid opening GUI windows unless a model simulation, Sysplorer operation, or visual verification genuinely requires it.
3. If a GUI window is opened by Sysplorer / Syslab / MCP, minimize it when possible and avoid bringing it to the foreground repeatedly.
4. Do not use broad MCP discovery calls repeatedly when a targeted tool call is enough.
5. During one development round, keep one reusable Sysplorer / Syslab / MWORKS GUI window open when repeated model checks are expected; do not close it after every small MCP call.
6. Save result evidence under `results/` and documentation-ready assets under `docs/`.
7. If MCP behavior may interrupt the user's desktop, state that risk before running the operation.
8. Do not call MCP tools merely to create activity. Use the smallest set of MCP calls that proves the current engineering claim.
9. If a tool exposes a release, stop, or non-GUI session cleanup API, call it after the useful result is saved.
10. Do not automatically close Sysplorer / Syslab / MWORKS windows before Git. Closing these windows can force license reactivation on the next run. Leave reusable windows open by default.
11. Close Sysplorer / Syslab / MWORKS windows only when the user explicitly asks, when the window is clearly frozen, when a login/activation prompt blocks progress, or when a stale process is opening duplicate sessions uncontrollably.
12. If a GUI window freezes, shows an unexpected login prompt, or an MCP call has no useful response within the planned timeout, stop that MCP sequence, clean up the related process/window if it is clearly identifiable, and continue with file-level work or report the blocker.

### 3.5 Simulation Evidence Rule

Separate offline generated evidence from real MWORKS/MCP simulation evidence.

Rules:

1. A result may be described as **MWORKS/Sysplorer simulation evidence** only if it was produced by loading or running the official model through Sysplorer/Syslab/MCP or MWORKS itself.
2. A result produced by Python/Julia scripts without running the official model must be labeled as **offline algorithm demo**, **reference generator**, or **script-level validation**.
3. Do not use offline generated CSV, metrics, or HTML replay as a substitute for official model reproduction.
4. When adding new results, record the source path or mechanism in the scenario, report, or commit summary:
   - `source=MWORKS_MCP` for MCP-driven model simulation;
   - `source=MWORKS_GUI` for manually run MWORKS simulation;
   - `source=offline_script` for generated validation data.
5. Before claiming a controller is integrated into `QuadrotorModel`, verify the model replacement location, signal interface, and run result through MCP or manual MWORKS evidence.
6. For each MCP-driven simulation, save at least the model name, scenario config, result variables, raw output path, metrics path, and any MCP/tool error log.
7. For every formal controller simulation claim, maintain a corresponding graphical Sysblock controller model that expresses the same system structure and time behavior. A graphical Sysblock file is not only a screenshot wrapper: it must expose the relevant signal path, saturation, filtering, discrete state, delay, switch/mode logic, fault-estimation logic, and allocation behavior used by the simulation.
8. Equation-form Sysblock models may be used as temporary full-plant integration bridges when Sysplorer/Sysblock embedding has compiler limitations, but they do not replace the graphical Sysblock deliverable. Mark the graphical counterpart as incomplete until both `structure_ok=true` and `behavior_equivalence_ok=true`.
9. Do not present a controller scenario as complete if its numerical simulation has no behavior-equivalent graphical Sysblock counterpart. In that case, label the result as equation-bridge evidence and keep the graphical model task open.

### 3.6 Simulation Cleanup Rule

For MWORKS simulations:

1. Run `check_model` before simulation.
2. Run the smallest simulation that validates the current change first.
3. Read required result variables after simulation.
4. Save logs or smoke-test evidence only when useful.
5. Keep one Sysplorer / Syslab / MWORKS GUI window open during a related batch of checks to avoid repeated startup cost and license reactivation. Do not close it before Git unless the user asks or it is blocking progress.
6. Do not leave long-running simulations active after the task is complete.
7. Prefer one active Sysplorer/Syslab session at a time unless parallel simulation is explicitly required.
8. Reuse an existing session for related operations instead of opening many windows.
9. If repeated simulations open multiple windows, stop opening new MCP sessions, clean up clearly identifiable stale windows before Git, and prefer fixing model files offline before retrying MCP.
10. Do not document a model as verified unless its latest version has a successful `load_file` and `check_model` log, or the report explicitly marks it as an unverified draft.

---

## 4. Project Directory Convention

Project structure should stay lean. Keep directories only when they contain
real project inputs, outputs, or documentation; do not create placeholder
folders just to match a future plan.

```text
A8-Quadrotor-Control/
├── AGENTS.md
├── README.md
├── docs/
│   ├── user_manual.md
│   ├── simulation_report.md
│   ├── mworks/
│   │   ├── converted/
│   │   ├── scan/
│   │   └── mcp/
│   └── index/
│       ├── doc_index.md
│       ├── api_index.md
│       └── workflow_index.md
├── workflows/
│   ├── debug_mcp.md
│   ├── run_simulation.md
│   ├── read_results.md
│   ├── calc_metrics.md
│   ├── generate_report_figures.md
│   ├── add_controller.md
│   ├── code_review.md
│   ├── run_tests.md
│   ├── smoke_test.md
│   ├── regression_test.md
│   └── pre_submit_check.md
├── controllers/
│   ├── pid/
│   ├── improved_pid/
│   └── nmpc_indi_l1/
├── planners/
│   └── waypoint/
├── scenarios/
│   ├── hover/
│   ├── figure8/
│   └── wind/
├── scripts/
│   ├── calc_metrics.jl
│   ├── plot_results.jl
│   ├── scan_mworks_docs.py
│   ├── convert_mworks_pdfs.py
│   └── qa_check.py
├── tests/
│   ├── fixtures/
│   └── smoke/
├── results/
│   └── test_reports/
```

Create `models/`, `results/{group}/{scene}/{experiment}/raw/`, `results/{group}/{scene}/{experiment}/metrics/`, `results/{group}/{scene}/{experiment}/figures/`, or
`docs/figures/` only when there is actual content to store. The raw official
MWORKS package is not required after the useful documents have been promoted to
`docs/mworks/converted/`; use a temporary `--source` path only when rescanning
new official materials.

---

## 5. MCP and Agent Skill Routing

This file records only the highest-priority operating rules. Detailed MCP tool
lists, wrapper commands, troubleshooting steps, and translated MathWorks /
Simulink patterns live in the indexes, workflows, and project-local skills.

| Need | Primary Entry |
|---|---|
| MCP tool list and preferred sequences | `docs/index/api_index.md` |
| MCP wrapper/debug steps | `workflows/debug_mcp.md` |
| Minimal-impact MCP operation rules | `Skills/Mworks/mworks-mcp-operations/SKILL.md` |
| Sysplorer model/component context | `Skills/Mworks/mworks-model-context/SKILL.md` |
| MWORKS simulation evidence | `Skills/Mworks/mworks-simulation-evidence/SKILL.md` |
| Syslab/MATLAB/Simulink migration | `Skills/Mworks/mworks-syslab-porting/SKILL.md` |
| Failed/slow/wrong simulation diagnostics | `Skills/Mworks/mworks-runtime-diagnostics/SKILL.md` |
| Tests, review, pre-submit quality | `Skills/Mworks/mworks-test-quality/SKILL.md` |
| Report figures, replay, video evidence | `Skills/Mworks/mworks-report-visualization/SKILL.md` |

Non-negotiable MCP rules:

1. Use the smallest targeted MCP call sequence that proves the current claim.
2. Check models before simulation and verify result variables after simulation.
3. Keep `source=MWORKS_MCP`, `source=MWORKS_GUI`, and `source=offline_script` evidence clearly separated.
4. Do not write tokens, SSH keys, API keys, or private configuration into tracked files.
5. Keep filesystem access project-local unless the user explicitly asks for infrastructure setup.

---

## 6. Documentation Strategy

The official MWORKS documentation may be large. Do not put all official documentation directly into this file.

Recommended approach:

```text
Official docs / PDFs / web docs
    ↓
Convert to Markdown with MinerU or equivalent
    ↓
Store under docs/mworks/
    ↓
Build manual indexes under docs/index/
    ↓
Write common workflows under workflows/
    ↓
Use MCP documentation tools when unsure
```

Recommended documentation folders:

```text
docs/mworks/
├── sysplorer/
├── syslab/
├── sysblock/
└── mcp/

docs/index/
├── doc_index.md
├── api_index.md
└── workflow_index.md
```

Rules:

1. Use `docs/index/doc_index.md` as the entry point for official documentation.
2. Use `docs/index/api_index.md` for API and MCP tool lookup.
3. Use `docs/index/workflow_index.md` for common project workflows.
4. Do not paste large documentation dumps into `AGENTS.md`.
5. Keep `AGENTS.md` as the project behavior and workflow control file.
6. If documentation is missing or unclear, use MCP documentation tools.

### 6.1 Project-Local MWORKS Skills

This repository includes compact project-local skills translated from MathWorks / Simulink agent patterns:

| Skill | Use When | File |
|---|---|---|
| `mworks-model-context` | Resolving Sysplorer model, component, port, parameter, controller replacement location, or signal interface | `Skills/Mworks/mworks-model-context/SKILL.md` |
| `mworks-simulation-evidence` | Running MWORKS simulations, reading results, computing metrics, or producing report evidence | `Skills/Mworks/mworks-simulation-evidence/SKILL.md` |
| `mworks-syslab-porting` | Translating MATLAB/Simulink skills, scripts, tests, plotting, or performance workflows into MWORKS/Syslab/Sysplorer practice | `Skills/Mworks/mworks-syslab-porting/SKILL.md` |
| `mworks-mcp-operations` | MCP session, wrapper, and minimal-impact operation behavior | `Skills/Mworks/mworks-mcp-operations/SKILL.md` |
| `mworks-runtime-diagnostics` | Failed, slow, unstable, or suspicious simulation diagnostics | `Skills/Mworks/mworks-runtime-diagnostics/SKILL.md` |
| `mworks-test-quality` | Tests, reviews, smoke checks, regressions, and pre-submit gates | `Skills/Mworks/mworks-test-quality/SKILL.md` |
| `mworks-report-visualization` | Report figures, replay assets, video evidence, and honest visual claims | `Skills/Mworks/mworks-report-visualization/SKILL.md` |

Use `Skills/Mworks/` as the default execution layer for this project. Treat upstream MATLAB / Simulink skills under `Skills/Matlab/` and `Skills/Simulink/` as second-level references only: consult them when the MWORKS skills do not cover a task, translate the useful pattern into MWORKS terms, and then update the relevant `Skills/Mworks/*/SKILL.md`, `workflows/`, or `docs/index/` file so the project improves over time. Verify every executable API call through MWORKS docs or MCP.

---

## 7. Core Workflow Routing

Use `docs/index/workflow_index.md` as the workflow entry point. Do not duplicate long workflow steps in this file.

| Task | Workflow |
|---|---|
| Run one simulation | `workflows/run_simulation.md` |
| Resolve model/component interface | `workflows/resolve_model_context.md` |
| Produce labeled evidence bundle | `workflows/produce_simulation_evidence.md` |
| Read exported results | `workflows/read_results.md` |
| Calculate metrics | `workflows/calc_metrics.md` |
| Generate report figures/replay | `workflows/generate_report_figures.md` |
| Add a controller | `workflows/add_controller.md` |
| Run tests | `workflows/run_tests.md` |
| Smoke/regression tests | `workflows/smoke_test.md`, `workflows/regression_test.md` |
| Code review | `workflows/code_review.md` |
| Pre-submit check | `workflows/pre_submit_check.md` |

All workflow outputs should be report-ready: scenario/config, raw result, metrics, figure/replay, source label, and pass/fail summary when applicable.

## 8. Algorithm Source of Truth

Algorithm details live in `Design/`. Keep this file limited to routing and non-negotiable project constraints.

| Topic | Design File |
|---|---|
| Overall architecture and innovation line | `Design/00_系统总体设计.md` |
| Scope, P0/P1/P2, acceptance | `Design/01_需求范围与验收.md` |
| Model interface, coordinates, buses | `Design/02_模型接口与运行流程.md` |
| PID / NMPC / INDI / L1-inspired control | `Design/03_控制系统架构.md` |
| Safety filter, fault injection, tolerance | `Design/04_安全故障与容错.md` |
| Path planning and trajectory generation | `Design/05_路径规划与轨迹生成.md` |
| Formation control | `Design/06_多机编队控制.md` |
| Scenario matrix | `Design/07_场景扰动与测试矩阵.md` |
| Metrics and evaluation criteria | `Design/08_仿真指标与自动评估.md` |

Core constraints:

1. Preserve the official PID baseline.
2. Do not overwrite official model files silently.
3. Treat planning/formation as upper-layer modules around the control contribution.
4. Use `L1-inspired` unless a complete L1 theoretical implementation is delivered.
5. Record both tracking metrics and constraint/safety metrics when safety filtering affects behavior.

## 9. Review and Testing Routing

Use `Skills/Mworks/mworks-test-quality/SKILL.md` for quality decisions.

| Need | File |
|---|---|
| Code review checklist | `workflows/code_review.md` |
| Test execution | `workflows/run_tests.md` |
| Smoke test | `workflows/smoke_test.md` |
| Regression test | `workflows/regression_test.md` |
| Final packaging check | `workflows/pre_submit_check.md` |
| Project structure and evidence guard | `scripts/qa_check.py` |

Before commit, run the smallest relevant checks and `git diff --check`.

## 10. Report and Figure Routing

Use `Skills/Mworks/mworks-report-visualization/SKILL.md` when producing figures, replay assets, report sections, or demo-video material.

| Need | File |
|---|---|
| Current evidence and report claims | `docs/simulation_report.md` |
| User-facing reproduction guide | `docs/user_manual.md` |
| Figure generation workflow | `workflows/generate_report_figures.md` |
| Metrics definitions | `Design/08_仿真指标与自动评估.md` |

Every comparison claim must trace to raw data, metrics, and a saved figure or replay asset.

## 11. Troubleshooting Routing

Use `workflows/debug_mcp.md` and `Skills/Mworks/mworks-mcp-operations/SKILL.md` for MCP troubleshooting.

Common routing:

| Symptom | Route |
|---|---|
| `/mcp` shows `Tools: (none)` | `workflows/debug_mcp.md` |
| Sysplorer/Syslab GUI/session behavior | `Skills/Mworks/mworks-mcp-operations/SKILL.md` |
| Failed model check/simulation | `Skills/Mworks/mworks-runtime-diagnostics/SKILL.md` |
| Missing result variables | `docs/index/variable_mapping.md` and `workflows/read_results.md` |

`Auth: Unsupported` is normal for local stdio MCP servers and is not a failure.

## 12. Common Development Prompts

Use precise prompts when asking Codex to work.

Good prompts:

```text
按照 AGENTS.md 和 workflows/run_simulation.md，使用 Sysplorer MCP 运行 figure8 场景，控制器为 pid_baseline，结果保存到 results/official/example3_figure8/official_example3_pid_baseline/raw/official_example3_pid_baseline.csv。
```

```text
按照 workflows/calc_metrics.md，使用 Syslab MCP 运行 scripts/calc_metrics.jl，计算 results/official/example3_figure8/official_example3_pid_baseline/raw/official_example3_pid_baseline.csv 的 RMSE、最大误差和控制能量，并保存到 results/official/example3_figure8/official_example3_pid_baseline/metrics/official_example3_pid_baseline.json。
```

```text
按照 workflows/code_review.md，对 controllers/nmpc/ 的改动进行接口兼容性和硬编码路径审查。
```

```text
按照 workflows/pre_submit_check.md，检查当前项目是否满足初赛提交要求。
```

Avoid vague prompts:

```text
帮我看看这个怎么仿真。
```

Prefer task-specific prompts with:

```text
目标
输入文件
使用工具
输出路径
验收标准
```

After every MWORKS simulation, run or verify `scripts/evaluate_result_quality.py --write-metrics`. Treat `check_model ok` / `simulate_model ok` as execution evidence only. If `quality_status=needs_iteration`, keep the evidence, update the controller/scenario, and rerun before claiming the work is complete.

---

### Git / Filesystem / MinerU Prompts

```text
检查当前 git 状态，说明哪些文件被修改、哪些是新增文件，并判断是否有不应该提交的文件。
```

```text
审查当前 git diff，重点检查硬编码路径、接口变更、结果文件缺失、测试是否需要更新。
```

```text
根据当前 git diff 生成一条规范 commit message，包含改动内容、原因和已运行的测试。
```

```text
我想回退刚才的改动。请先查看 git status 和 diff，告诉我有哪些安全回退方案，不要直接执行破坏性命令。
```

```text
使用 Filesystem MCP 检查项目目录结构，确认 workflows、docs/index、scripts、results 是否完整。
```

```text
使用 MinerU MCP 将指定官方 PDF 转为 Markdown，保存到 docs/mworks/converted/，然后更新 docs/index/doc_index.md。
```

```text
使用 Git MCP 审查 AGENTS.md 的改动，检查 Markdown 代码块是否闭合、章节编号是否合理、是否存在重复或冲突规则。
```

---

## 13. Deliverable Checklist

Final submission should contain:

```text
complete MWORKS model files
controller source files
trajectory/planning scripts
scenario configuration files
batch simulation scripts
raw simulation results
metrics tables
figures
user manual PDF
simulation analysis report PDF
demo video
README
AGENTS.md
```

Before final packaging:

1. Run pre-submit check.
2. Ensure all report figures exist.
3. Ensure all metrics tables match report values.
4. Ensure video only shows implemented functions.
5. Ensure non-original code and references are marked.
6. Ensure project can be opened and reproduced from user manual.

---

## 14. Final Development Policy

When uncertain:

1. Prefer querying MCP documentation tools over guessing.
2. Prefer running a small smoke test over assuming correctness.
3. Prefer saving intermediate results over relying on memory.
4. Prefer modular implementation over tightly coupled hacks.
5. Prefer report-ready artifacts over temporary screenshots.
6. Prefer clear downgrade paths over risky overengineering.

The project is successful if it forms a reproducible closed loop:

```text
scenario configuration
  → model simulation
  → result extraction
  → metric calculation
  → figure generation
  → report conclusion
```
