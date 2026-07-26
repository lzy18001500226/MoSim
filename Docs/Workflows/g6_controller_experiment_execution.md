# G6 Controller Experiment Execution

> Current execution contract for G6 in
> `Docs/Workflows/controller_evidence_closeout.md`. It refines, but does not
> replace, that G1-G7 workflow; it does not define another G6 or choose the
> current task. The current task selector is
> `Docs/Workflows/mainline_operations_board.md`.

## 1. Scope and Claim Boundary

The frozen current inventory is 49 top-level schemes: 46 MWORKS routes, two
implementation blockers, and the `px4ctrl` runtime baseline. G6 executes only
the 46 current MWORKS routes. Historical `65/67` code-generation or SIL
records are trace-back material only and are not G6 result rows.

Every route must produce a current result record, but the result class is
fixed by `Config/control_platform/formal_closed_loop_harness_map.json`:

| Route class | Count | Required G6 run | Allowed claim |
|---|---:|---|---|
| `internal_fixed_input_probe` | 41 | CheckModel, fixed-input MWORKS simulation, readable result variables, metrics, and native result-window capture | Internal graphical control-law behavior only; not aircraft/plant tracking |
| `whole_aircraft_minimum_closure` | 5 | CheckModel, plant-coupled minimum MWORKS simulation, readable result variables, metrics, and native result-window capture | Named formal whole-aircraft minimum closure only |

An internal probe cannot be relabeled as a whole-aircraft result. A failed or
blocked run is still valid evidence when its model hash, error, screenshot, and
stop reason are preserved.

## 2. G6 Execution Matrix

The reproducible matrix is generated from the current harness map and G5
status, not hand-maintained:

```powershell
python Scripts/quality/build_g6_controller_execution_matrix.py --output-root Results/model_library_refactor/controller_route_execution_current --write
python Scripts/quality/build_g6_controller_execution_matrix.py --output-root Results/model_library_refactor/controller_route_execution_current --check
```

Authority file:

```text
Results/model_library_refactor/controller_route_execution_current/G6_EXECUTION_MATRIX.json
```

The matrix freezes each route's current source hash, exact MWORKS target,
evidence class, and destination. A source change after matrix generation
invalidates that row until the matrix is regenerated and the earlier result is
retained as superseded trace-back evidence.

### Native direct-graph serialization refresh

The 13 generated direct graphical routes may receive one MWORKS-native default
experiment/sampling tuple on their first load and 0.2 s probe simulation:
`IntegratorStep=0, StartTime=0, StopTime=0.2, StoreEventValue=0`, plus
`OutputInterval=0.004`. This is not accepted as a generic source change. It
may be re-frozen only when the strict comparator proves that these exact
defaults are the sole difference; controller equations, ports, connections,
visual metadata, and every other experiment field must still match. Archive
the prior matrix/status and create the refresh manifest before rerunning only
those changed routes:

```powershell
python Scripts/quality/build_g6_controller_execution_matrix.py --output-root Results/model_library_refactor/controller_route_execution_current --write --refresh-native-serialization
```

The runner freezes the target, controller core, and every explicit model-load
prerequisite before live execution. Exact source bytes are stored under
`raw/frozen_bound_sources/`, then rechecked after prerequisite load, target
load/check/open/simulate, before the terminal record, and again after its
runner-owned dedicated Sysplorer process is confirmed closed. The last check
catches deferred native graph serialization during process shutdown. Only UTF-8
line-ending, trailing-horizontal-whitespace, and one terminal-final-newline
differences between a source and its exact snapshot may be accepted; the runner
restores the exact snapshot bytes and verifies their SHA-256 against the frozen
matrix binding. Any other later drift is a `source_hash_mismatch`, not a passed
simulation. Target-only records made before this contract remain explicitly
legacy rather than being silently upgraded.

If a route was stopped solely by the older post-session whitespace guard, first
run the file-only repair for an explicit route list, inspect its manifest, then
rerun those routes. The repair does not open MWORKS and rejects every source
whose native whitespace normal form differs from the exact frozen snapshot.
For legacy records made before snapshots were captured, it may use the local
`HEAD` blob only when that blob's SHA-256 exactly equals the frozen matrix
target; this provenance is recorded in the repair manifest:

```powershell
python Scripts/mworks/run_g6_controller_execution.py `
  --matrix Results/model_library_refactor/controller_route_execution_current/G6_EXECUTION_MATRIX.json `
  --only backstepping_baseline,fopid `
  --repair-native-whitespace
```

### Post-G6 metadata-only refresh

The formal harness map also records later champion selection, Official PID
baseline binding, and candidate-adapter metadata. Those fields are outside the
46-route execution source projection. After terminal G6 evidence exists, a
plain `--write` is intentionally rejected. When only that later metadata has
changed, use the guarded refresh:

```powershell
python Scripts/quality/build_g6_controller_execution_matrix.py --output-root Results/model_library_refactor/controller_route_execution_current --write --refresh-metadata-only
python Scripts/quality/build_g6_controller_execution_matrix.py --output-root Results/model_library_refactor/controller_route_execution_current --check
```

Before replacement, the command compares all 46 route bindings, including
target model path/class/SHA-256, probe contract, result destinations, and
claim boundary. It requires 46 passed status rows, hashes all 46 bound
`RUN_RECORD.json` files, retains the preceding matrix under
`matrix_superseded/`, and leaves `G6_EXECUTION_STATUS.json` plus every run
record untouched. The generated
`G6_METADATA_ONLY_REFRESH_MANIFEST.json` binds the prior status matrix hash to
the refreshed matrix only when the route-binding and run-record inventories
are identical. Any route-level difference must use an explicit source/rerun
supersession path; it cannot be hidden as metadata.

After the matrix reaches a terminal state, run the fail-closed evidence audit
before champion selection:

```powershell
python Scripts/quality/check_g6_controller_execution_evidence.py --output-root Results/model_library_refactor/controller_route_execution_current --write
```

## 3. Per-Route Procedure

Run routes serially in one reusable Sysplorer session. Do not parallelize GUI,
MCP, or live MWORKS actions.

1. Capture and classify the current MWORKS window once per contiguous batch.
   Stop for login, activation, authorization, demo, crash-report, or unknown
   modal states. The user authorized bounded ordinary recovery for non-license
   MWORKS instability; use the project MWORKS skill's one-restart limit.
2. Read the route from the generated G6 matrix. In a clean dedicated session,
   load only `Models/MoSimQuadrotorModel/package.mo`; its embedded `Plant`
   package owns the baseline plant and resources. Before loading the frozen
   target, freeze and verify the target, its controller core, and every
   route-bound `model_load_prerequisites` leaf. The 41 internal probes have no
   leaf prerequisite. Each
   fixed whole-aircraft chain first loads the real embedded Sysblock definition
   derived from the actual `controller3_2` source declaration, then loads the
   hash-bound namespace compatibility alias when that legacy declaration is
   unqualified. It need not equal that route's G5 graphical review target.
   Record root and route-prerequisite paths, classes, hashes, and load outcomes
   in provenance. Do not load an external `QuadrotorModel` package.
   Load the target without a forced project-root reload, because MWORKS can
   unload an already verified leaf definition when it forcibly reloads a child
   model. These loads are not substitute targets or evidence classes.
3. Run `CheckModel` before every simulation.
4. Run the declared fixed-input internal probe or formal whole-aircraft target
   through the existing project `Scripts/mworks/run_sysplorer_mcp_smoke.py`
   pathway. Read time and declared result variables through the MWORKS result
   API; a `SimulateModel` return alone is insufficient.
5. Allocate a fresh native `Result.msr` root for every execution before
   simulation. A retained result root may be locked by Sysplorer or cause
   MWORKS to create `ModelName-1`/`ModelName-2`; it is historical provenance,
   never a candidate for the current route's result binding. Open the real
   current native result in Sysplorer, plot a route-bound result
   variable, and capture the rendered native window. Do not use exported
   MWORKS canvas images, prior report images, cropped images, or stretched
   screenshots. The capture title must bind to the current model's native
   `- 结果查看器` window and the saved image must pass the runner's chart-body
   trace check; a Sysplorer model canvas, an unbound generic result viewer, or
   an empty result window is a `screenshot_failed` route result.
6. Write the result record, raw result locator, metrics, phase observations,
   and screenshot manifest under the route's matrix destination. Copy only the
   verified native result window to the report slot
   `Docs/报告/图/控制器/<family>/<scheme>/02_最小闭环结果原生窗口.png`.
   When a re-frozen target supersedes an earlier run of the same scheme, the
   report slot may be refreshed only when its existing hash exactly matches the
   archived same-scheme native result capture. Record both the archived and
   current target hashes; never overwrite a manually curated or unbound image.

Each run directory must contain:

```text
RUN_RECORD.json
logs/check_model.json
logs/simulate_model.json
logs/screenshot_manifest.json
raw/
raw/frozen_bound_sources/
metrics/
screenshots/01_after_check.png
screenshots/02_result_window.png
```

At the end of each G6 runner invocation, close only the dedicated Sysplorer
instance started by that invocation and write a batch cleanup record. Do not
close an existing user MWORKS/Sysplorer instance, a main window from another
session, or any login/license/authorization surface. After the process exit is
confirmed, append `after_session_shutdown` to the source-hash observations of
every protected source of every attempted route. Only the strict whitespace
rule may restore a frozen source at this final stage; otherwise mark the route
`source_hash_mismatch`.
If process closure cannot be verified, a previously passed route becomes
`session_cleanup_unverified` and cannot satisfy the final evidence audit.

### Guarded Report-Result Reconciliation

When a route has already completed CheckModel, native result read, native
result-window capture, post-session source validation, and dedicated-session
cleanup, the runner may still stop at `result_binding_failed` because an older
unbound report image occupies the destination slot. Do not silently overwrite
that image or rerun a healthy MWORKS route merely to replace it. Under an
explicit current-task instruction to replace legacy report assets, use the
file-only reconciliation path with an explicit route list:

```powershell
python Scripts/mworks/run_g6_controller_execution.py `
  --matrix Results/model_library_refactor/controller_route_execution_current/G6_EXECUTION_MATRIX.json `
  --only fixed_awff_l1_indi,fixed_awff_l1_residual,fixed_awff_pid,fixed_linear_mpc_l1_indi,fixed_qp_nmpc_l1_indi_cbf `
  --reconcile-report-result-bindings
```

This command starts no MWORKS process and changes no model/controller source.
It accepts only explicitly named `result_binding_failed` records whose failure
is the guarded report-slot conflict, whose current `Result.msr`, metrics,
result-window screenshot and capture manifest remain bound, and whose
post-session protected-source hashes still match. It first copies the prior
report image into that route's `superseded/report_asset_reconciliation/` tree
with a hash manifest, then atomically binds the current native capture and
records the status transition in `RUN_RECORD.json`. Any other failed state or
manually altered evidence remains rejected.

If that conflict occurred before the runner wrote its `before_record` hash
observation, the final evidence audit may accept that one missing phase only
when it independently validates the reconciliation schema and guarded prior
error, the archived-image hash manifest, the current native-capture/report
hash equality, complete result readiness, verified dedicated-session closure,
and exact `after_session_shutdown` hashes for every frozen protected source.
It never synthesizes the missing historical observation. A missing phase for
any other reason remains an audit failure.

## 4. Screenshot Acceptance

The screenshot source is Windows MCP direct whole-window or desktop capture of
the rendered MWORKS/Sysplorer window at native aspect ratio. A capture manifest
records the target title, process, dimensions, SHA-256, window state, capture
mode, and the bound model/harness hash. A result screenshot is accepted only
when all of the following agree:

1. matrix `scheme_id` and target class;
2. current target SHA-256;
3. result-window title or displayed model identity;
4. native result/metrics locator; and
5. `CheckModel` plus result-variable read in the same route record.

The existing `01_图形模型.png` assets remain G5 structure evidence. The
`02_最小闭环结果原生窗口.png` asset is G6 result evidence and must never be
filled by a structure screenshot or historic output.

## 5. Champion Promotion

After all 46 rows reach a terminal state, select one provisional candidate from
each nominal family: PID, classic/robust, sliding mode, optimization,
geometric/flatness, and learning. The internal-probe result is a readiness
screen, not a performance ranking. Selection must record:

- passed/blocked probe state and finite-output checks;
- controller interface and adapter feasibility;
- source ownership and model readability;
- the reason the candidate, rather than another family member, is promoted.

The current selection authority is
`Config/control_platform/g6_champion_selection.json`; the generator-backed
formal harness map records its derived core hashes, passed G6 probe bindings,
and whether a candidate is still awaiting an adapter. `official_pid` remains a
separate A/B baseline binding unless it is proven semantically identical to the
selected PID-family core; a small AWFF altitude-loop graphical probe cannot
stand in for that full baseline controller.

### Official PID formal baseline

Before any candidate adapter is built, run the separately bound formal
Official PID baseline. It uses
`OfficialPidFormalRunner -> OfficialPIDRotorAdapter -> RotorCommandRunner ->
Sunray150Assembly` on the 50-second `ClimbPath` scenario. This is not a
replacement for the frozen 46-route matrix and must never modify its route
records or status file.

```powershell
python Scripts/mworks/run_g6_formal_closed_loop_baseline.py --check-only
python Scripts/mworks/run_g6_formal_closed_loop_baseline.py
```

The dedicated run root is
`Results/control_platform/g6_formal_closed_loop_20260724/official_pid_climb_path_50s/`.
It must contain the formal `RUN_RECORD.json`, a CheckModel/model-window
capture, a native result-window capture, a fresh native `Result.msr`, raw CSV,
metrics, MCP JSONL, screenshot manifest, and session-cleanup record. Its
record explicitly declares `not_member` in the frozen 46-route matrix. On an
otherwise finite run, the final 5 s must also meet the recorded stability gate:
terminal and tail-RMSE position errors no greater than 0.5 m, and a tail peak
error no greater than 1.0 m. A finite but divergent trace is recorded as
`stability_failed`, not a passing baseline.
intentional retry, use `--rerun`; the previous record and logs are retained
under the run root's `superseded/` directory.

`OfficialPidFormalRunner` is an extends-only formal wrapper. Its window capture
proves that the named wrapper was checked, but a blank wrapper canvas is not
controller graphical-topology evidence and must not be used as such in the
report. The native result-viewer capture is restricted to position and
reference tracks for readable review; the full command/state set remains bound
in the raw CSV and native result.

For every selected candidate, create a formal-root binding consisting of its
controller core, explicit Adapter, plant-coupled whole-aircraft source harness,
minimal scenario, and source hashes. Update the formal harness map and its
checker before attempting the candidate's whole-aircraft minimum closure.

For a promoted leaf runner, preload `MoSimQuadrotorModel/package.mo` once with
`force_reload=false`, then hash/load the exact runner leaf and force-reload
only `MoSimQuadrotorModel/package.mo`. Leaf-first loading can leave graphical
block dependencies unresolved in a clean Sysplorer session; the preload binds
the canonical namespace before the leaf is parsed, while the root reload
rematerializes the target and embedded `Plant` through `package.order` before
`CheckModel`. Record both the base-package preload and package-root
materialization. This ordering is specific to promoted formal runner leaves
and does not rewrite the frozen 46-route evidence procedure.

When a continuous plant and a C-function controller create an initialization
algebraic loop, the formal runner may use an explicit sampled controller-input
boundary instead of changing the controller core. The champion binding must
state the sample period, initial measurement, and every delayed signal; the
runner's binding checker must verify the matching `UnitDelay` source topology.
This is a named offline MWORKS harness condition, not a claim that the deployed
controller has changed or that it has passed PX4/Gazebo/ROS runtime validation.

When a readable direct graphical controller passes its top-level G5 probe but
MWORKS fails only because nested Sysblock child ports are not materialized, the
formal adapter may use a current-root `equation_bridge`. The binding must freeze
both the graphical source and bridge hashes, name the bridge class and reason,
and preserve the G5 graphical model as the only topology evidence. The bridge
must carry the same scalar law, gains, limits, enable gate, and input/output
boundary; it is not a claim that nested graphical Sysblock semantics, code
generation, PX4, Gazebo, ROS, or flight runtime were independently accepted.

## 6. Seven-Scenario A/B

Only champions whose promoted test harness passes minimum closure enter the
same-parameter A/B matrix against Official PID:

```text
hover, step, figure8, spiral, wind, parameter_mismatch, motor_efficiency_fault
```

Each row records controller, scenario, plant/harness hashes, raw result,
metrics, result screenshot, acceptance decision, and claim boundary. The PID
family may reuse Official PID's formal harness only when Official PID is the
selected PID candidate; it is not double-counted.

## 7. Completion Boundary

G6 completion permits the MWORKS controller, metric, and comparison chapters
of the report to be written. It does not by itself claim code generation, SIL,
joint simulation, Gazebo/PX4 deployment, RViz review, or UE visualization.
Those remain separate report evidence lanes and must be bound to the final
selected controller rather than an earlier historic asset.
