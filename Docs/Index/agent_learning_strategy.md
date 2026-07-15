# Agent Learning Strategy

> Current MoSim strategy for learning from local/open-source agent projects.
> This replaces the legacy implementation strategy for active work.

## 1. Purpose

Use external agent projects to improve MoSim workflows, skills, hooks, indexes,
and verification habits. Do not import a third-party runtime or rebuild an
AgentOS inside MoSim unless the user explicitly approves that implementation.

## 2. First-Read Order

```text
Docs/Index/reference_project_index.md
Docs/Index/external_learning_index.md
Docs/Index/agent_project_classification.md
References/Agent/<relevant family>
```

Search the local mirror before web research when the target project is already
present under `References/`.

## 3. Output Contract

Every learning pass should end with one of:

```text
patch: a MoSim doc, skill, hook, checker, template, or index was improved
no_patch: sources were checked and no project change was justified
blocker: the source is missing, unclear, too large, or needs user approval
```

Useful outputs belong in:

| Output | Location |
|---|---|
| routing/index update | `Docs/Index/` |
| repeatable procedure | `Docs/Workflows/` |
| task-family operating method | `Docs/Skills/` |
| enforceable rule | `Scripts/hooks/`, `Scripts/quality/`, or `Config/` |
| research/cache note | `Docs/Cache/` |

## 4. Adoption Criteria

Adopt only ideas that are:

- relevant to current MoSim execution;
- small enough to verify locally;
- compatible with single-thread operation;
- expressible as a workflow, skill, checker, hook, template, or index;
- not dependent on hidden credentials, hosted services, or private app state.

Reject or defer ideas that require broad runtime replacement, provider-specific
configuration, large vendored frameworks, or multi-thread dispatch mechanics
that the current project has deprecated.

## 5. Completion Check

Before reporting a learning result:

1. Name the source slice inspected.
2. State `patch`, `no_patch`, or `blocker`.
3. If patched, list changed files and run the relevant checker.
4. If no patch, record why no project rule changed.
5. Do not claim engineering/runtime progress from learning alone.
