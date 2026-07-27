# COAGENT-ARCH-LONGRUN-01 Self-Evolution Protocol

Date: 2026-05-30
Status: phase 2 draft

## Purpose

Define how CoAgent learns from model-vendor articles, open-source agent
projects, and large-company management practice without drifting into broad,
unusable summaries.

## Principle

```text
problem first
source second
adoption decision third
implementation backlog last
```

## Source Classes

| Source | Use |
|---|---|
| model-vendor engineering docs | first-principles agent patterns, safety, context, tools |
| open-source agent projects | implementation patterns and UX ideas |
| enterprise management practice | ownership, handoff, review, metrics, incident response |
| local project experience | concrete failures, corrections, and MoSim-specific constraints |

## Intake Rule

ExternalIntelligenceAgent may open a research item only if it maps to one of:

- an open architecture problem;
- a failed CoAgent workflow;
- a user-requested improvement;
- a tool/runtime blocker;
- a design gap in the current stress tests.

No open-ended "summarize all repos" task should run without a problem matrix.

Current task-level queue:

```text
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/problem_driven_external_adoption_queue.md
```

This queue is the required route for applying vendor/open-source ideas to the
current architecture task.

Current task-level proposal contract:

```text
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/external_adoption_proposal_contract.md
```

This contract is the required route before any external idea is treated as
accepted, rejected, deferred, validated, or promoted.

## Adoption Proposal Contract

Each external idea must follow the structured contract above. At minimum it
needs:

- source path or URL;
- problem it addresses;
- pattern summary;
- why it fits or does not fit CoAgent;
- risk;
- implementation cost;
- security/licensing concerns;
- decision state;
- owner and review owner;
- verification method;
- promotion or rejection target;
- proposed artifact type:
  - design note;
  - protocol rule;
  - skill;
  - hook;
  - doctor check;
  - runtime feature;
  - tool/MCP capability;
  - rejected idea archive.

Evidence level must be explicit:

- `source_seen`;
- `mapped`;
- `designed`;
- `templated`;
- `validated`;
- `proved_in_loop`;
- `promoted`.

Do not claim an idea is adopted beyond the evidence level it has reached.

## Rejected Ideas

Rejected ideas still matter if they may fit another project.

Record:

- source;
- reason rejected for MoSim/CoAgent now;
- conditions where it may become useful;
- risk if copied blindly.

## Cadence

Design-only cadence:

- daily or on-demand external update scan;
- weekly architecture improvement review;
- incident-triggered targeted research;
- before major CoAgent runtime implementation.

Actual scheduled automation remains gated until separately approved.

## Promotion Gate

KnowledgeSecretaryAgent promotes an idea only after:

- problem mapping exists;
- owner accepts relevance;
- Safety checks risk;
- Verification defines how to evaluate it;
- Dispatch places it in backlog or rejects it.

Raw external project code must not be copied into CoAgent without license,
security, and integration review.

## Current Priority Research Problems

1. Reliable cross-conversation communication and recovery.
2. Context size, freshness, and semantic drift control.
3. Worktree/Git isolation for multi-agent development.
4. Human intervention and notification UX.
5. Tool/MCP capability cards and fallback rules.
6. Agent process metrics and trace evaluation.
7. Dynamic task-team topology selection.

## Current Priority Adoption Queue

For `COAGENT-ARCH-LONGRUN-01`, the priority queue is:

1. `EXT-003`: handoff/workflow objects;
2. `EXT-002`: context lifecycle and delta acknowledgement;
3. `EXT-001`: transport timeout/blocker reliability;
4. `EXT-006`: operating metrics and fake-parallelism detection;
5. `EXT-011`: trace evaluation and artifact manifests;
6. `EXT-007`: worktree binding validator;
7. `EXT-012`: adoption queue mechanics.

External Intelligence should read only the smallest source slice needed for the
current queue item.
