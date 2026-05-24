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
| Codex / OpenAI docs | official docs when needed | skills, durable goals, config limits, long-running agent behavior | unverified config keys or provider assumptions | 2026-05-21 | Codex config/tool behavior changes or agent runtime issue |
| Claude Code docs | official docs when needed | sub-agent role separation, memory, hooks, reviewer patterns | copying Claude-specific config syntax into Codex without verification | 2026-05-21 | recurring sub-agent lifecycle failure |
| `awesome-codex-skills` | `Docs/Skills/Agent/awesome-codex-skills` | planning, review, CI fix, issue triage, small task workflows | unrelated app/UI workflows as project requirements | 2026-05-21 | new workflow failure or missing skill pattern |
| `awesome-codex-subagents` | `Docs/Skills/Agent/awesome-codex-subagents` | reviewer, task-distributor, meta-orchestration, research roles | generic agents without project-specific scope/evidence contracts | 2026-05-21 | agent role design gap |
| `superpowers` | `Docs/Skills/Agent/superpowers` | verification-before-completion, parallel dispatch, code review handoff | endless loop/self-driving patterns without user-approved scope | 2026-05-21 | completion/review quality failure |
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
