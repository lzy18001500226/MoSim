# COAGENT-ARCH-LONGRUN-01 Transport Timeout Hardening Design

Date: 2026-05-30
Status: design contract for `COAGENT-IMPL-NEXT-12`

## Purpose

Visible Codex conversation transport is real but not reliable enough for
unattended multi-conversation work. `COAGENT-ARCH-LONGRUN-01-RUNTIME-01`
showed that a dispatch can consume the 60 second budget on startup/plugin/MCP
noise, leave a background process alive, leave a dispatch edge open, and later
produce a result packet after the timeout summary was written.

This document defines the hardening design for timeout classes,
plugin-sync/startup noise, late results, cleanup evidence, blocker packets, and
post-timeout reconciliation.

This is design only. It does not run dispatch, change transport, kill
processes, create conversations, alter Codex configuration, or implement app-
server transport.

## Observed Failure Class

Evidence:

- `Results/coagent_transport/runs/COAGENT-ARCH-LONGRUN-01-RUNTIME-01.summary.md`
- `Results/coagent_transport/runs/COAGENT-ARCH-LONGRUN-01-RUNTIME-01.json`
- `Results/coagent_transport/runs/COAGENT-ARCH-LONGRUN-01-RUNTIME-01.stdout.log`
- `Results/coagent_transport/runs/COAGENT-ARCH-LONGRUN-01-RUNTIME-01.stderr.log`
- `Results/agent_packets/tasks/coagent_architecture/COAGENT-ARCH-LONGRUN-01-RUNTIME-01.yaml`
- `transport_reliability_findings.md`

Current inconsistency:

```text
summary: result_file_exists=false, alive=true, done=false
later state: result packet exists
runtime edge: original run metadata shows status=open
```

The correct design response is not "just wait longer". The response is a
reconcileable state machine that can distinguish no result, late result,
invalid result, successful import, live process, dead process, and open edge.

## Core Rule

```text
every dispatch attempt ends in exactly one durable closeout state:
accepted result, review-required result, invalid-result blocker,
transport-timeout blocker, canceled dispatch, or explicit retry proposal
```

An attempt must not remain as "maybe still running" without a pollable record,
cleanup outcome, and next safe action.

## Non-Goals

`COAGENT-IMPL-NEXT-12` must not:

- enable unattended department dispatch by default;
- create new conversations;
- implement app-server transport;
- globally disable Codex plugins or change user Codex config;
- modify account caches, credentials, browser profiles, or provider settings;
- expand MCP/tool surfaces;
- kill arbitrary processes;
- auto-retry dispatch without a changed condition;
- hide late results or overwrite timeout evidence.

## Dispatch Attempt State Machine

| State | Meaning | Next |
|---|---|---|
| `planned` | command and paths known, not started | start or cancel |
| `started` | process launched, edge opened, logs allocated | poll |
| `waiting_for_result` | process alive, result missing | continue until budget |
| `result_detected` | result file exists | import/validate |
| `imported` | result packet imported into runtime | close edge |
| `invalid_result` | result exists but router/validator rejects it | invalid-result blocker |
| `timeout_no_result_alive` | budget exceeded, result missing, process alive | cleanup or hold per policy |
| `timeout_no_result_dead` | budget exceeded, result missing, process dead | timeout blocker |
| `timeout_late_result` | timeout summary exists, later result appears | reconcile result |
| `cleanup_succeeded` | targeted child process stopped or detached safely | timeout blocker or retry proposal |
| `cleanup_failed` | process still alive or cannot be identified safely | blocker with manual action |
| `edge_closed` | runtime conversation edge closed | closeout complete |
| `retry_proposed` | next attempt requires changed timeout class/config/template | review required |

Only these terminal closeout states are allowed:

- `accepted_result`
- `review_required_result`
- `invalid_result_blocker`
- `transport_timeout_blocker`
- `canceled`
- `retry_proposal_pending_review`

## Timeout Classes

| Class | Budget | Intended Use | Automatic Retry |
|---|---:|---|---|
| `quick_review` | 60 seconds | bounded review packet or smoke dispatch | no |
| `long_review` | 180 seconds | approved long read-only review with known startup overhead | no |
| `implementation_slice` | 300 seconds | approved implementation packet with expected file edits | no |
| `manual_monitor` | user-approved | supervised experiment where user expects longer wait | no |

The default remains `quick_review`. Increasing budget is a review decision, not
a hidden fallback. A timeout may propose a different class only if the evidence
shows startup overhead consumed the budget and the task is still worthwhile.

## Startup Noise Classification

The hardening tool should scan stdout/stderr for known startup-cost classes:

| Class | Example Evidence | Treatment |
|---|---|---|
| `remote_plugin_sync` | plugin catalog sync or featured plugin cache warning | record as startup overhead |
| `plugin_clone_timeout` | curated plugin Git clone timeout | record and propose lean mode |
| `missing_local_plugin` | local plugin loader warning | record as configuration finding |
| `mcp_startup_noise` | MCP startup or handshaking warnings | record as startup overhead |
| `state_db_repair_slow_path` | Codex state DB discrepancy or repair path | record as visibility/session risk |
| `worker_reading_evidence` | worker reaches project files but no packet yet | classify as productive but incomplete |

Startup noise alone does not make a dispatch successful. It only explains why
the timeout happened and what changed condition is required before retry.

## Lean Dispatch Investigation

`COAGENT-IMPL-NEXT-12` may investigate, but not silently enable, a lean dispatch
configuration:

- use a project-local `CODEX_HOME` with only required auth/config/session files;
- avoid plugin cache warmup if supported by Codex runtime flags or config;
- reduce MCP startup by using a minimal config profile if supported;
- preserve exact rollout id matching;
- prove the resulting command still sees the same target thread.

Any lean mode must be opt-in and evidence-backed. If Codex has no supported way
to disable plugin sync safely, the design must record that and rely on timeout
classes plus blocker/reconcile behavior.

## Required Closeout Record

Every dispatch attempt should produce a JSON record:

```json
{
  "task_id": "COAGENT-ARCH-LONGRUN-01-RUNTIME-01",
  "department": "RuntimePlatformAgent",
  "thread_id": "019e...",
  "timeout_class": "quick_review",
  "budget_seconds": 60,
  "pid": 58620,
  "started_at": "2026-05-30T02:50:46+08:00",
  "ended_at": "2026-05-30T02:51:46+08:00",
  "result_file": "Results/agent_packets/...",
  "result_file_state": "missing | present | late_present | invalid | imported",
  "process_state": "alive | dead | cleaned_up | cleanup_failed | unknown",
  "edge_state": "open | closed | close_failed | not_created",
  "startup_noise": ["remote_plugin_sync"],
  "decision": "transport_timeout_blocker",
  "evidence": [
    "Results/coagent_transport/runs/...stdout.log",
    "Results/coagent_transport/runs/...stderr.log"
  ],
  "next_action": "review logs before retry"
}
```

The record should be written under:

```text
Results/coagent_transport/runs/<task-id>.closeout.json
```

and summarized in:

```text
Results/coagent_transport/runs/<task-id>.summary.md
```

## Timeout Blocker Packet

When no valid result is imported within the approved budget, write:

```yaml
task_id:
blocked_task_id:
blocker_type: transport_timeout
severity:
owner: RuntimePlatformAgent
last_safe_state:
failed_command_or_tool:
timeout_class:
budget_seconds:
pid:
process_cleanup_state:
dispatch_edge_state:
expected_result_file:
result_file_state:
stdout_log:
stderr_log:
run_summary:
closeout_record:
startup_noise:
human_action_required:
resume_condition:
retry_policy:
dedupe_key:
created_at:
```

The dedupe key should include:

```text
transport_timeout:<department>:<thread_id>:<task_class>:<timeout_class>
```

The blocker must cite the expected result file. If a late result appears, the
blocker is not deleted; a reconcile record supersedes it.

## Late Result Reconciliation

If a result file appears after a timeout closeout:

1. classify `result_file_state=late_present`;
2. import through result router or future result packet validator;
3. if valid, close the runtime edge with `reconciled_late_result`;
4. if invalid, create or update an `invalid_result_packet` blocker;
5. preserve the original timeout summary;
6. write a reconcile record linking timeout and result packet evidence.

Late results must not erase timeout evidence because startup/transport
reliability is still a design finding.

## Cleanup Policy

Allowed cleanup:

- check the recorded child PID from the dispatch metadata;
- confirm the PID still belongs to the expected Codex command when possible;
- send a bounded stop/terminate signal only to that child process or process
  group if owned by the current dispatch attempt;
- record whether the process is alive, dead, cleaned, or unsafe to touch.

Forbidden cleanup:

- broad `pkill codex`;
- killing unrelated user Codex sessions;
- deleting Codex session history;
- deleting result packets or logs;
- removing runtime events;
- force-closing an edge without a closeout record.

If cleanup is unsafe or uncertain, emit a blocker with
`process_cleanup_state=manual_review_required`.

## Dispatch Edge Reconciliation

Open runtime edges are a reliability risk. Closeout should verify:

| Condition | Edge Action |
|---|---|
| valid result imported | close with imported state |
| timeout blocker written | close with blocked state or link blocker |
| invalid result blocker written | close with invalid-result blocker |
| cleanup unsafe | keep edge marked blocked/open with blocker reference |
| late result reconciled | close with `reconciled_late_result` |

The implementation must not leave a dispatch edge open without either a live
pollable process or a blocker packet.

## Stable Finding Codes

| Code | Meaning |
|---|---|
| `TRN_RESULT_MISSING` | expected result file absent after budget |
| `TRN_RESULT_LATE` | result appeared after timeout closeout |
| `TRN_RESULT_INVALID` | result exists but cannot be imported |
| `TRN_PROCESS_STILL_ALIVE` | recorded PID alive after budget |
| `TRN_PROCESS_CLEANUP_FAILED` | targeted cleanup failed |
| `TRN_PROCESS_CLEANUP_UNSAFE` | cleanup target cannot be safely identified |
| `TRN_EDGE_OPEN` | dispatch edge remains open after closeout |
| `TRN_EDGE_CLOSE_FAILED` | runtime edge close failed |
| `TRN_PLUGIN_SYNC_OVERHEAD` | plugin sync consumed budget or produced warning |
| `TRN_MCP_STARTUP_OVERHEAD` | MCP startup noise consumed budget or warning |
| `TRN_STATE_DB_DRIFT` | Codex DB/session drift affects dispatch |
| `TRN_TIMEOUT_CLASS_TOO_SMALL` | evidence supports larger reviewed class |
| `TRN_RETRY_WITHOUT_CHANGE` | retry proposed without changed condition |
| `TRN_BLOCKER_MISSING` | timeout/invalid result lacks blocker packet |

Codes are stable test-contract values.

## Fixture Matrix

Positive/neutral fixtures:

| Fixture | Expected |
|---|---|
| result within quick budget | `accepted_result` or `review_required_result` |
| timeout with missing result and blocker | `transport_timeout_blocker` |
| timeout then late valid result | `reconciled_late_result` plus preserved timeout |
| invalid result after timeout | `invalid_result_blocker` |

Negative fixtures:

| Fixture | Expected Codes |
|---|---|
| timeout without blocker | `TRN_BLOCKER_MISSING` |
| result missing and edge open | `TRN_RESULT_MISSING`, `TRN_EDGE_OPEN` |
| process alive and no cleanup state | `TRN_PROCESS_STILL_ALIVE` |
| retry proposed with same class and same packet | `TRN_RETRY_WITHOUT_CHANGE` |
| plugin sync warning omitted from closeout | `TRN_PLUGIN_SYNC_OVERHEAD` |
| late result overwrites timeout evidence | `TRN_RESULT_LATE` |

## Integration With Other Designs

| Design | Relationship |
|---|---|
| `blocker_packet_templates.md` | `transport_timeout` and `invalid_result_packet` packet shapes |
| `result_packet_validator_design.md` | validate any present or late result before import |
| `operating_metrics_snapshot_design.md` | counts timeout, missing blocker, open edge, and late result states |
| `mailbox_ledger_and_replay_design.md` | timeout/retry and expected-response state |
| `codex_visibility_drift_reliability_design.md` | pre-dispatch visibility must pass before transport starts |
| `candidate_a_validator_execution_design.md` | Candidate A live proof must treat timeout without blocker as blocked |

## Acceptance For `COAGENT-IMPL-NEXT-12`

Implementation is acceptable only when:

1. one controlled dispatch either imports a packet within budget or writes a
   timeout/invalid-result blocker;
2. a missing result file after budget creates a closeout record;
3. a late result can be reconciled without deleting timeout evidence;
4. process state is recorded as alive, dead, cleaned, cleanup failed, or unsafe;
5. dispatch edge state is closed or linked to a blocker;
6. startup plugin/MCP/state-DB noise is classified where visible in logs;
7. retries require a changed condition: packet fix, transport config fix,
   timeout class approval, or explicit user decision;
8. fixture tests cover stable `TRN_*` finding codes;
9. no automatic conversation creation, app-server transport, Git operation,
   MCP/tool call, dashboard, notification, or global Codex config change is
   introduced.

## Current Consequence

For `COAGENT-ARCH-LONGRUN-01`, the existing RuntimePlatformAgent run should be
treated as transport evidence with a late-result inconsistency. Before any
future live Candidate A proof, CoAgent should be able to close out this class
of attempt with a durable blocker or reconciled result instead of leaving the
state split across logs, packets, and runtime edges.
