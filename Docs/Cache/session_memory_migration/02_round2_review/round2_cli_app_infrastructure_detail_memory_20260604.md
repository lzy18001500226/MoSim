# Round 2 CLI/App Infrastructure Detail Memory

Date: 2026-06-04 CST

Scope: project-local evidence review of
`round1_cli_app_infrastructure_detail_memory_20260604.md`.

This file is cache-only. It verifies candidate memories against current project
documents only. It does not inspect external `.codex` databases, home-directory
session files, Windows registry/AppContainer mappings, live ROS ports, or
current Codex process state.

## Status

```text
round: 2
topic: Codex CLI/App token, resume, proxy, and MCP detail memory
status: round2_verified_mixed
risk: medium
formal_docs_patched_this_round: none
source_boundary:
  - project-local docs and caches only
  - no external `.codex`, registry, process, or live network state inspected
next_required_round:
  round 3 may patch formal docs only after re-reading the target doc and any
  explicitly requested live evidence in the same round
```

## Sources Re-Read

| Source | Finding |
|---|---|
| `Docs/Cache/session_memory_migration/01_round1_capture/round1_cli_app_infrastructure_detail_memory_20260604.md` | New candidate items cover `/status`/`/tokens`, token totals, `codex resume -C`, resume cwd prompts, lowercase path display, WSL proxy, `CheckNetIsolation`, Windows-MCP, ROS-MCP, rosbridge auto-start, and filesystem MCP startup failure. |
| `Docs/Workflows/debug_mcp.md` | Already documents Codex App large-session/token row risk, localhost proxy, PowerShell and `cmd` loopback commands, lower-case AppContainer moniker, SID fallback, Windows-MCP install/security boundary, ROS-MCP rosbridge auto-start, and robot-control approval gating. |
| `Docs/Index/codex_app_session_research.md` | Already documents that live App/VSCode/CLI sync is not a reliable durable state source, stale-path resume can happen, and manual SQLite/JSONL handoff is emergency-only. |
| `Docs/Workflows/ros2_runtime_setup.md` | Already documents ROS2 Humble, prior 2026-06-01 apt/key/rosbridge state as non-current evidence, ROS-MCP through rosbridge, and wrapper auto-start behavior. |
| `Docs/Cache/session_memory_migration/02_round2_review/round2_infrastructure_memory_20260604.md` | Already verifies broad infrastructure lessons and says external `.codex` edits are not authorized by migration memory. |

## Round 2 Disposition By Item

### CLI-DETAIL-MEM-001 - `/status` Is Built-In, `/tokens` Is Not

```text
round: 2
status: round2_verified_for_cache_needs_current_cli_check
risk: medium
finding:
  The visible conversation is enough to preserve the memory that `/tokens` was
  rejected in that CLI session, but project-local docs do not prove the current
  installed CLI/plugin surface. No formal doc currently needs a `/tokens` claim.
contradictions_or_limits:
  Codex CLI/plugin behavior can change by version. A future current CLI may
  support a new shortcut, but this round did not inspect live help or plugin
  manifests.
round3_action:
  If the user asks again for a token shortcut, re-check current CLI/plugin help
  and any project-local session-tool scripts. Otherwise keep cache-only.
```

### CLI-DETAIL-MEM-002 - Token Totals Need An Authoritative Counter Source

```text
round: 2
status: round2_verified_for_cache_high_privacy_boundary
risk: medium
finding:
  `debug_mcp.md` already records a historical large-session App state row with
  nearly `1e9` tokens and a 1.96 GB session file. That supports the boundary
  that token totals must identify source and scope. It does not prove the
  current total.
contradictions_or_limits:
  Total-token counters may live in external Codex state under user home
  directories, which is outside normal project-local memory migration. Chat
  memory alone must not be used to report a total.
round3_action:
  Only add a formal diagnostic route if the user explicitly requests token
  accounting infrastructure and the current counter source is verified with
  privacy boundaries.
```

### CLI-DETAIL-MEM-003 - Explicit `codex resume -C` Fallback

```text
round: 2
status: round2_verified_for_cache
risk: medium
finding:
  `codex_app_session_research.md` documents stale-path resume failures and
  manual handoff risks. The explicit `codex resume -C <project> <thread-id>`
  memory is consistent with those findings and is useful as a fallback.
contradictions_or_limits:
  This round did not inspect current Codex CLI resume behavior or session index
  state. The fallback must not become an instruction to edit external session
  metadata automatically.
round3_action:
  A narrow formal note may be added to `debug_mcp.md` or a new-conversation
  handoff doc only after re-checking current CLI help and target wording.
```

### CLI-DETAIL-MEM-004 - Resume Directory Prompt

```text
round: 2
status: round2_verified_cache_only
risk: medium
finding:
  Current formal docs already warn about stale cwd/path values and missing
  working directory errors. The specific "choose session directory or current
  directory" prompt is a UI behavior memory that needs current CLI support
  verification before any formal workaround.
contradictions_or_limits:
  No project-local source proves a config key exists to default to current cwd.
round3_action:
  Keep cache-only unless a supported flag/config/alias is verified.
```

### CLI-DETAIL-MEM-005 - Lowercase Path Display

```text
round: 2
status: round2_verified_rejected_as_project_state
risk: low
finding:
  The lowercase `/mnt/c/users/hp/desktop/mosim` display should not be treated
  as a project relocation or file rename. Current project operations still use
  `/mnt/c/Users/HP/Desktop/MoSim`.
contradictions_or_limits:
  This does not diagnose Codex TUI path-normalization internals.
round3_action:
  No formal patch needed unless path casing causes a reproducible tooling bug.
```

### CLI-DETAIL-MEM-006 - WSL Localhost Proxy Warning

```text
round: 2
status: round2_verified_for_cache_needs_live_infra_check
risk: medium
finding:
  `debug_mcp.md` covers Windows Codex App localhost proxy/AppContainer loopback
  behavior. The WSL NAT warning and host-IP proxy environment route are related
  but distinct and not fully documented in current formal docs.
contradictions_or_limits:
  Current WSL network mode, proxy env vars, shell startup files, and Windows
  host IP were not inspected in this round because they are outside normal
  project-local memory migration.
round3_action:
  If the user asks for persistent WSL proxy repair, do a live infrastructure
  check and then add a narrow `debug_mcp.md` subsection. Otherwise keep
  cache-only.
```

### CLI-DETAIL-MEM-007 - `CheckNetIsolation` Syntax And Moniker

```text
round: 2
status: already_represented_in_formal_doc
risk: medium
finding:
  `debug_mcp.md` already contains the PowerShell `& "$env:SystemRoot..."`
  syntax, `cmd` `%SystemRoot%...` syntax, the lower-case
  `openai.codex_2p2nqsd0c76g0` moniker, and the mapped-SID fallback.
contradictions_or_limits:
  This round did not live-check the Windows registry mapping or exemption list.
round3_action:
  No formal patch needed unless the existing command becomes stale in a future
  live infrastructure task.
```

### CLI-DETAIL-MEM-008 - Windows-MCP And ROS-MCP Boundaries

```text
round: 2
status: already_represented_in_formal_doc
risk: medium
finding:
  `debug_mcp.md` already documents Windows-MCP as Windows-native desktop
  automation with security cautions, and ROS-MCP as rosbridge-backed,
  ROS-version-agnostic at checkout level, with active generation determined by
  the ROS runtime. `ros2_runtime_setup.md` states this host uses ROS2 Humble.
contradictions_or_limits:
  MCP presence or installation does not prove current server health.
round3_action:
  No formal patch needed unless a later live MCP repair finds a reusable config
  correction.
```

### CLI-DETAIL-MEM-009 - ROS-MCP Rosbridge Auto-Start

```text
round: 2
status: already_represented_in_formal_doc
risk: medium
finding:
  Both `debug_mcp.md` and `ros2_runtime_setup.md` document that the ROS-MCP WSL
  wrapper can auto-start `rosbridge_websocket` on port `9090` when absent and
  reuse it when present. They also state prior rosbridge status is not a
  current live-host guarantee.
contradictions_or_limits:
  This round did not probe port `9090` or current rosbridge process state.
round3_action:
  No formal patch needed unless the wrapper behavior changes.
```

### CLI-DETAIL-MEM-010 - Filesystem MCP Startup Failure

```text
round: 2
status: round2_verified_cache_only
risk: medium
finding:
  The historical `filesystem` MCP initialize-handshake failure after Codex
  update belongs under the MCP debug workflow, but current project-local docs
  do not identify a reusable root cause beyond general config/startup repair.
contradictions_or_limits:
  This round did not run `codex mcp list` or inspect current config because the
  objective is memory migration, not live infrastructure repair.
round3_action:
  Keep as cache-only unless a current MCP repair task reproduces the failure
  and confirms a durable fix.
```

## Round 2 Summary

```text
already_represented_in_formal_doc:
  - CLI-DETAIL-MEM-007
  - CLI-DETAIL-MEM-008
  - CLI-DETAIL-MEM-009

round2_verified_for_cache:
  - CLI-DETAIL-MEM-002
  - CLI-DETAIL-MEM-003

round2_verified_cache_only_or_needs_live_check:
  - CLI-DETAIL-MEM-001
  - CLI-DETAIL-MEM-004
  - CLI-DETAIL-MEM-006
  - CLI-DETAIL-MEM-010

rejected_as_project_state:
  - CLI-DETAIL-MEM-005
```

## Round 3 Candidates

Only two narrow formal changes are plausible, and neither should be made
without same-round current evidence:

```text
1. Add a `codex resume -C <project> <thread-id>` fallback note if current CLI
   help still supports the route and the target doc lacks a concise resume
   recovery note.
2. Add a WSL NAT localhost-proxy subsection if the user requests persistent
   proxy repair and live current-state checks confirm the host-IP route.
```

All other items are either already represented, cache-only, or rejected as
project state.
