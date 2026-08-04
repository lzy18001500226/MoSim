# MoSim Hooks

## Purpose

This directory contains project-owned guardrails and preflight checks.

It is the project-local layer that turns policy into executable checks before
risky operations or long-running task execution.

## Current Components

| File | Purpose |
|---|---|
| `codex_native_hook.py` | adapter for Codex native lifecycle hooks. It is called by the global Codex hook config and delegates MoSim-specific checks to `preflight.py` only when the current `cwd` is inside this repository. |
| `preflight.py` | project-local preflight for path boundary, write scope, sensitive-path risk, destructive commands, broad Git risk, large-file risk, terminal evidence, runtime-output ignore policy, and reference-index health |

## Codex Native Global Hook

Current Windows-native Codex setup uses the Codex native global hook file:

```text
C:\Users\HP\.codex\hooks.json
```

It registers:

| Event | Current MoSim behavior |
|---|---|
| `SessionStart` | Injects a concise reminder to read `AGENTS.md` and `Docs/Workflows/new_conversation_context.md`; it does not load the full project memory. |
| `PreToolUse` | Runs the project preflight adapter for shell commands, file edits, writes, patches, and MCP calls; blocks hard risks such as destructive Git commands, outside-project writes, secret-risk paths, and large-file offenders. |
| `Stop` | No-op for now. Do not enable broad auto-continue logic here because it can create loops. |

The global hook is intentionally scoped by `cwd`. It exits without action when
Codex is not operating inside `C:\Users\HP\Desktop\MoSim`, so the same Windows
Codex installation can still work on other projects.

Codex requires non-managed hooks to be trusted before they run. In a new Codex
surface, use `/hooks` to review and trust the hook hash after verifying this
file and `C:\Users\HP\.codex\hooks.json`. Do not bypass hook trust for routine
project work.

Recurring health owner:

| Item | Owner | Cadence | Evidence |
|---|---|---|---|
| Hook trust and smoke tests | Current MoSim maintainer | After Codex upgrade or after hook/preflight edits | Test output plus this file if behavior changes |
| Windows-native Codex config or hook path repair | Current task-local maintainer under explicit user scope | On blocker only | Blocker/result packet plus exact external path reason |

Use `Docs/Workflows/documentation_governance.md` for placement rules when hook
behavior changes.

## Current Commands

```bash
python Scripts/hooks/preflight.py
python Scripts/hooks/preflight.py --path Scripts/hooks/preflight.py
python Scripts/hooks/preflight.py --write-path Results/tmp --command "git status" --result-packet Results/agent_packets/example.json
python Scripts/hooks/preflight.py --full-repo-large-scan
python Scripts/hooks/codex_native_hook.py
python Scripts/hooks/recover_git_index_lock.py --json
```

`recover_git_index_lock.py` is report-only by default. After confirming that no
repository writer is running and the lock is older than the safety threshold, an
explicit `--confirm-stale` invocation may remove only the exact repository
`.git/index.lock`; it never kills or restarts a process. Unclassified
repository processes are treated as active and block removal.

Hook smoke tests:

```powershell
$json = @{
  cwd = 'C:\Users\HP\Desktop\MoSim'
  hook_event_name = 'SessionStart'
  source = 'resume'
} | ConvertTo-Json -Compress
$out = $json | python Scripts\hooks\codex_native_hook.py | ConvertFrom-Json
if (-not $out.hookSpecificOutput.additionalContext) { throw 'expected additionalContext' }

$cmd = @(('g' + 'it'), ('res' + 'et'), ('-' + '-hard')) -join ' '
$json = @{
  cwd = 'C:\Users\HP\Desktop\MoSim'
  hook_event_name = 'PreToolUse'
  tool_name = 'Bash'
  tool_input = @{ command = $cmd }
} | ConvertTo-Json -Compress -Depth 5
$out = $json | python Scripts\hooks\codex_native_hook.py | ConvertFrom-Json
if ($out.hookSpecificOutput.permissionDecision -ne 'deny') { throw 'expected deny' }
if ($out.hookSpecificOutput.permissionDecisionReason -notmatch 'destructive_command') { throw 'expected destructive_command reason' }
```

The first command should return `additionalContext`. The second command should
return a `PreToolUse` deny decision. The destructive fixture is assembled at
runtime so the outer Codex hook does not block the smoke command before the
adapter receives the test payload.

Default mode keeps the large-file scan scoped to hook and workflow related tracked files
so it returns quickly in this repository. Use `--full-repo-large-scan` only
when a wider Git artifact audit is actually required.

`runtime_output_ignore` uses `git check-ignore` to confirm the current
runtime/review output locations are ignored:

- `Results/coagent_doctor/`
- `Results/coagent_gateway/`
- `Results/coagent_status/`
- `Results/coagent_transport/`
- `Results/agent_runtime/`
- `Results/agent_packets/`
- `Results/context_packs/`
- Python `__pycache__/` files

Tracked files are reported separately and are not required to match ignore
rules; untracked future runtime outputs must still be ignored before this check
passes.

`git_workspace_state` checks local Git safety before a long-running task tries
to commit:

- `.git/index.lock` is a hard failure because Git may be wedged or another Git
  owner may be active.
- staged `Results/`, `__pycache__/`, or `*.pyc` files are hard failures.
- staged `References/` or large external skill/reference trees are hard
  failures unless a separate reviewed import task explicitly owns that batch.
- staged file counts over the configured threshold are warnings; split or
  delegate large commits instead of one broad `git add -A`.

The reference-index check includes filesystem-only imports. Classify an
external reference root in `Docs/Index/reference_project_index.md` without
adding the imported source tree to version control.

Secret-risk checks are path-sensitive. Project return/blocker packet files
under `Results/agent_packets/returns/` and `Results/agent_packets/blockers/`
may contain task labels such as `SECRET`, `token`, or `credential` in the
packet filename; those labels alone are not treated as private material. Real
sensitive filenames and paths are still blocked, including Codex auth files,
SSH key paths, credential JSON files, client secret JSON files, token files,
and shell environment assignments whose variable names contain auth, secret,
credential, or token segments. Benign capacity terms such as `token_limit`,
`--token-limit`, and `max_tokens` remain allowed.

## Boundary

This is not a replacement for:

- `AGENTS.md`
- `Scripts/quality/doctor.py`
- GitHub/CI checks
- Codex native hook trust and product-level sandbox/approval settings

It is a project-owned local gate focused on:

- agent runtime safety,
- task and execution safety,
- reference-index consistency,
- project boundary compliance,
- large-file and secret-risk preflight signals.
- destructive-command and broad-Git risk checks,
- terminal evidence checks.
- runtime output ignore checks so local doctor/status/gateway/runtime artifacts
  stay out of Git unless a reviewed task explicitly changes that policy.
