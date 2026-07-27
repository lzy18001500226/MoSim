# CoAgent Scheduled Automation Decision

Date: 2026-05-28

Status: allow guarded dry-run and reviewed staged starts; defer unattended
scheduler expansion.

## Decision

Do not add wall-clock scheduler or unattended write automation in the current
phase.

Keep automation as durable task definitions, guard checks, dry-run dispatch
plans, and explicit reviewed starts. Codex App automation can remind or trigger
later, but it is not the source of truth.

## Evidence

- `CoAgent/automation/automation_tasks.json` declares daily tasks with scope,
  tool scope, stop conditions, and human-review flags.
- `CoAgent/automation/guardrails.py` blocks prompt-injection patterns,
  out-of-project paths, unknown tools, duplicate locks, missing review, and
  concurrency violations.
- `CoAgent/automation/worker_policy.json` defines low concurrency and stale
  lock reporting.
- Current doctor output:
  `Results/coagent_doctor/latest.json`.

## Allowed Now

- `automation_runner.py guard-due --cadence daily`
- `automation_runner.py worker-status`
- `automation_runner.py plan-due-dispatch --cadence daily`
- `automation_runner.py enqueue-due --cadence daily` when the operator wants
  durable task tickets
- `automation_runner.py start-due-dispatch --reviewed` only for explicit
  reviewed runs

## Forbidden Until Later Gate

- Automatic wall-clock wakeups that write project files.
- Automatic Git commits, pushes, resets, or force operations.
- Automatic code or docs mutation without result-router and human-review state.
- Codex App private DB or credential/account state modification.
- Treating automation locks as proof of task completion.

## Current Next Action

Keep recurring work as reviewed task tickets and dry-run plans. Expand to a real
scheduler only after multiple reviewed daily runs complete with no stale locks,
no active queue residue, and clear human-review evidence.
