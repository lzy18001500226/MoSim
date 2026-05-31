# MoSim Unreal MCP

Project-owned MCP server for live Unreal Editor automation.

This folder owns the UE Editor boundary only. Epic/Fab/Launcher inventory and
scene-source acceptance live in `Docs/Skills/Unreal/mosim-epic`.

## Layout

```text
mcp/server.py       MCP server and CLI diagnostics
wrappers/wsl.sh     WSL stdio entry used by Codex
wrappers/mosim-unreal.sh
                   Stable configured wrapper for the live UE MCP
wrappers/legacy_flopperam_wsl.sh
                   Rollback wrapper for the previous third-party MCP
```

## Commands

```bash
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-tools
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-context
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-assets --query Factory
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-maps
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-maps --query Demonstration --limit 20
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-level --timeout 1
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-reversible-probe
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-scene-sources --limit 3
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-log --lines 80
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-boundary
Docs/Skills/Unreal/mosim-unreal/wrappers/mosim-unreal.sh
```

## Codex Registration

The active Codex MCP server name should be:

```toml
[mcp_servers.mosim-unreal]
command = "/mnt/c/Users/HP/Desktop/MoSim/Docs/Skills/Unreal/mosim-unreal/wrappers/mosim-unreal.sh"
```

The old `unreal_engine` server name and third-party Flopperam wrapper are
legacy rollback paths only. They should not be the default for new MoSim UE
automation sessions.

## Boundary

This MCP owns live UE Editor project context, editor listener health, and future
AssetRegistry-backed scene/asset queries, controlled editor edits, viewport/log
diagnostics, and scene-truth export execution.

It does not own Epic/Fab account inventory, Launcher downloads, Marketplace
license decisions, or raw account cache reading.

Current implemented tools are deliberately read-first:

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

`scene_source_status` is compact by default so MCP responses stay bounded.
Use `detail=true` or CLI `--detail` only for a targeted source.
The server clamps detailed scene-source scans to at most 3 projects, compact
scans to at most 50 projects, log tails to at most 300 lines, and actor/asset
samples to bounded values.

`asset_search` and `list_maps` follow local Content directory junctions because
accepted scene packs are reused in `MoSimSceneLibrary` through ignored Windows
junctions. A running MCP process must be restarted after editing `mcp/server.py`;
otherwise the registered tools can still show old slow scan behavior or empty
package paths even when the local CLI is fixed.

`reversible_actor_probe` defaults to `execute=false`. It only returns the
planned temporary actor operation. Use `execute=true` only after a real review
map is loaded; the probe refuses `/Engine/Maps/Entry` and unknown maps unless
explicitly overridden.

The log tool returns only a bounded, redacted tail. It must not expose Epic
account identifiers, session ids, OAuth tokens, or raw Launcher/Fab cache paths.
