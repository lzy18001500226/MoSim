# Round 1 CLI/App Infrastructure Detail Memory

Date: 2026-06-04 CST

Scope: newly surfaced fine-grained Codex CLI/App/VSCode/MCP operating memories
from the visible `MoSim|鍥涙棆缈兼棤浜烘満浠跨湡绯荤粺` conversation after the main
session-memory migration closeout.

This file is cache-only. It does not prove the current machine state, does not
authorize reading or modifying external `.codex` files, and does not promote
any chat-only operational fact into a formal workflow. Each item must pass
round 2 and round 3 before it can change `Docs/Workflows/debug_mcp.md`,
`Docs/Index/codex_app_session_research.md`, or any other formal document.

## Status

```text
round: 1
topic: Codex CLI/App session, token, resume, proxy, and MCP detail memory
status: candidate_cache_created
risk: medium
formal_docs_patched_this_round: none
next_required_round:
  round 2 must re-read current debug_mcp.md, codex_app_session_research.md,
  current Codex CLI/App behavior if explicitly requested, and relevant MCP
  wrapper/config files before any formal patch
```

## Candidate Items

### CLI-DETAIL-MEM-001 - `/status` Is The Built-In Command, `/tokens` Is Not

```text
topic: Codex CLI token/status UX
round: 1
status: candidate
risk: medium
candidate_statement:
  The user corrected `/statas` to `/status`. In the current CLI conversation,
  `/status` is the recognized built-in command surface, while `/tokens` was
  rejected as an unrecognized command and plain `tokens` was treated as user
  text. A future token shortcut must be implemented through a supported CLI
  command/plugin mechanism or an external terminal command, not assumed to
  exist.
known_sources:
  - Visible conversation: `/tokens` returned "Unrecognized command '/tokens'".
  - Existing infrastructure memory: durable state is docs/cache, not live
    CLI/App sync.
contradictions_or_history:
  A prior attempt apparently made a `codex-session-tools:tokens` style helper,
  but invoking `/codex-session-tools:tokens` directly in bash failed because it
  is not a shell executable path.
current_evidence_needed:
  Round 2 should inspect current Codex plugin/skill command support and any
  project-local session tools before recommending a shortcut.
formal_target_if_promoted:
  Docs/Workflows/debug_mcp.md or a small project-local CLI utility note, only
  if a current supported route exists.
next_round_action:
  Verify current Codex slash-command/plugin behavior and record the shortest
  supported token-report command without inventing unsupported `/tokens`.
```

### CLI-DETAIL-MEM-002 - Token Totals Need An Authoritative Counter Source

```text
topic: total token accounting
round: 1
status: candidate
risk: medium
candidate_statement:
  The user wants total token usage for the whole conversation, matching API-like
  billing semantics rather than only visible-context size. `/status` or the
  TUI may not show prior historical token totals after resume or app/CLI
  migration. Any reported total must name the counter source and scope.
known_sources:
  - Visible conversation: user asked for the total and referenced a very large
    historical count, not only current context.
  - Docs/Workflows/debug_mcp.md records that the Windows App state row once had
    nearly `1e9` tokens for the large MoSim session.
contradictions_or_history:
  The visible CLI could not show the old VSCode/App transcript after some
  resume/update paths. A token count derived only from the current visible TUI
  would undercount the long session.
current_evidence_needed:
  Round 2 should identify which current local state field, if any, records
  total conversation tokens, and whether reading it requires a fresh explicit
  infrastructure request because it is outside the project directory.
formal_target_if_promoted:
  Docs/Workflows/debug_mcp.md only, and only as a diagnostic route with source
  and privacy boundaries.
next_round_action:
  Do not report a new total from memory. Re-check current counter storage only
  if the user explicitly requests token accounting infrastructure work.
```

### CLI-DETAIL-MEM-003 - `codex resume -C <project> <thread-id>` Is The Reliable Resume Form

```text
topic: Codex CLI resume workflow
round: 1
status: candidate
risk: medium
candidate_statement:
  For the long MoSim thread, the reliable CLI resume command was
  `codex resume -C /mnt/c/Users/HP/Desktop/MoSim <thread-id>`. Starting plain
  `codex` inside the project may still fail to list or select the desired
  session when the session index/cwd metadata points elsewhere.
known_sources:
  - Visible conversation: `codex resume -C /mnt/c/Users/HP/Desktop/MoSim
    019e0198-a041-77f1-84d0-c5524bfd4b81` allowed entry.
  - Docs/Index/codex_app_session_research.md records stale-path resume errors
    when session metadata points to an old cwd.
contradictions_or_history:
  The user wanted `/resume` inside plain `codex` from the project folder to
  find the session without a long command. Observed behavior did not reliably
  support that.
current_evidence_needed:
  Round 2 should verify current Codex CLI version behavior and current session
  index metadata before formalizing a shorter command or alias.
formal_target_if_promoted:
  Docs/Workflows/debug_mcp.md or a project-local new-conversation handoff note.
next_round_action:
  Keep the explicit `-C` resume route as a candidate fallback; do not patch
  external session metadata unless explicitly asked.
```

### CLI-DETAIL-MEM-004 - Resume Directory Prompt Is A UX Constraint, Not A Project Fact

```text
topic: Codex resume working-directory prompt
round: 1
status: candidate
risk: medium
candidate_statement:
  When resuming, Codex prompted "Choose working directory to resume this
  session" between the stored session directory and the current project
  directory. The user wanted it to default to the current directory option. This
  is a Codex CLI/App UX/config behavior, not a MoSim engineering state.
known_sources:
  - Visible conversation: prompt offered session directory
    `/mnt/c/Users/HP/Desktop/Codex` and current directory
    `/mnt/c/Users/HP/Desktop/MoSim`.
contradictions_or_history:
  Attempts to rely on stored session cwd caused stale or wrong path behavior.
current_evidence_needed:
  Round 2 should check whether current Codex supports a config key, flag, or
  alias to default to current cwd; otherwise preserve the manual selection as
  an accepted limitation.
formal_target_if_promoted:
  Docs/Workflows/debug_mcp.md only if a supported current-CWD default route is
  confirmed.
next_round_action:
  Verify with current CLI help/config before writing any formal instruction.
```

### CLI-DETAIL-MEM-005 - Lowercase `/mnt/c/users/.../mosim` Display Is Not Evidence Of A Project Move

```text
topic: path display normalization
round: 1
status: candidate
risk: low
candidate_statement:
  The CLI/TUI sometimes displayed the project path in lowercase, such as
  `/mnt/c/users/hp/desktop/mosim`, even when the user started from
  `/mnt/c/Users/HP/Desktop/MoSim`. Treat this as path display or resume
  normalization unless current filesystem evidence shows an actual project
  relocation.
known_sources:
  - Visible conversation: user reported lowercase path display after resuming.
  - Current environment can still operate from `/mnt/c/Users/HP/Desktop/MoSim`.
contradictions_or_history:
  The user suspected a `/resume` bug. No project file change is implied by the
  lowercase display alone.
current_evidence_needed:
  Round 2 should compare `pwd`, workspace root, and Codex cwd metadata if this
  becomes operationally relevant.
formal_target_if_promoted:
  Usually none. At most a debug note in Docs/Workflows/debug_mcp.md.
next_round_action:
  Do not rename project paths or patch design docs because of TUI casing.
```

### CLI-DETAIL-MEM-006 - WSL Localhost Proxy Warning Needs A Host-IP Proxy Route

```text
topic: WSL proxy warning
round: 1
status: candidate
risk: medium
candidate_statement:
  WSL can warn that a Windows localhost proxy is detected but not mirrored into
  WSL because NAT-mode WSL does not support localhost proxy mirroring. The
  user observed proxy port `7897` and wanted the warning to stop. The likely
  reusable route is to configure WSL-side proxy environment variables to the
  Windows host IP plus port, or change WSL/network proxy settings, but current
  host state must be checked before documenting exact commands.
known_sources:
  - Visible conversation: WSL printed the localhost proxy warning and user
    identified port `7897`.
  - Docs/Workflows/debug_mcp.md records localhost proxy and AppContainer
    loopback behavior for Windows Codex App.
contradictions_or_history:
  Windows AppContainer loopback exemption and WSL NAT proxy routing are related
  but not the same fix. Do not collapse them into one command.
current_evidence_needed:
  Round 2 should inspect current shell proxy env vars, WSL version/network mode,
  and whether the project wants a persistent shell profile entry; this requires
  explicit infrastructure scope if outside the project.
formal_target_if_promoted:
  Docs/Workflows/debug_mcp.md, as infrastructure troubleshooting only.
next_round_action:
  Record exact commands only after live-checking current WSL/network state.
```

### CLI-DETAIL-MEM-007 - `CheckNetIsolation` Syntax Differs Between PowerShell And `cmd`

```text
topic: Windows Codex App loopback exemption
round: 1
status: candidate
risk: medium
candidate_statement:
  In PowerShell, `%SystemRoot%\System32\CheckNetIsolation.exe` is not expanded
  like it is in `cmd`; use `& "$env:SystemRoot\System32\CheckNetIsolation.exe"`
  or the literal `C:\Windows\System32\CheckNetIsolation.exe`. On this machine,
  `-n=OpenAI.Codex_2p2nqsd0c76g0` returned invalid parameters, while existing
  debug docs point to the lower-case AppContainer moniker
  `openai.codex_2p2nqsd0c76g0` or the mapped SID route.
known_sources:
  - Visible conversation: PowerShell rejected `%SystemRoot%...`; literal
    `C:\Windows\System32\CheckNetIsolation.exe` ran but `OpenAI.Codex...`
    package family parameter was invalid.
  - Docs/Workflows/debug_mcp.md already documents the lower-case moniker and
    SID fallback.
contradictions_or_history:
  `Get-AppxPackage` package family names and AppContainer monikers can differ.
current_evidence_needed:
  Round 2 should re-read the current debug_mcp.md section and, only if needed,
  live-check the mapping registry before changing the formal command.
formal_target_if_promoted:
  Already likely represented in Docs/Workflows/debug_mcp.md.
next_round_action:
  Mark as already formalized if the command remains present and correct.
```

### CLI-DETAIL-MEM-008 - Windows-MCP And ROS-MCP Are Useful But Permission-Sensitive

```text
topic: installed MCP skill/tool boundaries
round: 1
status: candidate
risk: medium
candidate_statement:
  Windows-MCP and ROS-MCP were installed from project-local `Docs/Skills/*`
  sources. Windows-MCP can inspect/click/control the Windows desktop, so it
  must be used narrowly. ROS-MCP is ROS-version-agnostic at the MCP checkout
  level and connects through rosbridge; the active ROS generation is the ROS
  runtime behind rosbridge, currently intended as ROS2 Humble for MoSim.
known_sources:
  - Visible conversation: user asked what Windows-MCP can do, requested taskbar
    inspection/click attempts, installed ROS-MCP, and asked whether it is ROS1
    or ROS2.
  - Docs/Workflows/debug_mcp.md contains Windows-MCP and ROS-MCP sections.
  - Docs/Cache/session_memory_migration/01_round1_capture/round1_ros2_runtime_setup_memory_20260604.md
    records the ROS-MCP/rosbridge candidate route.
contradictions_or_history:
  ROS-MCP server capability is not proof that the current ROS2 runtime,
  rosbridge port, or robot graph is healthy.
current_evidence_needed:
  Round 2 should inspect current wrapper/config files and current MCP list only
  if an infrastructure task requests it.
formal_target_if_promoted:
  Already likely represented in Docs/Workflows/debug_mcp.md and
  Docs/Workflows/ros2_runtime_setup.md.
next_round_action:
  Treat desktop clicks and ROS write/control operations as permission-sensitive
  and do not use them as memory-migration proof.
```

### CLI-DETAIL-MEM-009 - ROS-MCP Rosbridge Auto-Start Is Desired, But Live Status Is Not Assumed

```text
topic: ROS-MCP background rosbridge wrapper
round: 1
status: candidate
risk: medium
candidate_statement:
  The user did not want to manually keep a separate rosbridge terminal open.
  The intended reusable fix is a wrapper that auto-starts or reuses
  `rosbridge_websocket` on port `9090` when ROS-MCP is needed. Old launch
  output showing rosbridge and rosapi started is prior evidence only.
known_sources:
  - Visible conversation: user provided rosbridge launch output and asked for
    automatic background startup.
  - Docs/Workflows/debug_mcp.md describes ROS-MCP wrapper auto-start behavior.
  - Docs/Workflows/ros2_runtime_setup.md records ROS2/rosbridge routing.
contradictions_or_history:
  A prior rosbridge log does not prove port `9090` is currently listening.
current_evidence_needed:
  Round 2 should inspect `/home/linux/mcp-wrappers/ros_mcp.sh` only under an
  explicit infrastructure exception, or inspect project-local wrapper docs if
  present. Live port checks are current-state diagnostics, not historical
  memory promotion.
formal_target_if_promoted:
  Already likely represented in Docs/Workflows/debug_mcp.md.
next_round_action:
  Keep as cache unless the current formal wrapper doc is missing the auto-start
  intent.
```

### CLI-DETAIL-MEM-010 - `filesystem` MCP Startup Failure Is A Config Diagnostic, Not A Project Claim

```text
topic: MCP startup failure after Codex update
round: 1
status: candidate
risk: medium
candidate_statement:
  After updating Codex, the CLI showed `MCP client for filesystem failed to
  start` with an initialize-handshake closed error. This should be treated as a
  config/runtime diagnostic under the MCP debug workflow, not as evidence about
  MoSim technical state.
known_sources:
  - Visible conversation: failure appeared immediately after `npm install -g
    @openai/codex` and restart.
  - Docs/Workflows/debug_mcp.md is the formal MCP repair entry.
contradictions_or_history:
  The user stated the later App problem was configuration-related, not network.
  That may be true for that incident but must not be generalized without a
  current log/config check.
current_evidence_needed:
  Round 2 should inspect current `codex mcp list`, relevant config entries, and
  server command paths only if the user requests current MCP repair.
formal_target_if_promoted:
  Docs/Workflows/debug_mcp.md, only if a reusable root cause and fix are
  confirmed.
next_round_action:
  Do not infer current filesystem MCP health from this historical failure.
```

## Rejected Or Unsafe Direct Promotions

| Historical Item | Current Treatment |
|---|---|
| Assuming `/tokens` exists because the user wanted it | Rejected until a supported command/plugin route is verified. |
| Reporting a token total from memory alone | Rejected; must name the source counter and scope. |
| Editing external `.codex` state to make `/resume` nicer | Not authorized by this cache. |
| Treating lowercase cwd display as project relocation | Rejected. |
| Treating Windows App loopback and WSL proxy warnings as the same fix | Rejected; verify separately. |
| Treating a prior rosbridge launch log as current ROS-MCP health | Rejected. |
| Treating desktop-click MCP experiments as project evidence | Rejected. |

## Round 2 Checklist

```text
1. Re-read Docs/Workflows/debug_mcp.md sections for Codex App, Windows-MCP,
   ROS-MCP, proxy, loopback, and MCP startup.
2. Re-read Docs/Index/codex_app_session_research.md for session sync/resume
   policy.
3. Re-read Docs/Workflows/ros2_runtime_setup.md only for ROS-MCP/rosbridge
   implications.
4. If a current machine diagnostic is needed, ask for or rely on a fresh
   infrastructure task because live `.codex`, home-directory, registry, and
   process checks are outside normal project-local memory migration.
5. If formal docs already contain the correct command/route, mark the item
   `already_represented` in round 2 instead of duplicating it.
```
