# Official Multi-Agent Principles Round 8

## source_slice

- Official and first-party multi-agent architecture sources from
  `CoAgent/docs/research/multi_agent_learning_urls.md`.
- Focused on agent-team architecture, context management, handoff semantics,
  workflow control, hooks, skills, and long-running task recovery.
- This audit is a design-learning record only. It does not approve more
  CoAgent runtime implementation by itself.

## read_files_or_urls

- `https://www.anthropic.com/engineering/built-multi-agent-research-system`
- `https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents`
- `https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents`
- `https://www.anthropic.com/engineering/building-effective-agents`
- `https://www.anthropic.com/engineering/writing-tools-for-agents`
- `https://docs.anthropic.com/en/docs/claude-code/sub-agents`
- `https://docs.anthropic.com/en/docs/claude-code/hooks`
- `https://docs.anthropic.com/en/docs/claude-code/skills`
- `https://openai.github.io/openai-agents-python/multi_agent/`
- `https://openai.github.io/openai-agents-python/handoffs/`
- `https://openai.github.io/openai-agents-python/ref/lifecycle/`
- `https://google.github.io/adk-docs/workflows/`
- `https://github.com/a2aproject/A2A/blob/main/docs/specification.md`
- `https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/`

## architecture_claims

1. Multi-agent systems are useful when work can be decomposed into independent
   or semi-independent subtasks with separate context windows, not merely when
   multiple chat surfaces exist.
2. The central design boundary is workflow authority versus worker autonomy.
   Durable task state, routing, cancellation, review, and recovery must belong
   to a harness/control plane, while individual agents consume bounded task
   context and return bounded results.
3. Context is a finite resource. Skills, tools, prior messages, retrieved
   files, and worker outputs all compete for the same attention budget. CoAgent
   must prefer high-signal context packs, just-in-time retrieval, compaction,
   and structured notes over loading everything.
4. Skills are selectively loaded procedural packages. They are suitable for
   repeatable operating procedures, checklists, templates, and supporting
   scripts. They are not the right place for hard policy or universal rules.
5. Hooks are lifecycle-enforced constraints or instrumentation points. They
   should be treated as hard gates for risky commands, tool calls, permission
   requests, stop events, post-tool checks, and review requirements. They must
   not rely on the model voluntarily selecting them.
6. Handoffs are explicit transfer contracts. The OpenAI Agents SDK models
   handoffs as routing tools with optional input schemas, filters, callbacks,
   and dynamic enabling. A2A models cross-agent interaction as stateful tasks,
   messages, artifacts, streaming updates, cancellation, and authorization.
7. Long-running work needs explicit restart artifacts. Anthropic's long-running
   harness pattern uses an initializer, feature/test inventory, progress log,
   git history, and incremental sessions. CoAgent's equivalent should be task
   packets, context packs, result packets, event logs, status board, and review
   gates.
8. Agent teams should be sparse and purpose-bound. Permanent departments are
   justified only when they reduce repeated context loading or isolate a
   long-running responsibility. Otherwise, bounded short-lived workers are less
   risky.
9. Evaluation must judge outcomes and process quality, not only whether a
   prescribed path was followed. Multi-agent systems can reach valid answers
   through different trajectories, so review rubrics, traces, artifacts, and
   human checks are mandatory for high-risk work.
10. Asynchrony improves throughput but increases state-consistency and recovery
    risk. CoAgent should start with synchronous or queued task/result packets
    and add asynchronous push/streaming only when status reconciliation is
    robust.

## adopt_now

- Treat `CoAgent/docs/research/multi_agent_learning_urls.md` as the official URL
  seed list and require every future source study to produce an audit record.
- Add a concept-boundary document that defines skills, hooks, tools/MCP,
  subagents, visible department agents, handoffs, task packets, result packets,
  context packs, and review gates.
- Keep PMO/dispatch as workflow authority. It should create task packets,
  choose the owner conversation, set stop conditions, require evidence, and
  route result packets.
- Keep department conversations visible and durable only for responsibilities
  that benefit from state over time: PMO, DevOps/Git, docs/knowledge,
  verification, safety/security, and research/engineering.
- Use short-lived subagents for bounded read/search/audit tasks where their
  detailed context should not pollute the main conversation.
- Move hard safety requirements into hooks/policies/preflight checks instead of
  relying on skill instructions.
- Require task packets to include owner, scope, context budget, required
  artifacts, stop condition, review gate, and result packet path.

## adapt_later

- Add an A2A-inspired internal task model with explicit states such as
  `queued`, `working`, `input_required`, `auth_required`, `review_required`,
  `completed`, `failed`, `canceled`, and `rejected`.
- Add handoff schemas with input filters so a worker receives only the relevant
  task context, not the full originating conversation.
- Add lifecycle instrumentation around agent starts, tool starts/ends,
  handoffs, task cancellation, and review transitions.
- Add a small eval harness for department outputs: factuality, completeness,
  evidence quality, scope discipline, and tool efficiency.
- Add asynchronous task updates only after task state reconciliation and stale
  session recovery are reliable.

## portable_only

- Full A2A wire-protocol compatibility is useful if CoAgent later communicates
  with non-Codex remote agents, but MoSim can initially use project-local
  Markdown/JSON task and result packets.
- Microsoft Semantic Kernel and Google ADK workflow runtimes are useful
  references for future portability, but importing either runtime would add
  dependency and abstraction cost before CoAgent's local contracts are stable.
- Agent cards with public/extended capability metadata are useful for future
  cross-project reuse. For now, simple department capability docs are enough.

## reject

- Do not treat visible Codex App conversations as the durable control plane.
  They are review and interaction surfaces; project files must remain the
  recoverable source of truth.
- Do not keep every department permanently active. More agents increase
  coordination surface, stale context, duplicated effort, and hidden failure
  modes.
- Do not load all skills or all reference projects into every conversation.
  Context overload directly contradicts the context-engineering guidance.
- Do not use skills to enforce security, git discipline, destructive-command
  blocking, credential rules, or large-file rules. These require hooks or
  deterministic preflight gates.
- Do not adopt free-form group chat as the default collaboration model. Use it
  only for explicit architecture reviews where discussion value exceeds the
  coordination cost.

## unknowns

- The exact context-pack size target for MoSim remains empirical. The current
  rule should be high-signal and bounded, not maximum-length.
- OpenAI Codex product docs for skills/hooks were not reliably retrievable via
  command-line scraping in this pass. Recheck through official docs/MCP or the
  browser before making product-specific claims.
- The right threshold for creating a durable department conversation versus a
  short-lived worker needs real-task evidence.
- Whether CoAgent should later support A2A-compatible transport depends on
  whether remote non-Codex agents become part of the workflow.

## required_patch

- Add this audit record.
- Add `CoAgent/docs/architecture/agent_concept_boundaries.md`.
- Keep the URL seed list as the source list for future self-learning rounds.
- No runtime or dispatch implementation changes in this pass.

## verification

```bash
python3 CoAgent/learning/learning_indexer.py validate --strict
python3 CoAgent/learning/learning_indexer.py coverage
python3 - <<'PY'
from pathlib import Path
for path in [
    Path('CoAgent/learning/audits/2026-05-27_official_multi_agent_principles_round8.md'),
    Path('CoAgent/docs/architecture/agent_concept_boundaries.md'),
]:
    assert path.exists(), path
    text = path.read_text(encoding='utf-8')
    assert 'skills' in text.lower()
    assert 'hooks' in text.lower()
print('official multi-agent learning docs OK')
PY
```

## next_trigger

- Before adding or changing CoAgent department conversations.
- Before implementing handoff, transport, A2A-style task state, or background
  worker execution.
- Before converting any process rule into a skill or hook.
- Before deciding whether Hermes/OpenClaw/Codex architecture elements should be
  migrated into CoAgent.
