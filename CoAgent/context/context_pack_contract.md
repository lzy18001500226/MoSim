# CoAgent Context Pack Contract V1

Date: 2026-05-28

Status: design baseline for `COAGENT-DESIGN-08`.

## Purpose

Context packs are the startup state for dedicated long-running task
conversations. They prevent two failure modes:

- a new conversation starts without enough history and drifts,
- a new conversation receives too much transcript and loses reliability.

## Required Sections

Every dedicated task context pack should contain:

```text
1. Task identity
2. Goal stack
3. Owner and role
4. Definition of done
5. Non-goals
6. Read scope
7. Write scope
8. Worktree binding, if any
9. Current state and recent checkpoints
10. Required evidence
11. Relevant decisions
12. Risks and assumptions
13. Appetite and circuit breaker
14. Escalation conditions
15. Forbidden actions
16. Review and acceptance gate
17. Expected output / result-packet path
18. Retrieval hints and source paths
```

## Goal Stack Section

The context pack must distinguish:

```text
project_goal:
phase_or_strategy_objective:
canonical_task_goal:
conversation_objective:
subagent_objective: optional
```

Only `canonical_task_goal` is the official durable task objective. The
conversation objective is a scoped execution order.

## Worktree Section

If the task runs in a Codex App worktree or Git worktree, the context pack must
include:

```text
worktree_path:
branch_or_base:
write_scope:
merge_owner:
review_gate:
close_condition:
```

If no separate worktree is used, state that explicitly:

```text
worktree: none; task edits run in the project main workspace
```

A worker must not infer write permission from the existence of a worktree. The
task packet and context pack write scope still control what may change.

## Context Budget

Default guidance:

| Size | Meaning |
|---|---|
| under 8k chars | preferred |
| 8k-14k chars | acceptable for complex tasks |
| 14k-22k chars | warning; justify why context is large |
| over 22k chars | fail by default; split into required brief plus evidence index |

The exact budget may vary by task, but any large pack must include why the
extra context is necessary.

## Required Content Rules

Use direct text for:

- task objective,
- stop condition,
- acceptance criteria,
- current blocker,
- recent user decision that changes behavior,
- short evidence summary.

Use paths or retrieval hints for:

- long logs,
- source files,
- audit records,
- prior result packets,
- external reference indexes,
- broad docs.

## Forbidden Content

Do not include:

- raw full chat transcript,
- private Codex App SQLite/JSONL data,
- account cache, launcher cache, browser profile, or session cookie content,
- tokens, API keys, SSH keys, credentials, or license files,
- unbounded source dumps,
- unrelated previous tasks,
- speculative memory not tied to a source path,
- personal data outside the project boundary.

## Evidence Handling

Evidence in a context pack should be:

- source-linked,
- short,
- labeled as accepted, pending, rejected, or unknown,
- enough to orient the worker,
- not a substitute for opening the source path when precision matters.

## Review Handling

The context pack must tell the worker how the result will be reviewed.

Required review fields:

```text
review_required:
review_owner:
acceptance_state_values:
review_status_values:
evidence_required_for_acceptance:
known_human_review_points:
```

If review ownership is unknown, the task should not be dispatched as a normal
execution task. Mark it `review_required`, `disordered_task`, or
`input_required` until DispatchCenter records the review gate.

## Freshness Rule

A context pack is stale when:

- the canonical task goal changed,
- owner changed,
- write scope changed,
- a new blocker or user decision appeared,
- result packet was already returned,
- evidence paths no longer exist.

Stale packs must be regenerated or amended before dispatch.

## Failure Rule

If the context pack cannot express the task compactly, the task should not be
sent for execution. Mark it:

- `disordered_task` when objective/scope/owner is unclear,
- `complex_task` when discovery is needed before execution,
- `input_required` when user/domain input is required,
- `blocked` when required external state is unavailable.
