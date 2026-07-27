# COAGENT-ARCH-LONGRUN-01 Goal Alignment Checker Design

Date: 2026-05-30
Status: design contract for `COAGENT-IMPL-NEXT-25`

## Purpose

Define the read-only checker that prevents CoAgent from proving the wrong
goal. The checker validates that user objectives, canonical task goals, scoped
conversation objectives, result summaries, checkpoints, and completion audits
remain aligned.

This document extends:

- `goal_authority_and_decomposition_protocol.md`
- `goal_creation_and_recovery_protocol.md`
- `validator_shared_envelope_design.md`
- `final_goal_completion_audit.md`
- `end_to_end_task_operating_runbook.md`

It is design-only. It does not create, delete, mutate, complete, or block
Codex goals. It does not dispatch conversations, call tools/MCP, stage Git,
create worktrees, send notifications, or change runtime transport.

## Core Rule

```text
passing a downstream validator is irrelevant if the target goal was weakened
```

Goal alignment is an L0 gate. It should run before evidence labels, result
packets, blockers, proof packages, operating metrics, or completion audits are
trusted.

## Inputs

The future checker should accept:

```text
--task-id <task id>
--task-root <task directory>
--mode scan|strict|preflight|post_dispatch|completion|fixture
--json-output <optional path>
```

Input files, when present:

| File | Purpose |
|---|---|
| `task_charter.md` or `task_charter.yaml` | user objective and canonical goal |
| `context_pack.md` | task context and non-substitution summary |
| `shared_task_board.md` | board goal, work items, and checkpoints |
| `department_dispatch_plan.md` | department objectives |
| scoped task packets | local objectives and alignment sentence |
| result packets | worker summary and evidence claims |
| blocker packets | blocked scope and resume condition |
| `review_brief.md` | review claims and expected audit |
| `goal_requirement_audit_map.md` | requirement/evidence map |
| `final_goal_completion_audit.md` | completion verdicts |
| runtime checkpoint output | active goal, checkpoint deltas, task state |

The checker should not require every file for every mode, but it must report
missing required inputs through the shared validator envelope.

## Required Goal Fields

Every serious task should expose:

```yaml
goal_authority:
  user_objective_excerpt: <verbatim or faithful user outcome>
  canonical_task_goal: <operational restatement>
  non_substitution_summary:
    - <forbidden substitute>
  required_scope_components:
    - <required component>
  goal_owner: MainAgent
  dispatch_owner: DispatchAgent
  completion_auditor: VerificationAgent
  allowed_goal_change_path: user_decision_required
```

Scoped conversation packets must include:

```yaml
canonical_task_goal_ref: <task id or path>
local_objective: <slice objective>
alignment_to_canonical_goal: <concrete contribution>
stop_condition: <when to stop>
result_path: <where output goes>
review_owner: <who audits>
```

## Alignment Checks

### User Objective To Canonical Goal

The canonical goal must preserve:

- the requested outcome;
- the main scope components;
- the review/audit expectation;
- duration or appetite if user specified it;
- explicit non-goals and gated boundaries.

Reject if the canonical goal:

- becomes a setup action;
- drops multi-conversation, context, Git/worktree, review/testing, safety,
  human intervention, external learning, self-evolution, implementation
  breakdown, or audit package when those are in the user objective;
- replaces "do sustained architecture design" with "create a task record";
- replaces "prove/validate" with "describe";
- claims implementation completion when the task is design-only.

### Canonical Goal To Local Objective

Every local objective must answer:

```text
How does this output make the canonical goal more true?
```

Reject local objectives that are only:

- open/create/resume a conversation;
- study a source without a problem id;
- write a plan without required decision, evidence, or checker target;
- run a tool without an evidence or blocker path;
- spend time;
- prepare for work without a concrete output.

### Result Packet To Assigned Objective

Result packets must not:

- change the canonical goal;
- mark a setup action as completion;
- remove unresolved risks from the parent task;
- promote design evidence into runtime/product proof;
- omit blockers that prevent the assigned objective.

### Checkpoint To Evidence Delta

Every long-running checkpoint should list:

```yaml
evidence_delta_since_last_checkpoint:
  - <new or changed artifact>
requirements_advanced:
  - <requirement or problem id>
setup_actions_only: false
```

Reject or flag checkpoints that only say time passed, files were touched,
conversations exist, or a task was created.

### Completion Audit

Completion audits must map every requirement to evidence. Reject if:

- a requirement passes because a file exists but the file does not cover the
  scope;
- a requirement passes because a backlog item exists;
- a requirement passes while its own row says proof/checker/live run is
  pending;
- a requirement drops from the audit table;
- final completion is claimed before latest command refresh and user review
  decision.

## Modes

| Mode | Required Behavior |
|---|---|
| `scan` | report likely drift without blocking |
| `strict` | reject missing required fields, weak canonical goals, and substitutions |
| `preflight` | validate task charter and scoped packets before dispatch |
| `post_dispatch` | validate result/blocker packets against assigned objectives |
| `completion` | validate final audit before any completion claim |
| `fixture` | run positive and negative goal-drift examples |

All modes should emit the shared envelope from
`validator_shared_envelope_design.md`.

## Stable Finding Codes

| Code | Meaning |
|---|---|
| `GOAL_USER_OBJECTIVE_MISSING` | user objective excerpt is missing |
| `GOAL_CANONICAL_MISSING` | canonical task goal is missing |
| `GOAL_CANONICAL_WEAKENED` | canonical goal is weaker than user objective |
| `GOAL_REQUIRED_SCOPE_DROPPED` | required scope component disappears |
| `GOAL_NON_SUBSTITUTION_MISSING` | task lacks explicit non-substitution summary |
| `GOAL_FORBIDDEN_SUBSTITUTION` | derived goal is setup/time/topology/document-volume activity |
| `GOAL_LOCAL_UNALIGNED` | local objective lacks concrete contribution |
| `GOAL_OBJECTIVE_AS_ACTIVITY` | local objective is only activity, not output |
| `GOAL_RESULT_MUTATION` | result packet changes or narrows the goal |
| `GOAL_CHECKPOINT_NO_DELTA` | checkpoint records no requirement-level evidence delta |
| `GOAL_COMPLETION_OVERCLAIM` | audit marks pass from weak or pending evidence |
| `GOAL_SCOPE_COMPONENT_LOST_ON_RECREATE` | recreated goal omits prior required scope |
| `GOAL_RECOVERY_UNRECORDED` | wrong goal was replaced without recovery record |
| `GOAL_USER_DECISION_REQUIRED` | proposed goal change needs explicit user decision |
| `GOAL_EVIDENCE_OUT_OF_SCOPE` | evidence path cannot prove the claimed requirement |

## Fixture Matrix

Positive fixtures:

| Fixture | Expected |
|---|---|
| current long-run goal with non-substitution summary and evidence deltas | `pass` or `pass_with_warnings` |
| scoped packet with concrete alignment and result path | `pass` |
| completion audit that marks pending implementation as gated follow-up | `pass_with_warnings` |

Negative fixtures:

| Fixture | Expected Codes |
|---|---|
| goal says "create a 10-hour task" | `GOAL_FORBIDDEN_SUBSTITUTION` |
| canonical goal drops human intervention and external learning | `GOAL_REQUIRED_SCOPE_DROPPED` |
| local objective says "study Hermes" without problem id | `GOAL_LOCAL_UNALIGNED` |
| result packet claims visible conversation creation completed the task | `GOAL_RESULT_MUTATION`, `GOAL_FORBIDDEN_SUBSTITUTION` |
| checkpoint has no evidence delta | `GOAL_CHECKPOINT_NO_DELTA` |
| final audit passes Candidate A while proof is pending | `GOAL_COMPLETION_OVERCLAIM` |
| recreated goal omits implementation breakdown | `GOAL_SCOPE_COMPONENT_LOST_ON_RECREATE` |
| wrong goal was deleted/recreated with no recovery note | `GOAL_RECOVERY_UNRECORDED` |

## Output

The checker should emit the shared envelope, for example:

```json
{
  "schema_version": "coagent.validator_report.v1",
  "validator": "goal_alignment_checker",
  "task_id": "COAGENT-ARCH-LONGRUN-01",
  "mode": "completion",
  "decision": "needs_review",
  "ok": false,
  "finding_codes": ["GOAL_COMPLETION_OVERCLAIM"],
  "findings": [
    {
      "code": "GOAL_COMPLETION_OVERCLAIM",
      "severity": "error",
      "path": "final_goal_completion_audit.md",
      "message": "requirement marked pass while live proof remains pending",
      "remediation": "change verdict to design_pass_with_gated_followup"
    }
  ],
  "dependency_reports": [],
  "evidence_paths": [
    "CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/final_goal_completion_audit.md"
  ],
  "side_effects": {
    "declared": ["read_project_files", "write_validator_report"],
    "forbidden": ["goal_mutation", "live_dispatch", "mcp_or_tool_call", "git_mutation"]
  },
  "claim_boundaries": [
    {
      "claim": "goal statements are aligned",
      "supported": false,
      "limitations": "does not prove task implementation or product behavior"
    }
  ],
  "next_action": "repair completion audit before any completion claim"
}
```

## Integration

- `validator_dependency_and_rollout_plan.md` treats this as an L0 gate.
- `validator_shared_envelope_design.md` defines the output shape.
- `result_packet_validator_design.md` should depend on this checker for goal
  mutation findings.
- `operating_metrics_snapshot_design.md` should count `GOAL_*` findings as
  high-severity drift.
- `retrospective_and_improvement_closure_protocol.md` should trigger
  improvement actions on repeated goal drift.
- `goal_completion_gate_protocol.md` should require a clean completion-mode
  report before `update_goal complete`.

## Implementation Boundary

The first implementation should be read-only and fixture-backed. It may read
task files and write validator reports under `Results/coagent_validators/`.
It must not create, delete, mutate, complete, or block Codex goals; dispatch
conversations; call MCP/tools; create worktrees; stage Git; send
notifications; edit global Codex state; or rewrite task documents
automatically.
