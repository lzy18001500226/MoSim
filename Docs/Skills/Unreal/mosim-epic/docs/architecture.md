# MoSim Epic MCP Architecture

## Purpose

MoSim needs a narrow MCP for Epic/Fab/Launcher library visibility and
scene-source readiness decisions. This server is intentionally separate from
the live Unreal Editor MCP because account/library concerns and editor object
graph concerns have different safety boundaries.

## Current Shape

```text
Codex
  -> stdio MCP wrapper
  -> Python MCP server
  -> Epic/Fab inventory scripts and scene-source registry scripts
  -> UE5/MoSimSceneLibrary/Content/MworksData
```

Current tools:

```text
epic_library_inventory
epic_scene_library_view
scene_source_registry
scene_source_acceptance
scene_truth_export_plan
tool_boundary
```

## What This MCP Owns

- sanitized local Epic/Fab/Launcher inventory;
- account-owned/cache/vault scene candidate classification;
- scene-source registry refresh and validation;
- acceptance gates that prove renderable scene plus planning truth;
- command planning for truth export from already local editable UE scenes.

## What This MCP Does Not Own

- Epic/Fab login or OAuth;
- Launcher UI automation or Marketplace downloads;
- raw webcache/log dumping;
- live Unreal Editor actor/Blueprint/material/viewport/PIE operations.

## Relationship To `mosim-unreal`

`mosim-epic` answers: "what scene sources do we have and are they accepted?"

`mosim-unreal` answers: "what can the currently opened UE Editor project do,
and can we inspect/edit/export from it?"
