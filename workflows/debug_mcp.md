# Debug MCP Workflow

> Purpose: fix MCP configuration or initialization issues.

---

## 1. Success Criteria

MCP is successful when `/mcp` shows tools.

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
and issue JSON-RPC MCP calls directly; record the log under `results/`.

For `QuadrotorExperiments.Sunray150CompleteSystemGraphical_Sysblock`, follow the
direct sequence in `workflows/run_simulation.md`. The key failure classes are:

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

The local Unreal MCP source lives under:

```text
Skills/unreal-engine-mcp/
```

The WSL wrapper is project-local:

```text
scripts/unreal_mcp_wsl_wrapper.sh
```

Manual smoke test:

```bash
scripts/unreal_mcp_wsl_wrapper.sh
```

If it starts and waits for input, that is normal for stdio MCP. To verify with a
client, send the standard MCP handshake and then `tools/list`; the server should
report `UnrealMCP_Advanced` and tools such as `get_actors_in_level`,
`set_actor_transform`, `create_blueprint`, `compile_blueprint`, and
`set_mesh_material_color`.

Codex MCP config entry, if enabling manually:

```toml
[mcp_servers.unreal_engine]
command = "/mnt/c/Users/HP/Desktop/Quadrotor/scripts/unreal_mcp_wsl_wrapper.sh"
args = []
startup_timeout_sec = 180
tool_timeout_sec = 300
```

Do not register this against opencode config files. The Unreal editor side still
needs the bundled `Skills/unreal-engine-mcp/UnrealMCP/` plugin enabled in a UE
project. The Python MCP server talks to that editor plugin on `127.0.0.1:55557`.
If Unreal is not open or the plugin is not enabled, `tools/list` can still work,
but actor/Blueprint tools will fail with connection refused.

Before running interactive actor/Blueprint tools, check the editor-side socket:

```bash
python3 scripts/probe_unreal_mcp_listener.py --host 127.0.0.1 --port 55557
```

If this fails, do not keep retrying actor/Blueprint MCP tools. Fix the Unreal
Editor/plugin/listener route first, or continue only with source-level files and
document the missing viewport evidence.

Interpret the preflight result before changing code:

| Probe result | Meaning | Next action |
|---|---|---|
| `[OK] Unreal Editor MCP listener reachable` | Editor-side socket is reachable from the current shell | Run one read-only UE MCP actor/scene probe, then proceed to viewport review if it succeeds |
| `ConnectionRefusedError` | No process is listening at that host/port from the current shell | Open the renderer `.uproject`, enable/load `UnrealMCP`, or start the editor-side plugin listener |
| `TimeoutError` or MCP tool timeout | A listener path may be blocked, bound to another interface, or stalled | Check UE log/plugin host binding; avoid repeated actor/Blueprint MCP calls until socket reachability is resolved |

For S0/S1 renderer work, run the combined gate first:

```bash
python3 scripts/check_unreal_s0_s1_readiness.py --build
```

Add `--check-listener` only when preparing for interactive viewport review.

Keep this separate from the project-owned external renderer plugin:

```text
unreal/QuadrotorMworksBridge/
```

`UnrealMCP` controls the editor through MCP. `QuadrotorMworksBridge` receives
MWORKS simulation state for video rendering. They solve different problems.

Project-local Unreal renderer entry:

```text
unreal/MworksUnrealRenderer/MworksUnrealRenderer.uproject
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
exec "/mnt/d/Program Files/MWORKS/Sysplorer 2026a/External/python64/python.exe" \
  "D:\Program Files\MWORKS\Sysplorer 2026a\Tools\sysplorer_mcp\sysplorer-mcp-server\main.py" \
  --mworks-install-dir "D:\Program Files\MWORKS\Sysplorer 2026a" \
  --sysplorer-platform-label "Sysplorer 2026a"
```

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
