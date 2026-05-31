# COAGENT-ARCH-LONGRUN-01 Blocker Packet Validator Design

Date: 2026-05-30
Status: design contract for `COAGENT-IMPL-NEXT-05`

## Purpose

Blocked work must be resumable from files, not from chat memory. The blocker
packet validator should prove that auth/license, GUI, manual review, invalid
packet, transport timeout, destructive action, and tool-unavailable stops have
enough state to resume safely or remain blocked deliberately.

This is a design artifact. It does not implement the validator, dispatch
conversations, call tools, send notifications, retry failed work, or change
runtime transport.

## Core Rule

```text
no blocked state is durable unless a blocker packet records last safe state,
the exact condition, the user or system action required, and the resume rule
```

A vague note such as "UE failed" or "login needed" is not a blocker packet.

## Inputs

The future validator should accept:

```text
--blocker-path <path>
--task-id <expected task id>
--blocked-task-id <optional expected blocked task id>
--mode strict|review|fixtures
--json-output <optional path>
```

`strict` is for runtime closeout and proof-package gates. `review` may allow
non-fatal warnings for design-only blockers but must still reject missing
resume conditions, unsafe retries, duplicate active user asks, secret leakage,
or destructive-action ambiguity.

## Required Common Fields

Every blocker packet must include:

| Field | Validation |
|---|---|
| `task_id` | equals expected task id |
| `blocked_task_id` | non-empty for subtask or dispatch blocker |
| `blocker_id` | stable id, unique within task |
| `blocker_type` | one allowed type |
| `severity` | `low`, `medium`, `high`, or `critical` |
| `owner` | accountable department or scoped worker |
| `last_safe_state` | concrete state before stopping |
| `failed_command_or_tool` | command/tool/action, or `not_applicable` |
| `evidence_paths` | JSON array, project-local unless approved exception |
| `human_action_required` | exact action or `none` |
| `resume_condition` | machine-checkable or review-checkable condition |
| `dedupe_key` | stable key preventing repeated asks |
| `retry_policy` | allowed retry count and changed condition |
| `created_at` | ISO timestamp |
| `next_safe_action` | what Dispatch may do next |

Terminal blocker packets should also include `review_owner` and
`closeout_required`.

## Allowed Blocker Types

Initial allowed values:

- `transport_timeout`
- `invalid_result_packet`
- `auth_or_license_required`
- `manual_review_required`
- `destructive_action_approval_required`
- `tool_unavailable`
- `gui_required`
- `input_required`
- `visibility_drift`
- `unsafe_retry_blocked`

Unsupported blocker types fail. New types require a design update and fixture.

## Type-Specific Requirements

### Transport Timeout

Required:

- stdout log path;
- stderr log path;
- expected result packet path;
- process cleanup result;
- dispatch edge id;
- timeout class;
- retry condition.

Reject if retry policy permits blind retry with unchanged packet, unchanged
timeout class, and no transport config change.

### Invalid Result Packet

Required:

- invalid packet path;
- validator finding JSON path or finding codes;
- repair policy decision;
- repaired packet path, if repaired;
- re-dispatch condition, if repair is forbidden.

Reject if a repaired packet changes the conclusion without a review owner.

### Auth Or License Required

Required:

- exact product/tool requiring user action;
- smallest health probe to run after user confirmation;
- safe parallel work decision;
- retry circuit breaker.

Reject if the packet includes credentials, tokens, license text, browser
profile data, or repeated unapproved retries.

### Manual Review Required

Required:

- one concrete review question;
- artifact paths for review;
- allowed user decisions;
- resume mapping for each decision.

Reject if the review question asks the user to infer hidden context or inspect
unstated files.

### Destructive Action Approval Required

Required:

- exact target path;
- exact proposed action;
- why non-destructive alternatives are insufficient;
- rollback or recovery note;
- explicit approval phrase required.

Reject if the target path is outside the project without an approved
infrastructure exception, or if the action is broad and underspecified.

### Tool Unavailable Or GUI Required

Required:

- smallest failed probe;
- expected MCP/server/tool name;
- fallback route;
- user action only when actually needed.

Reject if the packet hides a product claim behind a missing tool, for example
claiming UE truth export succeeded when only a capability probe failed.

## Output JSON

The future validator should emit:

```json
{
  "ok": false,
  "decision": "reject",
  "blocker_path": "Results/agent_blockers/example.yaml",
  "task_id": "COAGENT-ARCH-LONGRUN-01",
  "finding_codes": ["BLK_RESUME_CONDITION_MISSING"],
  "findings": [
    {
      "code": "BLK_RESUME_CONDITION_MISSING",
      "severity": "error",
      "field": "resume_condition",
      "message": "blocked work cannot resume safely without a resume condition"
    }
  ],
  "dispatch_allowed": false,
  "user_ask_allowed": false,
  "next_action": "repair blocker packet before retry or user ask"
}
```

Allowed decisions:

- `accept`;
- `accept_needs_review`;
- `block`;
- `reject`.

## Stable Finding Codes

| Code | Meaning |
|---|---|
| `BLK_MISSING_FIELD` | required common field absent |
| `BLK_UNSUPPORTED_TYPE` | blocker type not allowed |
| `BLK_LAST_SAFE_STATE_MISSING` | no concrete last safe state |
| `BLK_RESUME_CONDITION_MISSING` | no safe resume condition |
| `BLK_DEDUPE_KEY_MISSING` | repeated user ask cannot be deduped |
| `BLK_EVIDENCE_MISSING` | required evidence path absent |
| `BLK_EVIDENCE_OUT_OF_SCOPE` | evidence path outside allowed scope |
| `BLK_RETRY_POLICY_UNSAFE` | blind or repeated retry allowed |
| `BLK_DUPLICATE_ACTIVE_ASK` | active blocker already asks same user action |
| `BLK_SECRET_RISK` | packet exposes credential or private material |
| `BLK_DESTRUCTIVE_TARGET_AMBIGUOUS` | destructive action path/action unclear |
| `BLK_MANUAL_REVIEW_QUESTION_AMBIGUOUS` | user review ask is not concrete |
| `BLK_TIMEOUT_CLOSEOUT_MISSING` | timeout lacks process/edge cleanup result |
| `BLK_INVALID_PACKET_FINDING_MISSING` | invalid packet blocker lacks validator finding |
| `BLK_CAPABILITY_OVERCLAIM` | blocker or closeout claims unproven capability |

Codes are test-contract values and should remain stable.

## Fixture Matrix

Positive fixtures:

| Fixture | Expected |
|---|---|
| valid transport timeout blocker | `block` |
| valid invalid-result blocker with validator finding | `block` |
| valid auth/license blocker with safe parallel work | `accept_needs_review` |
| valid manual-review blocker with exact question | `accept_needs_review` |
| valid destructive-action approval blocker | `block` |

Negative fixtures:

| Fixture | Expected Codes |
|---|---|
| missing resume condition | `BLK_RESUME_CONDITION_MISSING` |
| missing last safe state | `BLK_LAST_SAFE_STATE_MISSING` |
| unsupported blocker type | `BLK_UNSUPPORTED_TYPE` |
| blind retry after license failure | `BLK_RETRY_POLICY_UNSAFE` |
| duplicate active user ask | `BLK_DUPLICATE_ACTIVE_ASK` |
| evidence outside project scope | `BLK_EVIDENCE_OUT_OF_SCOPE` |
| packet includes token or secret path | `BLK_SECRET_RISK` |
| destructive target says "delete old files" | `BLK_DESTRUCTIVE_TARGET_AMBIGUOUS` |
| manual review says "check if OK" only | `BLK_MANUAL_REVIEW_QUESTION_AMBIGUOUS` |
| transport timeout without cleanup result | `BLK_TIMEOUT_CLOSEOUT_MISSING` |
| invalid result blocker without finding codes | `BLK_INVALID_PACKET_FINDING_MISSING` |

## Integration With Other Contracts

- `blocker_packet_templates.md` defines the human-readable packet shapes.
- `transport_timeout_hardening_design.md` defines timeout-specific closeout.
- `result_packet_validator_design.md` produces findings for
  `invalid_result_packet` blockers.
- `candidate_e_auth_license_interruption_proof_package.md` depends on this
  validator for manual-interruption proof.
- `operating_metrics_snapshot_design.md` should count active blockers,
  duplicate asks, unsafe retries, and blocked time without packet.
- `mailbox_ledger_and_replay_design.md` should record blocker creation,
  acknowledgement, supersession, and closeout.

## Implementation Boundary

The first implementation must be read-only:

- no retry execution;
- no user notification;
- no email or desktop sender;
- no GUI/login/license automation;
- no conversation dispatch;
- no worktree creation;
- no Git staging, commit, push, reset, or cleanup;
- no MCP/tool probing.

## Design Decision

`COAGENT-IMPL-NEXT-05` should implement blocker packet validation before any
live proof is allowed to treat a blocked department, tool, or user-review state
as recoverable. Until then, blockers remain design-level records or manually
reviewed artifacts.
