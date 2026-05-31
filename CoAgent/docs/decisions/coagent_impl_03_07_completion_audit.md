# CoAgent IMPL-03 to IMPL-07 Completion Audit

Date: 2026-05-28

Status: complete with one documented transport warning.

## Scope

This audit verifies the active checkpoint objective:

- `COAGENT-IMPL-03`: strengthen preflight/hooks/doctor.
- `COAGENT-IMPL-04`: run one real visible department conversation lifecycle.
- `COAGENT-IMPL-05`: run one dedicated long-task lifecycle.
- `COAGENT-IMPL-06`: decide whether to expand transport.
- `COAGENT-IMPL-07`: decide whether to expand scheduled automation.

## Requirement Audit

| Requirement | Evidence | Result |
|---|---|---|
| IMPL-03 catches outside-project writes, secret-risk paths, destructive commands, broad Git risk, large-file risk, and missing result-packet evidence | `CoAgent/hooks/preflight.py`; `CoAgent/tests/test_preflight_policy.py`; `python3 CoAgent/hooks/preflight.py --result-packet Results/agent_packets/COAGENT-IMPL-04-VISIBLE-LIFECYCLE.yaml --result-packet Results/agent_packets/COAGENT-IMPL-05-LONG-TASK-LIFECYCLE.yaml` | pass |
| IMPL-04 sends a task packet to a visible department conversation and imports the visible result packet | `Results/agent_packets/COAGENT-IMPL-04-VISIBLE-LIFECYCLE.yaml`; isolated runtime summary under `Results/coagent_transport/visible_lifecycle/`; ledger row `COAGENT-IMPL-04` | pass |
| IMPL-05 starts from a compact context pack, records a checkpoint, imports a result packet, summarizes recovery, and closes the edge | `Results/context_packs/COAGENT-IMPL-05-LONG-TASK-LIFECYCLE.context.md`; `Results/agent_packets/COAGENT-IMPL-05-LONG-TASK-LIFECYCLE.yaml`; `Results/coagent_bootstrap/COAGENT-IMPL-05-LONG-TASK-LIFECYCLE.recovery.json`; `task_bootstrap.py status-task` terminal `done` | pass |
| IMPL-06 decides transport expansion only after lifecycle evidence and documents the app-server proof gate | `CoAgent/transport/TRANSPORT_EXPANSION_DECISION.md`; `Results/coagent_doctor/latest.json` | pass, app-server deferred |
| IMPL-07 decides scheduled automation expansion and keeps human review explicit | `CoAgent/automation/SCHEDULED_AUTOMATION_DECISION.md`; `automation_runner.py guard-due`; `automation_runner.py plan-due-dispatch`; isolated `enqueue-due` DB under `Results/coagent_automation/impl07/` | pass, unattended scheduler deferred |
| Status, progress, and ledger are updated | `CoAgent/STATUS.md`; `PROGRESS.md`; `Docs/Workflows/agent_task_ledger.md`; `CoAgent/docs/decisions/coagent_post_approval_backlog.md` | pass |

## Verification Commands

```bash
python3 CoAgent/hooks/preflight.py --result-packet Results/agent_packets/COAGENT-IMPL-04-VISIBLE-LIFECYCLE.yaml --result-packet Results/agent_packets/COAGENT-IMPL-05-LONG-TASK-LIFECYCLE.yaml
python3 CoAgent/doctor/check_design_gate.py
python3 CoAgent/tests/test_preflight_policy.py
python3 CoAgent/tests/test_transport_adapter.py
python3 CoAgent/tests/test_task_bootstrap.py
python3 CoAgent/tests/test_automation_dispatch_plan.py
python3 CoAgent/learning/learning_indexer.py validate --strict
python3 CoAgent/learning/learning_indexer.py coverage --strict
python3 CoAgent/automation/automation_runner.py guard-due --cadence daily
python3 CoAgent/automation/automation_runner.py plan-due-dispatch --cadence daily
python3 CoAgent/automation/automation_runner.py worker-status
python3 CoAgent/automation/automation_runner.py enqueue-due --cadence daily --db Results/coagent_automation/impl07/tasks.sqlite3 --events Results/coagent_automation/impl07/events.jsonl
python3 CoAgent/doctor/coagent_doctor.py --json --output Results/coagent_doctor/latest.json
python3 -m py_compile CoAgent/hooks/preflight.py CoAgent/doctor/coagent_doctor.py CoAgent/automation/automation_runner.py CoAgent/transport/codex_exec.py CoAgent/dispatch/codex_transport.py CoAgent/bootstrap/task_bootstrap.py
python3 CoAgent/bootstrap/task_bootstrap.py status-task --department TestOwner --task-id COAGENT-IMPL-05-LONG-TASK-LIFECYCLE
git diff --check -- CoAgent/doctor/check_design_gate.py CoAgent/hooks/preflight.py CoAgent/tests/test_preflight_policy.py CoAgent/transport/TRANSPORT_EXPANSION_DECISION.md CoAgent/automation/SCHEDULED_AUTOMATION_DECISION.md CoAgent/STATUS.md PROGRESS.md Docs/Workflows/agent_task_ledger.md CoAgent/docs/decisions/coagent_post_approval_backlog.md
```

## Known Warning

`python3 CoAgent/doctor/coagent_doctor.py --json --output Results/coagent_doctor/latest.json`
returns overall `warning`, not `fail`. The only warning is
`coagent.transport_session_files`: `TestOwner` has a matching local WSL rollout
file, while the other registered department thread ids do not. This is the
reason `COAGENT-IMPL-06` defers app-server/transport expansion.

## Security Boundary

The dry-run transport plan prepares a shadow Codex home under ignored Results
paths. Git ignore verification shows these are ignored:

```text
Results/coagent_transport/codex_home/auth.json
Results/coagent_transport/codex_home/config.toml
Results/coagent_automation/impl07/tasks.sqlite3
Results/coagent_doctor/latest.json
```

No credential file content was read into this audit.

## Next Gate

The next CoAgent implementation must be a new explicit backlog item. Closed
IMPL-01 through IMPL-07 scope must not be used to add app-server transport,
unattended automation, new permanent departments, or broad tool/MCP expansion.
