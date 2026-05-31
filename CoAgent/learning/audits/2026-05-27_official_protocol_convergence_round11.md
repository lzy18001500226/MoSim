# Official Protocol Convergence Round 11

## source_slice

- Current official/first-party agent architecture and protocol documentation.
- Focused on convergence between workflow-vs-agent boundaries, handoff
  payload control, task lifecycle states, artifacts, persistence, and
  human-review recovery.
- This is a learning record only. It does not approve CoAgent runtime,
  transport, automation, or task-schema implementation.

## read_files_or_urls

- `https://www.anthropic.com/engineering/building-effective-agents`
- `https://openai.github.io/openai-agents-python/multi_agent/`
- `https://openai.github.io/openai-agents-python/handoffs/`
- `https://docs.langchain.com/oss/python/langgraph/workflows-agents`
- `https://docs.langchain.com/oss/python/langgraph/persistence`
- `https://a2a-protocol.org/latest/specification/`
- `https://adk.dev/agents/multi-agents/`
- `CoAgent/learning/audits/2026-05-27_official_multi_agent_principles_round8.md`
- `CoAgent/learning/audits/2026-05-27_multi_agent_frameworks_round4.md`
- `CoAgent/learning/audits/2026-05-27_coagent_design_synthesis_round10.md`

## architecture_claims

1. Official sources converge on a workflow-vs-agent distinction. Workflows give
   predictable code paths and gates; agents provide model-directed flexibility.
   CoAgent should make workflow authority deterministic and only let workers
   choose tactics inside bounded task packets.
2. Handoffs are not just conversation forwarding. The OpenAI Agents SDK treats
   handoffs as model-visible tools with target agents, optional input schemas,
   callbacks, dynamic enablement, and input filters. CoAgent's task packet
   should be the durable equivalent, and context packs should act as the input
   filter.
3. Agent-to-agent protocol design separates direct messages from long-running
   tasks. A2A allows a simple `Message` response for simple work, but uses a
   `Task` with status, artifacts, history, streaming updates, cancellation, and
   push notification configuration for complex work. CoAgent should preserve
   that split: not every interaction deserves task overhead, but long work must
   be a first-class task.
4. Task states should distinguish terminal states from interrupted states. A2A
   exposes submitted, working, completed, failed, canceled, input-required,
   rejected, and auth-required states. CoAgent should not flatten these into
   only `done` or `blocked`.
5. Artifacts are separate from chat messages. A2A makes artifacts task outputs
   with identifiers and metadata; LangGraph persists state snapshots and
   task-level writes. CoAgent result packets should point to artifacts and
   evidence paths rather than relying on prose in a chat bubble.
6. Persistence must support human-in-the-loop and recovery. LangGraph
   checkpointing enables human inspection, approval, memory, time travel,
   fault tolerance, and pending-write recovery. CoAgent does not need
   LangGraph now, but it does need append-only events plus rebuildable state
   before asynchronous department work is trusted.
7. Parallelism is useful only when there is aggregation or shared state. Both
   Anthropic/LangGraph workflow patterns and OpenAI orchestration docs treat
   parallel workers as useful when independent work can be synthesized by a
   manager/orchestrator. CoAgent should use parallel workers for audits and
   independent checks, not for loosely coordinated long implementation.
8. Good agent design reduces abstraction when debugging matters. Anthropic's
   guidance favors simple, composable patterns and warns that frameworks can
   obscure prompts/responses. CoAgent should keep Markdown/JSON packets and
   doctor checks visible before adopting a framework or private app-server
   protocol.
9. Tool and interface design is part of agent reliability. Official guidance
   emphasizes clear tools, documented parameters, guardrails, evals, and
   monitoring. CoAgent should treat MCP/tool surfaces as engineered interfaces,
   not ad hoc command strings.
10. Codex App remains a UI/review surface under this convergence. None of the
    official designs imply that a desktop client's private session files
    should become the source of truth for task lifecycle, artifacts, or
    authorization state.

## adopt_now

- Keep the current approval gate: no implementation until the user confirms
  the design boundaries.
- Treat `task packet -> context pack -> worker/dept conversation -> result
  packet -> review gate -> durable state` as the minimum CoAgent protocol.
- Distinguish simple message-style interactions from durable long-running task
  conversations.
- Add the A2A-inspired interrupted states `input_required` and `auth_required`
  to the post-approval vocabulary discussion, alongside `review_required`,
  `completed`, `failed`, `canceled`, and `rejected`.
- Require result packets to reference artifacts/evidence paths explicitly.
- Prefer append-only events and readable packets before adding graph runtime,
  app-server transport, or remote agent protocol support.
- Use handoff input filtering as a design principle: a receiving department
  should get only the relevant context pack, not raw full transcript history.

## adapt_later

- After approval, map CoAgent task states to an internal enum that can later be
  translated to A2A-compatible states if cross-project or non-Codex agents
  become real requirements.
- Add a department capability card concept later, but keep it project-local
  and human-readable until remote discovery is needed.
- Add streaming or push-style status updates only after file/CLI task polling
  and result-packet reconciliation work reliably.
- Add checkpoint-style pending-write recovery after multiple real department
  lifecycles prove where partial progress is lost.
- Add eval rubrics for department outputs: scope discipline, evidence quality,
  artifact completeness, recovery quality, and policy compliance.

## portable_only

- Full A2A protocol compatibility is portable value for future distributed
  CoAgent use, but it is unnecessary for MoSim's immediate local Codex App /
  VSCode workflow.
- LangGraph checkpoint semantics are a strong reference for future replay, but
  importing LangGraph now would add abstraction before CoAgent's packet/state
  vocabulary is confirmed.
- Google ADK multi-agent patterns are useful for future framework comparison,
  but CoAgent should not switch to a framework-owned orchestration runtime
  during the current design gate.

## reject

- Do not copy framework topology without the evidence contract. A supervisor,
  crew, team, or handoff is not useful unless it has owner, scope, context
  filter, artifacts, status transitions, and review.
- Do not treat all chat turns as durable task history. Some messages are
  transient; critical state belongs in task/result packets, artifacts, and
  event logs.
- Do not use asynchronous updates before reconciliation is reliable. Streaming
  status without durable get/resume semantics would recreate the current
  "I cannot see the other conversation" failure mode.
- Do not make tool descriptions or skills carry hard safety policy. Tool
  ergonomics help reliability, but hard boundaries need hooks, preflight, and
  review gates.

## unknowns

- Whether MoSim needs `auth_required` as a separate state from
  `input_required` for Epic/Fab login, Codex App session repair, and external
  account access.
- Whether CoAgent's first persistent state should remain Markdown/JSONL only
  or use SQLite as an index derived from append-only events.
- Whether human-readable department capability cards should be created before
  or after the first real visible department lifecycle.
- Whether future A2A mapping should be exact protocol compatibility or only an
  internal conceptual mapping.

## required_patch

- Add this audit record.
- Update URL seed notes to include current ADK, LangGraph, and A2A official
  locations.
- Update the three-round discussion draft with protocol convergence lessons.
- No CoAgent runtime, transport, automation, schema, or department expansion.

## verification

```bash
python3 CoAgent/doctor/check_design_gate.py
python3 CoAgent/learning/learning_indexer.py validate --strict
python3 CoAgent/learning/learning_indexer.py coverage
python3 - <<'PY'
from pathlib import Path
path = Path('CoAgent/learning/audits/2026-05-27_official_protocol_convergence_round11.md')
text = path.read_text(encoding='utf-8')
for needle in ['A2A', 'LangGraph', 'OpenAI Agents SDK', 'input_required', 'auth_required']:
    assert needle in text, needle
print('official protocol convergence audit OK')
PY
```

## next_trigger

- Before freezing CoAgent task-state and event vocabulary.
- Before implementing any handoff or transport adapter.
- Before creating department capability cards.
- Before adding asynchronous updates, push notifications, streaming status, or
  app-server integration.
