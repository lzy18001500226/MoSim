# CoAgent Vendor And Framework Pattern Mapping

Date: 2026-05-28

Status: design synthesis from existing audits. This is not a new broad
research pass and does not approve runtime, transport, automation, schema
migration, or automatic worktree/conversation creation.

Task id: `COAGENT-DESIGN-11`

## Purpose

This document consolidates existing CoAgent learning records into one mapping
from external multi-agent designs to CoAgent architecture objects.

It answers:

- what each vendor/framework pattern actually solves,
- which CoAgent object should absorb the idea,
- what must be rejected or deferred,
- which evidence is already strong,
- which source families still need a targeted follow-up audit.

It does not repeat the original research. Source details remain in the audit
records listed below.

## Source Evidence

Primary existing records:

- `CoAgent/learning/audits/2026-05-27_official_multi_agent_principles_round8.md`
- `CoAgent/learning/audits/2026-05-27_official_protocol_convergence_round11.md`
- `CoAgent/learning/audits/2026-05-27_multi_agent_frameworks_round4.md`
- `CoAgent/learning/audits/2026-05-27_hermes_codex_runtime_boundaries_round2.md`
- `CoAgent/learning/audits/2026-05-27_local_runtime_architecture_round9.md`
- `CoAgent/learning/audits/2026-05-27_workflow_runtimes_round6.md`
- `CoAgent/docs/research/THREE_ROUND_STUDY_AND_DISCUSSION.md`
- `CoAgent/docs/architecture/local_runtime_design_matrix.md`
- `CoAgent/docs/research/multi_agent_learning_urls.md`

Evidence levels used in this document:

| Level | Meaning |
|---|---|
| `audited` | Covered by a local audit with adopt/adapt/reject outcomes |
| `partially_audited` | Mentioned in an audit or local corpus, but not deeply mapped |
| `seed_only` | Present in URL/source index, but not yet converted into an audit |

## Architecture Object Vocabulary

External patterns should map into these CoAgent objects, not into arbitrary new
departments.

| CoAgent object | Meaning |
|---|---|
| `WorkflowAuthority` | Deterministic owner of task state, routing, cancellation, review, and recovery |
| `CanonicalTask` | Durable unit with one official goal, state, evidence, and acceptance path |
| `TaskTeam` | Temporary multi-conversation execution container for one long objective |
| `ScopedConversation` | Visible working conversation for one slice inside a task team |
| `SubagentSlice` | Disposable bounded worker inside a scoped conversation |
| `ContextPack` | Filtered startup context for a worker/conversation |
| `SharedContextDelta` | Compact update that changes team-level shared context |
| `Artifact` | File/output/evidence independent of chat prose |
| `ReviewGate` | Human or automated acceptance/rejection transition |
| `WorktreeSurface` | File/Git isolation surface for task, review, integration, or ephemeral work |
| `EventLog` | Append-only history from which status can be rebuilt |
| `Skill` | Selectively loaded procedure |
| `Hook` | Deterministic lifecycle/policy gate |
| `ToolSurface` | MCP, shell, API, or hosted tool callable by an authorized owner |
| `CapabilityCard` | Future description of what a lane/agent can safely do |

## Pattern Mapping

| Source | Evidence | Core pattern | Adopt into CoAgent | Defer / reject |
|---|---|---|---|---|
| Anthropic multi-agent research + context/harness articles | audited | Orchestrator-workers, parallel exploration, context engineering, artifact outputs, evaluator/reviewer loops, long-horizon harness | `TaskTeam`, `SubagentSlice`, `ContextPack`, `Artifact`, `ReviewGate`, `EventLog` | Do not use parallelism for tightly coupled coding without aggregation and review |
| Claude Code subagents/hooks/skills | audited | Subagents have isolated context; hooks enforce lifecycle; skills are selectively loaded procedures | `SubagentSlice`, `Hook`, `Skill`, context budget rules | Do not make skills enforce hard safety policy; do not treat subagents as durable workers |
| OpenAI Agents SDK | audited | `agents-as-tools` manager pattern vs `handoffs` control transfer, handoff input filters, lifecycle hooks | `HandoffMode`, `ContextPack` as input filter, `WorkflowAuthority`, `CapabilityCard` later | Do not forward raw conversations as handoff payloads |
| OpenAI Codex source/app-server | audited | Threads, turns, items, goals, rollout traces, MCP/skill/hook surfaces, parent-child thread graph | `ScopedConversation`, `EventLog`, `ToolSurface`, `conversation_edges` | Do not depend on private App session files as source of truth |
| A2A protocol | audited | Distinguishes messages from tasks, task states, artifacts, history, cancellation, streaming, auth/input-required | `CanonicalTask`, task states, `Artifact`, future A2A-compatible mapping | Full wire-protocol compatibility deferred |
| Google ADK | audited in official pass; not deeply local | Sequential/parallel/loop/custom workflows and multi-agent composition | `WorkflowGraph` pattern selector, `TaskTeam` topology templates | Do not import ADK runtime now; needs deeper mapping before implementation |
| Microsoft Semantic Kernel | audited in official pass; not deeply local | Sequential, concurrent, group-chat, handoff, Magentic-style orchestration | `TopologySelector`: sequential, parallel, handoff, review-board, manager-worker | Free-form group chat is rejected as default |
| LangGraph | audited | State graph, checkpoints, interrupts, pending writes, durable execution | `EventLog`, future checkpoint/replay, human interrupt states | Do not import graph runtime before CoAgent schema stabilizes |
| CrewAI / LlamaAgents / AutoGen / AG2 / MetaGPT / CAMEL | audited | Crew/flow split, role teams, worker placement, group chat, role SOPs | role/team lessons only when tied to packets, review, state, capability routing | Reject role names as proof of capability; reject unmanaged peer chat |
| Temporal / OpenSpec / TaskWeaver / OKWinds | audited | Durable history plus mutable state, spec/action workflows, plugin boundaries, documentation packs | workflow history, task bootstrap, plugin/tool contract, proof-of-completion checklist | Full workflow engine deferred |
| Hermes | audited | Gateway/runtime split, context engine, memory manager, scheduler, hooks, guardrails, provider adapters | `WorkflowAuthority`, context lifecycle, memory provider, automation guardrails, doctor/recovery | Do not import Hermes UI/runtime wholesale |
| OpenClaw | audited | Gateway, lanes, session/workspace, standing orders, task flow, hooks, context engine, security posture | explicit lanes, task flow, context engine, standing-order concepts later, security boundary docs | Do not copy social-channel gateway or one-user trusted model as security boundary |
| Qwen-Agent / Qwen Code | seed_only or partial local reference | Assistant/GroupChat/nested agents, MCP/RAG/context management, Agent Arena multi-worktree comparison | candidate for `WorktreeSurface` arena pattern and nested-agent context rules | Needs targeted audit before adoption |
| Kimi / Moonshot + Hermes/OpenClaw integration | seed_only | Model/tool-call provider plus Hermes/OpenClaw adapter guidance | provider/runtime adapter lessons, tool-call compatibility, model portability checks | Needs targeted audit before architecture claims beyond provider adapter |
| Mistral Agents | seed_only | Agent capability definition separated from conversation history; conversations/entries; handoffs | `CapabilityTemplate` vs `ConversationState` separation | Needs targeted audit before adoption |
| MCP | seed_only but heavily used locally | Tool/context interoperability boundary | `ToolSurface` with explicit ownership and review | MCP is capability, not authority |

## Missing CoAgent Abstractions

Existing CoAgent design already has packets, context packs, event logs,
review gates, task teams, and worktree vocabulary. The mapping above shows
these missing or under-specified abstractions:

### 1. Handoff Mode Selector

External basis:

- OpenAI Agents SDK: manager `agents-as-tools` vs handoffs.
- Semantic Kernel: sequential/concurrent/group/handoff/Magentic.
- ADK: workflow composition patterns.

CoAgent needs a selector:

```text
direct_main
department_lane
task_team
manager_calls_subagents
handoff_to_scoped_conversation
parallel_slices_with_integration
review_board
arena_comparison
```

Selection must depend on coupling, risk, context size, artifact boundaries,
review needs, and worktree isolation.

### 2. Workflow Graph

External basis:

- Google ADK workflows,
- LangGraph state graphs,
- Temporal event histories,
- OpenSpec action workflows.

CoAgent currently has task packets and conversation edges, but not a formal
workflow graph that can express:

```text
deterministic node
agent node
review node
tool/MCP node
artifact node
human interrupt node
merge/release node
```

This should be designed before large multi-conversation automation.

### 3. Capability Template vs Conversation State

External basis:

- Mistral Agents separates agent definition from conversations.
- Codex source separates thread/state surfaces from skills/MCP/settings.
- A2A uses agent cards plus task/message artifacts.

CoAgent currently blurs visible thread, department role, capability, and state.
It needs:

```text
CapabilityTemplate:
  tools allowed
  skills allowed
  policies/hooks
  typical tasks
  forbidden actions

ConversationState:
  current task slice
  context pack
  local worktree
  checkpoints
  result packets
```

### 4. Worktree Arena / Comparative Execution

External basis:

- Qwen Code Agent Arena is a relevant seed pattern.
- Existing user requirement: conversation or subagent may need its own
  worktree.

CoAgent needs a rule for two cases:

```text
parallel complementary slices:
  different conversations edit different scopes

competitive/comparative slices:
  multiple agents attempt the same bounded problem in isolated worktrees
  reviewer selects or merges the best result
```

This must be gated because arena-style execution multiplies Git/review cost.

### 5. Shared Context Delta

External basis:

- Anthropic context engineering,
- Hermes context lifecycle,
- LangGraph checkpoints,
- OpenAI handoff input filtering.

CoAgent has context packs, but task teams need an update channel:

```text
slice result
  -> shared context delta
  -> affected slice context refresh
```

Without this, task-team conversations will either drift or copy too much raw
chat.

### 6. Evaluation / Trace Rubric

External basis:

- Anthropic multi-agent evals,
- OpenAI tracing/lifecycle ideas,
- LangSmith/promptfoo/OpenAI evals in URL seed list,
- framework audits on result quality.

CoAgent should evaluate not only final output but:

```text
scope discipline
evidence quality
context budget
tool economy
handoff clarity
review readiness
recovery readiness
policy compliance
```

## Recommended Synthesis

CoAgent should integrate the strongest parts as follows:

```text
Anthropic:
  use orchestrator-worker only when decomposition is real;
  treat context and evals as first-class engineering surfaces.

OpenAI:
  use explicit handoff modes and input filters;
  keep manager/tool-style delegation separate from control-transfer handoffs.

Google ADK / Semantic Kernel:
  add topology selection and workflow graph vocabulary;
  do not make every task a free-form team discussion.

A2A / LangGraph / Temporal:
  make tasks, artifacts, state, history, interruption, and replay explicit;
  keep readable local packets before protocol/framework import.

Codex / Hermes / OpenClaw:
  separate UI, runtime, session state, context, hooks, skills, memory, and
  tool surfaces;
  keep project-owned state recoverable.

Qwen / Mistral / Kimi:
  treat as targeted follow-up sources:
  Qwen for worktree arena and nested agent patterns;
  Mistral for agent-definition vs conversation-state separation;
  Kimi for provider/tool-call/runtime-adapter portability.
```

## What CoAgent Should Not Do

- Do not import a full framework as the coordination core.
- Do not make current seven visible threads the architecture boundary.
- Do not use peer-to-peer group chat as default coordination.
- Do not treat model provider docs as a workflow runtime.
- Do not create worktrees automatically without owner, review, merge, and
  closeout contracts.
- Do not let subagents own durable task state.
- Do not load all skills or all memory into a task context.

## Gap Audit

| Gap | Evidence status | Priority | Reason |
|---|---|---:|---|
| Handoff mode selector | supported by OpenAI/SK/ADK audits | high | Needed before reliable multi-conversation task dispatch |
| Workflow graph model | supported by ADK/LangGraph/Temporal audits | high | Needed to express deterministic, agent, review, and merge nodes |
| Capability template vs conversation state | seed from Mistral/Codex/A2A | high | Prevents role/thread/state confusion |
| Shared context delta | supported by Anthropic/Hermes/LangGraph audits | high | Required for task-team context synchronization |
| Worktree arena | Qwen seed only | medium | Useful but costly; needs targeted audit before adoption |
| Provider portability via Kimi/Moonshot | seed only | medium | Useful for future model/provider routing, not immediate architecture |
| Eval/trace rubric | partially audited | medium | Needed before unattended or large parallel work |
| Full A2A compatibility | audited but deferred | low | Portable future option, not needed for local MoSim V1 |

## Next Design Step

Use this mapping to write the true CoAgent operating architecture:

```text
CoAgent/learning/coagent_operating_architecture_v1.md
```

That document should define:

1. task lifecycle,
2. workflow graph and topology selection,
3. task-team lifecycle,
4. shared-context and slice-context lifecycle,
5. worktree/review/merge lifecycle,
6. capability template vs conversation state,
7. evaluation and retrospective loop.

Only after that should runtime or transport changes be considered.
