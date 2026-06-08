# Round 2 Scene Source And Renderer Memory Audit

Date: 2026-06-04 CST

Scope: verify long-session memory about UE scene-source selection, accepted /
deferred / rejected maps, active renderer links, scene truth, runtime-review
boundaries, and old S0/S1/blockout routes against current project files. This
is cache-only. It does not promote any scene, manual review status, runtime
state, or visual acceptance as final truth.

## Status

```text
round: 2
topic: UE scene source and renderer route
status: mixed_round2_verified_and_needs_round3
risk: high
formal_docs_patched_this_round: none
cache_only: true
runtime_or_gui_checks_run: none
```

## Sources Re-Read

| Source | Finding |
|---|---|
| `Docs/Workflows/unreal_renderer.md` | Formal workflow says Fab inventory is not scene acceptance, records Factory and Derelict as current main candidates, records rejected/deferred scene routes, and separates UE/RViz/FAST-LIO evidence. |
| `UE5/MoSimSceneLibrary/Content/MworksData/scene_source_registry.json` | Registry policy says `active_strategy=local_editable_fallback_until_fab_import_truth_verified` and `primary_scene_source_id=local_derelictcorridormegascans`; scene records include Derelict, Factory, and ElectricDreams truth artifacts, with different renderer/import fields. |
| `UE5/MoSimSceneLibrary/Content/MworksData/active_scene_links.json` | Active linked content currently points to `scene_source_id=local_factoryenvironmentcollect` and creates Factory content junctions into `UE5/MoSimSceneLibrary/Content/`. |
| `Results/unreal_scene_mapping/UE_SCENE_CLOSED_LOOP_STATUS.md/json` | Factory and Derelict are `ready_smoke_validated`, with `MWORKS Quality=smoke_only`, collision pass, and FAST-LIO handoff only `ready_for_ros2_replay`. |
| `Results/unreal_scene_mapping/UE_SCENE_RUNTIME_READINESS.md` | Preflight only; file loop ready but runtime was not ready in that snapshot. Global truth is validation oracle only. |
| `Results/unreal_scene_mapping/UE_SCENE_RUNTIME_BUNDLE_STATUS.md` | Execution contract summary, not runtime evidence; both scenes had runtime dependencies blocked in that older status. |
| `Results/unreal_scene_mapping/factoryenvironmentcollect/runtime_review_bundle.md` | Current Factory bundle is `ready_for_manual_rviz_ue_review`, but explicitly says it is a launch package and not proof that manual review already ran. |
| `Docs/Cache/session_memory_migration/02_round2_review/round2_ue_ros_fastlio_memory_20260604.md` | Current Factory Gate B opens manual UE/RViz review only; old keyboard/grid/static/HTML routes are rejected. |

## Round 2 Findings

### SCENE-MEM-001 - Fab Inventory Is Not Accepted Scene Content

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  The current scene-source route remains local editable fallback until a
  Fab/Epic asset is actually imported or reused in MoSim with edit access and
  planning truth. Fab/Epic inventory visibility alone is not acceptance.
current_evidence:
  - `scene_source_registry.json` policy:
    `active_strategy=local_editable_fallback_until_fab_import_truth_verified`.
  - `Docs/Workflows/unreal_renderer.md` says an owned Fab entry becomes a
    scene source only after local editable content, renderer load proof, and a
    truth artifact.
contradictions_or_history:
  Long-session Fab/Launcher inventory work is useful discovery history, but it
  did not make a Fab asset the current scene source.
formal_target_if_promoted:
  Already represented in `Docs/Workflows/unreal_renderer.md`.
next_round_action:
  Round 3 can mark already formalized unless the workflow index needs a short
  recovery pointer.
```

### SCENE-MEM-002 - Factory And Derelict Are Truth-Backed, But Primary/Active Is Ambiguous

```text
round: 2
status: round2_verified_for_cache_needs_round3_disambiguation
risk: high
candidate_statement:
  FactoryEnvironmentCollect and DerelictCorridorMegascans are current
  truth-backed local scene candidates. However, "primary scene", "active
  content links", and "manual review target" are currently separate and partly
  contradictory facts.
current_evidence:
  - `Docs/Workflows/unreal_renderer.md` lists both as current main candidates
    and later records `primary_scene_source_id: local_factoryenvironmentcollect`.
  - `scene_source_registry.json` policy currently records
    `primary_scene_source_id=local_derelictcorridormegascans`.
  - `active_scene_links.json` currently records
    `scene_source_id=local_factoryenvironmentcollect`.
  - `scene_source_registry.json` Derelict record has
    `imported_into_renderer=true`, `renderer_map_package=
    /Game/DerelictCorridor/Maps/DerelictCorridor`, and truth artifact
    `derelictcorridormegascans_collision_truth.json`.
  - `scene_source_registry.json` Factory record has planning truth and truth
    artifact `factoryenvironmentcollect_collision_truth.json`, but the
    per-scene `imported_into_renderer=false` and renderer map fields are empty
    even though `active_scene_links.json` links Factory content.
contradictions_or_history:
  A future answer must not collapse registry primary, active links, latest
  runtime review bundle, and manual visual acceptance into one phrase such as
  "current scene" without a fresh check.
formal_target_if_promoted:
  Possible narrow patch to `Docs/Workflows/unreal_renderer.md` only after
  round-3 rechecks current registry, active links, and load/review evidence.
next_round_action:
  Round 3 should define and verify separate fields:
  `registry_primary`, `active_content_links`, `latest_review_target`,
  `latest_manual_review_status`.
```

### SCENE-MEM-003 - Scene Acceptance Gates Are Formal, But Truth Is Not Visual Acceptance

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  Scene acceptance requires import/edit access, render/load proof, planning
  truth, and manual visual review. A truth artifact or registry status alone
  is not full visual/runtime acceptance.
current_evidence:
  - `Docs/Workflows/unreal_renderer.md` records scene acceptance gates:
    import/edit, render, and planning truth.
  - `scene_source_registry.json` includes ElectricDreams with
    `planning_truth_ready=true` and a truth artifact, but `imported_into_renderer=false`
    and empty renderer map fields.
  - `Docs/Workflows/unreal_renderer.md` table still classifies ElectricDreams
    as deferred after rendered review stayed black/non-reviewable.
contradictions_or_history:
  Registry `status=accepted_local_truth_fallback` can be misread as full
  visual acceptance. For ElectricDreams and any similar scene, truth-ready is
  not the same as current rendered-scene acceptance.
formal_target_if_promoted:
  Already represented in `Docs/Workflows/unreal_renderer.md`; possible round-3
  clarification only if the registry wording remains easy to misread.
next_round_action:
  Round 3 should keep "truth-backed" and "visually accepted/current active"
  separate.
```

### SCENE-MEM-004 - Rejected And Deferred Map Memory Is Still Needed

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  Rejected/deferred map classifications must remain recoverable to prevent
  future conversations from resuming bad routes.
current_evidence:
  - `Docs/Workflows/unreal_renderer.md` records CitySample, MedievalVillage,
    ABoyandHisKite, and FPS-Shooter as rejected for immediate main scene use,
    and ElectricDreams as deferred/high-risk.
  - `scene_source_registry.json` marks several assets as
    `needs_truth_extraction_or_proxy` or truth-ready-but-not-renderer-imported.
contradictions_or_history:
  Some rejected/deferred assets can still have inventory entries, openable
  projects, or truth artifacts. Those facts do not override the manual visual
  or renderer acceptance status.
formal_target_if_promoted:
  Already represented in `Docs/Workflows/unreal_renderer.md`; cache-only
  rejected-history may be enough.
next_round_action:
  Round 3 should map old S0/S1/blockout and rejected map routes into
  rejected/superseded buckets unless a new task explicitly reopens one as a
  smoke-only probe.
```

### SCENE-MEM-005 - Scene Truth Is Validation Oracle Only

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  Exported UE collision/occupancy truth is a validation oracle. It must not be
  fed to the planner as known global map input.
current_evidence:
  - `AGENTS.md` Unreal Mapping Window Rule states global UE truth is validation
    oracle only.
  - `UE_SCENE_RUNTIME_READINESS.md` records
    `global_truth_used_by_planner=false`.
  - `UE_SCENE_CLOSED_LOOP_STATUS.md` says global UE occupancy truth is used as
    validation oracle only.
contradictions_or_history:
  Offline truth, local-known-map frames, and debug overlays can look like
  planner input if source labels are not checked.
formal_target_if_promoted:
  Already represented in `AGENTS.md` and `Docs/Workflows/unreal_renderer.md`.
next_round_action:
  Round 3 can mark already formalized.
```

### SCENE-MEM-006 - File Loop And Smoke Evidence Are Not Final Runtime Review

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  `ready_smoke_validated`, file-loop readiness, generated replay files, and
  MWORKS `smoke_only` metrics are not final runtime/manual-review or
  controller-performance evidence.
current_evidence:
  - `UE_SCENE_CLOSED_LOOP_STATUS.md` defines `ready_smoke_validated` as
    file-level truth/mapping, controller-interface MWORKS smoke, and
    collision validation.
  - The same file says `smoke_only` is not a final controller-performance
    claim.
  - `UE_SCENE_RUNTIME_BUNDLE_STATUS.md` says runtime evidence requires native
    UE/RViz2 windows plus FAST-LIO topic recording/evaluation.
  - `runtime_review_bundle.md` for Factory says the bundle is not proof that
    runtime already ran.
contradictions_or_history:
  Historical "closed-loop" wording can overstate the evidence. Current files
  preserve smoke/runtime/final-acceptance boundaries.
formal_target_if_promoted:
  Already represented in result/status files and workflows.
next_round_action:
  Round 3 should keep this as a cache guard and avoid a formal patch unless a
  target doc lacks `smoke_only` wording.
```

### SCENE-MEM-007 - Renderer Review Camera And `review-scene` Rules Are Current Guardrails

```text
round: 2
status: round2_verified_for_cache_needs_live_recheck_before_use
risk: high
candidate_statement:
  Real scene visual review should use the documented review-scene route and
  camera rules; old generated preview/blockout and playback routes must not be
  mistaken for current real-scene acceptance.
current_evidence:
  - `Docs/Workflows/unreal_renderer.md` records `review-scene` mode, review
    camera behavior, accepted vehicle visual gate separation, and later
    sensor/localization gates.
  - Round-1 scene cache and PROGRESS preserve old S0/S1/blockout routes as
    smoke/history.
contradictions_or_history:
  This round did not open UE or inspect current runtime logs. Therefore it
  cannot state that a current review window is valid or accepted.
formal_target_if_promoted:
  Already represented in renderer workflow.
next_round_action:
  For any future visual-review task, re-run the current review command/log
  checks in that same task before claiming visual acceptance.
```

### SCENE-MEM-008 - Old S0/S1 And Blockout Routes Are Superseded For Main Scene Work

```text
round: 2
status: round2_verified_for_cache
risk: medium
candidate_statement:
  Old S0/S1 source-level renderer, generated/blockout maps, primitive factory
  scenes, and competition industrial hybrid blockout are historical smoke or
  runtime-reviewable artifacts, not the active main real-scene route.
current_evidence:
  - `Docs/Workflows/unreal_renderer.md` retires generated
    grid/STL/semantic-box/blockout routes for current main scene evidence.
  - `Docs/Workflows/agent_task_ledger.md` records old S0/S1 rows as completed
    or superseded by later real scene routes.
contradictions_or_history:
  S0/S1 work produced useful UE/UDP/control smoke evidence; that does not make
  it final scene-source work.
formal_target_if_promoted:
  Existing renderer workflow and ledger are enough.
next_round_action:
  Round 3 should preserve as superseded/rejected history only.
```

## Rejected Or Superseded Historical Items

| Historical Item | Current Treatment |
|---|---|
| Fab/Epic inventory visibility as scene acceptance | Rejected. |
| Generated grid/STL/semantic-box/blockout maps as final visuals | Rejected for main scene work; smoke/history only. |
| S0/S1 UDP/blockout work as current main scene route | Superseded by local editable real scene-source route. |
| HTML/browser point-cloud or UE debug overlay as native mapping evidence | Rejected. |
| `ready_smoke_validated` or `file_loop_ready=true` as final runtime readiness | Rejected. |
| Collision-truth export alone as manual visual acceptance | Rejected. |

## Round 3 Promotion Candidates

Only these narrow items are candidates for round 3:

1. A source-state disambiguation note:
   separate `registry_primary`, `active_content_links`, and
   `latest_review_target`.
2. A truth-versus-visual acceptance note:
   truth artifacts do not imply rendered-scene/manual-review acceptance.
3. A rejected-route recovery note:
   Fab inventory, S0/S1/blockout, HTML, and static preview routes are not the
   main evidence path.

No final current-primary-scene, manual visual acceptance, runtime readiness,
controller, planner, or FAST-LIO claim is ready for promotion from this cache.

## Verification Needed Before Round 3

```text
1. Re-read `scene_source_registry.json`, `active_scene_links.json`, and latest
   review/runtime bundles in the same round.
2. Check whether UE logs or manual review packets after this cache supersede
   the current ambiguity.
3. If editing `Docs/Workflows/unreal_renderer.md`, patch only the ambiguous
   recovery wording, not a broad scene-source rewrite.
4. Keep truth-backed, active-linked, loaded, visually accepted, runtime
   reviewed, and final product accepted as separate states.
```
