# MoSim Profile Configs

Status: active ExperimentProfile config skeleton, 2026-06-24.

This directory turns the architecture contract in
`Docs/Design/架构/00_架构与任务/ExperimentProfile与兼容性矩阵.md` into
machine-checkable project profiles.

## Layout

| Path | Purpose |
| --- | --- |
| `catalog.json` | Registered profile ids and the minimum metadata needed by the validator. |
| `runtime_bindings.json` | Static mapping from LaunchPlan templates to project-local runtime source paths. |
| `metrics_schema.json` | Metric definitions and required evidence semantics used by preflight. |
| `tracking_sources.json` | Registered source-column contracts for converting separate reference/state logs into standard `tracking.csv`. |
| `runtime_log_exports.json` | Registered runtime artifact collection contracts for logs, screenshots, review files, and CSV exports. |
| `experiments/` | ExperimentProfile files submitted by scripts, Agent tasks, or the future UI. |
| `candidates/` | Retained design-intent and compatibility ExperimentProfiles for controller families. These are not included by `--all`; they may be blocked or may validate after the referenced catalog profile moves to `implemented`. |
| `templates/` | Launch Plan, Run Manifest, and Profile Rejection skeleton shapes. |

`ExperimentProfile.profile_status` defaults to `active`. Profiles marked
`blocked` or `archived` are retained in `experiments/` only for audit/debug
traceability. `check_experiment_profile.py --all` and
`build_experiment_preflight.py --all` skip them by default; passing such a file
explicitly must reject before launch/preflight.

`RuntimeExportProfile` entries currently live in `catalog.json`. They describe
what a real ROS1/Sunray run must export after landing before the files are
collected into a run packet.

The current batch covers Goal 1 and Goal 2 px4ctrl baselines plus the first
FAST-LIO comparison branches:

```text
px4ctrl_takeoff_hover_land_v1
px4ctrl_figure8_baseline_v1
px4ctrl_spiral_baseline_v1
px4ctrl_step_baseline_v1
fastlio_independent_eval_figure8_v1
fastlio_px4_ekf_ab_figure8_v1
fastlio_hybrid_z_figure8_v1
g9_official_pid_figure8_v1
g9_se3_basic_figure8_v1
g9_dfbc_basic_figure8_v1
g9_smc_boundary_layer_figure8_v1
g9_pid_indi_figure8_v1
g9_nmpc_outer_figure8_v1
g10a_dfbc_smooth_robust_no_dob_figure8_v1
g10a_dfbc_smooth_robust_dob_figure8_v1
  -> G10-A DOB/ESO paired ablation profiles. The no-DOB profile keeps the same
     DFBC smooth bounded controller but forces the disturbance observer and
     compensation to zero; the DOB profile enables the low-frequency
     acceleration-residual observer through `dfbc_smooth_robust_dob`.
  -> These profiles are launch-intent contracts only until paired runtime A/B
     packets prove improvement under the selected disturbance or model-error
     scenario.
g10c_dfbc_smooth_robust_no_indi_figure8_v1
g10c_dfbc_smooth_robust_indi_figure8_v1
  -> `profile_status=blocked`. Current G10-C ATTITUDE_THRUST translational INDI
     runtime is blocked by
     `Results/sunray_ros1/g10c_indi_blocker_review_20260630_141530/SUMMARY.md`.
     Keep these profiles only for audit or explicit INDI-interface reopen.
g95_dfbc_high_order_takeoff_hover_land_v1
g95_dfbc_high_order_figure8_v1
g95_dfbc_high_order_bodyrate_takeoff_hover_land_v1
g95_dfbc_high_order_bodyrate_figure8_v1
g96_dfbc_smooth_robust_takeoff_hover_land_v1
g96_dfbc_smooth_robust_figure8_v1
g96_dfbc_smooth_robust_bodyrate_takeoff_hover_land_v1
g96_dfbc_smooth_robust_bodyrate_figure8_v1
  -> `profile_status=blocked`. G9.6 BODYRATE_THRUST release-smoke failed the
     takeoff-hover-land attribution gate; keep these ids only for explicit
     interface-debug/audit work.
  -> Current evidence:
     `Results/sunray_ros1/g96_bodyrate_failure_attribution_20260630_103317/G96_BODYRATE_ATTRIBUTION.json`
  -> Do not use these profiles for G10/G11 active batches unless the
     BODYRATE_THRUST interface task is explicitly reopened.
```

Skipped-by-default blocked profiles retained for audit:

```text
g10c_official_pid_no_indi_figure8_v1
g10c_official_pid_indi_figure8_v1
  -> Legacy prepared contracts from the earlier official-PID ablation route.
     They remain blocked/audit-only because G10-C now uses the accepted
     runnable G9.6 DFBC smooth robust baseline as the nominal controller.
g96_dfbc_smooth_robust_bodyrate_takeoff_hover_land_v1
g96_dfbc_smooth_robust_bodyrate_figure8_v1
```

G9 controller-family profiles start in `candidates/` until the corresponding
controller has source/paper audit, implementation evidence, and interface
evidence. While the referenced `controller_profile` has
`implementation_status=planned`, checking the candidate directly must reject
with `C-CTRL-01`. After implementation, the active profile is copied into
`experiments/`; the retained candidate file may validate because it references
the same now-implemented controller profile, but it remains outside `--all` and
does not count as runtime acceptance. Runtime acceptance still requires a real
run packet.

Current implemented-but-not-accepted G9 profiles:

```text
g9_official_pid_figure8_v1
  -> C++ ATTITUDE_THRUST backend, static G9-A gate, single-UAV Gazebo tasks,
     Diff-Planner single-UAV, and Diff-Planner three-UAV evidence are present
  -> User-frozen accepted baseline, MWORKS generated-code acceptance, and
     PX4-native deployment are still forbidden claims
g9_se3_basic_figure8_v1
  -> C++ ATTITUDE_THRUST backend, static G9-B gate, single-UAV Gazebo tasks,
     Diff-Planner single-UAV, and Diff-Planner three-UAV evidence are present
  -> User-frozen accepted baseline, MWORKS generated-code acceptance, and
     PX4-native deployment are still forbidden claims
g9_dfbc_basic_figure8_v1
  -> C++ ATTITUDE_THRUST backend, static G9-C gate, single-UAV Gazebo tasks,
     Diff-Planner single-UAV, and Diff-Planner three-UAV evidence are present
  -> User-frozen accepted baseline, jerk/snap high-order mode, MWORKS
     generated-code acceptance, and PX4-native deployment are still forbidden
     claims
g9_smc_boundary_layer_figure8_v1
  -> C++ ATTITUDE_THRUST backend, static G9-D gate, single-UAV Gazebo tasks,
     Diff-Planner single-UAV, and Diff-Planner three-UAV evidence are present
  -> User-frozen accepted baseline, terminal/super-twisting/body-rate SMC,
     MWORKS generated-code acceptance, and PX4-native deployment are still
     forbidden claims
g9_pid_indi_figure8_v1
  -> C++ ATTITUDE_THRUST backend, static G9-E gate, single-UAV Gazebo tasks,
     Diff-Planner single-UAV, and Diff-Planner three-UAV evidence are present
  -> User-frozen accepted baseline, standalone/body-rate/rotor-level INDI,
     MWORKS generated-code acceptance, and PX4-native deployment are still
     forbidden claims
g9_nmpc_outer_figure8_v1
  -> C++ ATTITUDE_THRUST backend, static G9-F gate, single-UAV Gazebo tasks,
     Diff-Planner single-UAV, and Diff-Planner three-UAV evidence are present
  -> User-frozen accepted baseline, full nonlinear online solver feasibility,
     MWORKS generated-code acceptance, and PX4-native deployment are still
     forbidden claims
g95_dfbc_high_order_takeoff_hover_land_v1
g95_dfbc_high_order_figure8_v1
  -> C++ ATTITUDE_THRUST backend, static G9.5 gate, and paper-derived
     high-order DFBC fields are present
  -> Body-rate/body-acceleration feedforward release, MWORKS generated-code
     acceptance, PX4-native deployment, and user-frozen G9.5 acceptance are
     still forbidden claims until real Gazebo metrics are reviewed
g95_dfbc_high_order_bodyrate_takeoff_hover_land_v1
g95_dfbc_high_order_bodyrate_figure8_v1
  -> C++ BODYRATE_THRUST release-smoke profiles use the existing px4ctrl
     `use_bodyrate_ctrl=true` MAVROS path and the mission-node jerk/yaw-rate
     fields. They prove only body-rate/thrust interface viability until full
     Gazebo metrics are reviewed.
  -> Snap/body-acceleration command-path acceptance, MWORKS generated-code
     acceptance, PX4-native deployment, and user-frozen G9.5 acceptance remain
     forbidden claims.
g96_dfbc_smooth_robust_takeoff_hover_land_v1
g96_dfbc_smooth_robust_figure8_v1
  -> C++ ATTITUDE_THRUST backend, static G9.6 gate, bounded feedback, and
     disturbance-estimate diagnostics are present
  -> Unknown-wind robustness, released DOB augmentation, MWORKS generated-code
     acceptance, PX4-native deployment, and user-frozen G9.6 acceptance are
     still forbidden claims until real Gazebo metrics are reviewed
g96_dfbc_smooth_robust_bodyrate_takeoff_hover_land_v1
g96_dfbc_smooth_robust_bodyrate_figure8_v1
  -> Blocked BODYRATE_THRUST release-smoke profiles use the existing px4ctrl
     `use_bodyrate_ctrl=true` MAVROS path and the mission-node jerk/yaw-rate
     fields. The current attribution packet shows the interface is not an
     active runnable G9.6 candidate.
  -> Unknown-wind robustness, released DOB augmentation, snap/body-acceleration
     command-path acceptance, MWORKS generated-code acceptance, PX4-native
     deployment, and user-frozen G9.6 acceptance remain forbidden claims.
```

Current retained G9 candidate ids:

```text
g9_se3_basic_figure8_candidate_v1
g9_dfbc_basic_figure8_candidate_v1
g9_smc_boundary_layer_figure8_candidate_v1
g9_pid_indi_figure8_candidate_v1
g9_nmpc_outer_figure8_candidate_v1
```

These candidates now have corresponding active profiles under `experiments/`
after implementation evidence was added. They are retained as design-intent
skeletons and compatibility regression fixtures; they are not included by
`--all` and do not override the implemented-but-not-accepted status of the
active `experiments/` profiles.

These configs are not runtime evidence. They are launch-intent contracts.
Runtime success still requires logs, metrics, screenshots, review notes, and a
Run Manifest under `Results/`.

## Validation

Run:

```powershell
python Scripts/quality/check_experiment_profile.py --all
```

Check a G9 candidate explicitly:

```powershell
python Scripts/quality/check_experiment_profile.py Config/profiles/candidates/g9_dfbc_basic_figure8_candidate_v1.json
```

Expected result for planned candidates whose referenced `controller_profile`
still has `implementation_status=planned`:

```text
ok=false
reason_code=C-CTRL-01
control_started=false
```

If the referenced controller profile has already moved to `implemented`, the
candidate may validate successfully. That result only proves the skeleton is
compatible with the implemented controller profile; it is still not runtime
evidence and is still excluded from `--all`.

To also emit static skeleton artifacts:

```powershell
python Scripts/quality/check_experiment_profile.py --all --emit-artifacts-dir Results/profile_validation/px4ctrl_baseline_static
```

Dry-run preflight:

```powershell
python Scripts/quality/build_experiment_preflight.py --all --emit-artifacts-dir Results/profile_validation/px4ctrl_baseline_static
```

Prepare a formal pre-run packet for one profile:

```powershell
python Scripts/quality/prepare_experiment_run.py Config/profiles/experiments/px4ctrl_takeoff_hover_land_v1.json --run-id <run_id>
```

This creates `Results/runs/<run_id>/LaunchPlan.json`,
`RUN_MANIFEST.json`, `preflight.json`, `source_hashes.json`,
`operator_checklist.md`, `commands.md`, `review.template.md`, and empty
`screenshots/`, `logs/`, and `raw/` directories. It does not start runtime
and does not create `tracking.csv`, `metrics.json`, or `review.md`.
`RUN_MANIFEST.json` is bound to the current source state through
`source_hashes.json`, `git_commit`, `git_dirty`, and source hash digests.

Run the full offline gate for a completed run packet:

```powershell
python Scripts/quality/run_experiment_gate.py Config/profiles/experiments/px4ctrl_takeoff_hover_land_v1.json --run-id <run_id> --reference-csv <reference.csv> --state-csv <state.csv> --runtime-log-profile fastlio_hybrid_z_runtime_log_export_v1 --tracking-source-profile fastlio_xy_yaw_gazebo_z_reference_state_csv_v1 --review-file <review.md> --screenshot <rviz.png> --log <ros.log>
```

Use `--prepare-only` when only the formal pre-run packet should be created.
Without `--prepare-only`, the formal accepted path requires real reference and
state CSV exports plus `--runtime-log-profile`. The wrapper writes
`runtime_export_manifest.json`, `runtime_log_manifest.json`, `tracking.csv`,
`metrics.json`, `threshold_report.json`, and `run_gate_report.json` before
invoking the Run Evidence Gate. It is still offline and never starts ROS,
Gazebo, PX4, MAVROS, RViz, UE, or MWORKS. `--tracking-csv` remains useful for
diagnostics, but a formal accepted packet must still satisfy both
`runtime_export_manifest.json` and `runtime_log_manifest.json`.

The runtime export chain has three distinct contracts:

```text
RuntimeExportProfile
  -> what a real ROS1/Sunray run must export after landing
  -> required artifact slots, source producers, expected destinations, review requirements

RuntimeLogProfile
  -> how exported files are copied into Results/runs/<run_id>
  -> artifact slot names, packet destinations, file size/hash provenance

TrackingSourceProfile
  -> how reference/state CSV columns are aligned into standard tracking.csv
  -> column names, phase/saturation source, timestamp tolerance
  -> state source, height source, localization-eval role, and leaderboard group

Localization CSV / map summary
  -> used only by FAST-LIO independent localization evaluation
  -> estimate-vs-Gazebo-truth pose, velocity, delay, sequence gaps, and map coverage
  -> does not replace tracking.csv for controller trajectory review
```

Current tracking source split:

```text
px4_mavros_fused_reference_state_csv_v1
  -> px4ctrl baseline control-state tracking

fastlio_eval_reference_state_csv_v1
  -> FAST-LIO evaluation-only run context; control state remains PX4/MAVROS fused
  -> formal localization metrics come from raw/localization.csv + raw/map_summary.json

fastlio_px4_ekf_fused_reference_state_csv_v1
  -> FAST-LIO odometry after PX4 EKF fusion, exported through MAVROS local state

fastlio_xy_yaw_gazebo_z_reference_state_csv_v1
  -> FAST-LIO XY/Yaw plus explicit Gazebo truth-aligned Z through the simulation alignment adapter
```

`px4ctrl_takeoff_hover_land_v1` is bound only to the Hybrid-Z runtime export
and tracking-source profiles above. Do not substitute the legacy
`px4_mavros_fused_*` export contracts for this profile: they describe a
different GPS/rangefinder-era state contract.

`prepare_experiment_run.py` writes the selected RuntimeExportProfile into
`preflight.json`, `RUN_MANIFEST.json`, `operator_checklist.md`, and
`commands.md`. The generated commands are still templates; they do not prove
runtime success until real exported files are collected and validated.

For real ROS/Sunray exports where reference and state/truth are separate CSV
files, prefer a registered TrackingSourceProfile:

```powershell
python Scripts/quality/run_experiment_gate.py Config/profiles/experiments/px4ctrl_takeoff_hover_land_v1.json --run-id <run_id> --reference-csv <reference.csv> --state-csv <state.csv> --runtime-log-profile fastlio_hybrid_z_runtime_log_export_v1 --tracking-source-profile fastlio_xy_yaw_gazebo_z_reference_state_csv_v1 --review-file <review.md> --screenshot <rviz.png> --log <ros.log>
```

Use explicit column arguments only for one-off diagnostics or when defining a
new TrackingSourceProfile.

Normalize a raw tracking CSV into the standard metrics input:

```powershell
python Scripts/quality/normalize_tracking_csv.py raw_tracking.csv --out Results/runs/<run_id>/tracking.csv --map time_s=stamp --map ref_x_m=ref_x --map ref_y_m=ref_y --map ref_z_m=ref_z --map truth_x_m=truth_x --map truth_y_m=truth_y --map truth_z_m=truth_z --default phase=unknown --default saturated=0
```

Build standard `tracking.csv` from separate reference and state/truth logs:

```powershell
python Scripts/quality/build_tracking_csv.py --reference-csv reference.csv --state-csv state.csv --out Results/runs/<run_id>/tracking.csv --tracking-source-profile fastlio_xy_yaw_gazebo_z_reference_state_csv_v1
```

After a real runtime finishes and exports artifacts, export them through the
registered RuntimeExportProfile. This is the preferred entry point because it
checks the run manifest binding, required artifact slots, source producers,
standard destinations, and required CSV columns before delegating collection to
the RuntimeLogProfile layer:

```powershell
python Scripts/quality/export_runtime_sources.py Results/runs/<run_id> --runtime-export-profile sunray_fastlio_hybrid_z_runtime_export_v1 --artifact reference_csv=<reference.csv> --artifact state_csv=<state.csv> --artifact rviz_screenshot=<rviz.png> --artifact ros_log=<ros.log> --review-file <review.md> --build-tracking
```

For FAST-LIO eval-only packets, the runtime export must additionally provide
the localization comparison stream and map coverage summary:

```powershell
python Scripts/quality/export_runtime_sources.py Results/runs/<run_id> --runtime-export-profile sunray_fastlio_eval_runtime_export_v1 --artifact reference_csv=<reference.csv> --artifact state_csv=<state.csv> --artifact localization_csv=<localization.csv> --artifact map_summary_json=<map_summary.json> --artifact rviz_screenshot=<rviz.png> --artifact ros_log=<ros.log> --review-file <review.md> --build-tracking
```

`localization.csv` is a FAST-LIO estimate-vs-Gazebo-truth log. It must contain
`stamp`, `seq`, estimated/truth position, estimated/truth velocity,
estimated/truth yaw, and `delay_s`. `map_summary.json` must contain
`map_completeness`, `coverage_ratio`, `observed_ratio`, or `coverage.ratio`.

This writes `runtime_export_manifest.json` and `runtime_log_manifest.json`,
copies raw CSVs to `raw/`, copies review screenshots and logs to the standard
evidence directories, and can build `tracking.csv` plus
`tracking_alignment_report.json`. The final Run Evidence Gate validates both
manifests: RuntimeExportProfile binding, required export slots, source file
size/hash, copied destination size/hash, RuntimeLogProfile linkage, tracking
linkage, required topics, and review requirements. It is still offline and does
not start ROS, Gazebo, PX4, MAVROS, RViz, UE, or MWORKS.

`collect_runtime_evidence.py` remains the low-level RuntimeLogProfile collector
for tests or explicit maintenance. Normal experiment packets should use
`export_runtime_sources.py` first.

Compute tracking metrics from a completed run:

```powershell
python Scripts/quality/compute_tracking_metrics.py Results/runs/<run_id>/tracking.csv --manifest Results/runs/<run_id>/RUN_MANIFEST.json --out Results/runs/<run_id>/metrics.json
```

Compute FAST-LIO independent localization metrics from a completed eval-only run:

```powershell
python Scripts/quality/compute_tracking_metrics.py --localization-csv Results/runs/<run_id>/raw/localization.csv --map-summary-json Results/runs/<run_id>/raw/map_summary.json --manifest Results/runs/<run_id>/RUN_MANIFEST.json --out Results/runs/<run_id>/metrics.json
```

Check whether metrics pass the evaluation threshold profile:

```powershell
python Scripts/quality/check_metric_thresholds.py Results/runs/<run_id>/metrics.json --manifest Results/runs/<run_id>/RUN_MANIFEST.json --report Results/runs/<run_id>/threshold_report.json
```

Validate a completed run evidence packet:

```powershell
python Scripts/quality/check_run_evidence.py Results/runs/<run_id>
```

Regression tests:

```powershell
python -m pytest Scripts/tests/test_experiment_profile_validator.py Scripts/tests/test_experiment_preflight.py Scripts/tests/test_prepare_experiment_run.py Scripts/tests/test_tracking_normalizer.py Scripts/tests/test_build_tracking_csv.py Scripts/tests/test_export_runtime_sources.py Scripts/tests/test_collect_runtime_evidence.py Scripts/tests/test_metric_threshold_gate.py Scripts/tests/test_run_evidence_gate.py Scripts/tests/test_run_experiment_gate.py -q
```

The validator checks:

```text
required ExperimentProfile slots
profile id registration
controller reference order vs trajectory output
controller output interface vs adapter input interface
state source / truth / hybrid-Z boundaries
optional localization evaluation source boundaries
controller safety and adapter compatibility
planner ownership of MAVROS control
display/runtime compatibility
runtime export profile compatibility and required artifact slots
RuntimeLogProfile registration, experiment compatibility, artifact slots, and TrackingSourceProfile linkage
TrackingSourceProfile registration, experiment compatibility, state/height/localization role, and leaderboard group
```

The dry-run preflight adds:

```text
LaunchPlan run_id binding
RunManifest template expansion
runtime template to project-local source path checks
runtime export contract expansion
metrics schema coverage checks
FAST-LIO EKF / Hybrid-Z state-source gate checks
```

The run preparation tool adds:

```text
one-profile run_id binding
Results/runs/<run_id> directory creation
LaunchPlan.json / RUN_MANIFEST.json materialization
operator checklist and command template output with RuntimeExportProfile slots
empty runtime evidence directories without fake evidence files
source_hashes.json and source_state binding in RUN_MANIFEST.json
runtime_log_exports.json and tracking_sources.json provenance in RUN_MANIFEST.json/source_hashes.json
```

The run experiment gate wrapper adds:

```text
one-command offline gate orchestration
prepare-only mode for formal pre-run packet creation
RuntimeLogProfile collection for formal accepted packets
standard tracking.csv copy or raw CSV normalization for diagnostic packets
metrics.json and threshold_report.json generation
FAST-LIO independent localization metrics from raw/localization.csv and raw/map_summary.json
runtime_log_manifest.json and review / screenshot / log attachment from real caller-provided evidence
final accepted decision requiring threshold accepted=true and evidence gate ok=true
```

The tracking normalizer adds:

```text
raw CSV column mapping into standard tracking.csv
required reference/truth/time column coverage checks
numeric validation for metrics columns
phase and saturated default handling
```

The tracking CSV builder adds:

```text
separate reference CSV and state/truth CSV alignment
nearest timestamp matching with strict max time-delta rejection
explicit reference/state column contracts
registered TrackingSourceProfile shortcuts for known ROS/Sunray exports
standard tracking.csv output plus tracking_alignment_report.json
```

The runtime export and evidence collection tools add:

```text
registered RuntimeExportProfile artifact slots, producer notes, destinations, and CSV column checks
runtime_export_manifest.json with source artifact size/hash and review requirements
registered RuntimeLogProfile artifact slots
required artifact rejection before final evidence review
runtime_log_manifest.json with source path, destination, size, and sha256
optional reference/state CSV to tracking.csv conversion through TrackingSourceProfile
FAST-LIO eval-only localization_csv and map_summary_json collection for ATE/RPE/delay/drop/map-completeness metrics
review.md, screenshots/, logs/, raw/ packet population without starting runtime
```

The run evidence gate adds:

```text
RUN_MANIFEST.json / LaunchPlan.json hash alignment
run_id consistency across run directory, LaunchPlan, RunManifest, and metrics
source_state / source_hashes.json reproducibility checks
placeholder value rejection
required artifact existence
runtime_log_manifest.json profile compatibility checks
runtime artifact destination, byte count, and sha256 checks
tracking_source_profile provenance checks
tracking_source_profile to state_source_profile / height_source_profile / localization_eval_profile compatibility checks
tracking.csv column and row checks
metrics.json required metric and unit checks
threshold_report.json run_id and accepted-field checks
review.md nonempty and forbidden-claim checks
screenshots/ and logs/ nonempty usable-file checks
```

The metric threshold gate adds:

```text
evaluation_profile to threshold profile lookup
required metric threshold coverage checks
metric unit and numeric value checks
max/min threshold pass/fail decision
accepted/rejected report for review
```

If validation fails, do not run the experiment as a formal evidence run.
If preflight fails, do not start ROS/Gazebo/PX4 for that ExperimentProfile.
If run evidence validation fails, do not use that run for review, comparison,
leaderboards, or report conclusions.

Generated skeletons are static review artifacts. They are not runtime evidence
until a real run fills the placeholders and attaches logs, metrics, screenshots,
and review notes.

The regression tests include negative cases for missing jerk/snap, output
interface mismatch, FAST-LIO eval-only misuse, Gazebo truth debug misuse,
Swarm namespace isolation, UE display bridge mismatch, trajectory contract
drift, missing run metrics, and forbidden review claims.

`state_source_profile` is the controller state source. `localization_eval_profile`
is optional and is only for parallel localization metrics, such as FAST-LIO
independent ATE/RPE review. A FAST-LIO eval-only profile can appear as
`localization_eval_profile`; the same id must still be rejected if selected as
`state_source_profile`.
