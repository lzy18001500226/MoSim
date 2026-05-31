# CoAgent Dispatch

## Purpose

This directory contains project-owned dispatch helpers.

Dispatch is the layer between:

- runtime task state,
- visible department conversations,
- task packets,
- result packets,
- future Codex App or CLI conversation routing helpers.

The normative V1 cross-conversation communication contract is
`CoAgent/dispatch/communication_contract.md`.

## Current Components

| File | Purpose |
|---|---|
| `department_threads.json` | visible department conversation registry |
| `dispatch_helper.py` | local CLI helper for registering departments, building dispatch envelopes, and importing result packets |
| `conversation_registry.py` | shared registry helpers for department conversations |
| `codex_transport.py` | transport-aware Codex dispatch planner and optional runner |
| `bootstrap_department_threads.py` | bootstrap permanent department conversations and sync VSCode/Codex App visibility metadata |

## Current Boundary

This layer does not call Codex directly yet.

It prepares stable project-owned payloads so later transport helpers can send
them through:

- Codex App visible conversations,
- WSL Codex CLI,
- or other project-approved surfaces.

Run `CoAgent/hooks/preflight.py` before wide-scope dispatch or result import
work when path/scope safety matters.

Current helper commands:

```bash
python CoAgent/dispatch/dispatch_helper.py list
python CoAgent/dispatch/dispatch_helper.py set-thread --department ProjectOwner --thread-id <id>
python CoAgent/dispatch/dispatch_helper.py dispatch-envelope --department ProjectOwner --task-id <id>
python CoAgent/dispatch/dispatch_helper.py department-task-text --department ProjectOwner --task-id <id>
python CoAgent/dispatch/dispatch_helper.py import-result --packet /abs/path/result_packet.json
python CoAgent/dispatch/dispatch_helper.py import-result-text --packet /abs/path/result_packet.txt
python CoAgent/dispatch/dispatch_helper.py review-brief --task-id <id>
python CoAgent/dispatch/codex_transport.py plan-dispatch --department ProjectOwner --task-id <id>
python CoAgent/dispatch/codex_transport.py validate-transport --department ProjectOwner --task-id <id>
python CoAgent/dispatch/codex_transport.py start-dispatch --department ProjectOwner --task-id <id>
python CoAgent/dispatch/codex_transport.py poll-dispatch --task-id <id>
python CoAgent/dispatch/codex_transport.py run-dispatch --department ProjectOwner --task-id <id>
python CoAgent/dispatch/codex_transport.py reconcile-result --department ProjectOwner --task-id <id>
python CoAgent/dispatch/codex_session_repair.py diagnose --department TestOwner
python CoAgent/dispatch/codex_session_repair.py restore --department TestOwner
python CoAgent/dispatch/codex_session_repair.py sync-visible --thread-id <id> --thread-name <title> --cwd /mnt/c/Users/HP/Desktop/MoSim
python CoAgent/dispatch/bootstrap_department_threads.py plan
python CoAgent/dispatch/bootstrap_department_threads.py create --apply-sync --apply-registry
python CoAgent/doctor/check_department_visibility.py
```

Current transport rule:

- `codex_transport.py` is dry-run first.
- It may build the exact `codex exec resume` command and materialize packet/result paths.
- `run-dispatch` is available, but should only be used after the target department
  thread has a real `thread_id` configured in `department_threads.json`.
- Current transport status on 2026-05-26:
  the helper now uses a project-local shadow `CODEX_HOME` and `sqlite_home`
  under `Results/coagent_transport/`. With that redirect, a real department
  thread wrote a project-local result packet file that CoAgent successfully
  imported back into runtime state.
- Remaining limitation:
  `run-dispatch` can still return non-clean CLI stderr/noisy timeout behavior,
  or be killed by the outer timeout, even when the department thread already
  completed the requested file write.
- Recovery path:
  use `reconcile-result` to import the declared project-local result file back
  into runtime state when the department thread has already produced it.
- Session-repair path:
  `codex_session_repair.py diagnose` is read-only and checks whether registered
  department thread ids have local WSL rollout files. `restore` is dry-run by
  default; `restore --apply` writes Codex session state and must be treated as an
  external-state repair after backup and user approval.
- Visibility-sync path:
  `codex_session_repair.py sync-visible` is dry-run by default and repairs one
  known Codex thread so VSCode/Codex App can list it. It copies the rollout if
  needed, upserts `session_index.jsonl`, and normalizes the thread DB row to
  `source=vscode`, `thread_source=vscode`, `has_user_event=1`, and
  `archived=0`. Pass `--cwd /mnt/c/Users/HP/Desktop/MoSim` for MoSim threads so
  App/VSCode cwd filters match the project exactly. Use `--apply` only after
  confirming the exact thread id/title and the target Codex homes. This is an
  external Codex-state repair, not a normal project-file edit.
- New visible-thread creation path:
  prefer a real WSL Codex TUI session, not `codex exec`, for candidate
  conversations that the user must see:

```bash
timeout 60s script -qfec \
  'codex --no-alt-screen -C /mnt/c/Users/HP/Desktop/MoSim \
    -c "model_provider=\"OpenAI\"" \
    -c "model_reasoning_effort=\"high\"" \
    -m gpt-5.5 -a never --sandbox danger-full-access "<short prompt>"' \
  /dev/null
```

  Then run `sync-visible --cwd /mnt/c/Users/HP/Desktop/MoSim --apply` and wait
  for user UI confirmation before marking the thread `active_visible`.
  The full SOP and the 2026-05-30 proof thread are recorded in
  `CoAgent/docs/status/codex_visible_thread_sop.md`.
- Current stable path:
  `start-dispatch` launches the real department-thread job in the background,
  and `poll-dispatch` can later observe the result file and import it back into
  runtime state as `done`.
- Permanent department bootstrap path:
  `bootstrap_department_threads.py` creates lightweight real Codex sessions for
  the permanent CoAgent departments, then syncs WSL and Windows Codex metadata
  through the same visibility repair path. Newly bootstrapped departments stay
  `visible_pending_user_confirmation` until the user confirms they are visible
  in the front end; only then may they be promoted to `active_visible`.
  Root cause found on 2026-05-29:
  DB/index rows alone are not enough. If the Windows-side `rollout_path`
  points at `C:\Users\HP\.codex\...` but the file was never copied there, the
  front end can still fail to show or open the thread. Also keep `cwd` fixed to
  `/mnt/c/Users/HP/Desktop/MoSim`; a lowercase variant can miss exact cwd
  filters used by the App/VSCode thread list.
