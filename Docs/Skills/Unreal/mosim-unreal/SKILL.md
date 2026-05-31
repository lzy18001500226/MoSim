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
