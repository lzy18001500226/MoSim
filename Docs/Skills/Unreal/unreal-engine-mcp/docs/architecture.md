# MoSim Unreal MCP Architecture

## Purpose

MoSim needs an Unreal automation surface similar in reliability to the MWORKS
MCP tools: small, explicit tools; clear project boundaries; repeatable
diagnostics; and no hidden Launcher or account-side actions.

## Current Shape

```text
Codex
  -> stdio MCP wrapper
  -> Python MCP server
  -> MoSim project scripts and UE listener probes
  -> UE5/MoSimSceneLibrary
```

Current tools:

```text
ue_health
project_context
scene_source_registry
ue_fab_goal_acceptance
scene_truth_export_plan
epic_scene_library_view
tool_boundary
```

## What We Borrow From Reference MCP Projects

From the Unreal MCP folders under `Docs/Skills/Unreal/mcp`, adopt ideas rather
than copying a broad tool surface:

- explicit tool schemas and narrow responsibilities;
- editor-side C++/plugin bridge for operations requiring AssetRegistry,
  Blueprint graph access, package saving, PIE, and game-thread dispatch;
- read-first workflows before write operations;
- reversible edit probes;
- logs and health endpoints before scene mutation.

## What We Avoid

- Launcher/Fab account automation inside `unreal_engine`;
- arbitrary Python execution as a normal editing mechanism;
- one MCP tool that silently does many unrelated operations;
- claiming a scene is usable before renderability and planning truth are both
  verified.

## Expansion Plan

1. Keep the Python MCP as the stable orchestration and diagnostic layer.
2. Add a project-owned UE plugin endpoint when local scene editing needs
   reliable AssetRegistry, Blueprint, map, and collision-truth operations.
3. Add tools in this order:

```text
read-only project/asset/scene query
-> listener health and log readback
-> reversible actor probe
-> scene truth export
-> scene import/link verification
-> controlled map edits
-> simulation playback hooks
```

4. Keep `mosim_epic_library` separate unless a future explicit tool boundary
   proves a merged MCP is simpler and safer.
