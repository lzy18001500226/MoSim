---
name: mosim-unreal-editor-mcp
description: Use when operating MoSim's Unreal Editor MCP for live UE scene, actor, Blueprint, material, or viewport work. This skill is only for the UE Editor MCP boundary; use mosim-epic-fab-library for Epic/Fab asset inventory.
---

# MoSim Unreal Editor MCP

Use this skill for live Unreal Editor automation after an editable UE project is
open.

## Boundary

`unreal_engine` edits a running Unreal Editor project. It is not responsible for
reading the Epic/Fab account library. Use `mosim_epic_library` first when the
question is "what scenes/assets do we have?"

## Preflight

Check the editor-side listener before actor/Blueprint calls:

```bash
python3 Scripts/UE5/probe_unreal_mcp_listener.py --wrapper-route-only --timeout 1
```

Then prove live editor read/write authority before claiming scene modification:

```bash
uv run python Scripts/UE5/probe_unreal_editor_mcp_tools.py \
  --json-output Results/tmp/unreal_mcp_editor_probe_<date>.json
```

The round-trip probe creates a temporary uniquely named probe actor, modifies
it, deletes it, and verifies cleanup. Treat its JSON output as temporary
evidence; do not commit `Results/tmp` artifacts. Do not force a reused fixed
actor name unless you have restarted the editor or verified no stale name state
remains.

For the project-owned renderer:

```bash
python3 Scripts/UE5/check_unreal_s0_s1_readiness.py --build
```

Add `--check-listener` only when preparing for interactive editor review.

## Operating Rules

1. A successful `/mcp` tool list proves only the stdio MCP server, not the UE
   Editor listener.
2. If the listener probe fails, stop actor/Blueprint calls and continue only
   source-level work.
3. Resolve asset paths through real project content. Do not guess `/Game/...`
   paths.
4. Batch UE edits, then verify with a read-only scene/actor probe.
5. Keep Epic/Fab inventory and downloads outside this skill.
6. Keep `MworksUnrealRenderer.uproject` plugin paths aligned with the current
   repository layout. After the `Skills` tree moved under `Docs/Skills`, the
   project must resolve `UnrealMCP` from
   `../../Docs/Skills/Unreal/unreal-engine-mcp/FlopperamUnrealMCP/Plugins`.
7. After a candidate scene opens, export collision truth before claiming planner
   readiness:

```bash
py Scripts/UE5/export_unreal_scene_truth.py export --scene-id <scene_id> --map-id <map_id>
```

Run validation from the normal project shell with:

```bash
uv run python Scripts/UE5/export_unreal_scene_truth.py validate <truth-json>
```

## Architecture Note

Preferred UE Editor MCP architecture is:

```text
agent -> Python/TypeScript MCP server -> TCP/WebSocket/HTTP -> C++ UE plugin
```

C++ belongs in the editor-side bridge because it has reliable access to
Blueprint graphs, AssetRegistry, package saving, PIE, and game-thread dispatch.
