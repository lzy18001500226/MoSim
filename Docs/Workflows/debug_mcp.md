# Debug MCP Workflow

> Purpose: fix MCP configuration or initialization issues.

---

## 1. Success Criteria

For Sysplorer/Syslab, MCP startup is successful when `/mcp` shows tools.
For Unreal, `/mcp` showing `mosim-unreal` tools only proves the WSL stdio
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
Use 60 seconds as the default timeout for interactive probes, GUI bridge checks,
Codex conversation bootstrap commands, and any command whose progress is unclear.
If it has not returned useful evidence within 60 seconds, abort that attempt and
report the exact partial state instead of waiting.
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

## 4. Check WSL Config And Default Distro

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

Codex App and VSCode Codex must both use the WSL configuration. Verify the
Windows default WSL distro is the project distro:

```powershell
wsl.exe -l -v
wsl.exe --set-default Ubuntu-22.04
```

After changing the default distro, fully quit and reopen Codex App. A common
failure mode is that the App starts in an older default distro such as
`RflySim-20.04`; then it cannot see `/home/linux/.codex/config.toml`, WSL MCP
wrappers, or the project toolchain even though VSCode Codex works.

---

## 5. Sync Windows-Side Config When Codex App Requires It

The canonical config source is:

```text
/home/linux/.codex/config.toml
```

VSCode Codex and WSL CLI should read the WSL config directly. If Codex App
cannot run reliably without a Windows-side config, copy the WSL config to
Windows instead of editing it separately:

```bash
mkdir -p /mnt/c/Users/HP/.codex
cp -p /home/linux/.codex/config.toml /mnt/c/Users/HP/.codex/config.toml
```

Reason:

```text
Codex App may still look for C:\Users\HP\.codex\config.toml even when the
workspace is WSL-backed. Keep the Windows file as a synchronized copy, not as a
second source of truth.
```

Verify the app-side WSL Codex binary reads the expected server set:

```bash
/mnt/c/Users/HP/.codex/bin/wsl/codex mcp list
```

Expected MoSim MCP servers include:

```text
filesystem
git
syslab
sysplorer
mosim-epic
mosim-unreal
```

### 5.1 Windows-MCP Desktop Automation Server

Windows-MCP is a Windows-native desktop automation MCP server. Do not run it
with WSL Python because its UI, screenshot, PowerShell, registry, and window
automation dependencies must execute in the Windows desktop session.

Install or repair the Windows-side runtime:

```bash
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command \
  "irm https://astral.sh/uv/install.ps1 | iex"

/mnt/c/WINDOWS/system32/cmd.exe /c \
  "cd /d C:\Users\HP\Desktop\MoSim\Docs\Skills\Windows-MCP && C:\Users\HP\.local\bin\uv.exe sync"
```

Use a WSL wrapper at:

```text
/home/linux/mcp-wrappers/windows_mcp.sh
```

Expected wrapper command:

```bash
exec /init /mnt/c/WINDOWS/system32/cmd.exe /c \
  "cd /d C:\Users\HP\Desktop\MoSim\Docs\Skills\Windows-MCP && set ANONYMIZED_TELEMETRY=false&& set WINDOWS_MCP_DEBUG=false&& set WINDOWS_MCP_SCREENSHOT_BACKEND=auto&& C:\Users\HP\.local\bin\uv.exe run windows-mcp serve"
```

Register it in the Codex config:

```toml
[mcp_servers."windows-mcp"]
command = "/home/linux/mcp-wrappers/windows_mcp.sh"
args = []
startup_timeout_sec = 180
tool_timeout_sec = 300
```

Verify:

```bash
codex mcp list
```

Expected entry:

```text
windows-mcp   /home/linux/mcp-wrappers/windows_mcp.sh   enabled
```

Security note: Windows-MCP can operate the Windows desktop and run PowerShell
commands. Use the smallest necessary tool call and avoid broad desktop or
filesystem actions unless the user explicitly requests them.

Reference only:

---

## 6. Codex App / WSL Session Policy

Use the current WSL-backed VSCode Codex conversation as the primary project
conversation unless the user explicitly switches the primary entry point.
Codex App is currently treated as a Windows desktop front end for reviewing the
same project and for opening additional conversations.

Do not assume the App and the WSL IDE extension share one live session store.
They may share execution environment and copied configuration, but their local
session indexes can differ:

```text
WSL / VSCode Codex sessions: /home/linux/.codex/sessions
Windows Codex App sessions: C:\Users\HP\.codex\sessions
Windows Codex App index:    C:\Users\HP\.codex\state_5.sqlite
```

Operational rule:

```text
Primary source of task truth: repo docs and the active WSL conversation
Codex App role: review UI / extra conversation UI
Allowed session sync: one-way handoff only
Disallowed sync: live bidirectional writes to the same conversation
```

When a WSL conversation must be recovered into Codex App and normal sync does
not work, use a controlled one-way handoff:

```text
1. Close Codex App.
2. Copy the selected WSL session JSONL into C:\Users\HP\.codex\sessions.
3. Rewrite stale cwd/path values from old project locations to MoSim.
4. Insert or update the matching row in C:\Users\HP\.codex\state_5.sqlite.
5. Reopen Codex App and verify the thread opens without "current working
   directory missing".
```

Do not use manual SQLite/JSONL writes to create department or dedicated-task
conversations. User testing showed those App-only threads can become invisible
to VSCode/WSL and fail to resume with stale rollout paths. Create new
department/task conversations from the WSL/VSCode Codex side, then let the App
display the synced conversation.

Validated department-thread creation route, 2026-05-26:

```text
1. Create the thread from WSL with codex exec or an interactive WSL/VSCode
   Codex conversation rooted at /mnt/c/Users/HP/Desktop/MoSim.
2. Normalize the WSL thread title and cwd if the bootstrap prompt was used as
   the title.
3. Copy the real WSL rollout JSONL to C:\Users\HP\.codex\sessions.
4. Upsert the matching Windows App thread row and rebuild
   C:\Users\HP\.codex\session_index.jsonl.
5. Verify every App-visible thread has cwd /mnt/c/Users/HP/Desktop/MoSim and
   an existing rollout_path.
```

During `codex exec` bootstrap, warnings about remote plugin auth, featured
plugin cache warmup, Sysplorer shutdown handshakes, or file-watch cleanup are
not department-thread blockers as long as the rollout JSONL and thread row are
created. If Codex App UI crashes or shows stale paths, fully exit the App,
restart it, and verify the state database against the backup before editing.

Observed 2026-05-26: `codex exec` can create valid rollout files and SQLite
rows that are still hidden from VSCode/App conversation lists. Required
visibility checks are:

```text
/home/linux/.codex/session_index.jsonl contains the thread ID
C:\Users\HP\.codex\session_index.jsonl contains the thread ID
both state_5.sqlite rows use source=vscode and thread_source=vscode
both rows have has_user_event=1 and archived=0
both rollout_path values exist
cwd is /mnt/c/Users/HP/Desktop/MoSim
```

If any of these fail, back up first, fix only the affected department rows, and
record the repair in `PROGRESS.md`. If all checks pass but the UI still hides
the thread, stop treating raw session/index edits as reliable and create the
thread through the interactive WSL/VSCode Codex UI.

Observed 2026-05-29: a `codex exec` session created WSL rollout/state rows
without automatically updating the visible WSL/Windows indexes. For the
candidate thread
`019e7373-37f4-75e1-9780-e1519a489715` (`MoSim｜候选测试闭环`), the minimal repair
was:

```text
backup: C:\Users\HP\.codex\backups\visibility-repair-20260529T125333Z
copy WSL rollout JSONL to C:\Users\HP\.codex\sessions\...
upsert WSL and Windows state_5.sqlite rows
upsert WSL and Windows session_index.jsonl entries
set title/preview to MoSim｜候选测试闭环
set source=vscode, thread_source=vscode, has_user_event=1, archived=0
set cwd=/mnt/c/Users/HP/Desktop/MoSim
```

This is still not enough to declare a route usable. A synced thread remains
awaiting user confirmation until the user confirms it is visible and openable
in VSCode Codex/Codex App.

The better creation route for a new test conversation is a real WSL Codex TUI
session, not `codex exec`:

```bash
timeout 60s script -qfec \
  "codex --no-alt-screen -C /mnt/c/Users/HP/Desktop/MoSim -m gpt-5.5 -a never --sandbox danger-full-access '<short prompt>'" \
  /dev/null
```

On 2026-05-29 this created:

```text
thread_id: 019e73e5-d97d-75a3-ba72-b52e19d755b3
title: MoSim｜可见对话测试
reply: MoSim visible thread ok
backup after sync: C:\Users\HP\.codex\backups\coagent-session-restore-20260529-213048
```

Then run:

```bash
python3 CoAgent/dispatch/codex_session_repair.py sync-visible \
  --thread-id <thread-id> \
  --thread-name '<short title>' \
  --preview '<short preview>' \
  --cwd /mnt/c/Users/HP/Desktop/MoSim \
  --source-codex-home /home/linux/.codex \
  --target-codex-home /home/linux/.codex \
  --target-codex-home /mnt/c/Users/HP/.codex \
  --apply
```

The `--cwd` value matters because Codex App thread listing can filter by exact
working directory.

If the App receives real-time updates from the active WSL conversation, treat
that as an App convenience layer, not as the durable task ledger. Important
instructions, user corrections, manual-review results, and task status changes
must still be recorded in `PROGRESS.md`, `Docs/Workflows/agent_task_ledger.md`,
or a TaskSecretary intake file.

### 6.1 Clear A Wrong Codex Goal

When the active Codex goal is wrong and blocks creating the next goal, do not
work around it by marking it complete or blocked. Clear the actual persisted
thread goal through the Codex app-server goal API.

Use this when `get_goal` shows a wrong active or paused goal and the user has
explicitly approved deleting it.

First capture the thread id from `get_goal`, then run a one-shot stdio
app-server request from WSL. The app-server daemon command can fail when the
VSCode extension binary is used because the daemon expects a standalone Codex
install; stdio mode avoids that dependency.

```bash
python3 - <<'PY'
import json
import selectors
import subprocess
import time

thread_id = "<thread-id-from-get_goal>"
cmd = ["codex", "app-server", "--listen", "stdio://", "--enable", "goals"]
proc = subprocess.Popen(
    cmd,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,
    cwd="/mnt/c/Users/HP/Desktop/MoSim",
)
sel = selectors.DefaultSelector()
sel.register(proc.stdout, selectors.EVENT_READ, data="stdout")
sel.register(proc.stderr, selectors.EVENT_READ, data="stderr")

def send(obj):
    proc.stdin.write(json.dumps(obj, ensure_ascii=False) + "\n")
    proc.stdin.flush()

def wait_for(request_id, timeout=20):
    deadline = time.time() + timeout
    while time.time() < deadline:
        for key, _ in sel.select(timeout=0.2):
            line = key.fileobj.readline()
            if not line or key.data != "stdout":
                continue
            msg = json.loads(line)
            if msg.get("id") == request_id:
                return msg
    return None

try:
    send({
        "method": "initialize",
        "id": 0,
        "params": {
            "clientInfo": {
                "name": "mosim_goal_clear",
                "title": "MoSim Goal Clear",
                "version": "0.1.0",
            },
            "capabilities": {"experimentalApi": True},
        },
    })
    print("INIT=", wait_for(0))
    send({"method": "initialized", "params": {}})
    send({"method": "thread/goal/get", "id": 1, "params": {"threadId": thread_id}})
    print("BEFORE=", wait_for(1))
    send({"method": "thread/goal/clear", "id": 2, "params": {"threadId": thread_id}})
    print("CLEAR=", wait_for(2))
    send({"method": "thread/goal/get", "id": 3, "params": {"threadId": thread_id}})
    print("AFTER=", wait_for(3))
finally:
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()
PY
```

Accepted result:

```text
CLEAR= {"id": 2, "result": {"cleared": true}}
AFTER= {"id": 3, "result": {"goal": null}}
```

Then call `get_goal` in the current conversation. It must return:

```text
goal: null
```

If `thread/goal/clear` returns `cleared: true` but `get_goal` still shows the
old goal, treat it as a current-process stale snapshot and restart/resume the
conversation before creating a new goal. Do not edit sqlite directly unless the
app-server route fails and the user approves a specific Codex-state repair.

Target MoSim department conversation set:

```text
MoSim｜主线总控
MoSim｜调度中台
MoSim｜文档秘书部
MoSim｜研发工程部
MoSim｜验证测试部
MoSim｜安全合规部
MoSim｜DevOps 发布部
```

Before any emergency direct SQLite/session edit, back up `state_5.sqlite`, its
WAL/SHM files, `session_index.jsonl`, and the affected rollout JSONL files. The
latest rollback backup for the rejected App-only department threads is:

```text
C:\Users\HP\.codex\backups\revert-app-local-department-threads-20260526-123853
```

Latest backup before the accepted WSL-created department-thread sync:

```text
C:\Users\HP\.codex\backups\wsl-department-thread-sync-20260526-130607
```

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

The configured MCP server name is:

```text
mosim-unreal
```

The stable WSL wrapper is project-local:

```text
Docs/Skills/Unreal/mosim-unreal/wrappers/mosim-unreal.sh
```

It points to MoSim's live UE Editor MCP surface:

```text
Docs/Skills/Unreal/mosim-unreal/wrappers/wsl.sh
Docs/Skills/Unreal/mosim-unreal/mcp/server.py
```

The older Flopperam wrapper is retained for rollback only:

```text
Docs/Skills/Unreal/mosim-unreal/wrappers/legacy_flopperam_wsl.sh
```

Manual smoke test:

```bash
Docs/Skills/Unreal/mosim-unreal/wrappers/mosim-unreal.sh
```

If it starts and waits for input, that is normal for stdio MCP. To verify with a
client, send the standard MCP handshake and then `tools/list`; the server should
report MoSim tools such as `ue_health`, `project_context`,
`editor_listener_health`, `reversible_actor_probe`, and `tool_boundary`.

Command-line checks that do not require UE Editor:

```bash
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-tools
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-context
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-assets --limit 5
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-maps --limit 5
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-level --timeout 0.5 --limit 5
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-reversible-probe
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-scene-sources --limit 1 --map-limit 2
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-log --lines 20
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-boundary
```

`dump-reversible-probe` is non-mutating unless `--execute` is passed. It is the
safe way to verify the write boundary before running a temporary actor
spawn/move/delete probe on a loaded review map.

`dump-scene-sources` is compact by default. Use `--detail` only for a targeted
project because local UE scene projects can contain thousands of assets and
maps.
The server also clamps large caller limits, so a mistaken `limit=10000` should
not produce a runaway MCP response.

Codex MCP config entry, if enabling manually:

```toml
[mcp_servers.mosim-unreal]
command = "/mnt/c/Users/HP/Desktop/MoSim/Docs/Skills/Unreal/mosim-unreal/wrappers/mosim-unreal.sh"
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
Scripts/UE5/build_unreal_renderer.sh
Scripts/UE5/open_unreal_renderer.sh editor
python3 Scripts/UE5/probe_unreal_mcp_listener.py --wrapper-route-only --timeout 1
python3 Docs/Skills/Unreal/mosim-unreal/mcp/server.py dump-level --timeout 2 --limit 5
```

If this fails, do not keep retrying actor/Blueprint MCP tools. Fix the Unreal
Editor/plugin/listener route first, or continue only with source-level files and
document the missing viewport evidence.

`Scripts/UE5/build_unreal_renderer.sh` and
`Scripts/UE5/open_unreal_renderer.sh` resolve the editor from
`MoSimSceneLibrary.uproject` `EngineAssociation`. Current MoSim renderer
association is `5.5`, so the normal executable is:

```text
D:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe
```

UE 4.27 uses `UE4Editor.exe` / `UE4Editor-Cmd.exe`, not
`UnrealEditor.exe` / `UnrealEditor-Cmd.exe`; project checks must account for
that when auditing older scene packs.

`--wrapper-route-only` checks the exact route used by
`Docs/Skills/Unreal/mosim-unreal/wrappers/mosim-unreal.sh`.
Without it, the probe also checks practical diagnostic fallbacks:
`UNREAL_HOST` when set, the WSL default gateway, and
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
mosim-unreal     live Unreal Editor automation
mosim-epic       Epic/Fab/Launcher library and scene-source readiness
```

Do not expand this phase into MWORKS, external renderer bridge, downloader,
or full simulator-control MCP work unless the user explicitly reopens that
scope. Skills are still required, but only for these MCP boundaries.

| Boundary | MCP / Tool Role | Why It Is Separate |
|---|---|---|
| Unreal Editor | `mosim-unreal` | Live editor scene/Blueprint/material/actor work through an editor listener |
| Epic/Fab/Launcher library | `mosim-epic` | Asset inventory and scene-source gates from Launcher/Fab/local caches; not a UE Editor object graph |

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

## 7.3 Epic/Fab / Scene-Source MCP

Project-local scripts:

```text
Scripts/UE5/epic_library_index.py
Scripts/UE5/epic_library_view.py
Docs/Skills/Unreal/mosim-epic/mcp/server.py
Docs/Skills/Unreal/mosim-epic/wrappers/mosim-epic.sh
Scripts/UE5/check_epic_library_inventory.py
Docs/Skills/Unreal/mosim-epic/SKILL.md
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
Docs/Skills/Unreal/mosim-epic/wrappers/mosim-epic.sh
```

Codex MCP config entry, if enabling manually:

```toml
[mcp_servers.mosim-epic]
command = "/mnt/c/Users/HP/Desktop/MoSim/Docs/Skills/Unreal/mosim-epic/wrappers/mosim-epic.sh"
args = []
startup_timeout_sec = 60
tool_timeout_sec = 60
```

Use this MCP to answer "what assets do we own / have cached / can create a
project from?" Use `mosim-unreal` only after an editable UE project is open and
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
