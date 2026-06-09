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
latest CoAgentOps activation patrol reference
  -> if no recent patrol and live work is needed: one bounded sentinel/API check or blocker
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
mworks_activation_patrol_reference
mworks_activation_patrol_age_minutes when known
mworks_phase_screenshots
mworks_phase_observations
will_not_click_activation_login=true
live_mworks_touched
current-turn activation_state_observation/license_state only if sentinel or capture was collected for an incident
```

GUI review is required for visual claims, but GUI state is not the audit source.
The audit source is the artifact path plus source label and reproducible checks.

## Acceptance Checks

Pass only if:

1. MWORKS department work references the latest CoAgentOps activation/window patrol when available. Static file-only department work records `live_mworks_touched=false`; real MCP/model/GUI simulation work records `live_mworks_touched=true`.
2. If no recent patrol exists and live MCP/GUI work is needed, the department ran at most one bounded current-turn sentinel/API check or returned a blocker. If current-turn evidence was collected, the department inspected it and classified `activation_state_observation` and `license_state`; path-only evidence is not enough.
3. The reusable MWORKS/Sysplorer/Syslab session was not in demo, unactivated, login, authorization-failed, mixed education/demo, unknown blocking, or GUI-error-report state according to the patrol or current task evidence.
4. Live simulation/model/GUI work included phase screenshots and observations after load/check and after simulate/plot/animation phases when those visuals were claimed. A patrol reference alone is not sufficient for GUI/result-viewer evidence claims.
5. `check_model` succeeded before simulation.
6. Required variables were found or mapped.
7. Raw result has a valid `time` column and more than 10 rows.
8. Core fields do not contain unexplained NaN/Inf.
9. Metrics identify controller, scenario, source, and timestamp.
10. The report does not overclaim offline evidence.
11. Formal Sysblock controller claims have a behavior-equivalent graphical Sysblock counterpart, or are explicitly labeled as equation-bridge evidence.

## Simulation Cleanup And Session Rules

For MWORKS simulations:

1. Run `check_model` before simulation.
2. Run the smallest simulation that validates the current change first.
3. Read the required result variables after simulation; do not treat
   `simulate_model ok` alone as quality evidence.
4. Save logs, smoke-test evidence, and native result references only when they
   support a claim or future debugging.
5. Keep one Sysplorer/Syslab/MWORKS GUI window open during a related batch of
   checks to avoid repeated startup cost and license reactivation. Do not close
   it before Git unless the user asks or it is blocking progress.
6. Do not leave long-running simulations active after the task is complete.
7. Prefer one active Sysplorer/Syslab session at a time unless parallel
   simulation is explicitly required.
8. Reuse an existing session for related operations instead of opening many
   windows.
9. If repeated simulations open multiple windows, stop opening new MCP
   sessions, clean up clearly identifiable stale windows before Git, and prefer
   fixing model files offline before retrying MCP.
10. Do not document a model as verified unless its latest version has a
    successful `load_file` and `check_model` log, or the report explicitly
    marks it as an unverified draft.
11. After temporary smoke tests, probes, or failed MCP attempts, delete
    `.running`, `.tmp`, `__pycache__`, and ad-hoc probe logs before commit.
12. If previously working simulations start returning unexplained activation,
    login, license, library-load, or authorization failures, preserve source
    changes, remove temporary artifacts, stop retrying MCP, and return a
    blocker for PMO/CoAgentOps recovery. Known signatures include `L5104-B0`,
    `软件尚未激活`, equation-limit authorization errors, unexpected demo mode,
    login prompts, and authorization failures.
13. If a MWORKS/Sysplorer GUI error-report dialog appears, save or reference a
    screenshot and write a GUI-incident blocker before further simulation work.
    Include visible dialog text, triggering task/command, report path or
    visible prefix when available, and proposed recovery action.
14. At the end of a completed simulation task, leave reusable GUI windows open
    and report which scenario/result should be manually reviewed.

## Failure Handling

| Failure | Action |
|---|---|
| missing result variable | inspect available variables and update `docs/index/variable_mapping.md` |
| simulation fails | save error, inspect model, reduce to smoke scenario |
| controller unstable | preserve result as failed evidence; do not hide it |
| GUI disturbance | stop live work if sentinel or phase screenshots report login/license/error-report state; otherwise continue minimal MCP calls and keep reusable windows open |
| graphical counterpart missing | do not mark the controller complete; route to `mworks-sysblock-graphical-modeling` |
| demo edition / activation lost / login prompt / mixed or unknown license state | return a `status=blocked` `license_or_login` blocker with sentinel and background screenshot evidence; PMO sends sparse email alert; do not tune solver/model code |
