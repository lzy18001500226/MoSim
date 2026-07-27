# Round 1 Audit: Context Packs and Agent Resource Boundaries

## source_slice

- `CoAgent/docs/research/LEARNING_STRATEGY.md`
- `Docs/Workflows/agent_orchestration.md`
- `References/Agent/anthropic-sdk-python/src/anthropic/resources/beta`
- Anthropic Engineering article queue recorded in `CoAgent/docs/research/LEARNING_STRATEGY.md`
- `Docs/Skills/Agent/Agent-Skills-for-Context-Engineering`

## read_files_or_urls

- `References/Agent/anthropic-sdk-python/src/anthropic/resources/beta/agents/agents.py`
- `References/Agent/anthropic-sdk-python/src/anthropic/resources/beta/sessions/sessions.py`
- `References/Agent/anthropic-sdk-python/src/anthropic/resources/beta/sessions/threads/threads.py`
- `References/Agent/anthropic-sdk-python/src/anthropic/resources/beta/memory_stores/memory_stores.py`
- `References/Agent/anthropic-sdk-python/src/anthropic/resources/beta/skills/skills.py`
- `References/Agent/anthropic-sdk-python/src/anthropic/resources/beta/environments/environments.py`
- `References/Agent/anthropic-sdk-python/src/anthropic/resources/beta/vaults/vaults.py`
- `https://www.anthropic.com/engineering`
- `https://www.anthropic.com/engineering/multi-agent-research-system`
- `https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents`
- `https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents`

## architecture_claims

1. Long-running agent work needs a stable boundary between reasoning state and
   durable task state. Chat transcript alone is not that boundary.
2. Agents, sessions, threads, memory stores, skills, environments, and vaults
   should be treated as separate resource classes even when CoAgent implements
   them with simpler project files.
3. Context should be assembled as an intentional startup artifact for each
   dedicated task conversation. Raw accumulated chat should be treated as
   evidence, not as the operating context.
4. Multi-agent work needs orchestrator-owned routing, task packets, result
   packets, and review points. Direct peer-to-peer hidden-agent communication
   is not a reliable project control plane.
5. Tool and credential boundaries must remain explicit. Vault/credential
   concepts are useful, but MoSim should not implement credential storage in
   project files.

## adopt_now

- Add a CoAgent context-pack generator that turns runtime task state into a
  compact Markdown startup packet for a dedicated visible task conversation.
- Keep task packet and result packet as the durable handoff contract.
- Keep memory as project-owned knowledge index and run summaries, not as raw
  hidden chat state.
- Record official article URLs as learning sources but verify any executable
  behavior locally before implementation.

## adapt_later

- First-class resource registry for sessions, threads, skills, memory stores,
  and environments. Current files approximate this, but the registry is not yet
  normalized.
- Stronger memory-store model with structured facts, decisions, and evidence
  provenance rather than keyword-only search.
- Standard task conversation bootstrap that creates the runtime task, context
  pack, visible thread dispatch, and result reconciliation in one controlled
  flow.

## portable_only

- A generic credential/vault abstraction may be useful when CoAgent is reused
  in other projects, but MoSim should keep credentials outside tracked project
  files.
- A generic hosted multi-tenant session service may be useful outside MoSim, but
  this project should remain file/runtime-first and Codex App-fronted.

## reject

- Do not import Anthropic SDK beta resource assumptions as CoAgent API contracts.
  They are useful design references, not local runtime guarantees.
- Do not create a custom frontend now. Codex App remains the visible UI unless
  it becomes the blocker.
- Do not put the full `References/Agent` tree into the daily knowledge index.
  It is too large and should be audited in bounded source slices.

## unknowns

- Exact optimal context size for a dedicated task conversation remains unknown.
  Current rule is qualitative: compact enough to stay task-focused, complete
  enough to avoid relying on chat memory.
- Official article details may change; use the URL queue as a refresh target
  before treating a claim as current.
- The best schema for structured long-term memory is still open.

## required_patch

- Add `CoAgent/context/context_pack.py`.
- Add `CoAgent/context/README.md`.
- Add this audit record.
- Add context-pack generator references to CoAgent component and migration docs.

## verification

Required local checks:

```bash
python3 CoAgent/context/context_pack.py --task-id <id>
python3 CoAgent/knowledge/knowledge_indexer.py build
python3 CoAgent/knowledge/knowledge_indexer.py search --query context_pack --limit 10
python3 CoAgent/hooks/preflight.py
python3 Scripts/reference/check_reference_index.py --strict
```

## next_trigger

Run the next audit when:

- creating a dedicated task conversation for PX4 log parameter identification,
- revising CoAgent memory/search beyond keyword indexing,
- adding a session/thread registry,
- or reading the Anthropic Engineering articles in detail for implementable
  context-engineering rules.
