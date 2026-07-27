# CoAgent Three-Round Study and Discussion Draft

> Status: discussion draft. This file is not an implementation approval.
> Current rule: finish three learning rounds and three document-optimization
> rounds, then discuss the architecture philosophy with the user before adding
> more CoAgent runtime features.

## Why This Draft Exists

The previous CoAgent work moved too quickly from source reading into
implementation. That creates two risks:

1. We may encode the wrong architecture before the design philosophy is clear.
2. We may copy surface patterns from external projects instead of extracting the
   underlying operating principles.

This draft resets the order:

```text
learn three rounds
  -> optimize the summary three rounds
  -> discuss design philosophy
  -> only then resume implementation
```

## Current Correction

Implementation is paused for this topic.

Existing files under `CoAgent/` are current evidence and prototypes, not a final
architecture. In particular, task packets, result packets, dispatch helpers,
knowledge indexes, doctor checks, and transport experiments remain useful, but
the next work should first decide whether their philosophy and boundaries are
right.

## Learning Round 1: Official Principles and Resource Boundaries

### Sources

Local:

- `References/Agent/anthropic-sdk-python/src/anthropic/resources/beta`
- `References/Agent/Agent-Skills-for-Context-Engineering`
- `CoAgent/learning/audits/2026-05-27_context_pack_and_agent_resource_round1.md`
- `CoAgent/learning/audits/2026-05-27_context_evaluation_harness_round3.md`

Official web references checked on 2026-05-27:

- `https://www.anthropic.com/engineering`
- `https://www.anthropic.com/engineering/built-multi-agent-research-system`
- `https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents`
- `https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents`
- `https://www.anthropic.com/engineering/harness-design-long-running-apps`
- `https://www.anthropic.com/engineering/managed-agents`
- `https://www.anthropic.com/engineering/building-effective-agents`

### Lessons

- Context is a finite engineering resource. Raw chat history is evidence, not
  automatically good operating context.
- Long-running work needs durable state outside the model context window.
- Session/event history, harness logic, sandbox/tools, memory, and credentials
  should be separated even if MoSim implements them with local files first.
- Multi-agent systems are useful when work is broad, high value, and naturally
  parallel. Coding tasks often have tighter dependencies, so parallelism needs a
  clear task graph and review boundary.
- Long-horizon agent work benefits from structured handoff artifacts and
  evaluator/reviewer stages. A worker's output is not accepted just because it
  was produced.

### MoSim Interpretation

- CoAgent should not treat Codex App, VSCode Codex, or hidden subagents as the
  durable source of truth.
- The durable source should be project-owned: task packets, result packets,
  event logs, status boards, context packs, and source-linked knowledge.
- Context packs should be a startup interface for long tasks, not a dumping
  ground for all prior messages.
- Human review is a workflow state, not an afterthought.

## Learning Round 2: Product Runtimes and Coding Agents

### Sources

Local:

- `References/Agent/hermes-agent`
- `References/Agent/hermes-desktop`
- `References/Agent/codex`
- `References/Agent/openclaw`
- `References/Agent/OpenHands`
- `References/Agent/claw-code`
- `References/Agent/CowAgent`
- `CoAgent/learning/audits/2026-05-27_hermes_codex_runtime_boundaries_round2.md`
- `CoAgent/learning/audits/2026-05-27_coding_agents_round5.md`
- `CoAgent/learning/audits/2026-05-27_local_runtime_architecture_round9.md`
- `CoAgent/docs/architecture/local_runtime_design_matrix.md`

### Lessons

- Hermes is valuable mainly for runtime philosophy: gateway, scheduler, memory,
  skill runtime, hook chain, doctor/recovery, and UI/runtime split.
- Codex is valuable mainly for boundaries: thread state, rollout/event traces,
  app-server separation, sandbox/exec policy, skills, and graph-like thread
  relationships.
- Coding-agent projects reinforce that user surface, event store, sandbox,
  settings/secrets, task flow, and reports must be explicit boundaries.
- Directly mutating private UI/client databases is fragile. Project state should
  survive even if a client UI changes.

### MoSim Interpretation

- Codex App should remain the visual front end, not the database of record.
- CoAgent should own the control plane. Codex conversations are execution and
  review surfaces.
- Hermes should not be imported wholesale. The useful parts are interface
  shapes and failure modes.
- Any future transport layer should be replaceable: today it may use Codex CLI
  resume paths; later it may use a supported app-server or another adapter.
- OpenClaw is valuable for boundaries around gateway ownership, session
  lanes, task flow, standing orders, hooks, memory, and trusted-operator
  security posture. The useful part is not the social-channel surface; it is
  the explicit separation of control plane, session state, hooks, queues, and
  review.
- LangGraph is valuable for durable state thinking: checkpoints, thread ids,
  pending writes, interrupts, and conformance tests. It should inform
  CoAgent's task/event schema, not replace the current local runtime.

## Learning Round 3: Frameworks, Workflow Runtimes, and Knowledge Systems

### Sources

Local:

- `References/Agent/langgraph`
- `References/Agent/crewAI`
- `References/Agent/MetaGPT`
- `References/Agent/autogen`
- `References/Agent/ag2`
- `References/Agent/camel`
- `References/Agent/llama-agents`
- `References/Agent/temporal`
- `References/Agent/TaskWeaver`
- `References/Agent/OpenSpec`
- `References/Agent/okwinds`
- `References/Agent/haystack`
- `References/Agent/langchain`
- `CoAgent/learning/audits/2026-05-27_multi_agent_frameworks_round4.md`
- `CoAgent/learning/audits/2026-05-27_workflow_runtimes_round6.md`
- `CoAgent/learning/audits/2026-05-27_knowledge_search_round7.md`

### Lessons

- Strong systems keep deterministic workflow control outside autonomous worker
  chats.
- Role names are not architecture. A department only matters when it has owner,
  scope, allowed tools, stop condition, evidence contract, and review state.
- Workflow state needs event history plus current mutable state. A queue alone
  is not enough for recovery.
- Knowledge systems should retrieve with provenance. Retrieval snippets are not
  instructions unless the current task packet or user message makes them so.
- Large frameworks are good reference material, but importing them as the core
  runtime would hide MoSim-specific safety and tool boundaries.

### MoSim Interpretation

- CoAgent should be a local, file-first, project-owned control plane, not a
  generic multi-agent framework deployment.
- Permanent departments should be few. Temporary long-task conversations should
  be created only when the task needs high-context continuity.
- Git/DevOps is a valid durable department because the Git state can be huge,
  slow, and hazardous.
- Research and engineering can often be task-specific rather than permanent
  departments, unless their queues become large enough to justify permanence.

## Summary Optimization Round 1: Raw Lessons

The raw cross-source lessons are:

1. Preserve state outside model context.
2. Separate planning, execution, memory, transport, sandbox/tools, and review.
3. Use visible conversations as surfaces, not hidden authoritative state.
4. Prefer bounded worker packets over free-form peer-agent chat.
5. Keep source provenance for every learned claim.
6. Add autonomy only where task value justifies cost and risk.
7. Human review and security boundaries must be modeled as state transitions.

## Summary Optimization Round 2: MoSim Design Principles

Recommended principles for discussion:

1. CoAgent is a control plane, not a chat collection.
2. The user-facing main conversation and DispatchCenter should be logically
   separate, even if initially operated by the same assistant.
3. Department conversations are durable only when backed by task ledger,
   context pack, result packet, and recovery path.
4. Short-lived subagents remain useful for bounded reading/review, but not for
   durable Git, testing, secretary, or safety queues.
5. Long-running task conversations are created per mission-level task, such as
   PX4 log parameter identification, not for every small command.
6. Memory is not one thing:
   - raw transcripts are evidence,
   - task packets are active state,
   - result packets are completion evidence,
   - summaries are recovery hints,
   - indexes route future lookup,
   - user-approved docs become operating rules.
7. Automation must be conservative: lock, scope, timeout, review gate, then
   execution.
8. Skills are selectively loaded procedures; hooks and policy are hard
   enforcement; memory/search is evidence; MCP/tools are callable capability
   surfaces. These categories should not be blurred.
9. A visible department conversation is only justified when it has a durable
   responsibility, task-state contract, result-packet contract, and review
   boundary.
10. A dedicated task conversation is a mission-level working surface, not a
    new department.

## Summary Optimization Round 3: Decisions To Discuss Before Implementation

These decisions should be discussed before adding more runtime features:

| Decision | Recommended Default | Why |
|---|---|---|
| Is CoAgent primarily a framework or MoSim-local control plane? | MoSim-local first, portable by clean boundaries | Avoid overbuilding before it works in the real project. |
| Should PMO and DispatchCenter be separate conversations? | Logically separate; physical split only when useful | Prevent user interaction from becoming buried in queue mechanics. |
| Minimum permanent departments? | PMO/user interaction, DispatchCenter/runtime, DevOps/Git, Verification/Test, Documentation Secretary, Security/Compliance | Fewer durable departments reduces communication errors. |
| Should Research and Engineering be permanent? | Usually task-specific at first | They can become permanent only when queue volume proves it. |
| When to create a dedicated task conversation? | High-context, multi-turn, independently reviewable work with a result packet | Prevent conversation explosion. |
| Should Hermes runtime be imported? | No | Extract philosophy and interfaces; keep MoSim runtime small. |
| Should Codex App private data be edited directly? | No | Use it as frontend. Keep project-owned state recoverable. |
| Should vector/RAG frameworks be added now? | No | Add only after deterministic local search fails on real tasks. |
| Should unattended automation run now? | Only dry-run or guarded task creation | Real autonomous mutation needs more evidence. |

## Proposed Operating Philosophy

CoAgent should follow this model:

```text
User-facing PMO conversation
  -> clarifies goal, tradeoffs, and human decisions

DispatchCenter / runtime
  -> owns task graph, queues, context packs, result packets, state transitions

Department or dedicated task conversation
  -> executes one bounded scope with a clear packet and stop condition

Verifier / Secretary / Security / DevOps lanes
  -> validate, record, guard, and integrate results

Knowledge layer
  -> stores source-linked summaries and retrieves only what the next task needs
```

This is not "many agents talking to each other." It is a disciplined workflow
system where agents are replaceable workers and project state is the durable
asset.

## Implementation Freeze List

Do not continue these until after user discussion:

- new transport features,
- unattended automation execution,
- new department creation,
- workflow replay implementation,
- structured memory schema,
- vector/RAG dependency import,
- direct Codex App/App-server integration,
- Hermes runtime migration.

Allowed before discussion:

- read-only source review,
- this summary draft,
- documentation corrections that clarify the study-first process,
- narrow status updates that prevent future confusion.

## Open Questions For User Discussion

1. Should PMO and DispatchCenter be two visible conversations immediately, or
   just two logical roles until the workflow stabilizes?
2. Is the proposed minimum department set acceptable, or should Engineering be
   a permanent department from day one?
3. For Git, do you want DevOps to own only staging/commit/push, or also file
   classification and large-tree cleanup planning?
4. For long scientific tasks such as PX4 parameter identification, should they
   be dedicated task conversations under Engineering, or direct child tasks
   under PMO?
5. What level of automation is acceptable before we have several successful
   human-reviewed task lifecycles?
6. Should the implementation already made in `CoAgent/` be treated as a
   prototype to refine, or should any part be reverted before the next phase?

## Discussion Entry Point

The next conversation should not start with code. It should start with:

```text
Review this draft's operating philosophy and answer the open questions.
Then choose the minimal CoAgent implementation sequence.
```

Use `CoAgent/docs/decisions/coagent_design_discussion_packet.md` as the concise
discussion packet for that conversation. It compresses the three learning
rounds into department boundaries, communication protocol, Skill/Hook/MCP
separation, state vocabulary, the user confirmation checklist, and the next
implementation sequence.

## Protocol Convergence Addendum

Additional official-source check:

- `CoAgent/learning/audits/2026-05-27_official_protocol_convergence_round11.md`

The main correction from this pass is that CoAgent should treat simple replies,
durable tasks, artifacts, and interrupted states as separate concepts.

Implications for the post-approval vocabulary discussion:

1. not every department interaction needs durable task overhead;
2. long-running work must have a task identity, status, artifacts/evidence,
   and result packet;
3. `input_required` and `auth_required` should be distinct from ordinary
   failure or completion;
4. receiving departments should get filtered context packs, not raw full chat
   history;
5. append-only state and readable packets should come before app-server,
   streaming, or remote-agent protocol integration.

This does not change the current freeze gate. It strengthens the evidence for
starting post-approval work with task-state and event vocabulary.
