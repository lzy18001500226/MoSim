# COAGENT-ARCH-LONGRUN-01 Human Review And Intervention UX Design

Date: 2026-05-30
Status: design draft

## Purpose

Turn human intervention from an ad-hoc chat interruption into a concrete
review experience that is safe, resumable, deduplicated, and auditable.

This document extends:

- `safety_human_intervention_protocol.md`
- `blocker_packet_templates.md`
- `blocker_packet_validator_design.md`
- `candidate_e_auth_license_interruption_proof_package.md`
- `end_to_end_task_operating_runbook.md`

It is design-only. It does not implement email, desktop notification, GUI
automation, credential handling, Codex transport, MCP calls, or live dispatch.

## Problem

CoAgent cannot be useful for long technical tasks if human intervention is
only "ask the user something". The user needs one specific action, enough
state to make the decision, and a clear resume condition. CoAgent needs a
durable packet so work can resume after context compaction, session loss, or a
different conversation taking over.

The review design must prevent:

- vague questions such as "what should I do?";
- repeated asks for the same unresolved blocker;
- retry loops after login, license, GUI, or activation blockers;
- leaking credentials, account cache, private paths, or raw transcript;
- presenting manual review as automated proof;
- continuing a blocked tool slice while claiming its evidence is valid;
- losing the last safe state after the user finishes a manual action.

## UX Principle

Human intervention is a state transition, not a failure message.

```text
working
  -> review_needed
  -> waiting_for_user
  -> user_decision_recorded
  -> resume_or_hold
  -> verification
  -> closeout
```

Only MainAgent/PMO sends user-facing asks. Worker conversations can propose a
review packet, but they do not ask the user directly for external action.

## Review Packet Shape

Every PMO-facing review packet should be reducible to this display block:

```text
Need: one specific action.
Reason: why this blocks the task.
Last safe state: what has been saved and what was not touched.
Decision required: allowed decision values.
Resume condition: exact phrase/evidence CoAgent needs after the action.
Can continue elsewhere: yes/no and which slices remain safe.
Timeout/default: what happens if no decision arrives.
```

The durable packet should contain:

```text
packet_id
task_id
blocked_slice_id
blocker_type
severity
owner
review_owner
user_action
allowed_decisions
last_safe_state
changed_files
evidence_paths
redaction_summary
dedupe_key
created_at
expires_or_review_after
safe_parallel_work
resume_condition
post_resume_probe
verification_after_resume
forbidden_actions_while_waiting
closeout_condition
```

## Severity Levels

| Severity | Meaning | PMO Behavior |
|---|---|---|
| `info_review` | user may inspect but work is not blocked | record review opportunity; continue safe work |
| `medium_blocker` | one slice is blocked, other slices may continue | ask once, continue only declared safe slices |
| `high_blocker` | important task path is blocked by auth, license, GUI, destructive approval, or manual acceptance | stop affected path and ask user |
| `critical_stop` | unsafe path, secret risk, broad destructive action, or state corruption risk | stop related work and require explicit user decision |

Severity never grants permission to bypass safety. It only controls urgency and
safe parallel-work rules.

## Allowed User Decisions

Use a small vocabulary so downstream resume logic is deterministic.

| Decision | Meaning | Required Follow-Up |
|---|---|---|
| `approve` | perform the exact requested action/scope | run the stated post-resume probe or next safe step |
| `reject` | do not perform this action | close blocked slice or redesign route |
| `rework` | packet is understandable but action/scope is wrong | revise review packet before continuing |
| `defer` | keep blocker open for later | record hold state and safe parallel work |
| `done` | user completed external action | run smallest health/proof probe |
| `manual_accept` | user accepts a manual review artifact | record manual evidence label and continue only claims supported by it |
| `manual_reject` | user rejects a manual review artifact | produce rework task and do not promote evidence |
| `need_more_context` | user cannot decide from packet | revise packet; do not repeat the same ask |

Free-form user comments can be attached, but they must be normalized into one
of these decisions before automation resumes.

## Dedupe And Rate Limit

Every review packet needs a `dedupe_key`:

```text
<task_id>:<blocked_slice_id>:<blocker_type>:<normalized_external_condition>
```

Rules:

- one active ask per dedupe key;
- repeated same blocker updates the existing packet instead of asking again;
- retries after suspected auth/license/login blockers require user
  confirmation or changed evidence;
- repeated same blocker three times triggers incident/retrospective handling;
- notification transport, when later approved, must enforce the same dedupe
  rule before sending email or desktop alerts.

## Redaction

The user-facing packet must not contain:

- tokens, API keys, SSH keys, cookies, browser profiles, or account-cache
  bodies;
- private Codex SQLite/JSONL dumps;
- full raw transcript;
- unrelated personal paths;
- long command outputs when a short error class is enough.

The durable packet may reference evidence paths inside the project. If an
external path is relevant, the packet records only the path and reason when the
user explicitly approved that infrastructure exception.

## Resume Mapping

Each blocker type maps to a different resume path.

| Blocker Type | User Ask | Resume Condition | First Probe After Resume |
|---|---|---|---|
| `auth_required` | log in, refresh account, approve VPN/session | user says auth is complete | smallest account/tool health probe |
| `license_required` | activate MWORKS/UE/plugin license | user says license dialog is cleared | smallest MCP/tool health probe |
| `gui_required` | complete named GUI dialog or import step | user says GUI step is complete and artifact path exists | read-only inventory or file existence check |
| `manual_review_required` | inspect specific artifact and choose accept/rework/reject | user gives normalized decision | review packet closeout, no tool retry unless needed |
| `approval_required` | approve exact destructive/high-risk action | user cites exact path/action/scope | preflight safety check before action |
| `tool_unavailable` | no user action unless tool is externally down | health evidence changes or fallback approved | route-specific health probe |
| `transport_timeout` | usually no user action | transport config/evidence changes | bounded dispatch or replay check |
| `invalid_result_packet` | usually no user action | repaired packet or repair note exists | result router validation |
| `secret_risk` | confirm cleanup policy if needed | secret not emitted and unsafe path stopped | safety review, no automatic retry |

## Required Cases

### MWORKS License Or Login

Ask:

```text
Need: Please open/activate MWORKS/Sysplorer until the license/login prompt is cleared.
Reason: the simulation slice cannot produce valid MWORKS evidence while the tool is blocked.
Last safe state: source files and task state are saved; no simulation claim was promoted.
Resume condition: reply "MWORKS ready" after the prompt is cleared.
Can continue elsewhere: yes, design/docs/research slices only.
```

Resume:

- run the smallest MCP health probe;
- then run only the smallest relevant model check before simulation;
- keep previous failed tool output labeled as blocker evidence, not simulation
  evidence.

### UE/Fab Manual Import Or Scene Setup

Ask:

```text
Need: Complete the named UE/Fab import or editor dialog for the specified project.
Reason: CoAgent cannot claim scene-source readiness or planning truth until the asset exists in the project and the capability card is refreshed.
Last safe state: current scene-source inventory and blocker packet are saved.
Resume condition: reply with the project/map path that now exists.
Can continue elsewhere: yes, planning-truth schema and documentation only.
```

Resume:

- refresh scene-source inventory;
- do not infer planning readiness from rendering or visual presence;
- require truth-artifact manifest before navigation/path-planning claims.

### Visual Scene Or Simulation Review

Ask:

```text
Need: Review the named screenshot/video/result asset and choose manual_accept, manual_reject, or rework.
Reason: this acceptance depends on human visual judgment and cannot be replaced by a script.
Last safe state: artifact paths and generation labels are recorded.
Resume condition: reply with the decision and any visible issue.
Can continue elsewhere: yes, but report claims stay blocked until decision.
```

Resume:

- record `manual_review` evidence label;
- keep manual acceptance separate from planning truth or numerical
  correctness;
- create rework task if rejected.

### Destructive Or Broad Git/File Action

Ask:

```text
Need: Approve or reject the exact path/action/scope.
Reason: this action may delete, move, stage, commit, or rewrite high-risk project state.
Last safe state: no destructive action has been executed.
Resume condition: reply with approve/reject and the exact path/action/scope.
Can continue elsewhere: yes, read-only inventory and planning only.
```

Resume:

- rerun path and Git-risk preflight;
- require inventory and rollback plan before action;
- never convert a vague approval into broad `git add -A`, delete, reset, or
  force-push permission.

### Invalid Packet Or Transport Timeout

Ask:

```text
Need: no user action by default.
Reason: this is an internal CoAgent transport/packet issue.
Last safe state: dispatch attempt, logs, and expected result path are saved.
Resume condition: internal repair, replay, or checker result exists.
Can continue elsewhere: yes, if no blocked claim is promoted.
```

Escalate to user only if:

- the packet content is ambiguous and changes task direction;
- repair requires changing runtime/transport behavior outside approved scope;
- repeated failures hit the incident threshold.

## Notification Design Boundary

Email and desktop notifications are desirable for long waits, but they remain
gated. A later implementation must prove:

- packet schema exists;
- dedupe key works;
- severity and rate limit work;
- redaction works;
- audit log is written;
- test mode exists;
- user opt-in exists;
- no secrets enter message body;
- no notification is sent from worker conversations directly.

Until then, the PMO-facing review packet is the source of truth.

## Audit Log

Each user-intervention cycle should eventually produce:

```text
review_packet.yaml
user_decision.yaml
resume_probe_result.json
verification_after_resume.yaml
closeout.md
```

If the user never responds, close the slice as deferred with the last safe
state and resume condition. Do not keep retrying the same blocked operation.

## Future Checker

The future checker should validate:

- required review-packet fields;
- allowed decision values;
- dedupe key uniqueness among active asks;
- no vague user ask;
- no forbidden secret/path content;
- blocker type has a resume condition;
- post-resume probe matches blocker type;
- manual review evidence is not inflated into tool/product proof;
- safe parallel work does not promote blocked claims;
- notification fields exist before notification transport is enabled.

This should become a read-only implementation slice after the shared validator
envelope and blocker packet validator exist.
