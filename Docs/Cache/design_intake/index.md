# Design Intake Cache

> Temporary intake area for architecture discussions, context-management
> gaps, and proposed workflow/schema/checker changes before they become
> canonical MoSim or portable CoAgent documents.

Status: cache index, 2026-06-10 CST.

Authority: none. Files in this tree are not workflow authority, project fact,
or dispatch permission until they are reviewed and promoted into a canonical
document, template, schema, checker, skill, or index.

## Purpose

Use this cache when a discussion produces useful design material but the final
landing place is not yet stable.

Typical intake:

- architecture options,
- context-management incidents,
- capability-router gaps,
- repeated rule conflicts,
- candidate schema/checker/template changes,
- proposed documentation cleanup batches.

Current notable intake notes:

| Note | Topic | Status |
|---|---|---|
| `inbox/20260610_capability_resolution_context_gap.md` | Capability discovery, duplicate-skill prevention, `capability-runtime` gap analysis | cache_draft |
| `inbox/20260610_agent_project_operating_layers_and_research_plan.md` | Agent-project operating layers, non-duplicative research goal, proposed subagent plan | cache_draft |

Do not use this cache for current engineering truth, runtime success claims,
MWORKS/ROS2/UE evidence, or visible-thread task results. Those belong in
`Results/`, the PMO board, domain workflows, packets, or reviewed project
documents.

## Directory Roles

| Path | Role |
|---|---|
| `inbox/` | Raw discussion-derived drafts and incident notes. |
| `review_queue/` | Drafts ready for documentation-secretary review, dedup, and landing proposal. |
| `promoted/` | Cache copies or summaries after canonical promotion. |
| `rejected/` | Ideas explicitly rejected or superseded, kept for audit. |

## Draft Header

Every intake note should start with:

```text
Status: cache_draft
Authority: none
Source: PMO discussion | CoAgentOps sync | user correction | research
Target canonical doc: <path or TBD>
Promotion owner: documentation secretary | PMO | CoAgentOps | TBD
Do not treat as workflow authority until promoted.
```

## Promotion States

```text
cache_draft
  -> reviewed_candidate
  -> promoted_to_canonical
  -> superseded
  -> rejected
```

Promotion requires:

1. target canonical document or checker/template is named,
2. duplicate or conflicting rules are identified,
3. host-local MoSim facts are not moved into portable CoAgent core,
4. entry documents are not expanded unless the rule is a hard boundary,
5. PMO/user approval exists when authority or runtime behavior changes.

## Documentation-Secretary Boundary

The documentation-secretary/context-maintenance route may:

- organize this cache,
- deduplicate similar drafts,
- propose landing targets,
- prepare reviewable patches,
- update this index.

It must not:

- silently change PMO authority,
- define product priority,
- accept engineering results,
- turn cache drafts into workflow authority without review,
- move half-formed rules into `AGENTS.md` or
  `Docs/Workflows/new_conversation_context.md`.
