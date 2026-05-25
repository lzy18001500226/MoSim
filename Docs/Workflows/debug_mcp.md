# Debug MCP Workflow

> Purpose: fix MCP configuration or initialization issues.

---

## 1. Success Criteria

For Sysplorer/Syslab, MCP startup is successful when `/mcp` shows tools.
For Unreal, `/mcp` showing `unreal_engine` tools only proves the WSL stdio
wrapper and Python server. Interactive Unreal actor/Blueprint/viewport work is
successful only after the editor-side listener is reachable and one read-only
actor/scene probe succeeds.

Expected:

```text
syslab
Tools: detect_syslab_toolboxes, evaluate_julia_code, ...

sysplorer
Tools: call_code, check_model, simulate_model, result_manager, ...
```

Normal:

```text
Auth: Unsupported
```

Failure:

```text
Tools: (none)
```

Operational rule:

```text
One development round may keep one Sysplorer / Syslab / MWORKS GUI window open
to avoid repeated startup cost and license reactivation. Do not close reusable
MWORKS windows before Git by default.
If a window freezes, shows an unexpected login prompt, or MCP stalls past the
planned timeout, stop the MCP sequence and clean up the clearly identifiable
process/window before continuing.
```

When the task is interactive model review, do not use project scripts as a
wrapper around MCP. Use the MCP tools directly. If the Codex tool surface does
not expose a `sysplorer` namespace, connect to the configured stdio wrapper
and issue JSON-RPC MCP calls directly; record the log under `Results/`.

For `QuadrotorExperiments.Sunray150CompleteSystemGraphical_Sysblock`, follow the
direct sequence in `Docs/Workflows/run_simulation.md`. The key failure classes are:

| Error | Interpretation |
|---|---|
| `错误(1401): 模型重复定义` | A duplicate standalone `.mo` was loaded; this is a workflow error |
| `组件的类型 ... 查找不到` | Required package/controller file was not loaded first |
| `组件引用 x_sum.u1` / `thrust_sum.u1` 查找不到 | Known graphical Sysblock embedding limitation, not an asset-load failure |

Any newly observed MCP/model-loading failure must be written back to the
workflow before the task is considered complete.

---

## 2. Check Current MCP State

Run:

```bash
codex mcp list --json
```

Check that commands use WSL wrapper scripts:

```text
/home/<WSL_USER>/mcp-wrappers/syslab_mcp.sh
/home/<WSL_USER>/mcp-wrappers/sysplorer_mcp.sh
```

---

## 3. Check Wrapper Scripts

```bash
ls -l ~/mcp-wrappers/syslab_mcp.sh
ls -l ~/mcp-wrappers/sysplorer_mcp.sh
```

They should be executable.

If not:

```bash
chmod +x ~/mcp-wrappers/syslab_mcp.sh ~/mcp-wrappers/sysplorer_mcp.sh
```

---

## 4. Check WSL Config

```bash
cat ~/.codex/config.toml
```

Expected:

```toml
[mcp_servers.syslab]
command = "/home/<WSL_USER>/mcp-wrappers/syslab_mcp.sh"
args = []
startup_timeout_sec = 180
tool_timeout_sec = 300

[mcp_servers.sysplorer]
command = "/home/<WSL_USER>/mcp-wrappers/sysplorer_mcp.sh"
args = []
startup_timeout_sec = 180
tool_timeout_sec = 300
```

---

## 5. Remove Windows-Side Conflicting Config

In PowerShell:

```powershell
$cfg = "$env:USERPROFILE\.codex\config.toml"
$content = Get-Content $cfg -Raw

$content = [regex]::Replace(
  $content,
  '(?ms)^\[mcp_servers\.syslab\]\s*.*?(?=^\[mcp_servers\.|\z)',
  ''
)

$content = [regex]::Replace(
  $content,
  '(?ms)^\[mcp_servers\.sysplorer\]\s*.*?(?=^\[mcp_servers\.|\z)',
  ''
)

$content.Trim() | Set-Content $cfg -Encoding UTF8
Get-Content $cfg
```

Reason:

```text
Windows auto-generated MCP config may conflict with WSL wrapper config.
```

Reference only:

```text
C:\Users\HP\.config\opencode\opencode.json
C:\Users\HP\.config\opencode\opencode-mworks.json
C:\Users\HP\.config\opencode\tongyuan-config.json
```

These files are useful for comparing official Windows MCP commands and provider
settings. `tongyuan-oauth-config.json` is a credential file; never copy its
contents into this repository or logs.

---

## 6. Test Wrapper Manually

Sysplorer:

```bash
~/mcp-wrappers/sysplorer_mcp.sh
```

Syslab:

```bash
~/mcp-wrappers/syslab_mcp.sh
```

If a command prints nothing and waits, this may be normal because stdio MCP servers wait for client handshake.

Press `Ctrl+C` after confirming no immediate error.

---

## 7. Check Logs

```bash
tail -n 160 ~/.codex/log/*.log
```

Common issues:

| Symptom | Possible Cause | Fix |
|---|---|---|
| Tools none | MCP process failed | Check wrapper |
| No such file | Wrong path | Check `/mnt/d/...` path |
| No module named mcp | Missing Python package | Install package in Sysplorer Python |
| Julia not found | Wrong julia-root | Check `C:\Users\Public\TongYuan\...` |
| Desktop failure | GUI issue | Use `nodesktop` for Syslab |
| Duplicate servers | Windows config conflict | Remove Windows-side config |

---

## 7.1 Unreal MCP Local Wrapper

The configured MCP server name remains:

```text
unreal_engine
```

The stable WSL wrapper is project-local:

```text
Scripts/UE5/unreal_mcp_wsl_wrapper.sh
```

It currently points to MoSim's own narrow MCP surface:

```text
Scripts/UE5/mosim_unreal_engine_mcp_wsl_wrapper.sh
Scripts/UE5/mosim_unreal_engine_mcp.py
```

The older Flopperam wrapper is retained for rollback only:

```text
Scripts/UE5/unreal_mcp_legacy_flopperam_wsl_wrapper.sh
```

Manual smoke test:

```bash
Scripts/UE5/unreal_mcp_wsl_wrapper.sh
```

If it starts and waits for input, that is normal for stdio MCP. To verify with a
client, send the standard MCP handshake and then `tools/list`; the server should
report MoSim tools such as `ue_health`, `project_context`,
`scene_source_registry`, `ue_fab_goal_acceptance`, and
`scene_truth_export_plan`.

Command-line checks that do not require UE Editor:

```bash
python3 Scripts/UE5/mosim_unreal_engine_mcp.py dump-tools
python3 Scripts/UE5/mosim_unreal_engine_mcp.py dump-context
python3 Scripts/UE5/mosim_unreal_engine_mcp.py dump-boundary
```

Codex MCP config entry, if enabling manually:

```toml
[mcp_servers.unreal_engine]
command = "/mnt/c/Users/HP/Desktop/MoSim/Scripts/UE5/unreal_mcp_wsl_wrapper.sh"
args = []
startup_timeout_sec = 180
tool_timeout_sec = 300
```

Do not register this against opencode config files. The MoSim MCP can report
project context without an open UE Editor. Live actor/Blueprint/viewport work
still requires an editor-side listener. The legacy Flopperam bridge and future
MoSim C++ plugin use `$UNREAL_HOST:$UNREAL_PORT` (default port `55557`) for
editor-side calls.

Before running interactive actor/Blueprint tools, check the editor-side socket:

```bash
python3 Scripts/UE5/probe_unreal_mcp_listener.py --wrapper-route-only --timeout 1
```

If this fails, do not keep retrying actor/Blueprint MCP tools. Fix the Unreal
Editor/plugin/listener route first, or continue only with source-level files and
document the missing viewport evidence.

`--wrapper-route-only` checks the exact route used by
`Scripts/UE5/unreal_mcp_wsl_wrapper.sh`. Without it, the probe also checks practical
diagnostic fallbacks: `UNREAL_HOST` when set, the WSL default gateway, and
`127.0.0.1`. Use `--host <addr>` only when you want to test one explicit route.

Interpret the preflight result before changing code:

| Probe result | Meaning | Next action |
|---|---|---|
| `[OK] Unreal Editor MCP listener reachable` | Editor-side socket is reachable from the current shell | Run one read-only UE MCP actor/scene probe, then proceed to viewport review if it succeeds |
| `ConnectionRefusedError` | No process is listening at that host/port from the current shell | Open the renderer `.uproject`, enable/load `UnrealMCP`, or start the editor-side plugin listener |
| `TimeoutError` or MCP tool timeout | A listener path may be blocked, bound to another interface, or stalled | Check UE log/plugin host binding; avoid repeated actor/Blueprint MCP calls until socket reachability is resolved |

For S0/S1 renderer work, run the combined gate first:

```bash
python3 Scripts/UE5/check_unreal_s0_s1_readiness.py --build
```

Add `--check-listener` only when preparing for interactive viewport review.

Keep this separate from the project-owned external renderer plugin:

```text
UE5/Bridge/
```

`UnrealMCP` controls the editor through MCP. `QuadrotorMworksBridge` receives
MWORKS simulation state for video rendering. They solve different problems.

Project-local Unreal renderer entry:

```text
UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject
```

Open this project in UE 5.7 when using MCP-driven scene setup. It enables both
`UnrealMCP` and `QuadrotorMworksBridge` through project-local plugin search
paths. Do not copy these plugins into `D:\Program Files\Epic Games` unless the
user explicitly asks for a global install.

Interpretation of Unreal MCP checks:

| Check | Meaning |
|---|---|
| MCP `initialize` succeeds | WSL wrapper and Python server are working |
| MCP `tools/list` returns tools | stdio MCP side is usable |
| `get_actors_in_level` returns `Connection refused` | UE Editor plugin is not loaded/listening yet |
| `get_actors_in_level` returns `Connection timeout` | UE Editor plugin listener is unreachable from the MCP server path |
| `get_actors_in_level` returns actors | Editor-side MCP is ready for scene automation |

Always treat the latest probe as authoritative. A previous successful
`get_actors_in_level` result only proves that the editor-side route worked at
that time. If a later read-only tool call times out, the current state is
unavailable until both checks pass again:

```bash
python3 Scripts/UE5/probe_unreal_mcp_listener.py --timeout 1
python3 Scripts/UE5/check_unreal_s0_s1_readiness.py --build --check-listener
```

Do not continue interactive actor, Blueprint, or viewport MCP work from stale
success evidence. Source-level checks and standalone `-game` UDP playback may
continue because they use different routes.

## 7.2 Current MoSim MCP Scope

Current development scope is limited to two MCP boundaries:

```text
unreal_engine        live Unreal Editor automation
mosim_epic_library   Epic/Fab/Launcher library inventory
```

Do not expand this phase into MWORKS, external renderer bridge, downloader,
or full simulator-control MCP work unless the user explicitly reopens that
scope. Skills are still required, but only for these MCP boundaries.

| Boundary | MCP / Tool Role | Why It Is Separate |
|---|---|---|
| Unreal Editor | `unreal_engine` | Live editor scene/Blueprint/material/actor work through an editor listener |
| Epic/Fab/Launcher library | `mosim_epic_library` | Read-only asset inventory from Launcher/Fab caches; not a UE Editor object graph |

Current Unreal MCP audits show the strongest UE authoring design is usually:

```text
Codex/agent
  -> Python/TypeScript MCP server over stdio
  -> WebSocket/TCP/HTTP bridge
  -> C++ plugin inside Unreal Editor
  -> UE Editor APIs on the game/editor thread
```

Reason: Blueprint graphs, AssetRegistry, `GEditor`, PIE, package saving,
Undo/Redo, and thread dispatch are more reliable in a C++ UE plugin than in a
pure external Python script. Python/TypeScript is still useful for MCP schema,
tool descriptions, batching, safety checks, and transport.

This does not mean the Epic/Fab library index should be a C++ UE plugin.
Launcher account cache and VaultCache inventory exist outside the editor, so a
read-only filesystem/cache MCP is a better boundary.

## 7.3 Epic/Fab Library Index MCP

Project-local scripts:

```text
Scripts/UE5/epic_library_index.py
Scripts/UE5/epic_library_view.py
Scripts/UE5/mosim_epic_library_mcp.py
Scripts/UE5/mosim_epic_library_mcp_wsl_wrapper.sh
Scripts/UE5/check_epic_library_inventory.py
Docs/Skills/Unreal/mosim-epic-fab-library/SKILL.md
Docs/Skills/Unreal/mosim-unreal-editor-mcp/SKILL.md
```

Read-only inventory command:

```bash
python3 Scripts/UE5/epic_library_index.py --compact
python3 Scripts/UE5/epic_library_view.py
python3 Scripts/UE5/epic_library_index.py --query Factory
python3 Scripts/UE5/check_epic_library_inventory.py
```

The indexer reads:

```text
C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests\*.item
C:\ProgramData\Epic\UnrealEngineLauncher\LauncherInstalled.dat
C:\ProgramData\Epic\EpicGamesLauncher\VaultCache
C:\ProgramData\Epic\EpicGamesLauncher\VaultCache\FabLibrary\listings_v1.db
C:\Users\HP\AppData\Local\EpicGamesLauncher\Saved\Data\OC_*.dat
```

Safety rule:

```text
Never dump raw Launcher logs, webcache, OAuth URLs, tokens, account ids, or full
cache blobs into docs, prompts, Git, or result files. The Epic library indexer
must expose only allowlisted asset fields such as display_name, app_name,
versions, local cache path, .uproject path, and install state.
```

MCP server smoke command:

```bash
Scripts/UE5/mosim_epic_library_mcp_wsl_wrapper.sh
```

Codex MCP config entry, if enabling manually:

```toml
[mcp_servers.mosim_epic_library]
command = "/mnt/c/Users/HP/Desktop/MoSim/Scripts/UE5/mosim_epic_library_mcp_wsl_wrapper.sh"
args = []
startup_timeout_sec = 60
tool_timeout_sec = 60
```

Use this MCP to answer "what assets do we own / have cached / can create a
project from?" Use `unreal_engine` only after an editable UE project is open and
the editor-side listener passes a read-only actor or scene probe.

---

## 8. Recommended Syslab Wrapper

```bash
#!/usr/bin/env bash
exec "/mnt/d/Program Files/MWORKS/Syslab 2026a/Tools/syslab-mcp-server/syslab-mcp-server-win64.exe" \
  --syslab-root "D:\Program Files\MWORKS\Syslab 2026a" \
  --julia-root "C:\Users\Public\TongYuan\julia-1.10.10" \
  --syslab-display-mode nodesktop
```

---

## 9. Recommended Sysplorer Wrapper

```bash
#!/usr/bin/env bash
set -euo pipefail

exec /init /mnt/c/WINDOWS/system32/cmd.exe /c \
  "D:\PROGRA~1\MWORKS\SYSPLO~1\External\python64\python.exe C:\Users\HP\Desktop\MoSim\Scripts\mworks\sysplorer_mcp_wsl_entry.py"
```

The old `C:\Users\HP\Desktop\Quadrotor\scripts\...` path is invalid after the
MoSim restructure and causes a `sysplorer` MCP handshake failure.

---

## 10. Final Validation

Run Codex:

```bash
codex
```

Inside Codex:

```text
/mcp
```

Pass condition:

```text
syslab tools listed
sysplorer_mcp tools listed
```
