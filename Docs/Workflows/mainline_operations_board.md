# Mainline Operations Board

> Current task selector for MoSim. Keep this file short: it records only the
> active work, the next decision, and blockers. It is not a history ledger or
> a result archive.

Status: P0a repaired the shared velocity-estimation and collective-thrust unit
boundary; P0b then passed Official PID and four shared Runner 50 s regressions
before the later reference-velocity/reference-acceleration contract repair.
Phase 1 completed its user-approved frozen 46-route matrix on 2026-07-27 CST.
The pre-P0a matrix and the six-candidate recovery both remain historical
trace-back only after the forward-reference repair. The new seven-scenario
contract, Plant/Runner bindings, Official PID hold harness, and trajectory
definitions passed static validation and native `CheckModel`; no current-source
replay, scenario simulation, or A/B comparison ran in that pre-simulation gate.

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

### Seven-Scenario Pre-Simulation Gate Passed - Awaiting User Review

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
- Stop: wait for user review before any current-source replay, the other 34
  `adapter_missing` rows, seven-scenario A/B, export, runtime validation, G7,
  or R1.

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

After the user reviews this contract repair, continue the approved
controller-evidence plan in this order:

1. replay Official PID and the six candidate Formal Runners on the same 50 s
   `ClimbPath` with this exact source, then derive the current RMSE ranking;
2. choose one measured winner from each of the seven semantic families and give
   only those candidates champion-specific minimum whole-aircraft closures;
3. compare each accepted winner with Official PID in hover, step, figure-8,
   spiral, wind, parameter-mismatch and motor-efficiency-fault scenarios; add
   `px4ctrl` only after its MWORKS-equivalent core passes its behavior/interface
   equivalence gate;
4. run the required ESO ablation trio, then export accepted candidates and
   validate the declared ROS1/Sunray/Gazebo/PX4/MAVROS/px4ctrl runtime path;
5. collect report/software-documentation material from the resulting evidence,
   then archive no-longer-used source only after a dependency audit.

Before a live MWORKS, Gazebo, ROS, UE, or desktop action, load the relevant
topic workflow and declare the evidence path under `Results/`.

## 4. Stopping And Handoff Conditions

For the completed seven-scenario pre-simulation gate:

- Static validation and native `CheckModel` passed for eight trajectories, four
  shared Runners, Official PID, and six champion Formal Runners. Commit and
  push the bounded repair, then wait for user review.
- Do not use P0b or the pre-repair six-candidate RMSE as current-source
  controller-family selection data. Replay is required first.
- Do not run the candidate/Official PID replay, the other 34 `adapter_missing`
  rows, seven-scenario A/B, ESO ablation, export, ROS1 runtime validation, G7,
  or R1 before a new user instruction.

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
