# CoAgent Vendor Gap Review

Date: 2026-05-29

Status: design review after re-checking existing vendor/framework audits and
spot-checking current first-party documentation. This does not approve runtime,
transport, automatic conversation creation, automatic worktree creation,
email sending, or new permanent conversations.

## Sources Rechecked

Local synthesis:

- `CoAgent/docs/architecture/coagent_vendor_pattern_mapping.md`
- `CoAgent/learning/audits/2026-05-27_official_multi_agent_principles_round8.md`
- `CoAgent/learning/audits/2026-05-27_official_protocol_convergence_round11.md`
- `CoAgent/learning/audits/2026-05-27_local_runtime_architecture_round9.md`
- `CoAgent/learning/audits/2026-05-27_multi_agent_frameworks_round4.md`
- `CoAgent/docs/research/THREE_ROUND_STUDY_AND_DISCUSSION.md`

Current external spot-checks:

- Anthropic, "How we built our multi-agent research system",
  `https://www.anthropic.com/engineering/multi-agent-research-system`.
- OpenAI Agents SDK, handoffs and Agents SDK overview,
  `https://openai.github.io/openai-agents-python/handoffs/`,
  `https://developers.openai.com/api/docs/guides/agents`.
- Google ADK workflow agents,
  `https://adk.dev/agents/workflow-agents/`.
- Microsoft Semantic Kernel Agent Orchestration,
  `https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/`.
- Qwen-Agent repository,
  `https://github.com/QwenLM/Qwen-Agent`.
- Kimi API docs and official tools,
  `https://platform.kimi.ai/docs/api/overview`,
  `https://platform.moonshot.ai/docs/guide/use-official-tools`.

## Current Design Strengths

The current 11-agent design is directionally correct.

| Current CoAgent choice | External pattern it matches | Keep |
|---|---|---|
| PMO + Dispatch as authority, workers as execution surfaces | Anthropic lead agent, OpenAI owner/handoff distinction, A2A task state | yes |
| Context packs instead of raw transcript forwarding | Anthropic context engineering, OpenAI handoff input filters, Hermes context lifecycle | yes |
| Task-scoped conversations for long work, disposable subagents for bounded slices | Anthropic subagent parallel research, Claude Code subagents, task-team frameworks | yes |
| Packet-first communication and result evidence | A2A artifacts, LangGraph/Temporal persistence, OpenAI results/state | yes |
| Explicit safety, DevOps, verification gates | OpenAI guardrails/human review, enterprise release and SRE practice | yes |
| No default peer group chat | Semantic Kernel group chat exists but is not safe as default for engineering tasks | yes |
| Provider-specific systems treated as adapters, not architecture authority | Qwen/Kimi docs focus on tools, function calling, provider compatibility | yes |

## Optimization Gaps

### 1. Handoff Mode Selector Is Still Too Informal

External basis:

- OpenAI distinguishes manager-style specialist use from real handoff/control
  transfer.
- Semantic Kernel explicitly lists concurrent, sequential, handoff, group chat,
  and Magentic-style patterns.
- ADK separates deterministic workflow agents from graph/dynamic workflows.

Current gap:

`coagent_solution_synthesis.md` lists topology names, but there is no typed
handoff-mode packet. Dispatch can still choose a route in prose, which is
where ambiguity enters.

Design fix:

Add a `handoff_mode` template with:

```text
mode
from_owner
to_owner
authority_transfer
input_filter
context_pack
expected_result
review_gate
return_path
cancellation_or_resume_rule
```

### 2. Capability Template And Conversation State Need Separation

External basis:

- OpenAI separates agent definitions, running agents, tools, guardrails,
  results/state, and tracing.
- Mistral-style agent APIs and A2A-style agent cards separate capability from
  task/conversation state.
- Qwen-Agent separates LLMs, tools, and higher-level agents.

Current gap:

`agent_profile.yaml` mixes durable capability, current state, tool policy, and
conversation behavior. This is acceptable for design, but not enough for stable
runtime or routing.

Design fix:

Keep `AgentProfile` as the human-readable contract, but split the machine model
later:

```text
CapabilityTemplate:
  tools, skills, hooks, safety policy, supported task classes

ConversationState:
  active task, context pack, local state, worktree, checkpoints
```

### 3. Workflow Graph Is Missing As A First-Class Object

External basis:

- ADK 2.0 emphasizes graph-based and dynamic workflows.
- LangGraph and Temporal show why replayable state graphs matter.
- Semantic Kernel makes orchestration pattern selection explicit.

Current gap:

We have task lifecycle, conversation edges, and topology names, but no compact
workflow graph schema for one task.

Design fix:

Add a workflow graph model before automating large task teams:

```text
node: deterministic | agent | tool | review | artifact | human_interrupt | merge
edge: depends_on | handoff | parallel_join | review_gate | resume_after
state: pending | running | blocked | review_required | completed | cancelled
```

### 4. Shared Context Delta Needs A Concrete Packet

External basis:

- Anthropic and Hermes both treat context as a lifecycle, not a static prompt.
- OpenAI handoff input filters imply a fresh, filtered handoff payload.
- LangGraph-style checkpoints preserve resumable state snapshots.

Current gap:

Context packs exist, and the Context Memory Agent produces `context_delta`, but
there is no template. That means multi-conversation task teams may drift or
copy raw chat.

Design fix:

Add `context_delta.yaml` and require Context Memory to convert accepted result
packets into compact updates for affected conversations.

### 5. Artifact Registry Is Under-Specified

External basis:

- A2A treats artifacts as task outputs separate from messages.
- OpenAI Agents SDK has results/state and observability surfaces.
- ADK docs have explicit artifacts, sessions, memory, and events sections.

Current gap:

Result packets carry evidence paths, but artifacts themselves do not yet have a
stable manifest with provenance, type, review state, and lifecycle.

Design fix:

Add `artifact_manifest.yaml` for evidence outputs such as result packets,
figures, logs, scene truth exports, simulation outputs, screenshots, and
worktree diffs.

### 6. Trace And Evaluation Rubric Is Too Weak For Multi-Agent Work

External basis:

- Anthropic emphasizes evaluation and checkpointing for multi-turn stateful
  agents.
- OpenAI separates tracing, observability, guardrails, and evaluating agent
  workflows.
- ADK and Semantic Kernel both expose observability/evaluation/runtime
  concerns separate from agent prompts.

Current gap:

Verification can pass/fail a task, but we do not yet score the multi-agent
process itself.

Design fix:

Add `trace_eval_rubric.yaml` with dimensions:

```text
scope discipline
context economy
handoff clarity
tool economy
evidence quality
review readiness
recovery readiness
policy compliance
user-intervention quality
```

### 7. Human Interrupt And Resume Semantics Need Tightening

External basis:

- A2A-style task states distinguish simple messages, durable tasks, input
  required, auth required, cancellation, and artifacts.
- OpenAI guardrails/human-review docs treat human review as a workflow state.
- LangGraph interrupts are explicit state transitions, not just chat messages.

Current gap:

We have blocker notification and human-intervention UX design, but no strict
binding between `auth_required` / `input_required` and the exact resume packet.

Design fix:

Blocker notification should always produce or reference:

```text
resume_packet_path
last_safe_state
manual_action_required
verification_after_resume
dedupe_key
```

### 8. Worktree Arena Is Useful But Must Stay Gated

External basis:

- Qwen Code / Agent Arena-style patterns suggest comparative execution can be
  useful.
- Enterprise code review practice says parallel implementation multiplies
  merge and review cost.

Current gap:

We have `arena_comparison` as a topology, but no strict gate.

Design fix:

Arena mode requires:

```text
same bounded objective
isolated worktrees
same test/eval rubric
explicit reviewer
merge/discard decision
cost cap
```

Do not use arena mode for broad feature implementation.

### 9. Provider/Model Routing Is Not An Agent Architecture

External basis:

- Kimi API is OpenAI-compatible and exposes tool use plus official tools.
- Qwen-Agent exposes LLM/tool/agent components, RAG, code interpreter, and MCP
  support.

Current gap:

It is easy to overinterpret model-provider docs as multi-agent operating
architecture. They mainly inform provider adapter, tool-call compatibility,
memory/tool capability, and sandbox risk.

Design fix:

Add provider routing later as `ModelProviderAdapter`, not as a department or
conversation design. Provider-specific tools must pass Toolchain + Safety
capability-card review.

### 10. Skill And Hook Loading Should Be In Capability Templates

External basis:

- Claude Code and Codex treat skills as selective procedures and hooks as
  lifecycle/policy gates.
- Hermes/OpenClaw make hooks/guardrails hard runtime surfaces.

Current gap:

`agent_profile.yaml` lists tools but not skills and hooks explicitly. This can
cause "load everything" behavior or, worse, treating safety hooks as optional
context.

Design fix:

Agent profiles should include:

```text
allowed_skills
required_hooks
optional_tools
blocked_tools
tool_risk_policy
```

### 11. Agent Activation Metrics Are Missing

External basis:

- Enterprise flow metrics and SPACE/DORA-style operating metrics measure where
  work actually flows.
- Large multi-agent rosters tend to accumulate idle roles that still create
  routing and context overhead.

Current gap:

We have Flow Analytics as a conditional department, but no concrete metrics
that tell us whether 11 permanent agents are too many or too few.

Design fix:

Record per-agent:

```text
activation_count
handoff_count
failed_handoff_count
average_context_size
blocked_time
review_escape_count
rework_count
accepted_result_count
```

Use this to demote idle lanes or promote conditional lanes.

## Prioritized Optimizations

### P0: Required Before Real Multi-Conversation Automation

1. Typed handoff mode selector.
2. Capability template vs conversation state split.
3. Shared context delta template.
4. Artifact manifest template.
5. Trace/evaluation rubric.

### P1: Required Before Scaling Beyond First Closed Loop

1. Workflow graph schema.
2. Human interrupt/resume contract tightening.
3. Agent activation and handoff quality metrics.
4. Tool capability card risk class for provider and MCP tools.

### P2: Keep As Gated Extensions

1. Worktree arena / comparative execution.
2. A2A-compatible external protocol mapping.
3. Provider/model routing adapters for Kimi, Qwen, Mistral, local models, and
   OpenAI-compatible endpoints.
4. Dedicated permanent Architecture, Observability, Flow Analytics, Reliability,
   Continuous Improvement, or Operator Experience agents.

## Impact On Current 11-Agent Design

The current 11 permanent agents should not be replaced. They should be refined:

| Agent | Main optimization |
|---|---|
| `MoSim｜主线 PMO` | Require compressed human-decision and acceptance packets. |
| `MoSim｜调度中台` | Own typed handoff mode and workflow graph selection. |
| `MoSim｜产品发现战略` | Own value/appetite before expensive multi-agent topology. |
| `MoSim｜Agent Runtime 平台` | Own capability template vs conversation state implementation design. |
| `MoSim｜上下文记忆索引` | Own shared context delta and freshness metrics. |
| `MoSim｜工具链 MCP` | Own tool capability cards and provider/tool risk classes. |
| `MoSim｜知识秘书` | Promote accepted deltas, artifacts, and lessons without copying raw chat. |
| `MoSim｜验证评测` | Own trace/eval rubric and artifact review. |
| `MoSim｜安全合规` | Enforce hooks/tool risk, external path, secret, and destructive-action gates. |
| `MoSim｜DevOps 发布` | Own worktree arena merge/discard and artifact packaging rules. |
| `MoSim｜外部情报进化` | Keep provider/framework updates problem-driven and source-linked. |

## Recommendation

Do not add more permanent conversations now.

The next design refinement should add the missing typed artifacts around the
existing 11-agent model:

```text
handoff mode
capability template
shared context delta
artifact manifest
trace/evaluation rubric
workflow graph
```

After that, run one minimal closed-loop task and measure whether the current
11-agent topology is too large, too small, or missing a promoted conditional
agent.
