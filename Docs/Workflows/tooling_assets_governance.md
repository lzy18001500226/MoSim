# Tooling Assets Governance

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
| `MoSim｜Codex 上下文维护` | Updates new-conversation context, project memory index, and recovery notes when tooling decisions affect startup context. |
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
| WindowsMCP / Computer-use tools | Use only when desktop inspection or GUI operation is necessary. Prefer screenshots and narrow probes over broad GUI automation. |
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

## 6. Maintenance Cadence

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

## 7. Acceptance Gates

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

## 8. Immediate Documentation Rule

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
| New startup/recovery rule | `Docs/Workflows/new_conversation_context.md` and `Docs/Index/project_work_memory_index.md` |
| Organization/thread rule | `Docs/Workflows/org_operating_model.md` and `Docs/Index/codex_app_session_research.md` |
| Codex native hook or App capability change | `CoAgent/hooks/README.md`, `Docs/Index/codex_app_session_research.md`, and this workflow |

Do not end a task with "record later" when the reusable rule is already known.
