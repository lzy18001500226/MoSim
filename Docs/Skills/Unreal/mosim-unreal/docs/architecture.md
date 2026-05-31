# MoSim Unreal MCP Architecture

## Purpose

MoSim needs a live Unreal Editor automation surface similar in reliability to
the MWORKS MCP tools: small explicit tools, clear project boundaries,
repeatable diagnostics, and read-first workflows.

## Current Shape

```text
Codex
  -> stdio MCP wrapper
  -> Python MCP server
  -> UE editor listener probe
  -> UE5/MoSimSceneLibrary
```

Current tools:

```text
ue_health
project_context
editor_listener_health
asset_search
list_maps
current_level_summary
find_level_actors
reversible_actor_probe
scene_source_status
scene_truth_export_plan
editor_log_summary
tool_boundary
```

## Reference MCP Ideas To Adopt

From the Unreal MCP reference folders under `Docs/Skills/Unreal/mcp`, adopt:

- explicit tool schemas and narrow responsibilities;
- editor-side C++/plugin bridge for AssetRegistry, Blueprint graph access,
  package saving, PIE, viewport capture, and game-thread dispatch;
- read-first workflows before write operations;
- reversible edit probes before persistent scene mutation;
- logs and health endpoints before actor/material/Blueprint operations.

## Expansion Plan

1. Keep the Python MCP as the stable orchestration and diagnostic layer.
2. Keep read-only tools useful without an open editor where possible: project
   context, local Content asset/map search, redacted logs, local scene-source
   status, and truth-export planning.
3. Add or replace the editor-side UE plugin endpoint when reliable
   AssetRegistry, Blueprint, map, and collision-truth operations are needed.
4. Add tools in this order:

```text
project/listener health
-> local asset/map search and redacted editor log summary
-> live read-only level/actor query
-> reversible actor probe
-> viewport screenshot
-> scene truth export execution
-> controlled map edits
-> simulation playback hooks
```

Keep Epic/Fab inventory, scene-source candidate selection, and acceptance gates
in `mosim-epic`.

## Response Size Policy

MCP responses must stay small enough for normal Codex use. `scene_source_status`
therefore returns a compact readiness summary by default: source name, engine,
verdict, counts, top review maps, plugin sample, and truth gap. Full audit rows
are available only through `detail=true` or CLI `--detail`, and should be used
for targeted review of one or two projects. The server clamps detailed
scene-source scans to 3 projects, compact scans to 50 projects, log tails to
300 lines, and local asset/actor samples to bounded values even if a caller
passes a larger limit.

## Write Boundary

The first write-capable surface is `reversible_actor_probe`. It defaults to
`execute=false`, which returns only the planned temporary actor operation. When
explicitly executed, it creates a uniquely named temporary cube, moves it,
deletes it, and does not save the level. It refuses `/Engine/Maps/Entry` and
unidentified maps by default. Persistent actor, material, Blueprint, map-save,
and truth-export writes remain future tools.
