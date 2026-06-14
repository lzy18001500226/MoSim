# Candidate Figure Readiness Inventory, 2026-06-10

Status: static figure inventory, not final report acceptance.

- Source manifest: `Results/static_audits/submission_evidence_manifest_20260610/candidate_submission_evidence_manifest.json`
- Source manifest status: `review_candidate_not_final_acceptance`
- Candidate rows: `13`
- Report-figure ready rows: `13`
- Not-ready rows: `0`
- Rows without replay files: `0`
- Rows without log files: `0`

## Claim Boundary

- Report-figure readiness means local static files exist near candidate evidence.
- It is not final PMO acceptance and does not prove live MWORKS, ROS2, UE, or native Syslab completion.
- Replay and log absence is recorded as review context; it does not by itself invalidate figure readiness.

## Candidate Rows

| Claim Slot | Family | Ready | Figures | Missing Core Figures | Replay | Logs |
|---|---|---:|---:|---|---:|---:|
| C0-baseline-step-example1 | official_baseline | True | 8 |  | 1 | 1 |
| C0-baseline-helix-example2 | official_baseline | True | 4 |  | 1 | 1 |
| C0-baseline-figure8-example3 | official_baseline | True | 4 |  | 1 | 1 |
| C1-optimized-step-example1 | optimized_controller | True | 4 |  | 1 | 1 |
| C1-optimized-helix-example2 | optimized_controller | True | 4 |  | 1 | 1 |
| C1-optimized-figure8-example3 | optimized_controller | True | 4 |  | 1 | 1 |
| C1-robustness-mass20 | robustness | True | 4 |  | 1 | 1 |
| C1-robustness-wind-gust | robustness | True | 4 |  | 1 | 1 |
| C1-fault-tolerance-rotor1-loss-wind | fault_tolerance | True | 4 |  | 1 | 1 |
| C1-safety-filter-return-land | safety_filter | True | 4 |  | 1 | 1 |
| C2-formation-triangle-figure8 | multi_uav_formation | True | 4 |  | 1 | 1 |
| C1-visual-helical-figure8 | visual_trajectory_review | True | 4 |  | 1 | 1 |
| C1-visual-planar-figure8 | visual_trajectory_review | True | 4 |  | 1 | 1 |

## Not-Ready Rows

- None. All candidate rows have metrics/raw paths, figure manifests, and core figures.

## Notes

- Replay/log presence is tracked to help report review and traceability.
- Missing replay/log files should be reviewed before final report packaging.
