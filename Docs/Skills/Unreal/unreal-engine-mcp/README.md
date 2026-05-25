# Unreal Engine MCP

Project-owned MCP server for MoSim Unreal automation.

This folder contains MoSim's own `unreal_engine` MCP implementation.
Third-party Unreal MCP projects live under `Docs/Skills/Unreal/mcp/` and are
references only.

## Layout

```text
mcp/server.py       MCP server and CLI diagnostics
wrappers/wsl.sh     WSL stdio entry used by Codex
wrappers/unreal_engine.sh
                   Stable configured wrapper for the `unreal_engine` server name
wrappers/legacy_flopperam_wsl.sh
                   Retained rollback wrapper for the previous third-party MCP
docs/architecture.md
                   Design boundary and expansion plan
```

## Commands

```bash
python3 Docs/Skills/Unreal/unreal-engine-mcp/mcp/server.py dump-tools
python3 Docs/Skills/Unreal/unreal-engine-mcp/mcp/server.py dump-context
python3 Docs/Skills/Unreal/unreal-engine-mcp/mcp/server.py dump-boundary
Docs/Skills/Unreal/unreal-engine-mcp/wrappers/unreal_engine.sh
```

## Boundary

This MCP owns MoSim UE project context, editor-listener health, scene-source
registry, Fab-route acceptance gates, and planning-truth export planning.

It does not own Epic/Fab login, Launcher downloads, raw account cache parsing,
or Marketplace license decisions.
