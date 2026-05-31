# CoAgent Department Capability Model

Date: 2026-05-29

Status: design baseline for portable CoAgent department capabilities. This
document defines capability departments first, then maps them to conversations.
It does not approve automatic conversation creation, app-server transport,
automatic worktree provisioning, email sending, or new runtime surfaces.

## Core Distinction

```text
department = long-lived capability, responsibility boundary, review boundary
conversation = one visible execution surface for a department or task
task team = temporary organization around one durable task
subagent = short-lived bounded helper inside a conversation
```

The old seven-conversation model is now treated as a conservative startup set,
not the target architecture. A portable CoAgent system needs a richer
department capability model so it can be moved to projects beyond MoSim.

## Design Criteria

A department exists when the capability has at least one of these properties:

1. recurring work across many tasks;
2. high state load or long memory requirement;
3. independent review or risk-control boundary;
4. platform capability used by many task teams;
5. high cognitive load if merged into another department;
6. direct impact on user experience or intervention quality;
7. long-term evolution responsibility.

A department should not automatically become a permanent conversation. The
conversation mapping is decided separately.

## Capability Departments

### 1. Strategic PMO / User Interface

Owns user alignment, priorities, final acceptance, route changes, and integrated
reporting.

Must not own hidden worker queues, Git execution, or detailed implementation.

### 2. Dispatch Center / Task Operations

Owns task tickets, state board, owner assignment, topology selection,
dependency tracking, result-packet intake, blocker routing, and closeout state.

Must not implement product features.

### 3. Product Discovery / Strategy Deployment

Owns working-backwards problem framing, project-poster style discovery,
breakthrough objectives, strategy deployment, portfolio fit, and whether a
candidate task is worth doing.

This department prevents the PMO from becoming overloaded with both user
interface and long-horizon product strategy.

### 4. Architecture And Standards

Owns high-impact architecture decisions, department boundaries, protocol
schemas, context-pack formats, and the decision whether a repeated lesson
becomes a skill, hook, runtime feature, MCP, checklist, or documentation.

This department prevents architecture decisions from being buried in normal
implementation threads.

### 5. Agent Runtime Platform

Owns conversation creation strategy, session/thread/rollout state, transport,
app-server/CLI/VSCode/Codex App integration, subagent boundaries, and durable
conversation lifecycle.

This department is necessary because CoAgent infrastructure cannot be treated as
ordinary product implementation.

### 6. Context / Memory / Indexing

Owns context packs, memory retrieval, knowledge indexes, context compression,
new-conversation startup packets, stale-context detection, and context pollution
prevention.

Multi-conversation work cannot scale without this department.

### 7. Toolchain / MCP Integration

Owns MCP servers, wrappers, capability cards, tool health probes, tool fallback
routes, and integration with UE, MWORKS, Git, browser, filesystem, or future
tools.

This department is separate from runtime: runtime moves messages; toolchain
makes external tools usable and safe.

### 8. Automation / Workflow Engine

Owns scheduled tasks, recurring checks, workflow DAGs, retries, circuit
breakers, dry-run automation, and automatic task generation proposals.

It does not bypass PMO/Dispatch review gates.

### 9. Domain Engineering

Owns project-specific implementation and technical investigation. In MoSim this
can instantiate sub-capabilities such as simulation platform, UE scene truth,
control/navigation algorithms, and product UI.

This department is configurable for each project.

### 10. Applied Research / Methods

Owns task-driven research: papers, open-source comparisons, method selection,
algorithm feasibility, and route recommendations for a concrete task.

It is not responsible for general self-improvement research.

### 11. External Intelligence / Self-Evolution

Owns ongoing learning from model-vendor engineering articles, new Codex/Claude/
Kimi/Qwen/OpenAI/Anthropic releases, high-quality GitHub agent projects, and
large-company project-management practices.

It proposes CoAgent improvements and records portable lessons. It is a
long-term evolution function, not a one-off research task.

### 12. Knowledge Secretary / Documentation

Owns decision records, user-instruction capture, docs consistency, indexes,
stable knowledge promotion, and reusable workflow documentation.

It records and promotes confirmed knowledge. It does not discover every new
external idea by itself.

### 13. Verification / Evaluation

Owns unit tests, integration tests, simulation evidence, reproducibility,
benchmarks, regression checks, and independent acceptance evidence.

It must remain independent from the feature implementation being evaluated.

### 14. Observability / Evidence

Owns traces, logs, result packets, evidence bundles, metrics surfaces,
dashboarding, and proof that a task actually progressed.

This is separate from Verification: Verification judges correctness;
Observability makes the work inspectable and recoverable.

### 15. Flow Analytics / Operating Metrics

Owns lead time, blocked time, failed handoff rate, review escape rate, rework
count, recovery time, WIP limits, context-pack freshness/size metrics, and
agent-drift or repeated-failure indicators.

This department measures how the CoAgent organization itself is performing. It
is separate from Observability: Observability records task evidence; Flow
Analytics analyzes organization health.

### 16. Safety / Compliance

Owns path boundaries, credentials, account material, destructive actions,
third-party license risk, prompt/tool injection risk, and notification-security
rules.

This is a hard-control department.

### 17. Reliability / Incident Response

Owns crashes, repeated tool failures, GUI hangs, Git index locks, session-state
corruption, activation loss, incident packets, recovery plans, and postmortems.

This is separate from Safety: Safety prevents unsafe actions; Reliability keeps
the operating system stable.

### 18. Continuous Improvement / Retrospective Closure

Owns after-action reviews, incident postmortems, repeat-failure closure,
retrospective action tracking, and promotion of repeated lessons into skills,
hooks, tests, doctor checks, workflows, or documentation tasks.

This is separate from Reliability: Reliability handles incidents; Continuous
Improvement ensures the system changes after incidents and repeated mistakes.

### 19. DevOps / Git / Release

Owns Git state, worktrees, staging, commits, LFS/ignore, merge strategy,
release packaging, rollback, and broad rename/import hygiene.

This remains separate because Git is high-state and high-risk.

### 20. Operator Experience / Human Intervention

Owns human-intervention UX, blocker notification templates, email/desktop
notification design, manual-action recovery instructions, dedupe/rate limits,
and preventing many agents from asking the user the same thing.

This department turns blocked automation into clear operator action.

## Conversation Mapping

Conversation count is a runtime decision, not the department count.

### Required Permanent Conversations For Portable CoAgent

These should normally be permanent visible conversations:

| Conversation | Capability Departments Represented |
|---|---|
| `CoAgent｜PMO` | Strategic PMO / User Interface |
| `CoAgent｜Dispatch` | Dispatch Center / Task Operations |
| `CoAgent｜Product Strategy` | Product Discovery / Strategy Deployment |
| `CoAgent｜Runtime Platform` | Agent Runtime Platform |
| `CoAgent｜Context Memory` | Context / Memory / Indexing |
| `CoAgent｜Toolchain MCP` | Toolchain / MCP Integration |
| `CoAgent｜Knowledge Secretary` | Knowledge Secretary / Documentation |
| `CoAgent｜Verification` | Verification / Evaluation |
| `CoAgent｜Safety Compliance` | Safety / Compliance |
| `CoAgent｜DevOps Release` | DevOps / Git / Release |
| `CoAgent｜External Intelligence` | External Intelligence / Self-Evolution |

### Conditional Permanent Conversations

These become permanent when project load justifies them:

| Conversation | Trigger |
|---|---|
| `CoAgent｜Architecture Standards` | frequent high-impact protocol/runtime/department decisions |
| `CoAgent｜Observability Evidence` | frequent long-running tasks or weak evidence traceability |
| `CoAgent｜Flow Analytics` | repeated need to optimize handoffs, WIP, blocked time, context quality, or rework |
| `CoAgent｜Reliability Incident` | repeated MCP/App/GUI/Git/runtime failures |
| `CoAgent｜Continuous Improvement` | repeated postmortem actions or process-learning debt |
| `CoAgent｜Operator Experience` | frequent manual intervention, notifications, or human-review flows |
| `CoAgent｜Domain Engineering` | one project has sustained implementation load |
| `CoAgent｜Applied Research` | project repeatedly needs papers/open-source/method comparison |

### Task-Scoped Conversations

Task-scoped conversations are created for high-context temporary work:

- PX4 parameter-identification task;
- UE scene-truth export task;
- FastLIO integration task;
- architecture review task;
- incident postmortem task;
- benchmark/evaluation campaign;
- product UI implementation slice.

They close after result packet import, review, and knowledge promotion.

## MoSim-Specific Initial Mapping

For MoSim, the recommended next mapping is:

### Permanent Now

1. `MoSim｜主线 PMO`
2. `MoSim｜调度中台`
3. `MoSim｜产品发现战略`
4. `MoSim｜Agent Runtime 平台`
5. `MoSim｜上下文记忆索引`
6. `MoSim｜工具链 MCP`
7. `MoSim｜知识秘书`
8. `MoSim｜验证评测`
9. `MoSim｜安全合规`
10. `MoSim｜DevOps 发布`
11. `MoSim｜外部情报进化`

### Conditional For MoSim

These should be promoted to permanent only when their queue pressure becomes
real and repeated:

1. `MoSim｜仿真平台`
2. `MoSim｜UE 场景真值`
3. `MoSim｜控制导航算法`
4. `MoSim｜观测证据`
5. `MoSim｜组织运行指标`
6. `MoSim｜可靠性事故`
7. `MoSim｜持续改进复盘`
8. `MoSim｜操作者体验`
9. `MoSim｜应用研究方法`
10. `MoSim｜架构标准`

### Still Task-Scoped

- `MoSim｜专项｜PX4 参数识别`
- `MoSim｜专项｜Derelict 场景真值`
- `MoSim｜专项｜FastLIO 接入`
- `MoSim｜专项｜RflySim UI`
- `MoSim｜专项｜事故复盘`
- `MoSim｜专项｜架构评审`

## Promotion And Demotion Rules

Promote a capability to a permanent conversation when at least two are true:

- it appears in three or more durable tasks;
- it carries state that is hard to reconstruct from packets;
- it has independent review or safety authority;
- its work repeatedly blocks other departments;
- context mixing causes repeated misunderstanding;
- it owns platform capability used by multiple task teams.

Demote or merge a permanent conversation when:

- it has no task ownership for a sustained period;
- all outputs are simple documentation notes;
- it duplicates another department's authority;
- coordination overhead is greater than saved context load.

## Anti-Patterns

- Treating department count as conversation count.
- Treating a user-visible conversation as project truth without task packets.
- Creating a permanent department for one task.
- Hiding long-running work inside a short-lived subagent.
- Letting PMO, Dispatch, and Runtime Platform collapse into one conversation.
- Letting PMO also own long-horizon product discovery and strategy deployment.
- Letting Knowledge Secretary become both external researcher and task-state
  owner.
- Letting Observability evidence and Flow Analytics become one confused metrics
  bucket.
- Treating incident handling as sufficient without postmortem action tracking.
- Letting Verification implement the feature under test.
- Letting Safety and Reliability be the same function.

## Open Design Questions

- Which of the conditional MoSim conversations should be created before the
  first real multi-conversation proof?
- Should `Architecture Standards` be permanent immediately, or can Dispatch own
  architecture routing until queue pressure appears?
- Should `Observability Evidence` be merged with Verification initially, or
  split now because evidence quality is central to long tasks?
- Should `Flow Analytics` and `Continuous Improvement` remain conditional until
  several real task lifecycles exist, or should they be permanent from the
  first multi-conversation proof?
- What is the smallest useful Runtime Platform conversation proof that does not
  require app-server transport?
