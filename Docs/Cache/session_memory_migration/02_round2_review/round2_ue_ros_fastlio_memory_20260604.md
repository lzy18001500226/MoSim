# Round 2 UE/ROS2/FAST-LIO Memory Audit

Date: 2026-06-04 CST

Scope: verify the long-session memory around Unreal rendering, ROS2/RViz2,
Mid360/Livox, FAST-LIO, and rejected toy mapping routes against current project
files. This is a cache-only round 2 audit. It does not promote old runtime
claims into final product evidence.

## Status

```text
round: 2
topic: UE/ROS2/FAST-LIO architecture and evidence boundary
status: mixed_round2_verified_and_needs_round3
risk: high
formal_docs_patched_this_round: none
cache_only: true
```

## Sources Re-Read

| Source | Finding |
|---|---|
| `Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md` | Records the architectural rejection of grid-cell movement, fake/static point clouds, and 2D-only mapping as product routes. Defines MWORKS as truth/controller authority, UE as renderer/sensor oracle, and ROS2/RViz2 as middleware/review surface. |
| `Docs/Workflows/unreal_renderer.md` | Records the current Factory-first UAV body gate, separate UE/RViz windows, native FAST-LIO route, and many negative rules around old RViz/HTML/manual keyboard routes. |
| `Docs/Workflows/ros2_runtime_setup.md` | Records ROS2 Humble setup, FAST-LIO candidate notes, and older scan099 status where Factory was degraded and Derelict passed with warnings. |
| `Results/unreal_scene_mapping/factoryenvironmentcollect/REALSTACK_MINILOOP_GATE_CURRENT.md` | Current Factory headless Gate B is `ready_for_manual_rviz_ue_review` with FAST-LIO counts and pass metrics. |
| `Results/unreal_scene_mapping/factoryenvironmentcollect/realstack_miniloop_gate_current.json` | Current gate details: `position_rmse_m=0.39454`, `max_position_error_m=0.611542`, `yaw_rmse_rad=0.017802`; claim boundary says this allows human review only and does not claim final controller/planner performance. |
| `Results/unreal_scene_mapping/factoryenvironmentcollect/runtime_review_bundle.md` | Current execution contract for opening UE/RViz review; explicitly says it is a launch package, not proof that runtime already ran. |
| `Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_INPUT_CONTRACT.md` | Dense Mid360-style input contract is `claimable_input_ready`, but implementation support notes the spark-fast-lio PointCloud2 path lacks Livox support and CustomMsg is guarded. |
| `Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_MID360_RUNTIME_BLOCKER.md` | Older/parallel blocker for a dense Factory Mid360 spark-fast-lio path: selected runtime could not consume current Livox/Mid360 PointCloud2 as a claimable path. |
| `Results/unreal_scene_mapping/FASTLIO_RUNTIME_STATUS.md` | Older 2026-06-01 scan099 status: ROS2 runtime outputs exist, Factory degraded, Derelict passed with warnings. |
| `Results/unreal_scene_mapping/SPARK_FASTLIO_LIVOX_PATCH_READINESS.md` | Static readiness for a spark-fast-lio Livox patch; passing this is not localization evidence. |

## Round 2 Findings

### UE-ROS-MEM-001 - Rejected Toy Mapping Route

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  The hand-rolled keyboard/grid-cell/static-point-cloud/2D-only mapping route
  is rejected as product architecture. It may remain only as smoke/debug
  plumbing, not controller, localization, mapping, or navigation evidence.
current_evidence:
  - `Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md` says the user rejected
    the toy path and restricts it to smoke testing ROS/RViz wiring.
  - `Docs/Workflows/unreal_renderer.md` says not to polish old hand-built
    RViz2 point-cloud/local-grid/browser preview routes as product work.
contradictions_or_history:
  Earlier HTML point clouds, keyboard loops, local occupancy replays, and
  browser previews were useful for plumbing but must not be revived as final
  evidence.
formal_target_if_promoted:
  Already mostly represented in `Docs/Design/09_*` and
  `Docs/Workflows/unreal_renderer.md`.
next_round_action:
  Round 3 can promote only a short recovery pointer if a gap remains; otherwise
  mark this as already formalized.
```

### UE-ROS-MEM-002 - Accepted Role Split

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  The accepted architecture separates MWORKS/Sysplorer/Syslab truth and
  controller evidence, UE rendered scene/sensor oracle, and ROS2/RViz2
  LiDAR/IMU/TF/FAST-LIO/map/planner review windows.
current_evidence:
  - `Docs/Design/09_*` Gate C role split.
  - `Docs/Workflows/unreal_renderer.md` says UE is the high-quality visual
    layer while MWORKS remains truth source.
  - `Docs/Workflows/ros2_runtime_setup.md` gives separate UE, RViz2 planning,
    and RViz2 FAST-LIO window layout.
contradictions_or_history:
  Browser HTML and UE debug overlays are not accepted active point-cloud/map
  review surfaces. UE global collision/occupancy truth is validation oracle,
  not planner input.
formal_target_if_promoted:
  Already represented in `AGENTS.md` and `Docs/Workflows/unreal_renderer.md`.
next_round_action:
  Round 3 should verify whether any shorter startup/recovery pointer is needed
  for new conversations; do not duplicate long sections.
```

### UE-ROS-MEM-003 - Factory Gate B Current State

```text
round: 2
status: round2_verified_for_cache_but_not_final_product_claim
risk: high
candidate_statement:
  Current Factory Gate B headless evidence is `ready_for_manual_rviz_ue_review`
  according to `REALSTACK_MINILOOP_GATE_CURRENT.md/json`: FAST-LIO runtime
  counts are nonzero and truth evaluation passes. This opens UE/RViz manual
  review only; it does not prove final controller integration, planner
  performance, or product acceptance.
current_evidence:
  - `REALSTACK_MINILOOP_GATE_CURRENT.md`: status `ready_for_manual_rviz_ue_review`,
    counts `odometry=80`, `path=8`, `registered_cloud=80`, evaluation pass.
  - `realstack_miniloop_gate_current.json`: `position_rmse_m=0.39454`,
    `max_position_error_m=0.611542`, `yaw_rmse_rad=0.017802`, and explicit
    claim boundary.
  - `runtime_review_bundle.md`: this is an execution contract for manual
    review and not proof the manual review already ran.
contradictions_or_history:
  Older files record Factory degraded scan099 status or earlier 9-10m RMSE
  failures. Those remain important failure history, but the `*_CURRENT` gate is
  the current Factory manual-review entry unless a newer result supersedes it.
formal_target_if_promoted:
  If needed, a narrow recovery pointer in `Docs/Workflows/unreal_renderer.md`;
  do not promote as final controller/planner evidence.
next_round_action:
  Round 3 must check whether a newer `REALSTACK_MINILOOP_GATE_CURRENT` or
  runtime review result exists before quoting these metrics.
```

### UE-ROS-MEM-004 - FAST-LIO Runtime And Mid360 Compatibility Caveat

```text
round: 2
status: round2_verified_for_cache_needs_round3_disambiguation
risk: high
candidate_statement:
  FAST-LIO evidence is not a single global yes/no state. The project has:
  current Factory Gate B evidence that opens manual review, older scan099
  Factory-degraded/Derelict-pass evidence, and a Mid360/Livox implementation
  compatibility caveat for spark-fast-lio PointCloud2 versus Livox CustomMsg.
current_evidence:
  - `FASTLIO_INPUT_CONTRACT.md`: dense input is claimable-ready, but
    spark-fast-lio PointCloud2 does not support Livox and CustomMsg is guarded.
  - `FASTLIO_MID360_RUNTIME_BLOCKER.md`: dense Factory Mid360 PointCloud2 path
    produced zero outputs with `Error LiDAR Type`; valid next steps are Livox
    CustomMsg support, another Mid360-capable implementation, or degraded smoke.
  - `SPARK_FASTLIO_LIVOX_PATCH_READINESS.md`: static patch readiness is not
    runtime localization evidence.
  - `FASTLIO_RUNTIME_STATUS.md`: older scan099 status says Derelict passed
    with warnings and Factory was degraded.
contradictions_or_history:
  Some docs are snapshots from different candidate/runtime routes. New sessions
  must compare file dates, `*_CURRENT` gates, and runtime directories before
  saying "Factory passed" or "Factory failed" globally.
formal_target_if_promoted:
  A small "status source priority" note in `Docs/Workflows/ros2_runtime_setup.md`
  or `Docs/Workflows/unreal_renderer.md` if round 3 confirms the ambiguity is
  still easy to misread.
next_round_action:
  Round 3 should reconcile current runtime source priority: latest
  `*_CURRENT` gate first, then current runtime review bundle, then older
  blocker/diagnosis files as history.
```

### UE-ROS-MEM-005 - MWORKS/UE Smoke Evidence Boundary

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  Factory and Derelict MWORKS/UE scene-control smoke metrics are real
  Sysplorer/MCP smoke evidence, but their own metrics files mark them
  `quality_status=smoke_only`. They cannot support final autonomous
  navigation, final FAST-LIO localization, or full controller-performance
  claims.
current_evidence:
  - `Results/unreal_scene_mapping/*/mworks_smoke/metrics/*.json` files include
    `quality_status: smoke_only`.
  - Collision JSON files state a pass is still smoke evidence, not completed
    autonomous navigation or FAST-LIO localization.
contradictions_or_history:
  Earlier conversation language may have treated scene-control smoke as a
  larger success than the evidence supports.
formal_target_if_promoted:
  MWORKS evidence workflow or UE workflow only if not already covered.
next_round_action:
  Round 3 should re-read the MWORKS evidence docs together with the MWORKS
  topic-specific audit before promoting anything.
```

## Rejected Or Superseded Historical Items

| Historical Item | Current Treatment |
|---|---|
| Keyboard/grid-cell movement as UAV simulator product route | Rejected; smoke/debug only. |
| Browser HTML point cloud as active mapping review | Rejected; report/offline preview only if explicitly requested. |
| UE debug overlay as replacement for RViz/FAST-LIO review | Rejected. |
| `/mosim/replay_odometry` as FAST-LIO odometry | Rejected; it is reference/replay pose only. |
| Nonzero FAST-LIO topics without truth-error evaluation | Insufficient for localization acceptance. |
| Old low-density or mixed-source Factory FAST-LIO results | Failure history; not current claimable evidence. |
| Treating Factory Gate B as final planner/controller acceptance | Rejected; it opens manual review only. |

## Round 3 Promotion Candidates

Only these narrow items are candidates for round 3:

1. A recovery pointer that the product route is UAV-stack-first:
   MWORKS state -> UE sensor/render oracle -> ROS2 LiDAR/IMU/TF -> native
   FAST-LIO/RViz2 evidence.
2. A status-source-priority note for FAST-LIO results:
   latest `*_CURRENT` gate and runtime review bundle first; older blocker and
   scan files remain failure/compatibility history.
3. A negative rule that old keyboard/grid/HTML/static point-cloud routes are
   smoke-only and must not be resumed as product work.

No final planner, autonomous navigation, or complete FAST-LIO production claim
is ready for promotion from this cache.

## Verification Needed Before Round 3

```text
1. Re-run or re-read the latest Factory `REALSTACK_MINILOOP_GATE_CURRENT`
   artifacts and check for newer runtime directories.
2. Re-check whether manual UE/RViz review has been accepted by the user.
3. Re-check whether the Mid360/Livox CustomMsg or selected FAST-LIO runtime
   route changed after the current blocker/readiness files.
4. Keep MWORKS smoke evidence and FAST-LIO localization evidence separate.
```
