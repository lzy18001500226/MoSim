# Codex App / WSL / VSCode Session Research

Date: 2026-05-26

Status: historical/reference research. This file explains why Codex App/WSL/
VSCode session stores and visible-thread mechanics should not be treated as
durable project truth. It is not the current MoSim operating model after the
2026-06-24 coordinating-thread reset. For current execution, start from
`Docs/Workflows/single_thread_operating_model.md`,
`Docs/Workflows/mainline_operations_board.md`, and the task-specific workflow.

Purpose: clarify how to use Codex App, VSCode Codex, WSL, sessions, MCP, skills,
and automations in MoSim without losing task state or creating conflicting
chat/session stores.

## Sources

Official OpenAI sources checked:

- Introducing the Codex app:
  https://openai.com/index/introducing-the-codex-app/
- Working with Codex:
  https://openai.com/academy/working-with-codex/
- Codex plugins and skills:
  https://openai.com/academy/codex-plugins-and-skills/
- Codex automations:
  https://openai.com/academy/codex-automations/
- Codex settings:
  https://openai.com/academy/codex-settings/
- OpenAI docs MCP:
  https://developers.openai.com/learn/docs-mcp
- Codex hooks:
  https://developers.openai.com/codex/hooks
- Codex advanced configuration:
  https://developers.openai.com/codex/config-advanced

Local evidence checked:

- WSL Codex session store: `/home/linux/.codex/sessions`
- Windows Codex App session store: `C:\Users\HP\.codex\sessions`
- Windows Codex App thread index: `C:\Users\HP\.codex\state_5.sqlite`
- Current MoSim project root: `/mnt/c/Users/HP/Desktop/MoSim`
- Windows-native Codex CLI feature surface on 2026-06-06:
  `codex doctor`, `codex features list`, `codex --help`
- Global hook config on 2026-06-06:
  `C:\Users\HP\.codex\hooks.json`

## Findings

Codex App is a desktop command center for managing projects, threads,
automations, skills, plugins, and longer-running work. OpenAI describes threads
as chat-like work units and the App as a place to review, steer, and continue
work.

The execution environment and the session database are separate concerns.
Selecting a WSL environment can make tool execution, shell commands, and project
paths WSL-backed, but it does not mean the Windows desktop App and the WSL
VSCode extension write one shared live session database.

Observed local behavior:

- VSCode Codex running inside WSL uses `/home/linux/.codex`.
- Windows Codex App maintains its visible thread list through
  `C:\Users\HP\.codex\state_5.sqlite`.
- A copied JSONL session is not sufficient for App visibility unless the
  matching SQLite thread row exists and points to a valid `cwd`.
- A migrated session can fail with "current working directory missing" if the
  JSONL metadata or SQLite row still points to an old path such as
  `/mnt/c/Users/HP/Desktop/Quadrotor`.
- Manual App-thread creation was tested on 2026-05-26 and rejected for normal
  use. Inserting `threads` rows into `state_5.sqlite` and creating short
  App-local `rollout-*.jsonl` files made conversations visible in Codex App, but
  those threads did not appear as normal WSL/VSCode conversations and produced
  stale-path resume errors. The injected department/test entries were removed.

## Interpretation

OpenAI documentation supports the idea that Codex App can pick up session
history and configuration from Codex CLI / IDE workflows, but it does not
establish a safe live bidirectional session store between Windows App and WSL
VSCode.

For MoSim, live bidirectional session sync is therefore not a safe dependency.
The reliable state source must be project files, especially:

- `PROGRESS.md`
- `AGENTS.md`
- `Docs/Workflows/mainline_operations_board.md`
- `Docs/Workflows/single_thread_operating_model.md`
- task-specific workflow, skill, design, result, and cache files

Chat history is useful review context, but it must not be the only place where
task state, decisions, blockers, or manual review results exist.

## MoSim Decision

Current policy after the 2026-06-05 Windows-native migration:

- Primary conversation/config/history: Windows-native VSCode/Codex under
  `C:\Users\HP\.codex`.
- Codex App role: Windows desktop review/front-end UI and extra conversation UI.
- WSL role: required runtime lane for ROS2, RViz2, FAST-LIO-family,
  rosbridge, and Linux-native robotics tooling; not the default Codex config
  home.
- Durable project state: repository docs and ledgers.
- Session transfer: controlled one-way recovery only, not department creation.
- Disallowed: live bidirectional writes to the same session from App and WSL.

Historical Codex native capability observations after the 2026-06-06 hook audit:

| Surface | MoSim Decision |
| --- | --- |
| Native hooks | Use global `C:\Users\HP\.codex\hooks.json` with project-scoped adapter `Scripts/hooks/codex_native_hook.py` for hard lifecycle guardrails. Trust with `/hooks` when Codex asks. |
| Native plugins/skills | Use installed skills/plugins on demand; do not copy plugin caches into the repo or load every skill at startup. |
| MCP/app connectors | Use the native MCP/app surface for live tools and private/authorized data. Keep Sysplorer/Syslab/Unreal/ROS/Windows desktop boundaries in project workflows. |
| Browser / Windows MCP | Use native Browser for web/local UI targets and Windows MCP plus Win32/UI Automation scripts for MoSim desktop GUI review. Computer Use is deprecated for MoSim desktop GUI monitoring and recovery; do not use it for MWORKS/Sysplorer/Syslab. |
| Goals | Use for long-running task persistence when the current Codex surface supports it, but keep durable state in project files. |
| Legacy visible-thread tools | Legacy/reference only for current MoSim. Official temporary subagents are a separate bounded delegation surface; do not assume App cross-thread send is synchronous RPC. |
| Automations / thread wakeups | Legacy/reference only unless explicitly configured for a scoped reminder or audit. Automation output must become project evidence before it is trusted. |
| Workspace dependencies | Use when document/sheet/slide/runtime dependencies are needed instead of guessing local bundled paths. |
| Native notify | Useful local completion/blocker signal. For MoSim long tasks, sparse email is the default user-facing intervention channel; WeChat is diagnostic or explicitly requested only. |

2026-06-08 native tool-surface correction: a conversation that was created or
migrated from the WSL/VSCode/CLI side may be visible in Codex App but still not
expose Codex App native thread-management or automation tools in that
conversation. In the historical multi-thread model, App-native visible threads
were the intended surface for `create_thread`, `read_thread`,
`send_message_to_thread`, `set_thread_title`, `set_thread_archived`, and
`automation_update` work. In current coordinating-thread MoSim work, these
tools are not a normal execution route. This does not prohibit official
temporary subagents, which remain a separate bounded delegation surface. If a
migrated or WSL-origin conversation cannot see those tools after `tool_search`,
it must not edit Codex private state or click through the UI as a substitute.

Historical adoption priority for MoSim:

| Priority | Surface | Operating Rule |
| --- | --- | --- |
| P0 | Worktrees | Historical note for visible threads that wrote code/assets. Current coordinating-thread work still uses path-limited Git hygiene, not multi-thread worktree routing by default. |
| P0 | Visible threads | Legacy/reference only after the 2026-06-24 coordinating-thread reset. |
| P0 | Goals | Use for long-running PMO or department tasks, not for every small implementation step. |
| P0 | Skills/plugins | Load on demand. They are context reducers, not hard constraints. |
| P0 | MCP/apps | Use native live tool surfaces for Sysplorer/Syslab/Unreal/Blender/ROS2/Windows desktop work before inventing ad-hoc automation. |
| P0 | Browser / Windows MCP | Use Browser for browser/local UI review and Windows MCP/Win32 scripts for desktop GUI screenshot and manual-review support. Do not use Computer Use for MoSim desktop GUI incidents, especially MWORKS/Sysplorer/Syslab. |
| P1 | App automations/thread wakeups | Legacy/reference only unless explicitly configured for a scoped reminder or audit. Every output must become project evidence before it is trusted. |
| P1 | `codex review` | Use as a bounded review gate. It does not replace owner-thread integration or targeted tests. |
| P1 | `codex exec` | Use for one-shot background audits, packet generation, and narrow department prompts. |
| P1 | Workspace dependencies | Use for docs/sheets/slides/report assets and bundled runtimes. |
| P1 | Native notify | Use as local signal; use sparse email for user-facing long-task intervention. |
| P2 | App server / remote control | Not a dependency until separately validated. |
| P2 | Experimental memory/chronicle/artifact surfaces | Auxiliary only; do not store project truth there. |

Current adoption rule: the active thread may use native surfaces only when the
current task and owning workflow authorize them. This research page does not
grant authority.

Hook behavior verified on 2026-06-06:

```text
SessionStart -> returns concise additionalContext for MoSim startup routing.
PreToolUse safe command -> no output, therefore allow.
PreToolUse git reset --hard -> returns Codex deny JSON.
Stop -> no-op; broad auto-continue intentionally disabled.
```

Known limitation: the native hook blocks hard mechanical risks before tool use.
It is not a substitute for simulation evidence, Git review, result packets, or
manual visual audit. `PostToolUse` cannot undo already-completed side effects,
so destructive operations must be blocked before they run.

The App currently appears able to display the active project conversation after
the Windows session/index copy was repaired. Treat that as a convenience layer,
not as the source of truth.

Codex App cross-thread send is transport only. It is not request/response RPC
and does not guarantee that a target thread's reply returns to the source
thread. Every cross-thread department request must include `origin_thread`,
`origin_thread_id`, `target_thread`, `target_thread_id`, `request_id`, and the
expected packet paths. The target department writes its result to
`Results/agent_packets/returns/<request_id>.json` or its blocker to
`Results/agent_packets/blockers/<request_id>.json`; email/WeChat remain only
sparse alert channels.

Codex App can display conversations created from the WSL/VSCode side. That is
the required route for department and dedicated-task conversations. Manual
SQLite/JSONL injection is reserved only for emergency recovery after backup, and
must not be used to create new department threads.

## Safe Handoff Procedure

Use this only for emergency recovery when a WSL conversation must be made
visible in Codex App and normal sync does not work.

1. Close Codex App.
2. Copy the selected WSL session JSONL from `/home/linux/.codex/sessions` to
   `C:\Users\HP\.codex\sessions`.
3. Rewrite stale `cwd` and project paths in the copied JSONL to MoSim.
4. Insert or update the matching thread row in
   `C:\Users\HP\.codex\state_5.sqlite`.
5. Reopen Codex App and verify the thread opens without a missing-workdir error.

Do not run this as continuous sync. Do not use it to create department/task
conversations. If automation is later added, it should be a manual recovery
command with backup and a single explicit direction.

## Department Thread Layout

Historical note: the table immediately below records the 2026-05-26 seven-thread
department experiment. It is not the current operating model. The later
historical visible-thread registry is kept below for audit only; current MoSim
execution is coordinated by one parent thread and uses project files as durable
state.

Historical seven-thread layout:

| Thread | Department | Scope |
| --- | --- | --- |
| `MoSim｜总经办 PMO` | General Management / PMO | User dialogue, current goal, task intake, integration, final decisions |
| `MoSim｜调度中台` | Dispatch Center | Task tickets, owner assignment, department status board, blocked-task checks, result routing |
| `MoSim｜文档秘书部` | Documentation Secretary | Instruction records, decision logs, documentation patches, docs consistency review |
| `MoSim｜研发工程部` | Project Department | UE/Fab, MCP/skills, MWORKS/Sysplorer, controllers, planners, scene truth, parameter research implementation |
| `MoSim｜验证测试部` | Test Department | Unit/regression/simulation/UE/manual-review evidence gates |
| `MoSim｜安全合规部` | Security Department | Path boundary, secrets, large files, license checks, destructive-operation review |
| `MoSim｜DevOps 发布部` | DevOps Department | Git hygiene, branches, commits, pushes, LFS/ignore/release checkpoints |

Current App state after WSL-created department sync, applied 2026-05-26:

```text
Rollback backup: C:\Users\HP\.codex\backups\revert-app-local-department-threads-20260526-123853
Pre-sync backup: C:\Users\HP\.codex\backups\wsl-department-thread-sync-20260526-130607
State DB: C:\Users\HP\.codex\state_5.sqlite
Sidebar index: C:\Users\HP\.codex\session_index.jsonl
Active App-visible MoSim entries: 1 main project thread + 7 WSL-origin coordination/department threads
```

The department threads were created from WSL with real Codex runtime sessions,
not by direct App-local thread injection. Their WSL rollout files were then
copied to the Windows App session store and matching App rows were upserted only
as a display handoff. Do not restore manually seeded App-only threads such as
`MoSim｜质量安全部`.

Visibility correction applied later on 2026-05-26:

```text
Backup before correction: C:\Users\HP\.codex\backups\visibility-fix-20260526-142902
Root cause: department rollouts existed, but WSL session_index.jsonl did not
            list them and SQLite rows were background exec rows
            (source=exec, has_user_event=0).
Correction: add the thread IDs to both WSL and Windows session_index.jsonl, then
            set source=vscode, thread_source=vscode, has_user_event=1,
            archived=0 on both state_5.sqlite files.
Verification: both WSL and Windows rows point at existing rollout JSONL files
              and cwd=/mnt/c/Users/HP/Desktop/MoSim.
```

This remains a compatibility workaround, not a guaranteed product API. The
2026-05-26 visibility test showed that manually injected rows can still be
hidden or produce stale-path resume errors. The reliable route is to create the
conversation through a real Codex runtime session, then optionally normalize its
title/index metadata after backup. Codex App can then be used as the review
front end.

Operational result on 2026-05-26:

```text
1. A real pseudo-TTY `codex --no-alt-screen -C /mnt/c/Users/HP/Desktop/MoSim ...`
   session appeared in the VSCode Codex task list.
2. The department conversations created the same way became visible in VSCode.
3. The first DB-injected department rows were archived to avoid duplicate
   sidebar entries.
4. The real department rollout files were copied to the Windows App `.codex`
   session directory and upserted into the Windows state DB for App visibility.
5. Interactive/bootstrap commands now have a 60 second default timeout; if a
   thread bootstrap does not return useful evidence within 60 seconds, stop it
   and report partial state instead of waiting.
```

Historical visible thread registry, refreshed from the Windows Codex App thread
surface on 2026-06-08 CST after a Codex App / VSCode history-title drift. Use
`Config/legacy/department_threads.json` only for historical routing and audit;
it is not a current dispatch allowlist. Titles ending
in `-历史` or `-旧` are display hygiene for restored archived/legacy threads and
do not make those threads dispatchable:

| Thread | ID | Use |
| --- | --- | --- |
| `MoSim｜主线 PMO` | `019e9868-83ea-70f0-92c5-a3a408bd78c6` | Current mainline PMO task conversation for Sunray150/MoSim dynamics work |
| `MoSim｜Git仓库代码管理部` | `019e74de-a452-7a50-99e7-ca9a247b32f1` | Git split, path-limited staging, commits, push hygiene |
| `MoSim｜UE实验控制台与场景交互部-R1` | `019e9b24-50aa-7cd3-9e7c-4c43b224d993` | Primary UE operator console, scene interaction, command/echo schema, render-review integration, build-gate, and authorized runtime-review thread |
| `MoSim｜UE实验控制台与场景交互部-R2` | `019eab9f-b0ef-7433-893d-3235ea9f3c7e` | Auxiliary UE source/static review, implementation-surface backup, UI/command/echo contract review, source-only fixture/checker work, and bounded parallel support thread |
| `MoSim｜Sunray150资产与PBR审核部` | `019e9b25-066e-7372-8152-209c2b1322a4` | Durable Sunray150 visual asset, DAE/FBX/GLB, material/PBR, and manual visual-review thread |
| `MoSim｜MWORKS动力学与控制验证部-R1` | `019e9be5-334b-76b1-93f9-8b02caebf376` | Durable MWORKS mainline dynamics/control/model-integration evidence thread |
| `MoSim｜MWORKS动力学与控制验证部-R2` | `019e9999-b0d3-7682-bccd-faef08fcf1df` | Historical MWORKS auxiliary model organization, graphical interface, connection/layout/readability, and model-hygiene thread. This ID had old dispatch/UI-submit incidents; do not use as current route unless the user explicitly reopens legacy visible-thread operation. |
| `MoSim｜ROS2感知定位与规划运行部-R1` | `019e9c72-ee74-79d1-b9fe-621d3c6fc99e` | Durable ROS2/RViz2/FAST-LIO/local-map/planner runtime integration thread; historical/default registry route after deleted old ROS2 thread `019e9917-6181-7ec2-b3d6-4b624d6d3348`. It is not the current Sunray ROS1 execution selector; check the PMO board before using it. |
| `MoSim｜ROS2感知定位与规划运行部-R2` | `019e9b85-d4d8-7bf3-8afd-a65697cd3889` | Historical visible ROS2 department thread. Do not use for current Sunray ROS1 execution; only explicit legacy audit or user-approved route reopening may consult it. |
| `MoSim｜微信网关运维部-R3-已删除` | `019e9c7d-a8bd-7dd1-ad94-6feef5a07e9c` | Archived by the user on 2026-06-07 after MoSim moved to email-only notifications, then deleted by the user on 2026-06-08; not visible, not `active_visible`, no scheduled health checks, no routine no-op/canary/diagnosis/recovery dispatch unless explicitly restored with a new scoped route |
| `MoSim｜Codex 环境迁移部-旧` | `019e8181-6653-73b3-9685-f5bc9a24b947` | Historical Windows-native Codex environment migration, bridge-residue audit, config/MCP launcher cleanup, and related one-time environment repair history; user restored it only to repair its title and will re-archive |
| `MoSim｜开源项目探针` | `019e9be3-94de-7dc3-b067-92a78b678287` | App-native inventory owner for relevant open-source projects and local reference-project update candidates |
| `MoSim｜legacy agent runtime运维平台` | `019e9bc1-ea9f-7102-b41a-4ef9b2308992` | Codex App native legacy/meta operations thread; coordinates recurring legacy/meta tasks, thread-registry hygiene, and native capability adoption checklists |
| `MoSim｜开源项目学习部` | `019e9be4-56d0-7981-b71c-a5ded1c7ec76` | App-native learning owner for crawled projects/vendor articles and adopt/adapt/reference-only/reject proposals |
| `MoSim｜Codex 上下文维护部` | `019eab73-c5bc-7740-a6d1-5e0541bdb0c5` | App-native documentation secretary/context-maintenance route for scheduled context-memory/index updates, documentation consistency review, and cache-first migration drafts. Legacy internal key: `CodexContextMaintenanceAgent`; former titles include `MoSim｜文档秘书部` and R-suffixed context-maintenance titles. |
| `MoSim｜WechatCodex-已删除` | `019e8358-86b4-7070-8fd6-a2b4f4d2af97` | Historical WeChat-side message path deleted by the user on 2026-06-08; inactive for MoSim notifications, not visible, not a routing/no-op/recovery target unless the user explicitly restores WeChat diagnosis with a new scoped route |

Replacement rule: if a listed department is replaced with an App-native R2
thread, the old conversation is not the durable source after deletion. Before
the old thread is marked safe to delete, its reusable work must be extracted
into canonical project documents such as workflow docs, indexes, cache-first
session-memory migration files, or result/blocker packets. The replacement
packet must name each landed topic and document path. Do not point future agents
to a raw old chat, screenshot, or backup as the routine recovery path.

Historical deleted or absent thread note:

```text
019e74d1-72fa-7d33-8783-90584035ae92: old MoSim｜legacy agent runtime运维平台. Created through
  an older WSL/non-App-native conversation path; deleted by user on 2026-06-06.
  Do not dispatch native thread or automation tasks there; recover history from
  project docs and result/blocker packets.
019e9917-6181-7ec2-b3d6-4b624d6d3348: old ROS2 department, deleted by user
  after Codex App delivery failures.
019e9855-aa43-7fe2-807e-be7d4095877b: old MoSim｜微信网关运维部, superseded by
  App-native R2 019e9be0-534e-7c22-97ff-98fa7c2af39b (`MoSim｜微信网关运维部-R2-历史`),
  then replacement 019e9c7d-a8bd-7dd1-ad94-6feef5a07e9c
  (`MoSim｜微信网关运维部-R3-已删除`). The replacement was archived by the
  user on 2026-06-07 after MoSim moved to email-only notifications, then
  deleted by the user on 2026-06-08. Reusable
  gateway procedures remain historical in AGENTS.md,
  Docs/Workflows/debug_mcp.md, the archived AgentOS material under
  Docs/Cache/agent_legacy/, and Results/coagent_gateway/.
019e3dac-de0e-7180-98ad-d7137e8a6275: old WSL-migrated MoSim｜Codex 上下文维护部,
  superseded for current dispatch by App-native `MoSim｜Codex 上下文维护部`
  019eab73-c5bc-7740-a6d1-5e0541bdb0c5. Reusable
  context recovery content is landed in Docs/Workflows/new_conversation_context.md,
  Docs/Workflows/session_memory_migration.md, Docs/Index/project_work_memory_index.md,
  and Docs/Cache/session_memory_migration/.
019e74cf-fb50-7d71-912c-f586b4dd5f06: old MoSim｜开源项目探针, superseded by
  App-native R2 019e9be3-94de-7dc3-b067-92a78b678287. The old thread had a
  mismatched early bootstrap prompt; current probe duties are landed in
  Docs/Workflows/tooling_assets_governance.md and the archived AgentOS
  material under Docs/Cache/agent_legacy/.
019e74de-a83c-7fc2-8987-06c95577a1d3: old MoSim｜开源项目学习部, superseded by
  App-native R2 019e9be4-56d0-7981-b71c-a5ded1c7ec76. Current learning/adoption
  evaluation duties are landed in Docs/Workflows/tooling_assets_governance.md;
  former multi-thread details are archived under Docs/Cache/agent_legacy/.
019e74ce-6e2e-7e71-902d-f6cee64e8a61
019e74d2-ec4b-7603-a41b-596508ab6982
019e74d5-d833-7e41-a65b-2868fd841ea1
019e74d8-c6fd-76c2-98fe-832dc1fea97b
019e74d4-619c-7133-b53f-78fbefff780a
019e74d7-4d58-70f1-84f7-873641995f9a
```

The user reported deleting these threads. This list is historical evidence, not
a current blacklist that must be maintained forever. Legacy dispatch used the
allowlist in `Config/legacy/department_threads.json`; if one of these old IDs
is absent from a scoped historical visible scan, treat it as gone and remove it
from historical routing rather than trying to resume, restore, archive, or route
work to it. Future context-memory and documentation-secretary work routes to
`MoSim｜Codex 上下文维护部`
(`019eab73-c5bc-7740-a6d1-5e0541bdb0c5`). Durable documentation updates are no
longer centralized in a secretary thread; each responsible thread must update
the relevant project docs before returning completion.

Legacy legacy agent runtime bootstrap conversations may still be visible in the Windows
Codex state DB, including old `MoSim｜工具链 MCP`, `MoSim｜验证评测`, and
`MoSim｜安全合规` entries. Do not treat these titles as active departments merely
because a stale row exists. MCP/skills/workflow upkeep is owned by the thread
doing the work, or by `MoSim｜legacy agent runtime运维平台` for recurring meta-maintenance.
Security is enforced through `AGENTS.md`, prompts, path boundaries, harnesses,
preflight checks, and review gates; it is not an always-on visible department.
Validation/testing is an on-demand isolated gate unless PMO explicitly creates
a scoped visible test conversation for a high-impact acceptance task.
`MoSim｜调度中台` is deprecated for ordinary MoSim work because PMO now directly
dispatches visible department threads with explicit return/blocker packets.

Title-source rule: thread IDs are the durable key. Codex App manual renames may
appear in `session_index.jsonl` before they appear in
`state_5.sqlite.threads.title`, and `threads.title` can remain an old
initialization prompt. When a user provides an App-visible title for an ID, use
the user-confirmed title as the project registry value. For future refreshes,
compare at least `state_5.sqlite`, `session_index.jsonl`, and the user's visible
App title before changing this table.

Manual rename sync workflow:

```text
1. User reports: <thread_id> -> <current App-visible title>.
2. Agent checks the thread ID in:
   - C:\Users\HP\.codex\state_5.sqlite
   - C:\Users\HP\.codex\session_index.jsonl
   - project docs registry
3. If the sources disagree, prefer the user-confirmed App-visible title and
   record the disagreement in this section.
4. Update only project registry/workflow docs unless the user explicitly asks to
   edit Codex App state files.
5. Never infer identity from title alone; always match by thread ID first.
```

Latest scan artifact:

```text
Results/codex_history_audit/current_codex_threads_title_scan_20260605.csv
```

Naming convention:

```text
MoSim｜<department name>
MoSim｜专项｜<task name>
```

Do not create persistent App conversations for every role such as
`McpSkillsMaintainer` or `UEScenePipeline`. Treat those as roles inside a
department unless the user explicitly approves a split.

In the historical multi-thread model, dedicated task conversations were allowed
when:

```text
the task spans many turns or manual reviews
the task has a parent department and task_id
the task has a clear stop condition and result-packet format
PMO or legacy ops records it in a recoverable ledger/status packet
```

The current default after the 2026-06-24 reset is single active Codex-thread
execution. Historical PMO direct dispatch to visible durable threads and legacy
agent runtime meta-task ledgers are not active MoSim workflow unless the user
explicitly reopens them.

## App Automations Policy

Codex App automations are useful as a front-end trigger/reminder layer, but
must not replace MoSim-owned task records. Verify behavior against the current
installed App before relying on a new automation.

Historical App-native legacy operations re-adoption baseline on 2026-06-06:

- At that time, `MoSim｜legacy agent runtime运维平台`
  (`019e9bc1-ea9f-7102-b41a-4ef9b2308992`) was used as the baseline thread for
  native thread and automation capability adoption.
- The old `MoSim｜legacy agent runtime运维平台`
  (`019e74d1-72fa-7d33-8783-90584035ae92`) was deleted by the user and is a
  deleted historical thread only. Do not read, recover, dispatch to, or depend
  on it for current capability conclusions.
- The historical legacy operations tool surface exposed `automation_update` and native thread tools.
  A read-only thread probe confirmed the gateway and open-source probe
  departments by title, and confirmed the context-maintenance department by ID.
   The context-maintenance thread then showed `cwd=C:\mnt\c\Users\HP\Desktop\MoSim`,
  so heartbeat or automation delivery to it needs a target-thread cwd/visibility
  validation before it is treated as operational.
- No App automation was created in the re-adoption audit because duplicate
  detection would require resolving existing automation ids. When private
  `$CODEX_HOME` automation-state reads are forbidden by the task, return
  candidate definitions and the missing dedupe evidence instead of creating a
  possible duplicate.

Planned recurring automation candidates:

| Automation | Owner | Purpose |
| --- | --- | --- |
| Workflow/skills improvement | Responsible task thread or `MoSim｜legacy agent runtime运维平台` | Inspect recent incidents and update workflows/skills when they become reusable rules |
| External-repo inventory update | `MoSim｜开源项目探针` | Crawl or inventory relevant open-source projects and produce manifests |
| External-learning review | `MoSim｜开源项目学习` | Study crawled projects/vendor articles and return adopt/reject proposals |
| Context-memory drift check | `MoSim｜Codex 上下文维护部` | Update new-conversation context, memory index, and recovery notes; `MoSim｜文档秘书部` and R-suffixed context-maintenance titles are alias/history only |
| Git/release hygiene | `MoSim｜DevOps 发布` | Check large files, ignored/generated assets, split commits, and push readiness |
| Security constraint scan | Task owner with preflight/harness checks | Apply path/secrets/destructive-operation/license constraints without creating a security department |

All automation outputs should be converted into task tickets or evidence files.
Do not treat an App automation notification as completed work.

Preferred automation candidates now that native surfaces are available:

```text
1. PMO or legacy ops patrol heartbeat: do not wake the archived WeChat gateway route.
   Use email-only notifications and check only active-visible departments plus
   explicit recovery validation targets.
2. Context recovery drift: wake `MoSim｜Codex 上下文维护部`, compare the current
   thread registry and startup docs, then return a packet.
3. Hook/preflight health: run hook smoke tests and `codex doctor`; if hook trust
   or feature availability changed, update `Scripts/hooks/README.md`.
4. Reference-project inventory: wake `MoSim｜开源项目探针` after crawl batches.
5. External-learning review: wake `MoSim｜开源项目学习` for adopt/adapt/reject
   proposals, not for implementation.
```

Do not create a standing `Toolchain MCP`, security, or documentation-secretary
department just to own these checks. The responsible task thread updates the
relevant docs; `MoSim｜legacy agent runtime运维平台` owns recurring meta-maintenance.

## Open Questions

- Whether future Codex App versions will expose a documented session import or
  shared-store API.
- Whether App-side automations can be configured to operate on the same WSL
  project without duplicating local session state.
- Whether a small MoSim-specific session-handoff script is worth maintaining
  after App/VSCode behavior stabilizes.
- Whether future Codex releases expose a safer documented API for visible
  thread title refresh, archive/delete, and packet-style return routing.

## Follow-Up Rules

- When Codex App / VSCode / CLI behavior changes, rerun this research against
  current official docs before changing workflow rules.
- Do not infer hidden storage semantics from UI behavior alone; verify local
  session files and SQLite index state.
- Keep task state in project docs even when App live display appears to work.
