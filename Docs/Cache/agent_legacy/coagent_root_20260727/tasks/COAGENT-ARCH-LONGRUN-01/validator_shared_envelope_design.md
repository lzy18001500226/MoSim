# COAGENT-ARCH-LONGRUN-01 Validator Shared Envelope Design

Date: 2026-05-30
Status: design contract for `COAGENT-IMPL-NEXT-00`

## Purpose

Define one shared output envelope for all future CoAgent validators and
doctor-style checks. This prevents each checker from inventing its own
decision vocabulary, dependency semantics, evidence fields, and side-effect
claims.

This document extends:

- `validator_dependency_and_rollout_plan.md`
- `common_proof_package_validator_design.md`
- `result_packet_validator_design.md`
- `blocker_packet_validator_design.md`
- `evidence_label_doctor_design.md`
- `operating_metrics_snapshot_design.md`

It is design-only. It does not implement validators, run proof packages,
dispatch conversations, create worktrees, stage Git, call MCP/tools, send
notifications, or mutate runtime state.

## Core Rule

```text
no validator report is durable unless it uses the shared envelope
```

A validator may add domain-specific sections, but the common fields, decision
vocabulary, dependency behavior, evidence-path rules, and side-effect
declarations must remain stable.

## Why This Exists

CoAgent has designs for result packets, blockers, evidence labels, workflow
graphs, context deltas, proof packages, transport timeouts, tool health,
external adoption, retrospective closure, and human review. Without a shared
envelope:

- downstream validators cannot reliably consume upstream reports;
- missing dependencies may be treated as success;
- operating metrics cannot compare checker outcomes;
- final audits cannot distinguish `pass`, `needs_review`, `blocked`, and
  `needs_dependency`;
- validators may accidentally imply that live dispatch, Git, MCP, email, or
  GUI automation happened when they only inspected files.

## Required Envelope

Every validator report should be valid JSON with these top-level fields:

```json
{
  "schema_version": "coagent.validator_report.v1",
  "report_id": "uuid-or-stable-id",
  "created_at": "2026-05-30T00:00:00+08:00",
  "validator": "result_packet_validator",
  "validator_version": "0.1.0",
  "task_id": "COAGENT-ARCH-LONGRUN-01",
  "mode": "preflight",
  "target": {
    "kind": "file",
    "path": "Results/agent_packets/example.yaml",
    "id": "optional-domain-id"
  },
  "ok": false,
  "decision": "fail_before_dispatch",
  "finding_codes": ["RPKT_MISSING_FIELD"],
  "findings": [],
  "dependency_reports": [],
  "evidence_paths": [],
  "side_effects": {
    "declared": [],
    "forbidden": [
      "live_dispatch",
      "mcp_or_tool_call",
      "git_mutation",
      "notification_send",
      "runtime_mutation"
    ]
  },
  "claim_boundaries": [],
  "next_action": "fix_package_before_dispatch"
}
```

## Field Contract

| Field | Required | Meaning |
|---|---|---|
| `schema_version` | yes | must be `coagent.validator_report.v1` for this design |
| `report_id` | yes | stable id for this run |
| `created_at` | yes | ISO timestamp |
| `validator` | yes | checker name from approved validator list |
| `validator_version` | yes | implementation or design version |
| `task_id` | yes | task the report applies to |
| `mode` | yes | one allowed mode |
| `target` | yes | file, directory, package, task, or synthetic fixture target |
| `ok` | yes | boolean summary derived from `decision` |
| `decision` | yes | one shared decision value |
| `finding_codes` | yes | array of stable codes, may be empty |
| `findings` | yes | detailed findings |
| `dependency_reports` | yes | upstream reports or missing dependencies |
| `evidence_paths` | yes | project-local evidence paths or approved references |
| `side_effects` | yes | explicit side-effect declaration |
| `claim_boundaries` | yes | what this report does and does not prove |
| `next_action` | yes | one actionable next step |

Domain validators may add fields such as `candidate_id`, `proof_package_root`,
`router_import_allowed`, `user_ask_allowed`, `dispatch_allowed`, or
`review_required`, but they must not replace common fields.

## Allowed Modes

| Mode | Use |
|---|---|
| `scan` | read-only scan that may produce warnings |
| `strict` | blocking validation for durable state |
| `preflight` | before dispatch, execution, or promotion |
| `post_dispatch` | after worker packets, blockers, or proof output exist |
| `fixture` | positive/negative test fixture evaluation |
| `review` | human or PMO review support |
| `snapshot` | read-only operating metrics or state summary |

Validators may support a subset, but unsupported modes must fail with a stable
finding code rather than being silently reinterpreted.

## Shared Decision Vocabulary

| Decision | `ok` | Meaning |
|---|---|---|
| `pass` | true | target satisfies the validator |
| `pass_with_warnings` | true | target satisfies gate but has non-blocking warnings |
| `needs_review` | false | human or owner review is required before promotion |
| `needs_dependency` | false | required upstream validator/report is missing |
| `fail_before_dispatch` | false | target must not be dispatched/executed/promoted |
| `blocked` | false | external condition or unresolved blocker prevents progress |
| `reject` | false | target is invalid and should be repaired or replaced |
| `not_applicable` | true | validator does not apply and explains why |

Rules:

- `ok=true` is allowed only for `pass`, `pass_with_warnings`, or
  `not_applicable`.
- missing dependencies must use `needs_dependency`, not `pass_with_warnings`;
- high-risk stale dependencies must use `blocked`;
- local synonyms such as `accepted_with_conditions`, `complete`, `ok_but`, or
  `done_needs_review` are forbidden;
- domain validators can expose extra booleans, but cannot override the shared
  decision.

## Dependency Report Shape

Each dependency entry should be one of:

```json
{
  "validator": "evidence_label_doctor",
  "required": true,
  "status": "present",
  "report_path": "Results/coagent_validators/task/evidence_label_doctor/report.json",
  "decision": "pass",
  "stale": false
}
```

or:

```json
{
  "validator": "blocker_packet_validator",
  "required": true,
  "status": "missing",
  "decision": "needs_dependency",
  "reason": "Candidate E closeout requires blocker validation"
}
```

Allowed dependency statuses:

- `present`
- `missing`
- `failed`
- `stale`
- `not_required`
- `not_implemented`

Dependency rules:

- before live dispatch, a missing required dependency is
  `fail_before_dispatch`;
- in design-only audit, a missing required dependency is `needs_dependency`;
- a failed required dependency produces `blocked` or `reject`;
- stale dependencies are `blocked` for high-risk claims;
- a validator cannot pass by ignoring a required dependency.

## Finding Shape

Every finding should include:

```json
{
  "code": "RPKT_MISSING_FIELD",
  "severity": "error",
  "message": "required field task_id is missing",
  "path": "Results/agent_packets/example.yaml",
  "field": "task_id",
  "evidence": [],
  "remediation": "add task_id matching dispatched task"
}
```

Required fields:

- `code`;
- `severity`;
- `message`.

Optional but recommended:

- `path`;
- `field`;
- `evidence`;
- `remediation`;
- `owner`;
- `related_problem_id`.

Allowed severities:

- `info`;
- `warning`;
- `error`;
- `critical`.

Stable codes are test contracts. User-facing text may change; codes should not
change casually.

## Evidence Path Rules

`evidence_paths` should be a list of project-local file paths or approved
external references.

Reject or flag:

- secrets, tokens, SSH keys, browser profiles, account-cache bodies;
- private Codex database dumps;
- raw full transcript;
- unrelated personal paths;
- output paths outside the project without an explicit approved
  infrastructure exception.

Evidence paths prove only the claim listed in `claim_boundaries`. A validator
report proving packet structure does not prove product behavior.

## Side-Effect Declaration

Every report must declare side effects.

For read-only validators:

```json
{
  "declared": ["read_project_files", "write_validator_report"],
  "forbidden": [
    "live_dispatch",
    "conversation_creation",
    "runtime_mutation",
    "mcp_or_tool_call",
    "gui_automation",
    "credential_handling",
    "git_mutation",
    "notification_send",
    "external_fetch"
  ]
}
```

If a future validator is allowed to perform a side effect, that permission must
come from an explicit implementation task. The side effect must appear in
`declared`, and the approval evidence must be listed in `evidence_paths` or a
domain-specific approval field.

## Claim Boundaries

Each report should include explicit claim boundaries:

```json
[
  {
    "claim": "packet schema is valid",
    "supported": true,
    "limitations": "does not prove worker conclusion is correct"
  },
  {
    "claim": "live dispatch is reliable",
    "supported": false,
    "limitations": "this validator is read-only"
  }
]
```

This prevents label inflation and scope creep in audit summaries.

## Report Storage

Default path:

```text
Results/coagent_validators/<task-id>/<validator>/<timestamp-or-report-id>.json
```

For proof packages, include either the report or a pointer:

```text
Results/coagent_proofs/<proof-id>/validator_reports/<validator>.json
```

Reports are durable evidence, but generated validator reports are not proof of
implementation unless the validator code, fixtures, and command output are
also present.

## Minimal Fixture Set

Future `COAGENT-IMPL-NEXT-00` should include fixtures for:

| Fixture | Expected Decision |
|---|---|
| valid envelope with no findings | `pass` |
| pass with warning finding | `pass_with_warnings` |
| missing required dependency in design audit | `needs_dependency` |
| missing required dependency before dispatch | `fail_before_dispatch` |
| stale high-risk dependency | `blocked` |
| unsupported decision synonym | `reject` |
| `ok=true` with blocking decision | `reject` |
| evidence path outside project without exception | `reject` |
| report claims side effect that is forbidden | `reject` |
| report claims product behavior from schema validation | `needs_review` or `reject` |

## Integration Rules

- Result packet, blocker packet, evidence label, tool capability, context,
  mailbox, proof package, transport, metrics, external adoption, retrospective,
  worktree/Git, and human-review validators should all emit this envelope.
- Operating metrics should count decisions by shared vocabulary, not local
  status strings.
- Completion audits should cite report paths and decision values, not only
  command success.
- Missing validators should be represented as `needs_dependency` until their
  implementation is approved and verified.

## Implementation Boundary

The first implementation slice should define shared constants, report schema,
sample reports, and fixture validation only. It must not implement every
domain validator and must not perform live dispatch, tool/MCP calls, Git
staging, worktree creation, notification, GUI automation, credential handling,
or runtime transport changes.
