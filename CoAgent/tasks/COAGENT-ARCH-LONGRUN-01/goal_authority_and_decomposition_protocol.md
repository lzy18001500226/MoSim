# COAGENT-ARCH-LONGRUN-01 Goal Authority And Decomposition Protocol

Date: 2026-05-30
Status: phase 2 design draft

## Purpose

Prevent CoAgent from replacing the user's real objective with a smaller,
easier, or administrative goal.

The trigger for this protocol is the failure mode where a goal like:

```text
sustain at least 10 hours of CoAgent architecture design work
```

is incorrectly rewritten as:

```text
create a 10-hour architecture task
```

The first is a user outcome. The second is only a setup action. This protocol
defines the goal hierarchy, authority boundaries, and drift checks that keep
multi-conversation work aligned with the real task.

## Goal Hierarchy

| Layer | Owner | May Define | May Change | Must Not Do |
|---|---|---|---|---|
| `user_objective` | user | desired end state, constraints, audit expectation | user only | be rewritten for convenience |
| `canonical_task_goal` | MainAgent + DispatchAgent | durable operational statement of the user objective | MainAgent after user-visible decision record | shrink scope without explicit user approval |
| `task_team_goal` | DispatchAgent | how a dynamic task team contributes to the canonical goal | DispatchAgent with review record | become a separate project objective |
| `department_goal` | department conversation | department-specific responsibility for this task | department may propose changes only | override canonical goal |
| `scoped_conversation_objective` | DispatchAgent + slice owner | one slice objective, context, output, stop condition | slice owner may propose re-scope through packet | silently continue after discovering mismatch |
| `subagent_prompt_objective` | parent conversation | one bounded one-shot subquestion | parent conversation | hold durable responsibility |
| `implementation_step_goal` | integration owner | one approved code/docs/check slice | integration owner within approved backlog item | implement gated features without approval |

Only the user objective and canonical task goal describe success for the whole
task. Lower layers are decomposition aids, not replacement goals.

## Non-Substitution Rule

A derived goal is invalid if it:

1. changes an outcome into a setup step;
2. changes "design and produce evidence" into "write a plan";
3. changes "multi-conversation collaboration" into "open conversations";
4. changes "minimum closed loop" into "describe a future closed loop" unless
   the task is explicitly design-only;
5. changes "10-hour sustained work" into "create a 10-hour task record";
6. removes product stress cases, safety gates, human intervention, external
   learning, or implementation breakdown from the requested scope;
7. uses existing documents as completion proof without checking the current
   requirement map.

If any derived goal matches one of these patterns, Dispatch must emit
`decision_required` or `goal_drift_detected` before dispatching more work.

## Canonical Goal Record

Every serious task charter must include:

```yaml
goal_authority:
  user_objective: <verbatim or tightly quoted user end state>
  canonical_task_goal: <operational restatement>
  non_substitution_summary:
    - <what must not be confused with success>
  goal_owner: MainAgent
  dispatch_owner: DispatchAgent
  completion_auditor: VerificationAgent
  allowed_goal_change_path: user_decision_required
  latest_user_confirmation_ref: <chat/date/file ref when available>
```

For `COAGENT-ARCH-LONGRUN-01`, the minimum non-substitution summary is:

- creating the task shell is not success;
- visible conversations are not success by themselves;
- document volume is not success by itself;
- elapsed time is not success by itself;
- implementation-ready design is not the same as implemented runtime proof.

## Decomposition Contract

Every scoped conversation packet must include both:

```yaml
canonical_task_goal_ref: <path or task id>
local_objective: <what this conversation does>
```

and one explicit alignment sentence:

```yaml
alignment_to_canonical_goal: <how the local output moves the canonical goal>
```

This alignment sentence is mandatory because it forces the sender to prove the
slice is not just activity. It should be concrete enough for VerificationAgent
to reject vague work.

Examples:

| Bad Local Objective | Why Invalid | Valid Replacement |
|---|---|---|
| create a 10-hour task | setup step, not outcome | produce the audit artifacts and requirement map for the 10-hour design goal |
| study Hermes | source-led drift | evaluate Hermes only for P05 mailbox replay and P27 blocker recovery |
| open DevOps conversation | topology-only activity | get a DevOps result packet for Candidate D Git-heavy proof-package risk |
| write a PX4 plan | too weak | produce data sufficiency and identifiability gates for PX4 parameter proof |

## Drift Signals

Dispatch and Verification should treat these as drift:

| Signal | Meaning | Required Response |
|---|---|---|
| `goal_verb_weakened` | user asked to solve/design/prove; packet says list/create/consider | pause and rewrite |
| `scope_component_missing` | required domain, gate, or artifact disappeared | add missing requirement or ask user |
| `evidence_replaced_by_intent` | packet claims future work as current progress | mark incomplete |
| `topology_as_progress` | conversation count is reported as progress | require result packet or artifact |
| `elapsed_time_as_progress` | time spent is reported as progress | require evidence delta |
| `document_volume_as_progress` | file count is reported as progress | require requirement coverage |
| `department_self_goal` | department optimizes its own area without task tie | rebind to canonical goal |
| `implementation_escape` | design task starts implementing gated runtime feature | stop under safety gate |

## Checkpoint Questions

At each long-task checkpoint, MainAgent or DispatchAgent asks:

1. What exact user objective are we still trying to satisfy?
2. Which requirements became more true since the last checkpoint?
3. Which artifacts prove that change?
4. Which conversations produced evidence, and which only consumed time?
5. Did any local objective narrow, rename, or replace the canonical goal?
6. Did any unresolved blocker require a user decision?
7. Is the next action still on the critical path?

If the answer to question 2 is "none", the checkpoint must be classified as
`activity_without_progress`.

## Completion Audit Consequence

`final_goal_completion_audit.md` may mark a requirement `design_pass` only when
the evidence proves that the original requirement is covered at the correct
scope. It must not mark pass because:

- the file exists;
- a department was assigned;
- a conversation is visible;
- the task has been running for a long time;
- an implementation backlog item exists.

Backlog items are accepted only when the missing piece is implementation,
runtime proof, or user-approved experiment, not when the architecture decision
itself is absent.

## Required Future Validator

Future implementation should add a read-only `goal_alignment_checker` that
compares:

- task charter goal fields;
- scoped packet objectives;
- result packet summaries;
- final audit requirement table;
- review brief;
- user objective excerpt.

Stable finding codes should include:

| Code | Meaning |
|---|---|
| `GOAL_USER_OBJECTIVE_MISSING` | task lacks a user objective excerpt |
| `GOAL_CANONICAL_WEAKENED` | canonical goal is weaker than user objective |
| `GOAL_LOCAL_UNALIGNED` | local objective has no concrete alignment sentence |
| `GOAL_COMPLETION_OVERCLAIM` | audit claims pass from weak evidence |
| `GOAL_FORBIDDEN_SUBSTITUTION` | derived goal matches a known substitution pattern |
| `GOAL_SCOPE_COMPONENT_DROPPED` | required scope component disappeared across layers |

This validator must be read-only. It must not create conversations, dispatch
packets, call tools/MCP, stage Git, change goals, or mark tasks complete.

## Current Task Application

For `COAGENT-ARCH-LONGRUN-01`:

- the active goal remains the full 10-hour design objective;
- this protocol is a design artifact only;
- it strengthens the audit path but does not prove completion;
- the goal remains active until final refresh and requirement-by-requirement
  audit pass;
- next implementation backlog should include the `goal_alignment_checker`
  before any unattended long-task orchestration is trusted.
