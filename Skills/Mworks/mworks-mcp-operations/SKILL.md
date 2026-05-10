---
name: mworks-mcp-operations
description: Operate MWORKS MCP tools with minimal desktop disruption and safe project boundaries. Use when checking MCP availability, wrapper paths, Sysplorer/Syslab sessions, Git/filesystem/MinerU MCP behavior, WSL/Windows wrapper configuration, or when an MCP call fails or may open GUI windows.
---

# MWORKS MCP Operations

Keep MCP usage targeted, quiet, and project-local.

## Boundaries

Always treat this as active:

```text
操作权限仅限 C:\Users\HP\Desktop\Quadrotor
```

Use `/mnt/c/Users/HP/Desktop/Quadrotor` in WSL. Do not read or write outside the project unless the user explicitly asks for infrastructure setup.

## Wrapper Paths

Prefer auto-detection in scripts:

```text
/home/linux/mcp-wrappers/*.sh
~/mcp-wrappers/*.sh
environment variable override when available
```

Do not hard-code only one user home.

## Minimal-Impact Rules

1. Use the smallest MCP tool sequence that proves the claim.
2. Prefer headless/background calls.
3. Reuse existing Sysplorer/Syslab sessions when useful.
4. Keep one reusable GUI window open during a related batch of checks when it avoids repeated startup cost.
5. Save useful MCP evidence under `results/test_reports/` or `results/logs/`.
6. Never write tokens, SSH keys, or API keys to tracked files.
7. Before `git add`, `git commit`, or `git push`, close or explicitly verify closure of Sysplorer / Syslab / MWORKS windows and MCP wrapper/server processes created in the current round.
8. If a GUI freezes, requests login unexpectedly, or an MCP call stalls past the planned timeout, stop that MCP sequence, clean up the clearly identifiable process/window, and continue with file-level work or report the blocker.

## Tool Routing

| Need | Go To |
|---|---|
| MCP tool list and sequences | `docs/index/api_index.md` |
| MCP troubleshooting | `workflows/debug_mcp.md` |
| Model context | `Skills/Mworks/mworks-model-context/SKILL.md` |
| Simulation evidence | `Skills/Mworks/mworks-simulation-evidence/SKILL.md` |
| MATLAB/Simulink translation | `Skills/Mworks/mworks-syslab-porting/SKILL.md` |

## Failure Handling

| Symptom | Action |
|---|---|
| `Tools: (none)` | Follow `workflows/debug_mcp.md` |
| wrapper missing | check server path, then `~/mcp-wrappers/` |
| Syslab stale state | call `restart_julia` |
| Sysplorer not ready | call `session_manager` health/probe/ensure |
| GUI interruption | stop the current MCP sequence; close only clearly identifiable stale windows before Git |
| model auto-upgrade backup created | inspect the diff; do not commit auto-generated rewrites or backup directories unless intentionally accepted |
