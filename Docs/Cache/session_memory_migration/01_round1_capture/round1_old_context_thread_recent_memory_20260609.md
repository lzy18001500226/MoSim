# Round 1 Old Context Thread Recent Memory Cache

Date: 2026-06-09 CST

Scope: cache-only first pass for the old context-maintenance thread
`019e3dac-de0e-7180-98ad-d7137e8a6275` (`MoSim｜Codex 上下文维护部-旧`).
This file is based only on Codex App `read_thread` recent turn summaries and
current project documents. It is not a raw transcript import and does not make
old chat content project truth.

## Status

```text
round: 1
topic: old context-maintenance thread recent summaries
status: candidate_cache_created
risk: medium_high
old_thread_id: 019e3dac-de0e-7180-98ad-d7137e8a6275
read_scope:
  - AGENTS.md
  - Docs/Workflows/new_conversation_context.md
  - Docs/Workflows/session_memory_migration.md
  - Docs/Index/project_work_memory_index.md
  - Docs/Workflows/mainline_operations_board.md
  - PROGRESS.md latest tail
  - CoAgent/dispatch/department_threads.json
  - Codex App read_thread recent two pages, outputs excluded
write_scope:
  - Docs/Cache/session_memory_migration/01_round1_capture/
  - Results/agent_packets/returns/
formal_docs_patched_this_round: none
cache_only: true
```

## Already Documented Sources

```text
old_thread_replacement:
  current_source:
    - CoAgent/dispatch/department_threads.json
  summary:
    - The current documentation-secretary/context-maintenance route is
      `MoSim｜文档秘书部` (`019e9be0-f6ac-7762-b80c-b1dd18b0d013`).
    - The old thread `019e3dac-de0e-7180-98ad-d7137e8a6275` is listed as
      superseded history.

existing_migration_coverage:
  current_sources:
    - Docs/Workflows/new_conversation_context.md
    - Docs/Workflows/session_memory_migration.md
    - Docs/Index/project_work_memory_index.md
    - Docs/Cache/session_memory_migration/00_index/coverage_matrix_20260604.md
    - Docs/Cache/session_memory_migration/00_index/completion_audit_20260604.md
    - Docs/Cache/session_memory_migration/03_round3_disposition/round3_promotion_rejection_map_20260604.md
  summary:
    - The 2026-06-04 identified topic set has round-1, round-2, and round-3
      dispositions.
    - Newly surfaced old-thread claims still must start at round 1.

coagent_ops_dispatch_boundary:
  current_sources:
    - Docs/Workflows/coagent_ops_patrol_workflow.md
    - CoAgent/dispatch/communication_contract.md
    - Docs/Workflows/mainline_operations_board.md
  summary:
    - Recent old-thread discussion about bounded CoAgentOps dispatch versus
      `dispatch_needed` is already represented in current operating docs.

dispatch_surface_failure_boundary:
  current_sources:
    - CoAgent/dispatch/communication_contract.md
    - Docs/Workflows/mainline_operations_board.md
    - PROGRESS.md latest entries
  summary:
    - Current docs already distinguish native send/read evidence from a real
      visible turn, expected packet, blocker packet, approval/provider surface,
      or dispatch-surface failure.
```

## Candidate Items

### OLDCTX-RECENT-001 - Dispatch Efficiency Needs Operational Metrics

```text
round: 1
status: candidate
risk: medium
candidate_statement:
  Old-thread recent discussion proposed measuring dispatch efficiency with
  `p0_idle_ready_minutes`, `return_to_next_dispatch_minutes`,
  `auto_dispatch_hit_rate`, and `blocked_by_pmo_decision_count`, mainly to
  reduce PMO wait time rather than to add dashboard-only metrics.
known_sources:
  - Codex App read_thread summary page for old thread around turns
    `019eaa06-0eeb-7af1-b6af-a7ffc3b71216` and
    `019ea835-29a2-7852-b54c-f5929fce688d`.
  - Current mainline board states and CoAgentOps bounded-dispatch docs.
contradictions_or_history:
  Metrics are advisory. They do not authorize CoAgentOps to bypass PMO product
  authority, live gates, manual review, or user decisions.
current_evidence_needed:
  Round 2 should re-read current dispatch tickets, board rows, and return/
  blocker packets to see whether these metrics can be computed from durable
  evidence without adding new workflow burden.
formal_target_if_promoted:
  Docs/Workflows/mainline_operations_board.md or a narrow PMO/CoAgentOps
  metrics note only after round 3.
next_round_action:
  Verify against current `Results/agent_packets/dispatch_tickets/` schema and
  recent return/blocker packets.
```

### OLDCTX-RECENT-002 - Work-Conserving Ready Queue Is A Candidate Pattern

```text
round: 1
status: candidate
risk: medium_high
candidate_statement:
  Old-thread recent discussion suggested a work-conserving ready queue where
  low-risk pre-authorized P0 tasks can be auto-dispatched by CoAgentOps when a
  routable active-visible thread is idle, while high-risk/live/manual decisions
  still escalate to PMO.
known_sources:
  - Codex App read_thread summary page for old-thread dispatch-efficiency
    discussion.
  - Current bounded-dispatch wording in CoAgentOps workflow and communication
    contract.
contradictions_or_history:
  The current board has P0 partition states and SLO rows, but no formal
  `Ready Queue` section was verified in this round. Do not infer that a queue
  is already implemented.
current_evidence_needed:
  Round 2 should check whether a current board or packet already implements
  ready-queue fields such as `auto_dispatchable`, resource locks,
  dependencies, acceptance gates, and next candidates.
formal_target_if_promoted:
  Docs/Workflows/mainline_operations_board.md and
  CoAgent/dispatch/communication_contract.md, but only after round 3 and PMO
  acceptance.
next_round_action:
  Treat as a planning candidate, not current project truth.
```

### OLDCTX-RECENT-003 - `Error Submitting Message` Should Be A Dead-Thread Signal Candidate

```text
round: 1
status: candidate
risk: medium
candidate_statement:
  Old-thread recent review identified user-visible `Error submitting message`
  as a candidate first-class dispatch-surface failure signal, distinct from a
  thread merely showing `thinking`.
known_sources:
  - Codex App read_thread summary page around old-thread turn
    `019eaa79-c17f-79e1-b61e-dd46a7803cae`.
  - Current communication contract already requires meaningful readback,
    expected packet, blocker packet, approval/provider surface, or
    dispatch-surface failure classification.
contradictions_or_history:
  A screenshot or UI label alone does not prove durable dead-thread state.
  It must be tied to native send/read evidence or expected packet absence.
current_evidence_needed:
  Round 2 should re-read current `communication_contract.md`,
  `coagent_ops_patrol_workflow.md`, and any dispatch-surface blocker packets
  before deciding whether a formal wording patch is still missing.
formal_target_if_promoted:
  CoAgent/dispatch/communication_contract.md or
  Docs/Workflows/coagent_ops_patrol_workflow.md.
next_round_action:
  Verify whether current docs already cover this enough through
  `dispatch_surface_failure_suspected`.
```

### OLDCTX-RECENT-004 - Hook Fix Was Accepted But MWORKS Window-Close Boundary Needs Review

```text
round: 1
status: candidate
risk: high
candidate_statement:
  Old-thread recent audit found the hook false-positive repair direction
  acceptable, but flagged `Scripts/tools/manage_mworks_windows.ps1`
  `CloseSafeErrors/Cleanup` as potentially conflicting with the MWORKS GUI
  rule that error/report/login/license/unknown windows must not be closed
  without PMO/user authorization.
known_sources:
  - Codex App read_thread summary page around old-thread turn
    `019ea833-fbfe-7253-aa63-e30b299db597`.
  - AGENTS.md MWORKS GUI/license/error boundary.
  - Current project files should be re-read before any formal conclusion.
contradictions_or_history:
  The old-thread audit summary is not proof that the script currently remains
  risky. The file may have changed after that audit, and the use mode may be
  manual-only or already gated.
current_evidence_needed:
  Round 2 must re-read `Scripts/tools/manage_mworks_windows.ps1`, preflight
  policy, current tests, AGENTS MWORKS boundary, and any supersede/clarification
  packet before judging this item.
formal_target_if_promoted:
  Possibly CoAgentOps patrol workflow, preflight policy, or a blocker/request
  packet, not a design doc.
next_round_action:
  Treat as high-risk cache-only candidate until current file evidence is
  checked.
```

### OLDCTX-RECENT-005 - Return Packet Git Narrative May Need Clarification

```text
round: 1
status: candidate
risk: medium
candidate_statement:
  Old-thread recent audit said a return packet claimed no commit/push while a
  nearby commit apparently contained the audited hook/MWORKS-window changes.
  This may require a supersede or clarification packet if no later packet
  already resolved it.
known_sources:
  - Codex App read_thread summary page around old-thread turn
    `019ea833-fbfe-7253-aa63-e30b299db597`.
contradictions_or_history:
  Git history and packets were not re-read in this round. The issue may already
  be superseded, accepted, or irrelevant to current mainline.
current_evidence_needed:
  Round 2 should re-read the named return packet, nearby Git commit metadata,
  and current board/ledger entries before taking any action.
formal_target_if_promoted:
  A clarification/supersede packet under `Results/agent_packets/`, not formal
  docs, unless a reusable audit rule is missing.
next_round_action:
  Verify or reject as stale.
```

## Chat-Only Candidates

The following remain chat-only or summary-only until round 2 evidence is
checked:

```text
chat_only_candidates:
  - OLDCTX-RECENT-001 dispatch efficiency metric set
  - OLDCTX-RECENT-002 work-conserving ready queue shape
  - OLDCTX-RECENT-003 explicit `Error submitting message` classification
  - OLDCTX-RECENT-004 MWORKS window close authorization risk
  - OLDCTX-RECENT-005 return-packet Git narrative inconsistency
```

## Round 2 Backlog

1. Re-read current dispatch ticket schema and recent dispatch tickets before
   judging metrics/ready-queue feasibility.
2. Re-read current CoAgentOps patrol workflow and communication contract before
   deciding whether `Error submitting message` needs a formal patch.
3. Re-read `Scripts/tools/manage_mworks_windows.ps1`, hook preflight tests, and
   any follow-up packets before acting on the MWORKS close-boundary candidate.
4. Re-read the cited return packet and Git commit metadata before writing any
   clarification packet.
5. Keep all formal promotion forbidden until round 3 final wording and evidence
   recheck are complete.
