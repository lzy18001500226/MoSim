# Session Memory Migration Coverage Matrix

Date: 2026-06-04 CST

Scope: coverage ledger for migrating the long `MoSim|四旋翼无人机仿真系统`
conversation into recoverable project-local memory.

This file is cache-only. It does not promote historical chat or old
`PROGRESS.md` entries into formal truth. It records what is already captured,
what still needs topic-specific extraction, and what must remain rejected,
superseded, or user-review-gated.

## Status

```text
round: coverage_audit
status: migration_incomplete_but_recoverable
formal_docs_patched_this_round:
  - Docs/Workflows/identify_quadrotor_parameters.md
  - Docs/Workflows/unreal_renderer.md
  - Docs/Workflows/ros2_runtime_setup.md
round3_rechecked_no_formal_patch:
  - MWORKS code generation / SIL route
  - CoAgent operating boundary
this_file_cache_only: true
primary_recovery_files:
  - PROGRESS.md
  - Docs/Workflows/agent_task_ledger.md
  - Docs/Workflows/session_memory_migration.md
  - Docs/Cache/session_memory_migration/long_goal_plan_20260604.md
  - Docs/Cache/session_memory_migration/coverage_matrix_20260604.md
  - Docs/Cache/session_memory_migration/round3_promotion_rejection_map_20260604.md
```

The current migration has a reliable process and the currently identified topic
set has round-1 capture plus round-2 evidence review. It is not complete
because high-risk items still need round-3 promotion/rejection decisions, and
formal target documents must be re-read in the same round before any patch.

## Coverage Summary

| Area | Current Coverage | Status | Next Migration Action |
|---|---|---|---|
| Migration process and anti-pollution rule | Workflow, round 1 cache, round 2 process review, round 3 map | `round3_map_ready` | Use the round 3 map before any formal patch. |
| Codex App / VSCode / CLI session policy | Round 2 infrastructure cache and debug workflow pointers | `covered_cache_round3_mapped` | Do not edit external `.codex` state unless the user asks for infrastructure repair. |
| MCP / Windows-MCP / ROS-MCP / config repair | Infrastructure cache plus `debug_mcp.md` pointers | `partially_covered` | Extract only reusable repair patterns; keep machine-specific paths as evidence pointers. |
| WeChat gateway progress/intervention | Infrastructure cache plus PROGRESS/AGENTS pointers | `covered_cache_round3_mapped` | Preserve as progress channel only, never proof channel. |
| Git split / large worktree hygiene | Infrastructure cache plus active ledger rows | `covered_cache_round3_mapped` | Keep path-limited; do not run broad Git status as migration proof. |
| Sunray150 source chain / DAE / standalone MID-360 | Round 2 Sunray cache and round 3 map | `covered_cache_round3_mapped` | Only source-chain wording is a narrow promotion candidate. |
| Sunray150 numeric placement / propeller assembly | Round 2 Sunray cache and round 3 map | `cache_only_high_risk` | Re-read current manifests and manual-review state before any parameter claim. |
| Sunray150 material/texture attempts | Round 2 Sunray cache and round 3 rejected history | `rejected_or_pending` | Keep rejected candidates as anti-regression memory; no UE export until accepted. |
| UE/ROS2/FAST-LIO real-stack correction | Round 2 UE/ROS cache and round 3 map | `covered_cache_round3_mapped` | Re-read latest `*_CURRENT` gates before claims. |
| Keyboard/grid/static point-cloud/HTML route | Round 2 UE/ROS cache and round 3 rejected history | `rejected_or_smoke_only` | Keep as anti-regression memory only. |
| Factory Gate B / FAST-LIO runtime status | Round 2 UE/ROS cache plus round 3 re-read of current Gate B, runtime bundle, input contract, blockers, status summaries, and helper scripts | `round3_applied_source_priority` | Use latest route-specific `*_CURRENT` gate and linked runtime directory first; Factory Gate B opens manual UE/RViz review only, not final controller/planner/product acceptance. |
| MWORKS evidence labels / smoke boundaries | Round 2 MWORKS cache and round 3 map | `covered_cache_round3_mapped` | Possible narrow patch only if workflow docs lack `smoke_only` boundaries. |
| MWORKS code generation / SIL route | Round 1 cache plus round 2 audit at `round2_mworks_codegen_runtime_memory_20260604.md`; round 3 re-read current workflow, architecture doc, and `Results/codegen_probe` evidence | `round3_rechecked_no_formal_patch` | Already represented formally: `GenerateModelCode` route, PID-demo-only compile/runtime/SIL smoke, time-varying/per-controller SIL still open, and rejected overgeneralization. No newer time-varying or target-controller SIL artifact was found in this round. |
| Sysblock graphical counterpart requirement | Round 2 MWORKS cache and AGENTS pointer | `covered_cache_round3_mapped` | Already represented; future patches should be narrow. |
| UE scene source selection / Factory / Derelict / rejected maps | Round 1 scene-source/renderer cache plus round 2 audit at `round2_scene_source_renderer_memory_20260604.md`; round 3 re-read registry, active links, manual packets, smoke status, and Factory Gate-B bundle | `round3_applied_state_disambiguation` | `Docs/Workflows/unreal_renderer.md` now separates registry policy primary, active renderer links, manual-review target, Gate-B/runtime readiness, smoke evidence, and final acceptance. Current files show registry policy primary Derelict while active links point to Factory; no scene was promoted to final product acceptance. |
| Unreal renderer / review-camera / listener / editor MCP history | Round 1 scene-source/renderer cache plus round 2 audit at `round2_scene_source_renderer_memory_20260604.md`; round 3 map updated | `round2_verified_needs_live_recheck_before_use` | Treat old S0/S1/blockout routes as superseded; re-run current review/log checks before any current visual-review claim. |
| ROS2 Humble runtime setup and apt/key state | Round 1 cache plus round 2 audit at `round2_ros2_runtime_setup_memory_20260604.md`; round 3 re-read current evidence and patched `Docs/Workflows/ros2_runtime_setup.md` | `round3_applied_source_priority` | ROS2 Humble route is formalized; apt/key and rosbridge notes are prior infrastructure evidence unless live-checked; current FAST-LIO answers must prefer latest route-specific `*_CURRENT` gates and existing helper scripts. |
| CoAgent organization / department / task-runtime history | Round 1 CoAgent operating cache plus round 2 audit at `round2_coagent_operating_memory_20260604.md`; round 3 re-read CoAgent STATUS/README, decision record, visible-thread SOP, orchestration workflow, and ledger | `round3_rechecked_no_formal_patch` | Existing docs already carry the gate; keep as guardrails only. No implementation, visibility-health claim, live notification, automation, department, transport, schema, or tool expansion is authorized by this migration. |
| Parameter identification / Sunray150 physical parameters | Round 1 parameter cache plus round 2 audit at `round2_parameter_identification_memory_20260604.md`; round 3 application clarified the formal workflow wording without numeric promotion | `round3_applied_no_numeric_promotion` | Current values remain `source=SDF_migration`; no project-local identification bundle was found in this pass; no numeric parameter is ready for formal promotion. |
| External repos / AirSim / RflySim / reference-learning policy | Round 1 external-reference cache plus round 2 audit at `round2_external_reference_memory_20260604.md`; round 3 map updated | `round2_verified_round3_mapped` | Keep external references as contracts/patterns unless an approved integration has local build/runtime evidence; preserve FAST-LIO status-source priority and rejected toy-route memory. |
| Active queues / mistakes to avoid / recovery pointers | Present in PROGRESS | `needs_compaction_review` | Decide whether to split into formal workflow pointers or cache-only historical backlog. |

## Required Topic Caches Still Missing

No currently identified coverage-matrix topic cache is still completely
missing. No currently identified topic remains round-1-only after this
checkpoint. This does not mean the migration is complete: all high-risk topics
still need round-3 promotion/rejection decisions before any formal target doc
patch.

```text
round1_only_caches_need_round2:
  - none
round2_verified_topics_need_round3_application:
  - external_reference_learning
```

## Completion Audit Against Workflow Criteria

`Docs/Workflows/session_memory_migration.md` says full migration is complete
only when all important items are cached or out of scope, all high-risk items
are promoted/rejected/superseded/user-review-gated, the cache has a promoted
target map, recovery indexes point to the state, and a new conversation can
recover without the old transcript.

Current audit:

```text
all_important_items_cached_or_out_of_scope:
  partial
  reason:
    - The currently identified coverage-matrix topics now have round-1 cache
      and topic-specific round-2 evidence review.
    - PROGRESS.md is still long and may expose lower-priority historical
      recovery notes during later compaction review.
    - The migration still needs more round-3 application: one narrow item at a
      time, with current evidence and target docs re-read in the same round.

all_high_risk_items_resolved:
  incomplete
  reason:
    - Sunray numeric assembly, Factory FAST-LIO state, and final UE scene
      acceptance remain high-risk.
    - Codegen/SIL has a round-3 disposition with no formal patch: it remains
      PID-demo-only architecture evidence, per-controller time-varying SIL is
      still open, and no newer target-controller SIL artifact was found under
      `Results/codegen_probe` in this round.
    - Scene-source/renderer has a round-3 state-disambiguation patch, but final
      scene acceptance is still not promoted; future claims must identify the
      exact state field and re-read current files.
    - ROS2/FAST-LIO has a round-3 source-priority disposition and narrow
      workflow patch. Factory current Gate B opens manual UE/RViz review only;
      final localization, planner performance, controller integration, and
      product acceptance remain unpromoted.
    - CoAgent has a round-3 no-formal-patch disposition: existing CoAgent docs
      already carry the gate; live visibility, implementation, automation,
      transport, schema, notification, department, and tool expansion are not
      authorized by this migration.
    - Parameter identification now has round-3 disposition for the current
      repository state: no project-local identification bundle was found, one
      accepted-mass wording risk was clarified, and no numeric parameter was
      promoted.
    - External reference learning remains reference/adaptation only unless a
      later task proves an approved runtime integration.

promoted_target_map_exists:
  partial_but_current_topic_set_mapped
  evidence:
    - round3_promotion_rejection_map_20260604.md now includes the current
      round-2 topic set.
  gap:
    - only parameter-identification wording has been patched from the new
      round-2 topic set.
    - each future formal patch must re-read current evidence and the target doc
      in that same round.

recovery_indexes_point_to_state:
  partial
  evidence:
    - PROGRESS.md, workflow index, and ledger point to the migration.
  gap:
    - they should also mention this coverage matrix.

new_conversation_can_continue_without_old_transcript:
  yes_for_current_topic_set
  gap:
    - broader PROGRESS/ledger themes still need topic caches to avoid relying on
      old chat or a 2000+ line progress file.
    - round-3 formal-patch decisions are still open and must remain
      item-by-item.
```

## Next Safe Work Order

1. Start from `round3_promotion_rejection_map_20260604.md`.
2. Pick one bucket item only.
3. Re-read the current evidence files and the target formal document in that
   same round.
4. Either patch the one target narrowly, mark the item rejected/superseded, or
   record a user-review/current-evidence blocker.
5. Do not clean or compress `PROGRESS.md` until equivalent recoverable topic
   caches exist.
