# Project Progress

> Historical progress snapshot only. This file is not a transcript, task
> selector, or authorization source. Work in each conversation starts from the
> current user's direct request, then the task-local source and workflow it
> names. Use the retired board or legacy ledger only for an explicit historical
> audit.

## 2026-08-03 CST - Current-catalog correction and adaptive MPC recovery status

- The fixed current catalog remains **30/48 passed, 18/48 completed failures,
  0/48 not-run**. Its failure-class breakdown is 9 terminal-position-error
  failures, 8 simulation timeouts, and 1 `adaptive_mpc` native
  `simulate_failed` record. The frozen historical G3 snapshot remains
  **28/48 passed, 20/48 failed** and is not overwritten.
- `pole_placement_luenberger` is no longer a current CheckModel failure: its
  2026-08-02 current-session CheckModel passed with 0 errors and one unit
  metadata warning, followed by a 50 s result with 25,001 finite samples,
  terminal error `402.1409427651827 m`, and RMSE `63.81822564113234 m`.
  It is now a current terminal-error failure. Evidence:
  `Results/mworks_live_gate/failed18_recovery_20260802/pole_placement_reopen/simulation_50s/POLE_PLACEMENT_SIMULATION_50S.json`.
- `adaptive_mpc` received a narrow adapter-local velocity-reference
  conditioning patch. The current GUI sentinel was clean, but final-source
  MWORKS reload timed out after 300 s; no final CheckModel, 50 s result,
  terminal metric, or catalog pass-count change is claimed. Evidence:
  `Results/mworks_live_gate/failed18_recovery_20260803/adaptive_mpc/ADAPTIVE_MPC_RECOVERY_20260803.json`.
- Reporting keeps the evidence layers separate: 48 catalog/run-audit entries,
  48 structure images, and 0/48 current-source-bound per-controller result
  images are different counts. This update changes Markdown status only; Word
  outputs are intentionally untouched.

## 2026-07-27 CST - Current Snapshot

This 2026-07-27 snapshot is historical evidence only. It does not select a
current task or authorize the MWORKS evidence-regeneration work below.

- The atomic model-library migration is statically complete. The canonical
  eight-layer root is `Models/MoSimQuadrotorModel/package.mo`; the root
  convergence, four-Runner contract, dynamics migration and controller-evidence
  contract checks pass. The current-root Official PID `ClimbPath` baseline and
  the four `ATTITUDE_THRUST`, `BODY_RATE_THRUST`, `ROTOR_COMMAND`, and `WRENCH`
  Runner contracts have also each passed real 50 s MWORKS runs with native
  results, two captures, valid metrics, and verified dedicated-session closure.
  Their evidence is under
  `Results/control_platform/g6_formal_closed_loop_20260724/official_pid_climb_path_50s/`
  and `Results/control_platform/g6_runner_boundary_baseline_20260727/`.
- The next current-root evidence gate is the serial 46-route graphical/internal
  matrix. The five baseline records validate the shared Plant/Runner boundaries
  only; they do not select six champions, establish seven-scenario A/B, or
  prove code-generation, Gazebo, PX4, ROS, MAVROS, or px4ctrl runtime behavior.
- The old G6 execution record is preserved under
  `Results/model_library_refactor/controller_route_execution_current/matrix_superseded/source_migration_20260727_031318/`,
  with each of its 46 route bundles under that route's `superseded/` directory.
  `G6_SOURCE_MIGRATION_SUPERSESSION_MANIFEST.json` binds the old 46/46 passed
  record to the current source-path transition. The active current-root matrix
  and status now have all 46 current-root rows passed: 41 internal fixed-input
  probes and 5 fixed whole-aircraft minimum closures. Their fresh records are
  under `Results/model_library_refactor/controller_route_execution_current/runs/`;
  the G6 evidence audit passes with 46 bound native-result screenshots and no
  errors. These results establish controller-level readiness only: champion
  selection, seven-scenario A/B, code generation, and runtime validation still
  require their own evidence.
- `Config/control_platform/formal_closed_loop_harness_map.json` has 0/6
  provisional champion minimum closures passed. The six candidate probes are
  awaiting the current matrix, and champion test-harness promotion plus
  seven-scenario A/B remain pending.
- `mworks_run_eligible_count=0` in
  `Config/control_platform/current_model_entry_map.json` is a static G4
  mapping field. It is not the G6 execution count and must not be read as
  "0/49 experiments run".

The 2026-07-22 three-UAV `r48`/`r49` MID360 obstacle-avoidance line remains
preserved evidence and a paused side branch. It is not the current mainline;
do not resume it from this file without a new board decision.

## How To Update This File

Keep only the newest active context and the smallest useful note for the next
turn. Move durable rules to workflows, skills, checkers, schemas, or design
docs. Do not append long packet histories or old thread logs here.
