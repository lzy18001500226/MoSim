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

## 3. Project Directory Convention

Recommended project structure:

```text
A8-Quadrotor-Control/
├── AGENTS.md
├── README.md
├── docs/
│   ├── user_manual.md
│   ├── simulation_report.md
│   ├── figures/
│   ├── mworks/
│   │   ├── sysplorer/
│   │   ├── syslab/
│   │   ├── sysblock/
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
├── models/
│   ├── baseline_pid/
│   ├── improved_pid/
│   ├── nmpc_indi_l1/
│   ├── planning/
│   └── formation/
├── controllers/
│   ├── pid/
│   ├── improved_pid/
│   ├── nmpc/
│   ├── indi/
│   ├── l1_adaptive/
│   ├── safety_filter/
│   └── allocation/
├── planners/
│   ├── waypoint/
│   ├── astar/
│   ├── rrt_star/
│   ├── kinodynamic_astar/
│   ├── bspline/
│   └── min_snap/
├── scenarios/
│   ├── hover/
│   ├── step/
│   ├── figure8/
│   ├── spiral/
│   ├── wind/
│   ├── motor_fault/
│   ├── obstacle/
│   └── formation/
├── scripts/
│   ├── calc_metrics.jl
│   ├── plot_results.jl
│   ├── batch_experiment.jl
│   ├── export_report_assets.jl
│   └── qa_check.py
├── tests/
│   ├── test_config.py
│   ├── test_metrics.py
│   ├── test_trajectory.py
│   ├── test_controller_interface.py
│   └── smoke/
├── results/
│   ├── raw/
│   ├── metrics/
│   ├── figures/
│   └── videos/
└── references/
```

If the real project has a different structure, preserve the existing structure but maintain the same conceptual separation.

---

## 4. MCP Tools

This project uses Codex through MCP to call **MWORKS.Sysplorer** and **MWORKS.Syslab**.

MCP is used for:

- model loading,
- model checking,
- simulation execution,
- result reading,
- Julia execution,
- documentation lookup,
- metrics computation,
- figure generation,
- automation of repeatable simulation workflows.

---

### 4.1 MCP Configuration State

The Codex `/mcp` command should show the following MCP servers.

```text
syslab
  Command: /home/lzy18001500226/mcp-wrappers/syslab_mcp.sh
  Auth: Unsupported
  Tools:
    detect_syslab_toolboxes
    evaluate_julia_code
    list_sessions
    map_matlab_functions_to_julia
    read_syslab_doc
    read_syslab_skill
    restart_julia
    run_julia_file
    search_syslab_docs

sysplorer_mcp
  Command: /home/lzy18001500226/mcp-wrappers/sysplorer_mcp.sh
  Auth: Unsupported
  Tools:
    call_code
    check_model
    get_api_document
    get_lib_model_document
    load_library
    model_manager
    plot_manager
    resources_retrieval
    result_manager
    session_manager
    simulate_model
    smart_layout
    translate_model

filesystem
  Command: /home/lzy18001500226/mcp-wrappers/filesystem_mcp.sh
  Auth: Unsupported
  Tools:
    create_directory
    directory_tree
    edit_file
    get_file_info
    list_allowed_directories
    list_directory
    list_directory_with_sizes
    move_file
    read_file
    read_media_file
    read_multiple_files
    read_text_file
    search_files
    write_file

git
  Command: uvx mcp-server-git --repository /mnt/c/Users/HP/Desktop/Quadrotor
  Auth: Unsupported
  Tools:
    git_add
    git_branch
    git_checkout
    git_commit
    git_create_branch
    git_diff
    git_diff_staged
    git_diff_unstaged
    git_log
    git_reset
    git_show
    git_status

mineru
  Command: uvx mineru-open-mcp
  Auth: Unsupported
  Tools:
    get_ocr_languages
    parse_documents
```

Important:

- `Auth: Unsupported` is normal for local stdio MCP servers.
- MCP success is determined by whether `Tools` are listed.
- `Tools: (none)` means the MCP server failed to initialize.
- Do not treat `Auth: Unsupported` as a failure.
- GitHub MCP is not required at the current stage. Local Git MCP plus SSH-based Git is enough for local version control, rollback, and commit workflows.

---

### 4.2 Sysplorer MCP Usage Rules

Sysplorer MCP is used for model-level operations.

Use Sysplorer MCP for:

| Task | Preferred tool |
|---|---|
| Start, connect, probe, reconnect, or close Sysplorer sessions | `session_manager` |
| Load Modelica standard libraries or commercial model libraries | `load_library` |
| Open, save, inspect, create, or manage models | `model_manager` |
| Check model instantiation and compilation | `check_model` |
| Translate model or generate simulation code | `translate_model` |
| Run automatic, independent, or real-time simulation | `simulate_model` |
| Read result files, variables, time series, or values at specific times | `result_manager` |
| Plot results or create animations in Sysplorer | `plot_manager` |
| Query Sysplorer Python API documentation | `get_api_document` |
| Query loaded model library documentation | `get_lib_model_document` |
| Search built-in rules, examples, and troubleshooting resources | `resources_retrieval` |
| Run scripts or Sysblock automation | `call_code` |
| Automatically organize model layout | `smart_layout` |

Required Sysplorer workflow:

```text
session_manager
  → load_library
  → model_manager
  → check_model
  → simulate_model
  → result_manager
  → plot_manager / Syslab metrics
```

Rules:

1. Before running a simulation, call `check_model`.
2. After simulation, call `result_manager` to verify required result variables exist.
3. Before changing model structure, back up the model file.
4. If API usage is unclear, call `get_api_document`.
5. If component ports, parameters, or model meanings are unclear, call `get_lib_model_document`.
6. If a model operation fails, search `resources_retrieval` before guessing.
7. Use `smart_layout` only after model structure is stable.
8. Do not silently overwrite model files.

---

### 4.3 Syslab MCP Usage Rules

Syslab MCP is used for Julia execution, metrics computation, plotting, and document lookup.

Use Syslab MCP for:

| Task | Preferred tool |
|---|---|
| Check Syslab, Julia, and installed packages | `detect_syslab_toolboxes` |
| Execute short Julia snippets | `evaluate_julia_code` |
| Execute local Julia scripts | `run_julia_file` |
| Restart Julia session | `restart_julia` |
| List active sessions | `list_sessions` |
| Search local Syslab documentation | `search_syslab_docs` |
| Read local Syslab documentation body | `read_syslab_doc` |
| Map MATLAB functions to Syslab Julia alternatives | `map_matlab_functions_to_julia` |
| Read Syslab skill markdown | `read_syslab_skill` |

Recommended Syslab workflow:

```text
detect_syslab_toolboxes
  → search_syslab_docs / read_syslab_doc
  → evaluate_julia_code or run_julia_file
  → save metrics / figures
```

Rules:

1. Use `evaluate_julia_code` for small calculations and environment checks.
2. Use `run_julia_file` for batch experiments, metrics, and plotting.
3. If a Syslab function is unclear, call `search_syslab_docs`.
4. If converting MATLAB logic, call `map_matlab_functions_to_julia`.
5. If Julia becomes unstable, call `restart_julia`.
6. Save all metrics to `results/metrics/`.
7. Save all generated figures to `docs/figures/` or `results/figures/`.
8. Prefer reusable `.jl` scripts for repeated metrics and plotting.

--- 

### 4.4 Git MCP Usage Rules

This project uses Git MCP for local repository inspection, change tracking, code review support, commit preparation, and rollback assistance.

GitHub MCP is not required at the current stage. Remote GitHub operations such as `git pull` and `git push` are handled through normal Git with SSH keys. Git MCP is used only for local repository understanding and safe development workflows.

Use Git MCP for:

| Task | Purpose |
|---|---|
| Check repository status | Understand modified, staged, untracked, or deleted files |
| Inspect local diff | Review code/model/script/document changes before commit |
| Inspect commit history | Understand recent changes and rollback points |
| Generate commit message | Summarize changes in a clear engineering style |
| Support rollback | Identify safe restore or reset targets |
| Support code review | Explain risks, affected modules, and required tests |

Rules:

1. Before modifying code, inspect the current Git status.
2. Before major changes, recommend creating a commit or backup branch.
3. Before committing, inspect the diff and summarize what changed.
4. Do not automatically run destructive Git commands unless explicitly requested.
5. Destructive commands include:
   - `git reset --hard`
   - `git clean -fd`
   - `git checkout -- <file>`
   - `git restore <file>`
   - deleting branches
   - rewriting history
6. If rollback is needed, first explain what will be lost.
7. Prefer safe rollback methods:
   - create a backup branch,
   - stash changes,
   - restore only specific files,
   - revert a commit instead of rewriting history.
8. Do not commit generated large files unless they are required deliverables.
9. Do not commit secrets, tokens, API keys, local absolute paths, or private logs.
10. Before final submission, ensure `git status` is clean or all remaining changes are intentionally documented.

Recommended local Git workflow:

```text
git status
  → inspect diff
  → run code review
  → run tests / smoke tests
  → generate commit message
  → commit
```

Recommended rollback workflow:

```text
git status
  → identify changed files
  → decide whether to stash, restore specific files, or create backup branch
  → perform rollback only after explicit confirmation
```

Commit message style:

```text
type(scope): short summary

- What changed
- Why it changed
- Tests or simulations performed
- Result files or metrics affected
```

Example:

```text
feat(controller): add nmpc-indi-l1 simulation workflow

- Add controller workflow documentation
- Add metrics calculation checklist
- Add QA pre-submit checks
- Verify MCP tools for Sysplorer and Syslab
```
---

### 4.5 Filesystem MCP Usage Rules

This project uses Filesystem MCP for project-local file operations only.

Filesystem MCP must be restricted to the project directory:

```text
/mnt/c/Users/HP/Desktop/Quadrotor
```

Use Filesystem MCP for:

| Task | Preferred tool |
|---|---|
| List project files | `list_directory` |
| Show project tree | `directory_tree` |
| Read one file | `read_text_file` or `read_file` |
| Read multiple files | `read_multiple_files` |
| Search project files | `search_files` |
| Create directory | `create_directory` |
| Write new file | `write_file` |
| Edit existing file | `edit_file` |
| Move file | `move_file` |
| Inspect file metadata | `get_file_info` |
| Check allowed roots | `list_allowed_directories` |
| Read media file | `read_media_file` |

Rules:

1. Filesystem MCP may only access the project directory.
2. Do not grant Filesystem MCP access to `/`, `/mnt/c`, `/mnt/d`, `C:\`, or `D:\`.
3. Before editing important files, inspect Git status and diff.
4. Prefer `edit_file` for small targeted changes.
5. Prefer `write_file` only when creating a new file or fully replacing generated documentation.
6. Do not overwrite model files, report files, or experiment results without checking Git diff first.
7. Do not use Filesystem MCP to read secrets, tokens, SSH keys, or private configuration files.
8. Use Git MCP before and after large file operations to confirm the change set.
9. Generated documentation should be saved under `docs/`, `workflows/`, or `scripts/`.
10. Generated figures and metrics should be saved under `results/` or `docs/figures/`.

Recommended file operation workflow:

```text
git_status
  → filesystem list/search/read
  → edit_file or write_file
  → git_diff
  → code review
  → test
  → commit
```

### 4.6 MinerU MCP Usage Rules

This project uses MinerU MCP for converting official documents, PDFs, PPTX files, DOCX files, screenshots, images, and HTML documents into Markdown.

Use MinerU MCP for:

| Task | Preferred tool |
|---|---|
| Convert documents to Markdown | `parse_documents` |
| Check OCR language support | `get_ocr_languages` |

Recommended input types:

```text
PDF
DOCX
PPTX
images
screenshots
HTML
scanned documents
official software manuals
training materials
competition documents
```

Recommended output locations:

```text
docs/mworks/converted/
docs/mworks/raw/
docs/index/
```

Rules:

1. Use MinerU MCP to convert official MWORKS documents into Markdown.
2. Do not paste large converted documents into `AGENTS.md`.
3. Store raw converted Markdown under `docs/mworks/converted/`.
4. After conversion, update `docs/index/doc_index.md`.
5. Extract API-related content into `docs/index/api_index.md`.
6. Extract reusable procedures into `workflows/`.
7. If OCR is needed, call `get_ocr_languages` before parsing.
8. Keep original source documents or source paths recorded.
9. Do not treat OCR output as fully reliable; review formulas, tables, and code blocks manually.
10. For important APIs, verify with Sysplorer MCP `get_api_document` or Syslab MCP `search_syslab_docs`.

Recommended document processing workflow:

```text
parse_documents
  → save Markdown under docs/mworks/converted/
  → summarize document structure
  → update docs/index/doc_index.md
  → extract API entries into docs/index/api_index.md
  → extract repeatable procedures into workflows/
```

---

## 5. WSL + Windows MWORKS MCP Notes

Codex runs inside WSL/Linux, while MWORKS.Sysplorer and MWORKS.Syslab are installed on Windows.

To avoid Windows path parsing problems, this project uses WSL wrapper scripts:

```text
/home/lzy18001500226/mcp-wrappers/syslab_mcp.sh
/home/lzy18001500226/mcp-wrappers/sysplorer_mcp.sh
```

Configuration principle:

```text
Codex
  → starts WSL wrapper script
  → wrapper calls Windows Sysplorer/Syslab MCP server
  → MCP server exposes tools through stdio
```

Do not configure WSL Codex directly with Windows paths as `command`, such as:

```toml
command = "D:\\Program Files\\MWORKS\\..."
```

Use wrapper scripts instead:

```toml
[mcp_servers.syslab]
command = "/home/lzy18001500226/mcp-wrappers/syslab_mcp.sh"
args = []
startup_timeout_sec = 180
tool_timeout_sec = 300

[mcp_servers.sysplorer_mcp]
command = "/home/lzy18001500226/mcp-wrappers/sysplorer_mcp.sh"
args = []
startup_timeout_sec = 180
tool_timeout_sec = 300
```

If Windows-side auto-generated Codex MCP configuration exists at:

```text
C:\Users\HP\.codex\config.toml
```

and contains Windows-path MCP entries, remove them to avoid conflicts with WSL wrapper configuration.

Failure pattern:

```text
Tools: (none)
```

Success pattern:

```text
Tools: detect_syslab_toolboxes, evaluate_julia_code, ...
Tools: call_code, check_model, simulate_model, result_manager, ...
```

### 5.1 Additional Local MCP Notes

Additional local MCP servers are used for repository management, document conversion, and project-local file operations.

Recommended local MCP servers:

| MCP | Purpose | Current status |
|---|---|---|
| Git MCP | Local git status, diff, history, commit support, rollback support | Enabled |
| Filesystem MCP | Project-local file access and editing | Enabled |
| MinerU MCP | Convert official documents into Markdown | Enabled |
| GitHub MCP | Remote GitHub issue, PR, and API operations | Not required currently |

GitHub MCP is not required at the current stage because the project only needs local Git automation, local code review, commit preparation, and rollback support. Remote operations such as `git pull` and `git push` are handled by normal Git over SSH.

Security rules:

1. Only install MCP servers from official or trusted sources.
2. Filesystem MCP must only access the project directory.
3. Never expose tokens, SSH keys, API keys, or credentials in prompts, logs, reports, or screenshots.
4. Do not install unnecessary MCP servers with broad filesystem, browser, email, database, or cloud permissions.
5. Before adding a new MCP server, record its purpose, command, permissions, and uninstall method.
6. Remove unused MCP servers before final submission.
7. Prefer wrapper scripts for Windows programs launched from WSL.
8. Prefer local Git MCP over GitHub MCP unless issue/PR automation is required.

Allowed Filesystem MCP root:

```text
/mnt/c/Users/HP/Desktop/Quadrotor
```

Disallowed Filesystem MCP roots:

```text
/
~
/mnt/c
/mnt/d
C:\
D:\
```

Recommended optional MCP startup commands:

```text
git:
  uvx mcp-server-git --repository /mnt/c/Users/HP/Desktop/Quadrotor

filesystem:
  /home/lzy18001500226/mcp-wrappers/filesystem_mcp.sh

mineru:
  uvx mineru-open-mcp
```

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

---

## 7. Core Workflows

### 7.1 Run a Simulation

Use this sequence:

```text
1. Confirm MCP tools are available with /mcp.
2. Use session_manager to connect or probe Sysplorer.
3. Use load_library to load required libraries.
4. Use model_manager to open the target model.
5. Use check_model before simulation.
6. Use simulate_model to run the scenario.
7. Use result_manager to verify result variables.
8. Export raw results to results/raw/.
9. Use Syslab to calculate metrics.
10. Save figures to docs/figures/ or results/figures/.
```

Required output:

```text
results/raw/{scene}_{controller}.csv
results/metrics/{scene}_{controller}.json
docs/figures/{scene}_{controller}_trajectory.png
docs/figures/{scene}_{controller}_error.png
```

---

### 7.2 Add a New Controller

When adding a controller:

1. Create a subfolder under `controllers/`.
2. Implement the standard controller input/output interface.
3. Add controller configuration under `scenarios/` or `configs/`.
4. Add at least one short smoke test.
5. Add metrics comparison with baseline.
6. Update README or workflow documentation.
7. Do not break existing PID baseline.

Standard controller input:

```text
state
reference
params
disturbance_estimate
time
dt
```

Standard controller output:

```text
thrust
attitude_ref
torque
motor_cmd
debug
```

---

### 7.3 Add a New Scenario

When adding a scenario:

1. Add scenario configuration under `scenarios/`.
2. Define reference trajectory or planner input.
3. Define controller to test.
4. Define disturbance or fault if applicable.
5. Define metrics to compute.
6. Save raw result, metrics, and figures.
7. Add the scenario to the experiment matrix.

Common scenarios:

```text
hover
step
circle
figure8
spiral
wind
mass_change
motor_fault
obstacle_avoidance
formation
formation_obstacle
```

---

### 7.4 Read and Analyze Results

When analyzing results:

1. Use `result_manager` to inspect result variables.
2. Export or read time series.
3. Use Syslab or scripts to calculate metrics.
4. Generate plots.
5. Save metrics in machine-readable format.
6. Report conclusions only from computed metrics or plotted results.

Required metrics:

```text
position_rmse
max_position_error
steady_state_error
settling_time
overshoot
attitude_rmse
control_energy
saturation_ratio
```

Optional metrics:

```text
minimum_obstacle_distance
planning_time
path_length
trajectory_smoothness
formation_error_rmse
minimum_inter_uav_distance
constraint_violation_count
```

---

## 8. Algorithm Development Rules

### 8.1 PID Baseline

Always preserve the official PID baseline.

Use it for:

- baseline tracking error,
- dynamic response comparison,
- wind robustness comparison,
- fault response comparison.

Do not delete or overwrite the official PID model.

---

### 8.2 NMPC

Use NMPC as the outer-loop trajectory tracking controller.

Recommended simplified state:

```text
X = [x, y, z, vx, vy, vz]
U = [ax, ay, az]
```

Recommended cost terms:

```text
position error
velocity error
control effort
control rate
terminal error
```

Recommended constraints:

```text
velocity limit
acceleration limit
tilt angle limit
thrust limit
altitude limit
```

---

### 8.3 INDI

Use INDI as the attitude inner loop.

Rules:

1. Filter angular acceleration estimates.
2. Limit control increments.
3. Tune attitude loop before connecting NMPC.
4. Test roll, pitch, yaw separately before full 3-axis control.
5. Log angular rate and attitude error.

---

### 8.4 L1-Inspired Adaptive Compensation

Use L1-inspired compensation for wind, mass uncertainty, and model mismatch.

Rules:

1. Estimate disturbance from measured and modeled acceleration.
2. Filter disturbance estimate before compensation.
3. Add saturation to compensation terms.
4. Compare with and without compensation.
5. Call it `L1-inspired` unless a full L1 theoretical implementation is completed.

---

### 8.5 Safety Filter

Use safety filtering for engineering robustness.

Recommended constraints:

```text
roll_ref limit
pitch_ref limit
thrust limit
velocity limit
altitude lower bound
obstacle distance lower bound
inter-UAV distance lower bound
```

If safety filtering affects tracking, record both tracking error and constraint violations.

---

### 8.6 Path Planning

Path planning is an upper-layer module, not the main control contribution.

Recommended planning candidates:

```text
waypoint trajectory
A*
RRT / RRT*
Kinodynamic A*
Minimum Snap
B-spline
EGO-inspired local collision cost
```

Planning output must be converted to a time-parameterized trajectory:

```text
time
position_ref
velocity_ref
acceleration_ref
yaw_ref
```

Do not rely on a full ROS navigation stack as the core project dependency.

---

### 8.7 Formation Control

Preferred method:

```text
Leader-Follower formation control
```

Recommended formations:

```text
triangle
line
diamond
row
```

Required metrics:

```text
formation_error_rmse
formation_error_max
minimum_inter_uav_distance
formation_keeping_rate
```

---

## 9. Automatic Code Review and Testing

Before submitting or merging changes, perform automated review and testing.

### 9.1 Code Review Checklist

Check:

1. Modified files follow the project directory structure.
2. Controller input/output interfaces remain compatible.
3. Trajectory CSV fields are complete.
4. Result files are saved to `results/`.
5. Generated figures are saved to `docs/figures/` or `results/figures/`.
6. Experiment conclusions are supported by metrics or plots.
7. No unnecessary hard-coded absolute paths are introduced.
8. MCP operations follow the documented workflow.
9. Model files are backed up before structural modification.
10. README or workflow documentation is updated if behavior changes.
11. Scripts have clear input and output paths.
12. Metrics formulas are documented.
13. Failed simulations are not silently ignored.
14. Report tables and figures match actual results.
15. Non-original code or algorithm references are marked.

### 9.2 Git-Based Review Requirements

Before code review, inspect local Git changes.

Required checks:

```text
git status
git diff
git diff --stat
```

Review must identify:

1. Modified source files.
2. Modified model files.
3. Modified workflow or report files.
4. Newly generated result files.
5. Unexpected binary files.
6. Hard-coded local paths.
7. Files that should be ignored by `.gitignore`.
8. Files that should be committed but are currently untracked.
9. Files that contain secrets, tokens, SSH keys, or personal paths.
10. Changes that may require updating tests, workflows, or report figures.

If generated files are large or temporary, do not commit them unless they are required submission artifacts.

Recommended `.gitignore` checks:

```text
temporary logs
cache files
large raw simulation outputs unless intentionally archived
local environment files
tokens or credentials
temporary MWORKS outputs
temporary Codex files
```

If a change affects controllers, scenarios, scripts, model files, or workflows, run the corresponding tests before commit.

Recommended Git-based review workflow:

```text
git_status
  → git_diff_unstaged
  → git_diff_staged
  → code review
  → qa_check
  → smoke test if needed
  → git_add
  → git_commit
```

---

### 9.3 Required Test Types

Run these test categories when applicable:

```text
configuration check
script unit test
controller interface test
short simulation smoke test
metrics regression test
pre-submit check
```

---

### 9.4 Configuration Tests

Check:

```text
MCP tools are available
wrapper scripts exist
required directories exist
required scripts exist
required docs exist
```

Required directories:

```text
models/
controllers/
planners/
scenarios/
scripts/
tests/
results/
docs/
workflows/
```

---

### 9.5 Script Tests

Test scripts such as:

```text
scripts/calc_metrics.jl
scripts/plot_results.jl
scripts/batch_experiment.jl
scripts/export_report_assets.jl
scripts/qa_check.py
```

For metrics scripts, use a small known input file and verify:

```text
RMSE
max error
control energy
settling time
saturation ratio
```

---

### 9.6 Controller Interface Tests

Verify all controllers accept consistent input and produce consistent output.

Input schema:

```text
state
reference
params
disturbance_estimate
time
dt
```

Output schema:

```text
thrust
attitude_ref
torque
motor_cmd
debug
```

---

### 9.7 Smoke Tests

Smoke tests should be short and fast.

Recommended smoke tests:

```text
hover_3s_pid
hover_3s_improved_pid
figure8_short_pid
figure8_short_nmpc_indi
wind_short_nmpc_indi_l1
```

Pass conditions:

```text
simulation finishes
result file exists
time variable exists
x/y/z variables exist
no NaN values
altitude remains non-negative
motor commands are not all zero
```

---

### 9.8 Regression Tests

Regression tests prevent performance degradation.

Compare new metrics against previous metrics.

Default rule:

```text
RMSE must not worsen by more than 20% unless the reason is documented.
Simulation must not fail.
Constraint violation count must not increase unexpectedly.
```

---

### 9.9 Pre-Submit Check

Before final submission, verify:

1. PID baseline runs.
2. Optimized controller runs.
3. At least one complex trajectory scenario runs.
4. At least one disturbance scenario runs.
5. At least one path planning or formation scenario runs if claimed.
6. Metrics exist for all reported experiments.
7. Figures exist for all report claims.
8. User manual is complete.
9. Simulation report is complete.
10. Video script matches implemented features.
11. MCP configuration screenshots are captured.
12. No broken absolute paths remain.

---

## 10. Report and Figure Rules

The final report must include:

1. Environment configuration.
2. MCP configuration and verification.
3. Official model and PID baseline analysis.
4. System architecture.
5. Control algorithm design.
6. Path planning design if implemented.
7. Formation control design if implemented.
8. Disturbance and fault scenario design.
9. Metrics definition.
10. Comparative simulation results.
11. Innovation summary.
12. Conclusion and outlook.

Figure requirements:

```text
Every figure must have a caption.
Every figure must be referenced in the text.
Every comparison claim must have a corresponding figure or table.
```

Recommended figure order:

```text
1. Environment and software installation
2. Sysplorer/Syslab MCP verification
3. Official quadrotor model
4. Official PID controller
5. Proposed system architecture
6. NMPC-INDI-L1 controller structure
7. Safety and fault module
8. Path planning module
9. Formation module
10. PID vs optimized trajectory comparison
11. Wind robustness comparison
12. Motor fault comparison
13. Path planning visualization
14. Formation trajectory visualization
15. Metrics summary table
```

---

## 11. MCP Troubleshooting

If `/mcp` shows `Tools: (none)`:

1. Check wrapper scripts:

```bash
ls -l ~/mcp-wrappers/syslab_mcp.sh
ls -l ~/mcp-wrappers/sysplorer_mcp.sh
```

2. Check MCP config:

```bash
codex mcp list --json
```

3. Check WSL config:

```bash
cat ~/.codex/config.toml
```

4. Check Windows-side conflicting config:

```powershell
notepad $env:USERPROFILE\.codex\config.toml
```

5. Check Codex logs:

```bash
tail -n 160 ~/.codex/log/*.log
```

6. If Syslab fails with desktop mode, use `nodesktop` first.
7. If Sysplorer fails from Windows path, use WSL wrapper.
8. If Julia session fails, call `restart_julia`.

### 11.1 Git / Filesystem / MinerU MCP Troubleshooting

If Git MCP fails, test manually:

```bash
uvx mcp-server-git --repository /mnt/c/Users/HP/Desktop/Quadrotor
```

If it waits without output, this is normal for stdio MCP servers. Press `Ctrl+C` to exit manual testing.

If Filesystem MCP fails, check:

```bash
ls -l ~/mcp-wrappers/filesystem_mcp.sh
cat ~/mcp-wrappers/filesystem_mcp.sh
```

The Filesystem MCP wrapper should restrict access to:

```text
/mnt/c/Users/HP/Desktop/Quadrotor
```

Recommended Filesystem MCP wrapper:

```bash
#!/usr/bin/env bash
cd "$HOME/.mcp-servers/filesystem"
exec "$HOME/.mcp-servers/filesystem/node_modules/.bin/mcp-server-filesystem" "/mnt/c/Users/HP/Desktop/Quadrotor" 2>> "$HOME/filesystem_mcp_error.log"
```

If Filesystem MCP still fails, check:

```bash
cat ~/filesystem_mcp_error.log
tail -n 120 ~/.codex/log/*.log
```

If MinerU MCP fails, test manually:

```bash
uvx mineru-open-mcp
```

If it waits without output, this is normal for stdio MCP servers.

If GitHub MCP fails with missing token, remove or disable GitHub MCP unless remote GitHub issue/PR operations are required. Local Git MCP does not need GitHub PAT.

If any MCP server shows `Tools: (none)`, check:

```bash
codex mcp list --json
cat ~/.codex/config.toml
tail -n 160 ~/.codex/log/*.log
```

---

## 12. Common Development Prompts

Use precise prompts when asking Codex to work.

Good prompts:

```text
按照 AGENTS.md 和 workflows/run_simulation.md，使用 Sysplorer MCP 运行 figure8 场景，控制器为 pid_baseline，结果保存到 results/raw/figure8_pid.csv。
```

```text
按照 workflows/calc_metrics.md，调用 Syslab MCP 执行 scripts/calc_metrics.jl，对 results/raw/figure8_pid.csv 计算 RMSE、最大误差和控制能量。
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
