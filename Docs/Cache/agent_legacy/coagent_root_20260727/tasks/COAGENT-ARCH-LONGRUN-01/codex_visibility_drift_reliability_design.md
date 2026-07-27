# COAGENT-ARCH-LONGRUN-01 Codex Visibility Drift Reliability Design

Date: 2026-05-30
Status: design contract for recurring visibility metadata drift

## Purpose

CoAgent depends on visible Codex conversations as review and task surfaces, but
durable state is still project-owned task files and runtime records. During
`COAGENT-ARCH-LONGRUN-01`, `check_department_visibility.py` repeatedly found
that DispatchAgent's visible thread metadata drifted in the WSL alternate Codex
database:

```text
/home/linux/.codex/sqlite/state_5.sqlite
```

The existing `codex_session_repair.py sync-visible --apply` path restored the
rows, but repeated manual repair is not a reliable dispatch boundary. This
document turns the recurrence into an explicit pre-dispatch reliability design.

This is a design artifact. It does not implement automatic dispatch,
automatic conversation creation, app-server transport, or unattended repair.

## Observed Failure

Symptom:

```text
python3 CoAgent/doctor/check_department_visibility.py
-> AssertionError: DispatchAgent missing valid state DB row or rollout file
```

Known repair:

```text
python3 CoAgent/dispatch/codex_session_repair.py sync-visible \
  --thread-id <department-thread-id> \
  --thread-name <department-thread-name> \
  --cwd /mnt/c/Users/HP/Desktop/MoSim \
  --source-codex-home /home/linux/.codex \
  --target-codex-home /home/linux/.codex \
  --target-codex-home /mnt/c/Users/HP/.codex \
  --apply
```

Current recurrence:

- DispatchAgent drift appeared during verification after previous successful
  sync.
- Re-syncing all non-MainAgent departments restored all 11 active-visible rows.
- The recurrence is now tracked as P47 and must be treated as transport/session
  state reliability risk.

Confirmed drift surface:

```text
WSL main DB: correct vscode/vscode row, canonical cwd, short title.
Windows DB: correct vscode/vscode row, canonical cwd, short title.
WSL alternate DB: reverts to source=cli, thread_source=user, lowercase cwd,
and the original long bootstrap prompt as title/preview/first_user_message.
```

The current design should therefore treat the alternate DB as the first
suspect surface, while still checking all indexes, rollout paths, and DB rows.

## Reliability Principle

```text
department visibility must be proved immediately before dispatch,
and drift must produce either a repaired state or a blocker packet
```

No scoped department dispatch should start from stale, partially visible, or
unverified Codex metadata.

## Visibility Invariants

For each active department conversation, these must hold:

| Surface | Required State |
|---|---|
| project registry | `status=active_visible`, correct thread id and title |
| WSL session index | thread id and title present |
| Windows session index | thread id and title present |
| WSL main DB | `source=vscode`, `thread_source=vscode`, `has_user_event=1`, `archived=0`, canonical `cwd` |
| WSL alternate DB | same as WSL main DB |
| Windows DB | same visibility row and rollout path |
| rollout file | exists for the stored rollout path |
| title | starts with the project `MoSim` title prefix and matches registry |

The project runtime task state may link a conversation only after these
invariants are true.

## Pre-Dispatch Gate

Before dispatching a packet to a visible department conversation:

1. run `check_department_visibility.py`;
2. if it passes, record `visibility_gate=passed`;
3. if it fails, run a bounded `diagnose` pass for the affected department;
4. if the failure matches known metadata drift and user-approved repair policy
   exists for the current task, run `sync-visible --apply`;
5. rerun `check_department_visibility.py`;
6. if it still fails, create a blocker packet and do not dispatch.

The gate may repair metadata only for registered CoAgent department sessions.
It must not create new conversations, delete sessions, rewrite unrelated Codex
history, or change project task goals.

## Repair Policy

Allowed automatic repair, after this design is implemented and approved:

- normalize registered department rows in WSL and Windows Codex metadata;
- copy or preserve rollout path references for the same thread id;
- update session indexes for the same thread id;
- write backup copies before modifying Codex metadata.

Forbidden during repair:

- creating a new conversation;
- deleting old sessions;
- changing thread titles except to the registry title for the same id;
- changing global Codex provider config;
- touching credentials, account cache, browser profiles, or unrelated user
  directories;
- repairing a non-registered thread;
- proceeding to dispatch after failed repair.

## Blocker Packet

If repair is not safe or fails, emit:

```yaml
blocker_class: codex_visibility_drift
task_id:
department:
thread_id:
thread_name:
failed_check:
diagnose_output_path:
repair_attempted: true | false
repair_output_path:
last_safe_state:
user_action_required:
resume_condition:
dedupe_key:
```

Recommended dedupe key:

```text
codex_visibility_drift:<department>:<thread_id>
```

This prevents repeated user prompts or repeated dispatch attempts against the
same broken conversation state.

## Evidence Records

Future implementation should save:

```text
Results/coagent_transport/visibility_checks/<timestamp>-<department>.json
Results/coagent_transport/visibility_repairs/<timestamp>-<department>.json
Results/agent_packets/blockers/<task-id>-<department>-visibility-drift.yaml
```

Evidence must include:

- check command;
- failing department;
- failing surface;
- before/after DB/index status;
- backup paths;
- repair command;
- final pass/fail.

## State Machine

| State | Meaning | Next |
|---|---|---|
| `visible_verified` | all invariants pass | dispatch allowed |
| `drift_detected` | doctor failed for registered thread | diagnose |
| `repair_allowed` | failure matches known drift and repair is in scope | repair |
| `repair_succeeded` | doctor passes after sync | dispatch allowed |
| `repair_failed` | doctor still fails | blocker |
| `repair_forbidden` | unknown/non-registered/external-risk failure | blocker |
| `blocked_visibility` | blocker packet created | wait for repair/user decision |

Dispatch may only start in `visible_verified` or `repair_succeeded`.

## Relationship To Existing Documents

- `codex_visible_thread_sop.md` remains the creation and manual visibility SOP.
- `transport_reliability_findings.md` records observed timeout and schema
  failures.
- This document covers recurring metadata drift after a thread is already
  registered and visible.
- `blocker_packet_templates.md` should later add `codex_visibility_drift` as a
  first-class blocker class.

## Future Implementation Slice

Add a later implementation item:

```text
COAGENT-IMPL-NEXT-22: Codex Visibility Drift Gate
```

Scope:

- wrap `check_department_visibility.py` and `codex_session_repair.py diagnose`
  into a read-only pre-dispatch check;
- add an approved repair mode for registered department threads only;
- write before/after evidence records;
- emit `codex_visibility_drift` blocker packets when repair is unsafe or fails;
- integrate the gate before `codex exec resume` or any future dispatch path.

Acceptance:

- clean department registry passes without repair;
- simulated DispatchAgent alternate-DB drift is detected;
- approved repair restores visibility and records evidence;
- unknown thread id produces blocker, not repair;
- failed repair blocks dispatch;
- no new conversation is created;
- no unrelated Codex history, credentials, provider config, or project files are
  modified.

## Open Questions

- The root cause of WSL alternate DB drift is not yet known. Candidate causes
  include Codex App/VSCode refresh behavior, multiple state DB writers, or stale
  session metadata replay.
- The first implementation should prioritize safe detection and bounded repair,
  not root-cause changes to Codex internals.
- If drift continues after the gate exists, RuntimePlatformAgent should open an
  incident review and compare WSL main DB, WSL alternate DB, Windows DB, rollout
  files, and session indexes over time.
