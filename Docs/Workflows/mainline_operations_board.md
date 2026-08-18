# Project Status Archive (Former Mainline Operations Board)

> RETIRED ROUTING PATH. This file is not a task selector, current P0, PMO
> queue, owner registry, authorization source, or startup context.

MoSim has no global conversation mainline. Each conversation is independent and
works only from its newest direct user instruction. The historical material
below is retained for status and evidence trace-back because existing reports,
quality checks, and links still reference this compatibility path. It must not
be used to start, continue, hand off, or reprioritize work.

Historical catalog snapshot retained for report/evidence checks:

- `Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_CATALOG_48_CURRENT_STATUS.json`
  records 30 passes, 18 completed failures, and zero `not_run` entries.
- `G3_STATUS.json` is a separate frozen historical snapshot and must not be
  confused with the catalog record.
- Detailed historical controller, runtime, and report notes remain below;
  their dates and task labels do not authorize a new action.

Historical engineering snapshot: P0a repaired the shared velocity-estimation and collective-thrust unit
boundary; P0b then passed Official PID and four shared Runner 50 s regressions
before the later reference-velocity/reference-acceleration contract repair.
Phase 1 completed its user-approved frozen 46-route matrix on 2026-07-27 CST.
The pre-P0a matrix and the six-candidate recovery both remain historical
trace-back only after the forward-reference repair. The current report-run
audit retains a fixed 48-entry catalog denominator. Its current status
reconciliation is
`Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_CATALOG_48_CURRENT_STATUS.json`:
30 passes, 18 completed failures, and zero `not_run` entries. All 48 catalog
entries now have a FormalRunner mapping. The reconciliation incorporates seven
post-freeze catalog records, including `pid_awff_linear_eso` (50 s completed
but failed the 5 m gate at `3412.359226529184 m`), `smc_boundary_layer`
(50 s completed but failed at `15.029940929898276 m`), `nmpc_outer` (50 s
passed at `0.142974149482056 m`), and the four former missing-runner records.
Those records are not extra controllers and do not change the denominator. The
frozen historical G3 execution snapshot remains separately preserved at
`G3_STATUS.json` (28 effective passes, 20 effective failures,
`completed=false`); it is not the current catalog reconciliation. The earlier v1
seven-scenario evidence remains historical trace-back only. The current
two-controller v2 A/B set is isolated at
`Results/control_platform/seven_scenario_ab_v2/`: 12 of 14 records are valid,
while both 50 percent rotor-1 fault cases remain preserved invalid negative
evidence. Do not change the baseline, fault magnitude, or Plant to mask either
failure.

Catalog vocabulary: 48 active entries consist of 47 MWORKS Control Profiles
(46 original routes plus the now materialized `pid_awff_linear_eso` route) and the
`px4ctrl` engineering/deployment baseline. The five named whole-aircraft Profiles belong
to the PID or optimization/predictive family; `mu_synthesis` and `neural_smc`
remain historical 67-route trace-back records only. This vocabulary changes no
historical result or current runtime state.

Latest adaptive_mpc recovery attempt, 2026-08-03 CST: the native failure was
diagnosed as correlated with the `ClimbPath` velocity-reference transition,
and a narrow adapter-local first-order conditioning boundary was staged. The
existing MWORKS GUI sentinel remained clean, but final-source reload timed out
after 300 s in the reusable result-viewer/MCP session. This attempt therefore
does not add a pass, change the 30/48 versus 28/48 distinction, add a current
source-bound result figure, or alter the fixed catalog. Evidence and the next
single reload/CheckModel/50 s gate are recorded at
`Results/mworks_live_gate/failed18_recovery_20260803/adaptive_mpc/ADAPTIVE_MPC_RECOVERY_20260803.json`.

For report screenshots, do not use the catalog denominator as a whole-aircraft
simulation completion claim. The 48-entry run-evidence audit is at
`Docs/报告/审计/控制器原生截图归位/FORMAL_RUN_SCREENSHOT_COVERAGE_20260731.md`.
It distinguishes source result captures, whole-aircraft FormalRunner records,
and report-directory assets; all 48 report structure images are now present,
while current-source-bound per-controller result-image materialization remains
separate work.

## 0. Non-Authority Notice And Historical Evidence Snapshot

This file never selects the current task. `PROGRESS.md`, task IDs, owner labels,
and the historical entries below never select it either. The current
conversation's newest direct user instruction is the only execution authority.
The detailed workflows linked below describe procedures only; they do not
create a task or grant permission.

There is no shared owner-thread boundary in the current operating model. Do not
compare the current conversation with a historical thread ID, and do not start
or resume a task because it appears in this archive.

## 1. Historical Task Records (Read-Only)

Every section below is historical evidence or a former plan. It is not a
current action, next gate, handoff, or authorization. The report, controller,
runtime, and graphical-golden records must be reopened only by a new direct
user request in the conversation that will perform that work.

Latest blocker, 2026-08-04 14:13 CST: the newly authorized read-only
disposable OLE probe opened the golden pilot without touching the authoritative
report or pilot bytes, but Word returned a null `OLEFormat.Object` before
`IDataObject.EnumFormatEtc` or any MathML query could run. The pilot-owned Word
process remained responding after the bounded COM quit, so it must be closed
or recovered manually; do not kill or restart it from automation without fresh
explicit authorization. Do not retry `SetData` or a conversion batch. The next
decision is a user-assisted MathType OLE activation or the documented MathType
UI conversion route on a disposable pilot. Evidence:
`Results/report_word_layout_20260804/mathtype_conversion_pilot/mathtype_mathml_ole_format_probe_20260804.json`.

The authoritative working document is the user's manually formatted
`Docs/报告/MoSim_仿真分析报告.docx`. Do not rebuild or overwrite it as the
first step. Preserve its corrected body text, headings, tables, figures,
captions, and first manually rebuilt MathType equation. Make experiments on a
new copy.

Priority order:

1. Inspect the first corrected equation as the golden layout: a borderless
   1-row/2-column table, editable MathType equation on the left, and a
   chapter-numbered Word field on the right.
2. Replace every remaining native Word display equation with an editable
   MathType equation and a correct equation number while preserving formula
   meaning and surrounding content. Validate counts, object types, field
   results, package integrity, and Word rendering before proposing replacement
   of the authoritative document.
3. Diagnose the duplicate Heading 1 numbering and the resulting `0-` figure/
   table captions. Compare the user-corrected report with the user-manual
   builder before changing field logic.
4. After the submission document is accepted, encode the accepted table style
   and formula layout in the report-specific builder. Table cells must inherit
   the accepted body font at the size measured from the current report, use no
   first-line indent, and use single line spacing. Do not guess a point size
   from prose when the formatted DOCX can be measured directly.

The first acceptance gate is the formula-converted review copy, not a generic
Pandoc refactor. If MathType automation cannot create editable, stable objects
without damaging the document, stop with the exact supported/unsupported split
and the remaining manual workload. The supplied WeChat article is supporting
research only; an inaccessible or unverified page must not override the local
document and OOXML evidence.

### Historical Official PID Single-UAV Graphical Golden Loop Record

Direct user assignment on 2026-08-03 is to establish the formal, expandable,
simulatable MWORKS entry
`MoSimQuadrotorModel.Experiment.Runners.Golden.OfficialPidSingleUavGoldenRunner`.
The design and implementation plan is
`Docs/Design/架构/01_控制器平台/Official_PID_单机黄金图形化闭环重构规划_20260803.md`.
The entry reuses `Sunray150Assembly`, its physical Sensors and visual shell, the
existing `Vehicle.Blocks.Controller.Controller` Official PID core, and an
explicit nominal Battery/ESC/four-rotor command path. The existing
`OfficialPidFormalRunner` and its `OfficialPIDRotorAdapter` remain unchanged.

The static contract and regression evidence are
`Results/mworks_live_gate/official_pid_golden_20260803/OFFICIAL_PID_GOLDEN_STATIC_CHECK.json`.
The existing `MWORKS_MCP` result bundle at
`Results/mworks_live_gate/official_pid_golden_20260803/live_attempt_20260803_1911/`
contains a completed 50 s Golden export, a Formal reference export, and four
graphical screenshots. Its `post_yaw_fix` result is retained as pre-layout
regression evidence; it is not a current-source CheckModel record. After the
graphical layout repair, the current-turn read-only MCP `probe` and the bounded
final-source `CheckModel` both timed out without a model error or an
authorization message. The visible Sysplorer main window remains `教育版`.
Therefore do not claim current-source CheckModel, current-layout screenshot
acceptance, or a new 50 s replay from that historical bundle.
Its next executable gate remains one bounded CheckModel followed by one
independent 50 s `ClimbPath` replay for the Golden entry, but it is not
authorized while report P0 is active.

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

### Historical Broader Report / Manual / Delivery Evidence Scope

The earlier direct user authorization on 2026-07-31 CST permitted only the evidence-driven
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

Historical action record:

### Historical v1 Official PID Native-Continuous Motor-Fault Record - Retained

The native-continuous Official PID is nominally valid and has six valid v1
seven-scenario records. The configured 50 percent rotor-1 loss at 15 s is
correctly wired, but the unchanged baseline becomes unbounded after the fault;
the 50 s solver call cannot produce a valid full trace. The bounded diagnostic
at `Results/control_platform/seven_scenario_ab/official_pid/motor_efficiency_fault/diagnostic_stop_16_6/`
proves that this is not an MCP timeout or an injection error. This is retained
as historical v1 negative evidence. It does not select a task; use the v2 entry
only as historical evidence when the current user explicitly requests that
review.

### G3 ClimbPath Status - Historical Execution And Catalog Reconciliation

This historical documentation record does not resume G3 execution. Preserve
the existing repair records. The immutable historical execution authority is
`Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_STATUS.json`:
G2 has 17/48 frozen passes; the historical G3 runner namespace has 28/48
effective passes and 20/48 effective failures. The 20 failures are nine
terminal-position-error violations, eight simulation timeouts, two simulation
API failures, and one CheckModel failure.

For the active fixed catalog terminology, use
`Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_CATALOG_48_CURRENT_STATUS.json`.
It maps 33 exact historical identities plus eight aliases, seven post-freeze
supplemental FormalRunner records, and one post-freeze current-state override.
The four former no-runner fixed
composite entries now have thin whole-aircraft FormalRunners and one native
nominal 50 s ClimbPath record each: `fixed_awff_l1_indi` and
`fixed_linear_mpc_l1_indi` pass the terminal 5 m gate, while
`fixed_awff_l1_residual` and `fixed_qp_nmpc_l1_indi_cbf` are retained as
terminal-error failures. The QP NMPC outer MCP call timed out but native
MWORKS completion was separately verified at 50 s with a readable result; it
is not represented as an API-success call. The current result is 30/48 passes,
18/48 completed failures, and 0/48 not-run entries; `completed=false`. The
seven historical G3-only execution rows remain preserved in the artifact but
are not silently substituted for catalog entries.

The current catalog failure classes are 9
`terminal_position_error_exceeds_5m`, 8 `simulation_timeout`, and 1
`simulate_failed` (`adaptive_mpc`). The 2026-08-02
`pole_placement_luenberger` override supersedes only its current status: its
CheckModel passed and its source/parameter/solver-stable 50 s result reached
`402.1409427651827 m` terminal error, so it is a terminal-error failure rather
than a current CheckModel failure. The 2026-08-03 adaptive_mpc recovery attempt
remains outside this reconciliation until its final source is reloaded,
checked, simulated for 50 s, and read back for `position_error_norm`.

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
for the present current-catalog 30/48 state or the frozen historical 28/48 snapshot. No G3 rerun, gain-performance optimization, or
Gazebo/ROS work is authorized by the P0 documentation task.

### Historical Operator Surface Record - Separate Support Lane

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

### Historical ROS1/Gazebo Reproducibility Closure - Support Lane

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

## 3. No Global Next Action

There is no project-wide next action in the current operating model. A
conversation may perform work only when its current user request states the
scope and permits that action. Read this archive for historical facts only;
never use its next-gate wording as an instruction.

Before a live MWORKS, Gazebo, ROS, UE, or desktop action, load the relevant
topic workflow and declare the evidence path under `Results/` in the current
task's scope.

## 4. Historical Stopping And Handoff Contracts

The bullets below preserve former acceptance boundaries for trace-back. They
are not active stopping conditions or handoffs for any conversation.

For the historical report gate:

- Never overwrite the user's manually formatted report during experimentation.
- Preserve all text, images, existing table formatting, heading corrections,
  caption fields, and the first corrected MathType formula.
- A converted formula is accepted only when it remains editable as MathType,
  appears in the approved borderless 1-row/2-column layout, has a correct
  chapter-local number, and survives save/reopen plus Word visual review.
- Stop and report a blocker if MathType automation is unavailable, conversion
  changes formula semantics, numbering resolves to zero, Word shows repair or
  compatibility prompts, or layout damage cannot be bounded.
- Do not begin the post-submission generic builder/template cleanup until the
  formula review copy is accepted or the user explicitly changes priority.

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
- A future G3 repair required a separate direct user instruction and evidence
  root. No archived P0 or G3 wording authorizes a new experiment or runtime
  action.

## 5. Archive Maintenance Rule

Update this compatibility archive only when a user explicitly requests a
historical/status correction and the change is limited to the named evidence.
Do not use it to record a current task, owner, next gate, or handoff.

Put detailed run history in `Results/`, stable design in `Docs/Design/`, and
historical plans in `Docs/Cache/`.

## 6. Historical Board

The pre-cleanup board, including prior controller, Factory, FUEL, and
closeout history, is preserved at:

```text
Docs/Cache/workflow_history/mainline_operations_board_20260726_pre_cleanup.md
```
