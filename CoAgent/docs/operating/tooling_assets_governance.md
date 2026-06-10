# Tooling Assets Governance

> Conservative no-loss migration landing. This file was seeded from
> `Docs/Workflows/tooling_assets_governance.md` on 2026-06-10 so native-surface,
> tooling, hook, context-hygiene, and entry-document slimming rules are not lost
> while CoAgent is made portable. It is currently a mixed portable-core +
> MoSim-adapter copy. Do not slim this file or its MoSim compatibility source
> until `CoAgent/docs/operating/MIGRATION_MAP.md` records each removed block as
> exact, equivalent, intentionally host-local, or obsolete.

> Purpose: maintain MoSim plugins, MCP servers, project-local skills, workflow
> docs, and crawled reference projects without creating a standing
> `Toolchain MCP` department or polluting new-conversation context.

Status: current operating workflow, 2026-06-06 CST.

## 1. Scope

This workflow covers these asset families:

| Asset Family | Location | Meaning |
|---|---|---|
| Reference projects | `References/`, `CoAgent/docs/research/`, `Docs/Index/external_learning_index.md` | Crawled open-source projects, vendor examples, papers, and source audits. These are source material, not active tools. |
| Project skills | `Docs/Skills/` | Condensed MoSim-approved operating procedures that agents may load on demand. |
| Project workflows | `Docs/Workflows/` | Repeatable project procedures, recovery routes, evidence gates, and cross-tool sequences. |
| Indexes | `Docs/Index/` | Human and agent routing tables for docs, APIs, workflows, references, and memory. |
| MCP wrappers/config | `Docs/Skills/*/*/wrappers/`, `Scripts/`, `C:\Users\HP\.codex\config.toml` | Actual runtime entry points for Codex App, Sysplorer/Syslab, Unreal, Blender, ROS2, WindowsMCP, and helper servers. |
| Codex plugins | `C:\Users\HP\.codex\plugins\` | Codex-provided local plugin bundles. Use their skills/tools when relevant, but do not copy provider credentials or large plugin caches into the repo. |
| Codex native hooks | `C:\Users\HP\.codex\hooks.json`, `CoAgent/hooks/codex_native_hook.py`, `CoAgent/hooks/preflight.py` | Hard lifecycle guardrails around session start, tool use, and completion checks. Hooks are not optional context assets. |

## 1.1 Codex Native Surface Policy

Use Codex native capabilities before extending CoAgent runtime. CoAgent should
fill MoSim-specific gaps, not reimplement product surfaces that Codex already
provides.

Wording matters when this rule is copied into another thread prompt. The
correct instruction is: "不要在 CoAgent 中重复实现 Codex 已经原生支持的能力".
Do not use inverted wording such as "不要重复手搓 CoAgent 已由 Codex 原生支持的能力",
because it incorrectly implies CoAgent itself is the capability provided by
Codex.

| Capability | MoSim Use | Avoid |
|---|---|---|
| Native hooks | Enforce mechanical guardrails such as destructive-command blocks, outside-project write blocks, secret-risk paths, and concise session-start reminders. | Loading all skills or long project memory through hooks; broad `Stop` auto-continue loops; treating hooks as proof of correctness after side effects. |
| `AGENTS.md` | Durable repository rules, authority boundaries, verification requirements, and agent coordination policy. | Storing volatile thread titles or high-volume status logs. |
| Skills | On-demand procedural knowledge for a task family. Load the minimal relevant skill only after routing the task. | Loading all skills into every conversation or using skills as hard enforcement. |
| Plugins and apps | Use installed Codex plugin skills, Browser, Windows MCP, workspace dependencies, and app tools when they directly match the task. | Copying plugin cache contents into project source or hand-rolling a local substitute before checking the native/plugin capability. |
| MCP servers | Live tool/data/action boundary for Sysplorer, Syslab, Unreal, Blender, ROS2, Windows desktop, and external services. | Guessing APIs when MCP docs/tools can answer; using MCP broad discovery repeatedly when a narrow probe is enough. |
| Visible threads | Durable department-like context for PMO-dispatched work that needs repeated follow-up or manual review. | Disposable sub-agent work, fake request/response RPC assumptions, or resurrecting deleted legacy departments. |
| Sub-agents | Bounded research/review/execution slices with explicit return evidence. | Long-lived Git/test/supervision queues or tasks that need visible durable context. |
| App automations / thread wakeups | Recurring reminders, health checks, context-memory drift checks, gateway checks, and scheduled review prompts after behavior is verified. | Treating a reminder as completed work or relying on it instead of project ledgers/result packets. |
| Native notify | Local completion/blocker notification when available. Sparse email is the user-facing intervention channel for MoSim long tasks; WeChat is diagnostic or explicitly requested only. | High-volume transcript mirroring or assuming notification delivery proves task success. |

Current installed Windows Codex feature audit on 2026-06-06 found these surfaces
available or enabled: hooks, plugins, apps, Browser, Windows MCP, goals,
multi-agent/thread tooling, workspace dependencies, and MCP/tool-call
elicitation. Re-verify with current Codex commands before depending on a newly
released or changed feature.

Adoption priority:

| Priority | Capability | Required Action |
|---|---|---|
| P0 | Worktrees | Use only for a concrete isolated write task after explicit PMO/user approval and a successful native handoff verification. PMO/R1/R2 do not move to worktrees by default. DevOps owns final Git integration. |
| P0 | Visible threads | Use for durable specialty context only: PMO, DevOps, ROS2 runtime, MWORKS dynamics/control, UE experiment console, Sunray150 assets/PBR, open-source probe/learning, and any future reusable specialty approved by PMO. The old WeChat gateway ops thread is archived and not part of the active set. |
| P0 | Goals | Use for long-running PMO or department tasks. Do not create a goal for every small step, and do not treat a goal as a replacement for result packets or ledgers. |
| P0 | Skills/plugins | Prefer installed Codex/plugin skills before writing new local procedures. Load the minimum skill required by the current task. |
| P0 | MCP/apps | Use native MCP/app surfaces for live tools and external actions before writing ad-hoc scripts, especially Sysplorer/Syslab/Unreal/Blender/ROS2/Windows desktop operations. |
| P0 | Browser / Windows MCP | Use Browser for browser/local web targets and Windows MCP plus Win32/UI Automation scripts for MoSim desktop GUI screenshot/inspection. Computer Use is deprecated for MoSim desktop GUI monitoring and recovery; do not use it for MWORKS/Sysplorer/Syslab. |
| P1 | App automations / thread wakeups | Configure only after behavior is verified locally. Good candidates are PMO/CoAgentOps health checks, context drift check, hook/preflight health, external project inventory, and Git hygiene. Do not schedule WeChat gateway heartbeat unless the user explicitly restores that route. |
| P1 | Native review / `codex review` | Use as a code-review gate or sub-agent-style bounded review, not as a standing test department. Findings must cite files/lines and be integrated by the owner thread. |
| P1 | Non-interactive `codex exec` | Use for clear background tasks such as packet generation, narrow audits, docs checks, and one-shot department prompts. Avoid using TUI as the only automation path. |
| P1 | Workspace dependencies | Use for sheets, slides, docs, packaged runtimes, and report assets instead of guessing local bundled dependency paths. |
| P1 | Native notify | Use as a local completion/blocker signal where available. For MoSim long tasks, sparse email is the default user-facing intervention channel. |
| P2 | App server / remote control | Do not make this a project dependency until a concrete task verifies current stability and security boundaries. |
| P2 | Experimental memory/chronicle/artifact surfaces | Treat as auxiliary only. Project truth remains in `Docs/`, `Results/agent_packets/`, ledgers, source files, and reviewed evidence. |

Decision rule:

```text
mechanical guardrail -> native hook + project preflight
durable repo instruction -> AGENTS.md
task procedure -> skill or workflow
live external action -> MCP/app/plugin
recurring reminder/check -> Codex automation or verified external scheduler
durable specialty context -> visible thread
bounded parallel work -> sub-agent
code review gate -> native review or scoped review sub-agent
background one-shot task -> codex exec
document/runtime dependency lookup -> workspace dependencies
MoSim-specific packet/evidence glue -> CoAgent
```

Before PMO dispatches any non-trivial task, it must run this decision rule as a
planning gate and record the selected native surface in the task graph or task
packet. If the selected surface is a visible thread, the packet must also
declare whether an isolated worktree is required, why a one-shot sub-agent is
insufficient, and where the result/blocker packet will be written. If the gate
points to a native Codex surface, do not add CoAgent runtime or transport
machinery for that task.

Compatibility gate for new JSON task packets:

```powershell
python Scripts\quality\check_agent_task_native_surface_gate.py `
  Results\agent_packets\<request_id>.json --strict
```

This checker is deliberately read-only. It validates that PMO recorded
`native_surface_gate`, `selected_native_surface`, `surface_selection_reason`,
`worktree_required`, `worktree_decision`, and delegated return/blocker paths
without changing CoAgent runtime, transport, or packet schema.

## 2. Ownership

There is no standing `MoSim｜工具链 MCP` department.

| Owner | Responsibility |
|---|---|
| Task thread | Owns the tool/skill/workflow updates discovered during its task. If it finds a reusable command, failure mode, recovery path, or operating constraint, it updates the relevant doc before claiming completion. |
| `MoSim｜CoAgent运维平台` | Owns recurring meta-maintenance: asset inventory cadence, current visible-thread allowlist hygiene, duplicate skill/workflow cleanup proposals, crawler/learning dispatch, and missing-index reports. Details live in `Docs/Workflows/coagent_meta_maintenance.md`. |
| `MoSim｜开源项目探针` | Keeps local reference-project inventory fresh, checks upstream freshness, and returns manifests/update candidates. It does not execute broad new crawls and does not decide adoption. |
| `MoSim｜开源项目学习` | Studies crawled projects/vendor articles and returns adopt/reject/reference-only proposals with evidence. |
| `MoSim｜Codex 上下文维护部` | Updates new-conversation context, project memory index, and recovery notes when tooling decisions affect startup context. Former `MoSim｜文档秘书部` and R-suffixed context-maintenance wording are alias/history only. |
| `MoSim｜DevOps 发布` | Handles safe Git import, ignore/LFS rules, large-file checks, and commits for reference projects or tool assets. |

PMO responsibility: the main PMO thread
`019e9868-83ea-70f0-92c5-a3a408bd78c6` owns adoption of Codex native
capabilities into day-to-day MoSim operation. It should route implementation to
existing visible specialty threads when appropriate, but it remains accountable
for deciding whether a need belongs to native Codex capability, project docs,
CoAgent glue, or a new visible department.

Open-source probe boundary:

```text
MoSim｜开源项目探针
  -> periodically checks local reference mirrors, metadata completeness,
     upstream freshness, and candidate update queues
  -> writes manifests/index deltas only
  -> does not perform broad new crawling as its standing duty

one-shot crawler sub-agent or scoped task packet
  -> fetches or crawls a specific requested repo/page/source slice
  -> records source URL, license, local path, and evidence
  -> stops after producing a manifest or learning input

MoSim｜开源项目学习
  -> evaluates crawled or updated material as adopt/adapt/reference-only/reject
  -> updates project-local workflow/skill/index only after evidence review
```

Do not keep a visible open-source probe thread busy as a generic crawler. If a
new repository, vendor page, MCP server, or docs family needs crawling, PMO or
CoAgentOps should dispatch a bounded sub-agent/task packet with explicit source
scope, write scope, stop condition, and evidence path. The probe thread remains
useful for recurring inventory and freshness checks over already-known local
reference material.

## 3. Promotion Pipeline

Do not move crawled or third-party material directly into active project skills.
Use this pipeline:

```text
discover / crawl
  -> inventory in References or external-learning index
  -> classify: adopt | adapt | reference-only | reject | blocked
  -> run a narrow smoke test when executable behavior is required
  -> write MoSim-specific workflow or skill only after the route is understood
  -> add MCP wrapper/config only when the server is actually useful
  -> add health check and failure recovery
  -> update indexes and new-conversation context only if startup routing changes
```

For open-source MCP tooling, use this intake rule before adding anything to the
Codex config:

```text
check local mirrors first:
  CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md
  Docs/Index/agent_project_classification.md
  References/Agent/Gateway
  References/Agent/Memory
  References/Agent/Security
  References/Agent/Skills
  References/Agent/Platforms
  -> if present locally, inspect the local mirror before web search/download
  -> if absent or stale, then discover via official MCP registry,
     vendor repository, or current project need
  -> classify: active_tool_candidate | reference_only | reject | blocked
  -> prefer existing Codex plugin/app/native surface if it already covers the use
  -> run MCP Inspector or documented health check in a bounded sandbox
  -> add only the smallest required toolset/server
  -> document credentials, dangerous calls, and recovery before routine use
```

Current watchlist from the 2026-06-06 open-source MCP scan:

| Candidate | Current MoSim Use | Disposition |
|---|---|---|
| `modelcontextprotocol/inspector` | Debug and smoke-test MCP servers before accepting a new wrapper/config. | P0 reference tool for MCP validation; use on demand, not always running. |
| `modelcontextprotocol/servers` reference servers (`git`, `fetch`, `filesystem`, `time`, etc.) | Useful examples and occasional local helpers. Local primary mirror: `References/Agent/Gateway/servers`; newer snapshot awaiting dedupe: `References/Agent/Gateway/servers-upstream-snapshot-20260606`. | Reference-first; official repo warns they are examples, so do not treat them as production-ready without MoSim smoke tests. |
| `github/github-mcp-server` | GitHub API context for issues, PRs, code search, code scanning, and remote workflows. Local mirror: `References/Agent/Gateway/github-mcp-server`. | P1 candidate when GitHub remote automation is needed; requires auth/toolset minimization. Not needed for local reference mirror freshness. |
| `microsoft/playwright-mcp` | Browser/UI automation and screenshots. Local primary mirror: `References/Agent/Gateway/playwright-mcp`; duplicate snapshot awaiting dedupe: `References/Agent/Gateway/playwright-mcp-upstream-snapshot-20260606`. | P1 on demand; prefer existing Browser/headless Chrome route for web targets and Windows MCP/Win32 scripts for desktop GUI targets when sufficient. |
| `mcp/io.github.upstash/context7` | Up-to-date library/API docs lookup. Local mirror: `References/Agent/Memory/context7`. | P1 docs lookup candidate; do not promote returned docs to project truth without source review. |
| `oh-my-pi` | Full coding-agent/IDE/runtime reference with MCP, workflow, and operator-surface examples. Local mirror: `References/Agent/Platforms/oh-my-pi`. | Reference-only until a concrete CoAgent/Codex workflow gap needs study. |
| `PrefectHQ/fastmcp` and official MCP Python SDK | Build small project-owned MCP servers when a proven gap exists. | P1/P2 framework reference; no new MoSim MCP server without an approved gap. |
| `docker/mcp-gateway` | Isolated lifecycle/profile management for many MCP servers. | P2 only if MCP count and secrets management become hard to operate manually. |
| `semgrep` MCP | Security scan surface around Semgrep. | P2/blocked for now; prefer deterministic CLI or native review unless a security-gate task approves MCP use. |
| `cloudflare/mcp-server-cloudflare` browser/docs servers | Remote browser rendering/docs or Cloudflare-specific operations. | P2; requires account token and is not needed while local headless capture works. |
| `awesome-mcp-servers` and MCP registry directories | Discovery sources. | Reference-only; each candidate still needs primary-source and smoke review. |

Required fields for a new reference project:

```text
name:
source_url:
local_path:
stars_or_quality_signal:
license:
last_checked:
category:
possible_use:
adoption_status: adopt | adapt | reference-only | reject | blocked
risks:
evidence_path:
owner_thread:
```

Required fields for a new or changed MCP server:

```text
name:
purpose:
launcher_command:
runtime_lane: Windows-native | WSL | external GUI
workspace_boundary:
health_check:
smoke_test:
common_failures:
recovery_steps:
dangerous_calls:
related_skill_or_workflow:
owner_thread:
last_verified:
```

Required fields for a new or changed skill:

```text
skill_name:
trigger_condition:
read_minimum:
tool_sequence:
forbidden_actions:
evidence_required:
smoke_or_acceptance_check:
overlap_with_existing_skills:
source_references:
owner_thread:
last_reviewed:
```

Required fields for a new or changed Codex hook:

```text
hook_name:
event:
scope: global | project
config_path:
adapter_path:
enforced_policy:
allowed_roots:
blocked_actions:
trust_requirement:
smoke_test:
failure_mode:
owner_thread:
last_verified:
```

## 4. Runtime Boundaries

Use these boundaries unless a later approved workflow changes them:

| Tool Area | Boundary |
|---|---|
| MWORKS/Sysplorer/Syslab | Use MCP first for interactive model work. Keep `source=MWORKS_MCP`, `source=MWORKS_GUI`, and `source=offline_script` separated. Do not call `ClearAll` or `ChangeDirectory`. |
| Unreal / UE5 | UE is rendering, scene, sensor/collision oracle, and operator intent UI. It must not be the source of controller/planner success. |
| ROS2 / RViz2 / FAST-LIO | WSL runtime lane by default. Native robotics windows are required for active point-cloud/map review. Browser HTML is not accepted active evidence. |
| Blender / material tooling | Use for visual asset assembly and material work. Verify import/export compatibility before replacing UE assets. |
| Windows MCP / Win32 / UI Automation | Use only when desktop inspection or GUI operation is necessary. Prefer project-local evidence scripts, screenshots, and narrow probes over broad GUI automation. Computer Use is deprecated for MoSim desktop GUI work and must not be used for MWORKS/Sysplorer/Syslab. |
| Codex plugins | Use installed plugin skills/tools on demand. Do not assume plugin cache contents are project-owned source. |
| Codex native hooks | Global hook config lives under `C:\Users\HP\.codex\hooks.json`; the MoSim adapter is project-owned and acts only for this repository. Hooks may block risky tool calls, but they do not replace tests, reviews, result packets, or startup context reading. |

## 5. Context Hygiene

New conversations must not load all skills, all references, or all MCP docs.
Use this startup path:

```text
AGENTS.md
Docs/Workflows/new_conversation_context.md
Docs/Index/project_work_memory_index.md
Docs/Index/workflow_index.md only to route the current task
one task-specific workflow or skill
```

Rules:

1. Load `Docs/Skills/` selectively. A task should read only the skill that it
   needs.
2. Treat `References/` as a source-of-truth library only after narrowing the
   exact project, file, and behavior being inspected.
3. Do not promote a chat-only memory or a broad reference-project claim into a
   workflow until it is checked against current files or executable evidence.
4. If a toolchain rule changes startup behavior, update
   `Docs/Workflows/new_conversation_context.md` and
   `Docs/Index/project_work_memory_index.md`.
5. If a new skill or workflow becomes the preferred route, update
   `Docs/Index/workflow_index.md`.
6. Hooks can inject concise context reminders, but they must not become the
   primary memory-loading mechanism. New conversations still follow the read
   order in `Docs/Workflows/new_conversation_context.md`.

## 6. Official MWORKS Documentation Routing

Official MWORKS/Sysplorer/Syslab documentation can be large. Do not paste
manuals, converted PDFs, or broad API extracts into `AGENTS.md` or fresh
conversation context.

Use the current project documentation route:

```text
official docs / PDFs / web docs
  -> scan or convert with Scripts/docs tools
  -> store curated outputs under Docs/MworksDocs/
  -> index them through Docs/Index/doc_index.md and Docs/Index/api_index.md
  -> promote repeatable project practice into Docs/Skills/Mworks/ or Docs/Workflows/
  -> consult MCP documentation tools when executable API behavior is unclear
```

Current entry points:

| Need | Entry |
|---|---|
| MWORKS documentation inventory | `Docs/Index/doc_index.md` |
| MCP/API/script lookup | `Docs/Index/api_index.md` |
| Converted official docs | `Docs/MworksDocs/converted/` |
| Scan/category indexes | `Docs/MworksDocs/scan/` |
| Project execution procedures | `Docs/Skills/Mworks/` and `Docs/Workflows/` |

If a newly converted official document changes the preferred project route,
update `Docs/Index/workflow_index.md` and only add startup-context text when
fresh conversations need that fact immediately. Historical paths such as
`Docs/Mworks/` are obsolete unless a current file explicitly reintroduces them.

## 7. Maintenance Cadence

When Codex App automation tools or an external scheduler are configured and
verified, recurring checks may be scheduled. Until then,
`MoSim｜CoAgent运维平台` keeps a manual checklist or dispatches task packets.

Recommended recurring checks:

| Cadence | Owner | Check |
|---|---|---|
| Weekly or before major work | `MoSim｜CoAgent运维平台` | Verify workflow index, duplicate skills, current visible-thread allowlist, stale MCP names, and broken routing links. If an old ID is absent from the current scan, remove it from dispatchable registry instead of maintaining a separate blacklist. |
| Weekly or after Codex upgrade | `MoSim｜CoAgent运维平台` | Verify native hooks are trusted, `codex doctor` is healthy, feature list still exposes required surfaces, and hook smoke tests pass. Record evidence per `Docs/Workflows/coagent_meta_maintenance.md`. |
| Weekly or on demand | `MoSim｜开源项目探针` | Inventory newly crawled reference projects and flag missing metadata. |
| After each crawl batch | `MoSim｜开源项目学习` | Produce adopt/adapt/reference-only/reject proposals with evidence. |
| After any MCP/config change | Task owner | Run health check and record exact failure or pass evidence. |
| Before Git import | `MoSim｜DevOps 发布` | Check large files, secrets, license markers, gitlinks, generated assets, and ignore/LFS strategy. |
| After repeated failure | Task owner plus `MoSim｜CoAgent运维平台` if reusable | Update workflow/skill with the recovery path or anti-pattern. |

## 8. Acceptance Gates

A tooling asset is accepted only when:

```text
source and local path are known
owner thread is known
intended use is explicit
minimum smoke test or review evidence exists
dangerous or forbidden actions are recorded
index entry is updated
new-conversation context is updated only if needed
Git/import policy is clear
```

A tooling asset is rejected or quarantined when:

```text
license is unclear for intended use
source path or provenance is unclear
it requires credentials or personal data in project files
it duplicates an existing skill/workflow without improvement
it encourages fake evidence, toy visualization, or bypassing MWORKS/ROS/UE boundaries
it cannot pass a minimal health check and no task depends on fixing it now
```

## 9. Immediate Documentation Rule

When a task reveals a reusable command, successful recovery route, workflow
correction, or new operating constraint, update the relevant project document in
the same task:

| Finding | Update |
|---|---|
| MCP launch or failure recovery | `Docs/Workflows/debug_mcp.md` or the related skill |
| Sysplorer/Syslab/MWORKS operation | `Docs/Skills/Mworks/` and relevant workflow/index |
| Unreal or Epic/Fab operation | `Docs/Skills/Unreal/`, `Docs/Workflows/unreal_renderer.md`, or `Docs/Index/workflow_index.md` |
| ROS2/RViz2/FAST-LIO operation | `Docs/Workflows/ros2_runtime_setup.md` or related architecture doc |
| Reference project adoption/rejection | `Docs/Index/external_learning_index.md` or `CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md` |
| New startup/recovery rule | `Docs/Workflows/new_conversation_context.md`, `CoAgent/docs/operating/agent_os_operating_model.md`, and `Docs/Index/project_work_memory_index.md` |
| Organization/thread rule | `CoAgent/docs/operating/org_operating_model.md`; MoSim adapter `Docs/Workflows/org_operating_model.md`; `Docs/Index/codex_app_session_research.md` |
| Codex native hook or App capability change | `CoAgent/hooks/README.md`, `Docs/Index/codex_app_session_research.md`, and this workflow |

Do not end a task with "record later" when the reusable rule is already known.

## 10. Entry-Document Slimming Rule

`AGENTS.md` and `Docs/Workflows/new_conversation_context.md` are routing and
startup documents. They may be shortened only after executable or durable
content has a verified destination.

Hard order: land first, audit second, slim third. Do not delete, compress, or
redirect a rule to a child document before the child document exists and the
removed block has a deletion-to-landing audit row.

Before deleting or compressing content from an entry document:

1. Classify each removed block as one of:
   `hard_boundary`, `startup_context`, `workflow_procedure`, `packet_contract`,
   `domain_skill_rule`, `index_pointer`, `historical_rejected_route`, or
   `obsolete_superseded`.
2. Move executable detail to the narrowest active destination:

   | Content Type | Destination |
   |---|---|
   | visible-thread dispatch, SLO, semantic boundary, packet fields | `CoAgent/dispatch/communication_contract.md` |
   | CoAgentOps patrol, recovery, bounded dispatch, R2/R3 failover | `CoAgent/docs/operating/coagent_ops_patrol_workflow.md`; MoSim adapter `Docs/Workflows/coagent_ops_patrol_workflow.md` |
   | task graph, sub-agent planning, timeouts, native surface choice, prompt sanity, long Git | `CoAgent/docs/operating/agent_orchestration.md`; MoSim adapter `Docs/Workflows/agent_orchestration.md` |
   | tool/MCP/plugin/hook governance, context hygiene, documentation promotion, entry-doc slimming | this file |
   | organization, route names, department ownership | `CoAgent/docs/operating/org_operating_model.md`; MoSim adapter `Docs/Workflows/org_operating_model.md` |
   | current startup facts, accepted/rejected routes, current product boundaries | `Docs/Workflows/new_conversation_context.md` |
   | MWORKS execution details | the relevant `Docs/Skills/Mworks/*/SKILL.md` |
   | official documentation routing | `Docs/Index/doc_index.md`, `Docs/Index/api_index.md`, and `Docs/Index/workflow_index.md` |
   | final packaging and release checks | `Docs/Workflows/pre_submit_check.md` |

3. If a block is obsolete, name the superseding document or evidence packet in
   the commit/diff note. Do not silently delete it.
4. Update `Docs/Index/workflow_index.md` or `Docs/Index/project_work_memory_index.md`
   when the preferred route changes.
5. Run a targeted search for stale wording, deleted thread names, deprecated
   model-effort settings, mojibake, and old paths such as `Docs/Mworks/` when
   the edit touches startup or routing docs.
6. Record an audit row for each removed or weakened block:

   ```text
   source block:
   landing file and section:
   status: exact | equivalent | intentionally_host_local | obsolete_superseded | missing
   reviewer:
   date:
   ```

An entry-document slimming task is incomplete if removed executable content
cannot be found in a child workflow, skill, contract, checker, packet template,
or index. It is also incomplete if the landing file is missing, the audit row
is missing, or the destination weakens stop conditions without a PMO/user
decision. In that case, restore the block or add the missing child-document
rule before reporting completion.

### 10.1 Current Slimming Landing Map

The 2026-06-09 `AGENTS.md` /
`Docs/Workflows/new_conversation_context.md` slimming keeps only routing and
startup facts in entry documents. The removed executable/detail blocks are
valid only because they are landed here:

| Removed Entry-Doc Topic | Landing Document |
|---|---|
| project-local filesystem boundary, external infrastructure exceptions, desktop GUI tool choice, Computer Use deprecation, source-first troubleshooting | `AGENTS.md`, this workflow section 11, `Docs/Workflows/new_conversation_context.md#10-codex-native-feature-use` |
| CoAgent runtime/transport/schema/permanent-department approval gate and native-surface-first rule | `CoAgent/docs/operating/agent_orchestration.md`, this workflow section 1.1, `CoAgent/STATUS.md` |
| PMO direct visible-thread routing, no mandatory DispatchCenter, visible-thread lifecycle authority, department ownership, context-maintenance title aliases | `CoAgent/docs/operating/org_operating_model.md`, `CoAgent/docs/operating/agent_orchestration.md`, `CoAgent/dispatch/department_threads.json` |
| visible-thread packet fields, local department goal, critical-path split, `subagent_plan`, evidence outputs, semantic-boundary enums, dispatch-ticket SLO, R2/R3 failover scope | `CoAgent/dispatch/communication_contract.md`, `CoAgent/docs/operating/coagent_ops_patrol_workflow.md`, `CoAgent/docs/operating/agent_orchestration.md` |
| CoAgentOps 10-minute patrol, approval/review/provider classification, durable-start liveness, main-shell pending indicators, dead-thread recovery, restart fail-close, board update limits, MWORKS window classification | `CoAgent/docs/operating/coagent_ops_patrol_workflow.md`, `Docs/Workflows/mainline_operations_board.md` |
| sparse Chinese email notification, manual-intervention alert wording, deleted WeChat route boundary, explicit WeChat-diagnosis-only path | `CoAgent/docs/operating/agent_orchestration.md`, `CoAgent/docs/operating/coagent_meta_maintenance.md`, `Docs/Workflows/debug_mcp.md`, `CoAgent/dispatch/department_threads.json` |
| MWORKS MCP minimal-impact rules, session reuse, forbidden Sysplorer APIs, activation/license/login/GUI-error stop rules, background screenshot limitations, phase screenshot and engineering-output requirements | `Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md`, `Docs/Skills/Mworks/mworks-simulation-evidence/SKILL.md`, `Docs/Skills/Mworks/mworks-sysblock-graphical-modeling/SKILL.md`, `CoAgent/dispatch/communication_contract.md` |
| simulation evidence source labels, graphical Sysblock counterpart requirement, cleanup/session rules, native result / `.msr` review boundary | `Docs/Skills/Mworks/mworks-simulation-evidence/SKILL.md`, `Docs/Workflows/run_simulation.md`, `Docs/Workflows/produce_simulation_evidence.md` |
| Sysplorer/Sysblock modeling modality, hybrid Modelica + Sysblock bridge limits, no text-overwrite topology rule | `Docs/Skills/Mworks/mworks-sysblock-graphical-modeling/SKILL.md`, `Docs/Skills/Sysplorer/ty-sysplorer-modeling-rules` |
| UE/RViz/FAST-LIO window split, rejected toy mapping routes, source-first UAV simulator references, current Factory Gate B limitation, Sunray visual/material boundary | `Docs/Workflows/new_conversation_context.md`, `Docs/Workflows/unreal_renderer.md`, `Docs/Workflows/ros2_runtime_setup.md`, `Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md` |
| algorithm/source-of-truth design routing, final report/checklist routing, project directory map | `Docs/Index/doc_index.md`, `Docs/Index/workflow_index.md`, `Docs/Workflows/pre_submit_check.md`, `AGENTS.md#8-directory-map` |
| long Git work, temporary `.gitignore` throttle/drain rules, large-file/LFS/gitlink gates, GitIntegrator ownership | `CoAgent/docs/operating/agent_orchestration.md#5-long-git-work`, `AGENTS.md#7-git-and-documentation-hygiene` |
| prompt/task-packet semantic sanity, bad-prompt correction, vague status word rejection | `CoAgent/docs/operating/agent_orchestration.md#prompt-and-task-packet-semantic-sanity-gate`, `CoAgent/docs/operating/coagent_meta_maintenance.md` |
| session-memory migration, cache-first three-round promotion/rejection, startup read order | `Docs/Workflows/new_conversation_context.md`, `CoAgent/docs/operating/session_memory_migration.md`, `Docs/Index/project_work_memory_index.md` |

If a future slimming edit removes a topic that is not covered by this table,
add its landing document before deleting the entry text. If a landing document
is renamed, update this table and `Docs/Index/workflow_index.md` in the same
change.

## 11. Filesystem And Desktop Tool Boundary

Default project operations stay inside `C:\Users\HP\Desktop\MoSim`.
Infrastructure exceptions must name the external path and reason before acting.
Common approved exception classes are Codex config/hook inspection, MCP wrapper
repair, SSH/Git authentication setup, or environment-variable verification.

Do not read or modify sibling user directories, browser profiles, SSH folders,
token/key files, other drives, WSL user homes, `/home/linux`, or
`/home/lzy18001500226` unless the approved task explicitly names that path.

MoSim desktop GUI monitoring, screenshots, recovery, and click workflows should
use Windows MCP, Win32/UI Automation, and project-local evidence scripts.
Computer Use is deprecated for MoSim desktop GUI work and must not be used for
MWORKS/Sysplorer/Syslab authorization, screenshots, login recovery, reusable
window checks, or GUI-error handling. Browser remains the route for
browser/local web targets.

Source-first troubleshooting rule: when a UE/UAV behavior problem matches an
existing ecosystem pattern, inspect local references first, especially RflySim,
Sunray/YunZong, PX4/Gazebo, AirSim, FAST-LIO, and EGO-Planner material under
`References/`. Use official docs or online sources only after local references
do not resolve the issue, and record any confirmed reusable pattern in the
relevant workflow before continuing.
