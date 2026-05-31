# CoAgent Migration Status

## Scope Correction

CoAgent is no longer tracked as a Hermes-only migration.

Hermes remains a high-value reference, but the current goal is broader:

- study and index the local agent/reference projects,
- study official engineering material such as Anthropic/Claude agent articles,
- study SDK/runtime resource boundaries such as Anthropic beta agents,
  sessions, threads, memory stores, skills, environments, files, vaults, and
  webhooks,
- classify each lesson as MoSim-ready, later adaptation, portable-only,
  rejected, or unknown,
- implement only the useful subset in MoSim-owned CoAgent runtime, dispatch,
  automation, knowledge, hooks, transport, and protocol layers.

Use `CoAgent/docs/research/LEARNING_STRATEGY.md` as the source-of-truth for this learning
and adoption loop.

## Current Gate

Current status is recorded in `CoAgent/STATUS.md`.

The design decision record is
`CoAgent/docs/decisions/coagent_design_decision_record.md` and currently gates
implementation. The first approved task is `COAGENT-IMPL-01`; this record
gates implementation by limiting the current write scope to that task. Treat the
capabilities listed below as evidence/prototypes unless they are explicitly
referenced by that task. Do not continue app-server transport, unattended
automation, permanent department expansion, durable department-internal agent
swarms, or tool/MCP expansion until later tasks are approved.

## Current Baseline

MoSim has already absorbed these ideas at the project-rule level:

- department-based operating model,
- queue/WAL mindset,
- durable task ledger requirement,
- visible conversation requirement,
- separation between policy, runtime, and execution workers,
- MCP-first mindset for tool-rich domains.

MoSim has also now absorbed these structural pieces into project files:

- `CoAgent/` as the architecture root,
- project-wide `References/` master index,
- index validation script,
- runtime implementation moved under `CoAgent/runtime/`,
- compatibility launcher retained under `Scripts/agent/`,
- first runtime-core packet/status capabilities:
  `task-packet`, `result-packet`, and `status-board`,
- first runtime conversation graph capability:
  `link-conversation`, `close-conversation`, and `conversation-graph` now
  record parent task, department, visible thread id, role, metadata, and
  open/closed lifecycle state in the same SQLite runtime DB as task state,
- first transport-to-graph bridge:
  `start-dispatch` opens a dispatch conversation edge, while `poll-dispatch`
  and `reconcile-result` close it after importing the result packet,
- first dispatch-core capabilities:
  department thread registry, dispatch envelope export, department-task text,
  review brief export, and result packet import,
- first result-router capability:
  `CoAgent/result_router/result_router.py` validates text/JSON result packets,
  imports them into runtime state, archives source and parsed packets under
  ignored `Results/agent_packets/archive/`, and writes searchable result
  summaries under `Results/agent_packets/summaries/`,
- first result review-gate capability:
  imported result packets now produce `accepted`, `needs_review`, or
  `rejected` review metadata under `Results/agent_packets/reviews/`, checking
  terminal evidence, next recommended action, blocker details, concerns, and
  unresolved risks. This separates runtime import from acceptance,
- first end-to-end lifecycle proof:
  `CoAgent/tests/test_lifecycle_smoke.py` proves one task can be created,
  converted into a context pack and department dispatch text, linked to a
  visible-conversation edge, completed by a result packet, imported through the
  result router, closed in the conversation graph, and recovered through the
  knowledge index,
- first reusable long-task bootstrap capability:
  `CoAgent/bootstrap/task_bootstrap.py` creates project-local context packs,
  dispatch packets, handoff files, dry-run transport plans, and conversation
  edges for dedicated long-running task conversations. The generated transport
  packet now carries the full handoff/context pack rather than the bare task
  packet. Recovery imports the declared result packet, closes the edge, writes
  a recovery summary, and upserts generated evidence into the knowledge index,
- first context-pack quality metrics:
  `CoAgent/context/context_pack.py` returns character counts, rough token
  estimates, section budgets, event/query counts, memory-hit and truncation
  counts, and `ok` / `warning` / `fail` risk so long-running task conversations
  can be judged by measurable startup-context size instead of chat intuition,
- first transport-aware dispatch capability:
  dry-run Codex resume-command planning with packet/result path materialization,
- first transport adapter capability:
  `CoAgent/transport/adapter.py` defines the visible-conversation transport
  interface, and `CoAgent/transport/codex_exec.py` owns the current
  `codex exec resume` shadow-home adapter instead of embedding process/session
  details in dispatch logic,
- first live transport proof:
  project-local shadow `CODEX_HOME` and `sqlite_home` allowed a real department
  thread to write `Results/agent_packets/transport_probe_task_v2.yaml`, and
  CoAgent imported that packet back into runtime state as `task_completed`,
- transport recovery proof:
  even when `run-dispatch` times out, `reconcile-result` can import the
  declared project-local result file and move the runtime task to `done`,
- staged transport supervisor proof:
  `start-dispatch` plus later `poll-dispatch` successfully observed a real
  department-thread result file and imported `transport_probe_task_v6` into
  runtime state as `done`,
- first hook/preflight capability:
  CoAgent-local path, index, compile, and large-file preflight checks,
- first automation capability:
  recurring automation definitions plus runtime task enqueue and dispatch-plan generation for daily tasks,
- first automation/transport bridge:
  automation can now generate department-ready dry-run dispatch plans, and the
  staged transport supervisor is the current execution path for real runs,
- first automation guardrail capability:
  `CoAgent/automation/guardrails.py` checks project path scope, tool scope,
  prompt-injection patterns, duplicate automation locks, and human-review gates
  before unattended `start-due-dispatch` launches a visible department run,
- first worker policy capability:
  `CoAgent/automation/worker_policy.json` and `worker-status` expose lock TTL,
  stale-lock warnings, global/automation/department concurrency limits, and
  recoverable lock inventory before unattended automation starts,
- first knowledge capability:
  project-owned knowledge source registry plus local index/search across
  CoAgent, workflows, progress, rules, ledger, and transport run summaries.
- first lightweight knowledge upsert capability:
  `CoAgent/knowledge/knowledge_indexer.py` can upsert one generated evidence
  file into the local index, so lifecycle checks do not need to rescan every
  source tree on each doctor run,
- first context-pack capability:
  `CoAgent/context/context_pack.py` can generate compact startup context from a
  runtime task, so a dedicated long-running task conversation can start from
  project state instead of raw chat history.
- first fenced memory-context capability:
  `CoAgent/memory/memory_context.py` recalls from the project knowledge index,
  sanitises nested memory tags, applies `CoAgent/memory/memory_policy.json`
  source weights and character budgets, and injects only a fenced
  background-evidence block into context packs when explicitly requested.
- first architecture-learning audit record:
  `CoAgent/learning/audits/2026-05-27_context_pack_and_agent_resource_round1.md`
  records the first bounded source-slice audit and maps agent resource-boundary
  lessons to concrete CoAgent patches.
- first source-to-architecture index:
  `CoAgent/learning/learning_indexer.py` validates learning audit sections and
  builds `Results/coagent_learning/learning_index.json` so audit outcomes are
  machine-searchable instead of Markdown-only.
- second architecture-learning audit record:
  `CoAgent/learning/audits/2026-05-27_hermes_codex_runtime_boundaries_round2.md`
  records Hermes/Codex runtime-boundary lessons: memory must be fenced,
  context compression should be a lifecycle, automation needs locks/tool scopes
  and prompt-injection checks, thread graphs need lifecycle state, and Codex
  App private storage should not be CoAgent's source of truth.
- third architecture-learning audit record:
  `CoAgent/learning/audits/2026-05-27_context_evaluation_harness_round3.md`
  records local context/evaluation/harness-skill lessons and Anthropic
  Engineering article lessons: context must be explicitly budgeted, result
  import must be separated from acceptance, locked harness checks must remain
  outside worker-owned editable surfaces, and full handoff/context packets
  should be the transport payload for dedicated long-running conversations.
- fourth architecture-learning audit record:
  `CoAgent/learning/audits/2026-05-27_multi_agent_frameworks_round4.md`
  records LangGraph, CrewAI, MetaGPT, AutoGen/AG2, CAMEL, and LlamaAgents
  framework lessons: use deterministic workflow/control-plane state around
  autonomous workers, keep human review as a state transition, route workers by
  capability and result packets, and reject importing a full external
  multi-agent framework as MoSim's coordination core.
- first learning coverage gate:
  `CoAgent/learning/learning_indexer.py coverage` reports required source
  families as covered or missing, so the overall research goal has a
  machine-checkable coverage surface instead of relying on chat memory.
- first doctor capability:
  `CoAgent/doctor/coagent_doctor.py` produces a structured local health report
  covering required files, department registry, transport registry readiness,
  reference index, learning audits, preflight, runtime/transport conversation
  graph smoke tests, fenced memory-context smoke tests, automation guardrail
  smoke tests, transport-adapter smoke tests, result-router/review-gate smoke tests,
  end-to-end lifecycle smoke tests, long-task bootstrap/transport-plan/recovery
  smoke tests, context-pack quality metrics through memory-context smoke,
  active queue, automation dispatch planning, and knowledge search.
- first goal-alignment doctor capability:
  `CoAgent/doctor/goal_alignment.py` validates task, context-pack, and result
  packet goal consistency and rejects setup-only substitutes such as creating a
  task shell, opening a conversation, elapsed time, or result-packet goal
  mutation as completion evidence.
- first runtime metadata patch capability:
  `CoAgent/runtime/mosim_agent_runtime.py update-metadata` records result
  packet evidence fields through the durable runtime event stream, avoiding
  manual SQLite edits for `files_changed`, `commands_run`, `evidence`,
  `risks`, `blockers`, `review_status`, `acceptance_state`, and
  `next_recommended_action`.
- active automation registry alignment:
  recurring automation definitions now route to the current active department
  names: `ExternalIntelligenceAgent`, `KnowledgeSecretaryAgent`,
  `ContextMemoryAgent`, `SafetyComplianceAgent`, and `DevOpsReleaseAgent`.

MoSim has also now recorded the broader external-learning target:

- local source slices include `References/Agent/` and
  `References/Agent/anthropic-sdk-python/src/anthropic/resources/beta`;
- external source slices include Anthropic Engineering / Claude engineering
  articles and other high-quality multi-agent projects;
- new long-running task conversations must start from durable context packs
  rather than relying on raw chat history.

## Not Yet Fully Landed

### Cross-Source Gaps

- durable conversation gateway beyond one Codex client; bootstrap now creates
  project-owned handoff/recovery artifacts and dry-run transport plans, but
  live delivery still depends on the current transport adapter,
- built-in scheduler/automation loop integrated with project task queue,
- richer structured memory facts beyond the first measured context-quality
  telemetry,
- stable background worker model beyond guarded staged starts,
- richer transport adapter implementations beyond the first Codex CLI adapter,
- richer result-packet review and approval workflows beyond packet import and
  lifecycle smoke coverage,
- richer conversation graph semantics beyond first open/closed edges,
- richer source-to-architecture audit database,
- self-improving skill/runtime loop,
- richer shell/tool guardrails and lifecycle hook chain,
- doctor/preflight and restart recovery beyond first local report,
- session-scoped structured logging,
- worktree/parallel-run isolation for engineering streams,
- clear rule for when to create a dedicated task conversation versus a
  short-lived worker.

### Source Families Still Needing Structured Audit

- Anthropic Engineering / Claude engineering articles.
- `References/Agent/anthropic-sdk-python/src/anthropic/resources/beta`.
- Agent skill/operator systems now under `References/Agent`, beyond the first
  context/evaluation/harness slice.
- Multi-agent frameworks under `References/Agent` beyond the first
  LangGraph/CrewAI/MetaGPT/AutoGen/AG2/CAMEL/LlamaAgents slice.
- Workflow/runtime references such as Temporal, OpenSpec, TaskWeaver, and
  OKWinds.

### From Codex Source

- direct use of app-server protocol for project-owned conversation tooling,
- explicit thread-store style boundary for project conversations,
- rollout trace based project event browser,
- stronger hook / policy integration,
- project-owned UI or dashboard built on top of official client semantics.

## Immediate Next Steps

1. keep Codex App as frontend,
2. keep WSL Codex conversation as primary execution surface,
3. keep `CoAgent/runtime/mosim_agent_runtime.py` as the runtime seed,
4. use `CoAgent/doctor/coagent_doctor.py --json --output Results/coagent_doctor/latest.json`
   before expanding transport or automation,
5. continue stabilizing staged transport dispatch,
6. use `CoAgent/bootstrap/task_bootstrap.py --include-transport-plan` as the
   standard long-task conversation bootstrap/recovery path,
7. run structured audits using `CoAgent/docs/research/LEARNING_STRATEGY.md`,
8. extend automation beyond enqueue into execution/report loops only after
   explicit review,
9. extend knowledge from keyword search into stronger recovery and
   source-to-doc memory,
10. postpone custom UI and only revisit it if Codex App becomes the blocker.

## Explicit Non-Goals

These are not the current target:

- rebuilding Hermes TUI,
- rebuilding Hermes Desktop,
- replacing Codex App UI,
- importing Hermes runtime wholesale,
- importing any third-party agent framework wholesale,
- depending on hidden Codex subagent state as the real runtime.
