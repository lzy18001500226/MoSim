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

If the work needs live MWORKS/Sysplorer/Syslab GUI/result-viewer evidence, reuse
current activation/window evidence when available. Return or blocker packets
should include `mworks_activation_reference` when known,
`will_not_click_activation_login=true`,
`bounded_login_recovery_user_authorized` when applicable, and
`live_mworks_touched`. Do not turn report/visualization work into repeated
activation probing or accept sentinel JSON as the report artifact.

If no current activation/window evidence exists and the work needs live MWORKS GUI/result-viewer
evidence, run at most one bounded current-turn sentinel/API check or return a
blocker. If current evidence shows demo, login, activation,
authorization, mixed blocking state, unavailable tooling, unknown blocking
state, or GUI error-report state, stop MWORKS/report evidence work and return a
`status=blocked` blocker. Bounded official login recovery is allowed only when
explicitly user-authorized, with
foreground/maximized target-window evidence, credential redaction, and the
MoSim stop conditions. For live report/result-viewer/plot/animation work,
ordinary phase screenshots use DPI-aware background capture with
`-RestoreMinimized -MinimizeAfter`, size/nonblank validation, and no maximize.
Use foreground/maximized screenshots only for activation/login/license/
authorization evidence or explicitly requested full-window review. Return
`mworks_phase_screenshots`, `mworks_phase_observations`, and
`screenshot_manifest`. If a phase screenshot shows activation/license/login/
authorization/GUI-error state, treat it as a P0 MWORKS infrastructure incident
and stop live evidence work.

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
