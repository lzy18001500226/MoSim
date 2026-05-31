# Hermes/Codex Runtime Boundaries Round 2

## source_slice

- Local Hermes runtime and desktop files that implement context engines,
  memory providers, scheduled jobs, guardrails, platform adapters, session
  caches, and desktop-side security/tool/session coordination.
- Local Codex app-server files that implement thread/turn/item primitives,
  thread state, app-server transport, MCP refresh/status, thread goals, doctor
  feedback reports, and thread-spawn agent graph storage.
- Official Anthropic engineering material for multi-agent systems and effective
  agents, used only for design constraints and not copied as implementation.

## read_files_or_urls

- `References/Agent/hermes-agent/agent/context_engine.py`
- `References/Agent/hermes-agent/agent/memory_manager.py`
- `References/Agent/hermes-agent/cron/scheduler.py`
- `References/Agent/hermes-agent/gateway/platforms/base.py`
- `References/Agent/hermes-desktop/src/main/sessions.ts`
- `References/Agent/hermes-desktop/src/main/session-cache.ts`
- `References/Agent/hermes-desktop/src/main/security.ts`
- `References/Agent/codex/codex-rs/app-server/README.md`
- `References/Agent/codex/codex-rs/app-server/src/thread_state.rs`
- `References/Agent/codex/codex-rs/app-server/src/transport.rs`
- `References/Agent/codex/codex-rs/app-server/src/request_processors/thread_summary.rs`
- `References/Agent/codex/codex-rs/app-server/src/request_processors/thread_goal_processor.rs`
- `References/Agent/codex/codex-rs/app-server/src/request_processors/feedback_doctor_report.rs`
- `References/Agent/codex/codex-rs/app-server/src/request_processors/mcp_processor.rs`
- `References/Agent/codex/codex-rs/agent-graph-store/src/lib.rs`
- `References/Agent/codex/codex-rs/agent-graph-store/src/store.rs`
- `References/Agent/codex/codex-rs/agent-graph-store/src/local.rs`
- `https://www.anthropic.com/engineering/multi-agent-research-system`
- `https://www.anthropic.com/engineering/building-effective-agents`

## architecture_claims

1. CoAgent should treat Codex App as the frontend and avoid writing private App
   state directly. Codex app-server has explicit thread, turn, item, goal,
   MCP, and notification primitives; those should be used as the conceptual
   model, while current project automation should stay file/CLI based until a
   stable supported interface is selected.
2. Long-running work needs a recoverable project graph, not just visible
   chats. Codex stores parent/child spawned-thread edges with open/closed
   lifecycle status, and CoAgent should mirror this idea in its task/runtime
   layer before adding many more department conversations.
3. Memory injection must be fenced and sanitised. Hermes routes memory through
   a manager, supports pre/post turn hooks, and strips memory-context blocks
   from user-visible streams; CoAgent should not treat recalled memory as raw
   user instruction.
4. Context compression should be a lifecycle interface. Hermes separates
   `on_session_start`, `update_from_response`, `should_compress`, `compress`,
   and `on_session_end`; CoAgent context packs are the first concrete version
   of this pattern, but they still need token budget policies and outcome
   summarisation.
5. Scheduled automation must have locks, toolset boundaries, and prompt
   injection checks before non-interactive execution. Hermes scheduler treats
   this as core infrastructure; CoAgent automation currently plans dispatch but
   should not auto-run without stronger guardrails.
6. Health reporting should be first-class. Codex doctor reports are structured
   JSON with status counts and failure tags; CoAgent needs a project-local
   doctor so the main conversation can distinguish real blockers from stale
   chat assumptions.

## adopt_now

- Add `CoAgent/doctor/coagent_doctor.py` as a structured local health report
  covering required files, department registry, reference index, learning
  audits, preflight, active queue, automation dispatch planning, and knowledge
  search.
- Add `conversation_edges` to `CoAgent/runtime/mosim_agent_runtime.py` so a
  durable task can record its visible department or dedicated task
  conversations with open/closed lifecycle state.
- Connect staged transport to that graph so `start-dispatch` opens an edge and
  `poll-dispatch` / `reconcile-result` close it when the result packet is
  imported.
- Keep context packs as the required startup artifact for dedicated task
  conversations; do not rely on raw accumulated chat history.
- Add the first fenced memory-context injector so recalled project knowledge
  enters context packs only as sanitised background evidence.
- Add a memory policy file so recalled project knowledge is source-weighted and
  capped by explicit character budget before entering a context pack.
- Add first automation guardrails so scheduled starts check locks, project
  scope, tool scope, prompt-injection patterns, and human-review gates.
- Add a first transport adapter boundary so dispatch prepares task/result
  packets while `CoAgent/transport/` owns visible-conversation delivery.
- Keep the learning audit taxonomy as adopt/adapt/portable/reject/unknown so
  external project ideas do not become unreviewed implementation debt.
- Keep Codex App as UI and CoAgent as project-local runtime; avoid direct
  mutation of Codex App private databases.

## adapt_later

- Extend the first `conversation_edges` table into a richer thread graph with
  reviewer edges, dependency edges, reason-for-close, result-packet refs, and
  Codex App/VSCode visibility reconciliation status.
- Extend the first fenced memory-context injector into a richer memory provider
  manager with structured facts, measured quality telemetry, and outcome
  summaries.
- Extend scheduler guardrails with time windows, stale-lock expiry,
  per-department concurrency limits, and richer source-aware prompt-injection
  scans before enabling unattended automation execution.
- Extend the first transport adapter interface with additional adapters only
  after the current `codex exec resume` loop proves stable across multiple real
  task dispatches.
- Add measured compaction policies to `CoAgent/context/context_pack.py` after
  several real long-running task conversations provide failure/recovery data.

## portable_only

- Hermes multi-platform gateway, delivery adapters, and desktop UX are useful
  for future projects with Slack/Discord/GitHub style frontends, but MoSim
  should not absorb them while Codex App is already the chosen frontend.
- Hosted remote-control/app-server style integrations may fit future team
  deployments, but this project currently needs local WSL/Windows reliability
  first.
- Anthropic SDK beta vault/environment/session abstractions are important
  resource-boundary references, but CoAgent should not implement a credential
  vault inside this repository.

## reject

- Do not import Hermes wholesale or rebuild its TUI/Desktop inside MoSim.
- Do not depend on private Codex App storage layout as the durable source of
  truth; CoAgent state must live in project files and ignored `Results/`.
- Do not enable auto-approved scheduled agents before tool scoping, prompt
  injection scanning, lock files, and human review gates exist and pass.
- Do not store tokens, vault records, browser/session secrets, or account
  cookies in CoAgent.

## unknowns

- The supported stability boundary of Codex app-server protocol for local
  project automation still needs official-version verification before direct
  app-server integration.
- The optimal context-pack size for GPT-5.5 long-running engineering work is
  still empirical; CoAgent needs measured failure/recovery data before setting
  hard token thresholds.
- Whether MoSim needs a persistent memory provider or only file-backed context
  packs remains open until several real long-running task conversations have
  been exercised.

## required_patch

- Add the CoAgent doctor command and document it.
- Add runtime conversation graph commands:
  `link-conversation`, `close-conversation`, and `conversation-graph`.
- Add transport graph reconciliation smoke coverage.
- Add fenced memory-context recall and context-pack smoke coverage.
- Add memory-policy source weighting, excerpt limits, and context character
  budget coverage.
- Add automation lock/tool-scope/prompt-injection/review-gate guardrails and
  smoke coverage.
- Add the transport adapter interface and smoke coverage.
- Update component and migration maps so the doctor/preflight/recovery path is
  visible.
- Rebuild the learning index and knowledge index so this audit becomes
  searchable.
- Run local checks proving the new doctor does not rely on Codex App private
  state.

## verification

```bash
python3 CoAgent/doctor/coagent_doctor.py
python3 CoAgent/learning/learning_indexer.py validate --strict
python3 CoAgent/learning/learning_indexer.py search --query doctor
python3 CoAgent/tests/test_runtime_thread_graph.py
python3 CoAgent/tests/test_transport_graph_reconcile.py
python3 CoAgent/tests/test_memory_context.py
python3 CoAgent/memory/memory_context.py build --query memory --max-chars 1200
python3 CoAgent/tests/test_automation_guardrails.py
python3 CoAgent/tests/test_transport_adapter.py
python3 CoAgent/knowledge/knowledge_indexer.py build
python3 CoAgent/knowledge/knowledge_indexer.py search --query runtime_boundaries
python3 CoAgent/hooks/preflight.py
```

## next_trigger

- Run the next audit slice when we inspect `Docs/Skills/Agent` in detail.
- Run the next audit slice when we compare OpenHands, MetaGPT, TaskWeaver,
  OpenSpec, Temporal-style workflow engines, or other local reference projects.
- Revisit direct Codex app-server integration only after the CLI/file transport
  loop has passed multiple real task dispatches without manual state repair.
