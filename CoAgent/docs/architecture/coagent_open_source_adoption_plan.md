# CoAgent Open-Source Adoption Plan

Date: 2026-05-30

Status: design package plus approved gateway smoke update. This document does
not approve unattended automation, broad code import, or unreviewed external
message sending. The user approved a cc-connect Weixin smoke test on
2026-05-31, and the project now has a narrow packet-to-Weixin adapter for
manual-review notifications.

## Decision

CoAgent should not be built from scratch, and no mirrored upstream project is
currently a complete drop-in replacement.

The adopted strategy is selective reuse:

```text
CoAgent-owned core:
  task state, context packs, result packets, safety policy, MoSim evidence rules

Reused or ported upstream capabilities:
  control UI, task board, inbox, worktree isolation, gateway notifications,
  context/memory indexing, skill lifecycle, durable workflow patterns,
  security/evaluation gates
```

The central rule is: adopt upstream components only when they reduce execution
risk and do not weaken MoSim's task evidence, safety boundary, or Codex/MCP
integration model.

## Why No Single Upstream Replaces CoAgent

CoAgent has requirements that are not covered by one existing project:

- project-owned durable task ledger and result packets;
- Codex App / VSCode / CLI visible conversation lifecycle;
- task-first multi-conversation topology, not only role-first teams;
- MoSim-specific MWORKS, Unreal, Epic/Fab, Git, report, and simulation evidence
  gates;
- strict project-local filesystem and credential boundaries;
- human intervention states for activation, login, license, manual visual
  review, destructive actions, and Git explosion;
- selective context packs instead of replaying full chat history;
- reusable architecture that can move to other projects without MoSim-specific
  tools baked into the control core.

Therefore the core coordination model remains MoSim-owned. Upstream projects
are used as source code, protocols, UI references, or implementation patterns.

## Adoption Modes

| Mode | Meaning | Review requirement |
|---|---|---|
| `reuse` | Use the upstream component or fork with minimal changes. | License, security, dependency, and integration review. |
| `port` | Reimplement the upstream pattern in CoAgent's stack. | Architecture review and targeted tests. |
| `wrap` | Run upstream as an external service/tool behind a narrow adapter. | Config, auth, data boundary, and failure-mode review. |
| `study` | Keep as design reference only. | Record the lesson and rejection reason for direct use. |
| `reject` | Do not use for CoAgent. | Record the blocking reason. |

## Primary Candidate Matrix

| Project | Path | Best Use | Adoption Mode | Rationale |
|---|---|---|---|---|
| `CodexMonitor` | `References/Agent/Control/CodexMonitor` | Codex workspaces, threads, worktrees, conversation UI, Git/GitHub panels, daemon model. | `port` first; possible later `reuse` for UI/control-plane slices. | Closest to the Codex App/control-console problem. It is not a task-state or safety system, so CoAgent keeps its own ledger and policy core. |
| `OpenMOSS` | `References/Agent/Control/OpenMOSS` | Task/module/subtask data model, planner/executor/reviewer/patrol roles, review loop, dashboard, scoring, patrol. | `port` | Strongest fit for "AI company operating system" semantics. It depends on OpenClaw-style agents and generic office/content workflows, so use its model rather than adopting it whole. |
| `ClawTeam` | `References/Agent/Control/ClawTeam` | Inbox, task board, CLI team commands, worktree/tmux isolation, worker identity, file or P2P transport. | `port` | Strong fit for multi-agent communication and isolated work. CoAgent should copy the concepts into packet-first communication instead of letting workers communicate invisibly. |
| `cc-connect` | `References/Agent/Gateway/cc-connect` | WeChat/Feishu/DingTalk/Slack/Telegram/QQ gateway, hooks, Management API, Bridge WebSocket protocol, mobile human intervention. | `wrap` for experiments; `port` selected protocol ideas. | Best current candidate for notification and human-intervention gateway. Do not let it become the task source of truth or hold secrets in tracked files. |
| `hermes-agent` | `References/Agent/Platforms/hermes-agent` | Memory, context compression, scheduler, gateway, skills, hooks, provider/runtime adapters, self-improvement loops. | `port` | Very rich runtime source. Direct adoption would replace too much of Codex/MoSim's boundary, but its memory and lifecycle patterns are valuable. |
| `openclaw` | `References/Agent/Platforms/openclaw` | Local-first gateway/platform, skills, session routing, sandbox policy, channel integrations, operator UX. | `study` plus selective `port` | Useful as platform philosophy and security/gateway reference. It is too broad to become CoAgent's core because CoAgent is a project operating system, not a personal assistant gateway. |
| `agent-teams-ai` | `References/Agent/Control/agent-teams-ai` | Team UI, agent-to-agent messages, task logs, review flow, desktop app. | `study`; avoid direct code reuse unless license is approved. | Local license is AGPL-3.0, which is high-friction for direct reuse. Still valuable for UX and product-control-plane patterns. |
| `OpenHands` | `References/Agent/Platforms/OpenHands` | Full coding-agent platform, agent server, React UI, execution environment. | `study` | Mature but too large and ecosystem-shifting for current CoAgent. Use as a benchmark for runtime/UI separation and coding-agent safety. |
| `langgraph` | `References/Agent/Workflow/langgraph` | Durable graph execution, HITL interrupts, memory, checkpointing. | `port` patterns later | Useful when CoAgent outgrows simple task ledger and packet routing. Do not introduce dependency before minimal loop proves stable. |
| `temporal` | `References/Agent/Workflow/temporal` | Durable workflow retries, long-running workflow semantics, worker model. | `study` now; possible later `wrap` | Strong for production workflow durability, but too heavy for the current local-first phase. |
| `AI-Infra-Guard` | `References/Agent/Security/AI-Infra-Guard` | MCP/skill/agent security scanning. | `port` or `wrap` after review | Needed before broad tool/MCP expansion. |
| `promptfoo` | `References/Agent/Security/promptfoo` | LLM eval/red-team/CI checks. | `wrap` later | Good candidate for trace and prompt regression checks. |
| `context7` / `docs-mcp-server` | `References/Agent/Memory/context7`, `References/Agent/Memory/docs-mcp-server` | Up-to-date docs retrieval and local docs MCP/search. | `wrap` | Useful for knowledge lookup. Must stay read-only by default. |
| `AutoSkill` / `ECC` | `References/Agent/Skills/AutoSkill`, `References/Agent/Skills/ECC` | Skill lifecycle, hooks, rule packs, cross-client operator methods. | `port` | Skills are selective context; hooks are hard policy. These projects help separate the two. |

## What CoAgent Must Own

These parts should be handwritten or kept as existing CoAgent-owned code:

1. Canonical task ledger and state vocabulary.
2. Task packet, result packet, review packet, blocker packet contracts.
3. Context-pack assembler and context freshness policy.
4. MoSim project boundary, filesystem rules, and approval gates.
5. MWORKS/UE/Epic/Fab capability gates and evidence labeling.
6. Goal alignment and drift detection.
7. Human-review package contract.
8. Integration rules for Git, worktrees, tests, simulation evidence, and report
   assets.
9. Adoption registry that records upstream component decisions and licenses.

Rationale: these are the project-specific correctness layer. If delegated to an
upstream runtime, CoAgent would lose the audit trail needed for engineering
work.

## What Should Be Reused First

### Phase 1: Design-to-Minimal-Loop

Goal: improve the existing CoAgent miniloop without switching platforms.

- Port `OpenMOSS` task/subtask/review/patrol concepts into the current task
  schema.
- Port `ClawTeam` inbox/worktree identity ideas into packet-first
  communication.
- Add `cc-connect` as a reviewed gateway candidate, not as an always-on sender.
- Use `CodexMonitor` as the UI/control-plane reference for future visible
  conversation management.

Exit criteria:

- adoption matrix reviewed;
- no runtime expansion beyond approved miniloop;
- all adopted concepts have a target CoAgent file/module;
- security risks and license risks are documented.

### Phase 2: Gateway and Human Intervention Spike

Goal: prove a safe notification path for blocked tasks.

- Run `cc-connect` locally only after secrets/config are placed outside tracked
  files.
- Use its internal send path / Management API / Bridge protocol behind a
  CoAgent adapter.
- Start with dry-run notification packets before sending real IM messages.
- Notify only for approved blocker classes:
  `auth_required`, `approval_required`, `manual_review_required`,
  `incident_required`.
- For Weixin on WSL, keep the runtime `data_dir` on WSL local storage when the
  internal Unix socket is needed; `/mnt/c` can receive messages but cannot host
  `api.sock`.

Exit criteria:

- one dry-run blocker packet maps to one outbound message payload;
- one real smoke packet can be sent by explicit `--send`;
- dedupe key prevents repeated spam;
- no token or account data enters Git;
- user can disable the gateway with one config flag.

### Phase 3: Control Plane/UI Spike

Goal: avoid hand-building a poor front-end.

- Compare `CodexMonitor`, `OpenMOSS`, and `agent-teams-ai` UI surfaces.
- Prefer adapting existing UI panels over creating a new dashboard.
- Keep Codex App as the main review surface until a better local control plane
  is proven.

Exit criteria:

- selected UI base or explicit rejection;
- data model mapping to CoAgent task/result packets;
- no broad UI fork without license/security approval.

### Phase 4: Memory/Skill/Security Upgrade

Goal: make long tasks recoverable without loading all skills or all history.

- Port Hermes/context-engineering patterns for context compression and memory
  promotion.
- Use `context7`/`docs-mcp-server` style read-only lookups for docs.
- Add security/eval checks from `AI-Infra-Guard`, `promptfoo`, and `rogue`
  before broad automation.

Exit criteria:

- context pack quality checks;
- skill selection remains opt-in and task-scoped;
- hooks stay mandatory policy, not optional context.

## Target Architecture After Adoption

```text
User / Codex App / VSCode
  -> MainAgent / PMO conversation
  -> CoAgent task ledger and packet store
  -> Dispatch topology selector
  -> visible scoped Codex conversations
  -> result/review/blocker packets
  -> optional Gateway adapter (cc-connect-style)
  -> Git / MCP / simulation / report evidence gates
```

External projects plug in around the core:

```text
CodexMonitor-like UI      -> view/control conversations and worktrees
OpenMOSS-like model       -> task, subtask, review, patrol
ClawTeam-like protocol    -> inbox, worker identity, worktree isolation
cc-connect-like gateway   -> human intervention notifications
Hermes/OpenClaw patterns  -> memory, skills, hooks, operator UX
LangGraph/Temporal ideas  -> future durable workflow escalation
Security tools            -> preflight, eval, MCP/skill scanning
```

## Immediate Backlog for User Review

| Priority | Task | Type | Acceptance |
|---|---|---|---|
| P0 | Update reference indexes for `Gateway/cc-connect`. | design/index | Validation passes and docs route Gateway correctly. |
| P0 | Freeze this adoption matrix. | design | User approves or edits reuse/self-build decisions. |
| P0 | Create CoAgent adoption registry format. | design | Every upstream use has mode, license, risk, target module, and review status. |
| P1 | Map `OpenMOSS` task schema to CoAgent packet schema. | design | Field-by-field mapping with conflicts listed. |
| P1 | Map `ClawTeam` inbox/worktree concepts to packet-first communication. | design | One example task shows coordinator-visible message flow. |
| P1 | Map `cc-connect` Bridge/Management API to blocker notification packets. | design spike | Dry-run payload only; no real external sending. |
| P1 | Compare `CodexMonitor` vs `OpenMOSS` vs `agent-teams-ai` UI reuse. | design spike | UI recommendation with license/security caveats. |
| P2 | Evaluate security tools for MCP/skill expansion. | design spike | Security gate checklist before broader automation. |

## Review Questions

The user should approve or modify:

1. Should `cc-connect` be treated as the first Gateway candidate for human
   intervention notifications?
2. Should `CodexMonitor` be the first UI/control-plane reference instead of
   OpenMOSS or agent-teams-ai?
3. Should AGPL-licensed projects such as `agent-teams-ai` remain study-only
   unless the whole CoAgent licensing strategy changes?
4. Should Phase 2 permit a dry-run gateway adapter before any real WeChat or
   IM message sending?
