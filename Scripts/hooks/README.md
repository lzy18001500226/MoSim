# MoSim Hooks

## Purpose

This directory contains project-owned guardrails and preflight checks.

It is the project-local layer that turns policy into executable checks before
risky operations or long-running task execution.

## Current Components

| File | Purpose |
|---|---|
| `codex_native_hook.py` | adapter for Codex native lifecycle hooks. It is called by the global Codex hook config and delegates MoSim-specific checks to `preflight.py` only when the current `cwd` is inside this repository. |
| `context_recovery.py` | bounded per-session capture of direct user scope, exact URL/path references, `update_plan` checkpoints, and observed Goal token budgets; when that primary capture is absent, it can inspect only a fixed tail of the hook-provided `transcript_path` for one recognized latest direct-user JSONL entry. |
| `preflight.py` | project-local preflight for path boundary, write scope, sensitive-path risk, destructive commands, broad Git risk, large-file risk, terminal evidence, runtime-output ignore policy, and reference-index health |

## Codex Native Global Hook

Current Windows-native Codex setup uses the Codex native global hook file:

```text
C:\Users\HP\.codex\hooks.json
```

It registers:

| Event | Current MoSim behavior |
|---|---|
| `SessionStart` | Injects a concise startup reminder and, after compaction, the bounded task-recovery pack. A direct request to diagnose an unexpected stop is treated as a self-contained Hook/continuity task before any interrupted business source is requested. If the pack is unavailable, it first tries one strict, bounded `transcript_path` fallback; if neither path recovers the current input, it leaves continuity unresolved and requests only the minimum recovery source. |
| `UserPromptSubmit` | Captures the active direct user input before it can be compacted; blocks App-generated `<codex_internal_context source="goal">` continuations and consumes known Stop-generated continuation markers so internal text cannot become a new task. |
| `PostToolUse` for `update_plan` and Goal tools | Stores bounded tracking state. An `update_goal` transition to `blocked` or `completed` also emits one conversation-keyed terminal task email. |
| `PreCompact` | Associates the execution turn with the latest valid direct-user record before manual or automatic compaction; it does not overwrite that record with the assistant execution ID. |
| `PreToolUse` | Runs the project preflight adapter for shell commands, file edits, writes, patches, and MCP calls; blocks hard risks such as destructive Git commands, outside-project writes, secret-risk paths, and large-file offenders. It also blocks `create_goal.token_budget` unless the current direct user request explicitly sets the exact numeric value. |
| `Stop` | Has no continuation side effect. A missing current prompt must not create a synthetic user prompt, because it cannot recover scope and can loop through the same unresolved state. |

The global hook is intentionally scoped by `cwd`. It exits without action when
Codex is not operating inside `C:\Users\HP\Desktop\MoSim`, so the same Windows
Codex installation can still work on other projects.

The global file is the only MoSim hook registration. The repository keeps the
adapter scripts but deliberately does not install `/.codex/hooks.json`; this
avoids duplicate execution and separate project-level trust prompts. The
global recovery events provide:

| Event | Recovery behavior |
|---|---|
| `UserPromptSubmit` | Stores a redacted, bounded direct user prompt and its exact HTTP(S)/Windows-path source identities under ignored `Results/context_packs/`. |
| `PostToolUse` for `update_plan` | Stores the current bounded plan after Codex accepts the update, never as task authority. |
| `PreCompact` | Stores both the compaction execution turn and its resolved direct-user turn before manual or automatic compaction. |
| `SessionStart` with `source=compact` | Injects the bounded recovery pack before the immediate continuation model request. An atomic claim ensures concurrent compact starts emit it only once. |

The pack contains only scope, source identities, and plan tracking. Its primary
path does not parse transcript JSONL, read the referenced source content,
select a task from history, or make an old plan authoritative. If that primary
capture is absent, the adapter may read only a 256 KiB tail from the
hook-provided `transcript_path` and accept only the latest recognized
direct-user JSONL record. App-generated `<codex_internal_context source="goal">`
continuations are internal Goal metadata, not direct-user messages, so they are
rejected rather than retained or re-injected. It does not skip an internal Stop
continuation to reuse an older message, and it discards unknown formats. This is a last-resort
compatibility path because Codex does not promise transcript-format stability.
The resource catalog retains
at most six source-bearing turns and only the two most recent bundles can be
attached when a later user prompt explicitly refers to earlier resources. A
bundle holds at most 16 resources, each session retains at most 12 direct-user
turn records, and successful compaction claims retain at most eight markers.

Codex lifecycle events can expose different IDs for the direct-user submission
and the assistant execution being compacted. When the execution ID has no
direct-input record, `PreCompact` preserves the latest valid direct-user record
in the same session and records both IDs, so a normal long-running task does
not become `continuity_unresolved` solely because those IDs differ. If an event
explicitly supplies a newer direct-user ID whose record is absent, recovery
remains unresolved rather than replaying an older task. UserPromptSubmit also
falls back to `CODEX_THREAD_ID` and a generated direct-input ID when the App
omits event IDs. When a bounded transcript contains a newer recognized direct
user message, it takes precedence over the preserved record; the preserved
record is used only if that bounded check finds nothing. A Goal checkpoint is
kept only as local tracking state and never enters a recovery pack; plan
checkpoints remain tracking-only.

Sessions written by the earlier execution-ID behavior are repaired on their
next compact start when the active pointer is invalid but the last captured
direct-user record is still present. This migration is limited to the old state
shape and never overrides an explicit newer direct-user ID.

If no valid direct-user record is available, recovery first attempts the strict
transcript fallback above. If that also has no recognized current prompt, it
keeps continuity unresolved and asks only for the original prompt, active goal
text, or task-packet path; a current-thread read is optional only when exposed.
It never creates a synthetic Stop prompt, so stale instructions cannot replace
newer input or cause a continuation loop.

Codex requires non-managed hooks to be trusted before they run. In a new Codex
surface, use `/hooks` to review and trust the global entries after verifying
this file and `C:\Users\HP\.codex\hooks.json`. Do not bypass hook trust for
routine project work. If newly added capture entries are still awaiting review,
the already-trusted global `SessionStart` entry still reports the bounded
unresolved state. It must not manufacture a replacement prompt or discard the
user's task.

Existing Codex tasks may retain a previously loaded project hook definition
until the task or app refreshes its configuration. Restart or open a new task
before judging whether duplicate hook entries are gone. A legacy task that
compacted before `UserPromptSubmit` capture was trusted, and whose current
runtime does not expose `codex_app__read_thread`, can recover only when its
hook-provided `transcript_path` contains a recognized latest direct-user
record; otherwise request the minimum recovery input instead of guessing the
task.

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
python -m pytest Scripts/tests/test_context_recovery.py
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
