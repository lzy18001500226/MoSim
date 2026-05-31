# COAGENT-ARCH-LONGRUN-01 Codex Visibility Recovery Experiment Design

Date: 2026-05-30
Status: phase 2 design draft

## Purpose

Define the experiment package for proving that Codex App/VSCode/CLI visible
conversation state can be checked, repaired, or safely blocked before CoAgent
uses a department conversation for task work.

This extends `codex_visibility_drift_reliability_design.md`. That document
defines invariants and the repair policy. This document defines the recovery
experiment and evidence package required before the repair path can be trusted
as an operational gate.

This is design only. It does not implement automatic repair, create
conversations, dispatch packets, change Codex provider configuration, or modify
runtime schemas.

## Problem Being Tested

Observed during `COAGENT-ARCH-LONGRUN-01`:

- `check_department_visibility.py` can pass, then fail later for registered
  active-visible departments;
- drift first appeared for DispatchAgent and later appeared for
  ProductStrategyAgent during the same verification sequence;
- running `codex_session_repair.py sync-visible --apply` for all registered
  non-Main departments restored the 11-conversation visibility check;
- the root cause is still unknown, so repair cannot be treated as proof that
  Codex transport is reliable.

The experiment must therefore prove a weaker but useful claim:

```text
CoAgent can detect registered-department visibility drift, repair only approved
registered threads when safe, record before/after evidence, and block dispatch
when repair is unsafe or incomplete.
```

It must not claim the UI/root-cause problem is solved.

## Required Evidence Package

Future runs should write:

```text
Results/coagent_transport/visibility_checks/<run-id>/precheck.json
Results/coagent_transport/visibility_checks/<run-id>/diagnose-<department>.json
Results/coagent_transport/visibility_repairs/<run-id>/repair-<department>.json
Results/coagent_transport/visibility_checks/<run-id>/postcheck.json
Results/coagent_transport/visibility_checks/<run-id>/summary.md
```

Each run id should include timestamp and task id:

```text
20260530-COAGENT-ARCH-LONGRUN-01-visible-recovery-01
```

Minimum fields:

```yaml
task_id:
run_id:
started_at:
ended_at:
departments_checked:
departments_failed_precheck:
departments_repaired:
departments_blocked:
registered_thread_only: true
external_paths_touched:
  - /home/linux/.codex
  - /mnt/c/Users/HP/.codex
backup_paths:
precheck_result:
postcheck_result:
final_decision: visible_verified | repair_succeeded | blocked_visibility
forbidden_claims:
  - root_cause_fixed
  - unattended_transport_reliable
  - arbitrary_codex_state_repair_allowed
```

External paths are allowed here only because Codex visibility repair is an
explicit project-infrastructure exception already approved for registered
department sessions.

## Scenario Matrix

| Scenario | Input State | Expected Decision | Required Evidence |
|---|---|---|---|
| `clean_registry` | all 11 active-visible rows pass | `visible_verified` | precheck and summary, no repair |
| `single_alt_db_drift` | one registered department has stale WSL alternate DB row | `repair_succeeded` | diagnose, repair output, postcheck |
| `multi_department_drift` | more than one registered non-Main department fails | `repair_succeeded` if all match approved pattern | per-department repair records and postcheck |
| `unknown_thread_id` | failing row is not in registry | `blocked_visibility` | blocker packet; no repair |
| `missing_rollout_file` | registered DB row points to absent rollout and no project-known source file exists | `blocked_visibility` | diagnose output and exact missing path |
| `windows_sync_failure` | WSL repaired but Windows DB/index still fails | `blocked_visibility` | before/after evidence, user action |
| `repair_repeat_same_department` | same department drifts again after successful repair | `repair_succeeded_with_incident` | repair plus retrospective action requirement |
| `rapid_recurrence_after_repair` | a department fails again in the next verification cycle after a successful all-department repair | `repair_succeeded_with_incident` or `blocked_visibility` depending on dispatch risk | second precheck, second repair record, incident note |
| `provider_config_requested` | fix would require editing global Codex provider config | `blocked_visibility` | explicit forbidden action finding |
| `credentials_or_account_cache` | fix would touch credentials/account cache/browser state | `blocked_visibility` | safety finding, no repair |

## Root-Cause Investigation Boundary

The recovery experiment may inspect:

- session indexes under registered Codex homes;
- rollout file existence for registered thread ids;
- `threads` table rows for registered thread ids;
- source/thread_source/cwd/title/archived/has_user_event fields;
- backup paths written by repair helper.

It must not inspect or modify:

- provider credentials;
- browser profiles;
- account cache body;
- unrelated threads;
- deleted user conversations not registered in
  `CoAgent/dispatch/department_threads.json`;
- arbitrary SQLite rows outside registered thread ids.

Root-cause hypotheses should be recorded as `unproven_hypothesis`, not accepted
facts, unless a later controlled experiment proves them.

## Dispatch Gate Decision

After the experiment:

| Final State | Dispatch Allowed? | Notes |
|---|---|---|
| `visible_verified` | yes | no repair required |
| `repair_succeeded` | yes for bounded/manual-supervised dispatch | still not unattended reliability |
| `repair_succeeded_with_incident` | yes only after retrospective record is opened | repeated drift must not be silent |
| `blocked_visibility` | no | blocker packet required |
| `unknown` | no | missing evidence cannot authorize dispatch |

Even after `repair_succeeded`, live dispatch must still pass transport timeout
and packet-validation gates.

If `rapid_recurrence_after_repair` appears while a live dispatch is planned,
default to `blocked_visibility` unless the user explicitly accepts a supervised
manual dispatch. A state that rewrites itself between checks is not stable
enough for unattended or long-running transport.

## Blocker Requirements

If recovery fails, write a blocker packet with:

```yaml
blocker_type: codex_visibility_drift
department:
thread_id:
thread_name:
failed_surface:
precheck_path:
diagnose_path:
repair_attempted:
repair_path:
postcheck_path:
last_safe_state:
exact_user_action_required:
resume_condition:
dedupe_key:
```

Vague asks such as "check Codex" are invalid. The user action must identify the
specific conversation, frontend surface, or manual approval needed.

## Retrospective Trigger

Create a retrospective action when:

- the same department drifts twice after repair;
- a department drifts again in the next verification cycle after an
  all-department repair;
- two or more departments drift in the same run;
- repair succeeds only after touching both WSL and Windows stores;
- drift blocks a planned dispatch;
- the repair helper changes behavior because Codex storage format changed.

The retrospective action should target one of:

- visibility drift gate implementation;
- repair evidence schema;
- Codex storage-format compatibility note;
- user-facing frontend troubleshooting guide;
- decision to stop relying on visible transport for that class of work.

## Interaction With Other Gates

| Gate | Relationship |
|---|---|
| `check_department_visibility.py` | current pre/post check |
| `codex_session_repair.py sync-visible` | bounded repair helper |
| `transport_timeout_hardening_design.md` | still required after visibility passes |
| `result_packet_validator_design.md` | still required after dispatch returns |
| `blocker_packet_validator_design.md` | validates failed-recovery blocker |
| `retrospective_and_improvement_closure_protocol.md` | handles recurring drift |
| `early_drift_detection_experiment_design.md` | treats repeated drift without action as review escape |

## Minimum Future Fixture Set

Later implementation should create fixtures or controlled test doubles for:

- `clean_registry`;
- `single_alt_db_drift`;
- `multi_department_drift`;
- `unknown_thread_id`;
- `missing_rollout_file`;
- `provider_config_requested`;
- `credentials_or_account_cache`;
- `repair_repeat_same_department`.
- `rapid_recurrence_after_repair`.

The fixture does not need to copy real Codex private data. It should use a
minimal synthetic SQLite/index/rollout directory under project test fixtures.

## Current Task Application

This design records the latest recurrence as a reliability finding:

```text
During this turn, `check_department_visibility.py` first failed for
DispatchAgent, then for ProductStrategyAgent. Syncing all registered non-Main
department sessions restored the check. The correct claim is "registered
metadata drift was repaired for this run", not "Codex visibility is reliable".
On a later check in the same continuation, DispatchAgent failed again shortly
after the all-department repair and then passed after another all-department
sync. This is now represented as `rapid_recurrence_after_repair`, which should
gate unattended dispatch and require retrospective tracking when the future
checker exists.
```

The active long-running goal remains open. This artifact advances P12/P47 by
turning recurring repair work into a future experiment and validator target.
