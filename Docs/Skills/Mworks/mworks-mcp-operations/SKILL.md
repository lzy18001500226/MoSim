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
12. For every MWORKS/Sysplorer/Syslab department task, run an activation preflight before business work, even when the task is static model-file organization. Use `Scripts/agent/check_mworks_gui_sentinel.py` and `Scripts/tools/capture_window_background.ps1` against the existing reusable window. Record `activation_sentinel_before`, `gui_sentinel_before`, `background_screenshot_before` when available, `activation_state_observation`, `license_state`, `will_not_click_activation_login=true`, `mworks_window_evidence_touched=true`, and `live_mworks_touched` in the return/blocker packet.
13. Do not only return screenshot paths. Read the sentinel JSON/capture manifest or inspect the screenshot/window-title metadata enough to classify the current window/license risk in `activation_state_observation` and `license_state` during the same task turn. If that evidence cannot be inspected or classified, return a blocker instead of continuing. Use `-OutDir` with `capture_window_background.ps1`; `-OutputDir` is not a valid parameter.
14. Do not treat `Sysplorer [教育版]` as proof that the account is activated. It is only an edition/window marker; both activated and unactivated states may show it. If only the education window/title is observed and no login/demo/error marker appears, use `license_state=education_window_observed_activation_unverified`. Live MCP/check/simulation work should also record `license_api_before` when available and should treat successful `check_model`/simulation without authorization errors as task-local license sufficiency evidence, not a permanent activation claim.
15. Treat the sentinel as an all-window gate. If any relevant MWORKS/Sysplorer/Syslab window is demo, login/activation, authorization-failed, GUI-error, mixed, or unknown, stop and block the whole task even if another window is education-mode. Do not close the suspect window and continue by choosing the clean one.
16. If the preflight sees demo edition, missing activation, login/activation prompts, authorization errors, an error-report dialog, mixed education/demo state, visible unknown MWORKS/Sysplorer/Syslab window, unavailable tooling, sentinel unavailable, screenshot unavailable, or an unknown state caused by sentinel failure, return `status=blocked` to PMO before live work. For unavailable tooling/sentinel/screenshot, use `license_state=sentinel_unavailable_blocked` and do not enter MCP/model/check/simulate/layout work. Hidden Qt/browser-proxy/helper windows with no license/error text are risk evidence, not standalone blockers. Do not tune solvers, patch models, open a new MWORKS window, or click login/activation/error-report controls from a specialist department.
17. Background screenshot evidence can miss the login/license pane. If the title, sentinel, or license API still indicates demo/login/authorization risk, delegated departments block instead of trusting a clean-looking screenshot. PMO may, after user authorization, maximize/focus the existing window and use only the official foreground login/license UI; after success, close only that dialog and keep the reusable main window open.
18. Static file-only MWORKS department tasks must keep `live_mworks_touched=false` but still set `mworks_window_evidence_touched=true` and include the activation/screenshot evidence. Only non-department compatibility checks may use a static packet without window evidence.
19. Live MWORKS tasks must continue background evidence during the task. R1 simulation/control tasks capture and inspect screenshots after model load/check and after simulate/plot/animation phases when those phases run. R2 graphical/model-audit tasks capture and inspect screenshots during or after layout/diagram review, checking missing wires, disconnected blocks, unreadable routing, wrong active window, and new license/login/error dialogs. Return `mworks_phase_screenshots` and `mworks_phase_observations` when `live_mworks_touched=true`.
20. MWORKS model/simulation/layout tasks must name and produce engineering outputs such as `.mo`/`package.mo`, `check_model`, `SimulateModel`, native result/`.msr`, metrics, diagram/layout screenshots, or wiring observations. JSON packets, ledgers, and progress notes are control-plane evidence only, not engineering progress, unless the task type is explicitly one of `diagnostic_only`, `rule_sync_only`, `preflight_drill_only`, `dispatch_surface_diagnostic`, or `static_inventory_only`.
21. Activation/license/login/authorization/GUI-error evidence at preflight or mid-task is a P0 MWORKS infrastructure incident. Stop live MCP/model/GUI work, return a blocker, and have PMO send both sparse WeChat and sparse email alert; do not rely on WeChat alone.

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
| demo edition / activation lost / login prompt | stop live MCP work; capture sentinel/screenshot evidence; return `license_or_login` blocker to PMO; PMO sends WeChat plus email alert |
| GUI interruption | stop the current MCP sequence; close only clearly identifiable stale/blocking windows |
| model auto-upgrade backup created | inspect the diff; do not commit auto-generated rewrites or backup directories unless intentionally accepted |
| workspace path looks wrong | do not call `ChangeDirectory`; reload target models with explicit absolute paths under the project |
