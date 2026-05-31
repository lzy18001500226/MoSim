# COAGENT-ARCH-LONGRUN-01 Goal Creation And Recovery Protocol

Date: 2026-05-30
Status: phase 2 design draft

## Purpose

Define how CoAgent should create, recreate, or recover an active Codex goal
without weakening the user's objective into setup work.

This protocol is narrower than
`goal_authority_and_decomposition_protocol.md`. That file defines the goal
hierarchy. This file defines the operational preflight for the moment an agent
is about to call `create_goal`, or continue after the user deletes a bad goal.

## Trigger Cases

Use this protocol when:

1. the user says to set or reset a goal;
2. the user says an existing goal is wrong and deletes it;
3. a long task is being converted from chat instructions into durable runtime
   state;
4. a worker proposes a scoped goal that may replace the canonical task goal;
5. final audit depends on proving the active goal matches the user's real
   objective.

## Goal Creation Rule

Before creating a goal, MainAgent must write or verify these fields:

```yaml
goal_creation_preflight:
  user_objective_excerpt: <tight quote or faithful summary of user outcome>
  canonical_goal_candidate: <full outcome goal to create>
  non_substitution_check:
    creates_task_shell_only: false
    opens_conversations_only: false
    spends_time_only: false
    writes_documents_only: false
    implements_unapproved_runtime_only: false
  required_scope_components:
    - <component explicitly requested by user>
  audit_entry: <review file or task charter path>
  owner: MainAgent
  verifier: VerificationAgent
```

If any non-substitution field is true, do not create the goal. Rewrite the goal
candidate until it expresses the user outcome.

## Valid Goal Shape

A valid long-running CoAgent goal should contain:

1. the real outcome, not the setup step;
2. the minimum duration or appetite only when the user requested it;
3. the major scope components that would be easy to drop;
4. the expected review artifact or audit path;
5. the completion standard.

For the current task, the valid shape is:

```text
Sustain at least 10 hours of real CoAgent architecture design work for a
task-first, multi-conversation, multi-agent operating system, and produce
auditable design documents, problem matrices, tradeoff records, minimum
closed-loop designs, department dispatch results, and next implementation
breakdown for user review.
```

Invalid shapes include:

```text
Create a 10-hour architecture task.
Build a task shell for later architecture work.
Set up a long-running goal record.
Open department conversations for architecture design.
```

Those are setup actions. They may be necessary, but they are not the user
objective.

## Recovery When A Goal Is Wrong

If an active goal is wrong and the runtime cannot rewrite it directly:

1. stop treating the wrong goal as authoritative;
2. write a `goal_recovery_required` note in the task board or status file;
3. ask the user to delete the wrong goal only if no safe local correction path
   exists;
4. after deletion, recreate the goal from the preflight fields above;
5. checkpoint runtime state with the corrected canonical goal and recovery
   reason;
6. update `goal_requirement_audit_map.md` and
   `final_goal_completion_audit.md` so the correction is visible at review.

Do not continue to dispatch workers under a known-wrong goal.

## Current Incident Pattern

The incident to prevent is:

```text
User objective:
  do at least 10 hours of actual architecture design work.

Bad derived goal:
  establish a 10-hour architecture design promotion task.
```

Why this is invalid:

- it turns execution into administration;
- it lets completion be claimed after task setup;
- it hides whether architecture requirements became more true;
- it makes later department goals inherit the wrong target.

Correct response:

- recreate the active goal with the real design-work outcome;
- record "creating the task shell is not success" in the charter, board, and
  audit map;
- require future checkpoints to state which requirement changed.

## Goal Checkpoint Rule

Every checkpoint for a long-running CoAgent goal must answer:

```yaml
goal_checkpoint:
  active_goal_matches_user_objective: true|false
  evidence_delta_since_last_checkpoint:
    - <file, result packet, design decision, or blocker record>
  requirements_advanced:
    - <requirement id or description>
  setup_actions_only: true|false
  next_critical_path_action: <action>
```

If `setup_actions_only` is true, the checkpoint must be labeled
`activity_without_goal_progress`.

## Integration With Future Validator

The future `goal_alignment_checker` must consume this file together with
`goal_authority_and_decomposition_protocol.md`.

Additional stable finding codes:

| Code | Meaning |
|---|---|
| `GOAL_CREATE_PREFLIGHT_MISSING` | goal was created without required preflight fields |
| `GOAL_SETUP_ACTION_ONLY` | candidate goal describes setup rather than outcome |
| `GOAL_RECOVERY_UNRECORDED` | wrong goal was replaced without a recovery record |
| `GOAL_CHECKPOINT_NO_DELTA` | checkpoint records activity but no requirement progress |
| `GOAL_SCOPE_COMPONENT_LOST_ON_RECREATE` | recreated goal omits a scope component from the user objective |

The validator is read-only. It must not create, delete, mutate, complete, or
block goals automatically.

## Current Task Application

For `COAGENT-ARCH-LONGRUN-01`:

- the active goal now correctly names sustained architecture design work and
  reviewable artifacts;
- the goal must remain active until the final requirement-by-requirement audit
  is refreshed;
- future checkpoint summaries must name evidence deltas, not just elapsed time
  or file count;
- this protocol is a design artifact only and does not implement the future
  checker.
