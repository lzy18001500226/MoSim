# Round 2 CoAgent Operating Memory Audit

Date: 2026-06-04 CST

Scope: verify long-session memory about CoAgent operating boundaries, approved
scope, visible department history, shadow-home transport lessons, runtime
state, WeChat/notification limits, and design-only future work against current
project files. This is cache-only. It does not authorize CoAgent
implementation, runtime/schema changes, transport expansion, automation
expansion, department creation, or MCP/tool expansion.

## Status

```text
round: 2
topic: CoAgent operating history and gated scope
status: mixed_round2_verified_and_needs_round3
risk: medium_high
formal_docs_patched_this_round: none
cache_only: true
coagent_runtime_changed: false
```

This round read `CoAgent/STATUS.md` before making any CoAgent-related
classification, as required by the project rule. No CoAgent runtime, transport,
schema, task packet, hook, department registry, or tool surface was modified.

## Sources Re-Read

| Source | Finding |
|---|---|
| `CoAgent/STATUS.md` | Current status file records implementation long-run pending review, the transport/Git approved task, visible-thread repair history, recurring metadata drift, current active-visible conversations, and many design-only future items. |
| `CoAgent/README.md` | Start-here document says not to infer CoAgent direction from old chat, and records current gate around `COAGENT-IMPL-TRANSPORT-GIT-6H-20260531`. |
| `CoAgent/docs/decisions/coagent_design_decision_record.md` | CoAgent design is approved, but runtime, transport, automation, task-state schema migration, and tool expansion remain gated outside accepted backlog tasks. |
| `CoAgent/docs/status/codex_visible_thread_sop.md` | Visible communication requires real WSL Codex TUI / real visible thread state and user confirmation; shadow `CODEX_HOME` packet transport is not proof of user-visible communication. |
| `Docs/Workflows/agent_orchestration.md` | App-server transport and unattended write automation are not V1 defaults; visible thread dispatch must use real visible thread routes and durable ledger/packet evidence. |
| `Docs/Workflows/agent_task_ledger.md` | Current session-memory task is documentation/cache migration only; CoAgent implementation is a separate gated lane. |

## Round 2 Findings

### COAGENT-MEM-001 - Direction Comes From CoAgent Docs, Not Old Chat

```text
round: 2
status: round2_verified_for_cache
risk: medium
candidate_statement:
  A new conversation must recover CoAgent direction from `CoAgent/STATUS.md`,
  `CoAgent/README.md`, decision records, and ledgers, not from old chat memory.
current_evidence:
  - `CoAgent/README.md` explicitly says not to infer current CoAgent direction
    from old chat history alone.
  - `AGENTS.md` requires reading `CoAgent/STATUS.md` before changing CoAgent
    runtime/transport/automation/schema/departments/tool surfaces.
contradictions_or_history:
  Long-session chat contains many old architecture passes, visible-thread
  fixes, and proposed departments. They are not authoritative without current
  status/doc checks.
formal_target_if_promoted:
  Already represented in CoAgent README and AGENTS.
next_round_action:
  Round 3 can mark already formalized.
```

### COAGENT-MEM-002 - Current Approved Scope Is Narrow And Gated

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  Current CoAgent work remains bounded by approved project-local transport,
  Git integration, task/result/review/status/evidence/recovery scope. App-server
  transport, unattended automation, new permanent departments, broad hook
  rewrites, tool/MCP expansion, external credentials/configuration, destructive
  cleanup, and routine real notifications remain gated unless explicitly
  approved.
current_evidence:
  - `CoAgent/README.md` current gate records
    `COAGENT-IMPL-TRANSPORT-GIT-6H-20260531`.
  - `CoAgent/STATUS.md` current review gate repeats the same allowed scope and
    blocked expansions.
  - `coagent_design_decision_record.md` says runtime, transport, automation,
    task-state schema migration, and tool expansion remain gated outside the
    accepted task sequence.
contradictions_or_history:
  Some later sections of `CoAgent/STATUS.md` list completed tasks, design
  continuations, and future `COAGENT-IMPL-NEXT-*` ideas. Those are not blanket
  approval for this migration turn.
formal_target_if_promoted:
  Already represented in CoAgent README/STATUS and AGENTS.
next_round_action:
  Round 3 should map as a high-priority guardrail, not a new implementation
  task.
```

### COAGENT-MEM-003 - Design-Only History Must Stay Design-Only

```text
round: 2
status: round2_verified_for_cache
risk: medium_high
candidate_statement:
  CoAgent architecture/design documents and `COAGENT-IMPL-NEXT-*` designs do
  not approve runtime dispatch, transport, notifications, app-server, Git,
  tool/MCP calls, or schema mutation unless a current accepted implementation
  task exists.
current_evidence:
  - `CoAgent/STATUS.md` repeatedly labels future items such as external
    adoption store/checker, context index/checker, operating metrics,
    transport timeout hardening, mailbox, goal authority, retrospective, and
    tool-capability designs as design-only.
  - `CoAgent/STATUS.md` says further implementation must continue through the
    post-approval backlog and acceptance gates.
contradictions_or_history:
  Design text can look like current operating capability. This cache must
  preserve the boundary because old chat may overstate it.
formal_target_if_promoted:
  Existing CoAgent status/decision docs.
next_round_action:
  Round 3 should preserve in rejected/superseded-history bucket.
```

### COAGENT-MEM-004 - Visible Department Communication Is Fragile

```text
round: 2
status: round2_verified_for_cache_not_live_checked
risk: medium_high
candidate_statement:
  CoAgent visible department communication is not equivalent to local shadow
  packet transport. Visibility claims require real Codex-home state, sync, and
  current checker or user confirmation.
current_evidence:
  - `CoAgent/STATUS.md` records the 2026-05-31 correction: DevOps dispatch used
    shadow Codex homes, so project packets/logs existed but real front-end
    stores were not updated.
  - `CoAgent/docs/status/codex_visible_thread_sop.md` says `codex_exec_resume`
    through a shadow `CODEX_HOME` proves result packets, not front-end-visible
    communication.
  - `CoAgent/STATUS.md` records recurring WSL alternate DB metadata drift and
    `sync-visible --apply` repairs.
contradictions_or_history:
  `CoAgent/STATUS.md` also says MainAgent and 10 department conversations are
  `active_visible`, but this round did not run
  `check_department_visibility.py`. Therefore this cache cannot claim current
  live visibility health.
formal_target_if_promoted:
  Existing visible-thread SOP and CoAgent status.
next_round_action:
  Round 3 can mark historical lesson formalized; any live visibility claim
  needs a current checker run in an infrastructure task.
```

### COAGENT-MEM-005 - Runtime State, Packets, And Closeouts Beat Chat

```text
round: 2
status: round2_verified_for_cache
risk: medium
candidate_statement:
  Durable CoAgent task state, review closeouts, result packets, status/export
  bundles, task-health, and evidence manifests are the task-control plane.
  Chat-only memory and Codex goal UI state are not enough to cancel, close, or
  resume CoAgent work.
current_evidence:
  - `CoAgent/STATUS.md` lists status export, resume bundle, task health,
    blocker packet, review queue, closeout, and closeout verification surfaces.
  - `CoAgent/README.md` documents status/export/task-health/evidence/review
    commands.
  - `Docs/Workflows/agent_orchestration.md` says Codex thread goals are display
    and recovery metadata, not the internal task-state source of truth.
contradictions_or_history:
  Long-session attempts to repair/delete Codex goals are visible-thread
  recovery only, not CoAgent runtime task control.
formal_target_if_promoted:
  Already represented in CoAgent docs and orchestration workflow.
next_round_action:
  Round 3 can mark already formalized.
```

### COAGENT-MEM-006 - WeChat Gateway Is Narrow, Sparse, And Usually Dry-Run

```text
round: 2
status: round2_verified_for_cache
risk: medium
candidate_statement:
  CoAgent WeChat integration is a narrow gateway adapter for required human
  review or blocker notification. Routine progress/status/local checks should
  remain dry-run/local unless a blocker or manual-review item exists.
current_evidence:
  - `CoAgent/STATUS.md` says `cc_connect_weixin.py` is the narrow approved
    adapter, defaults to dry-run, and real send requires `--send`.
  - `CoAgent/STATUS.md` user authorization note limits real Weixin messages to
    required human review or blocker notification.
  - `AGENTS.md` says WeChat is sparse progress/intervention, not a proof
    channel.
contradictions_or_history:
  Successful WeChat sending does not prove simulations, controller evidence,
  scene review, or CoAgent task completion.
formal_target_if_promoted:
  Already represented in AGENTS and CoAgent status.
next_round_action:
  Round 3 can mark already formalized.
```

### COAGENT-MEM-007 - Git Split Is A Separate DevOps Lane

```text
round: 2
status: round2_verified_for_cache
risk: medium_high
candidate_statement:
  Broad Git split/ignore-drain work is a separate DevOps/GitIntegrator lane.
  It must stay path-limited, small-batch, and evidence-backed, and should not
  be mixed into unrelated engineering or memory-migration tasks.
current_evidence:
  - `AGENTS.md` Git split rules require split-aware path-limited Git work.
  - `CoAgent/STATUS.md` warns CoAgent commits should be split or delegated
    when Git is slow and not done as broad external reference-tree batches.
  - `Docs/Workflows/agent_task_ledger.md` has active Git split/drain rows
    separate from session-memory migration.
contradictions_or_history:
  Visible-untracked count zero or IDE hiding is not Git completion. This cache
  does not perform Git split work.
formal_target_if_promoted:
  Already represented in AGENTS and ledger.
next_round_action:
  Round 3 can keep as already formalized/cache guard.
```

### COAGENT-MEM-008 - Current Migration Does Not Approve CoAgent Implementation

```text
round: 2
status: round2_verified_for_cache
risk: high
candidate_statement:
  This session-memory migration task is only documenting history and evidence
  boundaries. It does not approve or perform CoAgent implementation.
current_evidence:
  - Current ledger row `SESSION-MEMORY-MIGRATION-20260604` is scoped to
    migration cache, workflow pointers, and round gates.
  - No CoAgent files were modified in this round.
contradictions_or_history:
  Reading CoAgent status during migration must not be interpreted as resuming
  CoAgent runtime work.
formal_target_if_promoted:
  This cache and the migration ledger row.
next_round_action:
  Round 3 should keep CoAgent operating lessons as guardrails only.
```

## Rejected Or Superseded Historical Items

| Historical Item | Current Treatment |
|---|---|
| Design-only CoAgent architecture docs as approval for runtime/transport/automation/tool changes | Rejected. |
| Local-only shadow-home packet transport as visible department communication | Rejected. |
| Codex goal deletion/clearing as CoAgent task cancellation | Rejected. |
| Expanding app-server transport, unattended automation, new permanent departments, broad hooks, tool/MCP surfaces, or durable internal swarms without an approved task | Rejected. |
| WeChat notification as evidence proof | Rejected. |
| Running live visibility/transport repair as part of session-memory migration | Rejected for this turn. |

## Round 3 Promotion Candidates

Only these narrow items are candidates for round 3:

1. A CoAgent recovery pointer:
   read `CoAgent/STATUS.md` and `CoAgent/README.md` before CoAgent changes.
2. A visible-transport caution:
   local shadow packets are not front-end-visible communication.
3. A scope gate reminder:
   app-server, automation, departments, broad hooks, MCP/tool expansion, and
   routine external notifications remain gated.

No CoAgent implementation, live visibility-health claim, transport expansion,
or runtime-state mutation is ready for promotion from this cache.

## Verification Needed Before Round 3

```text
1. Re-read `CoAgent/STATUS.md` and `CoAgent/README.md` in the same round.
2. If claiming current department visibility, run or read current
   `check_department_visibility.py` evidence; do not infer from old status.
3. If touching CoAgent implementation, open a separate approved task and obey
   the current gate.
4. Keep this migration cache separate from CoAgent runtime work.
```
