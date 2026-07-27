# Mainline Operations Board

> Current task selector for MoSim. Keep this file short: it records only the
> active work, the next decision, and blockers. It is not a history ledger or
> a result archive.

Status: the canonical eight-layer Modelica root is established. The frozen
current-root MWORKS matrix is 46/46 terminal: 41 internal fixed-input probes
and five fixed whole-aircraft minimum closures. The Official PID baseline and
four shared Runner boundary baselines have the required native results,
captures, metrics, and dedicated-session closure, 2026-07-27 CST.

## 0. Task Authority and Evidence Snapshot

This board is the sole selector of the current task. `PROGRESS.md` is only a
dated snapshot and must not select or supersede current work. The detailed G6
execution contract is `Docs/Workflows/g6_controller_experiment_execution.md`;
`Docs/Workflows/controller_evidence_closeout.md` defines the G1-G7 completion
contract. Neither creates another task line or gate meaning.

## 1. Current Action

The approved atomic model-library migration is statically complete. The only
formal load root is `Models/MoSimQuadrotorModel/package.mo`; retired roots and
active old-path references are rejected by
`consolidate_mosimquad_model_root.py --check`.

The current 46-route evidence record is frozen at
`Results/model_library_refactor/controller_route_execution_current/`. It proves
41 controller-only internal responses and five fixed whole-aircraft minimum
closures, not family champion selection, seven-scenario comparison, code
generation, or flight-runtime behavior. The current-root Official PID baseline
is at `Results/control_platform/g6_formal_closed_loop_20260724/official_pid_climb_path_50s/`;
the four shared Runner-boundary baselines are at
`Results/control_platform/g6_runner_boundary_baseline_20260727/`.

The current action is G6 champion-test-harness promotion. For each of the six
nominal controller families, promote only a current-probe-passing candidate to
its own formal root-local core, public alias, explicit Adapter, whole-aircraft
source harness, minimum scenario, model hash, `CheckModel`, and minimum-closure
record. The provisional slate in
`Config/control_platform/g6_champion_selection.json` is eligibility input, not
a selected champion. `Config/control_platform/formal_closed_loop_harness_map.json`
currently records 0/6 provisional champion minimum closures passed.

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

1. do not rerun the frozen 46-route matrix unless the affected model hash,
   route interface, or evidence contract changes; keep the two missing-source
   blockers and `px4ctrl` runtime baseline explicit;
2. current executable gate: promote only a current-probe-passing candidate from
   each nominal family to
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

## 4. Stopping And Handoff Conditions

For the current champion-promotion gate:

- Stop and record a precise blocker if a candidate lacks the required current
  probe, source, interface mapping, native result, capture, metric, or
  dedicated-session closure. Do not substitute a fixed integrated chain or a
  historical result, and do not call that family promoted.
- Stop and ask the user before choosing a new controller/interface/runtime
  architecture, changing the approved source boundary, or widening into a
  different candidate family.
- Do not start seven-scenario A/B, ESO ablation, export, ROS1 runtime
  validation, G7, or R1 until this board selects that gate and the relevant
  workflow/evidence path is declared.

A champion may enter the seven-scenario A/B gate only after its own current-root
promotion record and verified minimum whole-aircraft closure exist. The current
promotion gate is complete only when all six families have that record or an
explicit family blocker on this board. A blocker does not authorize a substitute
architecture or A/B run for the blocked family. Update the D2 mapping/checker
and this board with accepted evidence pointers before handing off any champion.

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
