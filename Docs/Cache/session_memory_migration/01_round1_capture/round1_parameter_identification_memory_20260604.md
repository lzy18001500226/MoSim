# Round 1 Parameter Identification Memory Cache

Date: 2026-06-04 CST

Scope: first cache pass for long-session memory about Sunray150 physical
parameters, PX4 ULog identification, SDF-migration seeds, and MWORKS parameter
mapping. This is cache-only and does not promote any numeric parameter as
identified truth.

## Status

```text
round: 1
topic: Sunray150 parameter identification
status: candidate_cache_created
risk: high
formal_docs_patched_this_round: none
cache_only: true
sources_re_read:
  - Docs/Workflows/identify_quadrotor_parameters.md
  - Docs/Design/02_模型接口与运行流程.md
  - Docs/Design/03_控制系统架构.md
  - Docs/Design/07_场景扰动与测试矩阵.md
  - Docs/Workflows/agent_task_ledger.md
  - PROGRESS.md
```

## Candidate Items

### PARAM-MEM-001 - Current Parameters Are SDF Migration Seeds

```text
round: 1
status: candidate
risk: high
candidate_statement:
  Current Sunray150 mass, inertia, rotor position, and motor/lift coefficient
  values used in the project must remain labeled as SDF-migration or baseline
  simulation seeds unless a PX4 ULog / bench identification bundle upgrades
  them.
known_sources:
  - `Docs/Workflows/identify_quadrotor_parameters.md` says the workflow is not
    a claim that current parameters are already identified from real flight
    data.
  - `Docs/Workflows/agent_task_ledger.md` row `PARAM-20260521-PX4-IDENT`
    states that current `1.0 kg`, inertia, and `motorConstant/lift_cofficient`
    values must be labeled `source=SDF_migration`, not Sunray150 identified
    truth.
  - `Docs/Design/02_模型接口与运行流程.md` distinguishes `identified` from
    `sdf_migrated`.
contradictions_or_history:
  Old chat and old model notes contain numeric values that may look final.
  They are not final identified parameters.
current_evidence_needed:
  For round 2, re-read the exact model fields and latest parameter workflow
  sections, then verify whether any real ULog evidence has been added.
formal_target_if_promoted:
  Mostly already formalized in `Docs/Workflows/identify_quadrotor_parameters.md`
  and `Docs/Design/02_模型接口与运行流程.md`.
next_round_action:
  Round 2 should confirm no newer identified YAML/evidence bundle exists before
  this is marked `round2_verified`.
```

### PARAM-MEM-002 - Identified Truth Requires A Full Evidence Bundle

```text
round: 1
status: candidate
risk: high
candidate_statement:
  A Sunray150 parameter set can be called `identified` only after the project
  has raw PX4 `.ulg` logs, PX4 `.params`, exact takeoff mass, motor order,
  rotor direction, motor/prop/ESC context, identification output, held-out
  validation, and MWORKS verification evidence.
known_sources:
  - `Docs/Workflows/identify_quadrotor_parameters.md` lists required ULog
    fields, data quality gates, excitation flights, output YAML format, and
    required user/vendor inputs.
  - `PROGRESS.md` says the next useful package is RC-collected PX4 `.ulg`
    logs plus `.params`, exact takeoff mass, motor order, and motor/prop/ESC
    info.
  - `Docs/Workflows/agent_task_ledger.md` says parameters must not be upgraded
    from `source=SDF_migration` to `identified` until held-out validation
    passes.
contradictions_or_history:
  Public hardware specs, reference repository configs, and PX4/Gazebo Iris
  values are useful priors but not Sunray150 identified truth.
current_evidence_needed:
  Check for `Results/identification/sunray150/**/parameters/*.yaml`,
  matching raw `.ulg` logs, fit reports, and MWORKS verification logs.
formal_target_if_promoted:
  `Docs/Workflows/identify_quadrotor_parameters.md` or a result manifest under
  `Results/identification/sunray150/`.
next_round_action:
  Round 2 should perform a path-limited search for identification evidence and
  classify the current state as `no_identified_bundle`, `partial_bundle`, or
  `identified_bundle_present`.
```

### PARAM-MEM-003 - Numeric Seeds Are High-Risk Cache Pointers

```text
round: 1
status: candidate
risk: high
candidate_statement:
  Numeric values such as `mass=1.0 kg`, `Ixx/Iyy/Izz=0.0085/0.0085/0.012`,
  rotor positions around `(±0.065, ±0.065, -0.025) m`, SDF motor constant
  `8.54858e-06`, and MWORKS `lift_cofficient` conversions are audit pointers
  and baseline seeds, not final physical truth.
known_sources:
  - `Docs/Workflows/identify_quadrotor_parameters.md` lists these as current
    risk parameters and marks the example YAML values as placeholders or SDF
    migration seeds until ULog identification is complete.
  - Multiple `Models/QuadrotorExperiments/*.mo` files describe hover command
    scaling before Sunray150 SDF motorConstant calibration.
contradictions_or_history:
  Long-session history repeatedly refined geometry, propeller, and material
  values; this makes direct promotion of numeric parameters especially risky.
current_evidence_needed:
  Re-read current model fields and current Sunray/MWORKS geometry source before
  moving any number into formal docs.
formal_target_if_promoted:
  Only a result manifest or identified parameter YAML after evidence exists.
next_round_action:
  Round 2 should list exact current model locations and classify each numeric
  seed by provenance.
```

### PARAM-MEM-004 - No Current Real ULog Evidence In Repository

```text
round: 1
status: candidate
risk: high
candidate_statement:
  Current workflow evidence says no YunZong/Sunray real ULog files are present
  in the repository; only reference/sample ULog-like material exists.
known_sources:
  - `Docs/Workflows/identify_quadrotor_parameters.md` current audit result
    says no real Sunray/YunZong ULog files are present and current MWORKS
    parameter values must remain `source=SDF_migration`.
contradictions_or_history:
  If later user uploads real logs, this cache item becomes stale and must be
  rechecked before any answer.
current_evidence_needed:
  Round 2 path-limited search under `Results/identification/`, `References/Data`,
  and approved project data directories.
formal_target_if_promoted:
  None unless a short recovery pointer is missing; the workflow already records
  this boundary.
next_round_action:
  Verify the current absence/presence of real logs without scanning personal or
  external directories.
```

### PARAM-MEM-005 - Parameter Identification Is Long-Running Work

```text
round: 1
status: candidate
risk: medium
candidate_statement:
  PX4-log-based Sunray150 parameter identification is a long-running
  high-context task. It should not be delegated to disposable subagents or
  concluded with only "parameters are wrong".
known_sources:
  - `PROGRESS.md` mistakes-to-avoid section says long-running high-context
    tasks such as Sunray150 parameter identification need dedicated task
    conversations and that the result must include data, log fields, estimator
    route, MWORKS mapping, and validation plan.
  - `Docs/Workflows/agent_task_ledger.md` keeps
    `PARAM-20260521-PX4-IDENT` as done for workflow research, with next step
    data collection and identification execution.
contradictions_or_history:
  Prior work correctly produced the workflow, but no evidence indicates the
  actual flight-data identification is complete.
current_evidence_needed:
  Round 2 should confirm current task state in the ledger and decide whether a
  new active data-collection task is needed.
formal_target_if_promoted:
  Existing ledger and operating-model docs, not parameter design docs.
next_round_action:
  Classify this as already represented or as a new task-row candidate.
```

## Rejected Or Superseded Historical Items

```text
REJ-PARAM-001:
  Treating `1.0 kg`, SDF inertia, or SDF motor constants as measured
  Sunray150 truth is rejected.

REJ-PARAM-002:
  Copying PX4 Iris, ETH sample, or reference repository parameters into
  Sunray150 as final values is rejected.

REJ-PARAM-003:
  Calling a parameter fit "identified" without held-out validation and MWORKS
  verification is rejected.

REJ-PARAM-004:
  Treating public hardware specs as a substitute for weighing the exact
  battery/MID-360/guard/payload configuration is rejected.
```

## Round 2 Backlog

1. Search project-local identification output paths for real `.ulg`, `.params`,
   identified YAML, fit reports, and MWORKS verification logs.
2. Re-read current model fields that consume mass, inertia, rotor positions,
   `lift_cofficient`, and command-scaling factors.
3. Compare current design/workflow docs for the same evidence boundary.
4. Mark each cache item as `round2_verified`, `superseded`, or
   `needs_user_review`.

## Do Not Promote Yet

- Any numeric Sunray150 physical parameter as identified truth.
- Any claim that ULog-based identification has been run.
- Any model change based only on old chat values.
- Any upgrade from `source=SDF_migration` to `source=PX4_ULog_sysid` without a
  complete evidence bundle.
