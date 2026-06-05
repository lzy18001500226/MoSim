---
name: mworks-mcp-operations
description: Operate MWORKS MCP tools with minimal desktop disruption and safe project boundaries. Use when checking MCP availability, wrapper paths, Sysplorer/Syslab sessions, Git/filesystem/MinerU MCP behavior, WSL/Windows wrapper configuration, or when an MCP call fails or may open GUI windows.
---

# MWORKS MCP Operations

Keep MCP usage targeted, quiet, and project-local.

## Boundaries

Always treat this as active:

```text
操作权限仅限 C:\Users\HP\Desktop\MoSim
```

Use `/mnt/c/Users/HP/Desktop/MoSim` in WSL. Do not read or write outside the project unless the user explicitly asks for infrastructure setup.

## Wrapper Paths

Prefer auto-detection in scripts:

```text
C:\Users\HP\Desktop\MoSim\Docs\Skills\*\wrappers\*.cmd
/home/linux/mcp-wrappers/*.sh
~/mcp-wrappers/*.sh
environment variable override when available
```

For the Windows-native Codex App route, prefer Windows `.cmd` wrappers and do
not put `wsl.exe`, `\\wsl.localhost`, `/mnt/c`, or `/home/linux` launcher paths
in `C:\Users\HP\.codex\config.toml`. WSL wrappers are only for explicitly
WSL-backed runtime lanes.

## Minimal-Impact Rules

1. Use the smallest MCP tool sequence that proves the claim.
2. Prefer headless/background calls.
3. Reuse existing Sysplorer/Syslab sessions when useful.
4. Keep one reusable GUI window open during a related batch of checks when it avoids repeated startup cost.
5. Save useful MCP evidence under `results/test_reports/` or `results/logs/`.
6. Never write tokens, SSH keys, or API keys to tracked files.
7. Do not close reusable Sysplorer / Syslab / MWORKS windows before Git by default. Closing windows can force license reactivation and slow the next run.
8. Close or clean up only when the user asks, the GUI is frozen, a login/activation prompt blocks progress, or stale duplicate sessions are clearly causing failures.
9. If a GUI freezes, requests login unexpectedly, or an MCP call stalls past the planned timeout, stop that MCP sequence, clean up the clearly identifiable process/window, and continue with file-level work or report the blocker.
10. Never call Sysplorer `ClearAll`, `ChangeDirectory`, or equivalent broad workspace-reset APIs. If the current directory must be inspected, use read-only inspection and pass absolute project paths to model operations.
11. For Sysblock diagram authoring, use official API calls (`call_code`, `ModelingPy`, `AddComponent`, `ConnectPort`, `SetModelParamValue`) rather than text replacement of block topology.

## Tool Design Standard

When adding or changing MCP wrappers, helper scripts, or workflow-level MCP
steps, keep the tool boundary workflow-oriented:

1. Return high-signal results, not raw dumps that force the next agent to parse
   thousands of irrelevant lines.
2. Include actionable error messages: failing server/tool, exact command or
   model, original error text, likely cause, and next safe validation step.
3. Preserve protocol/session contracts. Do not hide `Tools: (none)`, login,
   activation, timeout, or GUI-freeze symptoms behind a generic script failure.
4. Validate one normal path and one expected failure path before documenting a
   tool sequence as the recommended workflow.

## Tool Routing

| Need | Go To |
|---|---|
| MCP tool list and sequences | `Docs/Index/api_index.md` |
| MCP troubleshooting | `Docs/Workflows/debug_mcp.md` |
| Model context | `Docs/Skills/Mworks/mworks-model-context/SKILL.md` |
| Simulation evidence | `Docs/Skills/Mworks/mworks-simulation-evidence/SKILL.md` |
| Graphical Sysblock controller modeling | `Docs/Skills/Mworks/mworks-sysblock-graphical-modeling/SKILL.md` |
| MATLAB/Simulink translation | `Docs/Skills/Mworks/mworks-syslab-porting/SKILL.md` |

## Failure Handling

Classify MCP/tool failures with this shared taxonomy:

```text
mcp_unavailable
tools_none
model_check_failed
simulate_failed
result_binding_failed
timeout
gui_blocked
license_or_login
permission
validation
unknown
```

Preserve the original server/tool/error text and the next safe validation step.
Do not collapse activation, login, GUI freeze, missing wrapper, and model
validation failures into a generic script failure.

GUI windows, plots, animations, and UI events are review surfaces, not audit
truth. Stable audit truth is the MCP/tool result, raw result path, metrics, log,
native-result locator, artifact manifest, and Git commit.

| Symptom | Action |
|---|---|
| `Tools: (none)` | Follow `workflows/debug_mcp.md` |
| wrapper missing | check server path, then `~/mcp-wrappers/` |
| Syslab stale state | call `restart_julia` |
| Sysplorer not ready | call `session_manager` health/probe/ensure |
| GUI interruption | stop the current MCP sequence; close only clearly identifiable stale/blocking windows |
| model auto-upgrade backup created | inspect the diff; do not commit auto-generated rewrites or backup directories unless intentionally accepted |
| workspace path looks wrong | do not call `ChangeDirectory`; reload target models with explicit absolute paths under the project |
