# Multi-Agent Frameworks Round 4

## source_slice

- Local multi-agent framework references under `References/Agent`:
  LangGraph, CrewAI, MetaGPT, AutoGen/AG2, CAMEL, and LlamaAgents.
- Focused read on orchestration philosophy, durable execution, human review,
  role/team modeling, worker placement, memory/state, and production control
  surfaces.
- Current CoAgent target surfaces: runtime task queue, conversation graph,
  bootstrap handoff, result review gate, automation guardrails, and future
  worker-loop recovery.

## read_files_or_urls

- `References/Agent/langgraph/README.md`
- `References/Agent/crewAI/docs/en/introduction.mdx`
- `References/Agent/MetaGPT/README.md`
- `References/Agent/autogen/docs/design/03 - Agent Worker Protocol.md`
- `References/Agent/ag2/README.md`
- `References/Agent/camel/docs/get_started/introduction.md`
- `References/Agent/llama-agents/README.md`

## architecture_claims

1. Production multi-agent systems separate deterministic workflow control from
   autonomous worker behavior. LangGraph durable execution, CrewAI Flows,
   LlamaAgents workflows, and AutoGen worker placement all point to the same
   boundary: state and routing belong to the harness, not to worker chat memory.
2. Role-based teams are useful only when tied to explicit SOPs, task routing,
   and review boundaries. MetaGPT's software-company framing supports MoSim's
   department model, but unmanaged permanent departments would increase
   coordination cost and context drift.
3. Human-in-the-loop is not an optional UX feature for long-running work. It is
   a state transition in the workflow, especially for destructive operations,
   acceptance of uncertain results, credential/login issues, and merge/deploy
   decisions.
4. Worker activation should be capability-routed and disposable. AutoGen's
   service/worker protocol and AG2's conversation patterns support CoAgent's
   current decision: workers should receive a bounded packet, return a result,
   and be released rather than becoming hidden durable authorities.
5. Memory/state should have layers. Frameworks distinguish working memory,
   persistent memory, workflow state, storage, and observability. CoAgent
   should keep task state in runtime, evidence in result packets/summaries,
   recovered knowledge in indexes, and visible discussion in Codex App.

## adopt_now

- Keep CoAgent's durable runtime and conversation graph as the workflow
  authority; visible department conversations are worker surfaces, not the
  source of truth.
- Keep `TaskSecretary`, PMO/DispatchCenter, DevOps, Verification, Security,
  Documentation, and Research/Engineering departments as SOP roles only when a
  concrete task packet and result packet exist.
- Treat human-review-required states as first-class result review states,
  instead of asking a worker to keep waiting inside a chat.
- Keep automation starts guarded by lock, tool-scope, prompt-injection, and
  review checks before launching a real visible worker.
- Add learning coverage reporting so required source families are visible and
  missing coverage cannot be mistaken for completed system research.

## adapt_later

- Add a stronger worker placement model: department capability registry,
  concurrency limits by task family, worker health, and timeout/retry policy.
- Add workflow-state replay for long-running tasks beyond the current SQLite
  queue and JSONL event stream.
- Add explicit human-interrupt packets that can pause a task with required
  decision, evidence, options, and resume command.
- Add richer observability traces for department task runs: tool calls,
  context-pack size, review status, elapsed time, and retry count.

## portable_only

- Hosted deployment platforms, distributed worker services, and server/client
  workflow APIs from LangGraph, LlamaAgents, and AutoGen are useful if CoAgent
  is reused by a team or SaaS environment, but MoSim should stay local,
  file-first, and Codex App-fronted for now.
- CAMEL's large-scale society/world-simulation and synthetic-data pipelines are
  valuable for future agent research, but they do not directly solve MoSim's
  current project-orchestration reliability problem.
- CrewAI/AG2 generic tool/plugin ecosystems are useful references, but MoSim's
  tools must remain constrained by project-local MCP and filesystem rules.

## reject

- Do not import a full multi-agent framework runtime into MoSim as the
  coordination core. The dependency and abstraction cost is higher than the
  current benefit, and it would obscure project-specific safety boundaries.
- Do not model MoSim departments as always-on peer agents that talk freely to
  each other. All durable work should pass through task packets, result
  packets, runtime state, and review gates.
- Do not use role names as proof of expertise. A department role is only valid
  when paired with read/write scope, stop condition, evidence, and a result
  schema.
- Do not allow workflow libraries or workers to store credentials or external
  account state inside the project tree.

## unknowns

- Whether CoAgent needs full workflow replay or whether SQLite events plus
  result summaries are enough will only be clear after several real long tasks.
- Whether department workers should be started through Codex CLI only or later
  through a stable app-server/control-plane adapter remains open.
- The best policy for splitting one large task into department packets versus
  one dedicated long-running task conversation is still empirical.

## required_patch

- Add `learning_indexer.py coverage` so required source-family coverage is
  machine-checkable.
- Add this audit record to cover the multi-agent framework family and connect
  framework lessons to CoAgent runtime/dispatch/automation decisions.
- Update status documents to record that multi-agent framework import is
  rejected while selected workflow/control-plane ideas are adopted.

## verification

```bash
python3 CoAgent/learning/learning_indexer.py coverage
python3 CoAgent/learning/learning_indexer.py validate --strict
python3 CoAgent/knowledge/knowledge_indexer.py build
python3 CoAgent/knowledge/knowledge_indexer.py search --query multi_agent_frameworks --limit 10
python3 CoAgent/doctor/coagent_doctor.py
python3 CoAgent/hooks/preflight.py
```

## next_trigger

- Revisit this audit when adding worker placement, replay, or human-interrupt
  packet support.
- Revisit this audit after the first real DevOps/GitIntegrator or PX4
  parameter-identification task uses a dedicated long-running conversation.
- Run the next coverage-closing audit for coding-agent runtimes, workflow
  runtimes, or knowledge/search references.
