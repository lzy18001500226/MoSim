# Codex Visible Thread SOP

Date: 2026-05-30

Purpose: create a Codex conversation that is visible in VSCode Codex and Codex App, then wait for user confirmation before using it as a communication target.

## Accepted Path

Use a real WSL Codex TUI session. Do not use `codex exec` for conversations that the user must see in the front end.

Current verified Codex binary:

```bash
codex
```

The plain `codex` on this WSL shell resolved to the current VSCode extension
binary on 2026-05-31:

```bash
/mnt/c/Users/HP/.vscode/extensions/openai.chatgpt-26.527.31454-win32-x64/bin/linux-x86_64/codex
```

```text
codex-cli 0.135.0-alpha.1
```

The older recorded path under `openai.chatgpt-26.519.32039-win32-x64` no longer
exists. Bootstrap code should prefer `COAGENT_CODEX_BIN`, then `codex` from
`PATH`, and only then a known fallback path.

Because `/home/linux/.codex/config.toml` currently sets `model_provider = "Anthropic"` while only `OpenAI` is configured, pass provider overrides on the command line instead of editing global config:

```bash
timeout 60s script -qfec \
  'codex --no-alt-screen -C /mnt/c/Users/HP/Desktop/MoSim \
    -c "model_provider=\"OpenAI\"" \
    -c "model_reasoning_effort=\"high\"" \
    -m gpt-5.5 -a never --sandbox danger-full-access \
    "<short prompt>"' \
  /dev/null
```

The TUI may be killed by the 60s timeout even after the assistant already answered. Treat a nonzero timeout as inconclusive, then inspect the rollout before retrying.

## Sync Path

After finding the generated thread id, sync both WSL and Windows Codex state:

```bash
python3 CoAgent/dispatch/codex_session_repair.py sync-visible \
  --thread-id <thread-id> \
  --thread-name '<short visible title>' \
  --preview '<short preview>' \
  --cwd /mnt/c/Users/HP/Desktop/MoSim \
  --target-codex-home /home/linux/.codex \
  --target-codex-home /mnt/c/Users/HP/.codex \
  --apply
```

This command must leave all of these true:

```text
WSL session_index.jsonl contains the thread id
Windows session_index.jsonl contains the thread id
WSL state_5.sqlite threads row has source=vscode, thread_source=vscode, has_user_event=1, archived=0
WSL sqlite/state_5.sqlite threads row has source=vscode, thread_source=vscode, has_user_event=1, archived=0
Windows state_5.sqlite threads row has source=vscode, thread_source=vscode, has_user_event=1, archived=0
Windows rollout file exists under C:\Users\HP\.codex\sessions\...
cwd is exactly /mnt/c/Users/HP/Desktop/MoSim
```

Run the project doctor after sync:

```bash
python3 CoAgent/doctor/check_department_visibility.py
```

If the doctor reports a missing index entry after a successful resume, rerun
`sync-visible --apply` for the exact thread id and both Codex homes.

For department bootstrap, create or register one department at a time when
recovering from a timeout:

```bash
python3 CoAgent/dispatch/bootstrap_department_threads.py --timeout 60 create \
  --apply-sync --apply-registry --department <DepartmentName>
```

Do not run multiple registry-writing bootstrap commands in parallel. The Codex
session creation can complete while the outer command times out; the bootstrap
tool must save `department_threads.json` after each department, and a failed
batch should be resumed by inspecting existing bootstrap rollouts rather than
recreating old deleted ids.

## 2026-05-31 DevOps Visibility Correction

The DevOps Git dispatch result existed in project artifacts, but the user did
not see a new DevOps message because `codex_exec_resume` used a shadow
`CODEX_HOME` under `Results/coagent_transport/`. That proves a worker can write
a result packet, but it does not guarantee the front-end-visible Codex
conversation was updated.

Validated visible message path:

```bash
printf '%s\n' '<short DevOps prompt>' | timeout 60s codex exec resume \
  019e74de-a452-7a50-99e7-ca9a247b32f1 \
  -m gpt-5.5 \
  -c 'model_provider="OpenAI"' \
  -c 'model_reasoning_effort="high"' \
  --dangerously-bypass-approvals-and-sandbox \
  --output-last-message Results/coagent_transport/devops_visible_ping_20260531_result.txt \
  -
```

On 2026-05-31, `/home/linux/.nvm/versions/node/v16.20.2/bin/codex`
failed with:

```text
SyntaxError: Unexpected reserved word
```

For WSL-backed VSCode sessions, the currently validated CLI is the VSCode
extension binary exposed by `command -v codex`:

```text
/mnt/c/Users/HP/.vscode/extensions/openai.chatgpt-26.527.31454-win32-x64/bin/linux-x86_64/codex
```

Use that binary, or `codex` when `command -v codex` resolves to it. Do not use
the old npm/node16 shim for visible conversation dispatch.

For long-running visible department work, do not wrap the whole `codex exec
resume` process in `timeout 60s`. That delivers the message and then kills the
worker, which makes the department appear to have stopped. Start a background
process, record PID/stdout/stderr/last-message paths, and let the department
return a result packet:

```bash
nohup "$(command -v codex)" exec resume <thread_id> \
  -m gpt-5.5 \
  -c 'model_provider="OpenAI"' \
  -c 'model_reasoning_effort="high"' \
  --dangerously-bypass-approvals-and-sandbox \
  --output-last-message Results/coagent_transport/<task>_last.txt \
  - < Results/coagent_transport/<task>_prompt.txt \
  > Results/coagent_transport/runs/<task>.stdout.log \
  2> Results/coagent_transport/runs/<task>.stderr.log &
```

Then write a metadata JSON with the PID and log paths. Use 60 second timeouts
inside the worker's Git/tool commands, not around the whole visible department
process.

Verified reply:

```text
DevOps 可见通信测试 2026-05-31 收到。
```

After the resume, run `sync-visible --apply` for WSL and Windows Codex homes.
Do not claim a department received a user-visible message unless the real Codex
home rollout is updated and synced, or the user explicitly accepts local-only
packet transport.

## 2026-05-30 Proof

Created real TUI test thread:

```text
thread_id: 019e74b9-2512-7171-94c7-edc4835fa5f9
thread_name: MoSim｜可见对话测试-20260530
reply: MoSim visible thread test 20260530 ok
```

Synced backups:

```text
/home/linux/.codex/backups/coagent-session-restore-20260530-011453
C:\Users\HP\.codex\backups\coagent-session-restore-20260530-011453
```

State after sync: user confirmed this test thread is visible in the front end.

Do not register this test thread, or any future department thread, as `active_visible` until the user confirms it is visible and openable in VSCode Codex or Codex App.

## 2026-05-30 Historical Department Bootstrap

Created or recovered 10 historical CoAgent department conversations through the
verified real TUI path, then synced WSL and Windows metadata:

```text
DispatchAgent: 019e74ce-6e2e-7e71-902d-f6cee64e8a61 / MoSim｜调度中台
ProductStrategyAgent: 019e74cf-fb50-7d71-912c-f586b4dd5f06 / MoSim｜产品发现战略
RuntimePlatformAgent: 019e74d1-72fa-7d33-8783-90584035ae92 / MoSim｜Agent Runtime 平台
ContextMemoryAgent: 019e74d2-ec4b-7603-a41b-596508ab6982 / MoSim｜上下文记忆索引
ToolchainMCPAgent: 019e74d4-619c-7133-b53f-78fbefff780a / MoSim｜工具链 MCP
KnowledgeSecretaryAgent: 019e74d5-d833-7e41-a65b-2868fd841ea1 / MoSim｜知识秘书
VerificationAgent: 019e74d7-4d58-70f1-84f7-873641995f9a / MoSim｜验证评测
SafetyComplianceAgent: 019e74d8-c6fd-76c2-98fe-832dc1fea97b / MoSim｜安全合规
DevOpsReleaseAgent: 019e74de-a452-7a50-99e7-ca9a247b32f1 / MoSim｜DevOps 发布
ExternalIntelligenceAgent: 019e74de-a83c-7fc2-8987-06c95577a1d3 / MoSim｜外部情报进化
```

This historical set is no longer the current routing registry. Several entries
were later deleted by the user or replaced by current visible department titles.
Do not recreate or resume these old IDs from this section. Current dispatchable
threads are the user-confirmed allowlist in
`CoAgent/dispatch/department_threads.json` and
`Docs/Index/codex_app_session_research.md#department-thread-layout`. If a
historical ID is absent from the current visible scan, treat it as gone rather
than maintaining a separate blacklist.
