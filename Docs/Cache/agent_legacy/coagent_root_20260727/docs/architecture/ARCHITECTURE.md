# CoAgent Architecture

## Objective

Build a project-owned agent system that is:

- reusable across projects,
- visible through Codex App conversations,
- durable across interrupted sessions,
- compatible with Codex tool/MCP strengths,
- not dependent on fragile hidden subagent state.

This is not limited to Hermes feature migration. Hermes is one strong reference
source, but CoAgent must also learn from Codex, Anthropic/Claude engineering
articles, Anthropic SDK beta runtime resources, agent skills, and other
multi-agent/workflow systems. The result must be a MoSim-owned architecture,
not a transplanted third-party runtime.

## Current Approval Gate

The design checkpoint through `COAGENT-IMPL-08` is complete. Current design
continuation is `COAGENT-DESIGN-11`, which consolidates existing
vendor/framework multi-agent research into a CoAgent architecture mapping
before writing the final operating architecture. It does not approve
transport, app-server, automation, automatic conversation creation, automatic
worktree provisioning, or department expansion.

Start with `CoAgent/STATUS.md`.

Use `CoAgent/docs/decisions/coagent_design_discussion_packet.md` as the concise
discussion packet and freeze gate. Use
`CoAgent/docs/research/THREE_ROUND_STUDY_AND_DISCUSSION.md` for the expanded
evidence behind it.

Use `CoAgent/docs/architecture/enterprise_to_agent_mapping.md` and
`CoAgent/docs/architecture/coagent_complexity_control.md` before translating the
enterprise operating model into runtime behavior. These documents define goal
hierarchy, context hierarchy, department-to-agent mapping, conversation
creation limits, and the first-phase ban on department-internal durable agent
swarms.

The durable decision record is
`CoAgent/docs/decisions/coagent_design_decision_record.md`. It is now `approved`, so
the initial protocol and compliance tasks are allowed and completed. Use
`CoAgent/docs/architecture/coagent_agent_design_protocol.md` for the current conversation
/goal/context/packet contract, and `CoAgent/docs/architecture/coagent_task_surface_model.md`
for task surface, worktree, and review surface design. Use
`CoAgent/docs/architecture/coagent_review_merge_protocol.md` for acceptance, merge, and
closeout role separation. Use
`CoAgent/docs/architecture/coagent_task_team_architecture.md` for the current
multi-conversation task-team, shared-context, scoped-conversation, and
worktree strategy. Use
`CoAgent/docs/architecture/coagent_vendor_pattern_mapping.md` to see how existing
Anthropic/OpenAI/A2A/ADK/Semantic Kernel/LangGraph/Hermes/Codex/OpenClaw and
other framework lessons map into CoAgent objects. Use
`CoAgent/docs/architecture/coagent_open_source_adoption_plan.md` for the
current reuse-vs-port-vs-self-build decision matrix. The current design
direction is selective reuse: CoAgent owns task state, packet contracts,
context, safety, and MoSim evidence rules, while upstream projects provide
control-plane, gateway, inbox, worktree, memory, skill, UI, and security
patterns after review. Do not add the following until their own later tasks are
approved and verified:

- new permanent department conversations,
- app-server transport,
- unattended automation,
- workflow replay,
- task-state schema migration,
- scheduled repo-update jobs,
- memory promotion beyond source-linked evidence,
- broad hook rewrites,
- task/result packet schema changes beyond the `COAGENT-IMPL-01` vocabulary
  alignment.

## Why This Exists

The current Codex subagent model is useful for bounded tasks, but it is not a
durable department system.

Observed limitations:

- subagent context is isolated,
- cross-agent communication is weak,
- long-running work is easy to lose,
- hidden subagents are not the same as user-visible department conversations,
- chat state alone is not durable enough for Git, review, test, and queue work.
- model capability declines when irrelevant long context accumulates, so
  completed worker context should be summarized into project state and released.

Therefore CoAgent uses a different rule:

```text
Codex main conversation = user-facing orchestrator
visible Codex App conversations = operating fronts and scoped task surfaces
task teams = large-objective execution containers
worktrees = file/Git isolation surfaces
project-owned runtime/logs = durable state
external open-source projects = reference only
```

## Learning Scope

CoAgent architecture decisions should be grounded in a recurring learning loop
over these sources:

- `References/Agent/`
- `References/Agent/`, routed through `Docs/Index/agent_project_classification.md`
- `References/Agent/anthropic-sdk-python/src/anthropic/resources/beta`
- Hermes / Hermes Desktop
- Codex source
- Anthropic Engineering / Claude engineering articles
- other high-quality multi-agent, workflow, memory, context-engineering, and
  coding-agent systems

Use `CoAgent/docs/research/LEARNING_STRATEGY.md` for the audit contract and adoption
taxonomy. Each source should end as `adopt_now`, `adapt_later`,
`portable_only`, `reject`, or `unknown`, with evidence.

## Long-Context Boundary

The design assumes that agent capability degrades as irrelevant context grows.
Long-running work must not depend on a single ever-growing transcript.

Required pattern:

```text
new long task
  -> task team charter
  -> team-level shared context pack
  -> one or more scoped context packs
  -> scoped visible task conversations when needed
  -> project-owned task packet / result packet
  -> runtime checkpoint and run summary
  -> searchable knowledge update
  -> release short-lived worker context
```

This is why CoAgent uses durable task packets, result packets, run summaries,
knowledge indexes, and visible department conversations instead of treating
hidden subagents as durable departments.

The local recoverability gate for this boundary is:

```bash
python3 CoAgent/doctor/coagent_doctor.py
```

The doctor does not prove task quality. It proves that the project-owned
runtime, indexes, learning records, dispatch registry, and automation planning
surface are coherent enough to start or resume work.

## Layer Model

### 1. Policy Layer

Source:

- `AGENTS.md`
- `CoAgent/docs/operating/agent_os_operating_model.md`
- `CoAgent/docs/operating/org_operating_model.md`
- `CoAgent/docs/operating/agent_orchestration.md`

Responsibility:

- project boundary,
- approval/escalation rules,
- department responsibilities,
- communication contracts,
- review gates.

### 2. State Layer

Source:

- `PROGRESS.md`
- `Docs/Workflows/agent_task_ledger.md`
- `Results/agent_runs/`
- `CoAgent/runtime/mosim_agent_runtime.py`

Responsibility:

- durable task queue,
- checkpoints,
- task ownership,
- task-to-visible-conversation lifecycle edges,
- evidence links,
- crash recovery.

Current status:

- present but still early.
- queue/event persistence exists.
- conversation edge graph exists for parent task, department, thread id, role,
  metadata, and open/closed state.
- no full visible-thread orchestration runtime yet.

### 3. Conversation Layer

Primary surfaces:

- WSL-backed VSCode Codex conversation
- Codex App visible project conversations

Rule:

- department work should be represented by real visible project conversations,
- not by pretending an internal short-lived subagent is that department.

Current approved department model:

- `MoSim｜主线总控`
- `MoSim｜调度中台`
- `MoSim｜文档秘书部`
- `MoSim｜研发工程部`
- `MoSim｜验证测试部`
- `MoSim｜安全合规部`
- `MoSim｜DevOps 发布部`

### 4. Worker Layer

Allowed worker types:

- bounded Codex subagents,
- shell commands,
- MCP tools,
- project scripts,
- future department-owned runtimes.

Rule:

- subagents are temporary workers,
- not durable departments.

### 5. Integration Layer

Main integrations:

- MWORKS MCPs
- Unreal / Epic MCPs
- Git
- local scripts
- future Codex conversation dispatch helpers

## Hermes Features We Have Not Fully Absorbed

From `References/Agent/hermes-agent`, the major ideas still not fully migrated
into MoSim are:

1. Durable gateway-style multi-surface conversation routing.
2. Built-in scheduled automation loop.
3. Stronger persistent memory/search model.
4. First-class background/delegation loop instead of ad-hoc task handoff.
5. Structured transport and platform-adapter architecture.
6. Tool and skill registry with runtime loading rules.
7. Native long-lived user-visible session continuity outside one terminal.
8. Shell/tool guardrails, hook model, and session-scoped logging.
9. Doctor/preflight, recovery, and restart resilience.
10. Worktree / parallel-run isolation for long engineering tasks.

## External Architecture Lessons To Track

CoAgent must track lessons from more than one project family:

| Source family | Adoptable questions |
|---|---|
| Anthropic/Claude engineering articles | How to pack context, when to split workers, how to review long-running agents, how to keep safety and observability in the loop |
| Anthropic SDK beta resources | How agents, sessions, threads, memory stores, skills, environments, files, vaults, and webhooks are represented as first-class resources |
| Codex source | How thread stores, rollout traces, app-server boundaries, skills, exec policy, sandboxing, and hooks are separated |
| Hermes | How gateway routing, scheduler, memory manager, skills runtime, shell hooks, doctor/recovery, and UI/runtime split work |
| Agent skills | How compact procedural memory and task-specific context packs are written |
| Multi-agent frameworks | Which role graphs, planner/executor flows, and group-chat patterns are useful or too heavy |
| Workflow runtimes | How WAL, replay, state transitions, specs, and durable execution can reduce chat-memory dependence |

Rejected or deferred ideas must still be recorded when they may be useful for a
future non-MoSim CoAgent deployment.

## Hermes Capability Migration Matrix

CoAgent does not need to copy Hermes literally.
It needs to recreate the useful capability in a MoSim-owned form.

| Hermes capability | Hermes evidence | CoAgent target |
|---|---|---|
| Gateway / multi-surface routing | `gateway/`, `gateway/platforms/`, README messaging/gateway sections | project-owned conversation dispatch and department-thread routing on top of Codex App / WSL Codex |
| Session continuity | README session/history claims, release notes, gateway/session handling | stable visible department/task conversations plus durable task/runtime state |
| Memory layer | README memory, `agent/memory_manager.py`, provider model | project memory and retrieval for directives, decisions, recovery, and reference learning |
| Cron / automation | `cron/jobs.py`, `cron/scheduler.py`, release notes | project-owned recurring automation for docs refresh, git cadence, safety scans, repo update checks |
| Skills runtime | README, `agent/skill_*`, skills directories | project-local skill registry and loading contract around MoSim tasks |
| Tool guardrails / shell hooks | `agent/tool_guardrails.py`, `agent/shell_hooks.py`, security docs | path guard, secret guard, destructive-op guard, large-file guard, hook chain |
| Logging / diagnostics | `hermes_logging.py`, doctor references, release notes | structured CoAgent runtime logs, per-task/event audit trail, recovery diagnostics |
| Parallel work isolation | release notes worktree isolation, subagent delegation | department queue plus Git/work-scope isolation for long-running streams |
| Review / background loop | background review, delegation, subagent helpers | durable reviewer lanes and result-packet loop in project state |
| Desktop / TUI UI | Hermes TUI and desktop | not migrated; Codex App remains frontend |

## CoAgent Build Strategy

We are not building a clone of Hermes Desktop or Hermes TUI.

The target stack is:

```text
Codex App UI
  + WSL Codex execution surface
  + MoSim-owned CoAgent runtime
  + MoSim-owned task queue / result packets / automation / hooks
  + project-owned MCP integrations
```

That means:

- UI is reused,
- runtime is self-built,
- policy is project-owned,
- state is project-owned,
- transport logic is project-owned,
- Hermes is reference only.

## Phase Roadmap

### Phase 0: Foundation

Already in place:

- `CoAgent/` root
- project-wide reference index
- seed runtime
- department operating model
- durable task ledger

### Phase 1: Runtime Core

Must build next:

1. task packet schema,
2. result packet schema,
3. queue claim/checkpoint/complete helpers,
4. status board view,
5. runtime-owned event log contract.

### Phase 2: Conversation Dispatch

Must build after runtime core:

1. visible department conversation registry,
2. dispatch helper for sending task packets,
3. returned result ingestion,
4. stale-conversation and resume checks,
5. conversation lifecycle policy.

### Phase 3: Guardrails and Reliability

Must build after dispatch:

1. file/path hook chain,
2. large-file and Git safety checks,
3. secrets guard,
4. docs consistency checks,
5. restart/recovery tooling,
6. doctor/preflight commands.

Current landed subset:

- `CoAgent/hooks/preflight.py`
  for path boundary, reference-index health, Python compile sanity, and
  tracked-file size preflight.

### Phase 4: Automation

Must build after reliability:

1. recurring docs/workflow optimization,
2. recurring reference-repo refresh checks,
3. recurring safety scans,
4. recurring Git/report reminders,
5. recurring simulation evidence audits.

Current landed subset:

- `CoAgent/automation/automation_tasks.json`
  for recurring automation definitions
- `CoAgent/automation/automation_runner.py`
  for listing due tasks and enqueueing them into runtime state

### Phase 5: Knowledge and Learning

Must build after automation:

1. searchable directive/decision memory,
2. source-to-doc coverage memory,
3. external-repo learning memory,
4. project pattern library,
5. rejection-pattern knowledge base.

Current landed subset:

- `CoAgent/knowledge/knowledge_sources.json`
  for authoritative knowledge-source routing
- `CoAgent/knowledge/knowledge_indexer.py`
  for local index build and keyword search across the core recovery sources

### Phase 2.5: Transport-Aware Dispatch

Current landed subset:

- `CoAgent/dispatch/conversation_registry.py`
  for department-thread lookup
- `CoAgent/dispatch/codex_transport.py`
  for dry-run `codex exec resume` planning against visible department threads

What we already partially absorbed:

1. Department separation.
2. Queue/WAL mindset.
3. Skills as procedural memory.
4. Need for durable state outside chat memory.
5. Need for transport/adaptor separation.

## Codex Features We Should Learn From

From `References/Agent/codex`, the main architecture pieces worth reusing at
the design level are:

1. `app-server`:
   The transport contract behind rich clients.
2. `thread-store`:
   Explicit thread persistence boundary.
3. `rollout` / `rollout-trace`:
   Durable event/history representation.
4. `core-skills`:
   Skills as structured capability bundles.
5. `execpolicy` / sandbox / hooks:
   Safer execution boundary.
6. `agent-graph-store` and thread-oriented primitives:
   Better ownership and dependency tracking.

What not to copy blindly:

- internal Codex storage hacks,
- unsupported private protocol assumptions,
- UI-specific behavior that only works inside official Codex clients.

## Immediate CoAgent Direction

Near-term priority is not building a full replacement frontend.

Near-term priority is:

1. keep Codex App as the visible frontend,
2. keep WSL Codex session as the strongest execution environment,
3. make task and department state durable in project files,
4. make `CoAgent/` the canonical runtime root,
5. index all external references so future learning is cheap,
6. hand-build Hermes-like runtime capabilities in phases instead of relying on hidden subagents.

## What CoAgent Is Not

CoAgent is not:

- a copy of Hermes,
- a copy of Codex,
- a replacement for Codex App UI,
- a fake department naming scheme without runtime support.

It is a controlled architecture layer for building a project-owned agent system
on top of Codex and MCP.
