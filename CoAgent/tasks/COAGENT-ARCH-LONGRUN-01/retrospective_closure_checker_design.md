# COAGENT-ARCH-LONGRUN-01 Retrospective Closure Checker Design

Date: 2026-05-30
Status: design contract for `COAGENT-IMPL-NEXT-26`

## Purpose

Define the read-only checker that turns repeated failures, user corrections,
review escapes, and incidents into auditable improvement closure. The checker
answers a concrete operating question:

```text
Did CoAgent learn from this failure in a way that future conversations can
recover, validate, and apply without relying on chat memory?
```

This document extends:

- `retrospective_and_improvement_closure_protocol.md`
- `operating_metrics_snapshot_design.md`
- `knowledge_promotion_protocol.md`
- `external_adoption_proposal_contract.md`
- `validator_shared_envelope_design.md`
- `runbook_readiness_checker_design.md`

It is design-only. It does not create issues, edit docs or skills, send
notifications, create conversations, mutate runtime state, call MCP/tools,
stage Git, create worktrees, or repair Codex state.

## Core Rule

```text
a repeated failure is not closed until it has an owner, evidence, a target,
and a verifiable closeout decision
```

Status notes, chat explanations, and "remember next time" statements are not
closure. A retrospective record must either promote a lesson, reject a proposed
change, defer it with a trigger, or map it to an implementation/checker/workflow
action.

## Inputs

The future checker should accept:

```text
--task-id <task id>
--task-root <task directory>
--mode scan|strict|trigger_scan|closeout|fixture
--json-output <optional path>
```

Input files, when present:

| File | Purpose |
|---|---|
| retrospective records | incident, correction, or improvement records |
| `architecture_problem_matrix.md` | problem ids and owner mapping |
| `shared_task_board.md` | task states and repeated blocker notes |
| `operating_metrics_snapshot` reports | recurrence and stale-action signals |
| result packets | invalid-result and review-escape evidence |
| blocker packets | timeout, manual, auth, license, tool, Git, or destructive blockers |
| `review_brief.md` | user-facing findings and unresolved risks |
| `post_design_implementation_backlog.md` | implementation action targets |
| `knowledge_promotion_protocol.md` records | promoted or rejected lessons |
| external adoption proposal records | external-source improvements |
| proof closeout files | whether a proof carried or closed the action |

The checker may run without every dependency in `scan` mode, but it must report
missing dependency evidence through the shared validator envelope.

## Retrospective Record Shape

Each record should be YAML or another structured project-local format with
these fields:

```yaml
retrospective_id: RETRO-YYYYMMDD-001
task_id: COAGENT-ARCH-LONGRUN-01
trigger_type: repeated_failure | user_correction | review_escape | incident | stale_context | unsafe_retry | invalid_packet | tool_failure | git_failure | external_learning_drift
trigger_summary: <what happened>
first_seen_at: <timestamp or known date>
last_seen_at: <timestamp or known date>
repeated_count: <integer>
problem_ids:
  - P59
owner: KnowledgeSecretaryAgent
review_owner: VerificationAgent
safety_owner: SafetyComplianceAgent
affected_goal_requirements:
  - retrospective_and_improvement_closure
evidence_paths:
  - <project path>
root_cause_status: unknown | suspected | confirmed | not_applicable
root_cause_hypotheses:
  - <hypothesis>
improvement_actions:
  - action_id: RETRO-YYYYMMDD-001-A1
    type: implementation_backlog | doctor_check | workflow_doc | skill_update | context_delta | external_adoption_proposal | rejected_idea | deferred_trigger
    target: <path, backlog id, checker id, proposal id, or rejected idea id>
    owner: <agent or department>
    review_owner: <agent or department>
    close_condition: <testable or reviewable condition>
    status: open | in_progress | blocked | closed_promoted | closed_rejected | closed_deferred | closed_duplicate
    evidence_paths:
      - <project path>
rejected_actions:
  - action: <proposal>
    reason: <why rejected>
deferred_actions:
  - action: <proposal>
    revisit_trigger: <condition>
    owner: <agent or department>
closeout_decision: open | blocked | closed_promoted | closed_rejected | closed_deferred | closed_duplicate
closeout_evidence_paths:
  - <project path>
claim_boundaries:
  - <what this closure does not prove>
```

## Trigger Discovery

The checker should identify likely mandatory retrospective triggers from:

- repeated `blocked`, `timeout`, `invalid_packet`, `visibility_drift`, or
  `unsafe_retry` records for the same task, department, tool route, or proof
  package;
- user corrections that identify the same process failure more than once;
- result packets repaired after import failure;
- completion audits that downgrade a previous overclaim;
- operating metrics showing stale open actions, fake progress, or missing
  blockers;
- proof closeout files that mention unresolved repeated incidents;
- Git/tool/MCP/GUI/license failures that recur after a documented fix.

The trigger scan is advisory unless a source provides enough evidence to
require a record. It should produce `needs_review` rather than invent records.

## Required Checks

### Record Presence

For mandatory triggers, check that one canonical retrospective record exists.

Reject if:

- the failure recurred and only appears in chat/status text;
- duplicate records exist without a canonical owner;
- a proof closeout mentions a repeated incident but no record is linked.

### Ownership

Check:

- owner is named;
- review owner is named;
- safety owner is named for tool, credential, path, destructive-action, GUI,
  license, notification, or external-path risks;
- owner matches the problem family or DispatchAgent is explicitly routing.

Reject vague owners such as "agent", "future worker", or "remember next time".

### Evidence

Check:

- evidence paths exist or are explicitly marked unavailable with reason;
- evidence stays inside the project unless an approved infrastructure
  exception is recorded;
- no secrets, tokens, account caches, raw full transcripts, private Codex DB
  dumps, or credentials are emitted;
- evidence label matches the source strength.

Reject closure based only on a prose claim.

### Action Target

Every action must point to a durable target:

- implementation backlog item;
- validator/checker design or report;
- workflow document;
- project-local skill;
- context delta;
- knowledge promotion record;
- external adoption proposal;
- rejected idea archive;
- deferred trigger record.

Reject action targets that only say "be careful", "discuss later", "add more
agents", or "done".

### Close Condition

Each open or in-progress action must have a close condition that can be tested
or reviewed.

Reject:

- untestable close conditions;
- closure that cites a backlog item but no acceptance evidence;
- closure that claims automation, notification, tool repair, Git recovery, or
  runtime reliability without the relevant approved validator/proof.

### Promotion, Rejection, And Deferral

If a lesson is promoted, require a target and review evidence.

If a proposal is rejected, require a rationale and revisit condition when
appropriate.

If an action is deferred, require:

- owner;
- trigger;
- reason;
- risk if ignored;
- next review condition.

### Staleness

Flag open actions as stale when:

- triggering problem recurs after the action opened;
- owner or close condition is missing;
- proof closeout depends on the action but does not reference it;
- action remains open past an explicit review checkpoint;
- action references superseded context.

Stale actions should block clean closeout for the affected requirement.

### Dependency And Claim Boundary

The checker must use the shared validator envelope. It should report
`needs_dependency` when required dependency reports are absent, such as:

- operating metrics snapshot for recurrence detection;
- result or blocker validators for packet-derived incidents;
- evidence label doctor for source-strength checks;
- external adoption checker for source-derived improvements;
- runbook readiness checker for task closeout.

It must not claim root-cause reliability or implemented fixes from a
retrospective record alone.

## Modes

| Mode | Required Behavior |
|---|---|
| `scan` | find likely missing or stale retrospective records |
| `strict` | validate record schema, owners, evidence, actions, close conditions, and safety boundaries |
| `trigger_scan` | compare triggers from metrics, packets, blockers, board, and closeouts against records |
| `closeout` | decide whether affected task requirements can close cleanly |
| `fixture` | run positive and negative retrospective examples |

## Stable Finding Codes

| Code | Meaning |
|---|---|
| `RETRO_RECORD_MISSING` | mandatory trigger has no retrospective record |
| `RETRO_DUPLICATE_UNRESOLVED` | duplicate records exist without canonical owner |
| `RETRO_OWNER_MISSING` | owner, review owner, or required safety owner is missing |
| `RETRO_PROBLEM_UNLINKED` | record does not link to a problem id or create one |
| `RETRO_EVIDENCE_MISSING` | required evidence paths are absent |
| `RETRO_EVIDENCE_UNSAFE` | evidence includes or points to secrets, account cache, private DB dumps, or raw transcripts |
| `RETRO_ACTION_TARGET_MISSING` | action lacks durable target |
| `RETRO_ACTION_UNTESTABLE` | close condition cannot be reviewed or tested |
| `RETRO_PROMOTION_UNLINKED` | promoted lesson lacks durable target or review evidence |
| `RETRO_REJECTION_UNJUSTIFIED` | rejected action lacks rationale |
| `RETRO_DEFER_TRIGGER_MISSING` | deferred action lacks owner or revisit trigger |
| `RETRO_STALE_OPEN_ACTION` | open action is stale by recurrence or checkpoint |
| `RETRO_UNSAFE_ACTION` | proposed action widens permissions or automates gated risk |
| `RETRO_CLOSEOUT_OVERCLAIM` | record is closed without evidence or claims more than closure proves |
| `RETRO_DEPENDENCY_MISSING` | required validator/report dependency is missing |
| `RETRO_FORBIDDEN_SIDE_EFFECT` | checker attempts or declares mutation beyond read/report output |

## Fixture Matrix

Positive fixtures:

| Fixture | Expected |
|---|---|
| visibility drift record with evidence, owner, safety owner, NEXT-22 action, and close condition | `pass` |
| user correction record that creates a goal-alignment checker target and rejected "remember next time" action | `pass` |
| deferred email notification action with owner, trigger, Candidate E dependency, and risk note | `pass_with_warnings` |
| closed rejected action with rationale and revisit condition | `pass` |

Negative fixtures:

| Fixture | Expected Codes |
|---|---|
| repeated visible-thread drift appears in board but no retrospective record | `RETRO_RECORD_MISSING` |
| record has no owner or review owner | `RETRO_OWNER_MISSING` |
| record says "be careful next time" as action target | `RETRO_ACTION_TARGET_MISSING`, `RETRO_ACTION_UNTESTABLE` |
| closeout claims issue fixed because a doc exists but no checker/proof passed | `RETRO_CLOSEOUT_OVERCLAIM` |
| proposal automates email before blocker/resume semantics are proven | `RETRO_UNSAFE_ACTION` |
| deferred action has no revisit trigger | `RETRO_DEFER_TRIGGER_MISSING` |
| record cites raw Codex DB dump or account cache as evidence | `RETRO_EVIDENCE_UNSAFE` |
| duplicate incident records remain open with different owners | `RETRO_DUPLICATE_UNRESOLVED` |
| metrics report repeated invalid packets but record is missing | `RETRO_RECORD_MISSING`, `RETRO_DEPENDENCY_MISSING` when packet validator report is absent |

## Output

The checker should emit the shared validator envelope, for example:

```json
{
  "schema_version": "coagent.validator_report.v1",
  "validator": "retrospective_closure_checker",
  "task_id": "COAGENT-ARCH-LONGRUN-01",
  "mode": "closeout",
  "decision": "needs_review",
  "ok": false,
  "finding_codes": ["RETRO_STALE_OPEN_ACTION"],
  "findings": [
    {
      "code": "RETRO_STALE_OPEN_ACTION",
      "severity": "error",
      "path": "retrospectives/RETRO-20260530-001.yaml",
      "message": "visibility drift recurred after the action opened and no updated closeout evidence is linked",
      "remediation": "update the action target, blocker, or closeout evidence before closing affected requirements"
    }
  ],
  "dependency_reports": [
    {
      "validator": "operating_metrics_snapshot",
      "decision": "needs_dependency",
      "required_for": "recurrence detection"
    }
  ],
  "evidence_paths": [
    "CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/codex_visibility_recovery_experiment_design.md"
  ],
  "side_effects": {
    "declared": ["read_project_files", "write_validator_report"],
    "forbidden": ["issue_creation", "doc_mutation", "skill_mutation", "live_dispatch", "mcp_or_tool_call", "git_mutation", "notification_send"]
  },
  "claim_boundaries": [
    {
      "claim": "retrospective closure is valid",
      "supported": false,
      "limitations": "checker does not implement the action target or prove root cause fixed"
    }
  ],
  "next_action": "keep affected closeout in needs_review until action evidence is updated"
}
```

## Implementation Boundary

The first implementation should be read-only and fixture-backed. It may read
project task records, retrospective records, packets, blocker files, metrics
reports, proof closeouts, backlog files, and knowledge/adoption records. It may
write validator reports under `Results/coagent_validators/`.

It must not:

- create or edit retrospective records automatically;
- create issues or tickets;
- edit skills, workflow docs, or AGENTS files;
- create, delete, or resume conversations;
- mutate runtime task state;
- call MCP/tools or inspect external account caches;
- create worktrees, stage, commit, or push Git changes;
- send email or desktop notifications;
- read or emit credentials, tokens, raw full transcripts, private Codex DB
  dumps, account caches, or provider configs.

## Rollout Position

This checker should run after the shared validator envelope and basic packet,
blocker, evidence-label, and operating-metrics reports exist. It may run in
`scan` mode earlier to expose missing records, but it must report missing
dependencies instead of silently passing.

It should feed:

- runbook readiness;
- goal completion audit;
- knowledge promotion;
- external adoption;
- future implementation approval packets when a prior incident created the
  approved slice.
