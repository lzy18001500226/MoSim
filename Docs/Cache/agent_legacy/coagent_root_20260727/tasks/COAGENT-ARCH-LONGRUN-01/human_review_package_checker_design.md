# COAGENT-ARCH-LONGRUN-01 Human Review Package Checker Design

Date: 2026-05-30
Status: design contract for `COAGENT-IMPL-NEXT-29`

## Purpose

Define the read-only checker that validates PMO-facing human-review and
external-intervention packets before CoAgent asks the user, waits for the user,
or resumes after the user acts.

This checker exists because human intervention is common in this project:

- MWORKS/Sysplorer login or license prompts;
- UE/Fab manual import or editor dialogs;
- visual scene or simulation review;
- destructive or broad Git/file approval;
- invalid packet or transport repair that changes task direction.

The checker ensures that the user receives one specific, redacted, resumable
ask and that worker conversations cannot turn manual review into automated
proof.

This design extends:

- `human_review_intervention_ux_design.md`
- `blocker_packet_validator_design.md`
- `candidate_e_auth_license_interruption_proof_package.md`
- `evidence_label_doctor_design.md`
- `tool_capability_health_and_fallback_protocol.md`
- `validator_shared_envelope_design.md`

It is design-only. It does not send email or desktop notifications, open GUIs,
call MCP/tools, create conversations, mutate runtime state, approve
destructive actions, retry tools, inspect credentials, or handle account-cache
content.

## Core Rule

```text
the user ask must be specific enough to resume without interpretation
```

A valid human-review packet is not a chat message. It is a durable state
transition with a blocker type, last safe state, allowed decisions, resume
condition, post-resume probe, verification plan, dedupe key, redaction
summary, and closeout condition.

## Inputs

The future checker should accept:

```text
--task-id <task id>
--packet <review packet path>
--mode pre_ask|post_decision|closeout|fixture
--json-output <optional path>
```

Input files, when present:

| File | Purpose |
|---|---|
| `review_packet.yaml` | user-facing ask and durable blocker state |
| `user_decision.yaml` | normalized user decision and optional comment |
| blocker packet | source blocker and resume condition |
| Candidate E package | auth/license/manual interruption proof context |
| manual rehearsal record | supervised manual run context |
| mailbox records | active asks, acknowledgements, and expected responses |
| tool capability card | route health and post-resume probe target |
| evidence-label report | manual/tool/product evidence boundary |
| `resume_probe_result.json` | smallest post-resume health/proof check |
| `verification_after_resume.yaml` | claim validation after resume |
| `closeout.md` | final state, deferred action, or carried blocker |

The checker may validate a standalone review packet in `pre_ask` mode, but it
must report missing dependencies when closeout depends on absent blocker,
evidence, tool, mailbox, or proof reports.

## Review Packet Required Fields

Every PMO-facing packet should include:

```yaml
packet_id: HREV-YYYYMMDD-001
task_id: COAGENT-ARCH-LONGRUN-01
blocked_slice_id: <slice or proof node>
blocker_type: auth_required | license_required | gui_required | manual_review_required | approval_required | tool_unavailable | transport_timeout | invalid_result_packet | secret_risk
severity: info_review | medium_blocker | high_blocker | critical_stop
owner: <agent or department>
review_owner: MainAgent
safety_owner: SafetyComplianceAgent
user_action: <one concrete action>
reason: <why this blocks the task>
allowed_decisions:
  - approve
  - reject
  - rework
  - defer
  - done
  - manual_accept
  - manual_reject
  - need_more_context
last_safe_state: <saved state and what was not touched>
changed_files:
  - <project path or none>
evidence_paths:
  - <project path>
redaction_summary: <what was omitted>
dedupe_key: <task:slice:blocker:condition>
created_at: <timestamp or date>
expires_or_review_after: <timestamp, duration, or none>
safe_parallel_work:
  allowed: true | false
  scope:
    - <safe slice>
  blocked_claims:
    - <claim that must remain blocked>
resume_condition: <exact phrase, artifact, or evidence required>
post_resume_probe:
  probe_type: tool_health | file_exists | inventory_refresh | packet_validation | safety_preflight | no_probe_required
  target: <path, route, or packet>
verification_after_resume:
  owner: VerificationAgent
  required_checks:
    - <check>
forbidden_actions_while_waiting:
  - <forbidden action>
closeout_condition: <how the packet closes>
notification_readiness:
  enabled: false
  opt_in_record: null
  rate_limit: null
  audit_log_path: null
claim_boundaries:
  - <what this manual review does not prove>
```

## Required Checks

### User Ask Specificity

Reject if:

- `user_action` is vague;
- the packet asks "what should I do?";
- the action does not name the target tool, artifact, path, or decision;
- allowed decisions are missing or unsupported;
- resume condition cannot be checked.

### Blocker-Type Resume Mapping

Check blocker-specific rules:

| Blocker Type | Required Resume Rule |
|---|---|
| `auth_required` | user says auth is complete, then smallest account/tool health probe |
| `license_required` | user says license is cleared, then smallest MCP/tool health probe |
| `gui_required` | user names completed GUI step and artifact path, then read-only inventory/file check |
| `manual_review_required` | user chooses `manual_accept`, `manual_reject`, or `rework`; claim stays manual |
| `approval_required` | user approves exact path/action/scope; safety preflight before action |
| `tool_unavailable` | no blind retry; route health or fallback approval changes first |
| `transport_timeout` | internal repair/replay/checker result; no user ask by default |
| `invalid_result_packet` | repaired packet or repair note; result router validation |
| `secret_risk` | stop unsafe path; no automatic retry; safety review |

Reject mismatched probe types, blind retries, and user asks for internal
transport issues unless task direction or external approval is needed.

### Dedupe And Rate Limit

Reject if:

- active packets share the same `dedupe_key`;
- repeated same blocker creates a new ask instead of updating existing state;
- review-after timeout is missing for long waits;
- repeated blocker threshold does not link to retrospective closure.

### Redaction And Path Safety

Reject if:

- packet includes secrets, tokens, account-cache bodies, private Codex DB
  dumps, raw full transcripts, or unrelated personal paths;
- evidence paths are outside the project without an approved infrastructure
  exception;
- redaction summary is missing for auth/license/account/tool blockers.

### Safe Parallel Work

If safe parallel work is allowed, verify:

- scope is explicit;
- blocked claims remain blocked;
- worker cannot retry the blocked tool path;
- closeout carries or clears the blocker before final completion.

Reject safe-parallel claims that advance or promote blocked evidence.

### Manual Evidence Boundaries

Manual acceptance may support:

- visual acceptance;
- user approval of exact path/action/scope;
- confirmation that a GUI or login step was completed.

Manual acceptance does not prove:

- MWORKS/Sysplorer simulation correctness;
- UE planning truth;
- Fab asset import correctness beyond observed artifact presence;
- tool reliability;
- automated dispatch;
- Git integration safety.

Reject label inflation.

### Notification Readiness

Notification metadata may be present, but a packet is not notification-ready
unless it records:

- user opt-in;
- rate limit;
- dedupe key;
- redaction summary;
- test mode;
- audit log path;
- sender authority limited to MainAgent/PMO.

The checker must not send the notification.

## Modes

| Mode | Required Behavior |
|---|---|
| `pre_ask` | validate the packet before asking the user |
| `post_decision` | validate normalized decision and resume condition before work resumes |
| `closeout` | validate probe, verification, evidence boundaries, and closeout |
| `fixture` | run positive and negative human-review packet cases |

## Stable Finding Codes

| Code | Meaning |
|---|---|
| `HREV_PACKET_MISSING` | review packet missing |
| `HREV_USER_ACTION_VAGUE` | user ask is not one concrete action |
| `HREV_DECISION_VALUES_INVALID` | allowed decisions missing or unsupported |
| `HREV_BLOCKER_TYPE_INVALID` | blocker type unsupported |
| `HREV_SEVERITY_INVALID` | severity missing or unsupported |
| `HREV_OWNER_MISSING` | owner, review owner, or safety owner missing |
| `HREV_LAST_SAFE_STATE_MISSING` | last safe state missing |
| `HREV_RESUME_CONDITION_MISSING` | resume condition missing or unverifiable |
| `HREV_PROBE_MISMATCH` | post-resume probe does not match blocker type |
| `HREV_DUPLICATE_ACTIVE_ASK` | duplicate active dedupe key |
| `HREV_RETRY_UNSAFE` | auth/license/tool blocker retries without changed evidence |
| `HREV_REDACTION_MISSING` | redaction summary missing |
| `HREV_SECRET_OR_PRIVATE_STATE_RISK` | packet emits secret, account cache, private DB dump, raw transcript, or unrelated personal path |
| `HREV_SAFE_PARALLEL_OVERCLAIM` | safe parallel work promotes blocked claim |
| `HREV_MANUAL_EVIDENCE_INFLATED` | manual review is claimed as tool/product/planning proof |
| `HREV_NOTIFICATION_READINESS_MISSING` | notification-ready claim lacks opt-in, rate-limit, dedupe, redaction, test mode, or audit log |
| `HREV_CLOSEOUT_MISSING` | closeout condition or closeout evidence missing |
| `HREV_DEPENDENCY_MISSING` | required blocker/evidence/tool/mailbox/proof report missing |
| `HREV_FORBIDDEN_SIDE_EFFECT` | checker attempted or declared notification/tool/runtime/Git mutation |

## Fixture Matrix

Positive fixtures:

| Fixture | Expected |
|---|---|
| MWORKS license packet with one action, last safe state, resume phrase, and health probe | `pass` |
| UE/Fab manual import packet with artifact path and planning truth still blocked | `pass` |
| visual review packet with `manual_accept/manual_reject/rework` and manual evidence boundary | `pass` |
| destructive Git approval packet with exact path/action/scope and safety preflight | `pass_with_warnings` |
| transport timeout packet that records no user action by default | `pass` |

Negative fixtures:

| Fixture | Expected Codes |
|---|---|
| ask says "what should I do about UE?" | `HREV_USER_ACTION_VAGUE` |
| missing resume condition | `HREV_RESUME_CONDITION_MISSING` |
| unsupported decision value | `HREV_DECISION_VALUES_INVALID` |
| duplicate active dedupe keys | `HREV_DUPLICATE_ACTIVE_ASK` |
| auth blocker retries tool without user or changed evidence | `HREV_RETRY_UNSAFE` |
| packet includes account cache body or raw Codex DB dump | `HREV_SECRET_OR_PRIVATE_STATE_RISK` |
| safe parallel work claims blocked simulation evidence is valid | `HREV_SAFE_PARALLEL_OVERCLAIM` |
| manual visual accept claims UE planning truth | `HREV_MANUAL_EVIDENCE_INFLATED` |
| notification-ready claim lacks opt-in or audit log | `HREV_NOTIFICATION_READINESS_MISSING` |

## Output

The checker should emit the shared validator envelope:

```json
{
  "schema_version": "coagent.validator_report.v1",
  "validator": "human_review_package_checker",
  "task_id": "COAGENT-ARCH-LONGRUN-01",
  "mode": "pre_ask",
  "decision": "fail_before_dispatch",
  "ok": false,
  "finding_codes": ["HREV_USER_ACTION_VAGUE"],
  "findings": [
    {
      "code": "HREV_USER_ACTION_VAGUE",
      "severity": "error",
      "path": "review_packet.yaml",
      "message": "user_action does not name one concrete action",
      "remediation": "replace vague ask with exact tool/artifact/path/action and allowed decisions"
    }
  ],
  "dependency_reports": [
    {
      "validator": "blocker_packet_validator",
      "decision": "needs_dependency",
      "required_for": "blocker-specific resume semantics"
    }
  ],
  "evidence_paths": [
    "CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/human_review_intervention_ux_design.md"
  ],
  "side_effects": {
    "declared": ["read_project_files", "write_validator_report"],
    "forbidden": ["notification_send", "gui_automation", "mcp_or_tool_call", "runtime_mutation", "git_mutation", "credential_access"]
  },
  "claim_boundaries": [
    {
      "claim": "review packet is ready to ask the user",
      "supported": false,
      "limitations": "checker does not send notification or perform external action"
    }
  ],
  "next_action": "revise PMO-facing packet before user ask"
}
```

## Implementation Boundary

The first implementation should be read-only and fixture-backed. It may read
project-owned review packets, blocker packets, mailbox files, tool capability
cards, evidence-label reports, proof packages, and closeout files. It may write
validator reports under `Results/coagent_validators/`.

It must not:

- ask the user automatically;
- send email or desktop notifications;
- open or automate GUI windows;
- call MCP/tools or retry blocked tools;
- inspect credentials, tokens, account caches, private Codex DBs, or raw full
  transcripts;
- approve destructive actions;
- stage, commit, push, delete, or move files;
- mutate runtime task state or conversation state.

## Rollout Position

Run after the shared validator envelope and blocker packet validator exist.
Run before Candidate E, supervised manual rehearsal closeout, notification
transport, or any route where a human decision blocks MWORKS, UE/Fab, Git,
visual review, or transport behavior.

It feeds:

- runbook readiness;
- implementation approval;
- evidence label doctor;
- retrospective closure after duplicate asks or unsafe retries;
- future notification transport approval.
