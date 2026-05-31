# DevOps Session Status

Date: 2026-05-29

Status: unavailable; superseded by active-visible registry rule

## Finding

`MoSim｜DevOps 发布部` does not currently have a verified standalone visible
Codex session under `/home/linux/.codex/sessions/2026/05`.

The only current search hit for the DevOps prompt is the main project
conversation:

```text
thread_id: 019e0198-a041-77f1-84d0-c5524bfd4b81
originator: codex_vscode
path: /home/linux/.codex/sessions/2026/05/07/rollout-2026-05-07T16-40-40-019e0198-a041-77f1-84d0-c5524bfd4b81.jsonl
```

## Validation

```text
python3 CoAgent/dispatch/codex_transport.py validate-transport \
  --department GitIntegrator \
  --task-id COAGENT-MINILOOP-03 \
  --packet-file Results/coagent_miniloop/COAGENT-MINILOOP-03/scoped_task_packet.md
```

Result:

```text
ok: false
message: missing matching local Codex session file
```

## Decision

Do not dispatch long Git work to `GitIntegrator` until a standalone visible
DevOps conversation is recreated or a new verified session id is registered.

Current registry status:

```text
GitIntegrator.status = inactive_ui_deleted
```

The same rule applies to every deleted department conversation: a historical
rollout file is not a valid route. Only conversations currently visible to the
user may be registered as `active_visible`.
