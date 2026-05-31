# COAGENT-MINILOOP-04 Visibility Review

Date: 2026-05-29

Status: real_tui_thread_synced_awaiting_user_confirmation

## Candidate Conversation

```text
title: MoSim｜候选测试闭环
thread_id: 019e7373-37f4-75e1-9780-e1519a489715
created_by: WSL Codex CLI
working_directory: /mnt/c/Users/HP/Desktop/MoSim
```

## Proven

- A new candidate Codex session was created.
- The candidate session read
  `Results/coagent_miniloop/COAGENT-MINILOOP-04/scoped_task_packet.md`.
- It wrote
  `Results/coagent_miniloop/COAGENT-MINILOOP-04/worker_result_packet.json`.
- The first result packet exposed a schema issue: the packet template omitted
  required `summary`.
- A repair packet was sent to the same candidate session.
- The repaired result passed result-router validation and was imported as
  `accepted`.

## Visibility Problem Found

- Before repair, the user confirmed that `MoSim｜候选测试闭环` was not visible in
  VSCode Codex or Codex App.
- This candidate must not be registered as `active_visible` unless it is
  intentionally promoted from a test conversation into a durable communication
  target.
- Diagnosis found that CLI-created sessions can exist in WSL `state_5.sqlite`
  and rollout files without appearing in WSL/Windows `session_index.jsonl`, and
  Windows Codex App has no matching row unless explicitly synced.
- A minimal visibility/index repair was applied.
- After repair, local WSL/Windows metadata checks pass, but user UI
  confirmation is still required.
- A second thread was then created through a real WSL Codex TUI route rather
  than `codex exec`:
  `019e73e5-d97d-75a3-ba72-b52e19d755b3` / `MoSim｜可见对话测试`.
  It replied `MoSim visible thread ok`.
- That real TUI thread was synced into both WSL and Windows `session_index.jsonl`
  and all relevant `state_5.sqlite` files with canonical
  `cwd=/mnt/c/Users/HP/Desktop/MoSim`.
- The repeatable repair command is now:
  `python3 CoAgent/dispatch/codex_session_repair.py sync-visible ... --apply`.

## Visibility Repair Applied

```text
backup_root: C:\Users\HP\.codex\backups\visibility-repair-20260529T125333Z
coagent_tool_backup_wsl: /home/linux/.codex/backups/coagent-session-restore-20260529-210054
coagent_tool_backup_windows: C:\Users\HP\.codex\backups\coagent-session-restore-20260529-210054
real_tui_thread_id: 019e73e5-d97d-75a3-ba72-b52e19d755b3
real_tui_thread_title: MoSim｜可见对话测试
real_tui_backup_wsl: /home/linux/.codex/backups/coagent-session-restore-20260529-213048
real_tui_backup_windows: C:\Users\HP\.codex\backups\coagent-session-restore-20260529-213048
wsl_index: /home/linux/.codex/session_index.jsonl
windows_index: C:\Users\HP\.codex\session_index.jsonl
wsl_state: /home/linux/.codex/state_5.sqlite
wsl_state_alt: /home/linux/.codex/sqlite/state_5.sqlite
windows_state: C:\Users\HP\.codex\state_5.sqlite
windows_rollout_copy: C:\Users\HP\.codex\sessions\2026\05\29\rollout-2026-05-29T19-16-31-019e7373-37f4-75e1-9780-e1519a489715.jsonl
```

After repair, both WSL and Windows state rows use:

```text
title: MoSim｜候选测试闭环
source: vscode
thread_source: vscode
has_user_event: 1
archived: 0
cwd: /mnt/c/Users/HP/Desktop/MoSim
```

## User Review Result

Before the repair, the user could not see a conversation named:

```text
MoSim｜候选测试闭环
```

After the repair, the user must confirm whether `MoSim｜可见对话测试` is visible
and openable in VSCode Codex and/or Codex App. Until then, both
`MoSim｜候选测试闭环` and `MoSim｜可见对话测试` remain non-dispatchable test
conversations, not promoted department conversations.
