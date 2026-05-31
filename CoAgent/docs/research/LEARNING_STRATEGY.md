# CoAgent Learning Strategy

## Purpose

CoAgent is not a Hermes migration project only.

The objective is to build a MoSim-owned, transferable, long-running
multi-conversation agent architecture by studying high-quality agent systems,
agent skills, official engineering writeups, and SDK/runtime designs.

Every source should produce one of these outcomes:

| Outcome | Meaning |
|---|---|
| adopt_now | Suitable for MoSim and should be implemented or documented in CoAgent now |
| adapt_later | Useful architecture idea, but needs more evidence or a later phase |
| portable_only | Not needed for MoSim now, but valuable if CoAgent is reused in another project |
| reject | Not suitable; record why so the same idea is not repeatedly re-opened |
| unknown | Worth revisiting after missing context, docs, or runtime evidence is available |

## Current Goal

Build CoAgent into a reusable, recoverable, long-running multi-conversation
agent system.

## Current Process Gate

The current CoAgent architecture work is in a discussion-first checkpoint.

Before adding more runtime, dispatch, automation, knowledge, transport, or
workflow-replay features, do the following:

1. study the relevant sources in three learning rounds,
2. optimize the summary/design document in three passes,
3. discuss the design philosophy and department boundaries with the user,
4. only then resume implementation.

Use `CoAgent/docs/research/THREE_ROUND_STUDY_AND_DISCUSSION.md` as the current
discussion draft. Existing CoAgent runtime files are prototypes and evidence;
they are not final approval to continue broad implementation.

The current local-runtime comparison is
`CoAgent/docs/architecture/local_runtime_design_matrix.md`. Treat it as a learning
artifact, not an implementation plan, until the three learning and discussion
passes are complete.

The current synthesis discussion packet is
`CoAgent/docs/decisions/coagent_design_discussion_packet.md`. Use it as the
discussion entry point before adding more runtime features. Its confirmation
checklist is the current implementation freeze gate.

Required learning scope:

- `References/Agent/`
- `References/Agent/`, routed through `Docs/Index/agent_project_classification.md`
- `References/Agent/anthropic-sdk-python/src/anthropic/resources/beta`
- Hermes and Hermes Desktop
- Codex source architecture
- Anthropic Engineering / Claude engineering articles
- official multi-agent, handoff, hook, skill, workflow, and context-engineering
  sources listed in `CoAgent/docs/research/multi_agent_learning_urls.md`
- other high-quality multi-agent, workflow, memory, and context-engineering systems

Deferred but required follow-up study:

- Kimi/Moonshot, Qwen-Agent, and other model-provider agent APIs as model/tool
  surfaces rather than durable control planes.
- OpenMOSS, CrewAI, AG2/AutoGen, MetaGPT, AutoGroq, Squad, and similar
  agent-team systems as organization-design references.
- Technical enterprise operating systems: mission command, RACI, design
  review, ADR, WIP limits, incident command, postmortems, quality gates,
  release management, and organizational memory.
- The follow-up study must focus on communication, routing, recovery,
  authority, review, and how task completion is preserved when department
  boundaries overlap.

Required implementation scope:

- `CoAgent/runtime/`
- `CoAgent/dispatch/`
- `CoAgent/automation/`
- `CoAgent/knowledge/`
- `CoAgent/hooks/`
- `CoAgent/protocol/`
- `CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md`
- `Docs/Workflows/agent_orchestration.md`
- `Docs/Index/external_learning_index.md`

## Architecture Questions To Answer

Each audit must answer these questions before recommending a change:

1. How does this system preserve useful context while avoiding long-context
   degradation?
2. What is the durable state boundary: chat transcript, database, event log,
   task queue, memory store, file tree, or workflow engine?
3. How are tasks decomposed, routed, claimed, checkpointed, reviewed, and
   completed?
4. How are tools, skills, MCPs, shell commands, and external APIs registered and
   constrained?
5. How does the system recover from interruption, stale context, failed tools,
   partial results, or missing credentials?
6. What should be consumed and released as a short-lived worker, and what must
   remain as durable project state?
7. Which design ideas improve MoSim now, and which are only useful for future
   CoAgent reuse in other projects?

## Source Families

| Family | First paths / sources | Main lessons to extract |
|---|---|---|
| Codex source | `References/Agent/codex` | app-server boundary, thread store, rollout/event trace, skills, sandbox, exec policy |
| Hermes | `References/Agent/hermes-agent`, `References/Agent/hermes-desktop` | gateway, scheduler, memory manager, skills runtime, shell hooks, doctor/recovery, UI/runtime split |
| Anthropic SDK beta | `References/Agent/anthropic-sdk-python/src/anthropic/resources/beta` | agents, sessions, threads, memory stores, skills, environments, vaults, webhooks |
| Anthropic Engineering | `https://www.anthropic.com/engineering` and linked agent articles | context engineering, multi-agent research, long-running harness design, safety/review loops |
| Agent reference corpus | `References/Agent`, routed through `Docs/Index/agent_project_classification.md` | runtimes, orchestrators, durable workflow, control planes, compact procedural memory, verification habits, context pack design, prompt/task shaping |
| Multi-agent frameworks | `References/Agent/autogen`, `ag2`, `crewAI`, `camel`, `MetaGPT`, `langgraph`, `llama-agents` | role graphs, planner/executor separation, group chat limits, graph/state-machine patterns |
| Coding agents | `References/Agent/OpenHands`, `openclaw`, `claw-code`, `CowAgent` | repository execution, shell safety, task ownership, tool/runtime boundaries |
| Workflow/runtime systems | `References/Agent/temporal`, `TaskWeaver`, `OpenSpec`, `okwinds` | durable workflows, WAL, replay, state transitions, spec-first execution |
| Knowledge/search systems | `References/Agent/haystack`, `langchain` | retrieval, pipeline composition, memory/index design |

## Initial Anthropic Engineering Queue

Start with these official articles before broader web research:

| Article | URL | Why it matters |
|---|---|---|
| Engineering index | `https://www.anthropic.com/engineering` | current official source list for agent, tool, context, and harness engineering |
| How we built our multi-agent research system | `https://www.anthropic.com/engineering/multi-agent-research-system` | orchestrator-worker pattern, parallel subagents, coordination/evaluation/reliability lessons |
| Effective context engineering for AI agents | `https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents` | context as finite resource, context curation, retrieval and context-pack implications |
| Effective harnesses for long-running agents | `https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents` | incremental progress across context windows and long-horizon harness requirements |
| Scaling Managed Agents: Decoupling the brain from the hands | `https://www.anthropic.com/engineering/managed-agents` | stable interfaces between model reasoning and execution environments |
| Writing effective tools for AI agents | `https://www.anthropic.com/engineering/writing-tools-for-agents` | MCP/tool descriptions, tool selection behavior, tool ergonomics and evaluation |
| Building effective agents | `https://www.anthropic.com/engineering/building-effective-agents` | workflow versus agent distinction and practical agentic system patterns |

These articles are reference material, not API documentation. Any executable
Codex, MCP, or SDK assumption still requires local verification before it is
implemented.

## MoSim Design Commitments

These decisions are currently adopted:

1. Codex App is a frontend and review surface, not the durable state source.
2. The WSL-backed primary conversation remains the main integration surface.
3. Visible department conversations are real collaboration surfaces, not
   internal subagents.
4. Long-running task state belongs in project-owned runtime files, task packets,
   result packets, run summaries, and searchable knowledge indexes.
5. Short-lived workers should be consumed and released after returning
   structured evidence.
6. Dedicated task conversations are appropriate for high-context long tasks
   such as PX4-log-based parameter identification.
7. New task conversations must start from a context pack, not from raw chat
   memory.

## Context Degradation Rule

Longer context is not automatically better.

CoAgent should assume:

- model capability declines as irrelevant context accumulates,
- chat transcripts are recovery evidence but not executable state,
- each long task needs a compact context pack,
- completed worker context should be summarized into durable artifacts, then
  released,
- new conversations must be able to reconstruct required context from project
  files, not from hidden model memory.

The target context pack for a dedicated task conversation should include:

```text
task_id:
parent_goal:
owner_department:
objective:
read_scope:
write_scope:
current_state:
relevant_decisions:
known_blockers:
required_tools:
acceptance:
stop_condition:
result_packet_path:
knowledge_search_queries:
```

## Audit Output Contract

Each learning round must write a compact result using this structure:

```text
source_slice:
read_files_or_urls:
architecture_claims:
adopt_now:
adapt_later:
portable_only:
reject:
unknowns:
required_patch:
verification:
next_trigger:
```

If no durable patch is justified, record `required_patch: no_patch` and the
reason.

## First Learning Rounds

| Round | Source slice | Target output |
|---|---|---|
| 0 | Official multi-agent, context, handoff, hook, skill, and workflow docs | shared vocabulary in `CoAgent/docs/architecture/agent_concept_boundaries.md` |
| 1 | Anthropic Engineering agent/context articles plus Anthropic SDK beta resources | context-pack, session/thread/memory-store lessons, safety/recovery implications |
| 2 | Hermes + Hermes Desktop | gateway, scheduler, memory, hooks, doctor, UI/runtime split comparison |
| 3 | Codex source | thread-store, rollout trace, app-server, skills, execpolicy mapping |
| 4 | Agent skill/operator systems under `References/Agent` | reusable task-shaping, operator-system, hook, plugin, and verification patterns |
| 5 | Multi-agent frameworks under `References/Agent` | graph, role, crew, workflow, and review-loop patterns |
| 6 | Workflow/runtime references such as Temporal, OpenSpec, TaskWeaver, OKWinds | durable state, WAL, replay, and spec-first execution patterns |
| 7 | Current official protocol convergence: OpenAI Agents SDK, A2A, ADK, LangGraph persistence, Anthropic workflow guidance | task/message/artifact/state vocabulary and handoff context-filter lessons |

Audit records live under `CoAgent/learning/audits/`.
Build the structured source-to-architecture index with:

```bash
python3 CoAgent/learning/learning_indexer.py validate --strict
```

## Validation

A learning change is not considered useful unless it is tied to at least one of:

- a `CoAgent/` implementation change,
- a workflow or index update,
- a new or improved context pack template,
- a new runtime/dispatch/automation/knowledge/hook check,
- a documented rejection with evidence.

Minimum recurring checks:

```bash
python3 CoAgent/doctor/coagent_doctor.py
python3 Scripts/reference/check_reference_index.py --strict
python3 CoAgent/hooks/preflight.py
python3 CoAgent/learning/learning_indexer.py validate --strict
python3 CoAgent/knowledge/knowledge_indexer.py build
python3 CoAgent/runtime/mosim_agent_runtime.py status-board --active-only
```
