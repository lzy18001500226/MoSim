# External Learning Index

> Compact index for recurring audits of external docs, skills, sub-agent
> catalogs, and workflow-runtime references. Use this file to decide what to
> re-read after repeated project failures or new tool imports.

## Purpose

External learning is used to improve this project's local workflows, not to
adopt third-party runtimes wholesale. Each audit must end in one of two states:

```text
patch: a project rule, workflow, skill, or index was improved
no_patch: sources were checked and no project change was justified
```

## Source Families

| Source family | Local path / reference | Useful patterns | Rejected patterns | Last audited | Next trigger |
|---|---|---|---|---|---|
| Project-wide external repo index | `CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md`, `References/` | stable entry point for all external repos, family classification, first-read routing | ad-hoc raw tree scanning as the default entry point | 2026-05-26 | any new repo import or new learning thread |
| CoAgent learning strategy | `CoAgent/docs/research/LEARNING_STRATEGY.md` | adopt/adapt/portable/reject taxonomy, context-degradation rule, source-family audit contract | treating Hermes as the only source of architecture ideas | 2026-05-27 | any CoAgent architecture or new long-task conversation design |
| Anthropic Engineering / Claude engineering articles | `https://www.anthropic.com/engineering` | context engineering, multi-agent research systems, long-running harnesses, review/safety loops | treating article guidance as executable API documentation | 2026-05-27 partial | context-pack, memory, long-running-agent, or multi-agent failure |
| Anthropic SDK beta resources | `References/Agent/anthropic-sdk-python/src/anthropic/resources/beta` | first-class agents, sessions, threads, memory stores, skills, environments, files, vaults, and webhooks | importing SDK runtime assumptions into CoAgent without local proof | 2026-05-27 partial | CoAgent protocol, memory, session, skill, or vault design |
| Hermes / Hermes Desktop | `References/Agent/hermes-agent`, `References/Agent/hermes-desktop` | context-engine lifecycle, memory manager, scheduler locks, guardrails, platform adapters, UI/runtime split | importing Hermes wholesale or rebuilding TUI/Desktop inside MoSim | 2026-05-27 partial | scheduler, memory provider, transport adapter, or doctor/recovery work |
| Codex source | `References/Agent/codex` | app-server thread/turn/item/goal/MCP primitives, thread-state lifecycle, doctor reports, thread-spawn graph | mutating private Codex App storage as durable project state | 2026-05-27 partial | direct app-server integration, thread graph, or transport design |
| Local agent reference projects | `References/Agent/` | durable runtime, group agents, planner/executor, coding-agent, workflow, graph, retrieval, and safety patterns | importing third-party frameworks wholesale | pending | architecture learning round or new framework import |
| Local agent references | `References/Agent/`, routed through `Docs/Index/agent_project_classification.md` | runtimes, orchestrators, workflow state, context packs, procedural memory, verification prompts, skill packaging, role/task shaping | copying provider-specific configs or credentials | pending | skill/workflow/context failure |
| Codex / OpenAI docs | official docs when needed; `Docs/Index/codex_app_session_research.md` | skills, durable goals, config limits, Codex App / VSCode / WSL session boundaries, long-running agent behavior | unverified config keys, provider assumptions, live bidirectional session sync as a dependency | 2026-05-26 | Codex Config/tool behavior changes or agent runtime issue |
| Claude Code docs | official docs when needed | sub-agent role separation, memory, hooks, reviewer patterns | copying Claude-specific config syntax into Codex without verification | 2026-05-21 | recurring sub-agent lifecycle failure |
| `awesome-codex-skills` | `References/Agent/awesome-codex-skills` | planning, review, CI fix, issue triage, small task workflows | unrelated app/UI workflows as project requirements | 2026-05-21 | new workflow failure or missing skill pattern |
| `awesome-codex-subagents` | `References/Agent/awesome-codex-subagents` | reviewer, task-distributor, meta-orchestration, research roles | generic agents without project-specific scope/evidence contracts | 2026-05-21 | agent role design gap |
| `superpowers` | `References/Agent/superpowers` | verification-before-completion, parallel dispatch, code review handoff | endless loop/self-driving patterns without user-approved scope | 2026-05-21 | completion/review quality failure |
| OKWinds repos | `Docs/Skills/okwinds/*` | WAL, task graph, evidence chain, capability coverage, doctor checks | hosted/runtime dependencies, UI/TUI products, unrelated SDK services | 2026-05-21 | ledger/WAL/recovery weakness |

## Recurring Audit Contract

Before starting a recurring audit, add or update a ledger row with:

```text
task_id:
trigger:
source_slice:
read_scope:
write_scope:
stop_condition:
expected_output:
```

Required output:

```text
source_to_doc_coverage:
adopt:
reject:
unknowns:
patch_or_no_patch:
review_result:
next_trigger:
```

Durable changes go to `Docs/Workflows/agent_orchestration.md`, `Docs/Workflows/agent_task_ledger.md`,
`Docs/Index/workflow_index.md`, or the relevant project-local skill. Keep
`AGENTS.md` policy-level only.

Do not import third-party execution runtimes, global agent configs, provider
configs, or unrelated UI/tool products unless the user explicitly approves
that specific integration. The reusable output is the project-local rule,
workflow, skill, checklist, or index entry.

Before any new external-repo learning thread starts, classify the target repo
through `CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md`. If the repo is not listed there
yet, update the index first.

For CoAgent architecture learning, use `CoAgent/docs/research/LEARNING_STRATEGY.md` as the
primary contract. The audit must explicitly distinguish MoSim-ready ideas from
portable-only ideas that should be kept for future projects but not implemented
in this repository now.
