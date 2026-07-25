# Docs Cache

This directory is the single project cache root. It stores reviewed but
non-startup material: migration notes, archived workflow bodies, research
drafts, session-memory promotion records, and runtime summary caches.

Do not put current operating rules here. Current rules belong in
`AGENTS.md`, `Docs/Workflows/`, `Docs/Skills/`, `Docs/Index/`, `Config/`, or
`Scripts/`.

## Layout

| Directory | Purpose |
|---|---|
| `agent_legacy/` | Legacy AgentOS, visible-thread, patrol, packet, and workflow migration material. |
| `cosim/` | Cached CoSim architecture drafts, source migration manifests, and audit notes. |
| `design/` | Cached design drafts, rebuild audits, absorbed/superseded architecture snapshots, and pre-rebuild material. |
| `design_intake/` | Reviewed design intake records before promotion into formal design docs. |
| `runtime_summaries/` | Small cached runtime summaries that are not authoritative result evidence. |
| `session_memory_migration/` | Reviewed memory/session promotion and rejection records. |
| `workflow_history/` | Superseded current-board bodies and one-off workflow snapshots retained for trace-back. |

## Rules

1. Keep the root mostly empty; put new cache files into the matching
   subdirectory.
2. Cache files are not routine startup context.
3. If a cached fact becomes a current rule, promote it into the owning
   workflow, skill, index, checker, or design document and leave the cache as
   history.
4. Do not store secrets, credentials, raw Codex session dumps, or large runtime
   artifacts here.
