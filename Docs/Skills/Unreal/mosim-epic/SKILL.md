---
name: mosim-epic-development
description: Use when editing, validating, or extending MoSim's Epic/Fab/scene-source MCP implementation under Docs/Skills/Unreal/mosim-epic. This skill covers sanitized Epic/Fab inventory, scene-source registry checks, acceptance gates, and truth-export planning; it is not for live Unreal Editor scene authoring.
---

# MoSim Epic MCP Development

Use this skill when changing MoSim's `mosim-epic` server.

## Paths

```text
Docs/Skills/Unreal/mosim-epic/mcp/server.py
Docs/Skills/Unreal/mosim-epic/wrappers/mosim-epic.sh
Docs/Skills/Unreal/mosim-epic/wrappers/wsl.sh
```

Third-party MCP projects under `Docs/Skills/Unreal/mcp/` are reference material
only. Do not edit them unless the user explicitly asks.

## Validation

After editing the MCP implementation:

```bash
python3 -m py_compile Docs/Skills/Unreal/mosim-epic/mcp/server.py
python3 Docs/Skills/Unreal/mosim-epic/mcp/server.py dump-tools
python3 Docs/Skills/Unreal/mosim-epic/mcp/server.py dump-health
python3 Docs/Skills/Unreal/mosim-epic/mcp/server.py dump-boundary
bash -n Docs/Skills/Unreal/mosim-epic/wrappers/mosim-epic.sh
bash -n Docs/Skills/Unreal/mosim-epic/wrappers/wsl.sh
```

If the Codex config changes, restart Codex or run `/mcp` in a fresh session to
verify the tool inventory.

## Boundary

Allowed:

- sanitized Epic/Fab/Launcher inventory;
- scene-source registry and acceptance gates;
- truth-export command planning for already local editable UE scenes.

Acceptance language:

- Fab visibility is not enough. A source is useful only after it becomes local
  editable Unreal content or an explicitly accepted local scene-source fallback.
- Rendering is not enough. The selected source must have a planning truth path:
  collision, semantic, occupancy, or an approved export plan that can generate
  those files from the local UE scene.

Not allowed in this MCP:

- live UE Editor actor, Blueprint, material, viewport, or PIE operations;
- Epic/Fab login or Launcher download automation;
- raw account cache dumping;
- Marketplace license decisions.

Use `Docs/Skills/Unreal/mosim-unreal` for live Unreal Editor automation.
