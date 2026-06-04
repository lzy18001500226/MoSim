# Round 3 CLI/App Infrastructure Detail Disposition

Date: 2026-06-04 CST

Scope: round-3 disposition for post-closeout CLI/App infrastructure detail
memory captured in:

```text
Docs/Cache/session_memory_migration/round1_cli_app_infrastructure_detail_memory_20260604.md
Docs/Cache/session_memory_migration/round2_cli_app_infrastructure_detail_memory_20260604.md
```

This file is cache-only. No formal project document was patched in this round
because the only plausible formal additions require live current evidence or an
explicit infrastructure task. This round intentionally prevents chat-only CLI
UX memories from becoming project claims.

## Status

```text
round: 3
topic: Codex CLI/App token, resume, proxy, and MCP detail memory
status: round3_disposition_complete_no_formal_patch
formal_docs_patched_this_round: none
reason_no_formal_patch:
  - existing formal docs already represent CheckNetIsolation, Windows-MCP,
    ROS-MCP, and rosbridge auto-start boundaries
  - token totals, `/tokens`, resume defaults, WSL NAT proxy repair, and
    filesystem-MCP health require current live evidence or explicit
    infrastructure scope before formal wording
```

## Evidence Re-Read In This Round

| Source | Round-3 Use |
|---|---|
| `Docs/Cache/session_memory_migration/round1_cli_app_infrastructure_detail_memory_20260604.md` | Candidate list and anti-pollution constraints. |
| `Docs/Cache/session_memory_migration/round2_cli_app_infrastructure_detail_memory_20260604.md` | Project-local verification and item-level disposition. |
| `Docs/Workflows/debug_mcp.md` | Confirmed formal coverage for Codex App large-session risk, loopback syntax/moniker/SID fallback, Windows-MCP, ROS-MCP, and rosbridge auto-start. |
| `Docs/Index/codex_app_session_research.md` | Confirmed durable-state and stale-path resume boundaries. |
| `Docs/Workflows/ros2_runtime_setup.md` | Confirmed ROS2 Humble, rosbridge prior-state, and ROS-MCP auto-start boundaries. |

No external `.codex`, registry, PowerShell process, WSL proxy, ROS port, or
Codex CLI live command was inspected in this round.

## Final Disposition By Item

```text
CLI-DETAIL-MEM-001:
  item: `/status` is recognized in the observed CLI; `/tokens` was not.
  round3_disposition: cache_only_live_cli_check_required
  formal_patch: none
  reason:
    Current project docs cannot prove the installed CLI/plugin slash-command
    surface. Do not claim `/tokens` exists or cannot exist globally from chat
    memory alone.

CLI-DETAIL-MEM-002:
  item: total token accounting needs an authoritative source and scope.
  round3_disposition: cache_only_privacy_and_infra_request_gated
  formal_patch: none
  reason:
    Historic nearly-`1e9` token row is documented, but a current total would
    require reading external Codex state or current app/CLI counters under an
    explicit infrastructure request.

CLI-DETAIL-MEM-003:
  item: `codex resume -C <project> <thread-id>` was the reliable fallback.
  round3_disposition: cache_only_possible_future_formal_note
  formal_patch: none
  reason:
    The fallback is consistent with stale-path research, but formalizing it
    should wait for same-round current CLI help/behavior verification.

CLI-DETAIL-MEM-004:
  item: resume working-directory prompt and desire to default to current cwd.
  round3_disposition: cache_only_supported_config_unknown
  formal_patch: none
  reason:
    No project-local evidence proves a supported config or flag for the default
    selection.

CLI-DETAIL-MEM-005:
  item: lowercase WSL path display.
  round3_disposition: rejected_as_project_state
  formal_patch: none
  reason:
    Treat as UI/path-normalization behavior unless a reproducible filesystem or
    tooling bug appears. It is not evidence of a project move or rename.

CLI-DETAIL-MEM-006:
  item: WSL localhost proxy warning with user-observed port 7897.
  round3_disposition: cache_only_live_infra_request_gated
  formal_patch: none
  reason:
    The likely host-IP proxy route requires live WSL network/proxy checks and
    possibly shell-profile changes outside normal project-local memory
    migration. Windows AppContainer loopback is already documented separately.

CLI-DETAIL-MEM-007:
  item: CheckNetIsolation PowerShell/cmd syntax and lower-case AppContainer
        moniker.
  round3_disposition: already_represented_no_patch
  formal_patch: none
  reason:
    `Docs/Workflows/debug_mcp.md` already carries the correct PowerShell,
    `cmd`, moniker, and SID fallback wording.

CLI-DETAIL-MEM-008:
  item: Windows-MCP and ROS-MCP capability/security boundaries.
  round3_disposition: already_represented_no_patch
  formal_patch: none
  reason:
    `Docs/Workflows/debug_mcp.md` already captures Windows-native desktop
    automation, security cautions, ROS-MCP via rosbridge, and robot-control
    approval gating.

CLI-DETAIL-MEM-009:
  item: ROS-MCP rosbridge auto-start intent.
  round3_disposition: already_represented_no_patch
  formal_patch: none
  reason:
    Both `debug_mcp.md` and `ros2_runtime_setup.md` already document wrapper
    auto-start/reuse and prior-state-not-current-state boundaries.

CLI-DETAIL-MEM-010:
  item: historical filesystem MCP startup failure after Codex update.
  round3_disposition: cache_only_live_mcp_repair_gated
  formal_patch: none
  reason:
    No reusable root cause was verified from project-local docs. A future live
    MCP repair task should run current `codex mcp list`/config checks before
    promoting any fix.
```

## Round-3 Outcome

```text
completed_without_formal_patch:
  - all 10 CLI/App detail items have round-3 dispositions

already_represented:
  - CheckNetIsolation syntax/moniker/SID route
  - Windows-MCP desktop automation boundary
  - ROS-MCP rosbridge and ROS2 Humble boundary
  - rosbridge auto-start/reuse intent

cache_only_or_live_check_gated:
  - `/tokens` shortcut behavior
  - total-token accounting
  - explicit resume fallback
  - resume directory default behavior
  - WSL NAT localhost proxy repair
  - filesystem MCP startup failure

rejected_as_project_state:
  - lowercase path display as project move/rename evidence
```

## Future Promotion Rule

If the user later asks to act on these details:

```text
1. Treat it as a fresh infrastructure task, not as automatic memory promotion.
2. Re-read the target formal doc in the same round.
3. Gather current live evidence only for the explicitly requested surface.
4. Patch narrowly or keep cache-only.
```

Do not edit external `.codex` state, Windows registry, shell profiles, or ROS
runtime state from this cache alone.
