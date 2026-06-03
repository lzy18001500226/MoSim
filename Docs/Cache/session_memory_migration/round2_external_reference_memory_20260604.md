# Round 2 External Reference Memory Audit

Date: 2026-06-04 CST

Scope: verify long-session memory about external repository learning and
RflySim/AirSim/PX4/Gazebo/Sunray/FAST-LIO reference boundaries against current
project files. This is cache-only. It does not promote any external project,
runtime, or historical result as final MoSim truth.

## Status

```text
round: 2
topic: external reference learning and reuse boundaries
status: mixed_round2_verified_and_needs_round3
risk: medium
formal_docs_patched_this_round: none
cache_only: true
```

## Sources Re-Read

| Source | Finding |
|---|---|
| `Docs/Index/external_learning_index.md` | External learning improves local workflows, rules, skills, and indexes. It explicitly rejects wholesale third-party runtime adoption as the default. |
| `Docs/Workflows/audit_external_repo.md` | External audits must classify usable and not-usable parts, run through three rounds when requested, verify schemas against official/current tooling, and end in `patch` or `no_patch`. |
| `CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md` | Stable entry point for `References/`; use it before raw external-tree searches. |
| `Results/unreal_scene_mapping/REAL_UAV_STACK_REUSE_MATRIX_20260602.md` | Records reuse levels: PX4 as architecture contract, Sunray control as adapt, RflySim as role-split reference, AirSim/Gazebo as API/window references, `spark-fast-lio` as patch candidate, keyboard/grid loop as smoke only. |
| `Results/unreal_scene_mapping/REAL_UAV_STACK_SOURCE_AUDIT_20260602.md` | Records user correction rejecting toy mapping and extracts Sunray control, Mid360, FAST-LIO, and EGO-planner lessons. |
| `Docs/Workflows/unreal_renderer.md` | Formal workflow already records UAV-stack-first route, separate UE/RViz roles, smoke-only keyboard/grid route, scene-source selection, and many FAST-LIO evidence boundaries. |
| `Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md` | Formal design records MWORKS/UE/ROS2 role split and Factory Gate B formal update with current Factory headless pass metrics. |
| `Results/unreal_scene_mapping/FASTLIO_RUNTIME_STATUS.md` | Older 2026-06-01 status: Factory degraded, Derelict passed with warnings. Useful failure history, not the latest Factory status by itself. |
| `Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_FACTORY_FAILURE_DIAGNOSIS.md` | Older/route-specific Factory diagnosis: not claimable under low-density/Velodyne-like or mismatched input contract. Useful as failure history. |
| `Results/unreal_scene_mapping/factoryenvironmentcollect/REALSTACK_MINILOOP_GATE_CURRENT.md` | Current Factory minimum-loop gate is `ready_for_manual_rviz_ue_review`, with nonzero FAST-LIO outputs and pass metrics. |
| `Results/unreal_scene_mapping/factoryenvironmentcollect/runtime_review_bundle.md` | Gate B formal evidence opens manual UE/RViz review; bundle is launch contract, not proof that manual review already ran. |
| `Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_INPUT_CONTRACT.md` | Current dense Mid360 input is `claimable_input_ready`, but spark-fast-lio PointCloud2 Livox support remains false and CustomMsg route is guarded. |
| `CoAgent/STATUS.md` | Current CoAgent gate remains project-local transport/Git/closed-loop implementation; app-server transport, unattended automation, new departments, broad hooks, MCP/tool expansion, credentials, and external config remain gated. |

## Round 2 Findings

### EXTREF-MEM-001 - Reference Index First

```text
round: 2
status: round2_verified_for_cache
risk: medium
candidate_statement:
  External learning should start from the local reference indexes and audit
  workflow, not broad raw-tree searches.
current_evidence:
  - `CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md` states its purpose is to
    answer what is in `References/`, why it is there, and where to look first.
  - `Docs/Index/external_learning_index.md` says new external-repo learning
    threads should classify targets through the reference index first.
  - `Docs/Workflows/audit_external_repo.md` requires confirming project-local
    paths and validating the master index before broad reference-learning.
contradictions_or_history:
  Long-session exploration included broad external scanning. That history is a
  locator only; it is not the durable recovery route.
formal_target_if_promoted:
  Already represented in the index and audit workflow.
next_round_action:
  Round 3 can mark this already formalized unless a target workflow lacks the
  reference-index pointer.
```

### EXTREF-MEM-002 - Reference Or Adapt, Not Direct Runtime Adoption

```text
round: 2
status: round2_verified_for_cache
risk: medium
candidate_statement:
  External projects are reusable as contracts, patterns, and evidence
  boundaries by default. Direct runtime/framework adoption requires a specific
  approved integration plus local build/runtime evidence.
current_evidence:
  - `Docs/Index/external_learning_index.md` says external learning improves
    local workflows and rejects importing third-party runtimes wholesale.
  - `Docs/Workflows/audit_external_repo.md` requires audit outputs listing
    usable parts, not usable parts, license/risk, recommendation, and next
    validation.
  - `REAL_UAV_STACK_REUSE_MATRIX_20260602.md` assigns bounded reuse levels
    rather than global adoption.
contradictions_or_history:
  Promising external repos were sometimes discussed as if they might be used
  directly. That remains unapproved unless a later task explicitly proves it.
formal_target_if_promoted:
  Already mostly represented in external learning/audit workflows.
next_round_action:
  Round 3 should either mark already formalized or add only a short
  "direct adoption requires approval and evidence" pointer if still needed.
```

### EXTREF-MEM-003 - RflySim/AirSim/Gazebo Role Lessons

```text
round: 2
status: round2_verified_for_cache
risk: medium
candidate_statement:
  RflySim, AirSim, and Gazebo are useful for simulator-window, ROS bridge, and
  role-split lessons. MoSim keeps MWORKS as dynamics/controller/truth authority,
  UE as renderer/sensor oracle, and ROS2/RViz2 as robotics middleware and
  review surface.
current_evidence:
  - `REAL_UAV_STACK_REUSE_MATRIX_20260602.md` records RflySim as role-split
    reference and AirSim/Gazebo as architecture/API references.
  - `REAL_UAV_STACK_SOURCE_AUDIT_20260602.md` maps RflySim motion/render/ROS
    separation into the MoSim split.
  - `Docs/Design/09_*` and `Docs/Workflows/unreal_renderer.md` already encode
    the same role split.
contradictions_or_history:
  RflySim packaged scenes and AirSim/Gazebo runtimes are not current editable
  MoSim scene assets or replacement solvers by default.
formal_target_if_promoted:
  Already represented in the architecture/workflow docs.
next_round_action:
  Round 3 should avoid duplicating long role-split text; if anything, promote a
  compact recovery pointer.
```

### EXTREF-MEM-004 - PX4/Sunray Behavior Contracts

```text
round: 2
status: round2_verified_for_cache
risk: medium
candidate_statement:
  PX4 Offboard and Sunray/YunZong provide behavior contracts such as streamed
  setpoints, timeout/failsafe, odometry validity, state-machine handling, and
  control/display rate separation. These are adaptation targets, not proof that
  PX4, MAVROS, Sunray, or EGO-Planner runtime has been adopted.
current_evidence:
  - `REAL_UAV_STACK_REUSE_MATRIX_20260602.md` lists PX4 as architecture
    contract and Sunray control as adapt.
  - `REAL_UAV_STACK_SOURCE_AUDIT_20260602.md` extracts `external_fusion`,
    `sunray_control_node`, command timeout, geofence, takeoff/hover/land/kill,
    Mid360 launch, EGO planner, and `positionCmd2sunray` lessons.
  - `Docs/Design/09_*` records controller/setpoint 20Hz, IMU 200Hz, LiDAR 10Hz
    baseline, and native RViz2 review expectations.
contradictions_or_history:
  ROS1/MAVROS as a first production dependency is rejected in the reuse matrix.
  Future PX4 routes still require version-aware message/runtime work.
formal_target_if_promoted:
  Architecture/workflow docs only if implementation checklists lack the
  behavior-contract wording.
next_round_action:
  Round 3 must keep wording as "contract/adapt" unless current code and tests
  prove a specific behavior is implemented.
```

### EXTREF-MEM-005 - FAST-LIO Status Requires Source Priority

```text
round: 2
status: round2_verified_for_cache_needs_round3_disambiguation
risk: high
candidate_statement:
  FAST-LIO status must be read from the latest matching route, not from one
  old global status file. Current Factory Gate B headless evidence opens manual
  UE/RViz review, while older scan099 and Factory failure files remain
  route-specific failure history.
current_evidence:
  - `FASTLIO_RUNTIME_STATUS.md` is dated 2026-06-01 and says Factory degraded,
    Derelict passed with warnings.
  - `FASTLIO_FACTORY_FAILURE_DIAGNOSIS.md` records a low-density/mismatched
    Factory route as not claimable.
  - `Docs/Design/09_*` records a 2026-06-02 formal Factory Gate B pass.
  - `REALSTACK_MINILOOP_GATE_CURRENT.md` records current status
    `ready_for_manual_rviz_ue_review`, counts `odometry=80`, `path=8`,
    `registered_cloud=80`, and pass metrics `position_rmse_m=0.39454`,
    `max_position_error_m=0.611542`, `yaw_rmse_rad=0.017802`.
  - `runtime_review_bundle.md` says this is claimable for Factory manual review
    only and not final controller/planner integration.
contradictions_or_history:
  New conversations can easily misread older `FASTLIO_RUNTIME_STATUS.md` or
  failure diagnosis as the latest Factory state. The correct reading is
  time- and route-specific: latest `*_CURRENT` gate first, then runtime review
  bundle, then older blocker/diagnosis files as historical evidence.
formal_target_if_promoted:
  A small status-source-priority note in `Docs/Workflows/unreal_renderer.md` or
  `Docs/Workflows/ros2_runtime_setup.md`.
next_round_action:
  Round 3 should re-check latest `*_CURRENT` files and add a narrow source
  priority note if the current formal docs remain easy to misread.
```

### EXTREF-MEM-006 - FAST-LIO Evidence Boundary Still Holds

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  A visible point cloud, transport probe, static patch-readiness result, or
  nonzero FAST-LIO topic count is not sufficient alone. Claimable localization
  needs the selected runtime consuming the intended LiDAR/IMU route plus
  truth-error evaluation and explicit claim boundary.
current_evidence:
  - `REAL_UAV_STACK_REUSE_MATRIX_20260602.md` requires registered cloud,
    odometry, path, and truth-error evaluation.
  - `REAL_UAV_STACK_SOURCE_AUDIT_20260602.md` says visible `PointCloud2` is
    display evidence only unless the selected FAST-LIO runtime parses it.
  - `FASTLIO_INPUT_CONTRACT.md` shows dense input readiness but also notes
    spark-fast-lio PointCloud2 Livox support is false and CustomMsg is guarded.
  - `runtime_review_bundle.md` separates Gate B evidence from final controller
    and planner claims.
contradictions_or_history:
  Earlier smoke artifacts and transport probes are useful but cannot close
  localization or planner gates by themselves.
formal_target_if_promoted:
  Already broadly represented in UE/ROS workflows and design docs.
next_round_action:
  Round 3 should only add a pointer if the status-source-priority note needs
  this boundary inline.
```

### EXTREF-MEM-007 - Keyboard/Grid/Static Cloud Route Remains Rejected

```text
round: 2
status: round2_verified_rejected_route
risk: high
candidate_statement:
  Keyboard/grid-cell movement, static point-cloud, 2D-only map, HTML active
  point-cloud review, and display tuning remain rejected as product routes.
  They are smoke/debug only.
current_evidence:
  - `REAL_UAV_STACK_SOURCE_AUDIT_20260602.md` records the user correction.
  - `REAL_UAV_STACK_REUSE_MATRIX_20260602.md` marks the keyboard/grid mapping
    loop as smoke only.
  - `Docs/Workflows/unreal_renderer.md` contains multiple negative rules for
    the keyboard/grid/HTML/static-point-cloud route.
contradictions_or_history:
  Old scripts and outputs may still exist for plumbing checks; that existence
  does not make them product evidence.
formal_target_if_promoted:
  Already represented in UE workflow and architecture docs.
next_round_action:
  Round 3 can add this to the rejection map as anti-regression memory.
```

### EXTREF-MEM-008 - Agent/Skill References Remain Gated

```text
round: 2
status: round2_verified_for_cache
risk: medium
candidate_statement:
  Agent, skill, MCP, and workflow reference projects can improve MoSim
  workflows, review patterns, memory, and audit contracts. They do not approve
  broad CoAgent runtime/tool expansion, provider configs, credentials,
  app-server transport, new permanent departments, or unattended automation.
current_evidence:
  - `Docs/Index/external_learning_index.md` lists useful and rejected patterns
    for agent-system sources.
  - `Docs/Workflows/audit_external_repo.md` rejects unverified schemas,
    provider configs, raw streams, and external runtime setup as project
    requirements.
  - `CoAgent/STATUS.md` current review gate explicitly blocks app-server
    transport, unattended automation expansion, permanent department expansion,
    broad hook rewrites, MCP/tool expansion, credentials/configuration, and
    destructive actions unless specifically approved.
contradictions_or_history:
  Long-session MCP/skills/plugin exploration is infrastructure history. It
  should not silently change the project runtime boundary.
formal_target_if_promoted:
  Already represented in external learning/audit docs and CoAgent status.
next_round_action:
  Coordinate with the CoAgent operating round-2 cache before any round-3
  wording or implementation.
```

## Rejected Or Superseded Historical Items

| Historical Item | Current Treatment |
|---|---|
| Broad raw `References/` scanning as the default recovery route | Superseded by reference-index-first workflow. |
| Direct adoption of RflySim/AirSim/Gazebo/PX4/Sunray/FAST-LIO runtimes by implication | Rejected without explicit approval, local build/runtime evidence, and target workflow ownership. |
| RflySim packaged scenes as directly editable MoSim assets | Rejected by current scene-source policy unless separately proven editable and accepted. |
| Keyboard/grid/static/HTML point-cloud route as product evidence | Rejected; smoke/debug only. |
| Treating `FASTLIO_RUNTIME_STATUS.md` alone as current global FAST-LIO truth | Superseded by source-priority rule: latest `*_CURRENT` route-specific gate first. |
| Treating Factory Gate B as final controller/planner/product acceptance | Rejected; it opens manual review only. |
| Treating agent/skill catalogs as approved runtime/tool expansions | Rejected unless separately approved and verified. |

## Round 3 Promotion Candidates

Only these narrow items are candidates for round 3:

1. A status-source-priority note for FAST-LIO results:
   latest `*_CURRENT` route-specific gate and runtime review bundle first;
   older runtime-status, blocker, and diagnosis files remain history for their
   route/date.
2. An already-formalized marker for the reference-index-first external learning
   route, unless the next review finds a missing recovery pointer.
3. An anti-regression entry that keyboard/grid/static/HTML point-cloud routes
   are smoke/debug only.
4. A compact reminder that external agent/skill/MCP references are workflow
   inputs, not approved CoAgent/runtime/tool expansion.

No direct external runtime adoption, final FAST-LIO production claim, final
planner/controller claim, Sunray150 numeric/visual claim, or CoAgent expansion
is ready for promotion from this cache.

## Verification Needed Before Round 3

```text
1. Re-read latest route-specific gate files, especially any `*_CURRENT` files,
   before quoting FAST-LIO status or metrics.
2. Re-check whether manual UE/RViz review has been accepted by the user.
3. Re-check whether a newer FAST-LIO runtime, Livox CustomMsg route, or dense
   dataset supersedes the current Gate B/manual-review state.
4. Re-read `CoAgent/STATUS.md` before any agent/tooling claim.
5. Keep external reference lessons separate from Sunray150 asset parameters and
   MWORKS controller evidence; those topics have their own caches.
```
