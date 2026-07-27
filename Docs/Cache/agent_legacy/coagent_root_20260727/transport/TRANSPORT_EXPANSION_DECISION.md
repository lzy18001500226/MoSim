# CoAgent Transport Expansion Decision

Date: 2026-05-28

Status: defer app-server transport; keep staged file/CLI transport.

## Decision

Do not implement app-server transport in the current phase.

Keep the current `codex_exec_resume` staged file/CLI route as the only real
visible-thread transport path until every registered department thread has a
matching local rollout file and repeated non-TestOwner lifecycles pass.

## Evidence

- IMPL-04 visible TestOwner lifecycle:
  `Results/agent_packets/tasks/coagent_implementation/COAGENT-IMPL-04-VISIBLE-LIFECYCLE.yaml`.
- IMPL-05 dedicated long-task lifecycle:
  `Results/coagent_bootstrap/COAGENT-IMPL-05-LONG-TASK-LIFECYCLE.recovery.json`.
- Current doctor output:
  `Results/coagent_doctor/latest.json`.
- Current doctor functional checks pass, but
  `coagent.transport_session_files` warns that only `TestOwner` has a matching
  local WSL rollout file. Other registered department thread ids are configured
  but not locally restorable.

## Gate Before Expansion

- At least two different departments complete real visible lifecycles.
- `coagent.transport_session_files` is `ok`, or the missing-rollout state is
  explicitly accepted as a manual-operation boundary.
- A read-only app-server proof documents supported APIs, auth model, thread
  identity mapping, rollback behavior, and security boundaries.
- Any new adapter is implemented behind `CoAgent/transport/adapter.py`, not in
  dispatch logic.

## Current Next Action

Use `task_bootstrap --include-transport-plan` plus
`codex_transport start-dispatch` / `poll-dispatch` for explicit reviewed runs.
