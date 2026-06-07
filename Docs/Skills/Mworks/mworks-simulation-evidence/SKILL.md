---
name: mworks-simulation-evidence
description: Run or validate MWORKS.Sysplorer/Syslab simulation evidence for this quadrotor project. Use when the user asks to run a simulation, reproduce official examples, compare controllers, read results, calculate metrics, generate figures, create report evidence, or distinguish real MWORKS evidence from offline demos.
---

# MWORKS Simulation Evidence

Use this skill to produce report-ready, reproducible evidence.

## Evidence Classes

Label outputs explicitly:

| Label | Meaning |
|---|---|
| `source=MWORKS_MCP` | Produced through Sysplorer/Syslab MCP or MWORKS session |
| `source=MWORKS_GUI` | Produced manually in MWORKS GUI |
| `source=offline_script` | Produced by Python/Julia reference generator without running the official model |

Do not present offline CSV/HTML replay as official MWORKS simulation evidence.

## Simulation Workflow

Follow these files:

```text
workflows/run_simulation.md
workflows/read_results.md
workflows/calc_metrics.md
workflows/generate_report_figures.md
docs/index/variable_mapping.md
workflows/build_sysblock_graphical_controller.md
```

Minimum MCP sequence:

```text
activation sentinel / background screenshot
  -> if license/login/GUI blocker: stop and return blocker
session_manager
  -> load_library / model_manager
  -> check_model
  -> simulate_model
  -> result_manager
  -> plot_manager or Syslab metrics
```

## Required Evidence Bundle

For every real MWORKS simulation, save or update:

```text
scenario YAML or run config
controller parameter file
MCP JSONL/tool log when available
raw CSV under results/raw/
metrics JSON/CSV under results/metrics/ or results/test_reports/
figures or replay assets under results/figures/ or docs/figures/
report note in docs/simulation_report.md when relevant
```

Every evidence bundle should include `artifact_refs`:

```text
raw result path
metrics path
figure / replay / native-result path when present
MCP/tool log path when present
source label: MWORKS_MCP | MWORKS_GUI | offline_script
optional sha256 and byte size for files used in report claims
claim role: raw | metrics | figure | replay | native_result | log
activation_sentinel_before
background_screenshot_before
mworks_phase_screenshots
mworks_phase_observations
activation_state_observation
license_state
will_not_click_activation_login=true
live_mworks_touched
mworks_window_evidence_touched
```

GUI review is required for visual claims, but GUI state is not the audit source.
The audit source is the artifact path plus source label and reproducible checks.

## Acceptance Checks

Pass only if:

1. MWORKS department work ran `Scripts/agent/check_mworks_gui_sentinel.py` and `Scripts/tools/capture_window_background.ps1` before business work. Static file-only department work records `live_mworks_touched=false`; real MCP/model/GUI simulation work records `live_mworks_touched=true`.
2. The department read the sentinel JSON/capture manifest or inspected the screenshot/window-title metadata enough to classify the current activation state in `activation_state_observation` and `license_state`; path-only evidence is not enough.
3. The reusable MWORKS/Sysplorer/Syslab session was not in demo, unactivated, login, authorization-failed, mixed education/demo, unavailable, unknown, or GUI-error-report state.
4. Live simulation/model/GUI work included phase background screenshots and observations after load/check and after simulate/plot/animation phases when those phases ran. `background_screenshot_before` alone is not sufficient for live MWORKS evidence.
5. `check_model` succeeded before simulation.
6. Required variables were found or mapped.
7. Raw result has a valid `time` column and more than 10 rows.
8. Core fields do not contain unexplained NaN/Inf.
9. Metrics identify controller, scenario, source, and timestamp.
10. The report does not overclaim offline evidence.
11. Formal Sysblock controller claims have a behavior-equivalent graphical Sysblock counterpart, or are explicitly labeled as equation-bridge evidence.

## Failure Handling

| Failure | Action |
|---|---|
| missing result variable | inspect available variables and update `docs/index/variable_mapping.md` |
| simulation fails | save error, inspect model, reduce to smoke scenario |
| controller unstable | preserve result as failed evidence; do not hide it |
| GUI disturbance | stop live work if sentinel or phase screenshots report login/license/error-report state; otherwise continue minimal MCP calls and keep reusable windows open |
| graphical counterpart missing | do not mark the controller complete; route to `mworks-sysblock-graphical-modeling` |
| demo edition / activation lost / login prompt / mixed or unknown license state | return a `status=blocked` `license_or_login` blocker with sentinel and background screenshot evidence; PMO sends WeChat plus email alert; do not tune solver/model code |
