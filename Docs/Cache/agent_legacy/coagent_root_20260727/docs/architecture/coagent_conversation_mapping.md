# CoAgent Conversation Mapping

Date: 2026-05-29

Status: recommended visible-conversation mapping for the 20-department
capability model. This document does not create conversations, mutate Codex App
state, or approve automatic conversation creation.

## Purpose

`coagent_department_capability_model.md` defines 20 capability departments. This
document maps those departments onto actual Codex-visible conversations.

Core rule:

```text
department capability count != permanent conversation count
```

The mapping must balance:

- cognitive load reduction,
- durable state ownership,
- independent review boundaries,
- coordination cost,
- current Codex App / VSCode / CLI session instability,
- the need to prove one minimal multi-conversation loop before scaling.

## Mapping Decision

For the next CoAgent phase, use this deployment model:

```text
11 required permanent conversations
6 conditional permanent conversations
task-scoped conversations for high-context temporary work
3 capabilities initially hosted by existing conversations
```

This supersedes the historical seven-conversation startup baseline.

## Required Permanent Conversations

These should be created as visible conversations before the first serious
multi-conversation CoAgent proof.

| # | Conversation | Primary capabilities | Why permanent |
|---|---|---|---|
| 1 | `MoSim｜主线 PMO` | Strategic PMO / User Interface | The user-facing authority and final integration lane must stay stable. |
| 2 | `MoSim｜调度中台` | Dispatch Center / Task Operations | Task state, topology, routing, and result intake need a durable control lane. |
| 3 | `MoSim｜产品发现战略` | Product Discovery / Strategy Deployment | Prevents PMO from carrying long-horizon product strategy and value filtering. |
| 4 | `MoSim｜Agent Runtime 平台` | Agent Runtime Platform | Conversation/session/transport work is core infrastructure, not ordinary development. |
| 5 | `MoSim｜上下文记忆索引` | Context / Memory / Indexing | Multi-conversation work depends on curated context and retrieval quality. |
| 6 | `MoSim｜工具链 MCP` | Toolchain / MCP Integration | MCP/tool health and capability cards repeatedly block MoSim execution. |
| 7 | `MoSim｜知识秘书` | Knowledge Secretary / Documentation | User decisions, docs, indexes, and knowledge promotion need a stable lane. |
| 8 | `MoSim｜验证评测` | Verification / Evaluation | Independent evidence and reproducibility must not be owned by implementers. |
| 9 | `MoSim｜安全合规` | Safety / Compliance | Path, secret, license, destructive-action, and third-party gates are hard boundaries. |
| 10 | `MoSim｜DevOps 发布` | DevOps / Git / Release | Git/worktree/release state is high-risk and state-heavy. |
| 11 | `MoSim｜外部情报进化` | External Intelligence / Self-Evolution | CoAgent must continuously absorb model-vendor articles, open-source agent projects, and management lessons. |

## Conditional Permanent Conversations

These are real capability departments, but should become permanent visible
conversations only after repeated queue pressure or a major task proves the
need.

| Conversation | Host before promotion | Promotion trigger |
|---|---|---|
| `MoSim｜架构标准` | `MoSim｜调度中台` + `MoSim｜Agent Runtime 平台` | repeated high-impact protocol/runtime/department decisions |
| `MoSim｜观测证据` | `MoSim｜验证评测` | repeated long-running tasks need trace/evidence bundles separate from correctness review |
| `MoSim｜组织运行指标` | `MoSim｜调度中台` | repeated need to optimize WIP, blocked time, handoff failure, context freshness, or rework |
| `MoSim｜可靠性事故` | `MoSim｜工具链 MCP` + `MoSim｜安全合规` | repeated MCP/App/GUI/Git/runtime failures or recurring incidents |
| `MoSim｜持续改进复盘` | `MoSim｜知识秘书` | repeated postmortems produce unclosed skill/hook/test/doc actions |
| `MoSim｜操作者体验` | `MoSim｜主线 PMO` + `MoSim｜安全合规` | frequent manual intervention, email/desktop notification, or user-review bottlenecks |

## Hosted Capabilities At Startup

These capability departments exist, but do not need their own visible
conversation for the first proof.

| Capability | Startup host | Reason |
|---|---|---|
| Architecture And Standards | Dispatch + Runtime Platform | Architecture work is active, but not enough yet to justify another always-on lane. |
| Automation / Workflow Engine | Dispatch Center | Scheduled automation is gated; keep planning under Dispatch until approved. |
| Applied Research / Methods | External Intelligence for general research; task-scoped conversation for task-specific research | Research should be problem-driven; do not create an idle generic research lane. |

## Domain Engineering Mapping For MoSim

`Domain Engineering` is project-specific. For MoSim it has three major product
streams:

| Product stream | Startup mapping | Promotion trigger |
|---|---|---|
| `MoSim｜仿真平台` | task-scoped or hosted by `MoSim｜工具链 MCP` / `MoSim｜验证评测` | repeated MWORKS/Syslab/Sysplorer simulation-platform tasks |
| `MoSim｜UE 场景真值` | task-scoped under scene tasks | repeated UE/Fab/map-truth work blocks product progress |
| `MoSim｜控制导航算法` | task-scoped under algorithm tasks | repeated PX4/FastLIO/planning/control tasks need persistent technical memory |

Do not create these three as permanent conversations until the first
multi-conversation proof shows where the real load lands.

## Task-Scoped Conversation Rules

Create a task-scoped conversation when all are true:

- the task has a `task_id`;
- the task has a canonical goal and parent department;
- the work is high-context or long-running;
- a context pack exists;
- a stop condition and result-packet path exist;
- Dispatch records the conversation edge;
- the conversation can close after result import and review.

Default naming:

```text
MoSim｜专项｜<task-name>
```

Examples:

- `MoSim｜专项｜PX4 参数识别`
- `MoSim｜专项｜Derelict 场景真值`
- `MoSim｜专项｜FastLIO 接入`
- `MoSim｜专项｜RflySim UI`
- `MoSim｜专项｜事故复盘`
- `MoSim｜专项｜架构评审`

## First Minimal Closed-Loop Test Topology

The first proof should not use all 11 permanent conversations. Use the smallest
loop that proves real multi-conversation behavior:

```text
主线 PMO
  -> 调度中台
  -> Agent Runtime 平台
  -> 上下文记忆索引
  -> 验证评测
  -> DevOps 发布
  -> 知识秘书
```

Optional, depending on test content:

```text
工具链 MCP
安全合规
```

Do not include Product Strategy or External Intelligence in the first
communication proof unless the proof task explicitly needs route/value
assessment or external-source learning.

## Message Ownership

| Message type | Owner conversation |
|---|---|
| user-facing ask | `MoSim｜主线 PMO` |
| task packet | `MoSim｜调度中台` |
| context pack | `MoSim｜上下文记忆索引` |
| conversation/session probe | `MoSim｜Agent Runtime 平台` |
| MCP/tool capability proof | `MoSim｜工具链 MCP` |
| test/evidence review | `MoSim｜验证评测` |
| safety/blocker review | `MoSim｜安全合规` |
| Git/worktree integration | `MoSim｜DevOps 发布` |
| durable lesson promotion | `MoSim｜知识秘书` |
| strategy/value review | `MoSim｜产品发现战略` |
| vendor/open-source learning | `MoSim｜外部情报进化` |

## Current Registry Gap

Current `CoAgent/dispatch/department_threads.json` still lists the historical
seven startup conversations:

```text
MainAgent
DispatchCenter
TaskSecretary
ProjectOwner
TestOwner
SecurityOfficer
GitIntegrator
```

Before creating or registering the 11-conversation mapping, the Runtime
Platform lane should run a session-state visibility proof and update the
registry only with conversations that are visible in the selected primary
surface.

## Anti-Patterns

- Creating all 20 departments as permanent conversations immediately.
- Continuing with only the historical seven conversations after adopting the
  20-department model.
- Creating task-specific permanent departments such as "PX4" or "Derelict".
- Letting `MoSim｜研发工程部` absorb Runtime, Context, MCP, Product Strategy, and
  External Intelligence.
- Letting `MoSim｜调度中台` become the hidden implementer.
- Treating Codex App sidebar visibility as durable state.

## Next Decision

The next decision is not "should CoAgent have 20 conversations?".

The concrete agent contracts for the 11 required permanent conversations are
defined in `CoAgent/docs/architecture/coagent_concrete_agent_design.md`.

The next decision is:

```text
Create/register the 11 required permanent conversations,
then prove one minimal closed-loop task across 6-7 of them.
```

If the proof shows that 11 is too many, demote a lane. If it shows that a
conditional department repeatedly blocks work, promote that lane.
