# COAGENT-ARCH-LONGRUN-01 Blocker Packet Templates

Date: 2026-05-30
Status: design draft

## Purpose

Make blocked work resumable without raw chat. A blocker packet records the last
safe state, the exact external condition, and the resume rule.

## Common Fields

Every blocker packet should include:

- `task_id`
- `blocked_task_id`
- `blocker_type`
- `severity`
- `owner`
- `last_safe_state`
- `failed_command_or_tool`
- `evidence_paths`
- `human_action_required`
- `resume_condition`
- `dedupe_key`
- `retry_policy`
- `created_at`

## Transport Timeout Blocker

Use when a department conversation is resumed but no result packet appears
within the approved budget.

```text
blocker_type: transport_timeout
severity: medium
last_safe_state: task packet written and dispatch process started
failed_command_or_tool: codex exec resume <thread id>
human_action_required: none by default
resume_condition: dispatch can be retried only after transport logs are
reviewed or timeout class is explicitly changed
retry_policy: no automatic retry; one manual retry allowed after packet
template or transport config is adjusted
```

Required evidence:

- stdout log;
- stderr log;
- run summary;
- process cleanup result;
- expected result path.

## Invalid Result Packet Blocker

Use when a worker writes a packet that the router rejects.

```text
blocker_type: invalid_result_packet
severity: medium
last_safe_state: result file exists but did not import
failed_command_or_tool: CoAgent/result_router/result_router.py import
human_action_required: no, unless the content is ambiguous
resume_condition: worker repairs packet or MainAgent converts substance into
router-compatible packet with repair note
retry_policy: no blind retry; include validator finding in repair prompt
```

Required evidence:

- invalid result file;
- review JSON;
- parsed archive if available;
- repaired packet path if repaired.

## Auth Or License Blocker

Use when a tool requires manual login, activation, account approval, or GUI
authorization.

```text
blocker_type: auth_or_license_required
severity: high
last_safe_state: source changes preserved; tool sequence stopped
failed_command_or_tool: exact MCP/tool command
human_action_required: user must log in, activate, or approve GUI prompt
resume_condition: user confirms tool is available and smallest health probe
passes
retry_policy: do not retry more than once without user confirmation
```

## Manual Review Blocker

Use when visual, safety, legal, product, or acceptance review cannot be
automated.

```text
blocker_type: manual_review_required
severity: medium_or_high
last_safe_state: artifacts generated and paths recorded
human_action_required: one concrete review question
resume_condition: user gives accept/rework/reject decision
retry_policy: none until decision
```

## Destructive Action Blocker

Use before deleting, force pushing, rewriting history, moving large source
batches, or touching files outside approved scope.

```text
blocker_type: destructive_action_approval_required
severity: high
last_safe_state: no destructive action executed
human_action_required: explicit approval of target path and action
resume_condition: approval cites exact path/action
retry_policy: not applicable
```

## Current Architecture Consequence

The RuntimePlatformAgent timeout in `COAGENT-ARCH-LONGRUN-01-RUNTIME-01`
should be represented by `transport_timeout` in the next implementation
slice. Until then, it remains recorded in the shared task board and runtime
task state.
