# Round 1 Scene Source And Renderer Memory Cache

Date: 2026-06-04 CST

Scope: first cache pass for long-session memory about UE scene-source
selection, accepted/deferred/rejected maps, renderer review-camera rules, scene
truth exports, and old S0/S1/blockout routes. This is cache-only. It does not
promote any current scene, manual review status, or runtime evidence as final
truth without a later round-2 verification.

## Status

```text
round: 1
topic: UE scene source and renderer route
status: candidate_cache_created
risk: high
formal_docs_patched_this_round: none
cache_only: true
source_pointers_re_read:
  - Docs/Workflows/unreal_renderer.md
  - Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md
  - Docs/Workflows/agent_task_ledger.md
  - PROGRESS.md
  - UE5/MoSimSceneLibrary/Content/MworksData/scene_source_registry.json
  - UE5/MoSimSceneLibrary/Content/MworksData/active_scene_links.json
  - Results/unreal_scene_mapping/UE_SCENE_RUNTIME_READINESS.md
  - Results/unreal_scene_mapping/UE_SCENE_RUNTIME_BUNDLE_STATUS.md
  - Results/unreal_scene_mapping/UE_SCENE_CLOSED_LOOP_STATUS.md
  - Results/unreal_scene_mapping/UE_SCENE_RUNTIME_READINESS.json
  - Results/unreal_scene_mapping/UE_SCENE_CLOSED_LOOP_STATUS.json
```

This cache deliberately preserves contradictions and historical rejects. Scene
selection, visual acceptance, truth export, and runtime review are high-risk
because they depend on the latest activated source, UE content links, manual
review, and current result manifests.

## Candidate Items

### SCENE-MEM-001 - Current Main Scene Pool Is Local Editable Fallback

```text
round: 1
status: candidate
risk: high
candidate_statement:
  The current scene-source route uses local editable Unreal projects under the
  `References/UnrealScenes` fallback until a Fab/Epic asset is actually
  imported or reused in the MoSim UE project with edit access and planning
  truth. Fab/Epic inventory visibility alone is not scene acceptance.
known_sources:
  - `Docs/Workflows/unreal_renderer.md` says Fab/Epic library entries are
    inventory and planning inputs, not accepted scenes.
  - `scene_source_registry.json` records
    `fab_route.status=inventory_visible_not_scene_accepted` and
    `active_strategy=local_editable_fallback_until_fab_import_truth_verified`.
  - `Docs/Workflows/unreal_renderer.md` records the local fallback and
    acceptance gates.
contradictions_or_history:
  Earlier work spent time on Fab/Launcher inventory and asset browsing. That
  history must not be read as "Fab route accepted".
current_evidence_needed:
  Round 2 should re-read the current registry and any newer Epic/Fab import
  proof before deciding the route is still fallback-first.
formal_target_if_promoted:
  Already represented in `Docs/Workflows/unreal_renderer.md`; likely no formal
  patch unless recovery wording is missing.
next_round_action:
  Verify current `scene_source_registry.json` and tool evidence. Keep external
  Launcher/Fab paths redacted.
```

### SCENE-MEM-002 - Factory And Derelict Are Current Truth-Backed Scene Set,
But Activation Is Ambiguous

```text
round: 1
status: candidate_with_contradiction
risk: high
candidate_statement:
  `FactoryEnvironmentCollect` and `DerelictCorridorMegascans` are the current
  local truth-backed rendered-map set in project docs/results, but the exact
  current primary/active scene must be rechecked before a new answer or formal
  patch.
known_sources:
  - `Docs/Workflows/unreal_renderer.md` lists Factory and Derelict as current
    main candidates with manual rendered-review and collision-truth evidence.
  - `UE_SCENE_CLOSED_LOOP_STATUS.json` contains both
    `factoryenvironmentcollect` and `derelictcorridormegascans` with
    `status=ready_smoke_validated`.
  - `scene_source_registry.json` records both scene sources as
    `accepted_local_truth_fallback` with truth artifacts.
contradictions_or_history:
  - `Docs/Workflows/unreal_renderer.md` says the current registry state uses
    `primary_scene_source_id: local_factoryenvironmentcollect`.
  - The current `scene_source_registry.json` policy field says
    `primary_scene_source_id=local_derelictcorridormegascans`.
  - The current `active_scene_links.json` says the activated content links are
    for `local_factoryenvironmentcollect`.
current_evidence_needed:
  Round 2 must check the current registry, active links, latest activation
  command, and renderer load proof before saying which scene is primary or
  active.
formal_target_if_promoted:
  Possibly `Docs/Workflows/unreal_renderer.md` if the primary/active wording is
  stale after verification.
next_round_action:
  Reconcile "primary scene", "active content links", and "current review target"
  as separate fields; do not collapse them into one claim.
```

### SCENE-MEM-003 - Scene Acceptance Requires Import/Edit, Render, Truth, MCP,
And Manual Review Gates

```text
round: 1
status: candidate
risk: high
candidate_statement:
  A scene is not accepted just because it exists in inventory or opens once.
  Acceptance requires editable assets, rendered review, explicit planning
  truth, MCP/automation route or documented fallback, and user manual visual
  review for the map/animation/video view.
known_sources:
  - `Docs/Workflows/unreal_renderer.md` section `Scene Acceptance Gates`.
  - `scene_source_registry.json` carries scene source status, truth artifacts,
    renderer map package, and fallback strategy.
contradictions_or_history:
  Older generated maps, one-room demos, packaged runtime-only scenes, and
  black/partial map loads were explored but are not accepted scene sources.
current_evidence_needed:
  Round 2 should re-read current scene-source audit output, renderer load
  proofs, truth artifacts, and any manual review packets.
formal_target_if_promoted:
  Already represented in `Docs/Workflows/unreal_renderer.md`.
next_round_action:
  Mark as already formalized or add only a narrow recovery pointer.
```

### SCENE-MEM-004 - Rejected And Deferred Map Memory

```text
round: 1
status: candidate
risk: high
candidate_statement:
  The current rejected/deferred map memory must be preserved to prevent new
  conversations from repeating old map routes.
known_sources:
  - `Docs/Workflows/unreal_renderer.md` current local review candidates table.
  - `scene_source_registry.json` for local project audit status.
candidate_classification:
  - `CityParkEnvironmentCollec`: deferred; Showcase variants stayed black while
    meshes built.
  - `CitySample`: rejected for immediate linked-content use; black maps and
    missing CitySample-specific classes/plugins in `MoSimSceneLibrary`.
  - `DarkRuinsMegascansSample`: rejected for main daytime rendered scene use;
    keep only as special dark/indoor/radar reference.
  - `ElectricDreamsEnv`: deferred/high-risk; truth artifact exists but rendered
    review/load path is not current main scene evidence.
  - `MedievalVillageMegascansS`: rejected for immediate main rendered scene
    use after black review and compatibility/static-mesh issues.
  - `ABoyandHisKite`: rejected for immediate linked-content use because
    GoldenPath stalls and TutorialMap is mostly black/missing parent classes.
  - `FPS-Shooter-Unreal`: rejected for formal scene-library use; keep as
    lightweight UE launch/control smoke only.
contradictions_or_history:
  `scene_source_registry.json` may label some assets such as ElectricDreams as
  truth-ready because collision truth exists. That is not the same as current
  main rendered-scene acceptance.
current_evidence_needed:
  Round 2 should re-read the current table, registry, and any new manual review
  packets before updating classifications.
formal_target_if_promoted:
  Already represented in `Docs/Workflows/unreal_renderer.md`; cache may be
  enough unless the table is stale.
next_round_action:
  Verify each rejected/deferred status against the latest registry and visual
  review evidence.
```

### SCENE-MEM-005 - Scene Truth Is Validation Oracle, Not Planner Input

```text
round: 1
status: candidate
risk: high
candidate_statement:
  Exported UE collision/occupancy truth is a validation oracle for mapping and
  route checks. It must not be fed to the planner as a known global map.
known_sources:
  - `AGENTS.md` Unreal Mapping Window Rule.
  - `Docs/Workflows/unreal_renderer.md` scene truth and runtime readiness
    sections.
  - `UE_SCENE_RUNTIME_READINESS.md/json` records
    `global_truth_used_by_planner=false`.
  - `UE_SCENE_CLOSED_LOOP_STATUS.json` records
    `global_truth_available_to_planner=false` for both Factory and Derelict.
contradictions_or_history:
  Offline truth, local-known-map frames, and rendered debug overlays can look
  like planner input. They are not proof of a closed planner unless source
  labels and truth-policy flags say so.
current_evidence_needed:
  Round 2 should re-read the latest status JSON and the scenario result before
  quoting any route or path claim.
formal_target_if_promoted:
  Already represented in `AGENTS.md` and `Docs/Workflows/unreal_renderer.md`.
next_round_action:
  Preserve as already formalized or cross-link in the round-3 map.
```

### SCENE-MEM-006 - File Loop And Smoke Evidence Are Not Runtime Review

```text
round: 1
status: candidate
risk: high
candidate_statement:
  `ready_smoke_validated`, `file_loop_ready=true`, generated replay files, and
  MWORKS `smoke_only` metrics are not final runtime/manual-review or controller
  performance evidence.
known_sources:
  - `UE_SCENE_RUNTIME_READINESS.md` says it is a preflight report, not a new
    simulation result.
  - `UE_SCENE_RUNTIME_BUNDLE_STATUS.md` says runtime evidence requires native
    UE/RViz2 windows plus FAST-LIO topic recording/evaluation.
  - `UE_SCENE_CLOSED_LOOP_STATUS.md/json` records `MWORKS Quality=smoke_only`.
  - `round2_mworks_controller_evidence_memory_20260604.md`.
contradictions_or_history:
  Old summaries can overstate "closed loop" or "runtime ready". The current
  JSON explicitly keeps runtime blockers and claim boundaries.
current_evidence_needed:
  Round 2 should re-read current runtime readiness and result metrics before
  any runtime or controller-quality statement.
formal_target_if_promoted:
  Already represented in runtime/evidence workflows.
next_round_action:
  Round 2 should align this with MWORKS evidence cache and decide if it belongs
  in the round-3 map.
```

### SCENE-MEM-007 - Renderer Review Camera And `review-scene` Mode Are Safety
Gates

```text
round: 1
status: candidate
risk: high
candidate_statement:
  Real scene visual review must use `review-scene` mode, force the MoSim review
  GameMode/camera, disable old generated preview/blockout and playback actors,
  and keep the review camera collision-constrained.
known_sources:
  - `Docs/Workflows/unreal_renderer.md` review-scene and camera sections.
  - PROGRESS entries about review-camera fixes and old S0/S1 blockout routes.
contradictions_or_history:
  Old generated preview maps, auto-spawned playback actors, imported Pawns, or
  disabled camera collision can create false visual acceptance or false visual
  failure.
current_evidence_needed:
  Round 2 should re-read current `open_unreal_renderer.sh`, review camera C++
  code, and latest UE logs before stating a review was valid.
formal_target_if_promoted:
  Already represented in `Docs/Workflows/unreal_renderer.md`.
next_round_action:
  Verify current scripts/log markers if a new visual-review task starts.
```

### SCENE-MEM-008 - Old S0/S1 And Blockout Routes Are Superseded

```text
round: 1
status: candidate
risk: medium
candidate_statement:
  Old S0/S1 source-level renderer, generated/blockout maps, primitive factory
  scenes, and competition industrial hybrid blockout are historical smoke or
  runtime-reviewable artifacts, not the active main map route.
known_sources:
  - `Docs/Workflows/unreal_renderer.md` current policy retires generated
    grid/STL/semantic-box/blockout routes.
  - `PROGRESS.md` active queues mark UE S0/S1 next round as
    `superseded-by-real-scene-source-route`.
  - `PROGRESS.md` records the S1 industrial hybrid blockout as visual blockout
    evidence only, not final art or formal local-avoidance proof.
contradictions_or_history:
  S0/S1 runtime autos-pawn and blockout work produced useful UE/UDP/control
  smoke evidence, but continuing it as final scene work is rejected.
current_evidence_needed:
  Round 2 should check whether any later task reactivated S0/S1 for a specific
  smoke purpose; otherwise preserve only as rejected/superseded history.
formal_target_if_promoted:
  Existing renderer workflow and PROGRESS/ledger.
next_round_action:
  Put in round-3 rejected/superseded bucket unless new evidence reopens it.
```

## Rejected Or Superseded Historical Items

```text
REJ-SCENE-001:
  Treating Fab/Epic inventory visibility as accepted local scene content is
  rejected.

REJ-SCENE-002:
  Treating old generated grid/STL/semantic-box/blockout maps as final visuals
  is rejected.

REJ-SCENE-003:
  Treating S0/S1 blockout/manual UDP smoke as current main scene work is
  superseded by the real editable scene-source route.

REJ-SCENE-004:
  Treating HTML/browser point-cloud review, UE debug overlays, or file previews
  as native RViz/FAST-LIO runtime evidence is rejected.

REJ-SCENE-005:
  Treating `ready_smoke_validated` or `file_loop_ready=true` as final runtime
  readiness is rejected.

REJ-SCENE-006:
  Treating collision-truth export alone as manual visual acceptance or semantic
  map completion is rejected.
```

## Round 2 Backlog

1. Re-read the current `scene_source_registry.json`, `active_scene_links.json`,
   and `Docs/Workflows/unreal_renderer.md` before any statement about the
   current primary or active scene.
2. Reconcile `primary_scene_source_id`, active content links, and review target
   as separate fields.
3. Re-read latest renderer load proofs, UE logs, runtime readiness reports, and
   manual review packets before calling a scene visually accepted.
4. Re-read `UE_SCENE_CLOSED_LOOP_STATUS.json` and scene metrics before quoting
   path cells, LiDAR points, collision clearance, or MWORKS smoke status.
5. Classify rejected/deferred maps against the current review-candidate table
   and registry.
6. Only after round 2, update
   `round3_promotion_rejection_map_20260604.md` with any narrow promotion or
   rejection decisions.

## Do Not Promote Yet

- Which scene is "current primary" without reconciling registry, active links,
  and latest launch target.
- Any rejected/deferred scene as accepted because it has an inventory entry or
  truth file.
- Any runtime review claim without native UE/RViz2/FAST-LIO topic evidence.
- Any full controller/planner acceptance from file-loop, smoke-only, or
  offline replay artifacts.
