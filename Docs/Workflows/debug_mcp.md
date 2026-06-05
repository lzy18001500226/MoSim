# Debug MCP Workflow

> Purpose: fix MCP configuration or initialization issues.

---

## 1. Success Criteria

For Sysplorer/Syslab, MCP startup is successful when `/mcp` shows tools.
For Unreal, `/mcp` showing `mosim-unreal` tools only proves the configured
stdio wrapper and Python server. Interactive Unreal actor/Blueprint/viewport work is
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

For the Windows-native Codex App route, check that project MCP commands do not
use `wsl.exe`, `\\wsl.localhost`, `/mnt/c`, or `/home/linux` in
`C:\Users\HP\.codex\config.toml`. Current Windows-native wrappers:

```text
C:\Users\HP\Desktop\MoSim\Docs\Skills\Windows-MCP\wrappers\windows-mcp.cmd
C:\Users\HP\Desktop\MoSim\Docs\Skills\ROS-MCP\wrappers\ros-mcp.cmd
C:\Users\HP\Desktop\MoSim\Docs\Skills\Unreal\mosim-unreal\wrappers\mosim-unreal.cmd
C:\Users\HP\Desktop\MoSim\Docs\Skills\Unreal\mosim-epic\wrappers\mosim-epic.cmd
C:\Users\HP\Desktop\MoSim\Docs\Skills\Blender-MCP\wrappers\blender-mcp.cmd
```

The standalone `filesystem` MCP is not configured in the Windows App route
unless a Windows Node/npm filesystem server is installed. Use Codex's own
filesystem tools and Windows-MCP for Windows-side file/UI work.

For a WSL-only VSCode/CLI route, WSL wrappers such as
`/home/<WSL_USER>/mcp-wrappers/syslab_mcp.sh` remain valid, but do not copy
those launcher paths into the Windows App config.

---

## 3. Check Wrapper Scripts

Windows-native route:

```cmd
C:\Users\HP\Desktop\MoSim\Docs\Skills\Windows-MCP\wrappers\windows-mcp.cmd
C:\Users\HP\Desktop\MoSim\Docs\Skills\ROS-MCP\wrappers\ros-mcp.cmd --help
cd /d C:\Users\HP\Desktop\MoSim
C:\Users\HP\.local\bin\uv.exe run --no-project --with mcp python Docs\Skills\Unreal\mosim-unreal\mcp\server.py dump-tools
C:\Users\HP\.local\bin\uv.exe run --no-project --with mcp python Docs\Skills\Unreal\mosim-epic\mcp\server.py dump-tools
```

ROS-MCP and Blender-MCP use project-local Windows environments named
`.venv-win`. Do not reuse WSL-created `.venv` directories from Windows; mixed
Windows/WSL virtual environments can fail with `lib64` permission errors.

WSL-only route:

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

This section applies only when the active Codex runtime is intentionally WSL
backed. It is not the policy for the Windows-native Codex App route.

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

If VSCode Codex is intentionally running in WSL, verify the Windows default WSL
distro is the project distro:

```powershell
wsl.exe -l -v
wsl.exe --set-default Ubuntu-22.04
```

After changing the default distro, fully quit and reopen VSCode. A common
failure mode is that a WSL-backed session starts in an older default distro such
as `RflySim-20.04`; then it cannot see `/home/linux/.codex/config.toml`, WSL MCP
wrappers, or the project toolchain.

### 4.1 VSCode Codex Fails On SQLite Migration Checksum

Observed 2026-06-01: VSCode Codex failed to load because the extension launched
the Windows Codex binary against `C:\Users\HP\.codex`, while the visible
project state had been created by the WSL/Linux Codex runtime. The log symptom
was:

```text
failed to initialize sqlite state runtime under C:\Users\HP\.codex:
migration 1 was previously applied but has been modified
```

Root cause: the SQL schema text is effectively equivalent, but the SQLx
migration checksum differs between the Windows and Linux packaged Codex
runtime. If the state database was initialized by one runtime and then opened
by the other, the app-server exits before the webview can mount.

Primary fix for this project is to keep VSCode Codex in WSL mode:

```json
"chatgpt.runCodexInWindowsSubsystemForLinux": true
```

Set it in:

```text
C:\Users\HP\AppData\Roaming\Code\User\settings.json
```

Verification:

```bash
rg -n "chatgpt.runCodexInWindowsSubsystemForLinux" \
  /mnt/c/Users/HP/AppData/Roaming/Code/User/settings.json

find /mnt/c/Users/HP/AppData/Roaming/Code/logs \
  -path '*/openai.chatgpt/Codex.log' -printf '%T@ %p\n' |
  sort -n | tail
```

Expected follow-up log after reload:

```text
[spawn-codex-process] Spawning codex process inside WSL
[startup][renderer] app routes mounted
```

If the log still shows `C:\Users\HP\.codex` migration failure after changing
the setting, fully reload VSCode or close all VSCode windows and reopen the
MoSim workspace. Do not delete `state_5.sqlite` to fix this without a backup:
it contains the visible thread index and token counters.

For the standalone Windows Codex App or Windows-native Codex runtime, the same
checksum failure can block launch with:

```text
Codex cannot access its local database.
failed to initialize sqlite state runtime under C:\Users\HP\.codex:
migration 1 was previously applied but has been modified
```

When that happens, first verify which Windows runtime is being launched. The
official Windows Codex App starts its own packaged app-server binary:

```text
C:\Program Files\WindowsApps\OpenAI.Codex_*\app\resources\codex.exe
```

If the desired policy is for Windows Codex App, Windows CLI, and VSCode Codex
to share `C:\Users\HP\.codex`, do not isolate `CODEX_HOME`. Instead, first
make the Windows CLI launcher use the same Codex runtime generation as the App
or VSCode extension. A common failure is an old
`C:\Users\HP\.codex\bin\codex.exe` such as `0.135.0-alpha.1` reading a state DB
created by `0.136.0-alpha.2`.

```cmd
codex --version
"C:\Users\HP\.vscode\extensions\openai.chatgpt-*\bin\windows-x86_64\codex.exe" --version
```

For the shared-home route, `C:\Users\HP\.codex\bin\codex.cmd` should point to
the shared home and same-directory runtime:

```cmd
@echo off
set "CODEX_HOME=C:\Users\HP\.codex"
"%~dp0codex.exe" %*
```

If `doctor` reports healthy databases but `app-server` still exits with
`migration 1 was previously applied but has been modified`, compare the SQLx
migration checksum rows against a clean temporary home generated by the current
runtime. On 2026-06-03 the table schemas were equivalent and differed only by
LF versus CRLF SQL text, so every `state_5.sqlite` migration checksum differed
while the actual schema and row data were usable. The minimal shared-home fix
was to back up `state_5.sqlite*` and update only `_sqlx_migrations.checksum`
from the clean runtime DB, preserving the `threads` index and session rollouts.

Do this only after closing Codex App and after a backup:

```bash
probe="/mnt/c/Users/HP/Desktop/MoSim/Results/tmp/codex-home-probe"
rm -rf "$probe" && mkdir -p "$probe"
timeout 5s cmd.exe /c "set CODEX_HOME=C:\Users\HP\Desktop\MoSim\Results\tmp\codex-home-probe&& C:\Users\HP\.codex\bin\codex.exe app-server --analytics-default-enabled"

backup_dir="/mnt/c/Users/HP/.codex/backups/shared_state_sqlx_checksum_fix_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"
for suffix in "" "-shm" "-wal"; do
  f="/mnt/c/Users/HP/.codex/state_5.sqlite${suffix}"
  [[ -e "$f" ]] && cp -a "$f" "$backup_dir/"
done

python3 - <<'PY'
import sqlite3
from pathlib import Path

root = Path("/mnt/c/Users/HP/.codex")
probe = Path("/mnt/c/Users/HP/Desktop/MoSim/Results/tmp/codex-home-probe")
expected_db = probe / "state_5.sqlite"
state_db = root / "state_5.sqlite"

src = sqlite3.connect(f"file:{expected_db}?mode=ro", uri=True)
expected = src.execute(
    "select version, checksum from _sqlx_migrations order by version"
).fetchall()
src.close()

dst = sqlite3.connect(state_db)
existing = [
    row[0] for row in dst.execute(
        "select version from _sqlx_migrations order by version"
    )
]
if existing != [row[0] for row in expected]:
    raise SystemExit("migration versions differ; do not patch checksums")
for version, checksum in expected:
    dst.execute(
        "update _sqlx_migrations set checksum=? where version=?",
        (checksum, version),
    )
dst.commit()
print(dst.execute("pragma integrity_check").fetchone()[0])
dst.close()
PY
```

Verify from Windows:

```cmd
set CODEX_HOME=C:\Users\HP\.codex&& C:\Users\HP\.codex\bin\codex.exe doctor
```

For a direct app-server smoke test, run it with a timeout. A timeout with no
SQLite error means the server stayed alive; an immediate exit with `migration 1
was previously applied but has been modified` means the active runtime still
does not match one of the SQLite migration families.

```bash
timeout 8s cmd.exe /c "set CODEX_HOME=C:\Users\HP\.codex&& C:\Users\HP\.codex\bin\codex.exe app-server --analytics-default-enabled"
```

Expected transition: `doctor` reports all four databases healthy and rollout
files agree with the state DB. The Windows Codex App opens to the normal chat UI
without the local database dialog. This repair does not touch the WSL primary
state DB under `/home/linux/.codex`.

If the user prefers isolation instead of shared state, use a separate
`C:\Users\HP\.codex-cli` home for terminal/doctor work and leave
`C:\Users\HP\.codex` for the Windows App. That avoids cross-runtime writes but
means Windows CLI and App do not share one local state DB.

### 4.2 Windows Codex App Not Responding

Observed 2026-06-03: after the SQLite checksum repair, Windows Codex App could
still show the Windows `Codex 未响应` dialog. Treat this as a separate App hang
class, not the same as the database launch failure.

Check evidence:

```powershell
Get-WinEvent -FilterHashtable @{LogName="Application"; Id=1002; StartTime=(Get-Date).AddDays(-3)} |
  Where-Object { $_.Message -match "Codex" } |
  Select-Object TimeCreated,ProviderName,Id,Message

Get-CimInstance Win32_Process |
  Where-Object {
    $_.Name -match "Codex|codex" -or
    ($_.CommandLine -and $_.CommandLine -match "Codex|codex|openai-bundled\\chrome|chrome.nativeMessaging|extension-host.exe")
  } |
  Select-Object ProcessId,Name,CreationDate,CommandLine
```

Known local contributors:

- Very large session JSONL files. On 2026-06-03 the main MoSim Windows App
  session file was about `1.96 GB`, and the active state row had nearly
  `1e9` tokens recorded. Windows App thread switching/resume can hang on this
  workload even when `app-server` is healthy.
- Local proxy through `127.0.0.1:7897`. Packaged Windows apps may need an
  AppContainer loopback exemption before they can reliably use localhost
  proxy endpoints.
- Residual Codex/plugin processes. The bundled Chrome extension host under
  `C:\Users\HP\.codex\plugins\cache\openai-bundled\chrome\...` can remain
  running or be relaunched, and logs can show plugin reconcile access-denied
  errors.
- Startup probes for Computer Use, plugins, skills, and MCP status can add
  multi-second timeouts. On 2026-06-03 logs showed repeated
  `IpcClient Initialize failed timeout`, `computer-use native pipe startup
  failed`, and `mcpServerStatus/list` requests taking about 16-17 seconds.

If the machine uses a localhost proxy, run this from an elevated Windows
terminal:

PowerShell:

```powershell
& "$env:SystemRoot\System32\CheckNetIsolation.exe" LoopbackExempt -a -n=openai.codex_2p2nqsd0c76g0
& "$env:SystemRoot\System32\CheckNetIsolation.exe" LoopbackExempt -s
```

`cmd.exe`:

```cmd
%SystemRoot%\System32\CheckNetIsolation.exe LoopbackExempt -a -n=openai.codex_2p2nqsd0c76g0
%SystemRoot%\System32\CheckNetIsolation.exe LoopbackExempt -s
```

Do not use `OpenAI.Codex_2p2nqsd0c76g0` for `CheckNetIsolation -n=` on this
machine. `Get-AppxPackage` reports that package family name, but the
AppContainer mapping uses `Moniker=openai.codex_2p2nqsd0c76g0`. If `-n=` still
returns `参数无效`, use the mapped SID instead:

```powershell
Get-ChildItem "HKCU:\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppContainer\Mappings" |
  ForEach-Object {
    $item = Get-ItemProperty $_.PSPath
    if (($item.DisplayName -match "Codex") -or ($item.Moniker -match "Codex")) {
      [PSCustomObject]@{ SID=$_.PSChildName; DisplayName=$item.DisplayName; Moniker=$item.Moniker }
    }
  }

& "$env:SystemRoot\System32\CheckNetIsolation.exe" LoopbackExempt -a -p=<SID_FROM_OUTPUT>
& "$env:SystemRoot\System32\CheckNetIsolation.exe" LoopbackExempt -s
```

If the App relaunches into a bad state, fully kill Codex and bundled plugin
hosts before reopening:

```powershell
Get-Process Codex -ErrorAction SilentlyContinue | Stop-Process -Force
Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -and $_.CommandLine -match "openai-bundled\\chrome|chrome.nativeMessaging|extension-host.exe" } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

Do not keep multi-GB project sessions as the active Windows App review thread.
Archive or migrate them to a summarized continuation thread, while preserving
the original JSONL under `C:\Users\HP\.codex\sessions` for forensic recovery.

### 4.3 Windows Codex App Shows No Chats After History Migration

Observed 2026-06-04: after WSL rollout files and `state_5.sqlite` rows were
migrated into `C:\Users\HP\.codex`, the Windows Codex App opened the MoSim
project but showed `暂无聊天`. The DB was readable and MoSim rows existed, but
the App `thread/list` request failed before returning any conversations.

Do not keep changing only `threads.cwd`. First check the App log DB:

```bash
python3 - <<'PY'
import sqlite3
con = sqlite3.connect('/mnt/c/Users/HP/.codex/logs_2.sqlite')
for row in con.execute("""
    select id,ts,level,feedback_log_body
    from logs
    where feedback_log_body like '%state db list_threads failed%'
    order by id desc
    limit 10
"""):
    print(row[0], row[1], row[2], row[3][:500])
con.close()
PY
```

The confirmed failure was:

```text
state db list_threads failed: unknown thread source: vscode
```

Windows Codex Desktop `26.601.21317` / CLI runtime `0.136.0-alpha.2` rejects
`threads.source='vscode'` during `thread/list`; one unsupported row can make
the whole project list appear empty. Back up the state DB family, then normalize
`source` to the Windows runtime's accepted `cli` value and keep the semantic
origin in `thread_source`:

```bash
backup_dir="/mnt/c/Users/HP/.codex/backups/app-list-fix_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"
for suffix in "" "-shm" "-wal"; do
  f="/mnt/c/Users/HP/.codex/state_5.sqlite${suffix}"
  [[ -e "$f" ]] && cp -a "$f" "$backup_dir/"
done

python3 - <<'PY'
import sqlite3
from pathlib import Path

db = Path('/mnt/c/Users/HP/.codex/state_5.sqlite')
con = sqlite3.connect(db)
con.execute('pragma busy_timeout=5000')

con.execute("""
    update threads
    set thread_source='subagent'
    where source like '{%subagent%'
       or source like 'subagent:%'
       or thread_source='subagent'
""")
con.execute("""
    update threads
    set thread_source='user'
    where thread_source is null
       or thread_source not in ('user','subagent')
""")
con.execute("update threads set source='cli' where source <> 'cli'")

win_mosim = r'C:\Users\HP\Desktop\MoSim'
con.execute("""
    update threads
    set cwd=?
    where lower(cwd) in (
        lower('/mnt/c/Users/HP/Desktop/MoSim'),
        lower('\\\\?\\C:\\Users\\HP\\Desktop\\MoSim'),
        lower('C:\\Users\\HP\\Desktop\\MoSim')
    )
    or lower(cwd) like '%users%hp%desktop%mosim%'
""", (win_mosim,))

con.commit()
print('integrity', con.execute('pragma integrity_check').fetchone()[0])
print('sources', list(con.execute("""
    select source, thread_source, archived, count(*)
    from threads
    group by source, thread_source, archived
    order by count(*) desc
""")))
print('mosim', list(con.execute("""
    select cwd, archived, count(*)
    from threads
    where cwd like '%MoSim%'
    group by cwd, archived
""")))
print('wal_checkpoint', con.execute('pragma wal_checkpoint(truncate)').fetchall())
con.close()
PY
```

Verify with the Windows runtime that the source inventory no longer contains
`vscode`:

```cmd
set CODEX_HOME=C:\Users\HP\.codex&& C:\Users\HP\AppData\Local\OpenAI\Codex\bin\716dda49c14d31a0\codex.exe doctor --json
```

Expected useful lines:

```text
state DB integrity: ok
rollout DB sources: cli=310
```

If checking rollout file existence from WSL, map raw Windows paths such as
`C:\Users\HP\.codex\...` to `/mnt/c/Users/HP/.codex/...` before calling
`Path.exists()`. A direct WSL `Path('C:\\...').exists()` check will falsely
report all Windows paths as missing and can lead to accidental deletion of good
thread rows.

#### 4.3.1 Windows Codex App Shows Wrong Or Long Titles

Observed 2026-06-05 after a clean App reinstall and history migration: the App
could show MoSim conversations, but many titles were the first long user prompt
or `thread/list` returned `name=null`. The App/backend does not derive the
visible title only from SQLite. Keep these three places synchronized:

```text
C:\Users\HP\.codex\state_5.sqlite        threads.title / preview
C:\Users\HP\.codex\session_index.jsonl   thread_name
rollout JSONL first line                 session_meta.payload.title/name/thread_name
```

Before editing, close Codex App and app-server/helper processes, then back up
the DB family, `session_index.jsonl`, `.codex-global-state.json`, and the active
rollout files. The accepted 2026-06-05 backup was:

```text
C:\Users\HP\.codex\backups\app-history-title-project-fix-20260605-221723
```

After rewriting the 28 reviewed active histories, verify through the app-server
protocol, not only through SQLite. Expected 2026-06-05 pass evidence:

```text
global active thread/list: 28, missing_name=0
C:\Users\HP\Desktop\MoSim: 14, missing_name=0
C:\Users\HP\Desktop\DH: 12, missing_name=0
C:\Users\HP\Desktop\JIT-Fine: 2, missing_name=0
```

If the App still shows only the currently opened project, check
`.codex-global-state.json`. The project roots may only list MoSim even though
global `thread/list` has all records. Add the reviewed project roots to
`project-order`, `active-workspace-roots`, and `electron-saved-workspace-roots`.
This affects App project selection/cache; it does not create or delete history.

### 4.4 Windows Codex App Shows Only The First 12 Chats

Observed 2026-06-04: after the empty-list repair, the App showed only 12
conversations even though the DB and rollout inventory were complete. Treat
this as a partial listing issue until the DB, rollout directories, and
app-server pagination prove otherwise.

First close Codex App and verify the local state inventory:

```bash
python3 - <<'PY'
import sqlite3

db = '/mnt/c/Users/HP/.codex/state_5.sqlite'
con = sqlite3.connect(db)
print('integrity', con.execute('pragma integrity_check').fetchone()[0])
print('total', con.execute('select count(*) from threads').fetchone()[0])
print('bad_source', con.execute(
    "select count(*) from threads where source <> 'cli' or source is null"
).fetchone()[0])
print('bad_thread_source', con.execute(
    "select count(*) from threads "
    "where thread_source not in ('user','subagent') or thread_source is null"
).fetchone()[0])
print('mosim active user', con.execute("""
    select count(*)
    from threads
    where cwd='C:\\Users\\HP\\Desktop\\MoSim'
      and source='cli'
      and thread_source='user'
      and archived=0
""").fetchone()[0])
con.close()
PY
```

Then run the Windows runtime doctor:

```cmd
set CODEX_HOME=C:\Users\HP\.codex&& C:\Users\HP\AppData\Local\OpenAI\Codex\bin\716dda49c14d31a0\codex.exe doctor --json
```

For the intermediate 2026-06-04 state, useful pass evidence was:

```text
state DB integrity: ok
rollout DB rows: 308
rollout DB active rows: 119
rollout DB archived rows: 189
rollout DB sources: cli=308
rollout DB stale rows: 0
MoSim active user rows: 27
```

If these counts pass but the UI still shows 12 items, query the app-server
protocol directly before changing SQLite again. The important distinction is
whether the missing conversations are normal active sessions or archived
sessions hidden from the project list.

```bash
python3 - <<'PY'
import json, select, subprocess, time

exe = '/mnt/c/Users/HP/AppData/Local/OpenAI/Codex/bin/716dda49c14d31a0/codex.exe'
proc = subprocess.Popen(
    [exe, 'app-server', '--stdio'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True,
    bufsize=1,
    cwd='/mnt/c/Users/HP/Desktop/MoSim',
)
try:
    proc.stdin.write(json.dumps({
        'id': 'init',
        'method': 'initialize',
        'params': {
            'clientInfo': {'name': 'debug-thread-list', 'version': '1'},
            'capabilities': {'experimentalApi': True},
        },
    }) + '\n')
    proc.stdin.write(json.dumps({'method': 'initialized', 'params': {}}) + '\n')
    proc.stdin.flush()

    all_threads = []
    cursor = None
    for page in range(10):
        rid = f'p{page}'
        proc.stdin.write(json.dumps({
            'id': rid,
            'method': 'thread/list',
            'params': {
                'archived': False,
                'cwd': 'C:\\Users\\HP\\Desktop\\MoSim',
                'limit': 100,
                'cursor': cursor,
                'sortKey': 'updated_at',
                'sortDirection': 'desc',
            },
        }) + '\n')
        proc.stdin.flush()

        deadline = time.time() + 15
        obj = None
        while time.time() < deadline:
            ready, _, _ = select.select([proc.stdout], [], [], 0.5)
            for fd in ready:
                line = fd.readline()
                if not line:
                    continue
                msg = json.loads(line)
                if msg.get('id') == rid:
                    obj = msg
                    break
            if obj:
                break
        if not obj:
            raise RuntimeError(f'missing page {page}')
        result = obj.get('result', {})
        data = result.get('data', [])
        all_threads.extend(data)
        cursor = result.get('nextCursor')
        print('page', page, 'items', len(data), 'next', bool(cursor))
        if not cursor:
            break
    print('total', len({t['id'] for t in all_threads}))
finally:
    proc.terminate()
PY
```

Final accepted 2026-06-04 fix: the MoSim history that the user expected in the
normal App list was still in `C:\Users\HP\.codex\archived_sessions`. Moving
only DB rows is not enough because app-server scans rollout file locations and
will rebuild archive state. The durable repair was:

```text
backup: C:\Users\HP\.codex\backups\unarchive-mosim-history-20260604-2242
move:   C:\Users\HP\.codex\archived_sessions\rollout-*.jsonl
        -> C:\Users\HP\.codex\sessions\YYYY\MM\DD\rollout-*.jsonl
DB:     update matching threads.rollout_path, archived=0, archived_at=NULL
verify: thread/list cwd=MoSim archived=false returned 211 unique rows
verify: thread/list cwd=MoSim archived=true returned 0 rows
doctor: rollout DB active rows=305, archived rows=3, stale rows=0
```

Also clear stale Codex++ hidden/archive localStorage state. Otherwise the UI
enhancement script can continue filtering conversations that have been restored
from archived to active. The accepted script patch bumped the storage version
and removed `__codexListPagebusterArchivedIds` during version migration and
manual reset:

```text
C:\Users\HP\AppData\Roaming\Codex++\user_scripts\market-codex-list-pagebuster.js
```

The 2026-06-04 failure mode was that unresolved native metadata checks could
prune valid snapshot rows, and project supplemental rows were skipped while the
native project list still had a collapsed "show more" state. The local fix was:

```text
backup: market-codex-list-pagebuster.js.bak-20260604-2129
script: keep unresolved metadata rows, allow project supplements while native
        lists are collapsed, and bump STORAGE_VERSION to force a fresh snapshot
backup: market-codex-list-pagebuster.js.bak-20260604-2248
script: clear ARCHIVED_IDS_KEY when migrating/resetting after unarchiving MoSim
```

Verify script syntax with the Codex-bundled Node runtime:

```bash
/mnt/c/Users/HP/AppData/Local/OpenAI/Codex/bin/5b9024f90663758b/node.exe \
  --check 'C:\Users\HP\AppData\Roaming\Codex++\user_scripts\market-codex-list-pagebuster.js'
```

After this, reopen Codex App. If it still shows only 12, inspect the browser
console for `[clpb] snapshot refreshed`, `[clpb] project supplement rendered`,
or `[clpb] snapshot refresh failed` before changing SQLite rows.

If the App instead shows a larger list but all entries are from the wrong
project, for example 90 DH conversations and no MoSim rows, treat that as a
frontend scope/cache problem first. The backend can already be correct while
the native App is currently scoped to another workspace. Verify with the
app-server protocol before moving files again:

```text
global active thread/list: 307 unique rows
MoSim cwd count:            212 rows
DH/DH-variant cwd count:     81 rows
explicit MoSim pagination:  100 + 100 + 11 rows
evidence: Results/codex_app_debug/after_exact_cwd_fix_protocol.json
```

The accepted 2026-06-04 Codex++ fix for the DH-only view was:

```text
backup:
  C:\Users\HP\.codex\backups\app-ui-dh-only-fix-20260604-221525

script:
  C:\Users\HP\AppData\Roaming\Codex++\user_scripts\market-codex-list-pagebuster.js

storage version:
  2026-06-04-global-history-v7-explicit-mosim
```

Required script behavior:

- explicitly request `thread/list` for `C:\Users\HP\Desktop\MoSim` in addition
  to the global/default list, so a current DH native scope cannot starve MoSim;
- keep subagent project history visible in the supplemental list instead of
  treating `subagent` as internal hidden history;
- bump the localStorage version so stale DH-only or archived-hidden snapshots
  are discarded on the next App load.

After patching, run:

```cmd
C:\Users\HP\AppData\Local\OpenAI\Codex\bin\5b9024f90663758b\node.exe --check C:\Users\HP\AppData\Roaming\Codex++\user_scripts\market-codex-list-pagebuster.js
set CODEX_HOME=C:\Users\HP\.codex&& C:\Users\HP\AppData\Local\OpenAI\Codex\bin\716dda49c14d31a0\codex.exe doctor --json
```

Expected relevant doctor evidence:

```text
state DB integrity: ok
log DB integrity: ok
state.rollout_db_parity: ok
rollout DB active files/rows: 308 / 308
rollout DB archived files/rows: 0 / 0
rollout DB stale rows: 0
rollout DB sources: cli=308
```

### 4.5 VSCode Codex Shows DH Histories But MoSim Is Missing

Observed 2026-06-05: VSCode Codex was Windows-native
(`chatgpt.runCodexInWindowsSubsystemForLinux=false`) and therefore read
`C:\Users\HP\.codex\state_5.sqlite`. The plugin history list showed about 50
DH conversations because the active Windows DB contained only 15 MoSim-like
rows and 52 DH-like rows, while the latest WSL sync backup contained 215
MoSim-like rows.

Root cause: the frontend script was already configured to request the explicit
MoSim cwd, so the backend state was the limiting factor. The current Windows DB
had lost most MoSim thread rows and rollout files after earlier App/CLI state
repairs. Do not replace the whole DB with the backup, because that would lose
newer DH and current App state.

Safe repair pattern:

```text
source backup:
  C:\Users\HP\.codex\backups\latest-wsl-sync-20260604-225318\state_5.sqlite

current DB:
  C:\Users\HP\.codex\state_5.sqlite

pre-repair backup:
  C:\Users\HP\.codex\backups\pre-mosim-visibility-repair-20260605-104256
```

Before editing the DB, stop only the clearly related VSCode Codex app-server,
not the active Codex App conversation if it is being used:

```powershell
Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match 'openai.chatgpt-.*\\codex.exe app-server'
  } |
  Select-Object ProcessId,Name,CommandLine

Stop-Process -Id <vscode-codex-app-server-pid> -Force
```

Then perform a MoSim-only upsert:

- back up `state_5.sqlite`, `state_5.sqlite-shm`, `state_5.sqlite-wal`, and
  `session_index.jsonl`;
- `pragma integrity_check` before and after;
- read only backup `threads` rows where `cwd`, `title`, or
  `first_user_message` references `MoSim`;
- normalize those rows to `cwd=C:\Users\HP\Desktop\MoSim`,
  `archived=0`, `archived_at=NULL`, and valid `thread_source`;
- insert missing MoSim rows and update existing MoSim rows by `id`;
- copy only missing rollout files from backup `replaced_rollouts*` into
  `C:\Users\HP\.codex\sessions`; skip existing files and do not overwrite DH
  rollouts.

Verification after the accepted repair:

```text
sqlite integrity: ok
total threads:    271
MoSim active:     215
MoSim archived:   0
DH-like rows:     52
missing rollouts: 7
top cwd:          215 C:\Users\HP\Desktop\MoSim
```

The 7 missing MoSim rollout files were also missing from the available backup,
so those rows are useful for list/title visibility but may not open with full
message history. This is acceptable for the visibility repair and must not be
fixed by deleting or replacing unrelated DH records.

Follow-up correction from 2026-06-05: for the current Windows Codex App and
VSCode Codex runtime, the MoSim project list must use the extended Windows cwd
form:

```text
\\?\C:\Users\HP\Desktop\MoSim
```

Do not normalize current MoSim rows back to plain
`C:\Users\HP\Desktop\MoSim` unless a later runtime proves that exact form is
required. A confirmed good post-check was:

```text
state_5.sqlite total rows: 266
MoSim extended cwd rows:  210
MoSim plain cwd rows:     0
MoSim-like rows:          210
codex doctor thread issues: 3 residual stale/missing rollout rows
```

The active Windows Codex App conversation
`019e8181-6653-73b3-9685-f5bc9a24b947` is a healthy MoSim user thread:

```text
title/preview: first user message from 2026-06-01
cwd:           \\?\C:\Users\HP\Desktop\MoSim
archived:      0
has_user_event: 1
rollout_path:  \\?\C:\Users\HP\.codex\sessions\2026\06\01\rollout-2026-06-01T12-46-41-019e8181-6653-73b3-9685-f5bc9a24b947.jsonl
```

If the user says that a new Codex App reply is not visible in history, first
check whether it was appended to this existing thread. The history sidebar
title and preview can remain the first message, so searching for the latest
reply text can look like a missing conversation even though the rollout and DB
row are updating. Also separate the App and VSCode surfaces: the desktop App,
Windows CLI runtime, and VSCode extension can run different `codex.exe`
binaries at the same time, and VSCode may require a full reload before its
stdio app-server rereads the shared `C:\Users\HP\.codex` state.

After repair, reload VSCode or reopen the Codex webview so the extension starts
a fresh app-server against the repaired DB. If it still shows a DH-only list,
inspect the Codex++ pagebuster logs and browser localStorage version before
doing another SQLite edit.

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

### 5.1 Install Windows-Native Codex CLI From WSL Config

Use this route when the user explicitly needs `codex` to run directly in
Windows PowerShell/CMD. Current project policy is Windows-native Codex
configuration and history under `C:\Users\HP\.codex`, with ROS2/RViz2/FAST-LIO
runtime work still remaining in WSL.

#### 5.1.0 Current Windows Native TUI Status

As of 2026-06-05, the Windows native Codex CLI can be installed and can run
non-interactive commands, but the interactive TUI is not reliable on this
machine. Treat this as a known local/upstream TUI input issue, not as an
ordinary keyboard failure.

Observed symptom:

```text
interactive `codex` in Windows Terminal / PowerShell:
Backspace appears to move in the wrong direction;
Enter, paste, and deletion do not behave as normal text input.
```

The standard Windows input path was verified separately with:

```powershell
pwsh/powershell -ExecutionPolicy Bypass -File `
  C:\Users\HP\Desktop\MoSim\Scripts\tools\windows_key_probe.ps1
```

The key probe correctly read `A`, `Backspace`, `Delete`, `Enter`, pasted
characters, and `Escape`, so Windows Terminal, the keyboard, and PowerShell's
basic console input were working.

Routes already tried without fixing Codex TUI input:

```text
Windows PowerShell 5.1
PowerShell 7.6.2
`codex --no-alt-screen`
`features.terminal_resize_reflow = false`
`CODEX_TUI_DISABLE_KEYBOARD_ENHANCEMENT=1`
direct native `codex.exe`
direct `C:\nvm4w\nodejs\codex.cmd`
`powershell.exe -NoProfile`
temporary `@openai/codex@0.130.0` downgrade
```

Known external reports with similar symptoms include OpenAI Codex GitHub
issues `openai/codex#12542` and `openai/codex#4401`.

Practical guidance:

```text
Do not spend more time treating this as an input-method/profile issue unless a
new Codex release or Windows Terminal setting specifically targets this bug.
Use Codex App / VSCode Codex for Windows-native work, or WSL Codex TUI when an
interactive terminal TUI is required.
```

Known-good install route as of 2026-06-05:

```powershell
winget install --id CoreyButler.NVMforWindows --exact `
  --accept-package-agreements --accept-source-agreements --silent

$env:NVM_HOME = 'C:\Users\HP\AppData\Local\nvm'
$env:NVM_SYMLINK = 'C:\nvm4w\nodejs'
$env:Path = "$env:NVM_HOME;$env:NVM_SYMLINK;$env:Path"
nvm install lts
nvm use lts
```

Keep `C:\Users\HP\AppData\Local\nvm` and `C:\nvm4w\nodejs` before WindowsApps
in the Windows user `Path`; otherwise `node` can resolve to the Codex App
packaged `node.exe` under `C:\Program Files\WindowsApps\...`, which may fail
with `Access is denied`.

Current verified Node/Codex CLI toolchain:

```text
nvm:  C:\Users\HP\AppData\Local\nvm\nvm.exe
node: C:\nvm4w\nodejs\node.exe
npm:  C:\nvm4w\nodejs\npm.cmd
npx:  C:\nvm4w\nodejs\npx.cmd
node version: v24.16.0
npm/npx:      11.16.0
codex:        C:\nvm4w\nodejs\codex.cmd
codex version: 0.137.0
```

The canonical Windows command-line Codex environment is the npm/nvm install:

```text
C:\Users\HP\AppData\Local\nvm\v24.16.0\node_modules\@openai\codex
```

Do not use the Codex App packaged `codex.exe`, the VSCode extension packaged
`codex.exe`, or `C:\Users\HP\.codex\bin\codex.exe` as the user CLI. The App
and VSCode extension may still launch their own bundled binaries internally;
that is their private runtime, not the canonical shell CLI.

The old local CLI launcher used to be:

```bat
@echo off
set "CODEX_HOME=C:\Users\HP\.codex"
"%~dp0codex.exe" %*
```

As of 2026-06-05, remove `C:\Users\HP\.codex\bin` from the Windows user `Path`
so `where codex` resolves first to:

```text
C:\nvm4w\nodejs\codex
C:\nvm4w\nodejs\codex.cmd
```

The previous `.codex\bin` CLI files were moved out of the active PATH lane to:

```text
C:\Users\HP\.codex\bin\disabled-legacy-cli-20260605
```

For a CLI install, copy reusable WSL config inputs, but do not copy WSL session
databases or large runtime logs as the install mechanism unless the user
explicitly asks to migrate chat history:

```bash
cp -f /home/linux/.codex/auth.json /mnt/c/Users/HP/.codex/auth.json
cp -f /home/linux/.codex/rules/default.rules /mnt/c/Users/HP/.codex/rules/default.rules
cp -a /home/linux/.codex/skills/. /mnt/c/Users/HP/.codex/skills/
```

When generating the Windows-side `config.toml`, convert paths instead of doing
a byte-for-byte copy:

| WSL config item | Windows-native config item |
|---|---|
| `/mnt/c/Users/HP/Desktop/MoSim` | `C:\Users\HP\Desktop\MoSim` |
| `/mnt/e/...` | `E:\...` |
| `/home/linux/...` marketplace or trusted path | Do not copy into Windows-native Codex config; use Windows-local Codex/plugin paths. |
| WSL-only MCP wrapper such as `/home/linux/mcp-wrappers/ros_mcp.sh` | Do not bridge through `wsl.exe` in Windows-native Codex config. Use the project Windows `.cmd` wrapper, for example `C:\Users\HP\Desktop\MoSim\Docs\Skills\ROS-MCP\wrappers\ros-mcp.cmd`. |
| Sysplorer MCP | Windows Python: `D:\Program Files\MWORKS\Sysplorer 2026a\External\python64\python.exe` plus `Tools\sysplorer_mcp\main.py` |
| Syslab MCP | Windows executable: `D:\Program Files\MWORKS\Syslab 2026a\Tools\syslab-mcp-server\syslab-mcp-server-win64.exe` |
| Git MCP repo argument | `C:\Users\HP\Desktop\MoSim` with `C:\Users\HP\.local\bin\uvx.exe` |

Verify from Windows:

```cmd
codex --version
codex mcp list
codex doctor
```

Expected current version:

```text
codex-cli 0.136.0-alpha.2
```

Current non-fatal Windows doctor warnings can include unrestricted filesystem
sandbox or update-probe timeouts. A provider route timeout is a network/provider
issue, not an install or chat-migration issue. The install is usable when
`config.toml parse ok`, auth is configured, the expected MCP server list is
present, and `state.rollout_db_parity=ok` after any requested chat migration.

### 5.1.1 Repair Windows Codex Startup Warnings

Observed 2026-06-05 in Windows-native VSCode Codex:

```text
Skipped loading skill(s): missing YAML frontmatter delimited by ---
MCP client for `openai-api-key-local-confirmation` failed to start: program not found
MCP client for `git` timed out after 30 seconds
Starting MCP servers ... blender ...
```

Use this repair sequence after backing up `C:\Users\HP\.codex\config.toml` and
the affected files:

1. If a skill file visibly starts with `---` but Codex says frontmatter is
   missing, check the first bytes. `EF BB BF 2D 2D 2D` means UTF-8 BOM before
   the frontmatter. Rewrite the `SKILL.md` as UTF-8 without BOM.
2. For OpenAI Developers plugin MCP, patch every active
   `openai-developers\.mcp.json` copy under `C:\Users\HP\.codex` so
   `openai-api-key-local-confirmation.command` is an absolute Windows Node:

```text
C:\Users\HP\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe
```

   Do not copy or print API keys. This MCP only needs the local confirmation
   server to start.
3. Add explicit timeouts to Git MCP:

```toml
[mcp_servers.git]
startup_timeout_sec = 120
tool_timeout_sec = 300
```

4. If `codex plugin list` fails because `[marketplaces.local]` points at
   `C:\Users\HP\.codex`, create a real local marketplace root with
   `.agents\plugins\marketplace.json`, write it as UTF-8 without BOM, and point
   `[marketplaces.local].source` at that root. Current local plugin is
   `codex-session-tools@local`.
5. In Windows-native Codex mode, prefer the Windows Blender wrapper:

```toml
[mcp_servers.blender]
command = 'C:\Users\HP\Desktop\MoSim\Docs\Skills\Blender-MCP\wrappers\blender-mcp.cmd'
args = []
startup_timeout_sec = 180
tool_timeout_sec = 300
```

   Use the WSL `blender-mcp.sh` wrapper only for intentionally WSL-backed
   Codex sessions.

Fresh verification commands:

```powershell
codex plugin marketplace list
codex plugin list
codex mcp list
codex mcp get blender
codex doctor --summary --ascii --no-color
```

`doctor` may still warn that state DB rows point at missing rollout files. That
is the separate chat-history migration/visibility repair, not proof that these
skill or MCP startup warnings remain.

Windows-native MCP inventory guard:

- Expected project server name for Sysplorer is `sysplorer`. If
  `[mcp_servers.sysplorer_mcp]` appears, compare it with `[mcp_servers.sysplorer]`.
  When both point at the same `D:\Program Files\MWORKS\Sysplorer 2026a\Tools\sysplorer_mcp\main.py`
  command, remove the duplicate `sysplorer_mcp` section. It is a migration
  residue, not an additional project boundary.
- `node_repl` is not a MoSim project MCP server. In current Codex builds it is
  an internal Browser/Chrome/Computer Use plugin JavaScript execution channel
  referenced by bundled plugin/native-host files. Do not add it to the project
  MCP inventory unless a future plugin explicitly requires a managed entry.
- CC Switch has its own MCP registry in
  `C:\Users\HP\.cc-switch\cc-switch.db` table `mcp_servers`. If CC Switch still
  shows `sysplorer_mcp` or `node_repl` after `codex mcp list` is clean, inspect
  that table before changing Codex config again:

```powershell
sqlite3 'C:/Users/HP/.cc-switch/cc-switch.db' `
  "SELECT id, name, enabled_codex, enabled_opencode, substr(server_config,1,220) FROM mcp_servers ORDER BY name;"
```

  Before editing the CC Switch database, stop `cc-switch.exe` and back up
  `C:\Users\HP\.cc-switch\cc-switch.db` under
  `C:\Users\HP\.cc-switch\backups\`. `sysplorer` and `sysplorer_mcp` may both
  point at the same MWORKS-installed Sysplorer MCP under
  `D:\Program Files\MWORKS\Sysplorer 2026a\Tools\sysplorer_mcp`. Use
  `sysplorer` as the canonical Codex server name, but keep `sysplorer_mcp` if a
  different client such as opencode has it enabled. To avoid duplicate Codex
  startup, set `sysplorer_mcp.enabled_codex=0` instead of deleting the row when
  another client still needs it. It is safe to remove `node_repl` from the
  MoSim/CC Switch project MCP list when Browser/Chrome/Computer Use is not
  being managed there. Do not remove `sysplorer` or `syslab`; those are the
  correct MWORKS built-in MCP entries.
- WSL wrappers and Windows direct entries are launch routes, not separate MCP
  implementations. Current WSL `syslab_mcp.sh` launches the Windows Syslab MCP
  server through `/init ... cmd.exe` with:

```text
--syslab-root D:\Program Files\MWORKS\Syslab 2026a
--julia-root C:\Users\Public\TongYuan\julia-1.10.10
--syslab-display-mode nodesktop
```

  Keep the Windows `syslab` entry aligned with those args. Current WSL
  `sysplorer_mcp.sh` launches Windows Sysplorer Python through the project
  bridge `Scripts\mworks\sysplorer_mcp_wsl_entry.py`, which runs the installed
  inner server `Tools\sysplorer_mcp\sysplorer-mcp-server\main.py`. Current
  Windows `sysplorer` can use the installed top-level
  `Tools\sysplorer_mcp\main.py`; that sidecar launcher sets `MCP_DEPLOY_ROOT`
  and then runs the same inner server. Do not download or create a second
  Syslab/Sysplorer MCP server just because the WSL and Windows launch commands
  differ.
- Codex may initially expose only `tool_search` in the visible tool list. That
  is deferred MCP tool discovery, not necessarily a failed MCP startup. Use
  targeted discovery queries such as `sysplorer syslab MWORKS` or
  `mosim unreal epic windows` and then verify the loaded namespaces. After
  editing `config.toml`, restart VSCode Codex/app-server to drop stale
  namespaces from the already-started tool surface.

### 5.2 Windows-MCP Desktop Automation Server

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

Use the Windows-native wrapper at:

```text
C:\Users\HP\Desktop\MoSim\Docs\Skills\Windows-MCP\wrappers\windows-mcp.cmd
```

Register it in the Windows-native Codex config:

```toml
[mcp_servers."windows-mcp"]
command = 'C:\Users\HP\Desktop\MoSim\Docs\Skills\Windows-MCP\wrappers\windows-mcp.cmd'
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
windows-mcp   C:\Users\HP\Desktop\MoSim\Docs\Skills\Windows-MCP\wrappers\windows-mcp.cmd   enabled
```

Security note: Windows-MCP can operate the Windows desktop and run PowerShell
commands. Use the smallest necessary tool call and avoid broad desktop or
filesystem actions unless the user explicitly requests them.

### 5.3 ROS-MCP Robot Bridge Server

ROS-MCP connects MCP clients to ROS or ROS 2 systems through rosbridge. The MCP
server can start without ROS installed, but robot operations require a reachable
rosbridge websocket, normally `127.0.0.1:9090` or a robot IP on port `9090`.
The project-local checkout is version-agnostic: its README advertises both ROS
and ROS2 support. The active ROS generation is determined by the ROS runtime
behind rosbridge. For this WSL project host, use ROS2 Humble.

Install or repair the source checkout runtime:

```bash
uv --directory Docs/Skills/ROS-MCP sync
```

Use a WSL wrapper at:

```text
/home/linux/mcp-wrappers/ros_mcp.sh
```

Expected wrapper command:

```bash
ROOT="${ROS_MCP_ROOT:-/mnt/c/Users/HP/Desktop/MoSim/Docs/Skills/ROS-MCP}"
ROS_SETUP="${ROS_SETUP:-/opt/ros/humble/setup.bash}"
ROSBRIDGE_HOST="${ROSBRIDGE_HOST:-127.0.0.1}"
ROSBRIDGE_PORT="${ROSBRIDGE_PORT:-9090}"
ROSBRIDGE_AUTO_START="${ROSBRIDGE_AUTO_START:-1}"
exec /home/linux/.local/bin/uv --directory "$ROOT" run server.py --transport=stdio
```

The actual wrapper is allowed to perform a small preflight before the final
`exec`: if `ROSBRIDGE_AUTO_START=1` and `ROSBRIDGE_HOST:ROSBRIDGE_PORT` is not
listening, it sources `/opt/ros/humble/setup.bash`, verifies
`rosbridge_server`, launches
`ros2 launch rosbridge_server rosbridge_websocket_launch.xml port:=9090` with
`nohup`, writes logs under `Results/logs/rosbridge_mcp/`, waits briefly for the
port, and then starts the MCP server. If port `9090` is already listening, it
reuses the existing rosbridge process.

Register it in the Codex config:

```toml
[mcp_servers."ros-mcp"]
command = "/home/linux/mcp-wrappers/ros_mcp.sh"
args = []
startup_timeout_sec = 180
tool_timeout_sec = 300
```

For safety, keep robot write/control tools approval-gated:

```toml
[mcp_servers."ros-mcp".tools.publish_once]
approval_mode = "approve"

[mcp_servers."ros-mcp".tools.publish_for_durations]
approval_mode = "approve"

[mcp_servers."ros-mcp".tools.call_service]
approval_mode = "approve"

[mcp_servers."ros-mcp".tools.send_action_goal]
approval_mode = "approve"

[mcp_servers."ros-mcp".tools.cancel_action_goal]
approval_mode = "approve"

[mcp_servers."ros-mcp".tools.set_parameter]
approval_mode = "approve"

[mcp_servers."ros-mcp".tools.delete_parameter]
approval_mode = "approve"
```

Verify:

```bash
codex mcp list
```

Expected entry:

```text
ros-mcp   /home/linux/mcp-wrappers/ros_mcp.sh   enabled
```

Current WSL diagnosis on 2026-06-01:

```text
ROS_VERSION=2
ROS_DISTRO=humble
ROS2 apt source=/etc/apt/sources.list.d/ros2.list
ROS2 apt key=/usr/share/keyrings/ros-archive-keyring.gpg
apt update probe=passed, no NO_PUBKEY/EXPKEYSIG observed
rosbridge_server=installed
port 9090=listening after manual launch; wrapper now auto-starts it when absent
```

Useful checks:

```bash
source /opt/ros/humble/setup.bash
ros2 pkg prefix rosbridge_server
apt-cache policy ros-humble-rosbridge-suite
ss -ltnp | grep -E ':9090|rosbridge'
```

If `rosbridge_server` is missing, install the ROS2 bridge package before
expecting ROS-MCP to inspect or control the ROS graph:

```bash
sudo apt install -y ros-humble-rosbridge-suite
source /opt/ros/humble/setup.bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

Normal Codex usage should not require a separate rosbridge terminal after the
wrapper is installed. Starting Codex/MCP is enough; the wrapper performs the
background launch only when the port is absent.

Security note: ROS-MCP can publish topics, call services, send actions, and set
parameters on a connected robot or simulator. Treat these as robot-control
operations and run read-only discovery first: `connect_to_robot`,
`ping_robots`, `get_topics`, `get_nodes`, and `get_services`.

Reference only:

---

## 6. Codex App / VSCode / WSL Session Policy

Use the current Windows-native VSCode/Codex conversation under
`C:\Users\HP\.codex` as the primary project conversation unless the user
explicitly switches the primary entry point. WSL remains the runtime lane for
ROS2, RViz2, FAST-LIO-family, and Linux-native robotics tooling. Codex App is a
Windows desktop front end for reviewing the same project and for opening
additional conversations.

Do not assume the App, VSCode extension, and WSL IDE extension share one live
session store. They may share copied configuration, but their local session
indexes can differ:

```text
Windows-native VSCode/Codex sessions: C:\Users\HP\.codex\sessions
Windows-native Codex index:           C:\Users\HP\.codex\state_5.sqlite
WSL Codex sessions, legacy/runtime:   /home/linux/.codex/sessions
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

### 6.1 Full WSL To Windows Chat History Migration

Use this only when the user explicitly asks to migrate chat history into the
Windows-native Codex home. It is infrastructure work outside the project tree,
so state the external paths first:

```text
source: /home/linux/.codex
target: C:\Users\HP\.codex
```

Required safety sequence:

```text
1. Close Codex App if practical.
2. Back up Windows session_index.jsonl, state_5.sqlite*, and manifests of
   existing Windows rollout files under C:\Users\HP\.codex\backups\...
3. Compare WSL and Windows rollout inventories before copying.
4. For duplicate rollout IDs, byte-identical files are skipped. If the files
   differ, back up the Windows copy and let the WSL copy win unless the user
   has requested a different conflict policy.
5. Preserve Windows-only rollout files and Windows-only session_index entries.
6. Copy WSL-only active rollouts into C:\Users\HP\.codex\sessions and WSL-only
   archived rollouts into C:\Users\HP\.codex\archived_sessions.
7. Merge session_index.jsonl by conversation ID, preferring WSL entries for
   duplicate IDs and preserving Windows-only IDs.
8. Repoint Windows state_5.sqlite threads.rollout_path values from
   /home/linux/.codex or WSL paths to C:\Users\HP\.codex paths.
9. Verify SQLite integrity, missing rollout paths, duplicate IDs, and rollout
   file to DB parity.
```

Validated 2026-06-04 migration result:

```text
backup: C:\Users\HP\.codex\backups\wsl-chat-migration-20260604-200448
active rollout files: 119
archived rollout files: 191
session_index entries: 215 unique
state_5.sqlite threads rows: 310
rollout DB active rows: 119
rollout DB archived rows: 191
rollout DB archive mismatches: 0
missing rollout paths: 0
Linux-style rollout paths in Windows DB: 0
SQLite integrity: ok
```

The 2026-06-04 migration preserved the Windows-only thread
`019e7c99-e807-7cc1-b1b4-2a88d012a68e`. Three shorter Windows conflicting
rollouts were backed up and replaced by WSL copies:

```text
019e8358-86b4-7070-8fd6-a2b4f4d2af97
019e0198-a041-77f1-84d0-c5524bfd4b81
019e74de-a452-7a50-99e7-ca9a247b32f1
```

Correction from 2026-06-05 user review: thread
`019e8358-86b4-7070-8fd6-a2b4f4d2af97` was created after WeChat human
intervention. It is not the dedicated WeChat gateway operations conversation
and must not be treated as the owner for cc-connect runtime maintenance, QR
recovery, or notification-channel health.

Dedicated WeChat gateway operations thread, manually created by the user on
2026-06-05 CST:

```text
019e9855-aa43-7fe2-807e-be7d4095877b = MoSim｜微信网关运维
```

Use this thread for cc-connect runtime maintenance, QR/context-token recovery,
and sparse notification-channel diagnostics. Keep WeChat intervention/event
threads separate from this operations thread.

WeChat path ownership:

```text
019e8358-86b4-7070-8fd6-a2b4f4d2af97
```

is the Codex conversation used by the WeChat-side message path. It is not an
operations owner. Do not ask this conversation to maintain cc-connect, QR
login, context-token, active-session, scheduled health checks, or gateway
recovery.

The gateway operations thread:

```text
019e9855-aa43-7fe2-807e-be7d4095877b = MoSim｜微信网关运维
```

owns cc-connect runtime health, QR login, stale context-token recovery, and
notification-path diagnostics.

Send gateway maintenance instructions to `019e9855-aa43-7fe2-807e-be7d4095877b`,
not to `019e8358-86b4-7070-8fd6-a2b4f4d2af97`.

Scheduled health check route:

```cmd
python Scripts\agent\check_weixin_gateway_health.py
```

This is local-only and writes a JSON health snapshot under
`Results/coagent_gateway/health/`. It checks data-dir existence, API socket,
project session file, active platform session, and context-token files without
sending a WeChat message.

Explicit low-frequency outbound canary:

```cmd
python Scripts\agent\check_weixin_gateway_health.py --send-canary
```

Use this sparingly, for example once every few hours or at work-session start.
Do not run a real send canary every few minutes because Weixin/iLink can reject
stale or high-frequency sends with `ret=-2`.

Windows Task Scheduler example for local-only health snapshots every 15 minutes:

```cmd
schtasks /Create /TN "MoSim Weixin Gateway Local Health" /SC MINUTE /MO 15 /TR "cmd /c cd /d C:\Users\HP\Desktop\MoSim && python Scripts\agent\check_weixin_gateway_health.py" /F
```

Optional outbound canary every 4 hours:

```cmd
schtasks /Create /TN "MoSim Weixin Gateway Canary" /SC HOURLY /MO 4 /TR "cmd /c cd /d C:\Users\HP\Desktop\MoSim && python Scripts\agent\check_weixin_gateway_health.py --send-canary" /F
```

Background maintenance rule:

```text
Codex conversations are not persistent daemons. Do not rely on the
MoSim｜微信网关运维 conversation staying open to maintain WeChat. Durable
maintenance is Windows Task Scheduler plus Scripts/agent/check_weixin_gateway_health.py.
```

Current scheduled-health verification, 2026-06-06 CST:

```text
MoSim Weixin Gateway Local Health:
  enabled, every 15 minutes
  command: cmd /c cd /d C:\Users\HP\Desktop\MoSim && python Scripts\agent\check_weixin_gateway_health.py
  observed last run: 2026/6/6 0:06:01
  observed last result: 0
  observed next run: 2026/6/6 0:21:00

MoSim Weixin Gateway Canary:
  enabled, every 4 hours
  command: cmd /c cd /d C:\Users\HP\Desktop\MoSim && python Scripts\agent\check_weixin_gateway_health.py --send-canary
  observed next run: 2026/6/6 3:21:00
  frequency must not be increased for routine monitoring
```

Latest-file contract:

```text
Results/coagent_gateway/health/gateway_healthy_latest.json
  Written when local cc-connect health is OK.

Results/coagent_gateway/health/gateway_unhealthy_latest.json
  Written when local health fails.
  This is the first file to inspect when background maintenance reports a
  problem, because WeChat may be the broken channel and cannot be trusted for
  failure notification.
```

The health script classifies local failures into:

| Failure kind | Meaning | Minimal action |
|---|---|---|
| `data_dir` | WSL data directory is inaccessible | Check WSL/Ubuntu-22.04 availability and project data path. |
| `api_socket` | cc-connect API socket is missing or not connectable | Restart or inspect cc-connect; do not ask the user to send WeChat first. |
| `session` | Project session file is missing | Recreate/reselect `MoSim｜微信通知网关`; QR may be needed. |
| `active_session` | Session exists but no platform active session is usable | Ask the user to send one ordinary message in the gateway chat, then retry once. |
| `context_token` | No local context token file | Ask the user to send one ordinary message; if still absent, rerun QR login. |
| `unknown` | Probe output does not match known categories | Inspect the latest JSON before taking action. |

On local health failure, the script may attempt a Windows local toast. This is
best-effort only. The latest JSON file is authoritative. The script must not
try to report local health failure by WeChat because WeChat may be the failing
surface.

Adapter default route correction, 2026-06-06 CST:

```text
CoAgent/gateway/cc_connect_weixin.py now uses a platform-aware default data-dir.
Windows resolves the default to:
\\wsl.localhost\Ubuntu-22.04\home\linux\.cache\mosim\coagent\cc-connect-weixin\data

Linux/WSL resolves the default to:
/home/linux/.cache/mosim/coagent/cc-connect-weixin/data
```

This keeps other Codex conversations from failing with
`no active session found (key="")` when they call the narrow adapter without
passing `--data-dir`.

Cross-thread notification guarantee:

1. Other Codex conversations must not maintain their own WeChat transport.
   They should create sparse JSON packets under `Results/coagent_gateway/`
   and send them only through:

   ```cmd
   python CoAgent\gateway\cc_connect_weixin.py notify --packet <packet.json> --send
   ```

2. Other conversations should treat send failure as a reportable gateway issue,
   not as a reason to retry in a loop. On failure, they should record the
   packet path and recovery path, then continue file-based progress if the task
   does not require immediate user approval.

3. `MoSim｜微信网关运维`
   (`019e9855-aa43-7fe2-807e-be7d4095877b`) owns the shared transport health:
   scheduled local snapshots, low-frequency outbound canary, latest failure
   classification, QR/context-token recovery, and instructions to the user.

4. Before a long-running task starts, the owning conversation should run the
   local health probe once. If it is unhealthy, it should ask
   `MoSim｜微信网关运维` to recover the gateway before relying on WeChat
   progress messages.

5. At completion, blocker, or manual-review time, the owning conversation sends
   exactly one sparse notification packet. It must not mirror logs, tool output,
   or full chat contents through WeChat.

Current scheduled-health verification, 2026-06-05 CST:

```text
MoSim Weixin Gateway Local Health:
  enabled, every 15 minutes
  command: cmd /c cd /d C:\Users\HP\Desktop\MoSim && python Scripts\agent\check_weixin_gateway_health.py
  observed next run: 2026/6/5 23:36:00

MoSim Weixin Gateway Canary:
  enabled, every 4 hours
  command: cmd /c cd /d C:\Users\HP\Desktop\MoSim && python Scripts\agent\check_weixin_gateway_health.py --send-canary
  observed next run: 2026/6/6 3:21:00
```

Both tasks showed the Task Scheduler sentinel `LastRunTime = 1999/11/30
0:00:00` and `LastTaskResult = 267011` during the initial verification. Treat
that as "registered but not yet proven by a scheduler-triggered run" until a
later scheduled run updates those fields.

Manual local-only health check on 2026-06-05 CST:

```cmd
python Scripts\agent\check_weixin_gateway_health.py
```

Result snapshot:

```text
Results/coagent_gateway/health/weixin_gateway_health_20260605_232655.json
ok_local=true
api_socket_exists=true
active_session_present=true
active_session_key_type=platform
context_token_files=1
send_canary=null
```

Real canary incident, 2026-06-05 CST:

```text
First failure:
  WinError 193 because Windows tried to execute the Linux ELF cc-connect binary
  directly.

Fix:
  CoAgent/gateway/cc_connect_weixin.py now bridges Windows sends through
  wsl.exe -d Ubuntu-22.04 -- /mnt/c/.../cc-connect.
  Scripts/agent/check_weixin_gateway_health.py now passes the WSL-backed
  data-dir explicitly for canary sends.

Actual outbound result after the launcher fix:
  cc-connect reached Weixin sendMessage, but Weixin returned ret=-2 errcode=0
  after three fresh-context retries.
  Evidence log:
  Results/tmp/cc-connect-weixin-smoke/recover-20260605_233952.log
```

Current local health probe after script correction:

```text
Results/coagent_gateway/health/weixin_gateway_health_20260605_234230.json
ok_local=true
api_socket_exists=true
api_socket_connectable=true
active_session_present=true
active_session_key_type=platform
context_token_files=1
send_canary=null
```

Interpretation: local cc-connect runtime/session health can be good while
end-to-end Weixin outbound send is still broken. `ret=-2` is a Weixin/iLink
send-context problem, not a missing project session or missing local
`context_tokens.json`.

Minimal recovery ask for `ret=-2`:

```text
Ask the user to send one ordinary plain-text message in the
MoSim｜微信通知网关 WeChat chat, then retry one canary. If it still fails with
ret=-2, rerun cc-connect Weixin QR login.
```

2026-06-05 CST follow-up: after the user sent one ordinary WeChat message,
fixing the adapter recovery wait to require `api_socket_connectable` allowed a
single retry canary to pass. Evidence:

```text
Results/coagent_gateway/health/weixin_gateway_health_20260605_235034.json
send_result.ok=true
stdout="Message sent successfully."
```

Do not run the canary by default during operations checks. If local health
fails, open the newest `Results/coagent_gateway/health/*.json` and classify the
failure before asking the user to act:

| Failed field | Classification | Minimal user action |
|---|---|---|
| `api_socket_exists=false` | `api_socket` / cc-connect runtime socket absent | No immediate user action; inspect/restart cc-connect once through the documented adapter path. |
| `project_session_files=0` or missing project session file | `session` | Recreate or reselect the `MoSim｜微信通知网关` cc-connect project session. |
| `active_session_present=false` or `active_session_key_type` is not `platform` | `active_session` | Ask the user to send one normal message in the WeChat gateway chat, then retry once. |
| `context_token_files=0` | `context_token` | Ask the user to send one normal message in the WeChat gateway chat; if still absent, rerun QR login. |
| outbound `ret=-2` during an explicit canary/send | stale Weixin/iLink send context | Ask the user to send one normal message in the WeChat gateway chat, then retry once. |

After migration, run:

```cmd
codex doctor --json
codex mcp list
```

`state.rollout_db_parity=ok`, `config.load=ok`, and `mcp.config=ok` prove the
local chat/config shape. Provider route timeouts or update-probe warnings are
separate network issues and do not by themselves invalidate the chat migration.

### 6.2 Clear A Wrong Codex Goal

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

---

## 11. Blender MCP

Project-local source:

```text
Docs/Skills/Blender-MCP
```

Project-local wrapper:

```bash
Docs/Skills/Blender-MCP/wrappers/blender-mcp.sh
```

The wrapper runs the local editable install from
`Docs/Skills/Blender-MCP/.venv` and disables telemetry by default:

```bash
DISABLE_TELEMETRY=true
BLENDER_HOST=172.17.48.1
BLENDER_PORT=9876
```

Codex registration command:

```bash
codex mcp add blender \
  --env DISABLE_TELEMETRY=true \
  --env BLENDER_HOST=172.17.48.1 \
  --env BLENDER_PORT=9876 \
  -- /mnt/c/Users/HP/Desktop/MoSim/Docs/Skills/Blender-MCP/wrappers/blender-mcp.sh
```

Install/update local Python environment:

```bash
rm -rf Docs/Skills/Blender-MCP/.venv
uv venv --python /usr/bin/python3 Docs/Skills/Blender-MCP/.venv
uv pip install --python Docs/Skills/Blender-MCP/.venv/bin/python -e Docs/Skills/Blender-MCP
```

The server is two-stage:

1. Codex starts the MCP stdio server through the wrapper.
2. The MCP server connects to the Blender addon socket.

Blender-side setup:

1. In Blender, install `Docs/Skills/Blender-MCP/addon.py`.
2. Enable `Interface: Blender MCP`.
3. In the Blender viewport sidebar, open the `BlenderMCP` tab.
4. Set port `9876`.
5. Click `Connect to MCP server`.
6. Disable addon telemetry in preferences unless explicitly needed.

Smoke checks:

```bash
codex mcp list
Docs/Skills/Blender-MCP/.venv/bin/python -c "import blender_mcp.server as s; print(s.DEFAULT_HOST, s.DEFAULT_PORT)"
```

Expected MCP list entry:

```text
blender  /mnt/c/Users/HP/Desktop/MoSim/Docs/Skills/Blender-MCP/wrappers/blender-mcp.sh  enabled
```

If Codex starts the MCP but tools cannot reach Blender, first verify the addon
socket is running. WSL cannot reach a Windows-only `localhost` listener through
its own `127.0.0.1`, so the project bootstrap binds the Blender addon server to
`0.0.0.0` and the Codex MCP env points `BLENDER_HOST` at the WSL default
gateway, currently `172.17.48.1`.

If `mcp__blender` was started before this host fix, it may keep the old process
environment:

```bash
tr '\0' '\n' < /proc/{pid}/environ | rg 'BLENDER_HOST|BLENDER_PORT|DISABLE_TELEMETRY'
```

An old process showing `BLENDER_HOST=127.0.0.1` must be stopped and the Codex
session restarted so the MCP tool channel is recreated with the updated config.
Independent end-to-end validation can be done with a short Python MCP client
against `Docs/Skills/Blender-MCP/wrappers/blender-mcp.sh`; the pass condition is
that `list_tools` returns Blender tools and `get_scene_info` returns the default
`Cube`, `Light`, and `Camera` scene.

When WindowsMCP is available, verify Blender MCP visually instead of inferring
UI state from logs. Use a WindowsMCP screenshot after launching Blender and
confirm the terminal/Blender UI shows:

```text
BlenderMCP addon registered
BlenderMCP server started on 0.0.0.0:9876
Connected to client
```

Safety:

```text
execute_blender_code can run arbitrary Python inside Blender. Use it only on
project assets, save before destructive edits, and avoid sending secrets,
tokens, browser paths, or personal files through Blender MCP.
```
