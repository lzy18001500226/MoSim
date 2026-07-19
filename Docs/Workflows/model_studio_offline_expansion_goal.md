# Model Studio Offline Expansion Goal

Status: active

Baseline commit: `7384e2161d0704c7e2dc022f359b74154c6d4ab9`

## 1. Objective

Preserve the reproducible competition baseline while expanding Model Studio
into an offline composition platform for every implemented controller,
augmentation, safety, fault-tolerance, and formation module. Each promoted
combination must have a legal Profile, an explicit output-boundary Adapter, a
real MWORKS run, `Result.msr`, strict metrics, and native animation-window
evidence.

Directory migration is deliberately last. Do not move or rename these paths
until the extension platform passes its full regression and a migration freeze
point is recorded:

```text
Models/MoSimQuadrotorModel
Models/QuadrotorControllerBlocks
Models/QuadrotorExperiments
```

## 2. Rollback And Ownership Boundary

The commit above is the immutable rollback and comparison baseline. P0 and P1
derive their inventory from the committed registry at that exact revision, not
from an uncommitted working-tree registry.

Until shared-file ownership is clear, this Goal owns only:

```text
Docs/Workflows/model_studio_offline_expansion_goal.md
Config/control_platform/offline_expansion_inventory.json
Config/control_platform/offline_composition_catalog.json
Config/control_platform/offline_runner_interface_contract_v1.json
Config/control_platform/offline_batch_a_adapter_backlog.json
Scripts/quality/build_offline_expansion_inventory.py
Scripts/quality/check_offline_expansion_inventory.py
Scripts/quality/check_offline_composition_catalog.py
Scripts/quality/check_offline_runner_interface_contract.py
Scripts/quality/check_offline_batch_a_adapter_backlog.py
Scripts/mworks/generate_offline_profile_wrapper.py
Scripts/mworks/run_offline_profile_certification.py
Models/MoSimQuadrotorModel/ExperimentRunner/Adapters/OfflineAttitudeThrustController.mo
Models/MoSimQuadrotorModel/ExperimentRunner/Adapters/OfflineAttitudeRateAllocator.mo
Results/control_platform/offline_expansion_goal_20260719/requests/*.json
Scripts/tests/test_offline_expansion_inventory.py
Scripts/tests/test_offline_composition_catalog.py
Scripts/tests/test_offline_profile_wrapper.py
Scripts/tests/test_offline_runner_interface_contract.py
Scripts/tests/test_offline_batch_a_adapter_backlog.py
```

Do not overwrite concurrent work in the realtime MWORKS lane, QGC, UE,
Orchestrator, profile catalog, module registry, or existing model packages.

## 3. Evidence Contract

A module or composition is offline-certified only when one same-version run
provides all of the following:

1. The MWORKS model check passes.
2. The MWORKS simulation completes without solver, numerical, login, license,
   authorization, or GUI errors.
3. A current `Result.msr` is produced from that run.
4. Required result variables are present and strict metrics pass unchanged
   thresholds.
5. The native result/animation window opens for the same model and result.
6. The Profile, generated Wrapper, model hash, result path, metrics, and window
   evidence are bound by one run manifest.
7. Targeted automated checks pass, exact task paths are committed, pushed, and
   verified against upstream.

Source checks, generated-C tests, Gazebo runs, historical raw files, screenshots
from another run, or a merely open window cannot replace a failed item above.
They may be retained as lower-level evidence with an accurate claim ceiling.

## 4. Composition Policy

Use the least duplicated implementation that real evidence permits:

1. Shared Plant/Animation, shared boundary Runner, and a thin generated Wrapper.
2. Shared Plant/Animation, a dedicated boundary Runner, and a thin Wrapper.
3. A dedicated complete model only after a recorded incompatibility proves the
   first two forms cannot preserve semantics or numerical stability.

Four controller output boundaries remain explicit and separate:

```text
ATTITUDE_THRUST
BODY_RATE_THRUST
WRENCH
ROTOR_COMMAND
```

Safety, fault events, formation references, and backend-owned inner loops are
not silently retyped as one of those command boundaries. Their composition
must declare the Adapter and owner that eventually reaches a Runner boundary.

Offline MWORKS inner-loop evidence and online PX4-owned inner-loop evidence are
different claims. Keep their owners explicit in Profiles and run manifests.

## 5. Batch Order

| Phase | Scope | Exit Gate |
|---|---|---|
| P0 | Freeze baseline, ownership, evidence contract, and acceptance rules. | This workflow and baseline hash pass checks. |
| P1 | Classify all baseline registry modules by layer, native boundary, maturity, evidence, Adapter state, legal Profile state, value, and batch. | Inventory covers all 77 unique baseline modules and passes the checker. |
| P2 | Extend shared Plant/Animation, four Runners, Adapter fixtures, catalog fields, Profile validation, and checker contracts. | Boundary fixtures and compatibility failures are deterministic; no current certified Profile regresses. |
| P3 / Batch A | Mature high-value PID family and augmentations, including Official PID, Cascade/Gain-Scheduled/Fuzzy/Neural PID claim-bounded variants, PID-INDI, anti-windup, feedforward, L1/AWFF, ADRC, standardized INDI, parameter scheduling, and ILC. | Each promoted default Profile has fresh complete MWORKS evidence. |
| P4 / Batch B | Classical, linear/robust, geometric, backstepping, SMC, and MPC families. | Stable modules are certified; numerical or capability failures remain blocked with exact evidence. |
| P5 / Batch C | Trained neural/RL routes, safety supervisors, fault detection, FTC, reconstruction, and safe landing. | No learning claim exceeds its trained-policy evidence; fault runs cover injection through recovery or safe terminal action. |
| P6 / Batch D | Multi-UAV formation only, beginning with leader-follower and then the remaining implemented formation methods. | Same-run multi-UAV `Result.msr`, formation metrics, and native animation evidence pass. |
| P7 | APP batch queue, run/cancel/rerun, result index, failure states, and bounded window/session cleanup. | Automated APP tests and manual smoke prove results remain attributable and rerunnable. |
| P8 | Freeze code-generation and online co-simulation-compatible interfaces. | Shared schemas preserve frame, time, lifecycle, authority, and output-boundary semantics without claiming online validation. |
| P9 | Full extension regression and migration freeze point. | Baseline plus every accepted extension reruns; migration manifest and rollback test are approved. |
| P10 | Refactor the three model directories in small reversible batches. | Compatibility aliases, path manifest, full regression, commits, pushes, and upstream verification all pass. |

## 6. Batch Acceptance And Stop Rules

Every batch is a separate deliverable. It must produce a checkpoint, tests,
evidence index, exact commit, push, upstream verification, and one terminal
Chinese email. Do not send terminal email for ordinary intermediate work.

Stop the affected batch immediately on MWORKS login, license, authorization,
unknown blocking window, GUI error, repeated solver divergence, or unclear file
ownership. Record the blocker and leave the Goal active. Do not relax metrics,
rename a failure, switch to substitute evidence, or move directory migration
forward to make progress appear complete.

After every live simulation, close only task-owned result/simulation windows
using the documented MWORKS window rules. Do not close reusable main windows or
other tasks' windows.

## 7. Current Checkpoint

P0 is frozen by this document. P1 authority is:

```text
Config/control_platform/offline_expansion_inventory.json
Scripts/quality/build_offline_expansion_inventory.py
Scripts/quality/check_offline_expansion_inventory.py
```

The first live MWORKS expansion must not begin until P1 is committed and
pushed, Batch A's exact write set is confirmed free, and the project-local
MWORKS operation/evidence skills have been loaded.

P2 static checkpoint 1 adds a versioned layered-composition contract while
preserving the competition baseline's legacy single-module requests. Existing
Adapters are now classified as boundary fixtures or legacy bundles. Only the
three currently provable registry mappings are exposed as exact layered
requests:

```text
official_pid
official_pid + awff
official_pid + pid_indi
```

The tuned `improved_pid`, historical `linear_mpc`, bundled `l1_awff`, blocked
`qp_nmpc_safety`, and bundled `fault_compensation` entries remain explicit
unresolved aliases. They can rerun their accepted legacy Profiles but cannot
claim arbitrary layered composition until source/model audits and new Adapters
close those mappings. P2 remains active: shared layer interfaces, compatibility
matrix expansion, Adapter fixtures, and full four-boundary regression are not
yet complete.

P2 static checkpoint 2 freezes the current four-Runner source surface at
`Config/control_platform/offline_runner_interface_contract_v1.json`. It records
the real signal names and current offline owners while explicitly blocking
physical-unit, coordinate-frame, lifecycle, code-generation, and online claims.
The existing legacy-scaled thrust, wrench, and rotor values must not be relabeled
as SI or MAVROS command units by documentation or APP code. The checker is
`Scripts/quality/check_offline_runner_interface_contract.py`.

The first current-turn Sysplorer `session_manager(probe)` did not return within
the bounded wait and was terminated without start, reconnect, click, or model
mutation. Therefore live four-Runner `check_model` and simulation remain blocked
at this checkpoint; static contracts do not supersede that blocker.

P2 static checkpoint 3 freezes candidate frame, solver-time, lifecycle, numeric
validity, and module-diagnostics semantics in the same Runner contract. These
fields are deliberately marked unbound: no `.mo` ports were changed, and the
contract checker rejects attempts to promote frame, fixed-step, realtime-rate,
lifecycle, diagnostics, or invalid-number handling from configuration alone.
This preserves a consistent future code-generation/online interface without
claiming either capability now.

A second bounded read-only Sysplorer `session_manager(probe)` also produced no
response within 30 seconds and was terminated. No start, reconnect, click,
model mutation, or window action was attempted. This is the second observed
live blocker occurrence for the active Goal; P2 live model checks and
simulations remain blocked while static fail-closed contract work can continue.

P2 static checkpoint 4 makes every current compatibility entry declare the
three-part Adapter chain: native registry boundary, Adapter output boundary,
and offline inner-loop owner. The three resolved registry compositions all
declare an offline-only legacy bundle conversion from `ATTITUDE_THRUST` to
`ROTOR_COMMAND`; this preserves their accepted offline Profiles but explicitly
blocks reuse as native-boundary code-generation or online evidence. Unresolved
legacy aliases must keep their native boundary null and remain disabled for
code-generation/online reuse until a source/model audit proves an exact
registry mapping.

The third bounded read-only probe returned once and exposed a visible
Sysplorer port, so the Goal attempted the smallest authorized live gate: one
batch `check_model` call covering the four existing Runners without reload or
model mutation. That call returned nothing within approximately 100 seconds
and was terminated. A follow-up read-only probe then also returned nothing
within 30 seconds. The live blocker record is:

```text
Results/control_platform/offline_expansion_goal_20260719/P2_LIVE_BLOCKER.json
```

This is an MCP/Sysplorer call-surface blocker, not a model-check failure. All
four Runner model-quality results remain `not_evaluated`; no simulation,
`Result.msr`, metric, or animation claim was made. Do not restart Sysplorer or
advance to simulation without a fresh healthy probe and a successful bounded
single-Runner check.

P2 live checkpoint 1 supersedes the call-surface blocker for the narrow
Official PID vertical slice. After loading the four project packages by their
absolute `package.mo` paths, all four Runner models passed current
`CheckModel`. The certification runner then completed a real 50-second MWORKS
simulation for `offline_official_pid_climb_v1`, produced 5001 result rows and a
current `Result.msr`, calculated strict metrics, opened the result, plot, model,
and native animation windows, and cleaned up the task-owned session. The
certification status is `accepted`; animation playback is not required by the
frozen acceptance rule.

The canonical checkpoint record is:

```text
Results/control_platform/offline_expansion_goal_20260719/P2_OFFICIAL_PID_LIVE_ACCEPTANCE.json
```

This acceptance is deliberately classified as current-worktree evidence, not
as a frozen-source certification. `Models/QuadrotorControllerBlocks/package.mo`
and `package.order` contain concurrent uncommitted changes owned by another
task. Their exact SHA-256 values are recorded in the checkpoint and those files
must not be staged by this Goal. P2 remains active until the four native output
boundaries have same-version simulation/result evidence and the dependency
state is reproducible from a committed revision.

P2 live checkpoint 2 closes the `ATTITUDE_THRUST` platform fixture's numeric
gate. The first current run exposed an unstable placeholder inner loop. The
Goal retained the blocked runs, aligned the offline position/attitude cascade
and rotor mixer with the accepted official baseline's sign and scale
conventions, added bounded position PD, altitude PID, attitude PD, and command
limits, and used 5-second tuning gates before rerunning the full 50-second
certification. The accepted v6 run ended within 0.008 m of the reference, kept
maximum tilt below 0.12 rad, produced a current `Result.msr`, passed strict
metrics, and opened the native result, plot, model, and animation windows.

The canonical checkpoint record is:

```text
Results/control_platform/offline_expansion_goal_20260719/P2_ATTITUDE_THRUST_LIVE_ACCEPTANCE.json
```

The certification session's final `shutdown` request timed out after evidence
capture. `RemoveAnimations` and `RemovePlots` succeeded before the evidence
windows were opened, but the post-run cleanup retry and read-only probe then
also timed out. Therefore the control/result acceptance is retained while
window/session cleanup remains an explicit blocker; no reusable main window
was force-closed. P2 still requires current `BODY_RATE_THRUST` and `WRENCH`
same-run evidence, plus a healthy cleanup path, before the platform-core phase
can close.

P2 static checkpoint 5 records an exact 16-row Batch A Adapter implementation
queue at `Config/control_platform/offline_batch_a_adapter_backlog.json`. Every
row is derived from the frozen inventory and points to an existing source or
historical MWORKS model anchor. The queue preserves important claim limits,
including `neural_pid` as `zero_untrained`, `ilc` as lifecycle-dependent, and
`px4ctrl` as an external runtime implementation that still needs a separately
defined claim-bounded offline equivalent. Source availability is not counted
as current shared-Runner certification.

P2 live checkpoint 3 prepares the `BODY_RATE_THRUST` candidate without
promoting it to live evidence. The candidate reuses the stable bounded
position-PD and altitude-PID outer loop, converts desired attitude to bounded
body-rate references, estimates measured rates from plant attitude, and closes
the offline rate loop through the dedicated allocator. The four-boundary
interface checker passed, the targeted certification tests passed `9/9`, and
the three-file diff passed Git whitespace checks.

The required read-only Sysplorer `session_manager(probe)` then returned no
response for approximately 60 seconds and was terminated. No `ensure`, restart,
force restart, GUI action, model load, `CheckModel`, or simulation was attempted.
The exact blocker record is:

```text
Results/control_platform/offline_expansion_goal_20260719/P2_BODY_RATE_THRUST_LIVE_BLOCKER.json
```

Therefore the current candidate remains source/static-only. It has no current
MWORKS model-quality result, `Result.msr`, metrics, plot, or native animation
evidence. Resume only after an independently healthy read-only probe, then
check this Runner alone and use a five-second bounded simulation before the
full 50-second certification. P2 and the long Goal remain active.

P2 live checkpoint 4 supersedes that blocker for the recorded current
worktree. A fresh read-only probe returned healthy, the four existing packages
were loaded without source mutation, and `BodyRateThrustRunner` passed its
single-model `CheckModel`. A dedicated five-second Wrapper then completed 501
finite samples with 0.0047 m terminal error, less than 0.00031 rad maximum
absolute attitude, and no unstable flip.

The unchanged 50-second certification subsequently passed all frozen platform
gates: 5001 samples, current `Result.msr`, strict metrics, result/plot/model
windows, the native animation window, bounded closed-loop checks, and
task-owned session shutdown. Terminal position error was below 0.003 m and
maximum tilt was below 0.14 rad. The 33 reported constraint samples are retained
as startup altitude samples below the shared 0.10 m minimum-altitude metric;
there were zero tilt violations. This fixture is not promoted as a competition
controller performance result.

The certification subprocess recorded a successful shutdown of its dedicated
task-owned session. A subsequent read-only probe against the separate primary
MCP session did not return within 30 seconds and was terminated without
recovery or window action. This does not invalidate the completed same-run
artifacts or dedicated shutdown, but it restores the healthy-probe hard gate
before any `WRENCH` live work begins.

The canonical checkpoint record is:

```text
Results/control_platform/offline_expansion_goal_20260719/P2_BODY_RATE_THRUST_LIVE_ACCEPTANCE.json
```

The loaded `QuadrotorControllerBlocks/package.mo` and `package.order` still
contain concurrent uncommitted changes owned by another task, so their exact
hashes are recorded and this remains current-worktree evidence rather than a
frozen-source certification. P2 remains active: `WRENCH` still needs the same
current model/check/simulation/result/animation proof, and all four boundary
fixtures need a final cleanup-health reconciliation before phase closure.

P2 static checkpoint 6 prepares the `WRENCH` fixture as a separate boundary
rather than wiring another Runner through an implicit conversion. The
Controller folds the already accepted position-PD, altitude-PID,
attitude-to-rate cascade, and rate damping into the declared legacy-scaled
`body_force/body_torque` outputs. The dedicated Allocator applies the accepted
four-rotor sign and scale convention. This does not claim verified newtons or
newton-meters; the existing interface contract keeps physical-unit mapping
explicitly unverified.

The four-boundary checker passed and the targeted offline Runner/Profile tests
passed `26/26`. The required fresh read-only Sysplorer probe then returned no
response within 30 seconds and was terminated. No recovery, reload,
`CheckModel`, simulation, window, or result operation followed. The checkpoint
record is:

```text
Results/control_platform/offline_expansion_goal_20260719/P2_WRENCH_LIVE_BLOCKER.json
```

The WRENCH candidate is therefore source/static-only at this checkpoint. It
must resume from a healthy probe, a single-Runner model check, and a five-second
numeric gate before the full certification. P2 and the long Goal remained
active at that checkpoint.

Blocked audit checkpoint: the same primary MCP/Sysplorer read-only probe
timeout then repeated in a third consecutive Goal turn. The final attempt was
terminated after 30 seconds with no `health`, `ensure`, restart, force restart,
GUI action, or model operation. Because live WRENCH work cannot proceed without
bypassing the declared healthy-probe gate, the long Goal transitions to
`blocked` at this checkpoint. Resume requires an independently restored call
surface and a fresh successful read-only probe; no accepted earlier boundary is
revoked, and WRENCH remains `not_evaluated` rather than failed.

P2 live checkpoint 5 supersedes the WRENCH blocked audit for this continuation.
The restored Sysplorer call surface passed a fresh read-only probe and health
check (`api_ready=true`). The four existing packages were loaded without source
mutation, and `MoSimQuadrotorModel.ExperimentRunner.Runners.WrenchRunner`
passed a single-model `CheckModel`.

The dedicated WRENCH certification then completed a real 50-second MWORKS
simulation with 5001 samples. It produced a current `Result.msr`, strict
metrics, result/plot/model windows, and a native animation window; playback is
not required by the acceptance rule. The dedicated task session shutdown was
recorded as successful. Terminal position error was `0.00263 m`, maximum
position error was `1.1769 m`, maximum tilt was `0.1383 rad`, and the result
contained no NaN/Inf values. The 33 constraint samples are retained as startup
samples below the shared 0.10 m altitude threshold; tilt violations were zero.

The canonical checkpoint record is:

```text
Results/control_platform/offline_expansion_goal_20260719/P2_WRENCH_LIVE_ACCEPTANCE.json
```

This closes the WRENCH platform-fixture gate for the recorded current
worktree. It does not claim competition-controller performance, code
generation, PX4, Gazebo, ROS1, online co-simulation, or flight evidence. The
next gate is `ROTOR_COMMAND`, followed by four-boundary regression and later
APP/batch integration; the three model directories remain unmoved.

P7 static checkpoint 1 adds the allowlisted offline batch runner and connects
the APP's offline MIL action to it. The runner executes only single-UAV
Certified Profiles from `offline_composition_catalog.json`, stops on the first
blocker, and writes one `BATCH_MANIFEST.json` plus per-run stdout/stderr logs.
Disabled Profiles, direct multi-UAV models, and unknown Profile IDs fail closed.
Generated run artifacts remain under `Results/`; no generated Wrapper is
written into the model source tree. The APP records the resulting manifest
path and keeps disabled Profiles from starting a run.

The targeted batch tests, offline inventory/composition/Runner checkers, and
Julia syntax parsing all pass. This is orchestration and UI integration only;
it does not turn historical or prior certification records into new MWORKS
evidence. A real batch run still requires a healthy MWORKS session and must
produce current `Result.msr` and window evidence per the contract.

P2 live checkpoint 6 records the four-boundary regression audit and the next
ATTITUDE retry. The audit currently reports:

```text
ATTITUDE_THRUST  blocked: task_owned_session_cleanup_missing
BODY_RATE_THRUST accepted_current_worktree
WRENCH           accepted_current_worktree
ROTOR_COMMAND    accepted
```

The audit file is:

```text
Results/control_platform/offline_expansion_goal_20260719/P2_FOUR_BOUNDARY_REGRESSION.json
```

The ATTITUDE retry used a new run ID and the original fixture request, but its
independent certification MCP client timed out while calling
`session_manager(health)` for 180 seconds before model load. It produced no
new model check, simulation, `Result.msr`, result-window, or animation claim.
The blocker is recorded at:

```text
Results/control_platform/offline_expansion_goal_20260719/P2_ATTITUDE_THRUST_LIVE_BLOCKER_V7.json
```

The direct current MCP health check immediately afterward still returned
`driver_ready=true` and `api_ready=true`; this distinguishes the failed
independent client startup from a proven model or license failure. P2 remains
active and the four-boundary regression remains blocked until ATTITUDE has a
fresh accepted run with task-owned session cleanup.

P2 live checkpoint 7 supersedes the ATTITUDE cleanup blocker. After the
current dedicated session on port `49152` was shut down, a fresh independent
certification run completed successfully:

```text
Results/mworks_generated_profiles/goal-p2-attitude-thrust-fixture-20260719-v8/CERTIFICATION.json
```

The run passed model load, `CheckModel`, the 50-second MWORKS simulation with
5001 samples, current `Result.msr`, strict result checks, result/plot/model/
animation-window creation, and task-owned session shutdown. Playback was not
required. The resulting four-boundary regression is now accepted; this closes
the platform-boundary fixture gate only and does not claim controller,
code-generation, PX4, Gazebo, ROS1, online co-simulation, or flight evidence.

P7 live checkpoint 2 validates the APP batch backend through one real
single-profile run. The allowlisted `offline_official_pid_climb_v1` profile
completed through the batch runner with a current MWORKS model check,
simulation, `Result.msr`, metrics, result/animation windows, and task-owned
session cleanup. The batch wrote `BATCH_MANIFEST.json`, retained per-run
stdout/stderr logs, and returned `status=accepted` without touching the model
source tree. The checkpoint is:

```text
Results/control_platform/offline_expansion_goal_20260719/P7_BATCH_LIVE_ACCEPTANCE.json
```

This proves one real batch path, not all eight Certified Profiles or the full
APP UI runtime. Remaining P7 work is batch failure/retry/result-management
coverage and then the broader Certified/Custom Profile batches.

P7 static checkpoint 3 closes the first failure-attribution gap in the batch
surface. The batch directory is now created before Profile resolution, so an
unknown, disabled, multi-UAV, or direct-model Profile writes a blocked
`BATCH_MANIFEST.json` with its exact reason and exits with code `2` without
starting MWORKS. A child certification failure also remains blocked with its
return code and logs. Model Studio preserves the expected manifest path on
both success and failure and exposes that path through the result action.
This is failure recording and result attribution only; it does not certify an
additional controller or change any realtime, ROS1, PX4, Gazebo, or QGC asset.

The immediate post-checkpoint read-only Sysplorer `session_manager(probe)` did
not return within approximately 30 seconds and was terminated under the
bounded-wait rule. No ensure, reconnect, restart, model load, check, simulation,
or window action followed. This does not invalidate the completed static P7
checkpoint, but it keeps the healthy-probe gate closed before the next live
MWORKS batch. The blocker record is:

```text
Results/control_platform/offline_expansion_goal_20260719/P7_MWORKS_PROBE_BLOCKER_V2.json
```

P7 static checkpoint 4 adds rerun lineage and a self-rebuilding result index.
`--retry-batch-id` reads the source batch's requested Profiles, creates a new
batch directory, and records `root_batch_id`, `retry_of`, and `attempt` in the
new manifest; the source batch is never overwritten. Every terminal manifest
also rebuilds the runtime-only `Results/control_platform/offline_batches/
BATCH_INDEX.json` atomically, including accepted/blocked counts, latest batch,
manifest paths, and index errors. Model Studio uses the previous batch as the
source for a same-Profile rerun and exposes both the manifest and index paths.
This remains batch orchestration evidence only; it does not imply a new live
MWORKS certification or alter the real-time lane.
