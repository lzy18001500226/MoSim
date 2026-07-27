# Mainline Operations Board

> Current task selector for MoSim. Keep this file short: it records only the
> active work, the next decision, and blockers. It is not a history ledger or
> a result archive.

Status: P0a repaired the shared velocity-estimation and collective-thrust unit
boundary; P0b then passed the current-root Official PID and four shared Runner
boundary 50 s regressions with native results, captures, metrics, and dedicated
session closure. Phase 1 then completed its user-approved frozen 46-route
matrix on 2026-07-27 CST. The pre-P0a 46-route matrix remains historical
trace-back only, not current Phase 1 evidence. The bounded six-candidate
recovery then completed with six current passing 50 s `ClimbPath` records; its
accepted ranking pointer is
`Results/control_platform/champion_candidate_recovery_20260727/CHAMPION_CANDIDATE_RMSE_RANKING.json`.

## 0. Task Authority and Evidence Snapshot

This board is the sole selector of the current task. `PROGRESS.md` is only a
dated snapshot and must not select or supersede current work. The detailed G6
execution contract is `Docs/Workflows/g6_controller_experiment_execution.md`;
`Docs/Workflows/controller_evidence_closeout.md` defines the G1-G7 completion
contract. Neither creates another task line or gate meaning.

## 1. Current Action

### Champion Candidate Recovery Complete - Awaiting User Review

- Workflow: `Docs/Workflows/run_simulation.md`.
- Frozen matrix driver: `Scripts/mworks/run_phase1_minimum_closure.py`.
- Contract test: `Scripts/tests/test_phase1_minimum_closure.py`.
- Recovery evidence root:
  `Results/control_platform/champion_candidate_recovery_20260727/`.
- Accepted ranking:
  `Results/control_platform/champion_candidate_recovery_20260727/CHAMPION_CANDIDATE_RMSE_RANKING.json`
  and `.csv`. All six named candidates passed their plant-coupled 50 s
  `ClimbPath` run with finite terminal error below 5 m and recorded position
  RMSE.
- The ranking is a common-scenario recovery record, not seven-scenario A/B,
  code-generation, Gazebo, ROS, or flight-runtime evidence.
- Stop: wait for a new user instruction. Do not run the other 34
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

The completed user-approved recovery was limited to the six nominal-family
candidate rows named above. Phase 1's original failures remain archived by the
rerun procedure; each successful rerun proves only that candidate's repaired
minimum whole-aircraft `ClimbPath` closure and supplies its RMSE for the next
ranking decision.

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

After the user reviews the six-candidate ranking, continue the approved controller-evidence plan
in this order:

1. choose one measured winner from each of the six nominal families and give
   only those candidates champion-specific minimum whole-aircraft closures;
2. compare each accepted champion with Official PID in hover, step, figure-8,
   spiral, wind, parameter-mismatch and motor-efficiency-fault scenarios;
3. run the required ESO ablation trio, then export accepted candidates and
   validate the declared ROS1/Sunray/Gazebo/PX4/MAVROS/px4ctrl runtime path;
4. collect report/software-documentation material from the resulting evidence,
   then archive no-longer-used source only after a dependency audit.

Before a live MWORKS, Gazebo, ROS, UE, or desktop action, load the relevant
topic workflow and declare the evidence path under `Results/`.

## 4. Stopping And Handoff Conditions

For the completed champion-candidate recovery gate:

- All six named candidates now have current passing 50 s `ClimbPath` records
  with documented RMSE. Commit and push the bounded repair, then wait for user
  review.
- Do not use P0b fixture results as controller-family selection data; they
  validate shared Runner boundaries only.
- Do not run the other 34 `adapter_missing` rows, seven-scenario A/B, ESO
  ablation, export, ROS1 runtime validation, G7, or R1 before a new user
  instruction.

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
