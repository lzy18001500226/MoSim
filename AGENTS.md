# AGENTS.md

> Project instructions for Codex / AI assistants working on MoSim, the A8
> quadrotor attitude and position-control project.

This file is the compact project constitution. Keep durable hard boundaries
here. Put executable procedures, packet schemas, patrol logic, MWORKS window
classification, dispatch SLOs, and domain-specific workflows in the linked
documents below.

## 0. Start Here

For every new or resumed MoSim conversation:

```text
1. AGENTS.md
2. Docs/Workflows/new_conversation_context.md
3. Docs/Workflows/mainline_operations_board.md
4. CoAgent/dispatch/department_threads.json
5. Topic-specific workflow / skill / design docs only as needed
```

Use `PROGRESS.md` only for newest active entries, not as a full transcript.
Read `Docs/Workflows/agent_task_ledger.md` only when the board or a packet
requires trace-back evidence.

Do not load raw Codex session JSONL files or old chat dumps as routine context.
Historical chat claims must go through
`Docs/Workflows/session_memory_migration.md` before becoming project truth.

## 1. Hard Boundaries

1. Work only inside `C:\Users\HP\Desktop\MoSim` unless the user explicitly
   approves a named infrastructure action outside the repository. Project-local
   means do not read or modify sibling personal directories, token files,
   browser profiles, SSH folders, other drives, `/home/linux`, or WSL/user
   home paths unless the approved infrastructure task names that path and why.
2. PMO owns product priority, scope, acceptance/rejection, final integration,
   visible-thread lifecycle decisions, manual/GUI action decisions, and restart
   decisions.
3. CoAgentOps may patrol, recover, and perform bounded pre-authorized P0
   dispatch only under `Docs/Workflows/coagent_ops_patrol_workflow.md`.
   CoAgentOps does not gain product authority.
4. Cross-thread work must use `status=active_visible` routes from
   `CoAgent/dispatch/department_threads.json`, carry `native_surface_gate`,
   `semantic_boundary`, `expected_return_path`, and `blocker_return_path`, and
   return durable packets under `Results/agent_packets/`.
5. Non-trivial visible-department dispatch packets must require a local goal,
   critical-path split, parallelizable-slice review, verification gates, and a
   `subagent_plan` decision. A department must record whether disposable
   sub-agents were `used`, `available_but_not_useful`, `unavailable`, or
   `unsafe`. This is a planning requirement, not a requirement to spawn a
   sub-agent.
6. Sparse Chinese email is the default human notification channel. Deleted
   WeChat gateway/message-path threads are historical only and must not be
   scanned, no-oped, recovered, or used unless the user explicitly restores a
   scoped WeChat diagnosis route.
7. P0 progress means moving MWORKS R1/R2, ROS2 R1/R2, and UE R1/R2 gates
   forward. Sunray/PBR remains frozen unless the user reopens it. Support lanes
   cannot mask idle P0 engineering work.
8. MWORKS activation/window patrol is owned by CoAgentOps. MWORKS departments
   stop on observed login/license/authorization/GUI-error/unknown blocking
   states and return blockers instead of retrying solver/model work.
9. For normal MoSim mainline, visible-department, automation, and disposable
   sub-agent dispatches, request `gpt-5.5` and `thinking=high` when the native
   tool accepts those settings. Do not wake healthy threads only to change
   settings.
10. Do not re-create deleted PMO heartbeat, detached CoAgentOps cron, Windows
    watchdog, or replacement visible threads without explicit user/PMO
    approval.
11. Temporary broad `.gitignore` rules for reference imports are only a drain
    queue. Durable ignores must be class/exact-risk decisions, not a hidden
    backlog of ordinary source, docs, scripts, configs, or small assets.
12. CoAgent runtime, transport, automation, schema, tool/MCP surface, and
    permanent department design changes remain gated by `CoAgent/STATUS.md`
    and `Docs/Workflows/agent_orchestration.md`; do not infer approval from
    this compact entry file.

## 2. Current Visible Routes

Canonical routing lives in `CoAgent/dispatch/department_threads.json`. Current
named corrections:

| Route | Current Rule |
|---|---|
| `MoSim｜主线 PMO` (`019e9868-83ea-70f0-92c5-a3a408bd78c6`) | Main user-facing PMO, dispatch, acceptance, and final integration. |
| `MoSim｜CoAgent运维平台` (`019e9bc1-ea9f-7102-b41a-4ef9b2308992`) | 10-minute patrol, bounded ops recovery, registry hygiene, dispatch SLO audit. |
| `MoSim｜Codex 上下文维护部` (`019eab73-c5bc-7740-a6d1-5e0541bdb0c5`) | Documentation-secretary/context-maintenance route. `MoSim｜文档秘书部`, R-suffixed context titles, and `MoSim｜知识秘书` are alias/history only. |
| MWORKS R1/R2/R3 | R1 owns primary dynamics/control/model evidence. R2 owns static/model organization, graphical review, checker/review, and safe failover. R3 is reserve only after PMO proposes/approves it because R2 failover still leaves P0 idle/blocked. |
| ROS2 R1/R2/R3 | R1 owns live ROS2/RViz/FAST-LIO/planner integration. R2 owns static/diagnostic/checker/review failover only. R3 is reserve only after PMO proposal/approval. |
| UE R1/R2/R3 | R1 owns primary UE console/runtime/editor/build work when authorized. R2 owns source-static, command/echo contract, checker/review, and safe failover. R3 is reserve only after PMO proposal/approval. |
| `019de24d-e993-72c0-a0b2-caf2ac8ac85e` | Refresh-only non-MoSim watch target after Codex App/PC restart. It is not a MoSim dispatchable department. |

R2 failover is limited by default to:

```text
source_static
diagnostic_only
packet_contract_fix
rule_sync_only
checker/review
```

R2 failover must not run MWORKS live work, ROS2 live work, UE runtime/build/
editor work, GUI clicks, login/authorization/save/restart actions, or setpoint
publication.

## 3. Operating Documents

| Need | Source Of Truth |
|---|---|
| Current PMO board and next action | `Docs/Workflows/mainline_operations_board.md` |
| CoAgentOps patrol, dead-thread recovery, visible-thread refresh, bounded dispatch, R2/R3 failover, MWORKS window patrol | `Docs/Workflows/coagent_ops_patrol_workflow.md` |
| Cross-thread packets, dispatch ticket SLO, semantic boundary, local goal/sub-agent planning fields, MWORKS/ROS2/UE return contracts | `CoAgent/dispatch/communication_contract.md` |
| Current visible departments and owner boundaries | `Docs/Workflows/org_operating_model.md` |
| Historical/recovery delegated-task trace | `Docs/Workflows/agent_task_ledger.md` |
| Session-memory promotion/rejection | `Docs/Workflows/session_memory_migration.md` |
| Workflow index | `Docs/Index/workflow_index.md` |
| Project memory index | `Docs/Index/project_work_memory_index.md` |
| API/MCP index | `Docs/Index/api_index.md` |
| CoAgent runtime/task graph/timeout/prompt sanity | `Docs/Workflows/agent_orchestration.md` |
| MCP/tooling/native hook governance, entry-document slimming, and immediate doc updates | `Docs/Workflows/tooling_assets_governance.md` |
| Final competition packaging checklist | `Docs/Workflows/pre_submit_check.md` |

## 4. Project Direction

MoSim is for the A8 quadrotor competition. The main contribution is robust
quadrotor attitude and position control, not a general robotics navigation
stack.

Primary technical line:

```text
Official PID baseline
  -> improved PID / PID-INDI
  -> NMPC outer loop
  -> INDI attitude inner loop
  -> L1-inspired adaptive disturbance compensation
  -> safety filter
  -> fault injection and control allocation reconstruction
  -> path planning and trajectory smoothing
  -> leader-follower multi-UAV formation
  -> automated simulation, metrics, figures, and report evidence
```

Core principles:

1. Keep control as the main line.
2. Keep planning, formation, MCP automation, safety filtering, fault injection,
   and metrics as replaceable modules.
3. Every claim needs evidence: source, simulation logs, result files, metrics,
   screenshots, figures, or packets.
4. Prefer reproducible workflows and report-ready outputs.
5. Do not guess APIs; consult docs, workflows, skills, or MCP documentation.

## 5. Domain Evidence Boundaries

MWORKS/Sysplorer/Syslab is the formal simulation source. UE is the scene,
visual, sensor, collision, and review surface. ROS2/RViz/FAST-LIO is the native
robotics transport/localization/planner review surface. None of these layers
may claim final closed-loop success without the evidence required by its
current workflow and packet.

Important MWORKS rules:

- Use MCP first for model-level operations when live MWORKS work is authorized.
- Reference the latest CoAgentOps activation/window patrol when live MWORKS
  work is planned.
- Activation/login/license/authorization acceptance needs foreground or
  maximized target-main-window evidence when a hidden UI blocker is possible.
- Ordinary graphical/layout/result-window review routes to MWORKS R2 and uses
  DPI-aware screenshot evidence plus written observations.
- Do not close or restart reusable Sysplorer/Syslab/MWORKS windows unless the
  user/PMO explicitly authorizes it or a documented blocker requires it.

Important ROS2/UE rules:

- Do not claim `planner_ready`, `closed_loop`, runtime success, controller
  performance, or final material/scene acceptance without the declared evidence
  gate.
- Do not publish setpoints, run extra live probes, open foreground RViz/manual
  review, or start UE editor/build/runtime work unless the task packet
  explicitly authorizes that live scope.
- Use local references first for matching UE/UAV simulation behavior patterns
  before online research.

## 6. Skills And Workflows

Use project-local MWORKS skills before generic upstream skills:

| Need | Skill / Workflow |
|---|---|
| MCP/session operations | `Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md` |
| Model/component context | `Docs/Skills/Mworks/mworks-model-context/SKILL.md` |
| Simulation evidence | `Docs/Skills/Mworks/mworks-simulation-evidence/SKILL.md` |
| Runtime diagnostics | `Docs/Skills/Mworks/mworks-runtime-diagnostics/SKILL.md` |
| Sysblock graphical modeling | `Docs/Skills/Mworks/mworks-sysblock-graphical-modeling/SKILL.md` |
| Syslab/MATLAB porting | `Docs/Skills/Mworks/mworks-syslab-porting/SKILL.md` |
| Tests and review | `Docs/Skills/Mworks/mworks-test-quality/SKILL.md` |
| Report figures/replay | `Docs/Skills/Mworks/mworks-report-visualization/SKILL.md` |
| ROS2 runtime | `Docs/Workflows/ros2_runtime_setup.md` |
| UE renderer/console | `Docs/Workflows/unreal_renderer.md` |
| Parameter identification | `Docs/Workflows/identify_quadrotor_parameters.md` |

Use only the workflow/skill needed for the current task. Do not bulk-load large
documentation trees.

## 7. Git And Documentation Hygiene

For normal project changes:

```text
inspect status -> inspect relevant diff -> run targeted checks -> path-limited
git add -> git diff --cached --check -> commit -> push if auth works
```

Rules:

1. Use path-limited Git commands; do not use broad `git add -A`, force push,
   reset, clean, or bulk destructive commands unless explicitly approved.
2. Do not commit secrets, private tokens, local credentials, or generated files
   above GitHub limits.
3. When a task reveals a reusable command, workflow correction, or operating
   constraint, update the appropriate project document before reporting
   completion.
4. Keep `AGENTS.md` small. If a rule becomes executable or detailed, move it
   to a workflow, skill, checker, packet template, or index and leave only a
   pointer here.

## 8. Directory Map

| Directory | Purpose |
|---|---|
| `Docs/Design/` | Algorithm, architecture, scope, and evidence design. |
| `Docs/Workflows/` | Repeatable procedures and CoAgent/PMO operating mechanics. |
| `Docs/Skills/` | Project-local and reference skills. |
| `Docs/Index/` | Documentation, API, memory, and workflow indexes. |
| `Models/` | Project-owned MWORKS/Sysplorer models. |
| `References/` | Official/reference projects and upstream examples. |
| `Config/scenarios/` | Scenario and experiment configuration. |
| `Scripts/` | Automation, quality checks, evidence scripts, and tests. |
| `Results/` | Reproducible outputs, packets, metrics, logs, figures, and review assets. |

## 9. Final Development Policy

When uncertain:

1. Prefer current project documents over chat memory.
2. Prefer small targeted checks over broad assumptions.
3. Prefer source/current evidence over inherited claims.
4. Prefer modular, reversible changes over coupled rewrites.
5. Prefer clear blockers over overclaiming completion.

The project is successful when it forms a reproducible loop:

```text
scenario configuration
  -> model simulation
  -> result extraction
  -> metric calculation
  -> figure/replay generation
  -> report conclusion
```
