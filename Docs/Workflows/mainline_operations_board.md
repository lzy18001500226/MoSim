# Mainline Operations Board

> Current task selector for MoSim. Keep this file short: it records only the
> active work, the next decision, and blockers. It is not a history ledger or
> a result archive.

Status: P0a repaired the shared velocity-estimation and collective-thrust unit
boundary; P0b then passed Official PID and four shared Runner 50 s regressions
before the later reference-velocity/reference-acceleration contract repair.
Phase 1 completed its user-approved frozen 46-route matrix on 2026-07-27 CST.
The pre-P0a matrix and the six-candidate recovery both remain historical
trace-back only after the forward-reference repair. The three review-only
profiles `pid_awff_linear_eso`, `smc_boundary_layer`, and `nmpc_outer` are
Tier1-only; the Tier2 whole-aircraft population is 45 routes. Official PID has
returned to its native continuous `RotorCommandRunner` boundary; its nominal
50 s `ClimbPath` passed with RMSE `0.1729701479 m` and terminal error
`0.0065067004 m`. Six Official PID seven-scenario records are valid. The
motor-efficiency-fault 50 s record remains invalid: a bounded native diagnostic
verified the configured injection and showed error above 5 m at 16.44 s and
35.2414 m at 16.6 s. Its evidence is
`Results/control_platform/seven_scenario_ab/official_pid/motor_efficiency_fault/`.
Do not change the baseline, fault magnitude, or Plant to mask this failure.

Catalog vocabulary: 48 active entries consist of 47 MWORKS Control Profiles
(46 existing routes plus planned `pid_awff_linear_eso`) and the `px4ctrl`
engineering/deployment baseline. The five named whole-aircraft Profiles belong
to the PID or optimization/predictive family; `mu_synthesis` and `neural_smc`
remain historical 67-route trace-back records only. This vocabulary changes no
historical result or current runtime state.

## 0. Task Authority and Evidence Snapshot

This board is the sole selector of the current task. `PROGRESS.md` is only a
dated snapshot and must not select or supersede current work. The detailed G6
execution contract is `Docs/Workflows/g6_controller_experiment_execution.md`;
`Docs/Workflows/controller_evidence_closeout.md` defines the G1-G7 completion
contract. Neither creates another task line or gate meaning.

## 1. Current Action

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

### Official PID Native-Continuous Motor-Fault Review Decision Required

The native-continuous Official PID is nominally valid and has six valid
seven-scenario records. The configured 50 percent rotor-1 loss at 15 s is
correctly wired, but the unchanged baseline becomes unbounded after the fault;
the 50 s solver call cannot produce a valid full trace. The bounded diagnostic
at `Results/control_platform/seven_scenario_ab/official_pid/motor_efficiency_fault/diagnostic_stop_16_6/`
proves that this is not an MCP timeout or an injection error. The next
executable action needs an explicit decision: retain it as a truthful failed
baseline case, or authorize a different fault-tolerant controller/allocator or
fault specification. Do not continue G3 or seven-scenario reruns on this line
until that decision is made.

### G3 ClimbPath Failure Repair - In Progress

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

Acceptance is 48/48 effective routes with a completed 50 s result and terminal
`position_error_norm < 5 m`. G3 does not authorize seven-scenario runs,
gain-performance optimization, code export, Gazebo/ROS work, G7, or R1. On
completion, update the G3 aggregate index, commit and push only task-owned
sources/scripts/evidence indexes, send one Chinese before/after review email,
and wait for review.

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
  px4ctrl / RViz` lane. Do not substitute ROS2, x500, fake clouds, Gazebo truth
  as controller state, QGC, or UE for runtime evidence.
- Execute serially: GPS/EKF boot-only state chain; single-aircraft
  takeoff-hover-land; FUEL point cloud/grid/rosbag replay; three-aircraft
  fixed-formation baseline; then native Diff-Swarm avoidance.
- GPS/EKF boot-only passed at
  `Results/sunray_ros1/sunray_ros1_gps_state_chain_20260729_007/`: the nested
  project-local GPS model, frozen boot parameters, MAVROS global/home/local
  state, Gazebo truth agreement, PX4 ULog fields, and no-flight contract all
  passed after a 90.11 s observed capture. The shorter `_006` capture remains
  diagnostic trace-back only.
- P3 has an explicit quality-blocked result at
  `Results/sunray_ros1/p3_runtime_closeout_20260730/P3_RUNTIME_STATUS.json`.
  Its functional subgate is complete: the project-local px4ctrl chain armed,
  took off, hovered, landed, and disarmed, while the bounded rotor-1
  efficiency `0.85` request was physically acknowledged by the Gazebo actuator
  plugin without controller override. Both P3 captures exceed the frozen
  hover/local-state quality thresholds, so this is not controller-performance
  or fault-tolerance acceptance.
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
- The current executable gate is P5: run the project-local, single-aircraft
  native Diff baseline through its smallest bounded source/build/preflight
  check, then decide whether a live trajectory gate is safe to open. Do not
  start P6 fixed formation or Diff-Swarm until the P5 terminal record exists.
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

G3 is active against the frozen 48-route denominator. The completed G1-0
reconciliation remains the authority for those 48 entries; do not infer an
additional runnable route from a historical `adapter_missing` row or the
planned ESO profile. Read
`Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_STATUS.json`
for the current effective pass/fail count; G2 records remain trace-back
evidence only.

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
- G3 may repair and rerun only the G2 failure set under its separate evidence
  root. Do not enter broader seven-scenario A/B, ESO ablation, code export,
  ROS1 runtime validation, G7, or R1 until G3 is complete and the user supplies
  a new instruction.

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
