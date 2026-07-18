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
Scripts/quality/build_offline_expansion_inventory.py
Scripts/quality/check_offline_expansion_inventory.py
Scripts/quality/check_offline_composition_catalog.py
Scripts/quality/check_offline_runner_interface_contract.py
Scripts/mworks/generate_offline_profile_wrapper.py
Scripts/tests/test_offline_expansion_inventory.py
Scripts/tests/test_offline_composition_catalog.py
Scripts/tests/test_offline_profile_wrapper.py
Scripts/tests/test_offline_runner_interface_contract.py
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
