# CoAgent Human Intervention UX

Date: 2026-05-29

Status: design baseline plus Weixin gateway smoke update. This document
specifies notification behavior and templates. It now also records the approved
cc-connect Weixin smoke adapter; it does not approve unattended automation.

## UX Goal

When a task needs human action, the user should receive one clear request:

```text
what is blocked
why automation stopped
what human action is needed
where the evidence is
how the task resumes
```

The system should not keep retrying a login/license/GUI/manual-review blocker
until the desktop, tool session, or task context degrades.

## Intervention Classes

| Class | Canonical state | Examples | Default action |
|---|---|---|---|
| `auth_required` | `auth_required` | MWORKS login, Epic/Fab login, Unreal license prompt, GitHub auth, VPN | Stop retries, write blocker packet, ask user to restore access. |
| `input_required` | `input_required` | Missing log file, ambiguous acceptance, unknown controller mapping | Ask one compressed question through PMO. |
| `approval_required` | `review_required` or `input_required` | delete/move broad files, force push, external write, destructive cleanup | Stop before action and request explicit approval. |
| `manual_review_required` | `review_required` | simulation animation, UE scene truth quality, report/video acceptance | Produce evidence bundle and wait for user/reviewer. |
| `incident_required` | `blocked` or `failed` | repeated crash, corrupted session, stale path, Git index lock, runaway process | Freeze risky work, capture evidence, propose recovery. |

## Notification Levels

| Level | Meaning | Channel |
|---|---|---|
| `thread_only` | Current conversation is active and low-risk. | Main conversation message. |
| `project_packet` | Durable record is needed for recovery. | `Results/agent_packets/*.yaml` or future task ledger record. |
| `gateway_requested` | User may be absent and task is blocked on human action. | Approved gateway adapter such as cc-connect Weixin, when explicitly enabled. |
| `email_requested` | Email specifically requested by policy or user. | Future email adapter after approval. |
| `immediate_stop` | Continuing may cause data loss, secret exposure, license churn, or destructive writes. | Stop task and report in main conversation. |

External notification escalation requires:

- blocker class is `auth_required`, `approval_required`, or
  `incident_required`, or a critical-path `input_required` has exceeded its
  checkpoint timeout;
- a dedupe key exists so repeated failures do not spam the user;
- the email body contains no tokens, secrets, private account data, or large raw
  logs;
- a resume packet exists.

Current approved gateway:

- `cc-connect` Weixin smoke path, implemented by
  `CoAgent/gateway/cc_connect_weixin.py`;
- default is dry-run;
- real sending requires explicit `--send`;
- only `auth_required`, `approval_required`, `manual_review_required`, and
  `incident_required` blocker classes are allowed;
- review packets can escalate only for review decisions requiring user action;
- adapter output is redacted, deduped, and audited under ignored
  `Results/coagent_gateway/`;
- cc-connect runtime socket state must stay on WSL local storage, not `/mnt/c`.

Current result-router integration:

- `CoAgent/result_router/result_router.py import --notify-weixin` is the
  approved bridge from result packet review to gateway notification.
- Accepted result packets do not notify.
- Review-required, blocked, failed, or auth-required packets produce a
  notification packet under ignored `Results/agent_packets/notifications/`.
- The bridge is dry-run by default. Real sending requires both
  `--send-weixin` and `--weixin-session`, and should normally pass
  `--omit-weixin-message-in-audit`.
- The task/runtime/result packet remains the source of truth. Weixin is only
  the user-intervention surface.

## Blocker Notification Contract

Required fields:

```text
notification_id
task_id
parent_goal
owner_conversation
state
severity
class
dedupe_key
blocked_surface
human_action_required
why_now
evidence_paths
resume_packet_path
retry_policy
expires_or_recheck_after
safe_to_continue_without_user
```

If a worker cannot fill these fields, it should not escalate by email. It
should return a normal `blocked` result packet for PMO review.

## User Ask Rules

1. Ask for one decision or action at a time.
2. Include the exact path or UI surface that needs user action.
3. State what automation already tried and why it stopped.
4. State what will happen after the user resolves it.
5. Do not include secrets or account identifiers unless the user explicitly
   needs them to identify the session.
6. Do not let multiple workers independently ask the user about the same
   blocker. PMO owns the final user-facing ask.

## Retry And Circuit Breaker Rules

| Blocker | Allowed retry behavior |
|---|---|
| login/license/auth prompt | One health recheck after user action. No blind loop. |
| GUI not responding | One targeted probe, then incident packet. |
| MCP listener missing | One read-only health probe, then report exact server/tool failure. |
| missing file/input | Search approved project paths once, then ask. |
| destructive approval | No retry. Wait for explicit approval. |
| Git explosion/index lock | Stop main-thread Git work; route to Git/integration owner when available. |

## Resume Packet

A resume packet should allow a new conversation to continue without reading the
full chat:

```text
task_id
blocked_at
blocker_class
last_safe_state
human_action_completed_checkbox
commands_to_recheck
expected_success_signal
next_owner
acceptance_remaining
```

The resume packet is not a command to proceed automatically. It is the minimal
safe context needed after the human resolves the blocker.

## External Adapter Guardrails

Before any external sender is used beyond the approved Weixin smoke path, the
design must be extended with:

- configured recipient policy;
- sender identity and rate limits;
- local dry-run mode;
- redaction rules;
- audit log path;
- opt-out and quiet-hours behavior;
- failure behavior when mail sending fails;
- tests proving no secrets are included.

Until a sender has an approved adapter, `gateway_requested` or
`email_requested` means "write a packet that is ready for that channel", not
"send automatically".

## Examples

### MWORKS License Lost

```text
class: auth_required
blocked_surface: MWORKS.Sysplorer simulation
human_action_required: Reactivate or log in to MWORKS, then tell PMO to resume.
why_now: Simulation evidence cannot be produced without official model access.
retry_policy: Recheck Sysplorer MCP health once after user confirms login.
```

### Unreal Editor Crash

```text
class: incident_required
blocked_surface: UE Editor write probe
human_action_required: Close crash reporter and confirm whether to reopen Editor.
why_now: Continuing write probes can corrupt transient Entry-map state.
retry_policy: Run read-only editor listener health before any future write probe.
```

### PX4 Log Missing Required Signals

```text
class: input_required
blocked_surface: parameter-identification data sufficiency
human_action_required: Provide actuator outputs or confirm estimation should
continue with reduced identifiable parameter set.
why_now: The current log cannot identify motor efficiency parameters reliably.
retry_policy: Continue only after user selects reduced-scope or supplies data.
```
