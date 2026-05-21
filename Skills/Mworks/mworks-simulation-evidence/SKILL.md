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
```

GUI review is required for visual claims, but GUI state is not the audit source.
The audit source is the artifact path plus source label and reproducible checks.

## Acceptance Checks

Pass only if:

1. `check_model` succeeded before simulation.
2. Required variables were found or mapped.
3. Raw result has a valid `time` column and more than 10 rows.
4. Core fields do not contain unexplained NaN/Inf.
5. Metrics identify controller, scenario, source, and timestamp.
6. The report does not overclaim offline evidence.
7. Formal Sysblock controller claims have a behavior-equivalent graphical Sysblock counterpart, or are explicitly labeled as equation-bridge evidence.

## Failure Handling

| Failure | Action |
|---|---|
| missing result variable | inspect available variables and update `docs/index/variable_mapping.md` |
| simulation fails | save error, inspect model, reduce to smoke scenario |
| controller unstable | preserve result as failed evidence; do not hide it |
| GUI disturbance | continue minimal MCP calls; keep reusable windows open |
| graphical counterpart missing | do not mark the controller complete; route to `mworks-sysblock-graphical-modeling` |
