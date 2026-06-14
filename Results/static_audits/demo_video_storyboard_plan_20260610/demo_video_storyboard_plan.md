# Demo Video Storyboard Plan, 2026-06-10

Status: `storyboard_plan_not_demo_video_acceptance`

## Summary

- Candidate rows: `13`
- Scenes: `7`
- Planned duration: `280 s`
- Missing figure links: `0`
- Storyboard ready for review: `True`
- Demo video exists: `False`
- Safe to record demo video now: `False`
- Records or renders video now: `False`
- Generates final outputs: `False`

## Claim Boundary

- This artifact is a storyboard and recording checklist only.
- It does not record, render, encode, or create demo_video.mp4.
- It does not claim final PMO acceptance or final submission readiness.
- It does not prove ROS2 planner_ready, closed_loop, or UE runtime success.

## Scenes

### 1. Scope and evidence boundary

- Scene ID: `S0-boundary-title`
- Duration: `20 s`
- Candidate rows: `0`
- Recording status: `not_recorded`
- Allowed narration:
  - This demo is planned from static candidate evidence only.
  - Final video recording and PMO acceptance are still pending.

### 2. Official PID baseline across required scenes

- Scene ID: `S1-official-pid-baseline`
- Duration: `45 s`
- Candidate rows: `3`
- Recording status: `not_recorded`
- Allowed narration:
  - Show baseline PID behavior for step, helix, and figure-8 scenes.
  - Use saved raw data, metrics, replay, and figures as candidate evidence.
- Evidence rows:
  - `C0-baseline-step-example1` / `official_example1_pid_baseline` (rmse=0.276295, health=52.464)
  - `C0-baseline-helix-example2` / `official_example2_pid_baseline` (rmse=0.487183, health=47.8827)
  - `C0-baseline-figure8-example3` / `official_example3_pid_baseline` (rmse=0.172311, health=60.5054)

### 3. Optimized controller comparison

- Scene ID: `S2-optimized-controller-comparison`
- Duration: `55 s`
- Candidate rows: `3`
- Recording status: `not_recorded`
- Allowed narration:
  - Compare optimized Sysblock controller candidates against official PID baseline.
  - Discuss tracking RMSE and health-score changes from saved metrics only.
- Evidence rows:
  - `C1-optimized-step-example1` / `official_example1_linear_mpc_sysblock` (rmse=0.135014, health=65.6656)
  - `C1-optimized-helix-example2` / `official_example2_linear_mpc_sysblock` (rmse=0.429079, health=62.0578)
  - `C1-optimized-figure8-example3` / `official_example3_linear_mpc_sysblock` (rmse=0.084584, health=68.3362)

### 4. Robustness, fault tolerance, and safety filter

- Scene ID: `S3-robustness-fault-safety`
- Duration: `60 s`
- Candidate rows: `4`
- Recording status: `not_recorded`
- Allowed narration:
  - Show mass perturbation, wind gust, rotor degradation, and safety-filter candidate evidence.
  - Keep boundary cases separate from completed pass cases.
- Evidence rows:
  - `C1-robustness-mass20` / `robust_mass20_example1_linear_mpc_sysblock` (rmse=0.2588, health=55.3882)
  - `C1-robustness-wind-gust` / `robust_wind_gust_example1_linear_mpc_sysblock` (rmse=0.2588, health=55.3882)
  - `C1-fault-tolerance-rotor1-loss-wind` / `robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock` (rmse=0.261434, health=51.3177)
  - `C1-safety-filter-return-land` / `official_example1_qp_nmpc_safety_return_land_sysblock` (rmse=0.208361, health=56.146)

### 5. Leader-follower multi-UAV formation

- Scene ID: `S4-formation-control`
- Duration: `40 s`
- Candidate rows: `1`
- Recording status: `not_recorded`
- Allowed narration:
  - Show the triangle figure-8 formation candidate and its formation score.
  - Describe this as saved Sysplorer/MWORKS candidate evidence, not live closed-loop acceptance.
- Evidence rows:
  - `C2-formation-triangle-figure8` / `formation_triangle_figure8_linear_mpc_sysblock` (rmse=0.0212508, health=93.6862, formation=100.0)

### 6. Visual trajectory review assets

- Scene ID: `S5-visual-trajectory-review`
- Duration: `35 s`
- Candidate rows: `2`
- Recording status: `not_recorded`
- Allowed narration:
  - Show planar and helical figure-8 visual-review trajectory candidates.
  - Do not claim UE build, runtime, editor, or final visual acceptance from these rows.
- Evidence rows:
  - `C1-visual-helical-figure8` / `official_example1_helical_figure8_trail_sysblock` (rmse=0.0188363, health=93.3606)
  - `C1-visual-planar-figure8` / `official_example1_planar_figure8_trail_sysblock` (rmse=0.0188624, health=93.3638)

### 7. Final packaging gates

- Scene ID: `S6-final-packaging-gates`
- Duration: `25 s`
- Candidate rows: `0`
- Recording status: `not_recorded`
- Allowed narration:
  - List remaining final artifacts: PDFs, demo video, and PMO acceptance packet.
  - State that final submission readiness remains blocked until those artifacts exist and are reviewed.

## Forbidden Video Claims

- final PMO acceptance
- final submission ready
- planner_ready
- closed_loop
- ROS2 controller handoff
- UE build/runtime/editor success
- native Syslab complete report generation
- live MWORKS no-start attach success
- final visual acceptance

## Blockers

- `demo_video_not_recorded`: Results/submission/demo_video.mp4 is missing Needed action: record or render the reviewed storyboard only after approval
- `manual_storyboard_review_required`: storyboard content must be reviewed before recording Needed action: confirm scenes, wording, and evidence boundaries before producing video
