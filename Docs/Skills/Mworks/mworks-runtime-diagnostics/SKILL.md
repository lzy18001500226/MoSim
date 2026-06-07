---
name: mworks-runtime-diagnostics
description: Diagnose failed, slow, unstable, or suspicious MWORKS simulations and model runs. Use when results are wrong at a time step, variables are missing, a model fails check/translate/simulate, solver/runtime is slow, controller output looks wrong, or you need a Simulink sldebug/profiler-style workflow adapted to MWORKS.
---

# MWORKS Runtime Diagnostics

Translate Simulink debugging/profiling habits into MWORKS evidence-first diagnostics.

## Triage Order

1. Identify the model, scenario, controller, and expected variable.
2. If the task is owned by a MWORKS/Sysplorer/Syslab department, run the activation sentinel and background screenshot before business work, even when the task is static file organization. Record `activation_sentinel_before`, `gui_sentinel_before`, `background_screenshot_before` when available, `activation_state_observation`, `license_state`, `will_not_click_activation_login=true`, `mworks_window_evidence_touched=true`, and `live_mworks_touched`.
3. Do not only return paths. Read the sentinel JSON/capture manifest or inspect the screenshot/window-title metadata enough to classify the current activation state in the same task turn. If that evidence cannot be inspected or classified, return a blocker and do not continue runtime diagnostics. `capture_window_background.ps1` uses `-OutDir`, not `-OutputDir`.
4. Treat the sentinel as an all-window gate. One relevant MWORKS/Sysplorer/Syslab window in demo, login/activation, authorization-failed, GUI-error, mixed, or visible unknown state blocks the whole diagnostic, even if another window is education-mode. Hidden Qt/browser-proxy/helper windows with no license/error text are risk evidence and must be counted, but they do not alone prove authorization loss.
5. If the sentinel/screenshot evidence reports demo edition, missing activation, login/activation prompt, authorization failure, mixed education/demo state, error-report dialog, unavailable tooling, visible unknown window, or unknown sentinel state, stop runtime diagnostics and return a `status=blocked` `license_or_login` or GUI blocker to PMO. Do not treat these symptoms as solver/model bugs.
6. Background screenshots can miss a hidden login/license pane. If the window title, sentinel, or `License(ltype="info")` still indicates demo/login/authorization risk, block instead of accepting a clean-looking screenshot. PMO may run a user-authorized foreground recovery on the existing window only; departments do not click login/activation controls.
7. During live diagnostics, capture and inspect phase screenshots after load/check and after simulate/plot/animation phases when they run. Return `mworks_phase_screenshots` and `mworks_phase_observations`; the observations must state what the screenshot/window evidence showed.
8. If activation/license/login/authorization/GUI-error evidence appears mid-task, stop live diagnostics and return a P0 MWORKS infrastructure blocker to PMO. PMO must send both sparse WeChat and sparse email alert for the open incident.
9. Run or inspect `check_model`.
10. If structure changed, inspect model text and component ports.
11. Run the smallest targeted simulation that reproduces the issue.
12. Probe result variables and values around the suspicious time.
13. A completed diagnostics/model task must produce engineering evidence such as `.mo`/`package.mo`, `check_model`, `SimulateModel`, native result/`.msr`, metrics, plots, or result variables. JSON packets and ledger/progress notes are not the engineering deliverable.
14. Save the failure as evidence; do not hide unstable results.

## MCP Sequence

```text
activation sentinel / background screenshot
  -> if license/login/GUI blocker: stop and return blocker
  -> otherwise continue
session_manager
  -> after load/check: background screenshot and observation
  -> model_manager(get_components/get_model_text/get_component_ports)
  -> check_model
  -> translate_model if compilation/build detail is needed
  -> simulate_model with shortest useful target_time
  -> after simulate/plot/animation: background screenshot and observation
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
| demo edition / activation lost / login prompt | stop live diagnostics and return a `license_or_login` blocker; PMO sends WeChat plus email alert and retries only after clean preflight proves recovery |
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
