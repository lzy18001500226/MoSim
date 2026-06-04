# Round 3 Promotion / Rejection Map - Session Memory Migration

Date: 2026-06-04 CST

Scope: build the round-3 gate for the long `MoSim|Quadrotor simulation system`
conversation memory. This file is still cache-only. It decides what may be
promoted later, what is already covered by formal docs, and what must stay
rejected, superseded, or pending user review.

## Status

```text
round: 3
status: round3_application_started
formal_docs_patched_this_round:
  - Docs/Workflows/identify_quadrotor_parameters.md
  - Docs/Workflows/unreal_renderer.md
  - Docs/Workflows/ros2_runtime_setup.md
round3_rechecked_no_formal_patch:
  - MWORKS codegen/SIL boundary
this_file_cache_only: true
source_rounds:
  - Docs/Cache/session_memory_migration/round1_candidate_cache_20260604.md
  - Docs/Cache/session_memory_migration/round2_process_review_20260604.md
  - Docs/Cache/session_memory_migration/round2_sunray150_asset_memory_20260604.md
  - Docs/Cache/session_memory_migration/round2_ue_ros_fastlio_memory_20260604.md
  - Docs/Cache/session_memory_migration/round2_mworks_controller_evidence_memory_20260604.md
  - Docs/Cache/session_memory_migration/round2_infrastructure_memory_20260604.md
  - Docs/Cache/session_memory_migration/round2_mworks_codegen_runtime_memory_20260604.md
  - Docs/Cache/session_memory_migration/round2_ros2_runtime_setup_memory_20260604.md
  - Docs/Cache/session_memory_migration/round2_scene_source_renderer_memory_20260604.md
  - Docs/Cache/session_memory_migration/round2_parameter_identification_memory_20260604.md
  - Docs/Cache/session_memory_migration/round2_coagent_operating_memory_20260604.md
  - Docs/Cache/session_memory_migration/round2_external_reference_memory_20260604.md
```

This map does not make old chat facts formal truth. A later formal patch must
still re-read the current target document and current evidence immediately
before editing.

Round-3 application checkpoint on 2026-06-04:

```text
PARAM-MEM-001/PARAM-MEM-002/PARAM-MEM-003/PARAM-MEM-004/PARAM-MEM-006:
  evidence_re_read:
    - Docs/Cache/session_memory_migration/round2_parameter_identification_memory_20260604.md
    - Docs/Workflows/identify_quadrotor_parameters.md
    - Docs/Design/02_模型接口与运行流程.md
    - Docs/Design/03_控制系统架构.md
    - project-local search for Results/identification, .ulg, .params,
      sunray150_identified, fit_report, residual_summary, and mworks_check
  disposition:
    - formal docs already represented the main rule that current Sunray150
      dynamics values remain source=SDF_migration.
    - one wording risk was corrected in
      Docs/Workflows/identify_quadrotor_parameters.md: accepted takeoff mass is
      only a provenance-labeled input for the exact flight configuration, not a
      promotion of inertia, rotor geometry, motor coefficients, drag,
      controller evidence, or the full parameter set to identified truth.
    - no numeric parameter was promoted.
    - no project-local identification evidence bundle was found in this round.

CODEGEN-MEM-001/CODEGEN-MEM-005/CODEGEN-MEM-007/CODEGEN-MEM-008:
  evidence_re_read:
    - Docs/Cache/session_memory_migration/round2_mworks_codegen_runtime_memory_20260604.md
    - Docs/Workflows/mworks_codegen_controller_runtime.md
    - Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md
    - Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/runtime_check.json
    - Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/mworks_constant_0p1_reference.json
    - Results/codegen_probe/AWFF_PID_Sysblock_Demo_api/sil_constant_0p1_check.json
    - project-local search under Results/codegen_probe for newer SIL/runtime
      artifacts
  disposition:
    - formal docs already represent the safe codegen boundary:
      `GenerateModelCode`, not `TranslateModel`, is the controller code-export
      route.
    - current evidence remains PID-demo-only architecture evidence:
      compile/runtime harness, zero-input SIL smoke, and nonzero constant-input
      SIL smoke passed for `AWFF_PID_Sysblock_Demo` only.
    - no newer time-varying SIL or target-controller SIL artifact was found
      under `Results/codegen_probe` in this round.
    - generated C/C++ runtime output remains generated-runtime/SIL evidence and
      cannot replace MWORKS/Sysplorer simulation evidence before each target
      controller has its own equivalence gate.
    - no formal patch was needed because the workflow and architecture docs
      already carry these restrictions.

SCENE-MEM-001/SCENE-MEM-002/SCENE-MEM-003/SCENE-MEM-005/SCENE-MEM-006:
  evidence_re_read:
    - Docs/Cache/session_memory_migration/round2_scene_source_renderer_memory_20260604.md
    - Docs/Workflows/unreal_renderer.md
    - UE5/MoSimSceneLibrary/Content/MworksData/scene_source_registry.json
    - UE5/MoSimSceneLibrary/Content/MworksData/active_scene_links.json
    - Results/unreal_scene_mapping/factoryenvironmentcollect/manual_review_packet.md
    - Results/unreal_scene_mapping/derelictcorridormegascans/manual_review_packet.md
    - Results/unreal_scene_mapping/UE_SCENE_CLOSED_LOOP_STATUS.md
    - Results/unreal_scene_mapping/factoryenvironmentcollect/runtime_review_bundle.md
    - Results/unreal_scene_mapping/factoryenvironmentcollect/REALSTACK_MINILOOP_GATE_CURRENT.md
  disposition:
    - formal workflow patched narrowly to prevent collapsing registry policy
      primary, active renderer content links, manual-review packet target,
      Gate-B/runtime readiness, smoke evidence, and final scene acceptance.
    - current files show
      `scene_source_registry.policy.primary_scene_source_id=
      local_derelictcorridormegascans` while
      `active_scene_links.scene_source_id=local_factoryenvironmentcollect`.
    - Factory Gate-B/runtime bundle is `ready_for_manual_rviz_ue_review`, which
      opens human UE/RViz review but does not prove final controller/planner
      integration.
    - Factory and Derelict closed-loop status remains `ready_smoke_validated`
      with MWORKS `smoke_only`, not final controller-performance evidence.
    - Fab/Epic inventory remains `inventory_visible_not_scene_accepted`.
    - no scene was promoted to final product acceptance in this round.

ROS2-MEM-001/ROS2-MEM-002/ROS2-MEM-003/ROS2-MEM-004/ROS2-MEM-005/ROS2-MEM-007/ROS2-MEM-008/ROS2-MEM-010:
  evidence_re_read:
    - Docs/Cache/session_memory_migration/round2_ros2_runtime_setup_memory_20260604.md
    - Docs/Workflows/ros2_runtime_setup.md
    - Results/unreal_scene_mapping/factoryenvironmentcollect/REALSTACK_MINILOOP_GATE_CURRENT.md
    - Results/unreal_scene_mapping/factoryenvironmentcollect/realstack_miniloop_gate_current.json
    - Results/unreal_scene_mapping/factoryenvironmentcollect/runtime_review_bundle.md
    - Results/unreal_scene_mapping/factoryenvironmentcollect/runtime_review_bundle.json
    - Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_INPUT_CONTRACT.md
    - Results/unreal_scene_mapping/factoryenvironmentcollect/FASTLIO_MID360_RUNTIME_BLOCKER.md
    - Results/unreal_scene_mapping/FASTLIO_RUNTIME_STATUS.md
    - Results/unreal_scene_mapping/FASTLIO_FAMILY_COMPATIBILITY.md
    - Results/unreal_scene_mapping/SPARK_FASTLIO_ROS2_CANDIDATE.md
    - Scripts/UE5/run_mosim_scene_replay_launch_ros2.sh
    - Scripts/UE5/run_factory_fastlio_mid360_headless_ros2.sh
    - Scripts/UE5/review_scene_mapping_loop.sh
    - Scripts/UE5/check_fastlio_ros2_topics.sh
    - project-local file check for `open_mapping_rviz_ros2.sh` and
      `run_fastlio_rviz_replay_ros2.sh`
  disposition:
    - formal workflow patched narrowly to mark the 2026-06-01 apt/key,
      rosbridge, and port notes as prior infrastructure evidence, not a live
      current-host guarantee.
    - formal workflow now says current FAST-LIO answers must prefer the latest
      route-specific `*_CURRENT` gate and linked runtime directory over older
      summary, candidate, preflight, compatibility, ROS1-bundle, or blocker
      files.
    - stale command references to missing helper scripts were removed from the
      current command list and replaced with scripts present in this checkout:
      `run_mosim_scene_replay_launch_ros2.sh`,
      `run_factory_fastlio_mid360_headless_ros2.sh`,
      `review_scene_mapping_loop.sh`, and `check_fastlio_ros2_topics.sh`.
    - current Factory `REALSTACK_MINILOOP_GATE_CURRENT` is
      `ready_for_manual_rviz_ue_review` with FAST-LIO output counts
      `odometry=80`, `path=8`, `registered_cloud=80` and evaluation pass, but
      it only opens manual UE/RViz review and does not prove final controller,
      planner, or product acceptance.
    - `runtime_review_bundle.md` reflects the newer Gate-B/manual-review route,
      while `runtime_review_bundle.json` still contains older ROS1 blocked
      fields. For current answers, use the latest `*_CURRENT` files and
      route-matching Markdown/runtime evidence first; keep the JSON mismatch as
      historical/stale evidence until regenerated.
    - older files remain route/date-specific: the local-source compatibility
      scan was metadata-only, the SPARK candidate file was a build-phase
      snapshot, the 2026-06-01 scan099 status had Factory failure/Derelict
      warning-pass, and the Mid360 blocker describes a PointCloud2 route that
      produced zero outputs with `Error LiDAR Type`.
    - no final FAST-LIO localization, planner performance, controller
      integration, or product acceptance claim was promoted.
```

## Promotion Buckets

### Already Represented In Formal Project Docs

These items should usually not create more formal documentation. Round 3 only
needs to confirm the existing formal entry is still present.

```text
INFRA-MEM-001:
  durable state is project docs, ledgers, and cache, not live session sync
  formal entries:
    - AGENTS.md
    - Docs/Index/codex_app_session_research.md
    - Docs/Workflows/session_memory_migration.md

INFRA-MEM-002:
  Codex App / Windows shared-state repair is infrastructure history
  formal entry:
    - Docs/Workflows/debug_mcp.md
  guard:
    - external .codex database or runtime edits require a fresh explicit
      infrastructure request

INFRA-MEM-003:
  Codex App hangs are multi-cause, not simply WSL versus Windows
  formal entry:
    - Docs/Workflows/debug_mcp.md
  guard:
    - do not turn the historic diagnosis into a guaranteed current root cause

INFRA-MEM-004:
  WeChat is progress/intervention only, not proof
  formal entries:
    - AGENTS.md
    - Docs/Workflows/agent_orchestration.md

INFRA-MEM-005:
  Git work must stay path-scoped and split-aware
  formal entries:
    - AGENTS.md
    - Docs/Workflows/agent_task_ledger.md
    - Docs/Workflows/agent_orchestration.md

MWORKS-MEM-001:
  preserve source labels such as source=MWORKS_MCP and source=offline_script
  formal entries:
    - AGENTS.md
    - Docs/Workflows/produce_simulation_evidence.md

MWORKS-MEM-004:
  formal controller claims require a behavior-equivalent graphical Sysblock
  counterpart or an explicit equation-bridge caveat
  formal entries:
    - AGENTS.md
    - Docs/Workflows/build_sysblock_graphical_controller.md

MWORKS-MEM-005:
  interactive MWORKS/Sysplorer/Syslab work should use healthy targeted MCP
  formal entries:
    - AGENTS.md
    - Docs/Workflows/debug_mcp.md
    - Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md

UE-ROS-MEM-001:
  keyboard/grid-cell/static point-cloud/HTML routes are rejected as product
  evidence and are smoke-only
  formal entries:
    - AGENTS.md
    - Docs/Workflows/unreal_renderer.md
    - Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md

UE-ROS-MEM-002:
  MWORKS is control/truth authority, UE is rendering/sensor oracle, and ROS2
  with RViz2 owns localization/map/planner review
  formal entries:
    - AGENTS.md
    - Docs/Workflows/unreal_renderer.md
    - Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md

ROS2-MEM-001:
  ROS2 Humble plus RViz2 is the documented Ubuntu 22.04 mapping/review route
  formal entries:
    - Docs/Workflows/ros2_runtime_setup.md
  guard:
    - apt/key and rosbridge status are prior infrastructure evidence unless
      live-checked in a fresh infrastructure task

ROS2-MEM-003:
  ROS-MCP uses rosbridge through the documented wrapper route
  formal entries:
    - Docs/Workflows/debug_mcp.md
    - Docs/Workflows/ros2_runtime_setup.md
  guard:
    - do not claim port 9090 is currently listening without a live probe

ROS2-MEM-006:
  HTML is not active point-cloud/map review; use RViz2 or equivalent native
  robotics tooling
  formal entries:
    - AGENTS.md
    - Docs/Workflows/unreal_renderer.md

ROS2-MEM-007:
  `/mosim/replay_odometry` is reference/replay pose, not FAST-LIO odometry
  formal entries:
    - Docs/Workflows/ros2_runtime_setup.md

SCENE-MEM-001:
  Fab/Epic inventory visibility is not scene acceptance
  formal entries:
    - Docs/Workflows/unreal_renderer.md

SCENE-MEM-005:
  exported UE scene truth is a validation oracle, not planner-known global map
  formal entries:
    - AGENTS.md
    - Docs/Workflows/unreal_renderer.md

SCENE-MEM-008:
  old S0/S1/blockout/generated map routes are superseded for main real-scene
  work
  formal entries:
    - Docs/Workflows/unreal_renderer.md
    - Docs/Workflows/agent_task_ledger.md

PARAM-MEM-001:
  current Sunray150 dynamics parameters remain `source=SDF_migration`, not
  identified physical truth
  formal entries:
    - Docs/Workflows/identify_quadrotor_parameters.md
    - Docs/Design/02_模型接口与运行流程.md
    - Docs/Design/03_控制系统架构.md
  round3_disposition:
    - applied_no_numeric_promotion
    - formal wording clarified that accepted takeoff mass is not a full
      identified-parameter upgrade

PARAM-MEM-002:
  `identified` requires raw logs, parameters, fit output, held-out validation,
  and MWORKS verification
  formal entries:
    - Docs/Workflows/identify_quadrotor_parameters.md
    - Docs/Design/02_模型接口与运行流程.md
  round3_disposition:
    - already_represented_and_rechecked
    - no complete identification bundle found in this round

CODEGEN-MEM-001:
  generated controller code export uses `GenerateModelCode`, not
  `TranslateModel`
  formal entries:
    - Docs/Workflows/mworks_codegen_controller_runtime.md
    - Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md

CODEGEN-MEM-008:
  generated runtime results are not MWORKS/Sysplorer simulation evidence before
  per-controller equivalence
  formal entries:
    - AGENTS.md
    - Docs/Workflows/mworks_codegen_controller_runtime.md

COAGENT-MEM-001:
  recover CoAgent direction from `CoAgent/STATUS.md`, `CoAgent/README.md`,
  decisions, and ledgers
  formal entries:
    - AGENTS.md
    - CoAgent/README.md
    - CoAgent/STATUS.md

COAGENT-MEM-006:
  WeChat is sparse progress/intervention, not evidence proof
  formal entries:
    - AGENTS.md
    - CoAgent/STATUS.md

EXTREF-MEM-001:
  external learning starts from project reference indexes and audit workflow
  formal entries:
    - CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md
    - Docs/Index/external_learning_index.md
    - Docs/Workflows/audit_external_repo.md

EXTREF-MEM-002:
  external projects are contracts/patterns by default; direct runtime adoption
  requires explicit approval and local evidence
  formal entries:
    - Docs/Index/external_learning_index.md
    - Docs/Workflows/audit_external_repo.md
```

### Narrow Formal Patch Candidates

These items may be promoted only by a later narrow patch after current evidence
is re-read in that same round. The wording must stay constrained.

```text
SUNRAY-MEM-001:
  candidate:
    - The current source-faithful Sunray150 audit chain uses 150.dae plus the
      standalone Livox MID-360 test2.dae referenced by the Sunray SDF.
  possible target:
    - Docs/Workflows/unreal_renderer.md
    - Docs/Index/sunray_migration_index.md
    - a Sunray asset source/evidence manifest under Results/ or SourceAssets/
  required immediate evidence before patch:
    - re-read the Sunray SDF include path, 150.dae, test2.dae, and the latest
      asset audit manifest
  allowed wording:
    - source-chain rule only
  forbidden wording:
    - final runtime placement, final material acceptance, or final UE export

MWORKS-MEM-002:
  candidate:
    - Smoke metrics and successful execution are not controller performance
      acceptance.
  possible target:
    - Docs/Workflows/run_simulation.md
    - Docs/Workflows/produce_simulation_evidence.md
  required immediate evidence before patch:
    - re-read current workflow wording and current result manifests
  allowed wording:
    - clarify quality_status=smoke_only boundaries if the target doc lacks it

MWORKS-MEM-003:
  candidate:
    - check_model ok and simulate_model ok prove load/execution only, not model
      quality or control performance.
  possible target:
    - Docs/Workflows/run_simulation.md
    - Docs/Skills/Mworks/mworks-simulation-evidence/SKILL.md
  required immediate evidence before patch:
    - re-read current simulation workflow and latest evidence bundle format

UE-ROS-MEM-005:
  candidate:
    - UE/MWORKS smoke evidence must remain separate from full controller,
      localization, planner, or product acceptance.
  possible target:
    - Docs/Workflows/unreal_renderer.md
    - Docs/Workflows/produce_simulation_evidence.md
  required immediate evidence before patch:
    - re-read current REALSTACK/Factory status files and current workflow text

ROS2-MEM-008:
  candidate:
    - FAST-LIO status must be read by route/date/source priority: latest
      matching `*_CURRENT` gate and runtime review bundle first; older
      preflight, blocker, candidate, and diagnosis files are historical context
      unless they match the current route.
  possible target:
    - Docs/Workflows/ros2_runtime_setup.md
    - Docs/Workflows/unreal_renderer.md
  required immediate evidence before patch:
    - re-read latest `Results/unreal_scene_mapping/**/**/*CURRENT*` files,
      route-specific runtime bundles, and any newer manual review record
  allowed wording:
    - source-priority rule and claim boundary only
  forbidden wording:
    - final FAST-LIO, final planner, final controller, or product acceptance

ROS2-MEM-010:
  candidate:
    - Some ROS2 helper-script references may be stale or renamed, especially
      `open_mapping_rviz_ros2.sh` and `run_fastlio_rviz_replay_ros2.sh`.
  possible target:
    - Docs/Workflows/ros2_runtime_setup.md
    - Docs/Workflows/unreal_renderer.md
  required immediate evidence before patch:
    - re-run a project-local file check for the referenced helper scripts
  allowed wording:
    - corrected command names or an explicit stale-command warning
  forbidden wording:
    - inventing replacement commands without verifying current scripts

SCENE-MEM-002:
  candidate:
    - Separate scene-source states before answering "current scene":
      `registry_primary`, `active_content_links`, `latest_review_target`,
      `latest_manual_review_status`, and final acceptance.
  possible target:
    - Docs/Workflows/unreal_renderer.md
  required immediate evidence before patch:
    - re-read `scene_source_registry.json`, `active_scene_links.json`, latest
      review/runtime bundles, and recorded manual-review packets
  allowed wording:
    - state-field disambiguation and recovery route only
  forbidden wording:
    - declaring a final current-primary or visually accepted scene from cache

SCENE-MEM-003:
  candidate:
    - Truth artifacts and registry status do not imply rendered-scene/manual
      visual acceptance.
  possible target:
    - Docs/Workflows/unreal_renderer.md
  required immediate evidence before patch:
    - re-read current scene registry and workflow acceptance table

PARAM-MEM-004:
  candidate:
    - The 2026-06-04 migration pass found no project-local Sunray150
      identification bundle under expected `Results/identification/...`
      patterns.
  possible target:
    - keep in cache unless a current report/status doc incorrectly implies an
      identification bundle exists
  required immediate evidence before patch:
    - rerun project-local evidence search in the same round
  allowed wording:
    - current-round repository state only
  forbidden wording:
    - permanent claim that no logs exist anywhere
  round3_disposition:
    - cache_only_current_repository_state
    - project-local evidence search returned no bundle in this round

CODEGEN-MEM-005:
  candidate:
    - PID demo compile/runtime, zero-input SIL smoke, and nonzero constant-input
      SIL smoke passed; this remains PID-demo-only architecture evidence.
  possible target:
    - Docs/Workflows/mworks_codegen_controller_runtime.md
    - Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md
  required immediate evidence before patch:
    - re-read latest `Results/codegen_probe/**/sil_*` files and current
      codegen workflow
  allowed wording:
    - PID-demo-only evidence with tolerance/source-label/timestamp limitation
  forbidden wording:
    - target-controller runtime authority or time-varying SIL completion

EXTREF-MEM-005:
  candidate:
    - External-reference-derived FAST-LIO status needs the same route/date/source
      priority as ROS2 runtime evidence.
  possible target:
    - Docs/Workflows/unreal_renderer.md
    - Docs/Workflows/ros2_runtime_setup.md
  required immediate evidence before patch:
    - coordinate with `ROS2-MEM-008`; do not duplicate if one source-priority
      note already covers it
```

### Keep Cache-Only / Needs Current Evidence

These items are high-risk and must not be written as final docs until the
latest source files, result files, and manual-review state are checked again.

```text
SUNRAY-MEM-002:
  reason:
    - MID-360 placement, scale, and yaw-like numeric values are cache-only
      audit constraints, not final formal parameters.
  next:
    - re-read current source manifests and accepted asset review result before
      promoting any number

SUNRAY-MEM-003:
  reason:
    - propeller placement is an assembly-constraint audit, not a runtime
      parameter commit.
  next:
    - use current visual audit and source-chain evidence; do not fix with
      manual yaw/Z/XY tweaking from old chat

UE-ROS-MEM-003:
  reason:
    - the Factory current gate opens manual UE/RViz review but does not prove
      final product acceptance.
  next:
    - use the latest `*_CURRENT` gate and result manifest first

UE-ROS-MEM-004:
  reason:
    - FAST-LIO status was route-specific and historically contradictory.
  next:
    - read current runtime candidate files and latest FAST-LIO result manifests
      before any formal claim

PARAM-MEM-003:
  reason:
    - numeric values such as mass, inertia, rotor positions, motor constants,
      and lift-coefficient conversions are seed/audit values only.
  next:
    - require a complete identification bundle before any numeric promotion
  round3_disposition:
    - rejected_for_numeric_promotion

PARAM-MEM-006:
  reason:
    - real Sunray150 parameter identification is a separate long-running task,
      not completed by this migration.
  next:
    - start from `Docs/Workflows/identify_quadrotor_parameters.md` if the user
      asks for actual identification
  round3_disposition:
    - routed_to_existing_workflow

CODEGEN-MEM-007:
  reason:
    - time-varying and per-controller SIL remain open.
  next:
    - require the target controller's own generated code hash, options
      snapshot, MWORKS reference trace, and SIL comparison

COAGENT-MEM-004:
  reason:
    - visible department communication was historically fragile and was not
      live-checked in this migration round.
  next:
    - run current visibility checks only under a separate infrastructure or
      CoAgent task
```

### Rejected Or Superseded History To Preserve

These are useful because they prevent future conversations from repeating bad
routes. They should be documented as rejected history only, not as current work.

```text
SUNRAY-MEM-004:
  rejected_or_pending:
    - simple PBR recolor/material candidate is not accepted as final
    - no UE export until manual material audit passes
  preserve_as:
    - rejected route / pending visual-review state

OLD MID-360 PROXY ROUTE:
  rejected:
    - proxy base/dome geometry is diagnostic only
  preserve_as:
    - superseded geometry route

OLD TOY MAPPING ROUTE:
  rejected:
    - keyboard motion, grid cells, static point clouds, HTML map review, and
      hand-fabricated mapping are smoke-only or rejected product routes
  preserve_as:
    - explicit anti-regression memory

OLD CODEX SYNC ASSUMPTION:
  superseded:
    - App/VSCode/CLI live session sync cannot be relied on as durable project
      memory
  preserve_as:
    - reason for this cache workflow

OLD SINGLE-CAUSE CODEX APP THEORY:
  superseded:
    - WSL versus Windows alone is not the established App hang root cause
  preserve_as:
    - debug history under Docs/Workflows/debug_mcp.md

OLD PARAMETER IDENTIFICATION ASSUMPTION:
  rejected:
    - treating SDF seeds, public specs, geometry, controller smoke, or old chat
      numeric values as identified Sunray150 physical truth
  preserve_as:
    - provenance guard for future parameter/report work

OLD CODEGEN OVERGENERALIZATION:
  rejected:
    - treating `translate_model`, zero-input SIL, or PID-demo constant-input SIL
      as proof that all generated controllers are runtime-authoritative
  preserve_as:
    - codegen/SIL anti-regression memory

OLD SCENE ACCEPTANCE COLLAPSE:
  rejected:
    - collapsing Fab inventory, truth artifact, active content link, rendered
      load, manual visual acceptance, and final product acceptance into one
      "accepted scene" claim
  preserve_as:
    - scene-source state-disambiguation guard

OLD ROS2/FAST-LIO GLOBAL STATUS:
  rejected:
    - treating one old candidate, blocker, or runtime-status file as the latest
      global FAST-LIO answer
  preserve_as:
    - source-priority and route/date-specific evidence guard

OLD COAGENT EXPANSION ASSUMPTION:
  rejected:
    - treating design-only CoAgent docs, shadow packets, skills/MCP catalogs,
      or this migration task as approval for runtime, transport, automation,
      department, notification, or tool expansion
  preserve_as:
    - CoAgent scope-gate guard
```

## Next Round Instructions

For the next new conversation:

1. Read `PROGRESS.md` and ledger row `SESSION-MEMORY-MIGRATION-20260604`.
2. Read this map before opening any formal target document.
3. Pick one bucket item only, re-read its current evidence and target doc, then
   either patch that one target narrowly or mark the item rejected/superseded.
4. Run path-limited checks for the changed files.
5. Update this map with the final promoted target or rejection reason.

The full migration is not complete until all high-risk items have either a
promoted target, a rejected/superseded status, or an explicit user-review
blocker.
