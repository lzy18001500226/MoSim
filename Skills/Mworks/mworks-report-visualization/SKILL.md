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

## Report Update Rule

When adding a figure or metric, update the smallest relevant section of `docs/simulation_report.md` or `docs/user_manual.md`. Avoid duplicating design theory there.
