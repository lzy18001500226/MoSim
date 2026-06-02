---
name: mosim-unreal-development
description: Use when editing, validating, or extending MoSim's live Unreal Editor MCP implementation under Docs/Skills/Unreal/mosim-unreal. This skill covers UE project context, editor listener health, future AssetRegistry/actor/viewport/truth-export tools, wrappers, and validation workflow; it is not for Epic/Fab library inventory.
---

# MoSim Unreal MCP Development

Use this skill when changing MoSim's `mosim-unreal` server.

## Paths

```text
Docs/Skills/Unreal/mosim-unreal/mcp/server.py
Docs/Skills/Unreal/mosim-unreal/wrappers/mosim-unreal.sh
Docs/Skills/Unreal/mosim-unreal/wrappers/wsl.sh
```

Third-party MCP projects under `Docs/Skills/Unreal/mcp/` are reference material
only. Do not edit them unless the user explicitly asks.

## Validation

After editing the MCP implementation:

```bash
Scripts/UE5/build_unreal_renderer.sh
Scripts/UE5/open_unreal_renderer.sh editor
python3 -m py_compile Docs/Skills/Unreal/mosim-unreal/mcp/server.py
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-tools
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-context
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-assets --limit 5
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-maps --limit 5
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-maps --query Demonstration --limit 20
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-level --timeout 0.5 --limit 5
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-reversible-probe
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-scene-sources --limit 1 --map-limit 2
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-log --lines 20
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-boundary
bash -n Docs/Skills/Unreal/mosim-unreal/wrappers/mosim-unreal.sh
bash -n Docs/Skills/Unreal/mosim-unreal/wrappers/wsl.sh
```

The project-owned renderer currently uses UE `5.5` through
`MoSimSceneLibrary.uproject` `EngineAssociation`. Build/open scripts must follow
that association. UE 4.27 scene packs use `UE4Editor.exe` and
`UE4Editor-Cmd.exe`, so version detection must not assume the UE5 executable
names.

`dump-level` may return `ok=false` when Unreal Editor is closed or the listener
is unreachable. That is an expected diagnostic state, not an MCP startup
failure.

`dump-reversible-probe` is safe by default because it does not execute writes.
Only use `--execute` when a real review map is loaded and the user expects a
temporary spawn/move/delete actor probe. Do not execute it on `/Engine/Maps/Entry`
or on an unidentified map.

`dump-scene-sources` is compact by default. Use `--detail` only for one or two
targeted projects after confirming the response size is manageable.
The server enforces response bounds: detailed scene-source scans are clamped to
3 projects, compact scans to 50 projects, log tails to 300 lines, and local
asset/actor samples to bounded values.

If the Codex config changes, restart Codex or run `/mcp` in a fresh session to
verify the tool inventory.

After changing `mcp/server.py`, restart the running `mosim-unreal` MCP process
or start a fresh Codex session before judging MCP tool behavior. Existing MCP
stdio server processes keep the old Python module in memory. Validate fixes
with the local CLI first, then with the registered MCP after restart.

`asset_search` and `list_maps` must treat `UE5/MoSimSceneLibrary/Content`
directory junctions as renderer-local content. Package paths should be derived
from the lexical renderer path (`/Game/Maps/Demonstration`), not from the
resolved source project path. Map search must prioritize `.umap` files under
`Maps` / `Levels`; otherwise large linked scene packs can spend minutes
walking meshes before returning the requested map.

Local scene activation now uses one active scene source at a time:

```bash
python3 Scripts/UE5/activate_renderer_scene_source.py \
  --scene-source-id local_factoryenvironmentcollect
python3 Scripts/UE5/build_scene_source_registry.py --write
python3 Scripts/UE5/build_scene_source_registry.py --validate \
  UE5/MoSimSceneLibrary/Content/MworksData/scene_source_registry.json
```

Do not keep all `References/UnrealScenes` projects mounted into
`MoSimSceneLibrary/Content` simultaneously. Marketplace/Fab samples commonly
reuse conflicting top-level packages such as `/Game/Blueprints`, `/Game/Meshes`,
and `/Game/Maps`. `activate_renderer_scene_source.py` removes only renderer
links that point into `References/UnrealScenes`, preserves project-owned roots
such as `MworksData`, and links the selected source's top-level Content folders.
For World Partition maps, it also links matching `__ExternalActors__` and
`__ExternalObjects__` companion roots.

After activation, use a bounded renderer load proof rather than assuming a map
opened correctly:

```bash
python3 Scripts/UE5/probe_renderer_map_load.py \
  --scene-source-id local_factoryenvironmentcollect \
  --engine-version 5.5 \
  --json-output Results/tmp/renderer_map_load_probe_factory_active_20260531.json \
  --log-output Results/tmp/renderer_map_load_probe_factory_active_20260531.log \
  --timeout-seconds 60
```

The probe must match the active registry `scene_source_id`,
`renderer_map_asset`, and `renderer_map_package`, and should report `ok=true`,
`loaded_expected_map=true`, and `actor_count>0`. `FactoryEnvironmentCollect` is
the current stable active scene. `ElectricDreamsEnv` has valid truth, but full
renderer loading can exceed 60 seconds during first-time Nanite/static mesh
builds. `DarkRuinsMegascansSample` needs a proper World Partition truth route;
commandlet actor enumeration currently sees only global/postprocess actors.

For manual review of a real linked scene, open the standalone game with the
scene-review mode:

```bash
RESTART_UNREAL_GAME=1 \
UNREAL_EXTRA_ARGS="/Game/Maps/Demonstration" \
Scripts/UE5/open_unreal_renderer.sh review-scene
```

This passes `-MoSimSceneReview`. It disables the old generated
`MworksData/map_open_blocks_render_map.json` preview map and default playback
actor, while keeping the review camera and lighting. Use normal `game` mode
only when intentionally testing MWORKS preview-map playback.

For Factory review, start inside `/Game/Maps/Demonstration` with camera
collision still enabled. The launcher injects the Factory camera default when no
manual camera override is supplied; do not use `-MoSimNoReviewCollision` to get
past an exterior start point. The current Factory default is the map-authored
`PlayerStart` area, approximately `(-5533, 2423, 190) cm` in Unreal coordinates
or `(-55.33, -24.23, 1.90) m` in exported truth coordinates. Do not restore the
older `(-4750, 3850, 180) cm` point because it intersects a CargoCar collision
proxy and blocks entry.

For Derelict review, start inside `/Game/DerelictCorridor/Maps/DerelictCorridor`
at approximately `(8704, -2240, 220) cm`, yaw `90 deg`. This is derived from
the exported truth bounds and replaces the generic MoSim preview-camera default,
which is outside the real corridor.

For imported maps that define their own GameMode, `review-scene` must force
`/Script/MoSimSceneLibrary.MoSimSceneLibraryGameMode` for every reviewed
`/Game/...` map; otherwise the map may spawn its own Pawn and bypass the MoSim
review camera/collision/log contract.
For maps with authored robot/vehicle Pawns, review mode must also keep
PlayerController possession on `MworksReviewCameraPawn` and disable imported
Pawn input. Treat `MWORKS scene-review control enforced:
pawn=MworksReviewCameraPawn... disabled_imported_pawns=N` as the log evidence
that map-local Pawns are not controlling the review session.

Manual map review should prefer white/daytime visibility. `review-scene` also
supports balanced camera/fill-light overrides such as:

```bash
UNREAL_EXTRA_ARGS="/Game/Maps/Demonstration \
  -MoSimReviewCameraX=-5533 -MoSimReviewCameraY=2423 -MoSimReviewCameraZ=190 \
  -MoSimReviewCameraPitch=-6 -MoSimReviewCameraYaw=0 \
  -MoSimReviewHeadLightIntensity=8 -MoSimReviewHeadLightRadius=25000" \
Scripts/UE5/open_unreal_renderer.sh review-scene
```

If a candidate remains visually dark or exploration-like after daylight review
overrides, do not promote it as a primary rendered-map scene. Keep it only as a
special indoor/radar test candidate.
Do not enable forced exposure by default; use `-MoSimDayReview` only for
diagnostics because excessive exposure bias can white out the viewport.

Manual review must keep camera collision enabled. The project review pawn uses
a swept collision sphere so the reviewer cannot fly through walls or scene
boundaries. `-MoSimNoReviewCollision` is diagnostic only; do not use it for
map acceptance. For planning work, rendered visibility is insufficient: export
and validate collision/occupancy truth before accepting a path or UAV route as
wall-safe.

## Expected Tools

`mosim-unreal` should expose at least:

- `ue_health`
- `project_context`
- `editor_listener_health`
- `asset_search`
- `list_maps`
- `current_level_summary`
- `find_level_actors`
- `reversible_actor_probe`
- `scene_source_status`
- `scene_truth_export_plan`
- `editor_log_summary`
- `tool_boundary`

## Boundary

Allowed:

- MoSim UE project context and listener health;
- local Content asset/map search;
- live read-only current-level and actor queries when the editor listener is up;
- redacted editor log summary;
- local scene-source and truth-export planning diagnostics;
- planned-only or explicitly executed reversible actor probe;
- future persistent actor/material/Blueprint/map edits;
- future viewport capture, PIE control, and truth export execution.

Not allowed in this MCP:

- Epic/Fab login or Launcher download automation;
- account-library inventory;
- raw account cache dumping;
- Marketplace license decisions.

Use `Docs/Skills/Unreal/mosim-epic` for Epic/Fab/scene-source inventory.
