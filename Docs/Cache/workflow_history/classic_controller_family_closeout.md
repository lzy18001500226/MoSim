# Classic Controller Family Closeout (Historical Snapshot)

> Archived from `Docs/Workflows/` on 2026-07-27. It remains a trace-back
> reference for the quality contract, not an active execution workflow.

Status: frozen historical evidence snapshot, 2026-07-18 CST.
>
> This file records the 2026-07-17/18 closeout only. It does not authorize a current model entry,
> a G5 graphical layout result, a current MWORKS run, a report screenshot, a whole-aircraft claim,
> or the retirement of a legacy model root. Current execution is owned by
> `Docs/Workflows/controller_evidence_closeout.md` and its D2 harness map.

## 1. Historical Scope

This workflow closes a bounded canonical controller set. It does not interpret
"all controllers" as every named variant in the literature. A controller is
covered only when its algorithm identity, architecture layer, implementation,
MWORKS evidence, generated-code evidence and Gazebo claim are explicit.

The canonical additions are:

```text
pole_placement_luenberger
mrac
ndi
fopid
h2_state_feedback
```

Historical executable state, 2026-07-17 CST:

- all five source identity/lifecycle gates pass;
- all five real graphical Sysblock MIL fixtures pass `CheckModel` and live
  simulation; the shared bridge diagram and Sysplorer evidence are archived
  under `Results/control_platform/classic_controller_closeout_20260717/mworks/`;
- official `ModelingPy.GenerateModelCode` succeeded and archived 12 generated
  files in the declared code-generation directory;
- generated-C SIL passed 700/700 scalar comparisons with maximum absolute
  difference `0.0` at tolerance `1e-12`;
- the `classic_controller_attitude_thrust` px4ctrl backend now builds in the
  Ubuntu-20.04 catkin workspace; build-only provenance confirms the selected
  CMake definition/directory, generated bundle SHA-256
  `0f44c05a4d36ed4a2040989ff48a47b9b1033f24ced152da1c5eb38428da7772`,
  executable SHA-256
  `4c9bb00dc6e124550f60cb56726bd3eef1d7ce2ccd79cab1f980e1c263f666ac`
  and the `MosimClassicStepScalar` binary symbol;
- the generated backend emitted same-run controller id/name, model symbol,
  source hash and executable provenance for all five controller profiles;
- all five completed a real takeoff attempt and the accepted run completed
  landing/disarm; MRAC and NDI passed the unchanged takeoff-hover-land gate,
  while Pole Placement + Luenberger, FOPID and H2 remained blocked by the
  unchanged vertical hover thresholds;
- fresh figure-eight runs were executed for the two hover-pass profiles. Both
  retained valid runtime provenance and landed/disarmed, but MRAC exceeded the
  XYZ RMSE/P95 limits and NDI exceeded the pre-trajectory hover XY RMSE and
  trajectory XYZ RMSE limits;
- the final 67-row authority is `closed_with_blockers`: 27 accepted, 33
  executed-blocked and 7 not-run. All five additions remain
  `implemented/selectable=false`; runtime selection exists for evidence and
  diagnosis, but no failed final row is promoted to a selectable accepted
  controller.

The historical machine-readable authorities are:

```text
Results/control_platform/classic_controller_closeout_20260717/mworks/MWORKS_MIL_MANIFEST.json
Results/control_platform/classic_controller_closeout_20260717/mworks/MWORKS_CODEGEN_MANIFEST.json
Results/control_platform/classic_controller_closeout_20260717/mworks/sil/CLASSIC_CONTROLLER_GENERATED_SIL.json
Results/control_platform/classic_controller_closeout_20260717/px4ctrl_build/PX4CTRL_BACKEND_ENSURE.json
Results/control_platform/classic_controller_closeout_20260717/px4ctrl_build/CLASSIC_CONTROLLER_BUILD_PROVENANCE.json
Results/control_platform/classic_controller_closeout_20260717/CLASSIC_CONTROLLER_FINAL_MATRIX.json
Results/control_platform/classic_controller_closeout_20260717/CLASSIC_CONTROLLER_COMPARISON.csv
Results/control_platform/classic_controller_closeout_20260717/COVERAGE_AUDIT_CURRENT.json
```

Final Gazebo results:

| Controller | Hover result | XY RMSE (m) | Z RMSE (m) | Representative trajectory |
|---|---|---:|---:|---|
| Pole Placement + Luenberger | blocked | 0.016693 | 0.055173 | not run after hover blocker |
| MRAC | passed | 0.014747 | 0.014800 | blocked: XYZ RMSE 0.063493, P95 0.087888 |
| NDI | passed | 0.010331 | 0.014736 | blocked: pre-trajectory hover XY RMSE 0.023158 and XYZ RMSE 0.050397 |
| FOPID | blocked | 0.010483 | 0.030180 | not run after hover blocker |
| H2 state feedback | blocked | 0.013688 | 0.022701 | not run after hover blocker |

The first NDI attempt passed flight metrics but lost its constructor INFO ACK
to redirected stdout buffering. It is retained under
`gazebo/ndi_r1_missing_buffered_ack/`; the runner now starts roslaunch through
`stdbuf -oL -eL`, and the independent NDI rerun passed both flight and same-run
provenance. The first H2 attempt is retained under
`gazebo/h2_state_feedback_r1_px4_startup_blocked/` because PX4 returned startup
code 2 before MAVROS connected. The independent retry entered the controller
gate and supplies the H2 performance result above.

The existing registered controllers omitted from the 2026-07-17 final matrix
must also remain visible. This includes LQR, LQI, H-infinity, mu synthesis,
SO(3), non-adaptive Backstepping, high-order/robust DFBC, DOB/ESO, L1-AWFF and
Neural-SMC entries. A blocked implementation stays blocked; matrix inclusion
does not imply acceptance.

## 2. Algorithm Identity

| Controller | Layer | Minimum identity requirement |
|---|---|---|
| Pole placement + Luenberger | nominal outer loop | declared double-integrator plant, feedback poles, observer poles, persistent observer state |
| MRAC | nominal outer loop | declared reference model, tracking error, adaptive law, projection bounds and persistent adaptive state |
| NDI | nominal outer loop | declared translational model inversion, gravity/drag compensation, bounded virtual acceleration and attitude conversion |
| FOPID | nominal outer loop | declared fractional orders and a fixed-memory or rational approximation whose state is executed, not PID gains under a new name |
| H2 state feedback | nominal outer loop | declared generalized hover plant and frozen H2 gain with synthesis provenance; do not call an arbitrary LQR gain H2 |

The five controllers use the project `ATTITUDE_THRUST` contract. They do not
replace the PX4 attitude/rate inner loop or control allocator.

## 3. Evidence Ladder

Each new controller advances in this order:

```text
registered interface and profile
  -> independent source behavior gate
  -> real graphical Sysblock MIL and check_model
  -> official MWORKS GenerateModelCode
  -> generated-C SIL equivalence
  -> px4ctrl backend build and same-run provenance
  -> Gazebo takeoff-hover-land
  -> representative trajectory for report-selected accepted rows
```

Every level is fail-closed. Static source, an equation bridge, a diagram image,
successful landing, or an older executable cannot substitute for a later
level. Common hover thresholds remain unchanged. Failed and not-run rows stay
in the final matrix with their first blocker.

## 4. Existing Coverage Reconciliation

The machine-readable reconciliation matrix and audit are:

```powershell
python Scripts/control_platform/summarize_classic_controller_closeout.py
python Scripts/control_platform/audit_classic_controller_coverage.py
```

The reconciler preserves the frozen 48-row matrix and appends missing canonical
rows under `Results/control_platform/classic_controller_closeout_20260717/`.
The audit compares that matrix with
`Config/control_platform/control_module_registry.json` and checks unique ids
plus declared evidence paths. It is a coverage checker, not runtime evidence.

The initial audit identified registered controllers that were absent as
independent rows from the 48-row matrix. Existing evidence must be reused only
at its declared tier. In particular:

- Wave A LQR, LQI, SO(3) and Backstepping have MWORKS/codegen/SIL evidence but
  still require individual Gazebo rows.
- H-infinity has bounded hover synthesis/source evidence but no complete
  allocator/adapter/runtime acceptance.
- dynamic mu synthesis is blocked by the installed tool capability and must
  not be represented by constant-matrix mu analysis.
- Neural-SMC has no frozen trained artifact and remains blocked.
- DOB/ESO, L1-AWFF and DFBC variants retain their current bounded claim ceilings.

## 5. Historical Runtime Policy

Gazebo runs are serial and use the current Ubuntu-20.04 ROS1 Sunray lane. Run
only after the MWORKS/codegen/SIL gate for that exact controller passes. The
runtime wrapper must record the selected controller id, generated source hash,
loaded backend hash, pre-takeoff state, takeoff, hover metrics, landing/disarm
and first blocker.

If the official/shared baseline fails before controller selection, preserve a
shared-baseline blocker. Do not classify unexecuted controller rows as failed
controller performance and do not relax the baseline threshold.

## 6. Historical Documentation Updates

Update this workflow after every completed evidence tier. Update
`Docs/Workflows/mainline_operations_board.md` only when the executable state or
next gate changes. The final closeout updates the controller design document,
registry, profile catalog, final matrix, CSV, figures and report claim limits.

This bounded extension is closed. A future tuning task must create versioned
profiles and retain these failed runs; it may not overwrite evidence or relax
the common hover/trajectory thresholds. The remaining 19 canonical rows in the
67-row reconciliation matrix retain their independent existing blockers and
are not silently promoted by this extension.
