# CoAgent Hooks

## Purpose

This directory contains project-owned guardrails and preflight checks.

It is the CoAgent layer that turns policy into executable checks before risky
operations, dispatch, or long-running task execution.

## Current Components

| File | Purpose |
|---|---|
| `preflight.py` | project-local CoAgent preflight for path boundary, write scope, secret-risk paths, destructive commands, broad Git risk, large-file risk, result-packet evidence, task runtime files, and reference-index health |

## Current Commands

```bash
python CoAgent/hooks/preflight.py
python CoAgent/hooks/preflight.py --path CoAgent/runtime/mosim_agent_runtime.py
python CoAgent/hooks/preflight.py --write-path Results/tmp --command "git status" --result-packet Results/agent_packets/example.json
python CoAgent/hooks/preflight.py --full-repo-large-scan
```

Default mode keeps the large-file scan scoped to CoAgent-related tracked files
so it returns quickly in this repository. Use `--full-repo-large-scan` only
when a wider Git artifact audit is actually required.

`runtime_output_ignore` uses `git check-ignore` to confirm the current
CoAgent runtime/review output locations are ignored:

- `Results/coagent_doctor/`
- `Results/coagent_gateway/`
- `Results/coagent_status/`
- `Results/coagent_transport/`
- `Results/agent_runtime/`
- `Results/agent_packets/`
- `Results/context_packs/`
- Python `__pycache__/` files

`git_workspace_state` checks local Git safety before a long-running task tries
to commit:

- `.git/index.lock` is a hard failure because Git may be wedged or another Git
  owner may be active.
- staged `Results/`, `__pycache__/`, or `*.pyc` files are hard failures.
- staged `References/` or large external skill/reference trees are hard
  failures unless a separate reviewed import task explicitly owns that batch.
- staged file counts over the configured threshold are warnings; split or
  delegate large commits instead of one broad `git add -A`.

## Boundary

This is not a replacement for:

- `AGENTS.md`
- `Scripts/quality/doctor.py`
- GitHub/CI checks

It is a CoAgent-owned local gate focused on:

- agent runtime safety,
- dispatch safety,
- reference-index consistency,
- project boundary compliance,
- large-file and secret-risk preflight signals.
- destructive-command and broad-Git risk checks,
- terminal result-packet evidence checks.
- runtime output ignore checks so local doctor/status/gateway/runtime artifacts
  stay out of Git unless a reviewed task explicitly changes that policy.
