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

## Architecture Note

Preferred UE Editor MCP architecture is:

```text
agent -> Python/TypeScript MCP server -> TCP/WebSocket/HTTP -> C++ UE plugin
```

C++ belongs in the editor-side bridge because it has reliable access to
Blueprint graphs, AssetRegistry, package saving, PIE, and game-thread dispatch.
