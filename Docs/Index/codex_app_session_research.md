# Codex App / WSL / VSCode Session Research

Date: 2026-05-26

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

Local evidence checked:

- WSL Codex session store: `/home/linux/.codex/sessions`
- Windows Codex App session store: `C:\Users\HP\.codex\sessions`
- Windows Codex App thread index: `C:\Users\HP\.codex\state_5.sqlite`
- Current MoSim project root: `/mnt/c/Users/HP/Desktop/MoSim`

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
- `Docs/Workflows/agent_task_ledger.md`
- TaskSecretary intake files under `Results/tmp/task_intake/`

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

The App currently appears able to display the active project conversation after
the Windows session/index copy was repaired. Treat that as a convenience layer,
not as the source of truth.

Codex App cross-thread send is transport only. It is not request/response RPC
and does not guarantee that a target thread's reply returns to the source
thread. Every cross-thread department request must include `origin_thread`,
`origin_thread_id`, `target_thread`, `target_thread_id`, `request_id`, and the
expected packet paths. The target department writes its result to
`Results/agent_packets/returns/<request_id>.json` or its blocker to
`Results/agent_packets/blockers/<request_id>.json`; WeChat remains only a
sparse alert channel.

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

MoSim uses a small number of long-lived App-visible department conversations
plus dedicated task conversations for long-running high-context work. The goal
is lower coordination risk: routine work stays inside department threads, but a
task such as PX4-log-based Sunray150 parameter identification may receive its
own conversation because it needs iterative research, user data requests,
estimator design, and repeated review.

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

Current visible thread registry, refreshed from the Windows Codex state DB on
2026-06-05 CST:

| Thread | ID | Use |
| --- | --- | --- |
| `MoSim｜主线 PMO` | `019e9868-83ea-70f0-92c5-a3a408bd78c6` | Current mainline PMO task conversation for Sunray150/MoSim dynamics work |
| `MoSim｜DevOps 发布` | `019e74de-a452-7a50-99e7-ca9a247b32f1` | Git split, path-limited staging, commits, push hygiene |
| `MoSim｜微信网关运维` | `019e9855-aa43-7fe2-807e-be7d4095877b` | cc-connect, QR login, context token, active session, scheduled health checks |
| `MoSim｜WechatCodex` | `019e8358-86b4-7070-8fd6-a2b4f4d2af97` | Codex conversation used by the WeChat-side message path; not a gateway operations owner |

Other active legacy CoAgent bootstrap conversations were still present in the
Windows Codex state DB at this refresh, including `MoSim｜调度中台`,
`MoSim｜产品发现战略`, `MoSim｜Agent Runtime 平台`,
`MoSim｜上下文记忆索引`, `MoSim｜工具链 MCP`, `MoSim｜知识秘书`,
`MoSim｜验证评测`, `MoSim｜安全合规`, and `MoSim｜外部情报进化`.
Treat them as inactive/legacy unless the user explicitly reactivates CoAgent
runtime work.

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

Dedicated task conversations are allowed when:

```text
the task spans many turns or manual reviews
the task has a parent department and task_id
the task has a clear stop condition and result-packet format
the Dispatch Center records it on the status board
```

The task-ticket mechanism and department status board belong to the Dispatch
Center. The Documentation Secretary records durable decisions and documentation
changes, but should not become the global dispatcher.

## App Automations Policy

Codex App automations are useful as a front-end trigger/reminder layer, but
must not replace MoSim-owned task records. Verify behavior against the current
installed App before relying on a new automation.

Planned recurring automation candidates:

| Automation | Owner | Purpose |
| --- | --- | --- |
| Daily workflow/skills improvement | Dispatch Center + Knowledge Department | Inspect recent incidents and update workflows/skills when needed |
| Daily external-repo update | DevOps Department + Knowledge Department | Pull/update reference repos and summarize upstream fixes |
| Daily documentation drift check | Documentation Secretary + DocsQualityTest | Ensure PROGRESS, ledger, and workflow docs match current state |
| Daily safety scan | Security Department | Check large files, secrets, external paths, destructive-operation residue |

All automation outputs should be converted into task tickets or evidence files.
Do not treat an App automation notification as completed work.

## Open Questions

- Whether future Codex App versions will expose a documented session import or
  shared-store API.
- Whether App-side automations can be configured to operate on the same WSL
  project without duplicating local session state.
- Whether a small MoSim-specific session-handoff script is worth maintaining
  after App/VSCode behavior stabilizes.

## Follow-Up Rules

- When Codex App / VSCode / CLI behavior changes, rerun this research against
  current official docs before changing workflow rules.
- Do not infer hidden storage semantics from UI behavior alone; verify local
  session files and SQLite index state.
- Keep task state in project docs even when App live display appears to work.
