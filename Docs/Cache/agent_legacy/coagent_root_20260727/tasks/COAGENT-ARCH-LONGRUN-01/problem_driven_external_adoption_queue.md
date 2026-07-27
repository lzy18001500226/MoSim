# COAGENT-ARCH-LONGRUN-01 Problem-Driven External Adoption Queue

Date: 2026-05-30
Status: design draft

## Purpose

CoAgent has many local reference projects and vendor articles. The risk is not
lack of material; the risk is unbounded learning that produces summaries
without changing the system.

This document defines a problem-driven adoption queue for external ideas.
External Intelligence should use this queue to map sources to current CoAgent
problems, then either adopt, adapt, reject, or defer them.

Structured proposal contract:

```text
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/external_adoption_proposal_contract.md
```

The queue decides what deserves attention. The proposal contract defines how a
specific idea is accepted, rejected, deferred, validated, and promoted.

## Queue Rule

No external-learning item enters the queue without a current CoAgent problem.

Required intake:

```text
problem_id
source_family
source_path_or_url
pattern
why_it_might_help
risk_if_copied_blindly
proposed_decision
verification_method
owner
next_trigger
```

## Decision States

| State | Meaning |
|---|---|
| `adopt_now` | fits current CoAgent problem and can become a design/protocol/backlog item |
| `adapt_later` | useful but needs proof, validator, or approved implementation phase |
| `portable_only` | not needed for MoSim now, useful if CoAgent moves to another project |
| `reject_now` | inappropriate for current safety, complexity, license, or task needs |
| `unknown_until_probe` | requires a bounded local experiment before decision |

## Current Problem-To-Source Queue

| Queue ID | Problem | Source family | Candidate pattern | Current decision | Required output |
|---|---|---|---|---|---|
| EXT-001 | cross-conversation communication fails or times out | Codex source, Hermes gateway, A2A-style artifacts | packet-first transport, session metadata repair, explicit result artifacts | adopt_now_design_only | transport hardening backlog and blocker packets |
| EXT-002 | new conversations need enough context without transcript bloat | Anthropic context engineering, Hermes memory, context-engineering kits | context packs, context deltas, filtered handoff payload | adopt_now | context lifecycle schema and context delta checker |
| EXT-003 | handoff routing is too prose-driven | OpenAI handoffs, Semantic Kernel orchestration, ADK workflows | typed handoff modes and workflow graphs | adopt_now | handoff/workflow validators backlog |
| EXT-004 | graph/state is needed but full runtime import may overfit | LangGraph, Temporal, TaskWeaver, OpenSpec | event log, checkpoints, interrupts, replayable graph ideas | adapt_later | read-only graph/packet validators before engine adoption |
| EXT-005 | human intervention must be clear and deduped | OpenClaw, Hermes, incident/SRE practices | blocker notification, dedupe key, resume packet | adopt_now_design_only | blocker templates and operator-experience policy |
| EXT-006 | many agents can create fake parallelism | Kimi Agent Swarm, Anthropic multi-agent research, enterprise WIP limits | true-parallelism metrics, critical path tracking, small team size | adopt_now_design_only | operating metrics snapshot backlog |
| EXT-007 | worktree isolation can help but creates merge debt | Claude Code worktrees, Codex worktree features, enterprise release practice | worktree binding, integration worktree, arena constraints | adapt_later | validator before automatic worktree creation |
| EXT-008 | skills and hooks are confused | Codex/Claude skills and hooks, Hermes hooks | skills are selective context; hooks are hard gates | adopt_now | capability templates and hook policy docs |
| EXT-009 | plugins could package skills/hooks/MCP but are unstable | Codex plugins, Claude plugins, local plugin repos | plugin as capability package after protocol stability | reject_now_for_runtime | revisit after protocol validators and one proof pass |
| EXT-010 | agent swarms or group chats may look powerful but become unsafe | AutoGen/AG2/CrewAI/CAMEL/MetaGPT/Kimi | group/team orchestration, role specialization | adapt_later | only use through task-team packet protocol, not raw peer chat |
| EXT-011 | evidence/trace must be inspectable | OpenAI tracing/evals, LangSmith-like tooling, mlflow/promptfoo | trace eval rubric and artifact manifests | adopt_now_design_only | trace eval and artifact manifest validators |
| EXT-012 | long-term self-improvement can become broad research loop | vendor engineering blogs, reference corpus | scheduled learning with adoption proposals | adapt_later | adoption queue plus no-scheduler gate |

## Source Reading Contract

For every queue item, External Intelligence must return:

```text
source_slice:
read_files_or_urls:
problem_id:
architecture_claim:
evidence_from_source:
fit_for_coagent:
risk:
decision:
required_patch_or_no_patch:
verification:
next_trigger:
```

If the source is local code, cite file paths and specific modules. If the
source is a web/vendor article, cite the URL and summarize only the relevant
pattern.

## Adoption Gate

An idea may be promoted only if:

1. it maps to a problem in `architecture_problem_matrix.md`;
2. it reduces a concrete failure mode or improves a proof requirement;
3. Safety can state the risk boundary;
4. Verification can state how to test or review it;
5. Dispatch can put it into a task, protocol, validator, or backlog item.

## Rejection Gate

Reject or defer ideas when:

- they require direct API integration with unreviewed third-party runtime;
- they move durable state out of project-owned files before a proof exists;
- they depend on hidden group chat as source of truth;
- they require credentials, cloud services, or external automation not approved;
- they add permanent departments before queue pressure proves the need;
- they solve a generic agent problem that is not a current CoAgent bottleneck.

## Evidence Levels

| Level | Evidence |
|---|---|
| `source_seen` | source read and cited |
| `mapped` | linked to a CoAgent problem |
| `designed` | design document or protocol updated |
| `templated` | template or schema draft exists |
| `validated` | check or fixture proves expected behavior |
| `proved_in_loop` | minimal closed-loop proof exercised it |
| `promoted` | stable lesson added to skill/hook/workflow/doctor/backlog |

Do not claim an idea is adopted beyond the evidence level it has reached.

## Current Priority Order

1. EXT-003 handoff/workflow objects.
2. EXT-002 context lifecycle and delta acknowledgement.
3. EXT-001 transport timeout/blocker reliability.
4. EXT-006 operating metrics and fake-parallelism detection.
5. EXT-011 trace eval and artifact manifest validators.
6. EXT-007 worktree binding validator.
7. EXT-012 adoption queue mechanics.

## Current Consequence

The next external-learning work should not be "study all projects again".
It should be:

```text
choose one open problem
  -> read the smallest relevant source slice
  -> produce one adoption/rejection decision
  -> update one CoAgent artifact or backlog item
```

This keeps CoAgent evolvable without turning external learning into a second
main task.

## Proposal Contract Consequence

For any queue item that is being moved beyond `mapped`, create or update an
adoption proposal with:

- one primary `problem_id`;
- bounded `source_slice`;
- explicit `risk_if_copied_blindly`;
- `license_security_notes`;
- `decision`;
- `evidence_level`;
- `promotion_target`;
- `verification_method`;
- `owner` and `review_owner`;
- `next_trigger`.

Accepted ideas may update docs, protocols, skills, hooks, doctor checks, or
backlog only through that proposal record. Rejected ideas must keep a reason
and reopen trigger so future conversations do not reargue them from memory.
