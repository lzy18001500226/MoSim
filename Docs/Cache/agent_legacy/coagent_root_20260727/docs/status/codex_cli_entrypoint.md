# Codex CLI Entrypoint

Date: 2026-05-30

Status: verified in WSL for project-local CoAgent conversation bootstrap.

## Working Entrypoint

Current preferred entrypoint:

```bash
codex
```

On 2026-05-31, `command -v codex` resolved to:

```bash
/mnt/c/Users/HP/.vscode/extensions/openai.chatgpt-26.527.31454-win32-x64/bin/linux-x86_64/codex
```

It reported:

```text
codex-cli 0.135.0-alpha.1
```

When creating visible test or department conversations, pass provider overrides
because `/home/linux/.codex/config.toml` currently says
`model_provider = "Anthropic"` while only `[model_providers.OpenAI]` is
configured:

```bash
timeout 60s script -qfec \
  'codex --no-alt-screen -C /mnt/c/Users/HP/Desktop/MoSim \
    -c "model_provider=\"OpenAI\"" \
    -c "model_reasoning_effort=\"high\"" \
    -m gpt-5.5 -a never --sandbox danger-full-access "<short prompt>"' \
  /dev/null
```

The repeatable visible-thread procedure is recorded in
`CoAgent/docs/status/codex_visible_thread_sop.md`.

## Historical Entrypoint Notes

The Codex npm entrypoint installed under Node 16 exists here:

```bash
/home/linux/.nvm/versions/node/v16.20.2/bin/codex
```

Do not execute it with Node 16. On 2026-05-29 it failed with:

```text
SyntaxError: Unexpected reserved word
```

The same JS entrypoint works when launched with Node 20:

```bash
/home/linux/.nvm/versions/node/v20.20.2/bin/node \
  /home/linux/.nvm/versions/node/v16.20.2/lib/node_modules/@openai/codex/bin/codex.js \
  -C /mnt/c/Users/HP/Desktop/MoSim \
  --ask-for-approval never \
  --sandbox danger-full-access \
  exec "你好"
```

Verified output:

```text
codex-cli 0.134.0
session id: 019e715d-eeaa-7ac0-9547-a1415d4e002b
prompt: 你好
response: 你好，我在 `/mnt/c/Users/HP/Desktop/MoSim` 项目目录内待命。
```

## Notes

- `/usr/bin/node` is Node v12.22.9 and is not suitable for this entrypoint.
- `/home/linux/.nvm/versions/node/v16.20.2/bin/codex --version` fails because
  the shebang resolves to an incompatible Node runtime.
- The VSCode extension also ships a Codex binary. On 2026-05-31 the current
  binary is:

```bash
/mnt/c/Users/HP/.vscode/extensions/openai.chatgpt-26.527.31454-win32-x64/bin/linux-x86_64/codex
```

The previously recorded extension path under
`openai.chatgpt-26.519.32039-win32-x64` no longer exists. Prefer `codex` from
`PATH` or `COAGENT_CODEX_BIN` instead of hard-coding a versioned extension
directory.

## Known Warnings

The successful run emitted non-fatal warnings:

- remote plugin sync requires ChatGPT auth; API key auth is not enough;
- featured plugin cache warmup failed for the same reason;
- shutdown reported several MCP process groups were already gone.

These warnings did not block the one-shot conversation.

## Visibility Caveat

`codex exec` and a raw interactive TUI launch can create valid rollout files and
`threads` rows without making the conversation visible in VSCode Codex or Codex
App task lists.

The observed hidden metadata pattern was:

```text
source: exec or cli
thread_source: user
has_user_event: 0
missing from session_index.jsonl
Windows Codex App state absent unless explicitly synced
```

The observed visible metadata pattern was:

```text
source: vscode
thread_source: vscode
has_user_event: 1
archived: 0
short title in session_index.jsonl
matching row in the Codex state DB used by the frontend
```

Use the project repair helper for one known candidate thread:

```bash
python3 CoAgent/dispatch/codex_session_repair.py sync-visible \
  --thread-id <thread-id> \
  --thread-name '<short title>' \
  --cwd /mnt/c/Users/HP/Desktop/MoSim \
  --source-codex-home /home/linux/.codex \
  --target-codex-home /home/linux/.codex \
  --target-codex-home /mnt/c/Users/HP/.codex
```

Add `--apply` only after reviewing the dry-run. The command backs up affected
Codex state before writing. A synced row is still not an accepted communication
target until the user confirms the conversation is visible and openable.
