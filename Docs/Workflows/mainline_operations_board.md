# Mainline Operations Board

> Current task selector for MoSim. Keep this file short: it records only the
> active work, the next decision, and blockers. It is not a history ledger or
> a result archive.

Status: P0a repaired the shared velocity-estimation and collective-thrust unit
boundary; P0b then passed Official PID and four shared Runner 50 s regressions
before the later reference-velocity/reference-acceleration contract repair.
Phase 1 completed its user-approved frozen 46-route matrix on 2026-07-27 CST.
The pre-P0a matrix and the six-candidate recovery both remain historical
trace-back only after the forward-reference repair. The current report-run
audit retains a fixed 48-entry catalog denominator. Its current status
reconciliation is
`Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_CATALOG_48_CURRENT_STATUS.json`:
28 passes, 16 completed failures, and four entries without a FormalRunner
record. It incorporates the post-freeze records for `pid_awff_linear_eso`
(50 s completed but failed the 5 m gate at `3412.359226529184 m`),
`smc_boundary_layer` (50 s completed but failed at `15.029940929898276 m`),
and `nmpc_outer` (50 s passed at `0.142974149482056 m`). Those three records
are not extra controllers and do not change the denominator. The historical
G3 execution matrix remains separately preserved. The earlier v1
seven-scenario evidence remains historical trace-back only. The current
two-controller v2 A/B set is isolated at
`Results/control_platform/seven_scenario_ab_v2/`: 12 of 14 records are valid,
while both 50 percent rotor-1 fault cases remain preserved invalid negative
evidence. Do not change the baseline, fault magnitude, or Plant to mask either
failure.

Catalog vocabulary: 48 active entries consist of 47 MWORKS Control Profiles
(46 existing routes plus planned `pid_awff_linear_eso`) and the `px4ctrl`
engineering/deployment baseline. The five named whole-aircraft Profiles belong
to the PID or optimization/predictive family; `mu_synthesis` and `neural_smc`
remain historical 67-route trace-back records only. This vocabulary changes no
historical result or current runtime state.

For report screenshots, do not use the catalog denominator as a whole-aircraft
simulation completion claim. The 48-entry run-evidence audit is at
`Docs/报告/审计/控制器原生截图归位/FORMAL_RUN_SCREENSHOT_COVERAGE_20260731.md`.
It distinguishes source result captures, whole-aircraft FormalRunner records,
and report-directory assets; all 48 report structure images are now present,
while current-source-bound per-controller result-image materialization remains
separate work.

## 0. Task Authority and Evidence Snapshot

This board is the sole selector of the current task. `PROGRESS.md` is only a
dated snapshot and must not select or supersede current work. The detailed G6
execution contract is `Docs/Workflows/g6_controller_experiment_execution.md`;
`Docs/Workflows/controller_evidence_closeout.md` defines the G1-G7 completion
contract. Neither creates another task line or gate meaning.

### User-Assigned Thread Boundary (2026-07-30 CST)

```text
This coordinating thread:
  MWORKS controller/model/evidence work
  -> later MoSim Studio APP work

Separate QGC/Gazebo conversation:
  QGC and ROS1/Gazebo/PX4/MAVROS runtime work
```

The separate conversation owns live runtime execution, Factory-map work,
runtime scripts, PX4/EKF/sensor configuration, and QGC operations. This thread
may prepare a factual handoff from completed `Results/sunray_ros1/` evidence,
but must not run, change, or diagnose that lane. Direct user ownership takes
precedence over historical runtime status below.

## 1. Current Action

### Seven-Scenario v2 Official PID / PX4CTRL A/B - Completed, Awaiting Review

The direct user-authorized v2 evidence task is complete. The frozen contract
is `Config/control_platform/seven_scenario_injection_contract_v2.json`; the
seven Profile definitions are
`Config/control_platform/seven_scenario_experiment_profiles_v2.json`. The
v2 set deliberately keeps `ClimbPath` as the separate all-controller
minimum-closure screen and uses `Figure8` for wind and motor-fault tracking,
and `SpiralAscent` for the 20 percent physical mass/inertia mismatch.

The 14-row matrix is
`Results/control_platform/seven_scenario_ab_v2/SCENARIO_RMSE_MATRIX.pending_syslab.json`.
Twelve records are valid and contain the bound Profile/contract hashes,
`RUN_CONFIG.json`, `RUN_RECORD.json`, raw CSV, metrics, native `Result.msr`,
and native result-window capture. The direct injection checks pass for both
wind records, both parameter-mismatch records, and the PX4CTRL motor-fault
record. The PX4CTRL fault run reaches only 17.06 s before exceeding the 5 m
validity gate (`15.659533 m` terminal error), so it is retained as invalid
negative evidence. The Official PID primary fault run does not return inside
the 120 s MCP bound; its separate 0-16.6 s native diagnostic verifies the
configured rotor-1 1.0-to-0.5 transition at 15 s and records error above 5 m
at 16.44 s, reaching `13.101713 m` at 16.6 s. That diagnostic is supplementary
only and does not relabel the incomplete 50 s primary record as valid.

The v1 ClimbPath disturbance/fault records remain intact and are not merged
into this v2 matrix. This completed gate by itself does not authorize new
controller experiments, gain tuning, or Gazebo/ROS/QGC runtime action. The
later direct P0 report/manual/codegen-delivery authorization is tracked below
and is document/build work only; it does not alter this frozen matrix.

### P0 Report / Manual / Delivery Evidence Convergence - In Progress

Direct user authorization on 2026-07-31 CST permits only the evidence-driven
rewrite of `Docs/报告/` and the named documentation locations, plus the
px4ctrl C delivery material under `src/control/codegen/px4ctrl/` and root
`RELEASE_CHECKLIST.md`. The source of truth is
`Docs/Design/报告手册交付证据总账_P0_20260731.md`.

This task does not modify `Models/`, `Config/`, or existing `Results/`, does
not start simulations, and does not exercise the separately owned
Gazebo/PX4/ROS/QGC runtime lane. It must preserve negative evidence, verify
paths/hashes/builds, and publish only task-owned documentation and C delivery
files.

### MWORKS PX4CTRL Three-UAV Figure-8 - Completed, Awaiting Next Instruction

The bounded direct user task of 2026-07-30 CST is complete. The nominal
three-UAV PX4CTRL virtual-structure triangle used three current
`Sunray150Assembly` instances, three `Px4CtrlAttitudeThrustAdapter` instances,
and three `OfflineAttitudeRateAllocator` instances; it did not reuse the
historical LinearMPC/QuadChassis prototype as PX4CTRL evidence. Native
`CheckModel` passed, and staged 5 s/10 s/50 s MWORKS simulations completed.
The 50 s record has 5001 finite samples; each UAV has position RMSE about
`0.081432 m`, terminal position error about `0.041230 m`, and the minimum
inter-UAV distance is `2.078461 m`. The user accepted the native MWORKS
three-aircraft figure-eight replay. Raw CSV, native `Result.msr`, metrics,
screenshot, `RUN_CONFIG.json`, and `RUN_RECORD.json` are under
`Results/control_platform/px4ctrl_three_uav_figure8_v1/`.

This is only nominal MWORKS virtual-structure closure. It does not claim
obstacle avoidance, distributed swarm planning, inter-UAV collision avoidance,
or Gazebo/PX4/ROS/QGC/APP runtime validation. Stop here and await a new user
instruction; do not infer multi-UAV seven-scenario, avoidance, Gazebo/QGC,
APP, G3 repair, gain tuning, export, or runtime work from this completed gate.

### px4ctrl Graphical Completion - Completed

The bounded correction completed before G1 review resumed. The native
`PX4CTRL_Original_OuterLoop_Graphical_Sysblock` diagram is the reviewable
Sysblock artifact; the separately checked equation bridge remains only for the
whole-aircraft runner because the current MWORKS compiler cannot embed its
multi-operator Sysblock topology in a Modelica composite. `Px4CtrlFormalRunner`
then replayed `ClimbPath` for 50 s: `CheckModel` passed, 5001 samples were
finite, `position_rmse_m=0.276705`, and terminal position error was `0.002734`
m. Native graphical/model/result-window captures, raw CSV, metrics, MCP log,
and session-cleanup record are at
`Results/control_platform/px4ctrl_graphical_completion_20260728/`. This is
MWORKS equation-bridge closure evidence only, not authorization or proof for
G2, seven-scenario work, export, Gazebo, ROS, or runtime validation.

### Controller Evidence G1 - Review Required

The user authorized the 48-controller MWORKS closed-loop evidence line on
2026-07-28 CST. G0 is complete: `Px4CtrlFormalRunner` passed the common 50 s
`ClimbPath` baseline with 5001 samples, no NaN, `position_rmse_m=0.276705`,
and `terminal_position_error_norm=0.002734`. Its native `CheckModel` capture
shows 0 errors and 0 warnings. Current evidence is
`Results/control_platform/px4ctrl_baseline_verification/`.

G1-0 reconciled the catalog and route denominator. G1 Batch 1 added the
`LQI`, `LQG`, `H2 state feedback`, `H-infinity hover wrench`,
`pole-placement/Luenberger`, `MRAC`, and `NDI` routes as thin bridge/Adapter
pairs. Native `CheckModel` passed for all 15 new/support classes, with no
source drift; the compact result record is
`Results/control_platform/g1_batch1_checkmodel_20260728/CHECK_MODEL_RESULTS.json`.
This proves model integrity only, not closed-loop behavior or controller
performance.

G1 Batch 2 added `backstepping`, `adaptive backstepping`, `feedback
linearization`, `passivity-based control`, and `FOPID` as thin bridge/Adapter
pairs. Native `CheckModel` passed for all 10 classes without source drift; the
compact result record is
`Results/control_platform/g1_batch2_checkmodel_20260728/CHECK_MODEL_RESULTS.json`.
This proves model integrity only, not closed-loop behavior or controller
performance.

G1 Batch 3 added `integral SMC`, `terminal SMC`, `nonsingular terminal SMC`,
`adaptive SMC`, and `fuzzy SMC` as thin bridge/Adapter pairs. Native
`CheckModel` passed for all 10 classes without source drift; the compact result
record is
`Results/control_platform/g1_batch3_checkmodel_20260728/CHECK_MODEL_RESULTS.json`.
This proves model integrity only, not closed-loop behavior or controller
performance.

G1 Batch 4 added `robust MPC`, `adaptive MPC`, `tube MPC`, explicit
gain-scheduled MPC, `iLQR`, and `MPPI` through one shared equation kernel, six
named Bridges, and six thin ATTITUDE_THRUST Adapters. Native `CheckModel`
passed all 13 classes without source drift; the compact result record is
`Results/control_platform/g1_batch4_checkmodel_20260728/CHECK_MODEL_RESULTS.json`.
This proves model integrity only, not closed-loop behavior or controller
performance.

G1 Batch 5 added `SE3 Basic`, `DFBC Basic`, `DFBC SmoothRobust` attitude,
`DFBC SmoothRobust` body-rate, and `DFBC HighOrder` body-rate routes as five
named Bridges and five thin Adapters. The two body-rate routes use the
BODY_RATE_THRUST boundary; the graphical source models remain unchanged.
Native `CheckModel` passed all 10 classes without source drift; the compact
result record is
`Results/control_platform/g1_batch5_checkmodel_20260728/CHECK_MODEL_RESULTS.json`.
This proves model integrity only, not closed-loop behavior or controller
performance.

G1 Batch 6 added `GainScheduled PID`, `Fuzzy PID`, `Neural PID`, and `RL GainScheduler`
as four Bridges and four thin ATTITUDE_THRUST Adapters. The first three compose
their existing PID subblock through the complete cascade boundary rather than
claiming a standalone plant. Native `CheckModel` passed all eight classes without
source drift; the compact result record is
`Results/control_platform/g1_batch6_checkmodel_20260728/CHECK_MODEL_RESULTS.json`.
This completes G1 structural validation only; it is not a closed-loop run or a
controller-performance claim.

Current action:

### Historical v1 Official PID Native-Continuous Motor-Fault Record - Retained

The native-continuous Official PID is nominally valid and has six valid v1
seven-scenario records. The configured 50 percent rotor-1 loss at 15 s is
correctly wired, but the unchanged baseline becomes unbounded after the fault;
the 50 s solver call cannot produce a valid full trace. The bounded diagnostic
at `Results/control_platform/seven_scenario_ab/official_pid/motor_efficiency_fault/diagnostic_stop_16_6/`
proves that this is not an MCP timeout or an injection error. This is retained
as historical v1 negative evidence, not the current task selector; use the
v2 entry above for the active review packet.

### G3 ClimbPath Status - Historical Execution and Current Catalog Reconciliation

The direct P0 documentation task does not resume G3 execution. Preserve the
existing repair records. The immutable historical execution authority is
`Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_STATUS.json`:
G2 has 17/48 frozen passes; the historical G3 runner namespace has 28/48
effective passes and 20/48 effective failures. The 20 failures are nine
terminal-position-error violations, eight simulation timeouts, two simulation
API failures, and one CheckModel failure.

For the active fixed catalog terminology, use
`Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_CATALOG_48_CURRENT_STATUS.json`.
It maps 33 exact historical identities plus eight aliases, accounts for the
three post-freeze FormalRunner records, and leaves four catalog entries as
`not_run` because no FormalRunner exists. Its current result is 28/48 passes,
16/48 completed failures, and 4/48 not-run entries; `completed=false`. The
seven historical G3-only execution rows remain preserved in the artifact but
are not silently substituted for catalog entries.

All 48 public
`Runners.Formal.*` entries received one nominal 50 s `ClimbPath` attempt with
no scenario injection, gain tuning, model edit, or seven-scenario work. The
frozen matrix and terminal records are at
`Results/control_platform/phase2_full_48_climbpath/`: 17 routes passed and 31
failed. The failure record is explicit: 10 terminal-error violations, four
simulation-API failures, nine MCP timeouts, and eight dedicated
Sysplorer-session startup failures.

The user subsequently authorized G3. Keep the G2 directory immutable and write
all retry records to
`Results/control_platform/phase2_full_48_climbpath/g3_repair/`, preserving the
G2 row, source bindings, and failure reason alongside each new attempt. First
distinguish transient execution-chain failures from model failures. For a proven
model defect, limit changes to interface wiring, reference/measurement use,
coordinate signs, equation-bridge equations, or allocation units; do not tune
for performance. Each source change requires native `CheckModel` and the same
single-route 50 s `ClimbPath` replay before the next repair.

The historical G3 target remains 48/48 effective routes with a completed 50 s
result and terminal `position_error_norm < 5 m`. It is not an acceptance claim
for the present 28/48 state. No G3 rerun, gain-performance optimization, or
Gazebo/ROS work is authorized by the P0 documentation task.

### User-Authorized Operator Surface - Separate Support Lane

The user authorized the long-running `MoSim Studio + QGC Factory 2D operation
surface` task on 2026-07-28 CST. It is a support-layer task and does not change
the controller evidence gate below:

- rename the visible native APP identity to `MoSim Studio` without opaque
  MWORKS execution or export automation;
- replace QGC embedded UE and the minimap with a registry-backed Factory 2D
  Fly View and Plan View, preserving native QGC flight functions;
- show only authoritative live or rosbag-derived vehicle, waypoint, actual
  path, future path, and task-boundary data; gate native mission publication on
  a geodetic round-trip check;
- let QGC select published compatible profiles before prepare/arm and issue
  discrete pending/apply/recover fault requests while retaining visible terminal
  logs; no new mandatory Orchestrator dependency;
- keep UE independent and repair its pointer-release behavior separately.

This task may perform source/UI/build checks, but it must not start MWORKS,
Gazebo, ROS, PX4, MAVROS, QGC, UE or RViz until its relevant execution gate is
opened. It must not claim controller, planner or runtime success from UI work.

### User-Authorized ROS1/Gazebo Reproducibility Closure - Active Support Lane

On 2026-07-29 CST, the user authorized a separate runtime closure whose goal
is that a reviewer can obtain the project source, configure the documented
Ubuntu-20.04 environment, and reproduce the declared Gazebo evidence without
Codex assistance. This does not supersede or broaden MWORKS G3.

- Preserve the declared `ROS1 Noetic / Sunray / Gazebo Classic / PX4 / MAVROS /
  px4ctrl / RViz` lane. Do not substitute ROS2, x500, fake clouds, direct
  Gazebo-truth controller feedback, QGC, or UE for runtime evidence.
- Execute serially: source-local FAST-LIO/external-vision single-aircraft
  takeoff-hover-land; FUEL point cloud/grid/rosbag replay; three-aircraft
  fixed-formation baseline; then native Diff-Swarm avoidance. The nested
  GPS/EKF boot-only gate is a separate no-flight compatibility diagnostic.
- GPS/EKF boot-only passed at
  `Results/sunray_ros1/sunray_ros1_gps_state_chain_20260729_007/`: the nested
  project-local GPS model, frozen boot parameters, MAVROS global/home/local
  state, Gazebo truth agreement, PX4 ULog fields, and no-flight contract all
  passed after a 90.11 s observed capture. The shorter `_006` capture remains
  diagnostic trace-back only.
- The prior P3 record at
  `Results/sunray_ros1/p3_runtime_closeout_20260730/P3_RUNTIME_STATUS.json`
  used the nested GPS/barometer estimator branch. Keep it as a diagnostic
  lifecycle and actuator-ack trace only; it is not an accepted hover, state
  quality, controller-performance, or fault-tolerance result. The source-local
  FAST-LIO/external-vision rerun at
  `Results/sunray_ros1/sunray_ros1_fastlio_hover_source_local_20260730_004/`
  has now reproduced the state chain and full arm/takeoff/hover/land/disarm
  lifecycle from `src/`: GPS and barometer are disabled, PX4 accepts external
  vision, and px4ctrl consumes MAVROS local odometry. Its truth/local
  consistency gate passes in the steady-hover window, but the frozen XY hover
  tracking gate is still blocked at 0.03465 m RMSE and 0.05859 m peak against
  0.02 m and 0.05 m limits. This is a tracking-quality blocker, not a source
  migration or GPS/barometer-state failure.
- P4 Factory FUEL historical display replay completed at
  `Results/sunray_ros1/sunray_ros1_p4_factory_fuel_replay_20260730_0945/`.
  The exact source bag, Gazebo-world truth display stream, isolated RViz topic
  replay, Factory 2D operator-map replay, and one-way UE receiver are bound by
  `P4_DISPLAY_REPLAY_STATUS.json`. Its final state is
  `completed_with_rviz_window_capture_limitation`: WSLg RAIL prevented a
  pixel-level RViz background capture, while the recorded point cloud,
  occupancy, and truth-path subscriptions all completed. P4 remains historical
  display/reproducibility evidence and cannot rehabilitate the P3 quality
  blocker or be cited as a live FUEL, PX4, MAVROS, controller, planner, fault,
  QGC-command, or UE-control success.
- The current executable gate is bounded attribution of the source-local P3
  horizontal hover tracking error. Do not start P5 native Diff, P6 fixed
  formation, or Diff-Swarm until the P3 terminal record passes its frozen
  hover-quality contract or the user explicitly accepts the blocked baseline.
- Each terminal subgate records a bounded result directory and triggers one
  concise Chinese email. Every successful path must later receive a cold-start,
  stop, recording, replay, and troubleshooting check plus a path-limited Git
  publication check.

### Historical Seven-Scenario Pre-Simulation Gate

- Workflow: `Docs/Workflows/run_simulation.md`.
- Frozen matrix driver: `Scripts/mworks/run_phase1_minimum_closure.py`.
- Contract test: `Scripts/tests/test_phase1_minimum_closure.py`.
- Recovery evidence root:
  `Results/control_platform/champion_candidate_recovery_20260727/`.
- Pre-repair historical six-candidate recovery trace:
  `Results/control_platform/champion_candidate_recovery_20260727/CHAMPION_CANDIDATE_RMSE_RANKING.json`
  and `.csv`. The six candidates in that historical recovery passed a plant-coupled 50 s `ClimbPath`
  run with finite terminal error below 5 m and recorded position RMSE before
  the shared forward-reference repair. Do not rank current-source candidates
  from those values; replay the common 50 s run first.
- Seven trajectory definitions are present under
  `Models/MoSimQuadrotorModel/Guidance/Trajectories/`: `HoverHold`,
  `StepResponse`, `Figure8`, `SpiralAscent`, `WindDisturbance`,
  `ParameterMismatch`, and `MotorFault`. The source repair carries
  position, velocity, and acceleration references through the four shared
  controller contracts and the six champion Formal Runners. The scenario
  injection parameters are bound through the Plant and all four shared Runner
  boundaries.
- `Results/control_platform/seven_scenario_preflight_20260727/` records
  static contract validation, a native MWORKS `CheckModel` pass for eight
  trajectories, four shared Runners, Official PID, and six champion Formal
  Runners, raw MCP JSONL, clean GUI sentinels before and after, and a
  DPI-aware native-aspect capture. It contains no solver result or simulation
  performance claim.
- `Config/control_platform/seven_scenario_injection_contract.json` now fixes
  the offline scenario semantics and required binding path: persistent 0.25 N
  world-frame lateral force, plant-only +20 percent mass/inertia mismatch, and
  rotor 1 transition to 50 percent effectiveness at 15 s. It additionally
  requires a 0.01 s external hold harness around Official PID and defines the
  step-response metric semantics. The Plant, Runner, and metric implementation
  are complete and self-checked; no scenario simulation has run.
- The recovery ranking and P0b runner results are pre-repair records, not
  current-source performance evidence. The `CheckModel` record proves model
  integrity only, not RMSE improvement, seven-scenario A/B, code-generation,
  Gazebo, ROS, or flight-runtime behavior.
- The prior wait condition was superseded only for G0-G3 above. This record
  remains static preflight evidence and does not authorize seven-scenario A/B,
  export, runtime validation, G7, or R1.

The approved atomic model-library migration is statically complete. The only
formal load root is `Models/MoSimQuadrotorModel/package.mo`; retired roots and
active old-path references are rejected by
`consolidate_mosimquad_model_root.py --check`.

The pre-P0a 46-route evidence record is frozen at
`Results/model_library_refactor/controller_route_execution_current/`. It proves
41 controller-only internal responses and five fixed whole-aircraft minimum
closures, not family champion selection, seven-scenario comparison, code
generation, or flight-runtime behavior. It was superseded for new experiment
acceptance because P0a changed the shared Runner interface/units.

The P0b result root is
`Results/control_platform/p0b_interface_regression_20260727/`: Official PID and
ATTITUDE_THRUST, BODY_RATE_THRUST, WRENCH, and ROTOR_COMMAND all completed the
same 50 s ClimbPath regression with finite results, native result-window
captures, and verified dedicated-session closure. Official PID terminal position
error is 0.00651 m.

Phase 1 is complete at
`Results/control_platform/phase1_minimum_closure/`. All 46 frozen rows have a
terminal `RUN_RECORD.json` for the sole 50 s `ClimbPath` trajectory: three
passed the finite terminal `position_error_norm < 5 m` gate, while 34 rows are
truthfully classified `adapter_missing`, six `model_check_failed`, and three
`terminal_position_error_exceeds_limit`. The concurrent promoted CFunction
source-import consistency check passes. This is a readiness screen only, not
family-champion selection, seven-scenario comparison, code generation, or
runtime validation.

The completed user-approved recovery was limited to the historical six-candidate
row set named above. Phase 1's original failures remain archived by the rerun
procedure; each successful rerun proves only that candidate's repaired minimum
whole-aircraft `ClimbPath` closure and supplies trace-back RMSE, not a current
seven-family ranking.

## 2. Current Engineering Boundaries

```text
Formal MWORKS package root:
  Models/MoSimQuadrotorModel/package.mo

Current runtime evidence lane:
  Ubuntu-20.04 / ROS1 Noetic / Sunray / Gazebo Classic
  / PX4 / MAVROS / px4ctrl / RViz

Display and operator surfaces:
  UE, QGC, Flight Console and Model Studio are support layers.
  They do not replace MWORKS, Gazebo, PX4, MAVROS, logs, or metrics.
```

The current competition architecture is owned by `Docs/Design/架构.md`. The
future CoSim three-phase platform roadmap is owned by
`Docs/CoSim/research/raw/CoSim设计.md`; do not rewrite it as a statement of
current completion.

## 3. Next Engineering Selection

The active bounded action is P0 report/manual/codegen-delivery evidence
convergence. It uses the fixed 48-route denominator and
`Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_CATALOG_48_CURRENT_STATUS.json`
for current catalog state, with `G3_STATUS.json` retained as the immutable
historical execution record. Do not infer an additional runnable route from a
historical `adapter_missing` row or the planned ESO profile. G2 remains
trace-back evidence; no live rerun is part of P0.

Before a live MWORKS, Gazebo, ROS, UE, or desktop action, load the relevant
topic workflow and declare the evidence path under `Results/`.

## 4. Stopping And Handoff Conditions

For the historical bounded seven-scenario A/B gate:

- Retain valid and invalid records for all 14 cases; no failed run may silently
  abort or be replaced by an unrecorded rerun.
- Its stop condition was satisfied before the later G2 authorization; it does
  not authorize any new execution by itself.

For the frozen G2 full-route gate:

- Preserve all 48 terminal records, including every failure, as the current
  screening evidence. Do not replace a timeout or session-start failure with an
  unrecorded rerun.
- It is not overwritten by G3 retries.

For the later G0-G3 controller line:

- Stop at every batch boundary after its native `CheckModel`, exact-path
  commit, push, and email report; do not allow one failed route to silently
  change the next batch's interface contract.
- G0 and G2 use only the common 50 s `ClimbPath` and the terminal-error gate
  of less than 5 m. A completed solver call with a divergent signal is a fail.
- The old P0b and pre-repair six-candidate RMSE values are trace-back evidence,
  not current-source ranking data.
- A future G3 repair may rerun only the G2 failure set under its separate
  evidence root after a new direct user instruction. The current P0 task
  permits documentation and px4ctrl C build verification only; it does not
  permit broader experiment or runtime work.

## 5. Board Update Rule

Update this board only when one of these changes:

- current task or next executable gate;
- declared architecture/runtime authority;
- terminal blocker and its required resolution;
- accepted evidence pointer.

Put detailed run history in `Results/`, stable design in `Docs/Design/`, and
historical plans in `Docs/Cache/`. Do not append progress narration here.

## 6. Historical Board

The pre-cleanup board, including prior controller, Factory, FUEL, and
closeout history, is preserved at:

```text
Docs/Cache/workflow_history/mainline_operations_board_20260726_pre_cleanup.md
```
