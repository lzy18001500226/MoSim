---
name: mworks-runtime-diagnostics
description: Diagnose failed, slow, unstable, or suspicious MWORKS simulations and model runs. Use when results are wrong at a time step, variables are missing, a model fails check/translate/simulate, solver/runtime is slow, controller output looks wrong, or you need a Simulink sldebug/profiler-style workflow adapted to MWORKS.
---

# MWORKS Runtime Diagnostics

Translate Simulink debugging/profiling habits into MWORKS evidence-first diagnostics.

## Triage Order

1. Identify the model, scenario, controller, and expected variable.
2. For live MWORKS/Sysplorer/Syslab diagnostics, reuse current activation/window evidence when available. Record `mworks_activation_reference` when known, `will_not_click_activation_login=true`, and `live_mworks_touched`. Do not spend the diagnostics turn repeatedly proving activation or return only sentinel JSON.
3. If no current activation/window evidence is available and the diagnostic needs live MCP/GUI work, run at most one bounded current-turn sentinel/API check or return a blocker. Activation/login/license evidence must include a maximized or foreground screenshot whose content actually shows the target reusable MWORKS/Sysplorer/Syslab main window; `capture_window_background.ps1` background output is auxiliary window-state evidence and uses `-OutDir`, not `-OutputDir`.
4. A visible `[教育版]` title is not proof of activation, but it is not by itself a blocker. Continue to the requested diagnostic/check/simulation work when no demo/login/authorization/error marker exists.
5. If current evidence reports demo edition, missing activation/login prompt, authorization failure, mixed education/demo state, unavailable tooling, visible unknown blocking state, unknown blocking evidence, or a GUI error whose meaning is unclear, stop runtime diagnostics and return a `status=blocked` `license_or_login` or GUI blocker. Do not treat these symptoms as solver/model bugs.
6. Background screenshots can miss a hidden login/license pane. The current active thread may run foreground/maximized official login recovery only when the user has explicitly authorized it, and login/license screenshots must be maximized target-window evidence whose content visually matches that window; otherwise do not click login/activation/save/close/send-report controls. If the official login action does not return or cannot complete on the existing window, authorized recovery may reopen MWORKS and log in through the official UI as a bounded recovery. Use only the approved secure credential source; never write credentials to docs, logs, packets, screenshot manifests, email, or terminal output. Stop on MFA/captcha, account/password error, abnormal authorization, unknown modal/window, non-MWORKS credential surface, save/overwrite prompt, send-report/close prompt, or any title/control mismatch.
7. Non-license internal/compiler/dmp incidents have a bounded retry route. Capture and inspect the screenshot/error text first; preserve the visible `.dmp` path. If there is no login/license/activation/authorization marker and the symptom is an internal compiler error, crash dump prompt, stale GUI, or one-off GUI malfunction, restart or reopen MWORKS once, retry the same smallest command, then stop and debug the model/codegen path if the same failure repeats.
8. If the screenshot/error text says missing wires, unconnected ports, no connection, `未连线`, or similar model-structure wording, classify it as model/graphical topology. Inspect source, ports, and visible topology instead of routing to activation recovery.
9. During live diagnostics, capture and inspect phase screenshots after load/check and after simulate/plot/animation phases when those visuals are part of the claim. Ordinary phase screenshots use DPI-aware background capture with `-RestoreMinimized -MinimizeAfter`, size/nonblank validation, and no maximize. Formal simulation result bundles include `screenshots/` and `logs/screenshot_manifest.json`. Return `mworks_phase_screenshots` and `mworks_phase_observations`; the observations must state what the screenshot/window evidence showed.
10. If activation/license/login/authorization or unclear GUI-error evidence appears mid-task, stop live diagnostics and return a P0 MWORKS infrastructure blocker to PMO. PMO or user-authorized ops handles notification and recovery.
11. Run or inspect `check_model`.
12. If structure changed, inspect model text and component ports.
13. Run the smallest targeted simulation that reproduces the issue.
14. Probe result variables and values around the suspicious time.
15. A completed diagnostics/model task must produce engineering evidence such as `.mo`/`package.mo`, `check_model`, `SimulateModel`, native result/`.msr`, metrics, plots, or result variables. JSON packets and ledger/progress notes are not the engineering deliverable.
16. Save the failure as evidence; do not hide unstable results.

## MCP Sequence

```text
current activation/window evidence when available
  -> if absent and live work is needed: one bounded sentinel/API check or blocker
  -> if license/login/GUI blocker: stop and return blocker
  -> bounded official login recovery only when user-authorized
  -> otherwise continue
session_manager
  -> after load/check: phase screenshot and observation when GUI evidence is claimed
  -> model_manager(get_components/get_model_text/get_component_ports)
  -> check_model
  -> translate_model if compilation/build detail is needed
  -> simulate_model with shortest useful target_time
  -> after simulate/plot/animation: phase screenshot and observation
  -> result_manager(get_result_variable_info/get_vars_value_at/get_vars_values)
```

## Common Cases

| Problem | Diagnostic |
|---|---|
| missing variable | inspect components/ports and update `docs/index/variable_mapping.md` |
| wrong signal sign | compare model port meaning, coordinate convention, and reference bus |
| unstable controller | preserve raw result and inspect saturation, NaN, mode, motor commands |
| slow simulation | reduce scenario, compare target time, note compile vs run-time symptoms |
| model check failure | inspect source text and library docs before patching |
| solver/runtime issue | record error, time range, model name, controller, and minimal reproduction |
| internal compiler error or `.dmp` prompt with no license/login marker | screenshot first, preserve dmp path, restart/reopen MWORKS once, retry the same smallest command, then debug model/codegen if repeated |
| missing wires / unconnected ports / `未连线` | classify as model/graphical topology and inspect ports/wiring |
| demo edition / activation lost / login prompt | stop live diagnostics and return a `license_or_login` blocker; bounded official login recovery is allowed only under explicit user authorization and credential-redaction rules |
| clean-looking background screenshot but title/API says demo or logged out | block and ask PMO for bounded foreground recovery; do not continue solver/model diagnostics |

## Outputs

Use the smallest artifact that helps future debugging:

```text
results/test_reports/{case}.jsonl
results/logs/{case}_diagnostics.md
docs/index/variable_mapping.md update
workflow/report note with source label
```

## Do Not

1. Do not guess an equivalent of Simulink `sldebug`; use MWORKS introspection and result probing.
2. Do not claim a GUI plot proves correctness without raw data or metrics.
3. Do not broaden to batch runs until a smoke case reproduces or clears the issue.
4. Do not continue solver/model trial-and-error while the reusable MWORKS window is in demo, unactivated, login, authorization-failed, or GUI-error-report state.
