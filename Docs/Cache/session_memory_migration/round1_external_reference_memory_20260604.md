# Round 1 External Reference Memory Cache

Date: 2026-06-04 CST

Scope: first cache pass for long-session memory about external repositories,
RflySim/AirSim/PX4/Gazebo/Sunray/FAST-LIO learning, and reference-versus-runtime
boundaries. This is cache-only. It does not promote any third-party repository
as a current MoSim runtime dependency or completed integration.

## Status

```text
round: 1
topic: external reference learning and reuse boundaries
status: candidate_cache_created
risk: medium
formal_docs_patched_this_round: none
cache_only: true
source_pointers_re_read:
  - Docs/Index/external_learning_index.md
  - Docs/Workflows/audit_external_repo.md
  - CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md
  - Results/unreal_scene_mapping/REAL_UAV_STACK_REUSE_MATRIX_20260602.md
  - Results/unreal_scene_mapping/REAL_UAV_STACK_SOURCE_AUDIT_20260602.md
```

Round 2 must still perform a focused verification pass before any formal
promotion. In particular, re-read the current reference index, audit workflow,
runtime status files, and target workflow/design docs in the same round that
decides whether an item is verified, rejected, superseded, or ready for round 3.

## Candidate Items

### EXTREF-MEM-001 - Reference Index Before Raw Tree Search

```text
round: 1
status: candidate
risk: medium
candidate_statement:
  External learning should start from
  `CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md` and
  `Docs/Index/external_learning_index.md`, not from broad ad-hoc searches over
  raw `References/` trees.
known_sources:
  - `CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md` says to use it before
    searching raw external trees.
  - `Docs/Index/external_learning_index.md` says external learning improves
    local workflows, not wholesale runtime adoption.
  - `Docs/Workflows/audit_external_repo.md` requires path confirmation,
    classification, risk recording, and source-to-doc coverage.
contradictions_or_history:
  Long-session work sometimes explored many external repos quickly. That history
  is useful as a locator, but raw tree search is not the durable recovery route.
current_evidence_needed:
  Round 2 should run or re-read the current reference-index validation route and
  check whether any newer index file supersedes these entry points.
formal_target_if_promoted:
  Usually already formalized in the external learning index and audit workflow.
next_round_action:
  Classify as already-formalized or add a narrow pointer if a workflow target
  lacks the recovery route.
```

### EXTREF-MEM-002 - External Repos Improve Local Rules, Not Runtime By Default

```text
round: 1
status: candidate
risk: medium
candidate_statement:
  AirSim, RflySim, PX4, Gazebo, Sunray, FAST-LIO, EGO-Planner, and agent-system
  repositories may provide architecture contracts, API shapes, workflow
  patterns, tests, or rejected-pattern memory. They must not become direct
  MoSim runtime dependencies unless a specific integration is approved and
  locally built, checked, and evidenced.
known_sources:
  - `Docs/Index/external_learning_index.md` defines `patch` versus `no_patch`
    audit outcomes and rejects wholesale third-party runtime adoption.
  - `Docs/Workflows/audit_external_repo.md` requires classification of usable
    parts, not usable parts, integration recommendation, and next validation.
  - `Results/unreal_scene_mapping/REAL_UAV_STACK_REUSE_MATRIX_20260602.md`
    uses reuse levels such as architecture contract, adapt, adapt later,
    architecture/API reference, patch candidate, and smoke only.
contradictions_or_history:
  Earlier discussions sometimes treated a promising external project as if it
  could be adopted immediately. This cache keeps that as a rejected assumption
  until there is explicit approval and local runtime evidence.
current_evidence_needed:
  Round 2 should compare current formal docs against this boundary and list any
  document that implies direct adoption without evidence.
formal_target_if_promoted:
  `Docs/Index/external_learning_index.md`,
  `Docs/Workflows/audit_external_repo.md`, or a relevant design workflow only
  if a gap is found.
next_round_action:
  Verify current docs already contain the reject-by-default policy; otherwise
  prepare a narrow round-3 patch.
```

### EXTREF-MEM-003 - RflySim Role Split Pattern

```text
round: 1
status: candidate
risk: medium
candidate_statement:
  RflySim is useful as an architecture reference for process/window ownership:
  MoSim should keep MWORKS as dynamics, controller, and truth authority; Unreal
  as rendered-scene and sensor-oracle surface; and ROS2/RViz2 as algorithm and
  robotics-state review surface.
known_sources:
  - `Results/unreal_scene_mapping/REAL_UAV_STACK_REUSE_MATRIX_20260602.md`
    records this split as a MoSim action.
  - `Results/unreal_scene_mapping/REAL_UAV_STACK_SOURCE_AUDIT_20260602.md`
    maps RflySim motion/control, UE rendering/perception, and ROS review into
    the MoSim split.
  - `AGENTS.md` Unreal mapping window rule preserves separate UE and RViz/RViz2
    review responsibilities.
contradictions_or_history:
  Old browser/HTML point-cloud and static preview routes can blur the review
  surfaces. They are not accepted as active map/localization review surfaces.
current_evidence_needed:
  Round 2 should re-read `Docs/Workflows/unreal_renderer.md`,
  `Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md`, and the latest runtime
  artifacts to confirm this is still the active role split.
formal_target_if_promoted:
  Likely `Docs/Workflows/unreal_renderer.md` or architecture doc only if the
  split is missing or stale.
next_round_action:
  Treat as an architecture boundary candidate, not proof that all three runtime
  surfaces are currently healthy.
```

### EXTREF-MEM-004 - PX4/Sunray Contracts Are Behavior References

```text
round: 1
status: candidate
risk: medium
candidate_statement:
  PX4 Offboard and Sunray/YunZong control sources provide behavior contracts:
  continuous setpoint streaming, stale-command timeout, odometry validity,
  geofence, takeoff/hover/land/kill states, and separation of control rates
  from display rates. These semantics should be adapted into MoSim command or
  controller adapters rather than copied as a ROS1/MAVROS runtime requirement.
known_sources:
  - `Results/unreal_scene_mapping/REAL_UAV_STACK_REUSE_MATRIX_20260602.md`
    classifies PX4 as an architecture contract and Sunray control as adapt.
  - `Results/unreal_scene_mapping/REAL_UAV_STACK_SOURCE_AUDIT_20260602.md`
    cites Sunray `externalFusion.cpp`, `UAVControl.cpp`, command timeout,
    geofence, takeoff/hover/landing/emergency kill, and 20Hz command mapping.
contradictions_or_history:
  Treating ROS1/MAVROS as a first production dependency for MoSim was rejected
  in the reuse matrix. A PX4 route would require version-aware message/runtime
  work and is not the first minimum loop.
current_evidence_needed:
  Round 2 should verify the current controller adapter and architecture docs
  before claiming any specific behavior is implemented.
formal_target_if_promoted:
  `Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md`,
  `Docs/Workflows/unreal_renderer.md`, or a controller-adapter workflow.
next_round_action:
  Separate "desired contract" from "implemented and tested behavior".
```

### EXTREF-MEM-005 - Livox Mid360 / FAST-LIO Evidence Boundary

```text
round: 1
status: candidate
risk: high
candidate_statement:
  Sunray Mid360, FAST-LIO, and Livox references define a strict evidence
  boundary: a visible `PointCloud2` or static cloud is display evidence only.
  FAST-LIO claims require a selected local runtime to parse the actual LiDAR/IMU
  contract and publish nonzero registered cloud, odometry, and path with truth
  error evaluation.
known_sources:
  - `Results/unreal_scene_mapping/REAL_UAV_STACK_REUSE_MATRIX_20260602.md`
    requires MWORKS truth, 200Hz IMU, 10Hz Mid360 baseline, per-point timing,
    TF/extrinsics, FAST-LIO outputs, and local 3D map.
  - `Results/unreal_scene_mapping/REAL_UAV_STACK_SOURCE_AUDIT_20260602.md`
    rejects visible `PointCloud2` as FAST-LIO evidence unless the runtime
    actually parses the chosen Livox route.
  - Existing round-1 ROS2 cache records contradictions between older FAST-LIO
    compatibility scans and later `spark-fast-lio` runtime status.
contradictions_or_history:
  Earlier keyboard/grid/static-cloud demos, 2D `OccupancyGrid` surfaces, and
  RViz point-size tuning are smoke-only or rejected as product evidence.
current_evidence_needed:
  Round 2 should re-read latest `FASTLIO_RUNTIME_STATUS.md`,
  `FASTLIO_FACTORY_FAILURE_DIAGNOSIS.md`, current runtime-env reports, and any
  current `*_CURRENT` gates before stating FAST-LIO status.
formal_target_if_promoted:
  Likely already in architecture/runtime docs; only patch if the display versus
  localization boundary is unclear.
next_round_action:
  Coordinate with the ROS2 runtime round-2 verification cache before any
  promotion or rejection.
```

### EXTREF-MEM-006 - Keyboard/Grid/Static Cloud Route Is Rejected Or Smoke-Only

```text
round: 1
status: rejected
risk: high
candidate_statement:
  The keyboard/grid-cell movement, static point-cloud, 2D-only map, HTML
  point-cloud, and display-parameter-tuning route must not be resumed as the
  product path. It is at most smoke plumbing evidence.
known_sources:
  - `Results/unreal_scene_mapping/REAL_UAV_STACK_SOURCE_AUDIT_20260602.md`
    records the user correction rejecting grid-cell motion, direct pose
    overwrite, static/fake point clouds, and 2D-only accepted review.
  - `Results/unreal_scene_mapping/REAL_UAV_STACK_REUSE_MATRIX_20260602.md`
    marks the current keyboard/grid mapping loop as smoke only.
  - `AGENTS.md` Unreal mapping window rule says browser HTML is not accepted
    active point-cloud/map review surface.
contradictions_or_history:
  Old demos and generated artifacts may still exist and may be useful for
  plumbing checks. They must not be described as current localization, mapping,
  planning, or controller evidence.
current_evidence_needed:
  Round 2 should verify any current docs or report drafts do not present those
  outputs as final evidence.
formal_target_if_promoted:
  Rejected-pattern lists in `Docs/Workflows/unreal_renderer.md` or cache-only if
  already covered.
next_round_action:
  Keep as anti-regression memory and do not promote except as a rejected route.
```

### EXTREF-MEM-007 - Sunray Provides Local Patterns, Not Automatic Acceptance

```text
round: 1
status: candidate
risk: high
candidate_statement:
  Sunray local sources are important references for `external_fusion`,
  `sunray_control_node`, Mid360/FAST-LIO launch shape, EGO planner 3D local map,
  and `positionCmd2sunray`. They do not automatically validate MoSim asset
  placement, material appearance, ROS runtime status, or controller performance.
known_sources:
  - `Results/unreal_scene_mapping/REAL_UAV_STACK_SOURCE_AUDIT_20260602.md`
    lists concrete Sunray source files and reusable details.
  - Existing Sunray150 round-2 cache and parameter round-1 cache warn that
    geometry/material/parameter values are high-risk and must be rechecked.
contradictions_or_history:
  Long-session history includes many wrong or superseded Sunray150 assembly and
  material attempts. The source chain matters, but final visual/numeric claims
  still require current manifests and manual review.
current_evidence_needed:
  Round 2 should cross-check with Sunray150 asset/parameter caches and current
  manifests before any statement about accepted geometry or materials.
formal_target_if_promoted:
  Asset workflow, renderer workflow, or a source-chain evidence doc only after
  current evidence review.
next_round_action:
  Keep architecture/source-chain lessons separate from high-risk visual and
  numeric claims.
```

### EXTREF-MEM-008 - Agent/Skill References Are Workflow Inputs Only

```text
round: 1
status: candidate
risk: medium
candidate_statement:
  External agent, skill, MCP, and workflow repositories can inform MoSim
  documentation, orchestration, audit, review, and recovery patterns, but their
  provider configs, credential flows, runtime services, and UI stacks must not
  be imported as project requirements without explicit approval.
known_sources:
  - `Docs/Index/external_learning_index.md` lists agent-system source families,
    useful patterns, and rejected patterns.
  - `Docs/Workflows/audit_external_repo.md` requires provider-specific schema
    verification and rejects unverified tool schemas or configs.
  - Existing CoAgent round-1 cache says design-only docs do not authorize broad
    runtime/tool expansion.
contradictions_or_history:
  Long-session discussion included many MCP/skills/plugin recommendations.
  Installed or researched tools should not become MoSim runtime dependencies
  merely because they were useful for one infrastructure repair.
current_evidence_needed:
  Round 2 should re-read CoAgent status and external learning docs before any
  formal claim about approved agent tooling.
formal_target_if_promoted:
  `Docs/Index/external_learning_index.md`,
  `Docs/Workflows/audit_external_repo.md`, or CoAgent decision/status docs only
  if a current gap exists.
next_round_action:
  Coordinate with CoAgent operating round-2 cache; reject provider config or
  credential assumptions unless explicitly approved and verified.
```

## Round 2 Verification Backlog

```text
must_re_read:
  - Docs/Index/external_learning_index.md
  - Docs/Workflows/audit_external_repo.md
  - CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md
  - Docs/Workflows/unreal_renderer.md
  - Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md
  - Results/unreal_scene_mapping/FASTLIO_RUNTIME_STATUS.md
  - Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_FACTORY_FAILURE_DIAGNOSIS.md
  - CoAgent/STATUS.md if agent/tooling reference claims are involved

promotion_guard:
  - no direct third-party runtime adoption unless explicitly approved
  - no FAST-LIO claim without current runtime evidence
  - no Sunray150 numeric or visual claim without current manifests and review
  - no agent/tool/provider config claim without current approval and schema check
```
