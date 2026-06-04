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

### 3.0 New Conversation Recovery Rule

When starting or resuming a Codex conversation for this project, read
`Docs/Workflows/new_conversation_context.md` immediately after this file. Use
`Docs/Index/project_work_memory_index.md` for the broader work-history index.
Use `PROGRESS.md` only for newest active entries, not as a full transcript. Do
not load raw Codex session JSONL files or old chat dumps as routine context;
any historical claim that is not already represented in current source
documents must go through `Docs/Workflows/session_memory_migration.md` before
it becomes project truth.

### 3.1 Filesystem Boundary

Before each operation, explicitly treat the following sentence as active:

```text
操作权限仅限 C:\Users\HP\Desktop\MoSim
```

The WSL path equivalent is:

```text
/mnt/c/Users/HP/Desktop/MoSim
```

Rules:

1. All reads, writes, deletes, moves, searches, Git commands, tests, scripts, and MCP file operations must stay inside this project directory.
2. Do not read or modify files under `/mnt/c/Users/HP`, `/mnt/c/Users/HP/Desktop`, `/home/linux`, `/home/lzy18001500226`, other drives, SSH folders, token files, browser profiles, or personal data directories.
3. The only exception is when the user explicitly requests project infrastructure setup outside the repository, such as SSH authentication, MCP wrapper repair, or environment-variable verification.
4. For exceptions, state the exact external path and reason before acting.
5. Do not run broad destructive commands such as `rm -rf`, `git clean -fd`, or bulk file moves unless the target path is explicitly inside the project and the operation has been summarized first.

### 3.2 Autonomous Execution Rule

Default behavior is to continue working automatically until the requested task is complete.

Current CoAgent exception: before changing `CoAgent/` runtime, transport,
automation, task-state schema, task/result packet schema, permanent department
conversation design, or tool/MCP surfaces, read `CoAgent/STATUS.md`. Current
approval allows only `COAGENT-IMPL-MINILOOP-01`; later app-server transport, unattended
automation, new permanent departments, broad hook rewrites, and tool/MCP
expansion remain gated until their own approved task exists.

Do not stop only to ask whether to continue when the next step is clear. Continue through:

- file inspection,
- implementation,
- documentation updates,
- tests,
- shortest useful targeted simulations,
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

Default timeout rule: interactive commands, GUI/MCP probes, Codex conversation bootstrap commands, and any operation with unclear progress must use a 60 second timeout by default. If there is no useful response within 60 seconds, stop that attempt, clean up any clearly identifiable child process, record the partial state, and report the blocker. Use a longer timeout only when the task has an explicit known runtime and the user has approved waiting.

Immediate documentation rule: when a task reveals a reusable command,
successful recovery route, workflow correction, or new operating constraint,
record it in the appropriate project document before reporting completion. Do
not end with "record later" or leave the knowledge only in chat. If the write is
blocked, report the exact target document and blocker.

Source-first troubleshooting rule: when a UE/UAV simulation behavior problem
matches an existing ecosystem pattern, inspect local reference implementations
first, especially RflySim, Sunray/YunZong, PX4/Gazebo, AirSim, FAST-LIO, and
EGO-Planner materials under `References/`. If local references do not resolve
the issue, then search official docs or high-quality online sources. Record the
confirmed reusable pattern in the relevant workflow before continuing.

### 3.2.1 WeChat Progress and Intervention Rule

For long-running architecture validation, simulation, MCP, UE/ROS2, Git split,
or human-review work, WeChat is the default out-of-band progress and
intervention channel when the gateway is available.

Rules:

1. Send a WeChat milestone packet at task start, at completed architecture
   gates, when manual review is needed, and when a blocker changes the plan.
2. Use the narrow CoAgent adapter
   `CoAgent/gateway/cc_connect_weixin.py`; do not call `cc-connect send`
   directly for project notifications unless diagnosing the gateway.
3. Use sparse messages only. Do not mirror high-volume Codex transcripts, tool
   outputs, logs, or long command results through WeChat.
4. If WeChat sending fails, do not assume the user was notified. Record the
   failed send in `Results/coagent_gateway/`, diagnose the failure immediately,
   and update `PROGRESS.md` or the relevant workflow/status document.
5. If the failure is `no active session found`, inspect the runtime session
   file under `/home/linux/.cache/mosim/coagent/cc-connect-weixin/data/sessions/`
   and verify `active_session` before retrying once through the adapter.
6. If the failure is `weixin: sendMessage: ret=-2`, ask the user to send one
   normal message to the WeChat gateway conversation, then retry once. If it
   still fails, rerun the documented 10 minute QR setup and require one normal
   user message to refresh `context_token`.
7. If WeChat cannot be restored quickly, report the exact failure in the main
   conversation and continue with file-based progress records unless the task
   specifically requires user approval.
8. Do not retry WeChat sends in a tight loop.

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
7. For very large imports or restructures, first ignore or keep the whole new
   batch outside tracked scope, then unignore/stage/push small reviewed slices.
   Do not `git add -A` a broad external tree or 1000+ file batch directly.
8. Temporary large-tree ignore rules are not the end state. They are only a
   throttle to keep Git usable while the tree is drained. A Git split task is
   not complete merely because visible untracked files are 0; finish by removing
   or narrowing temporary ignores until `.gitignore` retains only real long-term
   exclusions such as >100 MB files, credentials, generated/cache/runtime assets,
   missing LFS assets, or explicitly manifest-only external materials. If a
   large tree is already tracked or shows as modified, `.gitignore` cannot hide
   or solve it; classify and commit those tracked changes in path-limited
   batches instead. Directory renames or moves that create 10k+ tracked
   changes are tracked-change work: first throttle any new untracked spill with
   ignore rules, then commit the tracked changes in reviewed small batches.
9. When Git is slow, has LFS/hook/index-lock residue, or another Git owner is
   active, delegate commit/push work to `GitIntegrator` instead of blocking the
   main engineering thread. The main agent remains responsible for scope,
   review, and final reporting; details live in `Docs/Workflows/agent_orchestration.md#5-long-git-work`.

### 3.3.1 Parallel Agent Rule

Use parallel agents when the user has authorized multi-agent work and the task
can be split into independent work streams.

Parallelism is not only for different task types. If one task type is itself
large, split it by repository group, subsystem, model family, result family, or
file ownership. For example, a broad open-source reference audit must not be
assigned to one generic "research" agent when it covers many repos; split it
into UE/rendering, planning/trajectory, perception/mapping, skills/workflow,
and Git/quality work streams.

Before starting a non-trivial task, spend a short planning pass on the task
graph:

```text
critical path work to do locally now
parallel research or documentation checks
parallel implementation slices with disjoint write sets
parallel simulation/evidence checks
parallel Git/quality checks
blocked steps that require user, license, GUI, or external data
```

Do not spawn agents just to create activity. Do spawn or reuse agents when a
sidecar task is independent, material to the result, and can proceed while the
main agent stays on the critical path.

If the user points out that the task should have been split, immediately update
the relevant project rule or workflow before continuing implementation, so the
same coordination failure is less likely in the next session.

Coordinator rules:

1. The main agent is the orchestrator. It owns task graph, ledger updates,
   integration, verification, and final report.
2. Treat Codex sub-agents as short-lived capability calls, not durable
   departments. Use them for bounded research, review, or execution slices that
   can return one structured result. Do not rely on them for long-running Git,
   review, test, or supervision queues.
3. Project sub-agent spawn calls should request `model=gpt-5.5` and
   `reasoning_effort=high` when the current runtime accepts those parameters;
   otherwise record the runtime limitation and continue with the configured
   default.
4. Spawn sub-agents only with concrete objective, read scope, write set, stop
   condition, expected output, and forbidden actions.
5. Keep research/review sub-agents read-only by default. For durable Git,
   testing, review, secretary, and security roles, route through the project
   task queue/runtime when available instead of leaving a Codex sub-agent
   waiting for follow-up instructions.
6. Split large task types by content family or model/result ownership.
7. Record long-running tasks in `Docs/Workflows/agent_task_ledger.md`; recover from
   ledger/WAL, not chat memory.
8. Accept sub-agent results only with evidence, inference, unknowns, risks, and
   next validation.
9. Use `Docs/Workflows/agent_orchestration.md` for contracts, queues, nested
   delegation, WAL, worktrees, reviewers, and external-repo audit routing.
10. Use `PROGRESS.md` for current status and repeated mistakes.
11. For long or volatile sessions, keep a `TaskSecretary` intake record so new
    user instructions, corrections, sub-agent returns, and manual-review
    decisions become recoverable tasks instead of chat-only memory.
12. Treat the current WSL-backed VSCode Codex conversation as the primary
    project conversation unless the user explicitly switches. Codex App is a
    review/front-end surface for this project and for extra conversations; do
    not rely on App/VSCode live session sync as the durable task ledger.

### 3.4 MCP Minimal-Impact Rule

MCP calls should be minimal, targeted, and non-disruptive.

Rules:

1. Prefer command-line, headless, or background MCP operations when available.
2. Avoid opening GUI windows unless a model simulation, Sysplorer operation, or visual verification genuinely requires it.
3. If a GUI window is opened by Sysplorer / Syslab / MCP, minimize it when possible and avoid bringing it to the foreground repeatedly.
4. Do not use broad MCP discovery calls repeatedly when a targeted tool call is enough.
5. During one development round, keep one reusable Sysplorer / Syslab / MWORKS GUI window open when repeated model checks are expected; do not close it after every small MCP call.
6. Save result evidence under `Results/` and documentation-ready assets under `Docs/`.
7. If MCP behavior may interrupt the user's desktop, state that risk before running the operation.
8. Do not call MCP tools merely to create activity. Use the smallest set of MCP calls that proves the current engineering claim.
9. If a tool exposes a release, stop, or non-GUI session cleanup API, call it after the useful result is saved.
10. Do not automatically close Sysplorer / Syslab / MWORKS windows before Git. Closing these windows can force license reactivation on the next run. Leave reusable windows open by default.
11. Close Sysplorer / Syslab / MWORKS windows only when the user explicitly asks, when the window is clearly frozen, when a login/activation prompt blocks progress, or when a stale process is opening duplicate sessions uncontrollably.
12. If a GUI window freezes, shows an unexpected login prompt, MCP health is unresponsive, or logs show a clear authorization/activation/tool failure, stop that MCP sequence, clean up the related process/window if it is clearly identifiable, and continue with file-level work or report the blocker. Do not classify slow QP/NMPC-style, Safety Filter, or fault-isolation simulations as frozen only because progress is slow.
13. Formal simulation runs should generate Sysplorer native result assets by default so the user can inspect curves and the actual quadrotor 3D animation. A window that only shows static propeller geometry or curves is not sufficient for manual visual audit. Use `--no-gui-result-viewer` only for headless tests, batch regressions, or known GUI/license instability. Use `--no-gui-open` when batch evidence should still write `native_result/Result.msr` but should not automatically open plot/animation windows.
14. `native_result/` and `*.msr` files are local GUI review assets and are ignored by Git. Do not commit them.
15. If automation cannot open a generated `.msr`, do not ask the user to open it manually. Diagnose the result binding path first. In particular, check whether Sysplorer wrote the current run to a suffixed folder such as `{ModelName}-1` while the opener targets stale `{ModelName}/Result.msr`; fix the cleanup/path logic and rerun.
16. When Sysplorer/Syslab MCP tools are healthy, interactive model loading, checking, simulation, plotting, animation, and GUI review must go through MCP directly. Project scripts remain for batch runs, result export, metrics, summaries, and regression automation.
17. Never call Sysplorer `ClearAll`, `ChangeDirectory`, or equivalent broad workspace-reset APIs from MCP automation. Use targeted `model_manager` load/unload/reload operations and explicit absolute project paths instead.
18. Before any task that touches Sysplorer, Syslab, Sysblock, Epic/Fab inventory, or Unreal Editor, check MCP availability first with the smallest useful probe. Expected MCP server names are `sysplorer`, `syslab`, `mosim-epic`, and `mosim-unreal`. If a required MCP server is missing, has `Tools: (none)`, or an editor-side read-only probe fails, stop the interactive operation and report the exact failing server, command, and error before falling back.
19. Do not use command-line scripts as a substitute for healthy MCP during interactive model work. Command-line tools are allowed for Git, file inspection, documentation, batch export, metrics, tests, and MCP wrapper diagnostics.

### 3.4.1 Unreal Mapping Window Rule

For UE scene simulation work, keep the rendered-world window and the robotics
state window separate.

Rules:

1. Unreal / `UE5/MoSimSceneLibrary` is the high-fidelity scene-rendering
   window: map appearance, UAV body, camera view, scene movement, trajectory
   video, and optional local debug overlays.
2. Point cloud, occupancy/grid map, TF, odometry, FAST-LIO output, and planner
   state must be reviewed in RViz/RViz2 or an equivalent native robotics
   visualization window.
   Default UE scene review should use separate native windows when possible:
   one RViz planning/grid window for occupancy and local planning, and one
   RViz point-cloud/FAST-LIO window for LiDAR, registered cloud, odometry, and
   path. A combined RViz overview is acceptable for smoke tests.
3. Browser HTML is not an accepted active point-cloud/map review surface. It is
   allowed only as an explicitly requested offline report preview.
4. UE debug overlays and local mesh previews do not replace RViz/RViz2 evidence.
   FAST-LIO/localization claims require ROS runtime topics and recorded
   comparison evidence.
5. Global UE collision/occupancy truth is a validation oracle only. It must not
   be fed to the planner as a known global map.
6. Keyboard/mouse mappings may be kept for UE/RViz view and camera control
   only. They must not directly drive UAV pose, overwrite MWORKS truth, or
   substitute for controller/setpoint input.
7. After the user gives a manual review result, accept that result as the
   authoritative visual gate outcome. Do not spend more time proving whether
   the review window is open unless the user asks; either implement the
   reported corrections or stop at the next explicit manual-review gate.
8. Current scene-rendering workflow details live in
   `Docs/Workflows/unreal_renderer.md`; keep that file updated whenever this
   window split, topic contract, or evidence boundary changes.

### 3.5 Sysplorer / Sysblock Modeling Modality Rule

Use the official Sysplorer skill rules as the hard boundary between modeling modes:

1. **Modelica physical / plant / wrapper models** are edited as `.mo` text in project-owned files. These models must keep meaningful `Placement` and `annotation(Line(...))` diagram semantics when they are used for graphical review.
2. **Sysblock internal block diagrams** are built and repaired with official Sysplorer/Sysblock APIs, preferably `call_code(mode="run_script")` / `ModelingPy`, using `NewModel(..., "Sysblock")`, `AddComponent`, `ConnectPort`, and `SetModelParamValue`.
3. Do not hand-write, bulk patch, or `SetModelText` a Sysblock block diagram as the primary topology authoring method. Text edits are allowed only for narrow generated metadata or display annotation repair, followed by `check_model` and graphical review.
4. **Hybrid Modelica + Sysblock** means layered integration: finish/check the Sysblock controller first, then instantiate or connect it from a Modelica physical top-level wrapper. Do not force physical components and SysplorerEmbeddedCoder blocks into the same layer with ordinary `AddComponent` and do not interpret that failure as proof that hybrid modeling is unsupported.
5. If a Sysblock graphical controller cannot be embedded into the physical plant because of current compiler/platform limitations, keep the graphical controller as the design/time-behavior artifact and use an equation bridge only for full-plant simulation evidence.

### 3.6 Simulation Evidence Rule

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

### 3.7 Simulation Cleanup Rule

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
11. After temporary smoke tests, probes, or failed MCP attempts, delete `.running`, `.tmp`, `__pycache__`, and ad-hoc probe logs before commit.
12. If previously working MWORKS simulations start returning unexplained activation/login/license/library-load failures, assume possible login or activation loss. Preserve current source changes, remove temporary test artifacts, stop retrying MCP, and ask the user for manual login/activation review.
13. At the end of each completed simulation task, leave reusable GUI windows open and report which scenario/result should be manually reviewed.

---

## 4. Project Directory Convention

Project structure should stay lean. Keep directories only when they contain
real project inputs, outputs, or documentation; do not create placeholder
folders just to match a future plan.

Core directories:

| Directory | Purpose |
|---|---|
| `Docs/Design/` | Algorithm and system design source of truth. |
| `Docs/` | User manual, simulation report, converted MWORKS docs, indexes. |
| `Docs/Workflows/` | Repeatable procedures and detailed agent/task mechanics. |
| `Docs/Skills/` | Project-local and reference skills. |
| `Models/`, `References/MWORKS/QuadrotorModel/` | MWORKS/Sysplorer models and official case model. |
| `Config/scenarios/`, `Scripts/`, `Scripts/tests/` | Scenario configs, automation scripts, checks. |
| `Results/` | Reproducible outputs, metrics, logs, figures, local review assets. |

Create subdirectories only when there is actual content to store. The raw
official MWORKS package is not required after useful documents are promoted to
`Docs/Mworks/converted/`; use temporary source paths only when rescanning new
official materials.

---

## 5. MCP and Agent Skill Routing

This file records only the highest-priority operating rules. Detailed MCP tool
lists, wrapper commands, troubleshooting steps, and translated MathWorks /
Simulink patterns live in the indexes, workflows, and project-local skills.

| Need | Primary Entry |
|---|---|
| MCP tool list and preferred sequences | `Docs/Index/api_index.md` |
| MCP wrapper/debug steps | `Docs/Workflows/debug_mcp.md` |
| Minimal-impact MCP operation rules | `Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md` |
| Sysplorer model/component context | `Docs/Skills/Mworks/mworks-model-context/SKILL.md` |
| MWORKS simulation evidence | `Docs/Skills/Mworks/mworks-simulation-evidence/SKILL.md` |
| Syslab/MATLAB/Simulink migration | `Docs/Skills/Mworks/mworks-syslab-porting/SKILL.md` |
| Failed/slow/wrong simulation diagnostics | `Docs/Skills/Mworks/mworks-runtime-diagnostics/SKILL.md` |
| Tests, review, pre-submit quality | `Docs/Skills/Mworks/mworks-test-quality/SKILL.md` |
| Report figures, replay, video evidence | `Docs/Skills/Mworks/mworks-report-visualization/SKILL.md` |

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
Store under Docs/Mworks/
    ↓
Build manual indexes under Docs/Index/
    ↓
Write common workflows under Docs/Workflows/
    ↓
Use MCP documentation tools when unsure
```

Recommended documentation folders:

```text
Docs/Mworks/
├── sysplorer/
├── syslab/
├── sysblock/
└── mcp/

Docs/Index/
├── doc_index.md
├── api_index.md
└── workflow_index.md
```

Rules:

1. Use `Docs/Index/doc_index.md` as the entry point for official documentation.
2. Use `Docs/Index/api_index.md` for API and MCP tool lookup.
3. Use `Docs/Index/workflow_index.md` for common project workflows.
4. Do not paste large documentation dumps into `AGENTS.md`.
5. Keep `AGENTS.md` as the project behavior and workflow control file.
6. If documentation is missing or unclear, use MCP documentation tools.

### 6.1 Project-Local MWORKS Skills

This repository includes compact project-local skills translated from MathWorks / Simulink agent patterns:

| Skill | Use When | File |
|---|---|---|
| `mworks-model-context` | Resolving Sysplorer model, component, port, parameter, controller replacement location, or signal interface | `Docs/Skills/Mworks/mworks-model-context/SKILL.md` |
| `mworks-simulation-evidence` | Running MWORKS simulations, reading results, computing metrics, or producing report evidence | `Docs/Skills/Mworks/mworks-simulation-evidence/SKILL.md` |
| `mworks-syslab-porting` | Translating MATLAB/Simulink skills, scripts, tests, plotting, or performance workflows into MWORKS/Syslab/Sysplorer practice | `Docs/Skills/Mworks/mworks-syslab-porting/SKILL.md` |
| `mworks-mcp-operations` | MCP session, wrapper, and minimal-impact operation behavior | `Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md` |
| `mworks-runtime-diagnostics` | Failed, slow, unstable, or suspicious simulation diagnostics | `Docs/Skills/Mworks/mworks-runtime-diagnostics/SKILL.md` |
| `mworks-test-quality` | Tests, reviews, targeted simulation checks, regressions, and pre-submit gates | `Docs/Skills/Mworks/mworks-test-quality/SKILL.md` |
| `mworks-report-visualization` | Report figures, replay assets, video evidence, and honest visual claims | `Docs/Skills/Mworks/mworks-report-visualization/SKILL.md` |
| `mworks-sysblock-graphical-modeling` | Building, repairing, and validating graphical Sysblock controller diagrams | `Docs/Skills/Mworks/mworks-sysblock-graphical-modeling/SKILL.md` |

Use `Docs/Skills/Mworks/` as the default execution layer for this project. Treat upstream MATLAB / Simulink skills under `Docs/Skills/Matlab/`, `Docs/Skills/Simulink/`, and official opencode skills under `C:\Users\HP\.config\opencode\skills` as second-level references only: consult them when the MWORKS skills do not cover a task, translate the useful pattern into MWORKS terms, and then update the relevant `Docs/Skills/Mworks/*/SKILL.md`, `Docs/Workflows/`, or `Docs/Index/` file so the project improves over time. Verify every executable API call through MWORKS docs or MCP. Never copy opencode OAuth/provider credentials into the repository.

---

## 7. Core Workflow Routing

Use `Docs/Index/workflow_index.md` as the workflow entry point. Do not duplicate long workflow steps in this file.

| Task | Workflow |
|---|---|
| Run one simulation | `Docs/Workflows/run_simulation.md` |
| Resolve model/component interface | `Docs/Workflows/resolve_model_context.md` |
| Produce labeled evidence bundle | `Docs/Workflows/produce_simulation_evidence.md` |
| Read exported results | `Docs/Workflows/read_results.md` |
| Calculate metrics | `Docs/Workflows/calc_metrics.md` |
| Generate report figures/replay | `Docs/Workflows/generate_report_figures.md` |
| Add a controller | `Docs/Workflows/add_controller.md` |
| Build/repair graphical Sysblock controller | `Docs/Workflows/build_sysblock_graphical_controller.md` |
| Run tests | `Docs/Workflows/run_tests.md` |
| Regression tests | `Docs/Workflows/regression_test.md` |
| Code review | `Docs/Workflows/code_review.md` |
| Pre-submit check | `Docs/Workflows/pre_submit_check.md` |

All workflow outputs should be report-ready: scenario/config, raw result, metrics, figure/replay, source label, and pass/fail summary when applicable.

## 8. Algorithm Source of Truth

Algorithm details live in `Docs/Design/`. Keep this file limited to routing and non-negotiable project constraints.

| Topic | Design File |
|---|---|
| Overall architecture and innovation line | `Docs/Design/00_系统总体设计.md` |
| Scope, P0/P1/P2, acceptance | `Docs/Design/01_需求范围与验收.md` |
| Model interface, coordinates, buses | `Docs/Design/02_模型接口与运行流程.md` |
| PID / NMPC / INDI / L1-inspired control | `Docs/Design/03_控制系统架构.md` |
| Safety filter, fault injection, tolerance | `Docs/Design/04_安全故障与容错.md` |
| Path planning and trajectory generation | `Docs/Design/05_路径规划与轨迹生成.md` |
| Formation control | `Docs/Design/06_多机编队控制.md` |
| Scenario matrix | `Docs/Design/07_场景扰动与测试矩阵.md` |
| Metrics and evaluation criteria | `Docs/Design/08_仿真指标与自动评估.md` |

Core constraints:

1. Preserve the official PID baseline.
2. Do not overwrite official model files silently.
3. Treat planning/formation as upper-layer modules around the control contribution.
4. Use `L1-inspired` unless a complete L1 theoretical implementation is delivered.
5. Record both tracking metrics and constraint/safety metrics when safety filtering affects behavior.

## 9. Review and Testing Routing

Use `Docs/Skills/Mworks/mworks-test-quality/SKILL.md` for quality decisions.

| Need | File |
|---|---|
| Code review checklist | `Docs/Workflows/code_review.md` |
| Test execution | `Docs/Workflows/run_tests.md` |
| Regression test | `Docs/Workflows/regression_test.md` |
| Final packaging check | `Docs/Workflows/pre_submit_check.md` |
| Project structure and evidence guard | `Scripts/quality/qa_check.py` |

Before commit, run the smallest relevant checks and `git diff --check`.

## 10. Report and Figure Routing

Use `Docs/Skills/Mworks/mworks-report-visualization/SKILL.md` when producing figures, replay assets, report sections, or demo-video material.

| Need | File |
|---|---|
| Current evidence and report claims | `Docs/simulation_report.md` |
| User-facing reproduction guide | `Docs/user_manual.md` |
| Figure generation workflow | `Docs/Workflows/generate_report_figures.md` |
| Metrics definitions | `Docs/Design/08_仿真指标与自动评估.md` |

Every comparison claim must trace to raw data, metrics, and a saved figure or replay asset.

## 11. Troubleshooting Routing

Use `Docs/Workflows/debug_mcp.md` and `Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md` for MCP troubleshooting.

Common routing:

| Symptom | Route |
|---|---|
| `/mcp` shows `Tools: (none)` | `Docs/Workflows/debug_mcp.md` |
| Sysplorer/Syslab GUI/session behavior | `Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md` |
| Failed model check/simulation | `Docs/Skills/Mworks/mworks-runtime-diagnostics/SKILL.md` |
| Missing result variables | `Docs/Index/variable_mapping.md` and `Docs/Workflows/read_results.md` |

`Auth: Unsupported` is normal for local stdio MCP servers and is not a failure.

## 12. Prompting and Task Shape

Prefer task-specific prompts with goal, input file, tool/MCP route, output path,
and acceptance criteria. Use `Docs/Index/workflow_index.md` for examples.
After every formal MWORKS simulation, verify result quality; `check_model ok`
and `simulate_model ok` are execution evidence only, not quality evidence.

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
