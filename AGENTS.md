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

Codex native capability rule: use Codex native surfaces before expanding
CoAgent runtime. Native hooks are hard lifecycle guardrails for mechanical
checks; `AGENTS.md` is durable project policy; skills and workflows are
on-demand procedural context; plugins/apps/MCP/Browser/Windows MCP provide live
tool capabilities; automations/thread wakeups are recurring triggers; and
visible threads are durable specialty contexts. CoAgent should provide
MoSim-specific packet, evidence, gateway, and recovery glue, not reimplement
these native surfaces without a documented gap.
MoSim desktop GUI rule: Computer Use is deprecated for MoSim desktop GUI
monitoring, recovery, screenshot, and click workflows. Use Windows MCP,
Win32/UI Automation, and project-local PowerShell/Python evidence scripts
instead. For MWORKS/Sysplorer/Syslab specifically, do not route authorization,
screenshots, login recovery, reusable-window checks, or GUI-error handling
through Computer Use.

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
   When a task reaches `completed`, send a sparse WeChat completion packet
   automatically if the gateway is available. Completion notification is
   required even when no human review is needed.
2. Use the narrow CoAgent adapter
   `CoAgent/gateway/cc_connect_weixin.py`; do not call `cc-connect send`
   directly for project notifications unless diagnosing the gateway.
3. Use sparse messages only. Do not mirror high-volume Codex transcripts, tool
   outputs, logs, or long command results through WeChat.
   WeChat text must be a short Chinese human-facing update. Do not include
   concrete English file names, long paths, JSON/log names, or raw evidence
   lists in the WeChat body unless the user explicitly asks for that exact
   locator in WeChat. Store those details in result/blocker/notification
   packets and project evidence files instead. Manual-intervention, incident,
   auth/license, GUI-crash, or dead-thread messages should use a visibly
   different alert header such as `!!! MoSim 需要人工介入 !!!` so they are not
   mistaken for routine progress.
   When a task produces a local image, video, `.msr`, native result viewer, or
   other artifact that needs human review, do not only report a file path.
   PMO must directly open or display the artifact for the user when the user is
   online, or send a concise WeChat review prompt/image when available. Keep
   exact paths and evidence details in packets or project files, not in the
   human-facing notification body.
4. If WeChat sending fails, do not assume the user was notified. Record the
   failed send in `Results/coagent_gateway/`, diagnose the failure immediately,
   and update `PROGRESS.md` or the relevant workflow/status document.
5. If the failure is `no active session found`, inspect the runtime session
   file under `/home/linux/.cache/mosim/coagent/cc-connect-weixin/data/sessions/`
   and verify `active_session` before retrying once through the adapter.
6. If the failure is `weixin: sendMessage: ret=-2`, ask the user to send one
   normal message such as "你好" in the WeChat-side Codex conversation
   `MoSim｜WechatCodex` (`019e8358-86b4-7070-8fd6-a2b4f4d2af97`) to refresh
   the send context, then retry once. If the gateway implementation or health
   diagnosis is needed, send the incident to `MoSim｜微信网关运维部`
   (`019e9c7d-a8bd-7dd1-ad94-6feef5a07e9c`), not to the WeChat-side Codex
   conversation. If it still fails after the inbound message and one retry,
   rerun the documented 10 minute QR setup and require one normal user message
   to refresh `context_token`.
7. If WeChat notification fails and the task needs human intervention, use the
   gateway-owned sparse email fallback at most once for the open incident. The
   email asks the user to send one ordinary message in the WeChat-side
   conversation to restore the send context; after that intervention, retry
   WeChat once and keep subsequent notifications on WeChat. Do not turn gateway
   failure into repeated email alerts.
   MWORKS/Sysplorer/Syslab activation, license, login, authorization, or GUI
   error-report incidents are stricter: PMO must send a sparse WeChat alert and
   a sparse email alert for the same open incident, even if WeChat appears
   healthy, because missed GUI/license incidents can waste live simulation
   time. Keep both messages short and Chinese-facing; put paths, screenshots,
   and command details in blocker/evidence packets instead of the alert body.
8. If WeChat cannot be restored quickly, report the exact failure in the main
   conversation and continue with file-based progress records unless the task
   specifically requires user approval.
9. Do not retry WeChat sends in a tight loop.

Current multi-dialog boundary: the separate "dispatch center" layer is not the
default operating surface. The main PMO conversation directly routes work to
existing visible Codex department conversations, and may create a new visible
department thread when no suitable reusable department exists and the task
needs durable context rather than a one-shot sub-agent. CoAgent dispatch,
runtime, queue, result-router, and doctor tools are support infrastructure for
packet generation, recovery, validation, and evidence import; they are not a
mandatory scheduling middle office for ordinary MoSim work.
Do not recreate the old `MoSim｜调度中台`, `MoSim｜工具链 MCP`,
`MoSim｜安全合规`, `MoSim｜知识秘书`, `MoSim｜上下文记忆索引`, or
`MoSim｜验证评测` conversations unless the user explicitly reverses this
decision. Current dispatch uses the visible-thread allowlist in
`CoAgent/dispatch/department_threads.json`; if an old thread ID is absent from
the current visible scan, treat it as gone and remove it from dispatchable
registry instead of maintaining a separate blacklist. MCP/skills/workflow upkeep
is owned by the thread doing the work, or by `MoSim｜CoAgent运维平台` for
recurring meta-maintenance. Security is a hard constraint enforced through this
file, prompts, harnesses, preflight checks, and review gates; it is not a
separate standing department. Testing is normally an isolated task-local gate
or bounded sub-agent review, not an always-on department. Create a visible test
thread only for a high-impact acceptance task with explicit resource locks,
stop condition, and result/blocker packet paths, because parallel test threads
can compete for ROS topics, ports, GUI/MCP sessions, worktrees, or simulator
processes.

Prefer notifying the user through WeChat when the user is online and manual
thread creation/coordination is useful; if the user is offline or the next
action is clear, PMO may create/dispatch directly. Every new or reused
department thread must receive a clear role prompt, origin thread id, request
id, expected return/blocker packet paths, checkpoint cadence, allowed
read/write scopes, and forbidden actions. A visible thread is a reusable
department, not a disposable Codex sub-agent. Do not claim autonomous
department scheduling is working unless the target conversation is visible or
created successfully and a result/blocker packet is returned through the
approved transport.
Every visible department thread must also plan its own local execution before
doing non-trivial work. For each assigned task, the department should derive a
department-local goal, split the task graph into critical-path work,
parallelizable read-only/review slices, verification gates, and blockers, and
decide whether any short-lived Codex sub-agent is useful. These are disposable
sub-agents only: the department may use them for bounded research, review, or
independent file-level checks when the current runtime exposes such capability,
but must record the sub-agent objective, scope, stop condition, and returned
evidence in its return/blocker packet. Department-local sub-agent use never
grants permission to create, fork, rename, archive, or route work to visible
department threads; visible-thread operations remain PMO-only unless the user
explicitly changes this rule.
Dispatch packets for non-trivial department work must explicitly remind the
target department to plan its local goal/task graph and to decide
`subagent_plan` before deep execution. When a safe independent slice exists,
the department should use disposable sub-agents; if it does not, it must record
`available_but_not_useful`, `unavailable`, or `unsafe` with a concrete reason.
This is a requirement to plan sub-agent scheduling and record the decision, not
a requirement to use at least one sub-agent. Prompt text must not say or imply
that every dispatched department task must spawn a sub-agent.
Required return/blocker planning fields for non-trivial department work:
`department_local_goal`, `critical_path_steps`, `parallelizable_slices`,
`subagent_plan`, `subagent_plan_reason`, `subagents_used`, `verification_gates`, and
`manual_review_or_blocker_triggers`.
After planning, a visible department is expected to execute as an accountable
owner inside the declared scope, not wait for PMO to send step-by-step
``continue`` prompts. It must run the task-specific infrastructure preflight
before business work, stop promptly on real infrastructure/tool/runtime
blockers, and return a blocker instead of producing unrelated JSON, solver
retries, parameter tweaks, or metadata-only progress. Completed department
returns must include domain engineering evidence that matches the task type:
MWORKS work needs `.mo`/`package.mo`, `check_model`, `SimulateModel`, native
result/`.msr`, metrics, diagram/layout screenshots, or wiring observations as
applicable; ROS2 work needs topic/process/source-window/log/runtime evidence;
UE work needs source/static/build/runtime evidence according to scope; asset
work needs Blender/UE asset files, rendered review images, material manifests,
or visual-review artifacts. JSON task/result/blocker packets, ledger rows, and
`PROGRESS.md` entries are control-plane evidence only. They count as the
engineering deliverable only for tasks explicitly scoped as `diagnostic_only`,
`rule_sync_only`, `preflight_drill_only`, `dispatch_surface_diagnostic`, or
`static_inventory_only`. PMO must reject or return-for-fix completed packets
that lack the declared engineering outputs, omit the local plan/sub-agent
decision, or turn a real blocker into completed metadata.

Current MWORKS department split: `MoSim｜MWORKS动力学与控制验证部-R1`
(`019e9be5-334b-76b1-93f9-8b02caebf376`) is the primary mainline owner for
MWORKS dynamics/control/model-integration evidence. `MoSim｜MWORKS动力学与控制验证部-R2`
(`019e9999-b0d3-7682-bccd-faef08fcf1df`) is an auxiliary owner for model
organization, graphical simulation interface completeness, connection/layout
readability, and visual diagram hygiene. Because R2 previously showed
dispatch-surface instability, its first real business task must be preceded by
a bounded synchronization/no-op validation return packet. Historical packets
may still call the current R1 thread "R2"; do not rewrite those evidence
labels, but use the current dispatch registry for new routing.

PMO must include an activation/screenshot gate in every MWORKS/Sysplorer/
Syslab department dispatch. This is required even when the requested business
work is static model-file organization, because reusable MWORKS windows can
drift into demo, login, authorization, or GUI-error states and departments must
learn to report that state instead of retrying model or solver work. The target
department must perform a non-invasive preflight GUI sentinel and background
screenshot check before any business work, using both
`Scripts/agent/check_mworks_gui_sentinel.py` and
`Scripts/tools/capture_window_background.ps1` against the existing reusable
window/session. This evidence collection is the target department's own
preflight responsibility; PMO does not silently do it on the department's
behalf. If the department cannot run the sentinel or background screenshot
because its tool surface is unavailable, it must return a blocker with
`license_state=sentinel_unavailable_blocked`, no live MWORKS/MCP/model work,
and the unavailable command/surface recorded. The return or blocker packet must
include
`activation_sentinel_before`, `gui_sentinel_before`,
`background_screenshot_before` when available,
`activation_state_observation`, `license_state`,
`will_not_click_activation_login=true`, `mworks_window_evidence_touched=true`,
and `live_mworks_touched`.
The screenshot/sentinel is the first business gate for the target department in
that turn. PMO-side screenshots, earlier 014/015/016 drills, or a static ACK do
not satisfy a later business dispatch. `activation_state_observation` must
describe what the current sentinel, window title, or screenshot actually showed,
and must not be only a path, empty manifest reference, or generic status word.
The department must read the sentinel JSON/capture manifest or otherwise inspect
the screenshot/window-title evidence enough to classify the current activation
state in the same task turn. If it cannot inspect or classify that evidence, it
must return a blocker instead of continuing business work.
The sentinel is an all-window gate. A visible `[教育版]` main window is not
enough to prove account activation, because both activated and unactivated
states may show the education-edition title. It only proves an edition/window
marker. If no login/demo/error marker is present and only the education title
is observed, record
`license_state=education_window_observed_activation_unverified` or equivalent
wording unless a current-turn API/result explicitly proves stronger activation
state. Any other MWORKS/Sysplorer/Syslab-related window in `[演示版]`, login/
activation, authorization-failed, GUI-error, or visible unknown still blocks
the entire MWORKS task until PMO/user resolves or classifies the session;
departments must not close the suspect window and continue by choosing the
clean-looking one. Hidden Qt/browser-proxy/helper windows that have no
demo/login/authorization/error text are risk evidence and must be counted in
the sentinel/capture manifest, but they do not by themselves prove
authorization loss.
Background screenshots are necessary but not sufficient when the window title,
sentinel, or API reports demo/login/authorization risk. Sysplorer can show an
ordinary `[教育版]` main window while a login/license pane is only visible after
the existing application window is maximized or brought to foreground. In that
case, delegated departments still stop and return a blocker; PMO may, after
explicit user authorization, maximize/focus the existing Sysplorer/MWORKS
window and use the official foreground login/license UI to recover the reusable
session. Do not open a fresh window or close/restart MWORKS just to expose the
login pane.
`license_state` must be a concrete classification such as
`education_window_observed_activation_unverified`,
`license_api_recorded_education_version_only`,
`mixed_education_and_demo_blocked`, `demo_blocked`, `login_required`,
`authorization_failed`, `gui_error_report_blocked`,
`sentinel_unavailable_blocked`, or `unknown_blocked`; vague labels such as
`ok`, `normal`, or `looks_fine` are not acceptable. For
`live_mworks_touched=true`, packets must include `license_api_before` when the
API surface is available, and must not claim permanent account activation
unless that API/result explicitly exposes account activation status. A
successful `check_model` or `SimulateModel` without authorization errors is
task-local license sufficiency evidence, not a standing activation claim.

Use `live_mworks_touched=true` only when the task proceeds to MCP,
open/check/translate/simulate, plot, animate, Smart Layout, or graphical GUI
review after the preflight. If the business work remains static file-only,
keep `live_mworks_touched=false`, but still run the activation/screenshot
preflight and set `mworks_window_evidence_touched=true` in both task and
return/blocker packets. If the sentinel sees demo edition, unactivated state,
login/activation prompts, authorization errors, mixed `[教育版]`/`[演示版]`
windows, visible unknown MWORKS/Sysplorer/Syslab windows, unknown/unavailable
sentinel state, or an unexpected error-report dialog, the
department must stop live retries, preserve source edits, and return a blocker
with `status=blocked` to PMO instead of tuning solver settings, changing model
code, opening a fresh window, closing/restarting MWORKS, or clicking through
the dialog.
Live MWORKS work also requires phase screenshots after the preflight. R1
simulation/control tasks must capture and inspect background screenshots after
model load/check and after simulate/plot/animation phases when those phases
run. R2 graphical/layout tasks must capture and inspect background screenshots
during or after graphical layout review, and explicitly check for missing
wires, disconnected blocks, unreadable routing, wrong active window, or new
license/login/GUI-error prompts. Return/blocker packets for
`live_mworks_touched=true` must include `mworks_phase_screenshots` and
`mworks_phase_observations`; a preflight screenshot alone is not enough for
live simulation, result-viewer, animation, Smart Layout, or graphical-review
claims.
If an activation/license/login/authorization/GUI-error state appears at
preflight or mid-task, treat it as a P0 MWORKS infrastructure incident, not a
solver/model failure. The owning department must stop live work, preserve
source edits, return a blocker, and PMO must send both a sparse WeChat alert
and a sparse email alert while keeping the incident open until a later clean
department preflight proves a reusable valid session.
For live MWORKS dispatches, PMO task packets must carry a `mworks_live_gate`
object with the preflight order and required return fields. A live MWORKS
return/blocker packet is incomplete without activation sentinel evidence,
background screenshot locator when available,
`activation_state_observation`, `license_state`,
`will_not_click_activation_login=true`, `mworks_window_evidence_touched=true`,
`live_mworks_touched`, and, for live work, `mworks_phase_screenshots` plus
`mworks_phase_observations`. If visible
Sysplorer/MWORKS windows show mixed states such as `[教育版]` plus `[演示版]`,
classify the run as a license/login blocker until PMO/user chooses and verifies
a valid reusable session; do not let a department proceed by guessing which
window MCP will use.
MWORKS task packets must also declare `expected_engineering_outputs`. For
model optimization, simulation, wrapper/chassis work, package cleanup, or
graphical/layout review, completion requires concrete engineering outputs such
as `.mo`/`package.mo` edits, `check_model`, `SimulateModel`, native result/
`.msr`, metrics, diagram/layout screenshots, or wiring observations. JSON
task/result/blocker packets, ledger rows, and `PROGRESS.md` entries are only
control-plane evidence; they do not count as MWORKS engineering progress unless
the task is explicitly `diagnostic_only`, `rule_sync_only`,
`preflight_drill_only`, `dispatch_surface_diagnostic`, or
`static_inventory_only`.
PMO should validate live MWORKS task and return/blocker packets with
`Scripts/quality/check_mworks_live_gate.py --expect department`; packets that
omit the sentinel, background screenshot, activation-state observation, license state, no-click pledge,
`mworks_window_evidence_touched`, `live_mworks_touched`, or required live phase screenshot/observation fields are incomplete and
should be returned for correction.
Packets that include `activation_sentinel_before`, `gui_sentinel_before`, or
`background_screenshot_before` but omit
`mworks_window_evidence_touched=true` are also incomplete: the department
collected MWORKS window evidence without declaring the window-evidence gate.

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
   A directory or external project being hundreds of MB in total is not itself a
   reason to leave it ignored. Durable ignore decisions are file/class based:
   individual files at or over GitHub's hard limit, local auth material,
   dependency folders, generated/build/cache/runtime output, missing LFS
   payloads, or manifest-only assets. Ordinary source, docs, scripts, configs,
   and small assets must be reopened and submitted in reviewed project-sized
   batches instead of being hidden by a growing `.gitignore`.
   For crawled open-source references, work one source project directory at a
   time. Do not convert normal source, docs, scripts, configs, or small assets
   into durable file-level ignore rules just because a batch is noisy or a
   whitespace gate fails. Whitespace-gate failures are review/defer evidence,
   not ignore policy. In the final state, such project ignores should normally
   cover only a few durable categories: individual files at or above GitHub's
   100 MiB hard limit, operator-local settings, dependency folders,
   generated/build/cache/runtime outputs, missing LFS assets, or an explicitly
   documented manifest-only asset class.
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
For non-trivial tasks, this is an explicit gate, not optional style. The main
agent and every visible department must record one of these outcomes before
deep execution:

```text
subagent_plan = used | available_but_not_useful | unavailable | unsafe
reason =
```

Use `used` whenever there is at least one independent read-only audit,
reference comparison, file-level review, or disjoint write slice that can run
while the owner advances the critical path. If `available_but_not_useful`,
state why the next step is too coupled, urgent, resource-conflicting, or small
for a disposable sub-agent. If `unavailable`, record the missing runtime tool.
If `unsafe`, record the resource lock or data-risk reason. A department return
packet with `subagents_used=[]` is incomplete unless it also records this
decision and reason.

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
   Visible Codex threads are different: they are reusable department-style
   conversations with durable context. Use or create them when sustained
   ownership, manual inspection, repeated handoff, or a recurring specialty is
   needed. The active long-running DevOps/Git thread
   `019e74de-a452-7a50-99e7-ca9a247b32f1` must not be repurposed while it owns
   its current long task; other suitable visible threads may be dispatched, and
   missing departments may be created with a full charter and return contract.
   Current visible-thread lifecycle authority is granted only to user-approved
   mainline threads. The approved mainline threads are `MoSim｜主线 PMO`
   (`019e9868-83ea-70f0-92c5-a3a408bd78c6`) and `MoSim｜CoAgent运维平台`
   (`019e9bc1-ea9f-7102-b41a-4ef9b2308992`). These approved mainline threads
   may call `create_thread`, fork a visible department, rename a department,
   archive a department, and create/update/view/delete Codex App automations
   when their current Codex tool surface exposes the native tools. Other visible
   departments, including the architecture/design thread
   `019e0198-a041-77f1-84d0-c5524bfd4b81`, may advise a department charter or
   return a blocker requesting a new department, but they must not create,
   fork, rename, archive, create automation tasks, or delegate creation of
   visible threads.
   Before managing visible threads, an approved mainline thread must use the
   native thread tools surfaced in the current Codex session (`list_threads`,
   `read_thread`, `send_message_to_thread`, `create_thread`,
   `set_thread_title`, `set_thread_archived`, `fork_thread`, or related
   tools). Before creating or editing a recurring task, it must search for and
   use the native `automation_update` tool. If these native tools are not
   exposed, write a blocker packet instead of editing Codex App private state,
   clicking GUI controls, or using sub-agents as substitutes.
   If a visible department is readable but cannot start turns, accept messages,
   or submit from its own UI composer, treat it as a dispatch-surface incident
   first. Do not immediately create a replacement thread. Route bounded
   diagnosis to `MoSim｜CoAgent运维平台`, write a blocker packet, attempt one
   sparse Chinese user notification, then use the authorized Codex++ restart
   recovery route if the same start-turn/agent-loop failure persists. Restart
   ends the current conversation, so recovery validation must be resumed by the
   PMO/CoAgentOps heartbeat: read the latest blocker, run no-op delivery
   validation, and classify the thread as `partial_recovery`, `restored`, or
   `still_quarantined`. Create a replacement only with explicit PMO/user
   approval, repeated failed restart recovery, or a critical path that cannot
   wait.
   Every planned Codex++ restart for a dead-thread incident must attempt one
   sparse email notification before restart, even if WeChat was attempted or
   appears healthy. Record the email audit path in the blocker/recovery packet.
   If `MoSim｜CoAgent运维平台` itself is the dead thread, it cannot self-rescue;
   a heartbeat targeted at that same thread is not a recovery mechanism because
   the message cannot enter the failed start-turn surface. PMO and CoAgentOps
   must therefore use dual-mainline cross-checking through their own
   thread-attached 30-minute heartbeats: whichever mainline is still healthy
   sends the email, triggers the authorized restart route, and lets
   post-restart validation classify the affected mainline. Detached cron
   `mosim-coagentops` and Windows scheduled task
   `MoSim-CoAgentOps-OuterWatchdog` were removed after user review and must not
   be recreated as the default automatic recovery layer because they create a
   separate automation context and can pollute the project. If both mainlines or
   the whole Codex App are dead, user manual restart is the recovery path.
   `Scripts/agent/codex_outer_watchdog.ps1` is retained only as a manually
   authorized emergency helper for a written incident.
   When PMO creates a department, the initial prompt must address the new
   thread as the department itself: say "你就是该部门线程，请初始化自己"; do not
   say "请创建线程" or wrap a creation request inside another thread prompt.
   Default coordination is PMO -> visible department thread -> result/blocker
   packet. Do not insert a synthetic dispatch-center conversation as a required
   hop unless the specific task explicitly needs CoAgent runtime queue tooling.
   Once assigned, a visible department is responsible for its own local goal and
   task graph. It should state or record the department-local objective,
   planned sub-slices, verification gates, and any disposable sub-agent usage in
   the return/blocker packet. It must not simply execute ad hoc file reads and
   hand back a conclusion when the task is large enough to split.
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
12. Treat the current Windows-native VSCode/Codex conversation under
    `C:\Users\HP\.codex` as the primary project conversation unless the user
    explicitly switches. WSL remains the required runtime lane for ROS2,
    RViz2, FAST-LIO-family, and Linux-native robotics tooling. Do not rely on
    App/VSCode/WSL live session sync as the durable task ledger; durable state
    lives in project docs, ledgers, result packets, and source-controlled files.

### 3.4 MCP Minimal-Impact Rule

MCP calls should be minimal, targeted, and non-disruptive.

Rules:

1. Prefer command-line, headless, or background MCP operations when available.
2. Avoid opening GUI windows unless a model simulation, Sysplorer operation, or visual verification genuinely requires it.
   For Sysplorer / Syslab / MWORKS specifically, do not open a new window or
   start a fresh GUI session by default. The startup/loading splash can disrupt
   the user's desktop, and repeated windows make manual review unreliable.
   Reuse the current logged-in window/session first.
3. If a GUI window is already open or must be opened by Sysplorer / Syslab /
   MCP, minimize it when possible and avoid bringing it to the foreground
   repeatedly.
4. Do not use broad MCP discovery calls repeatedly when a targeted tool call is enough.
5. During one development round, keep one reusable Sysplorer / Syslab / MWORKS
   GUI window open when repeated model checks are expected; do not close it
   after every small MCP call.
6. Save result evidence under `Results/` and documentation-ready assets under `Docs/`.
7. If MCP behavior may interrupt the user's desktop, state that risk before running the operation.
   Windows MCP `Snapshot` / `Screenshot` are foreground desktop observation
   tools, not background screenshot tools. Do not use them while the user may be
   typing or using another app unless the user explicitly asked for a visible
   desktop capture, already approved the interaction, or an urgent GUI incident
   has no safer sentinel. Prefer UI Automation/PowerShell invocation,
   process/window queries, headless browser capture, Windows MCP, or
   app-specific APIs first. For MoSim desktop GUI workflows, do not use
   Computer Use; use the Windows MCP / Win32 / PowerShell route documented
   below. Browser remains the route for browser/local web targets.
8. Do not call MCP tools merely to create activity. Use the smallest set of MCP calls that proves the current engineering claim.
9. If a tool exposes a release, stop, or non-GUI session cleanup API, call it after the useful result is saved.
10. Do not automatically close Sysplorer / Syslab / MWORKS windows before Git. Closing these windows can force license reactivation on the next run and makes manual review harder. Leave the current logged-in education/license-active Sysplorer window open and reuse it across related MWORKS tasks. Prefer `session_manager(action="health"|"ensure")` reconnect/reuse over repeated full restarts. Opening a new Sysplorer / Syslab / MWORKS window is a last-resort action, not a normal recovery path. It requires one of: the existing window is frozen and cannot be recovered through MCP/session health, the session is bound to the wrong project/session in a way MCP cannot repair, the window is explicitly logged out or activation-blocked and PMO/user approves a clean login route, or the user explicitly asks for a clean session. Departments must write a blocker or ask PMO before taking that path.
11. Close Sysplorer / Syslab / MWORKS windows only when the user explicitly asks, when the window is clearly frozen, when a login/activation prompt blocks progress, or when a stale process is opening duplicate sessions uncontrollably. Do not close an otherwise usable MWORKS window just to make the next task "clean"; task cleanliness comes from explicit load/check/result evidence, not a fresh GUI process.
12. If a GUI window freezes, shows an unexpected login prompt, MCP health is unresponsive, or logs show a clear authorization/activation/tool failure, stop that MCP sequence, clean up the related process/window if it is clearly identifiable, and continue with file-level work or report the blocker. Do not classify slow QP/NMPC-style, Safety Filter, or fault-isolation simulations as frozen only because progress is slow.
    Treat `L5104-B0`, "软件尚未激活", "当前授权不允许变量方程数大于 300", unexpected demo-edition mode, login prompts, and authorization failures as license/login incidents first. A department thread must not keep changing solver settings or model code to work around these symptoms; it must return an auth/license blocker or ask PMO to recover the Sysplorer/Syslab login state. Credentials must be entered only through the official foreground login UI and must not be written to task packets, docs, logs, screenshots, or scripts.
13. If Sysplorer / Syslab / MWORKS shows a GUI crash/error-report dialog, treat it as a GUI incident and stop the current MCP/model sequence. The department must capture or reference a screenshot under `Results/`, record the visible dialog text, triggering command/action, MWORKS error-report path or visible path prefix, and whether the dialog would restart or send a report. Do not click restart, send report, confirm/close, or keep solver/model trial-and-error running unless PMO/user explicitly authorizes cleanup. Return a blocker packet if the task was active.
    A department must not rely only on noticing the dialog in chat. Before and
    after any MWORKS/Sysplorer MCP step that can open, simulate, translate,
    plot, animate, or otherwise interact with the GUI, perform the smallest
    available GUI sentinel check. Preferred order:
    1. Windows MCP / UI Automation / EnumWindows style title and text detector
       for MWORKS/Sysplorer/Syslab windows, including all-window license-state
       classification.
    2. Project-local Win32 background evidence scripts: use
       `Scripts/tools/capture_window_background.ps1` for window-level
       screenshots, and `Scripts/tools/invoke_window_background_click.ps1` only
       for approved low-risk UI actions such as opening an AI/helper panel.
       These scripts can temporarily restore a minimized Sysplorer window
       without activation, capture or post one bounded action, then re-minimize
       it. They must not be used to click login, activation, save, close,
       restart, send-report, or error-dialog recovery controls.
    3. Windows MCP `Snapshot` / `Screenshot` window summary and visible desktop
       capture, accepting that this may require the window to be visible or may
       only prove the foreground desktop state.
    4. Sysplorer/MCP health plus process/window-title scan as a weak fallback.
    If no sentinel surface is available, record `gui_sentinel=unavailable` in
    the task packet/return and avoid making unattended GUI evidence claims. Do
    not create a separate Windows desktop or move Sysplorer to another desktop
    unless PMO/user approves that disruptive fallback.
    Do not create a new Sysplorer / Syslab / MWORKS window merely to get a
    cleaner screenshot or avoid reusing the current session. Use the background
    evidence scripts for window-level inspection, and escalate to PMO if the
    existing session cannot be safely reused.
    If a department sees activation, login, authorization, crash, or
    error-report evidence, it should capture additional background evidence if
    safe, stop its model/MCP retries, and return a blocker to `MoSim｜主线 PMO`.
    PMO or `MoSim｜CoAgent运维平台` owns any follow-up background recovery or
    user-facing intervention. Specialist departments must not independently
    click through activation/login/error-report dialogs.
14. Formal simulation runs should generate Sysplorer native result assets by default so the user can inspect curves and the actual quadrotor 3D animation. A window that only shows static propeller geometry or curves is not sufficient for manual visual audit. Use `--no-gui-result-viewer` only for headless tests, batch regressions, or known GUI/license instability. Use `--no-gui-open` when batch evidence should still write `native_result/Result.msr` but should not automatically open plot/animation windows.
15. `native_result/` and `*.msr` files are local GUI review assets and are ignored by Git. Do not commit them.
16. If automation cannot open a generated `.msr`, do not ask the user to open it manually. Diagnose the result binding path first. In particular, check whether Sysplorer wrote the current run to a suffixed folder such as `{ModelName}-1` while the opener targets stale `{ModelName}/Result.msr`; fix the cleanup/path logic and rerun.
17. When Sysplorer/Syslab MCP tools are healthy, interactive model loading, checking, simulation, plotting, animation, and GUI review must go through MCP directly. Project scripts remain for batch runs, result export, metrics, summaries, and regression automation.
18. Never call Sysplorer `ClearAll`, `ChangeDirectory`, or equivalent broad workspace-reset APIs from MCP automation. Use targeted `model_manager` load/unload/reload operations and explicit absolute project paths instead.
19. Before any task that touches Sysplorer, Syslab, Sysblock, Epic/Fab inventory, or Unreal Editor, check MCP availability first with the smallest useful probe. Expected MCP server names are `sysplorer`, `syslab`, `mosim-epic`, and `mosim-unreal`. If a required MCP server is missing, has `Tools: (none)`, or an editor-side read-only probe fails, stop the interactive operation and report the exact failing server, command, and error before falling back.
20. Do not use command-line scripts as a substitute for healthy MCP during interactive model work. Command-line tools are allowed for Git, file inspection, documentation, batch export, metrics, tests, and MCP wrapper diagnostics.
21. For any live MWORKS/Sysplorer/Syslab task, the activation sentinel is a
    hard preflight, not an optional incident check. Before the first MCP
    `session_manager`, `load_file`, `check_model`, `translate_model`,
    `simulate_model`, plot, animation, or GUI-review operation, capture or
    reference a background screenshot/sentinel result for the existing window.
    If the state is demo edition, unactivated, logged out, activation-blocked,
    or unknown because the sentinel failed, stop live work and return a blocker
    unless PMO explicitly authorizes a bounded recovery attempt. Do not use a
    new MWORKS window to bypass a failed activation check.
    If the blocker is license/login/demo state and PMO is authorized to recover
    it, first reuse the existing window: maximize/focus it to reveal hidden
    license/login panes, operate only the official foreground login/license UI,
    then recheck sentinel, background screenshot, and `License(ltype="info")`.
    Close only the license/login dialog after success; keep the reusable
    Sysplorer/MWORKS main window open.

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
12. If previously working MWORKS simulations start returning unexplained activation/login/license/library-load failures, assume possible login or activation loss. Preserve current source changes, remove temporary test artifacts, stop retrying MCP, and ask the user for manual login/activation review. Known signatures include `L5104-B0`, "软件尚未激活", "当前授权不允许变量方程数大于 300", unexpected demo-edition mode, login prompts, and authorization failures. These are not solver-tuning tasks until license health has been restored and a smallest MCP `check_model` passes again.
13. If a MWORKS/Sysplorer GUI error-report dialog appears, save or reference a screenshot and write a GUI-incident blocker before further simulation work. The blocker must include the screenshot path, visible dialog text, triggering task/command, MWORKS error-report path or visible prefix, and the proposed recovery action. Do not continue hidden MCP retries while the dialog is open.
14. At the end of each completed simulation task, leave reusable GUI windows open and report which scenario/result should be manually reviewed.
15. If PMO successfully restores a MWORKS/Sysplorer login state, subsequent department tasks should treat that window as the reusable review/session surface. They should not close or restart it merely to rerun `check_model`, small smoke simulations, result reads, or plot/animation review.
16. Before any live MWORKS/Sysplorer/Syslab simulation cleanup, check,
    translate, simulate, plot, or animation step, run the activation sentinel
    on the reusable window and record the result. A department packet that
    lacks `activation_sentinel_before` is incomplete for live MWORKS work. If
    the sentinel reports demo edition, missing activation, login, authorization
    failure, or an error-report dialog, stop cleanup/simulation and return an
    auth/license or GUI blocker instead of continuing model or solver trials.
17. Before any MWORKS window-evidence task, including activation checks and
    background screenshots that do not call MCP/model operations, set
    `mworks_window_evidence_touched=true` in the task and return/blocker
    packets. If the sentinel or screenshot sees demo, mixed, unknown, login,
    activation, authorization, or GUI-crash state, return a blocker immediately
    and do not proceed to model work.

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
| Plugin/MCP/skills/workflow/reference asset governance | `Docs/Workflows/tooling_assets_governance.md` |
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

Use `Docs/Skills/Mworks/` as the default execution layer for this project. Treat upstream MATLAB / Simulink skills under `Docs/Skills/Matlab/`, `Docs/Skills/Simulink/`, official opencode skills under `C:\Users\HP\.config\opencode\skills`, Codex plugin skills, and crawled external project skills as second-level references only: consult them when the MWORKS skills do not cover a task, translate the useful pattern into MoSim/MWORKS terms, and then update the relevant `Docs/Skills/Mworks/*/SKILL.md`, `Docs/Workflows/`, or `Docs/Index/` file so the project improves over time. New tooling assets must follow `Docs/Workflows/tooling_assets_governance.md` before becoming active project guidance. Verify every executable API call through MWORKS docs or MCP. Never copy opencode OAuth/provider credentials into the repository.

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

Before sending a prompt, task packet, or cross-thread instruction to another
visible Codex thread, run a semantic sanity check. The instruction must not
contain typos, contradictory ownership, unclear pronouns, or inverted relations
that could make the target thread execute the wrong architecture. In
particular, do not write statements such as "不要重复手搓 CoAgent 已由 Codex
原生支持的能力"; the correct meaning is "不要在 CoAgent 中重复实现 Codex 已经
原生支持的能力". If a bad prompt is found after drafting, correct the prompt and
record the reusable correction in the relevant workflow before dispatching.

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
