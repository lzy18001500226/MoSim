# Project Progress

> Current active-progress note only. This file is not a transcript and must not
> be used for historical recovery. For current operating state, read
> `Docs/Workflows/mainline_operations_board.md` first. For historical
> multi-thread or packet trace-back, use `Docs/Workflows/agent_task_ledger.md`
> only when explicitly auditing legacy material.

## 2026-07-27 CST - Current Snapshot

`Docs/Workflows/mainline_operations_board.md` is the only current-task
selector. Its active task is the current-root MWORKS evidence regeneration;
this file does not select a competing task.

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
  and status now have five passed PID-family graphical fixed-input probes
  (`official_pid`, `cascade_pid`, `gain_scheduled_pid`, `fuzzy_pid`, and
  `neural_pid`) and 41 pending rows. Their fresh records are under
  `Results/model_library_refactor/controller_route_execution_current/runs/`;
  they establish only internal controller responses, so new MWORKS executions
  are still required before any controller-family, champion, A/B, or runtime
  claim.
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
