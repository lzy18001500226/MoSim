# Round 2 Codex Infrastructure Memory Audit

Date: 2026-06-04 CST

Scope: verify the long-session memory around Codex App/CLI/VSCode sessions,
MCP configuration, WeChat notifications, and Git hygiene. This is a cache-only
round 2 audit. It does not authorize external `.codex` database edits or other
infrastructure mutations.

## Status

```text
round: 2
topic: Codex / MCP / WeChat / Git operating memory
status: round2_verified_for_cache
risk: medium
formal_docs_patched_this_round: none
cache_only: true
```

## Sources Re-Read

| Source | Finding |
|---|---|
| `Docs/Index/codex_app_session_research.md` | App/VSCode/CLI live bidirectional session sync is not a safe durable dependency. Project docs and ledgers are the reliable state source. Manual SQLite/JSONL injection is emergency recovery only. |
| `Docs/Workflows/debug_mcp.md` | Contains the current Codex App/VSCode SQLite checksum repair, shared `CODEX_HOME` route, App hang diagnosis, loopback exemption commands, Windows-MCP and ROS-MCP setup notes, and session policy. |
| `AGENTS.md` | Project rule says Codex App is review/front-end, not durable task ledger; long/volatile work must be in TaskSecretary/ledger. It also records WeChat and Git split rules. |
| `PROGRESS.md` | Current focus records the 2026-06-03 Codex shared Windows state repair and App hang diagnosis. |
| `Docs/Workflows/agent_task_ledger.md` | Active DevOps rows show repository Git work must remain path-limited and split into reviewed batches; visible-untracked zero is not enough to finish ignore cleanup. |

## Round 2 Findings

### INFRA-MEM-001 - Durable State Is Project Docs, Not Live Session Sync

```text
round: 2
status: round2_verified_for_cache
risk: medium
candidate_statement:
  New Codex conversations must recover MoSim state from repository docs,
  ledgers, and cache files, not from assumed live sync between Codex App,
  VSCode, and CLI session stores.
current_evidence:
  - `Docs/Index/codex_app_session_research.md` says live bidirectional session
    sync is not a safe dependency and durable state must be project files.
  - `AGENTS.md` says Codex App is a review/front-end surface and not the
    durable task ledger.
  - This migration workflow now stores candidates under
    `Docs/Cache/session_memory_migration/`.
contradictions_or_history:
  Earlier user expectation was that shared session files would fully sync
  between VSCode and CLI/App. Observed behavior did not support relying on that
  for recovery.
formal_target_if_promoted:
  Already represented in `AGENTS.md`,
  `Docs/Index/codex_app_session_research.md`, and
  `Docs/Workflows/session_memory_migration.md`.
next_round_action:
  Round 3 can mark as already formalized; no new patch unless a shorter
  startup pointer is needed.
```

### INFRA-MEM-002 - Codex App/Windows Shared-State Repair Is Infrastructure History

```text
round: 2
status: round2_verified_for_cache
risk: medium
candidate_statement:
  The 2026-06-03 Windows Codex shared-home repair is documented as a reusable
  troubleshooting route, but it is infrastructure history. It must not be
  repeated automatically or treated as normal project engineering work.
current_evidence:
  - `Docs/Workflows/debug_mcp.md` section 4.1 documents the SQLx migration
    checksum mismatch, shared `CODEX_HOME`, backup-first checksum repair, and
    verification commands.
  - `PROGRESS.md` records the exact 2026-06-03 repair outcome.
contradictions_or_history:
  User preferred not to isolate Windows CLI into a separate `.codex-cli` home.
  That preference explains the shared-home route but does not authorize future
  external DB mutation without explicit infrastructure request.
formal_target_if_promoted:
  Already represented in `Docs/Workflows/debug_mcp.md`.
next_round_action:
  Round 3 should only verify that debug_mcp remains the single repair entry.
```

### INFRA-MEM-003 - Codex App Hang Is Multi-Cause

```text
round: 2
status: round2_verified_for_cache
risk: medium
candidate_statement:
  Codex App hangs are documented as multi-cause: huge active session files,
  AppContainer/localhost proxy behavior, startup plugin/skills/MCP/Computer Use
  probes, permission issues, and session-index pressure can all contribute.
current_evidence:
  - `Docs/Workflows/debug_mcp.md` section 4.2 lists observed hang causes and
    AppContainer loopback command syntax.
  - `PROGRESS.md` records app-server health after SQLite repair plus remaining
    startup probe risks and the about-1.96GB active MoSim session concern.
contradictions_or_history:
  Earlier theory that the issue was simply WSL versus Windows is superseded.
formal_target_if_promoted:
  Already represented in `Docs/Workflows/debug_mcp.md`.
next_round_action:
  Round 3 should avoid broadening this into a guaranteed root-cause claim.
```

### INFRA-MEM-004 - WeChat Is Progress/Intervention, Not Proof

```text
round: 2
status: round2_verified_for_cache
risk: medium
candidate_statement:
  WeChat is the default out-of-band progress and intervention channel for
  long-running work when available, but WeChat sends are not simulation proof,
  task completion proof, or audit truth. Failed sends must be recorded and not
  retried in a tight loop.
current_evidence:
  - `AGENTS.md` WeChat progress rule.
  - `PROGRESS.md` records gateway recovery/failure notes.
contradictions_or_history:
  Long chat history contains WeChat success and failure episodes. Those are
  notification state, not evidence of engineering completion.
formal_target_if_promoted:
  Already represented in `AGENTS.md`.
next_round_action:
  Round 3 can mark as already formalized unless gateway workflow gaps appear.
```

### INFRA-MEM-005 - Git Must Remain Path-Scoped And Split-Aware

```text
round: 2
status: round2_verified_for_cache
risk: medium
candidate_statement:
  MoSim has large tracked/untracked surfaces and active split-Git work. Future
  migration or documentation tasks should use path-limited status/diff/checks,
  not broad full-tree operations; slow Git release work should go through
  GitIntegrator when needed.
current_evidence:
  - `AGENTS.md` Git automation rule says temporary large-tree ignores are only
    throttles, visible-untracked zero is not completion, and slow Git can be
    delegated to GitIntegrator.
  - `Docs/Workflows/agent_task_ledger.md` active DevOps rows show many
    path-limited reference-tree and `.gitignore` drain batches.
  - This migration attempted a broad `git status --short` and it timed out in
    60 seconds; path-limited checks are the practical route.
contradictions_or_history:
  Earlier broad Git operations and temporary ignore rules created slow/large
  surfaces. New sessions must not interpret a clean narrow probe as whole-repo
  completion.
formal_target_if_promoted:
  Already represented in `AGENTS.md` and DevOps ledger rows.
next_round_action:
  Round 3 can promote a migration-specific note only if new sessions keep
  running broad Git during memory extraction.
```

## Rejected Or Superseded Historical Items

| Historical Item | Current Treatment |
|---|---|
| Assuming Codex App, VSCode, and CLI live-sync all chat history reliably | Rejected as durable-state strategy. |
| Manual SQLite/JSONL session injection as normal thread creation | Rejected; emergency recovery only after backup. |
| Treating a Codex App hang as one root cause | Rejected; current docs list multiple independent causes. |
| Treating WeChat send success as proof of task completion | Rejected. |
| Using broad full-tree Git status/add as normal session-migration hygiene | Rejected for this large repo; use path-limited checks. |

## Round 3 Promotion Candidates

Most items are already formalized. Round 3 should only promote a small recovery
pointer if needed:

1. Start new conversations from `PROGRESS.md`,
   `Docs/Workflows/agent_task_ledger.md`, and
   `Docs/Cache/session_memory_migration/`, not from assumed App/CLI sync.
2. Use `Docs/Workflows/debug_mcp.md` as the single entry for Codex/MCP
   infrastructure repair.
3. Keep memory-migration Git checks path-limited.

No external Codex/App database operation is authorized by this cache.

## Verification Needed Before Round 3

```text
1. Re-read debug_mcp.md and codex_app_session_research.md before changing any
   Codex infrastructure document.
2. Do not inspect or modify external `.codex` state unless the user explicitly
   asks for infrastructure repair.
3. For Git, use path-limited status/diff/check commands for migration files.
4. If a new WeChat gateway failure happens, record it in the appropriate
   project result/progress file; do not rely on chat-only memory.
```
