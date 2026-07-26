# Mainline Operations Board

> Current task selector for MoSim. Keep this file short: it records only the
> active work, the next decision, and blockers. It is not a history ledger or
> a result archive.

Status: the 47-Profile target, seven-family taxonomy and enhancement boundary
are documented. The project-owned Modelica surface is now the canonical
eight-layer root; static migration gates and the current-root Official PID plus
four-Runner baseline gate pass. The 46-route current-hash evidence matrix is
the next executable gate, 2026-07-27 CST.

## 0. Task Authority and Evidence Snapshot

This board is the sole selector of the current task. `PROGRESS.md` is only a
dated snapshot and must not select or supersede current work. The detailed G6
execution contract is `Docs/Workflows/g6_controller_experiment_execution.md`;
it refines current G6 in
`Docs/Workflows/controller_evidence_closeout.md` and does not create another
task line or gate meaning.

## 1. Current Action

The approved atomic model-library migration is statically complete. The only
formal load root is `Models/MoSimQuadrotorModel/package.mo`, with
`Parameters` / `Vehicle` / `Control` / `Experiment` / `Guidance` /
`Deployment` / `Visualization` / `Common`; retired roots and active old-path
references are rejected by `consolidate_mosimquad_model_root.py --check`.

The current-root Official PID `ClimbPath` 50 s baseline at
`Results/control_platform/g6_formal_closed_loop_20260724/official_pid_climb_path_50s/`
passed with a readable native result, two MWORKS captures, valid metrics, and
verified dedicated-session closure. The `ATTITUDE_THRUST`, `BODY_RATE_THRUST`,
`ROTOR_COMMAND`, and `WRENCH` Runner contracts under
`Results/control_platform/g6_runner_boundary_baseline_20260727/` also each
passed a 50 s, 5,001-sample current-root run with the same result and cleanup
requirements. These five records validate the common Plant/Runner boundaries;
they do not promote a controller family or establish flight-runtime behavior.

The next executable gate is the current-hash 46-route MWORKS evidence matrix.
Do not treat a static namespace migration or an old-hash result as a current
MWORKS simulation.

The pre-migration Official PID `ClimbPath` 50 s reference reached the declared
stop time with terminal position error `0.00651 m`, final-5-s RMSE `0.01703 m`,
and final-5-s peak `0.04650 m`. It remains comparison evidence under
`Results/model_library_refactor/20260726_plant_runner_baseline/official_pid_climb_path_50s/`,
but must be regenerated from the canonical root before it becomes the current
A/B baseline.

`Config/control_platform/controller_route_interface_matrix.json` records the
46 current route interfaces. The preserved pre-migration G6 execution record
contains 46/46 terminal constrained rows: 41 `internal_fixed_input_probe`
records and 5 named `whole_aircraft_minimum_closure` records. Their model hashes
do not constitute current-root evidence after the atomic namespace migration.
They are not a 46-route whole-aircraft closure, seven-scenario comparison,
code-generation, or runtime-acceptance result. In particular,
`Config/control_platform/formal_closed_loop_harness_map.json` records 0/6
provisional champion minimum closures passed; champion promotion and seven
scenario A/B have not started. The `mworks_run_eligible_count=0` field in
`Config/control_platform/current_model_entry_map.json` is a G4 static mapping
field, not a count of the preserved G6 execution rows.

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

Continue the user-approved controller-evidence plan in this order:

1. re-run the current-hash graphical/internal evidence matrix for the 46
   resolved MWORKS routes, keeping the two missing-source blockers and
   `px4ctrl` runtime baseline explicit;
2. promote only a current-probe-passing candidate from each nominal family to
   a champion-specific core/Adapter/plant harness, then establish its minimum
   whole-aircraft closure;
3. compare each accepted champion with Official PID in hover, step, figure-8,
   spiral, wind, parameter-mismatch and motor-efficiency-fault scenarios;
4. run the required ESO ablation trio, then export accepted candidates and
   validate the declared ROS1/Sunray/Gazebo/PX4/MAVROS/px4ctrl runtime path;
5. collect report/software-documentation material from the resulting evidence,
   then archive no-longer-used source only after a dependency audit.

Before a live MWORKS, Gazebo, ROS, UE, or desktop action, load the relevant
topic workflow and declare the evidence path under `Results/`.

## 4. Board Update Rule

Update this board only when one of these changes:

- current task or next executable gate;
- declared architecture/runtime authority;
- terminal blocker and its required resolution;
- accepted evidence pointer.

Put detailed run history in `Results/`, stable design in `Docs/Design/`, and
historical plans in `Docs/Cache/`. Do not append progress narration here.

## 5. Historical Board

The pre-cleanup board, including prior controller, Factory, FUEL, and
closeout history, is preserved at:

```text
Docs/Cache/workflow_history/mainline_operations_board_20260726_pre_cleanup.md
```
