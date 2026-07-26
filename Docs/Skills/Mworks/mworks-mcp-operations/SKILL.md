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
9. `MCP Transport closed`, a stale Sysplorer endpoint, or an ordinary recovery-after-abnormal-exit dialog is a recoverable tool incident, not a project blocker. End the clearly identifiable `mworks` and `sysplorer-acp-server` processes, restart MWORKS, maximize the target main window, handle the normal recovery dialog, rediscover the live port through the official API, and retry the same smallest operation. If the native MCP channel remains stale but official `ModelingPy` can connect to the recovered window, continue through that official API and preserve the recovery log. A model/compiler/connection error exposed after recovery is a route-level engineering result to repair or record while the next route proceeds.
10. Never call Sysplorer `ClearAll`, `ChangeDirectory`, or equivalent broad workspace-reset APIs. If the current directory must be inspected, use read-only inspection and pass absolute project paths to model operations.
11. For Sysblock diagram authoring, use official API calls (`call_code`, `ModelingPy`, `AddComponent`, `ConnectPort`, `SetModelParamValue`) rather than text replacement of block topology.
12. Current active-thread live MWORKS work should reuse current activation/window evidence when available and declare `live_mworks_touched`. Static file-only work keeps `live_mworks_touched=false`. Do not spend each task repeatedly proving activation or return only sentinel JSON. If the user has explicitly authorized bounded MWORKS login/license recovery for the current incident, set `will_not_click_activation_login=false`, capture/classify the visible state first, then operate only the official MWORKS/Sysplorer login, activation, recovery, or close controls needed for that recovery.
13. If no current activation/window evidence exists and live MCP/GUI work is required, run at most one bounded current-turn sentinel/API check or return a blocker. If a current-turn sentinel/capture is run for an incident, read the JSON/capture manifest or inspect screenshot/window-title metadata enough to classify `activation_state_observation` and `license_state`. Activation/login/license acceptance requires a maximized or foreground screenshot whose content actually shows the target reusable MWORKS/Sysplorer/Syslab main window; screenshots showing Codex App, another application, helper/proxy windows, or incomplete background output are not valid activation evidence. Use `-OutDir` with `capture_window_background.ps1`; `-OutputDir` is not a valid parameter.
14. Do not treat `Sysplorer [教育版]` as proof that the account is activated. It is only an edition/window marker; both activated and unactivated states may show it. If no login/demo/error marker appears, continue to the requested MCP/check/simulation/layout work and treat successful `check_model`/simulation without authorization errors as task-local license sufficiency evidence, not permanent activation.
15. If current evidence shows demo edition, login/activation prompt, authorization failure, mixed relevant windows, visible unknown blocking state, unknown blocking evidence, or a GUI error whose license/login/authorization meaning is unclear, first capture and classify it. If bounded recovery has already been explicitly authorized by the user/PMO, continue through the official recovery UI under rule 17. If recovery has not been authorized, stop and block the live task. Do not close the suspect window and continue by choosing a clean one.
16. Do not tune solvers, patch models, open a new MWORKS window, or click login/activation/save/close/restart/send-report/error-report controls while a license/login/authorization or unknown GUI incident is open.
17. Background screenshot evidence can miss the login/license pane. The current active thread may run bounded foreground/maximized official login recovery only when the user has explicitly authorized it; login/license screenshots must use maximized target-window evidence and must visually show that target window, not Codex/another app/helper windows. Authorized recovery sequence: screenshot and classify the dialog, click the smallest official recovery/login/activation control, wait 1-2 minutes normally and at most 5 minutes, capture the result, and retry the same smallest operation only after the main window is usable. If the official login action does not return or cannot complete on the existing window, the authorized recovery may reopen MWORKS and log in through the official UI as a bounded recovery. Use only the approved secure credential source and never write credentials to docs, logs, packets, screenshot manifests, email, or terminal output. Stop on MFA/captcha, account/password error, abnormal authorization, unknown modal/window, crash/error-report, save/overwrite prompt, or any non-MWORKS credential surface. Do not treat a visible login-failure code as the root cause without first recording the screenshot and deciding whether the next official recovery action is still inside the authorized scope. After success, close only the login/license dialog when possible and keep the reusable main window open.
18. Static file-only MWORKS tasks keep `live_mworks_touched=false` and may proceed without touching live MWORKS if they do not make live GUI/MCP claims.
19. Live MWORKS tasks still need phase evidence for the engineering claim. Simulation/control tasks capture and inspect screenshots after model load/check and after simulate/plot/animation phases when those phases run. Graphical/model-audit tasks capture and inspect screenshots during or after layout/diagram review, checking missing wires, disconnected blocks, unreadable routing, wrong active window, and new license/login/error dialogs. Ordinary phase screenshots use `capture_window_background.ps1 -RestoreMinimized -MinimizeAfter` with DPI/size/nonblank validation and no maximize. Formal simulation result bundles index or copy screenshots under `Results/<group>/<scene>/<experiment>/screenshots/` and write `Results/<group>/<scene>/<experiment>/logs/screenshot_manifest.json`. Return `mworks_phase_screenshots` and `mworks_phase_observations` when `live_mworks_touched=true` and GUI/layout/result-viewer evidence is part of the claim.
20. MWORKS model/simulation/layout tasks must name and produce engineering outputs such as `.mo`/`package.mo`, `check_model`, `SimulateModel`, native result/`.msr`, metrics, diagram/layout screenshots, or wiring observations. JSON packets, ledgers, and progress notes are control-plane evidence only, not engineering progress, unless the task type is explicitly one of `diagnostic_only`, `rule_sync_only`, `preflight_drill_only`, `dispatch_surface_diagnostic`, or `static_inventory_only`.
21. Activation/license/login/authorization evidence, or a GUI-error state whose meaning is unclear, at preflight or mid-task is a P0 MWORKS infrastructure incident. If bounded recovery is already explicitly authorized, perform the screenshot-first recovery path in rule 17 before declaring a blocker. If recovery is not authorized, or if a rule-17 stop trigger appears, stop live MCP/model/GUI work, return a blocker, and have PMO send a sparse email alert; WeChat is optional and diagnostic-only unless the user explicitly asks for it.
22. Non-license MWORKS internal/compiler/dmp incidents use a bounded retry path. First capture and inspect the exact dialog/screenshot/error text, preserving any `.dmp` path. If the evidence is an internal compiler error, crash dump prompt, stale GUI, or other non-credential MWORKS/Sysplorer malfunction with no login/license/authorization marker, restart or reopen MWORKS once through the normal session/process lifecycle and retry the same smallest command. If the same failure repeats after one restart, stop treating it as infrastructure and debug it as project/model/codegen/graphical topology. If the screenshot says missing wires, unconnected ports, no connection, `未连线`, or similar model-structure text, do not route it to activation recovery; route it directly to Sysblock/model repair.
23. For every unexpected MWORKS dialog or abnormal run result, the first action is visual classification, not code/model editing: capture the screenshot, record the visible error text, classify it as license/login/authorization, MWORKS internal/dmp/stale-GUI, graphical-topology/model-validation, or unknown. Only after that classification may the task continue.
24. If classification shows a non-license MWORKS software malfunction and no project-specific model error, restart or reopen MWORKS exactly once and retry the same smallest operation. If the retry passes, record it as transient MWORKS instability and continue. If the retry fails with the same symptom, treat it as a project-side issue. If the retry changes to a concrete project message such as missing connections, disconnected ports, invalid block topology, or code-generation validation failure, debug that concrete project issue instead of restarting again.

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
internal_or_dmp
graphical_topology
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
| demo edition / activation lost / login prompt | screenshot and classify first; if bounded recovery is explicitly authorized, operate the smallest official recovery/login/activation control and re-check within the 1-2 minute normal wait / 5 minute max wait; otherwise return `license_or_login` blocker |
| unexpected MWORKS dialog or abnormal run result | screenshot first, copy visible error text, classify the symptom, then choose restart, blocker, or project debug; do not edit code/model before classification |
| non-license internal compiler error / `.dmp` prompt / stale GUI crash | capture screenshot and error text, preserve the `.dmp` path when visible, restart or reopen MWORKS once, then retry the same smallest command; if it repeats, classify as project/model/codegen issue |
| missing wires / unconnected ports / `未连线` / no-connection screenshot | classify as `graphical_topology` or `model_check_failed`; inspect ports and repair the model, not license state |
| GUI interruption | stop the current MCP sequence; close only clearly identifiable stale/blocking windows; use the bounded one-restart path only when the screenshot rules out login/license/authorization |
| model auto-upgrade backup created | inspect the diff; do not commit auto-generated rewrites or backup directories unless intentionally accepted |
| workspace path looks wrong | do not call `ChangeDirectory`; reload target models with explicit absolute paths under the project |
