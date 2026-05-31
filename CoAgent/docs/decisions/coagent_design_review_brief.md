# CoAgent Design Review Brief

Date: 2026-05-27

Purpose: give the user a short review surface before CoAgent implementation is
unfrozen.

This brief does not approve implementation. It points to the current decision
packet and explains what the user is being asked to confirm.
The decision must be recorded in
`CoAgent/docs/decisions/coagent_design_decision_record.md`; chat-only approval is not
durable enough to unfreeze implementation.

## Review Entry Points

Read in this order:

1. `CoAgent/docs/decisions/coagent_design_discussion_packet.md`
2. `CoAgent/docs/architecture/task_intake_and_governance.md`
3. `CoAgent/docs/architecture/enterprise_to_agent_mapping.md`
4. `CoAgent/docs/architecture/coagent_complexity_control.md`
5. `CoAgent/docs/research/THREE_ROUND_STUDY_AND_DISCUSSION.md`
6. `CoAgent/docs/architecture/agent_concept_boundaries.md`
7. `CoAgent/docs/architecture/local_runtime_design_matrix.md`

The first file is the approval surface. The other files are supporting
evidence.

## External Principles Rechecked

| Source | Relevant principle | CoAgent interpretation |
|---|---|---|
| OpenAI Agents SDK orchestration | Manager/as-tool keeps one controller; handoffs transfer control to a specialist | CoAgent should keep PMO/DispatchCenter as workflow authority and use specialist conversations only through explicit task packets |
| OpenAI Agents SDK handoffs | Handoffs can carry input schemas and input filters | CoAgent task packets should carry typed metadata and should not forward raw chat history by default |
| OpenAI Agents SDK lifecycle hooks | Agent runs expose start/end, handoff, and tool lifecycle events | CoAgent should record task state transitions and tool/review events outside chat |
| Anthropic Claude Code subagents | Subagents use separate context windows and configurable tool permissions | Short-lived subagents are useful for bounded work but are not durable departments |
| Anthropic Claude Code hooks | Hooks can block or modify lifecycle behavior around tools, prompts, stops, and subagent stops | Safety, Git, secrets, destructive actions, and review gates belong in hooks/policies, not optional skills |
| Anthropic long-running harnesses | Long tasks need restart artifacts across context windows | CoAgent needs context packs, task packets, result packets, logs, summaries, and recovery docs |
| Anthropic multi-agent research | Subagents help by parallel exploration and compressing results back to a lead agent | CoAgent should consume and release workers, then preserve only evidence-backed summaries |
| Google ADK multi-agent docs | Multi-agent systems combine hierarchy, workflow agents, shared state, delegation, explicit invocation, and review patterns | CoAgent should keep explicit hierarchy and state instead of free-form peer chat |
| A2A protocol | Simple messages and durable tasks are separate; tasks carry status, artifacts, history, cancellation, auth, and input-required states | CoAgent should distinguish simple replies from long-running task lifecycles and require artifacts/evidence paths |
| LangGraph persistence | Threads, checkpoints, pending writes, interrupts, and human review need persistent state | CoAgent should prefer append-only events and rebuildable state before app-server or streaming transport |

Source URLs:

- https://openai.github.io/openai-agents-python/multi_agent/
- https://openai.github.io/openai-agents-python/handoffs/
- https://openai.github.io/openai-agents-python/ref/lifecycle/
- https://docs.anthropic.com/en/docs/claude-code/sub-agents
- https://docs.anthropic.com/en/docs/claude-code/hooks
- https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- https://www.anthropic.com/engineering/built-multi-agent-research-system
- https://adk.dev/agents/multi-agents/
- https://a2a-protocol.org/latest/specification/
- https://docs.langchain.com/oss/python/langgraph/persistence

## Proposed Design Philosophy

CoAgent is not a subagent collection.

CoAgent is a project-owned workflow control plane with:

- visible conversations as UI/review/work surfaces,
- project files as durable truth,
- task packets and result packets as communication,
- hooks/policies as enforced boundaries,
- skills as selectively loaded procedures,
- MCP/tools as callable capability surfaces,
- memory/search as evidence retrieval.

The controller should be boring and explicit. The workers can be specialized,
but they must receive scoped work and return structured evidence.

## Department Boundary To Confirm

Keep only these permanent conversations for now:

| Conversation | Status | Reason |
|---|---|---|
| `MoSim｜主线总控` | permanent | user alignment, final decisions, integrated reporting |
| `MoSim｜调度中台` | permanent/logical | task tickets, routing, result intake, status board |
| `MoSim｜研发工程部` | permanent | default technical execution lane |
| `MoSim｜验证测试部` | permanent | independent verification and reproducibility |
| `MoSim｜文档秘书部` | permanent | directives, decisions, docs consistency |
| `MoSim｜安全合规部` | permanent | path, secrets, licensing, destructive-action gates |
| `MoSim｜DevOps 发布部` | permanent | Git state, batching, branches, large-file checks |

Do not add UE, MWORKS, parameter-identification, Git-review, or research
departments yet. Use dedicated task conversations for those when the work is
long and context-heavy.

## Approval Questions

The user should explicitly accept or edit these defaults:

1. PMO/DispatchCenter own workflow authority; workers do not self-route.
2. The seven permanent conversations above are enough for the next phase.
3. Engineering stays one general execution lane until repeated queue pressure
   proves a split is needed.
4. DevOps remains separate because Git is high-risk and state-heavy.
5. Documentation records decisions, but DispatchCenter owns task state.
6. Hooks/policies enforce risk boundaries; skills do not.
7. Long tasks require task_id, parent department, scope, stop condition,
   context pack, and result packet.
8. Task-state/event vocabulary must distinguish simple replies, durable tasks,
   artifacts/evidence, `input_required`, `auth_required`, `review_required`,
   `completed`, `failed`, `canceled`, and `rejected`; do not collapse these
   into only `done/blocked`.
9. Task intake must classify requests before execution. Complex work starts
   with discovery; long-running work requires appetite, circuit breaker,
   checkpoint, and escalation conditions.
10. Goal hierarchy is fixed: Project Goal -> Canonical Task Goal ->
    Conversation Objective -> Subagent Objective. DispatchCenter records the
    canonical task goal; workers escalate drift instead of silently changing it.
11. V1 maximum nesting is PMO/main -> DispatchCenter -> department or
    dedicated task conversation -> short-lived subagent. Department-internal
    durable agent swarms are out of scope.
12. Transport stays file/CLI first; Codex App remains UI/review until app-server
   behavior is proven stable.
13. Automation stays dry-run/guarded until hooks and review gates are proven.

## If Approved

Implement in this order. The executable backlog is
`CoAgent/docs/decisions/coagent_post_approval_backlog.md`.

1. Freeze task-state and event vocabulary, including simple message, durable
   task, artifact/evidence, interrupted states, review states, and terminal
   states.
2. Add task intake fields and execution modes: task class, owner, appetite,
   circuit breaker, checkpoint, escalation, and acceptance gate.
3. Encode goal hierarchy and V1 complexity limits in the protocol docs.
4. Align task packet and result packet schemas to that vocabulary.
5. Strengthen preflight/hooks for path, secrets, destructive actions, Git, and
   result-packet validation.
6. Run one small real communication lifecycle through DevOps or Verification.
7. Run one dedicated long-task conversation with a context pack and result
   packet.
8. Only then consider app-server transport or scheduled automation.

## User Response Format

Use one of these formats so the decision can be recorded without ambiguity.

Accept all defaults:

```text
CoAgent design approved.
Decision date: YYYY-MM-DD
Approved defaults: all
Notes: <optional>
```

Accept with edits:

```text
CoAgent design approved with edits.
Decision date: YYYY-MM-DD
Accepted defaults: <list>
Rejected or changed defaults: <list>
Required doc updates before implementation: <list>
Notes: <optional>
```

Reject for revision:

```text
CoAgent design revision required.
Decision date: YYYY-MM-DD
Rejected defaults: <list>
Required changes: <list>
Do not implement until revised packet is reviewed: yes
```

After any accepted response, record the decision in
`CoAgent/docs/decisions/coagent_design_decision_record.md`,
`CoAgent/docs/decisions/coagent_goal_readiness_audit.md`, and
`Docs/Workflows/agent_task_ledger.md` before changing runtime code.
Then start from `COAGENT-IMPL-01` in
`CoAgent/docs/decisions/coagent_post_approval_backlog.md`.

## If Not Approved

Update these files before implementation:

- `CoAgent/docs/decisions/coagent_design_discussion_packet.md`
- `CoAgent/docs/decisions/coagent_design_review_brief.md`
- `CoAgent/docs/architecture/ARCHITECTURE.md`
- `CoAgent/docs/architecture/COMPONENT_MAP.md`
- `Docs/Workflows/agent_orchestration.md`
- `Docs/Workflows/agent_task_ledger.md`

Typical rejection paths:

| Rejected default | Required edit |
|---|---|
| Too many permanent conversations | Merge roles and update department table |
| Too few permanent conversations | Add creation criteria and review burden |
| DispatchCenter split is premature | Make it a logical role under PMO until communication stabilizes |
| Engineering should split earlier | Define split trigger, owner, scope, and result contract |
| File/CLI transport is too weak | Define app-server proof gate before use |
| Automation should start earlier | Define exact hooks, dry-run evidence, and human approval state |

## Current Status

Implementation remains frozen.

Allowed work before approval:

- read-only source study,
- documentation clarification,
- learning-index validation,
- small corrections to the discussion packet and review brief.
