---
name: mworks-report-visualization
description: Prepare report-ready figures, metrics tables, replay assets, and demo-video material for the MWORKS quadrotor project. Use when generating plots, replay HTML/JSON, health-score summaries, simulation report sections, user manual updates, or video-story assets.
---

# MWORKS Report Visualization

Turn simulation outputs into honest, report-ready evidence.

## Source Rule

Every visual claim must trace back to:

```text
scenario/config
raw CSV or MWORKS result
metrics JSON/CSV
figure/replay path
source label
```

Do not let replay or offline animation replace real simulation evidence.

If the work is owned by a MWORKS/Sysplorer/Syslab department, run the
activation sentinel and background screenshot before business work, even if the
business slice later stays offline or report-only. Return or blocker packets
must include `activation_sentinel_before`, `gui_sentinel_before`,
`background_screenshot_before`, `activation_state_observation`,
`license_state`, `will_not_click_activation_login=true`,
`mworks_window_evidence_touched=true`, and `live_mworks_touched`. The
department must read the sentinel JSON/capture manifest or inspect the
screenshot/window-title metadata enough to classify the current activation
state; path-only evidence is not enough. If the preflight shows demo, login,
activation, authorization, mixed, unavailable tooling, sentinel unavailable,
screenshot unavailable, unknown, or GUI error-report state, stop MWORKS/report
evidence work and return a `status=blocked` blocker. For unavailable
tooling/sentinel/screenshot, use `license_state=sentinel_unavailable_blocked`
and do not enter MCP/model/check/simulate/layout work.
For live report/result-viewer/plot/animation work, continue background
screenshots after plot/result-viewer/animation phases and return
`mworks_phase_screenshots` plus `mworks_phase_observations`. If a phase
screenshot shows activation/license/login/authorization/GUI-error state, treat
it as a P0 MWORKS infrastructure incident; stop live evidence work and have PMO
send both sparse WeChat and sparse email alert.

## Workflows

```text
workflows/generate_report_figures.md
workflows/calc_metrics.md
workflows/produce_simulation_evidence.md
docs/simulation_report.md
docs/user_manual.md
```

## Required Visual Assets

| Claim | Asset |
|---|---|
| tracking improvement | trajectory plot + position error plot + metrics table |
| robustness | disturbed vs nominal metrics + recovery time |
| safety/fault | event log + constraint/fault metric + replay marker |
| planning | path/trajectory plot + obstacle distance + trackability score |
| formation | multi-UAV replay + formation error + min inter-UAV distance |

## Replay Rules

1. Replay reads exported data; it does not participate in control.
2. `replay.json` should include time, UAV state, reference, events, obstacles, and metrics.
3. Keep video narration aligned with implemented features and evidence level.

## HTML / Replay Validation

For HTML replay, dashboard, or report-preview outputs, do not accept the file
only because it exists. Validate the smallest useful render path:

```text
source raw/metrics/replay path
output HTML/SVG/PNG path
nonzero file size
expected title or manifest entry
expected data series count
visual smoke check when a browser/canvas is involved
```

If a dev server or browser is needed, start the smallest local process,
wait for the page to stabilize, capture the relevant evidence, and stop only
the process that was started for this check. Do not let visual artifacts become
control or planning evidence.

## Report Update Rule

When adding a figure or metric, update the smallest relevant section of `docs/simulation_report.md` or `docs/user_manual.md`. Avoid duplicating design theory there.
