# Round 2 Parameter Identification Memory Audit

Date: 2026-06-04 CST

Scope: verify long-session memory about Sunray150 physical parameters, SDF
migration seeds, PX4 ULog identification requirements, model-field mapping,
and current evidence absence/presence against project-local files. This is
cache-only. It does not promote any numeric parameter as identified truth.

## Status

```text
round: 2
topic: Sunray150 parameter identification
status: mixed_round2_verified_and_needs_round3
risk: high
formal_docs_patched_this_round: none
cache_only: true
external_data_paths_read: none
```

This round searched only project-local paths. It did not inspect personal
directories, external flight-log folders, or hardware-connected storage.

## Sources Re-Read

| Source | Finding |
|---|---|
| `Docs/Workflows/identify_quadrotor_parameters.md` | Formal workflow states current parameters are not already identified from real flight data, defines required ULog bundle, identifies current seeds, and records no real YunZong/Sunray ULog files in the repository. |
| `Docs/Design/02_模型接口与运行流程.md` | Distinguishes `identified`, `sdf_migrated`, `reference_only`, and `scenario_override`; says current mass/inertia/rotor/lift parameters cannot be claimed as PX4 ULog identification. |
| `Docs/Design/03_控制系统架构.md` | Says controller tuning must record parameter provenance and current nominal mass/inertia/rotor/motor values remain `source=SDF_migration`. |
| `Docs/Design/07_场景扰动与测试矩阵.md` | Says robustness/mass/fault scenarios use `source=SDF_migration` nominal parameters until identification is complete. |
| `Models/QuadrotorExperiments/Sunray150UEFactoryLinearMPCSysblockSmoke.mo` | Current experiment uses hover-command scaling comments tied to Sunray150 SDF motorConstant calibration and `rotorVelocitySlowdownSim`. |
| `Models/QuadrotorExperiments/Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop.mo` | Same hover-command scaling pattern appears in planning experiments. |
| Project-local search under `Results/` | No `Results/identification/`, `.ulg`, `.params`, `sunray150_identified.yaml`, `fit_report`, `residual_summary`, or `mworks_check` identification bundle was found in this pass. |
| Project-local search for `References/Data` | `References/Data` was not present in the current visible project tree during this pass, although formal docs describe it as an auxiliary route from earlier/local reference planning. |

## Round 2 Findings

### PARAM-MEM-001 - Current Parameters Remain SDF Migration Seeds

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  Current Sunray150 mass, inertia, rotor geometry, motor/lift coefficient, and
  related values must remain labeled as SDF migration or baseline simulation
  seeds unless a complete PX4 ULog / bench identification bundle is added.
current_evidence:
  - `Docs/Workflows/identify_quadrotor_parameters.md` explicitly says the
    workflow is not a claim that current parameters are already identified.
  - `Docs/Design/02_*` says current parameters are usable for simulation
    baseline and sensitivity analysis but cannot be called PX4 ULog
    identification results.
  - `Docs/Design/03_*` says current nominal mass, inertia, rotor position, and
    motor coefficients remain `source=SDF_migration`.
contradictions_or_history:
  Old chat and model notes contain many numeric values. Those values are
  useful pointers only, not identified truth.
formal_target_if_promoted:
  Already represented in parameter workflow and design docs.
next_round_action:
  Round 3 can mark already formalized unless a result/report doc currently
  mislabels these values as identified.
```

### PARAM-MEM-002 - Identified Truth Requires A Full Evidence Bundle

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  A parameter set may be called `identified` only with raw PX4 `.ulg` logs,
  `.params`, exact takeoff configuration context, identification output,
  held-out validation, and MWORKS verification evidence.
current_evidence:
  - `identify_quadrotor_parameters.md` defines minimum output under
    `Results/identification/sunray150/<date_or_run_id>/` with raw logs,
    processed windows, metrics, parameters, command logs, and MWORKS checks.
  - `Docs/Design/02_*` defines `identified` as PX4 ULog identified with
    held-out log and MWORKS check evidence.
contradictions_or_history:
  Public specs, SDF values, reference repository samples, and ordinary
  simulation success are not enough to upgrade provenance.
formal_target_if_promoted:
  Already represented in workflow/design docs.
next_round_action:
  Round 3 can mark already formalized; if an evidence bundle appears later,
  verify it before updating this cache.
```

### PARAM-MEM-003 - Numeric Seeds Are High-Risk Pointers

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  Numeric values such as `mass=1.0 kg`, `Ixx/Iyy/Izz=0.0085/0.0085/0.012`,
  rotor positions around `(+-0.065,+-0.065,-0.025) m`, SDF motor constant
  `8.54858e-06`, and MWORKS `lift_cofficient` conversions are current
  seed/audit values, not final identified physical truth.
current_evidence:
  - `identify_quadrotor_parameters.md` lists these as current known
    Sunray/MWORKS seed values and marks them SDF migration or high risk.
  - `Docs/Workflows/unreal_renderer.md` contains the same rotor-coordinate
    source-chain/visual audit values for geometry, not dynamics truth.
  - Current experiment models include hover speed conversion comments:
    physical Sunray150 motor speed is 10x visual rotor speed by
    `rotorVelocitySlowdownSim`.
contradictions_or_history:
  Geometry visual acceptance, SDF seed values, and controller smoke results can
  be confused with measured dynamics. They must stay provenance-labeled.
formal_target_if_promoted:
  No formal numeric promotion target until an identified parameter YAML exists.
next_round_action:
  Round 3 should keep numeric seeds cache-only unless correcting a mislabeled
  report sentence.
```

### PARAM-MEM-004 - No Current Project-Local Identification Bundle Was Found

```text
round: 2
status: round2_verified_no_identified_bundle_found
risk: high
candidate_statement:
  This migration pass found no project-local Sunray150 identification evidence
  bundle under the expected result paths.
current_evidence:
  - `rg --files Results | rg -i '(^Results/identification/|\\.ulg$|\\.params$|sunray150_identified|fit_report|residual_summary|mworks_check)'`
    returned no matching files.
  - `Docs/Workflows/identify_quadrotor_parameters.md` current audit result
    says no YunZong/Sunray real ULog files are present in the repository and
    current MWORKS values must remain `source=SDF_migration`.
contradictions_or_history:
  If the user later uploads logs or stores them outside the project, this item
  becomes stale. It is only a project-local repository state from this round.
formal_target_if_promoted:
  None. Keep cache-only unless a future data-collection task is opened.
next_round_action:
  Round 3 should map as `no_identified_bundle_found_current_round`, not as a
  permanent claim that no logs exist anywhere.
```

### PARAM-MEM-005 - Public/Vendor Data And Geometry Are Priors Only

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  Public Sunray/Livox/CUAV/motor/prop data, SDF/STL geometry, and reference
  repositories are useful priors and sanity checks, not a replacement for
  Sunray150 flight-configuration identification.
current_evidence:
  - `identify_quadrotor_parameters.md` separates public/vendor data,
    geometry, and low-cost identification tiers.
  - It says SDF rotor coordinates are migrated simulator seeds and should be
    cross-checked against STL, real motor-axis measurement, and PX4 motor
    order before changing dynamics or mixer geometry.
contradictions_or_history:
  User-facing reports can be tempted to quote public mass/wheelbase or
  component tables as final. That is rejected unless provenance is clear.
formal_target_if_promoted:
  Existing parameter workflow.
next_round_action:
  Round 3 can mark already formalized.
```

### PARAM-MEM-006 - Parameter Identification Is A Separate Long-Running Task

```text
round: 2
status: round2_verified_for_cache
risk: medium
candidate_statement:
  PX4-log-based Sunray150 identification is a separate high-context task. This
  migration only preserves the route and current evidence boundary; it does not
  run identification.
current_evidence:
  - `identify_quadrotor_parameters.md` defines collection, topic audit,
    sysid, YAML, and MWORKS verification workflow.
  - `Docs/Workflows/agent_task_ledger.md` includes historical parameter
    identification planning and warns not to upgrade values without held-out
    validation.
contradictions_or_history:
  "Parameters are wrong" is not a completed identification result. The next
  actual task needs data, fit, validation, and MWORKS mapping.
formal_target_if_promoted:
  Existing workflow and task ledger.
next_round_action:
  If the user wants actual identification later, create or resume a dedicated
  task from the workflow, not from chat memory.
```

## Rejected Or Superseded Historical Items

| Historical Item | Current Treatment |
|---|---|
| Treating `1.0 kg`, SDF inertia, or SDF motor constants as measured Sunray150 truth | Rejected. |
| Copying PX4 Iris, ETH samples, or reference-repo parameters as final Sunray150 values | Rejected. |
| Calling parameters `identified` without held-out validation and MWORKS verification | Rejected. |
| Treating public hardware specs as a substitute for exact configuration weighing/logs | Rejected. |
| Updating controller gains as if that fixed plant/actuator parameter provenance | Rejected. |

## Round 3 Promotion Candidates

Only these narrow items are candidates for round 3:

1. A provenance reminder if any formal report/evidence doc lacks it:
   current Sunray150 dynamics parameters are `source=SDF_migration`.
2. A no-bundle recovery note:
   this round found no project-local `Results/identification/sunray150/...`
   evidence bundle.
3. A task-routing note:
   real parameter identification should start from
   `Docs/Workflows/identify_quadrotor_parameters.md`.

No numeric parameter is ready for formal promotion from this cache.

## Verification Needed Before Round 3

```text
1. Re-run a project-local evidence search if new logs/results were added.
2. Re-read current model fields before quoting any numeric parameter.
3. Do not read external/personal log folders unless the user explicitly asks.
4. If a bundle exists, verify raw logs, `.params`, selected windows, fit
   report, identified YAML, held-out validation, and MWORKS check.
```
