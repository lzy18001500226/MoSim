# MoSim Epic MCP

Project-owned MCP server for Epic/Fab/Launcher inventory and MoSim
scene-source readiness.

This folder is not the live Unreal Editor MCP. The live UE Editor MCP is
`Docs/Skills/Unreal/mosim-unreal`.

## Layout

```text
mcp/server.py        MCP server and CLI diagnostics
wrappers/wsl.sh      WSL stdio entry used by Codex
wrappers/mosim-epic.sh
                    Stable configured wrapper for the Epic/scene-source MCP
docs/architecture.md
                    Boundary and expansion plan
```

## Commands

```bash
python3 Docs/Skills/Unreal/mosim-epic/mcp/server.py dump-tools
python3 Docs/Skills/Unreal/mosim-epic/mcp/server.py dump-health
python3 Docs/Skills/Unreal/mosim-epic/mcp/server.py dump-boundary
Docs/Skills/Unreal/mosim-epic/wrappers/mosim-epic.sh
```

## Codex Registration

The active Codex MCP server name should be:

```toml
[mcp_servers.mosim-epic]
command = "/mnt/c/Users/HP/Desktop/MoSim/Docs/Skills/Unreal/mosim-epic/wrappers/mosim-epic.sh"
```

The old `mosim_epic_library` server name and
`Scripts/UE5/mosim_epic_library_mcp_wsl_wrapper.sh` path are legacy and should
not be used for new Codex sessions.

## Boundary

This MCP owns sanitized Epic/Fab/Launcher inventory, scene-source registry
checks, scene-source acceptance gates, and truth-export planning for already
local editable UE scenes.

It does not own live Unreal Editor actor edits, Blueprint/material work,
viewport capture, PIE/runtime control, Epic/Fab login, Launcher downloads, or
Marketplace license decisions.
