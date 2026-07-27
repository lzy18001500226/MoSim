# COAGENT-ARCH-LONGRUN-01 Safety And Human Intervention Protocol

Date: 2026-05-30
Status: phase 2 draft

## Purpose

Define when CoAgent must stop, ask the user, or continue elsewhere during
long-running multi-conversation work.

## Principle

Manual intervention is not failure. It is a task state with a last safe state
and a resume path.

## Blocker Classes

| Class | Examples | Default Action |
|---|---|---|
| `auth_required` | login, token, account pool, VPN | stop affected slice, ask PMO to notify user |
| `license_required` | MWORKS activation, UE plugin license | stop affected tool loop |
| `gui_required` | Fab import, manual UE dialog, visual scene review | create manual review packet |
| `approval_required` | destructive delete, broad move, force push | stop and ask user |
| `data_required` | missing PX4 logs, vehicle config, actuator data | ask for exact missing data |
| `tool_unavailable` | MCP down, editor listener missing | fallback only if allowed; otherwise block |
| `unsafe_path` | write outside project boundary | immediate stop |
| `secret_risk` | token/key/profile material | immediate stop and sanitize |
| `incident_required` | repeated failure, session corruption, Git lock | switch to incident response |

## User Ask Format

Only MainAgent/PMO sends user-facing asks.

Format:

```text
Need: one specific action.
Reason: why this blocks the task.
Last safe state: what has already been saved.
Resume condition: what to tell CoAgent after the action.
Can continue elsewhere: yes/no.
```

## Notification Design

Future email/desktop notification is useful but not implemented in this task.

Before implementation, the design requires:

- notification packet schema;
- dedupe key;
- rate limit;
- severity levels;
- safe redaction;
- no secrets in message body;
- user opt-in;
- test mode;
- audit log.

## Retry Policy

Retrying is allowed only when:

- error is transient;
- command is safe;
- retry count is bounded;
- no login/license prompt is suspected;
- retry will not duplicate writes or corrupt state.

Stop after:

- 3 repeated same blockers;
- one unsafe-path or secret-risk event;
- one destructive approval requirement;
- one GUI/login/license blocker requiring user action.

## Long Task Continuation

If one slice blocks, Dispatch decides whether other slices can continue.

Example:

- MWORKS activation blocks simulation tuning.
- Method research, context design, and documentation may continue.
- Simulation claims remain blocked until activation is resolved.

## Human Review Points

Human review should be required for:

- visual UE scene correctness;
- final simulation behavior or video audit;
- project direction changes;
- broad Git/file restructuring;
- accepting unresolved safety risks;
- enabling automatic conversation/worktree/email features.

## Resume Packet Requirements

A resume packet must include:

- task id;
- blocked slice;
- blocker class;
- last safe state;
- files already changed;
- command/tool to retry, if safe;
- verification after resume;
- context pack version.

## Unsafe Actions

Never proceed without explicit user approval for:

- deleting or moving broad source/reference trees;
- force push/history rewrite;
- writing credentials or tokens;
- reading private paths outside approved boundary;
- uncontrolled external tool automation;
- automatic email/notification sender activation.
