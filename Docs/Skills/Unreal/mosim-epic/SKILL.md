---
name: unreal-engine-mcp-development
description: Use when editing, validating, or extending MoSim's own Unreal Engine MCP implementation under Docs/Skills/Unreal/unreal-engine-mcp. This skill covers the project-owned MCP source, wrappers, tool boundary, and validation workflow; it is not for generic Unreal scene authoring.
---

# Unreal Engine MCP Development

Use this skill when changing MoSim's own `unreal_engine` MCP server.

## Paths

```text
Docs/Skills/Unreal/unreal-engine-mcp/mcp/server.py
Docs/Skills/Unreal/unreal-engine-mcp/wrappers/unreal_engine.sh
Docs/Skills/Unreal/unreal-engine-mcp/wrappers/wsl.sh
```

Third-party MCP projects under `Docs/Skills/Unreal/mcp/` are reference material
only. Do not edit them unless the user explicitly asks.

## Validation

After editing the MCP implementation:

```bash
python3 -m py_compile Docs/Skills/Unreal/unreal-engine-mcp/mcp/server.py
python3 Docs/Skills/Unreal/unreal-engine-mcp/mcp/server.py dump-tools
python3 Docs/Skills/Unreal/unreal-engine-mcp/mcp/server.py dump-context
python3 Docs/Skills/Unreal/unreal-engine-mcp/mcp/server.py dump-boundary
bash -n Docs/Skills/Unreal/unreal-engine-mcp/wrappers/unreal_engine.sh
bash -n Docs/Skills/Unreal/unreal-engine-mcp/wrappers/wsl.sh
```

If the Codex config changes, restart Codex or run `/mcp` in a fresh session to
verify the tool inventory.

## Boundary

Allowed:

- MoSim UE project context and listener health;
- scene-source registry and acceptance gates;
- truth-export planning;
- small, reversible editor probes after the listener is proven reachable.

Not allowed in this MCP:

- Epic/Fab login or Launcher download automation;
- raw account cache dumping;
- arbitrary editor Python execution as a default path;
- broad game-specific tools copied from reference MCP projects.

Read `docs/architecture.md` before expanding the tool surface.
