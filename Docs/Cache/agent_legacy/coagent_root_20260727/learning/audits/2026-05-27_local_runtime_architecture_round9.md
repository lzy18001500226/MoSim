# Local Runtime Architecture Round 9

## source_slice

- Local Hermes runtime files around context engines, memory management, shell
  hooks, guardrails, Codex app-server transport, and event projection.
- Local Codex source files around app-server threads, turns, items, thread
  store, rollout trace, skills watcher, and persisted parent-child thread
  graph edges.
- Local OpenClaw files around gateway architecture, agent loop, multi-agent
  routing, delegate boundaries, task flow, hooks, standing orders, compaction,
  context engine, command queue, memory, workspace, sessions, auth, and
  security posture.
- Local LangGraph files around stateful graph orchestration, checkpointing,
  checkpoint conformance, prebuilt interrupt schemas, and threat model.

## read_files_or_urls

- `References/Agent/hermes-agent/README.md`
- `References/Agent/hermes-agent/AGENTS.md`
- `References/Agent/hermes-agent/agent/context_engine.py`
- `References/Agent/hermes-agent/agent/memory_manager.py`
- `References/Agent/hermes-agent/agent/shell_hooks.py`
- `References/Agent/hermes-agent/agent/tool_guardrails.py`
- `References/Agent/hermes-agent/agent/transports/codex_app_server.py`
- `References/Agent/hermes-agent/agent/transports/codex_event_projector.py`
- `References/Agent/codex/codex-rs/app-server/README.md`
- `References/Agent/codex/codex-rs/thread-store/README.md`
- `References/Agent/codex/codex-rs/docs/protocol_v1.md`
- `References/Agent/codex/codex-rs/rollout-trace/README.md`
- `References/Agent/codex/docs/skills.md`
- `References/Agent/codex/codex-rs/app-server/src/skills_watcher.rs`
- `References/Agent/codex/codex-rs/agent-graph-store/src/types.rs`
- `References/Agent/codex/codex-rs/agent-graph-store/src/store.rs`
- `References/Agent/openclaw/README.md`
- `References/Agent/openclaw/AGENTS.md`
- `References/Agent/openclaw/docs/concepts/architecture.md`
- `References/Agent/openclaw/docs/concepts/agent-loop.md`
- `References/Agent/openclaw/docs/concepts/multi-agent.md`
- `References/Agent/openclaw/docs/concepts/delegate-architecture.md`
- `References/Agent/openclaw/docs/automation/taskflow.md`
- `References/Agent/openclaw/docs/automation/hooks.md`
- `References/Agent/openclaw/docs/automation/standing-orders.md`
- `References/Agent/openclaw/docs/concepts/compaction.md`
- `References/Agent/openclaw/docs/concepts/context-engine.md`
- `References/Agent/openclaw/docs/concepts/queue.md`
- `References/Agent/openclaw/docs/concepts/memory.md`
- `References/Agent/openclaw/docs/concepts/active-memory.md`
- `References/Agent/openclaw/docs/concepts/session.md`
- `References/Agent/openclaw/docs/concepts/agent-workspace.md`
- `References/Agent/openclaw/SECURITY.md`
- `References/Agent/openclaw/docs/auth-credential-semantics.md`
- `References/Agent/langgraph/README.md`
- `References/Agent/langgraph/libs/langgraph/README.md`
- `References/Agent/langgraph/libs/checkpoint/README.md`
- `References/Agent/langgraph/libs/checkpoint-conformance/README.md`
- `References/Agent/langgraph/libs/prebuilt/README.md`
- `References/Agent/langgraph/.github/THREAT_MODEL.md`

## architecture_claims

1. CoAgent needs a project-owned control plane, not a chat-list convention.
   Codex app-server already models thread, turn, item, metadata, goal, skill,
   hook, MCP, review, interrupt, rollback, and thread graph concepts. CoAgent
   should align its vocabulary with those concepts while keeping durable state
   in project files and generated runtime artifacts.
2. Long-running work needs event-sourced evidence before interpretation.
   Codex rollout trace records raw ordered events and lets an offline reducer
   build semantic meaning later. CoAgent should prefer append-only raw event
   records plus derived status views over editing chat transcripts directly.
3. Context must be a managed lifecycle, not an ever-growing prompt. Hermes and
   OpenClaw both separate context assembly, compaction, after-turn updates, and
   subagent lifecycle. LangGraph checkpointers preserve graph state at every
   superstep. CoAgent context packs should become lifecycle artifacts with
   explicit budgets, source priority, and checkpoint references.
4. Memory is evidence and recall, not command authority. Hermes fences and
   sanitizes memory context before it reaches the user-visible stream.
   OpenClaw splits curated `MEMORY.md`, daily notes, indexed memory search, and
   reviewable dreaming. CoAgent should use memory/search as background evidence
   and keep hard authority in policy, hooks, and task packets.
5. Hooks and guardrails are hard runtime gates. Hermes shell hooks require
   allowlist consent, bounded timeouts, and JSON input/output. OpenClaw hooks
   have lifecycle events and terminal blocking semantics. CoAgent should use
   hooks for path boundaries, destructive actions, credential handling,
   Git/large-file checks, and review gates, not as optional skills.
6. Skills should stay procedural and selectively loaded. Codex watches skill
   roots and notifies on changes; OpenClaw loads workspace/shared skills with
   allowlists; Hermes supports skill improvement but with review risk. CoAgent
   should treat skills as task-local procedures and scripts, never as global
   policy or universal memory.
7. Durable task orchestration should separate tasks, flows, queues, and
   visible conversations. OpenClaw has per-session lanes, global concurrency
   lanes, background tasks, task flows, cancel intent, revision tracking, and
   standing orders. CoAgent needs a simpler first version: task packet,
   result packet, event log, owner conversation, state, stop condition, and
   review gate.
8. Multi-agent isolation is useful only when identity, workspace, auth,
   session, and tool policy are separated. OpenClaw's multi-agent routing and
   delegate model show why one shared gateway is not a multi-tenant security
   boundary. CoAgent department conversations should be sparse, explicit, and
   backed by scope/tool boundaries.
9. Human-in-the-loop must be represented in state. LangGraph interrupts,
   OpenClaw approvals/standing orders, and Codex permission/review primitives
   all treat human review as a state transition. CoAgent should record
   `review_required`, `input_required`, `auth_required`, and `approved` as
   task states, not as informal chat text.
10. Directly importing Hermes/OpenClaw/LangGraph is lower value than importing
    their architecture boundaries. MoSim already chose Codex App/VSCode as
    the main UI. The durable work is a MoSim-owned harness, not another TUI,
    desktop app, or social-channel gateway.

## adopt_now

- Add a local runtime design matrix that compares Hermes, Codex, OpenClaw, and
  LangGraph by control plane, context/memory, skills/hooks, task model,
  safety/recovery, and CoAgent lesson.
- Treat Codex App and VSCode as UI/review surfaces only. Keep task packets,
  result packets, context packs, status boards, and event logs in CoAgent.
- Require task state names to distinguish work, waiting for input, waiting for
  auth, waiting for review, completed, failed, canceled, and rejected.
- Make hooks/policies the home for security and Git/path/destructive-action
  boundaries. Skills may explain a procedure, but hooks must enforce it.
- Keep visible department conversations sparse. Permanent departments need
  durable responsibility and a defined state contract; otherwise use
  short-lived workers or one-off task conversations.
- Use append-only event logs and derived status boards as the durable
  communication substrate between conversations.
- Start every dedicated long-task conversation from a context pack, not from a
  raw chat transcript or the Codex App private session database.
- Keep memory/search outputs fenced as background evidence with source paths,
  freshness, and budget limits.

## adapt_later

- Add a checkpoint-style persistence contract for CoAgent task runs, inspired
  by LangGraph checkpoints but implemented as project-owned JSONL/SQLite only
  after the state schema is stable.
- Add a Codex app-server adapter only after direct protocol stability and
  failure behavior are verified; keep current file/CLI transport as the safer
  near-term path.
- Add event projection similar to Hermes' Codex projector so Codex-native
  events can be converted into CoAgent task/result/status records without
  leaking UI-specific details into the runtime core.
- Add standing-order support for recurring MoSim maintenance jobs only after
  hooks, review gates, and rollback/recovery records are reliable.
- Add active-memory style pre-turn retrieval only after source trust,
  truncation, and citation rules are deterministic.
- Add richer department capability cards when cross-project reuse becomes real.

## portable_only

- OpenClaw's social-channel gateway, device nodes, pairing flows, and canvas
  surface are useful for future assistant products but not needed for MoSim's
  current Codex App/VSCode workflow.
- Hermes multi-channel gateway and TUI are useful references for UI/runtime
  separation but should stay out of the MoSim runtime.
- LangGraph full graph runtime is useful if CoAgent becomes a standalone
  agent framework, but importing it now would add abstraction before MoSim's
  task/result/event contracts are stable.
- OpenClaw delegate identity patterns are valuable for future organizational
  deployments; MoSim currently needs project and repository boundaries first.

## reject

- Do not use Codex App session files or UI labels as the canonical state
  store for CoAgent communication.
- Do not create many permanent department conversations just because the UI can
  show them. More visible agents increase stale context and coordination
  failure unless their responsibilities are durable and narrow.
- Do not auto-mutate skills from agent output without human review. Hermes'
  self-improvement loop is interesting but too risky for MoSim until review
  and regression checks are mature.
- Do not put secrets, OAuth refresh tokens, browser cookies, launcher account
  cache, or personal session material into CoAgent project files.
- Do not treat OpenClaw's one-user trusted gateway model as a multi-tenant
  security boundary.

## unknowns

- The stable public boundary of Codex app-server for third-party automation
  still needs product-doc/API verification before CoAgent depends on it.
- The right CoAgent persistence backend is still open: JSONL is easiest to
  inspect; SQLite is better for indexing/revision checks; both may be needed.
- The optimal context-pack size and freshness policy must be measured on real
  MoSim long tasks.
- Whether department conversations should be created by app-server protocol,
  CLI resume, or manual UI action remains a runtime reliability question.
- The minimum useful event schema for task replay needs a third learning pass
  and a design discussion before implementation.

## required_patch

- Add this second-pass local runtime audit.
- Add `CoAgent/docs/architecture/local_runtime_design_matrix.md`.
- Update `CoAgent/learning/README.md` so future agents read the matrix before
  modifying CoAgent runtime/dispatch.
- Update `CoAgent/docs/research/LEARNING_STRATEGY.md` to record that local runtime design is
  still in the learning/discussion gate and not yet approved for broad
  implementation.
- Run learning index validation and coverage.

## verification

```bash
python3 CoAgent/learning/learning_indexer.py validate --strict
python3 CoAgent/learning/learning_indexer.py coverage
python3 - <<'PY'
from pathlib import Path
paths = [
    Path('CoAgent/learning/audits/2026-05-27_local_runtime_architecture_round9.md'),
    Path('CoAgent/docs/architecture/local_runtime_design_matrix.md'),
]
for path in paths:
    text = path.read_text(encoding='utf-8')
    assert 'Hermes' in text
    assert 'Codex' in text
    assert 'OpenClaw' in text
    assert 'LangGraph' in text
print('local runtime learning docs OK')
PY
```

## next_trigger

- Before changing CoAgent runtime, dispatch, transport, automation, memory, or
  department-conversation creation logic.
- Before deciding whether to use Codex app-server directly or keep a file/CLI
  transport loop.
- Before implementing durable task states, event logs, or standing orders.
- Before the third learning pass and design discussion with the user.
