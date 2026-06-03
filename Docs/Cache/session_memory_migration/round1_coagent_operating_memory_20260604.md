# Round 1 CoAgent Operating Memory Cache

Date: 2026-06-04 CST

Scope: first cache pass for long-session memory about CoAgent operating
boundaries, current approval gates, visible department/thread history, transport
lessons, review/status/recovery surfaces, and gated future work. This is
cache-only. It does not approve new CoAgent implementation, runtime/schema
changes, transport expansion, automation expansion, or MCP/tool expansion.

## Status

```text
round: 1
topic: CoAgent operating history and gated scope
status: candidate_cache_created
risk: medium_high
formal_docs_patched_this_round: none
cache_only: true
source_pointers_re_read:
  - CoAgent/STATUS.md
  - CoAgent/README.md
  - CoAgent/docs/decisions/coagent_design_decision_record.md
  - Docs/Workflows/agent_orchestration.md
  - Docs/Workflows/agent_task_ledger.md
  - PROGRESS.md
```

This cache is not a CoAgent work authorization. The current task is session
memory migration only. Any future task that touches `CoAgent/` runtime,
transport, automation, task-state schema, task/result packet schema, permanent
department conversation design, or tool/MCP surfaces must first re-read
`CoAgent/STATUS.md` and the current design/approval gate.

## Candidate Items

### COAGENT-MEM-001 - Current CoAgent Direction Must Come From Docs, Not Old
Chat

```text
round: 1
status: candidate
risk: medium
candidate_statement:
  A new conversation must recover CoAgent direction from `CoAgent/STATUS.md`,
  `CoAgent/README.md`, decision records, and ledgers, not from old chat memory
  alone.
known_sources:
  - `CoAgent/README.md` says do not infer current CoAgent direction from old
    chat history alone.
  - `CoAgent/STATUS.md` records current gate and completed/superseded tasks.
  - `AGENTS.md` requires reading `CoAgent/STATUS.md` before changing CoAgent
    runtime/transport/automation/schema/departments/tool surfaces.
contradictions_or_history:
  Long-session history contains many design passes, visible-thread repairs,
  and old department layouts. Some are superseded or design-only.
current_evidence_needed:
  Round 2 should re-read the current status and decision records before any
  formal summary or implementation plan.
formal_target_if_promoted:
  Already represented in `CoAgent/README.md` and `AGENTS.md`.
next_round_action:
  Mark as already formalized unless recovery docs lack a pointer.
```

### COAGENT-MEM-002 - Current Approved Work Is Narrow And Project-Local

```text
round: 1
status: candidate
risk: high
candidate_statement:
  Current CoAgent approval is narrow: project-local transport, Git integration,
  task/result, review, notification-packet, checkpoint, status, evidence, and
  recovery work may continue only inside the approved task gate. App-server
  transport, unattended automation, new permanent departments, broad hook
  rewrites, tool/MCP expansion, external credentials/configuration,
  destructive reference cleanup, routine external notifications, and durable
  internal agent swarms remain gated.
known_sources:
  - `CoAgent/README.md` current gate.
  - `CoAgent/STATUS.md` current review gate for
    `COAGENT-IMPL-TRANSPORT-GIT-6H-20260531`.
  - `CoAgent/docs/decisions/coagent_design_decision_record.md` original
    implementation gate.
contradictions_or_history:
  Earlier design docs mention app-server transport, automation, permanent
  departments, and broad tool health. Many of those are design-only or future
  backlog, not approved live work.
current_evidence_needed:
  Round 2 should verify current `CoAgent/STATUS.md` before any new CoAgent
  implementation or formal claim.
formal_target_if_promoted:
  Already represented in `CoAgent/README.md`, `CoAgent/STATUS.md`, and
  `AGENTS.md`.
next_round_action:
  Keep as high-priority guardrail in round-3 map.
```

### COAGENT-MEM-003 - Old Architecture Long-Run Was Superseded Or Design-Only

```text
round: 1
status: candidate
risk: medium
candidate_statement:
  CoAgent architecture long-run tasks generated useful design documents and
  checker specs, but design-only tasks did not approve runtime mutation,
  dispatch, MCP/tool calls, notification sending, Git staging, or automatic
  document edits.
known_sources:
  - `CoAgent/STATUS.md` marks `COAGENT-ARCH-LONGRUN-01` as cancelled after the
    user redirected to approved implementation work.
  - `PROGRESS.md` repeatedly labels architecture/checker documents as
    design-only.
  - `CoAgent/docs/decisions/coagent_design_decision_record.md` keeps
    implementation gated to accepted backlog slices.
contradictions_or_history:
  The design material is extensive and can look like implementation approval.
  It is not by itself approval.
current_evidence_needed:
  Round 2 should identify which design docs are still current versus archived
  before promoting any operating rule.
formal_target_if_promoted:
  Already represented in CoAgent status/decision docs.
next_round_action:
  Preserve as rejected/superseded-history guard.
```

### COAGENT-MEM-004 - Visible Department Communication Had Metadata Drift

```text
round: 1
status: candidate
risk: medium_high
candidate_statement:
  CoAgent visible department communication is fragile: local-only packet
  transport under shadow Codex homes cannot be described as front-end-visible
  communication, and visible thread metadata drift has recurred across WSL and
  Windows Codex stores.
known_sources:
  - `CoAgent/STATUS.md` current correction: DevOps dispatch used shadow Codex
    homes, so project-local packets/logs existed but the real front-end stores
    were not updated.
  - `CoAgent/STATUS.md` visibility metadata notes about repeated
    `sync-visible --apply` repairs and `check_department_visibility.py`.
  - `PROGRESS.md` active queue and visibility repair history.
contradictions_or_history:
  A successful local result packet does not mean the user can see a department
  conversation update in Codex App/VSCode/CLI.
current_evidence_needed:
  Round 2 should re-read current visible-thread SOP and only inspect external
  Codex state if the user explicitly requests infrastructure repair.
formal_target_if_promoted:
  Existing CoAgent status/SOP and debug workflows.
next_round_action:
  Keep as infrastructure/recovery memory, not normal project truth.
```

### COAGENT-MEM-005 - Runtime State Beats Chat For Task Control

```text
round: 1
status: candidate
risk: medium
candidate_statement:
  Durable CoAgent task cancellation, review, closeout, and resume decisions
  must use CoAgent runtime state, result packets, status/export bundles, and
  closeout artifacts. Chat-only memory and Codex goal UI state are not the
  internal task-control plane.
known_sources:
  - `CoAgent/STATUS.md` task cancellation boundary.
  - `CoAgent/README.md` status/export/task-health/evidence/review-package
    commands.
  - `Docs/Workflows/agent_orchestration.md` queue/WAL recovery rules.
contradictions_or_history:
  Old attempts to clear or edit Codex goals are visible-thread recovery only
  and do not automatically cancel CoAgent runtime tasks.
current_evidence_needed:
  Round 2 should re-read current task runtime docs before any task-state
  answer.
formal_target_if_promoted:
  Already represented in CoAgent docs and orchestration workflow.
next_round_action:
  Cross-link with session-memory migration if a future recovery doc needs it.
```

### COAGENT-MEM-006 - WeChat Gateway Is Narrow And Gated

```text
round: 1
status: candidate
risk: medium
candidate_statement:
  CoAgent WeChat integration is a narrow gateway adapter for sparse progress,
  blocker, and review notifications. Real sending is explicit; dry-run/local
  artifacts are the default for routine checks.
known_sources:
  - `CoAgent/STATUS.md` says `cc_connect_weixin.py` is the narrow approved
    adapter, defaults to dry-run, and records redacted audits under ignored
    `Results/coagent_gateway/`.
  - `AGENTS.md` WeChat Progress and Intervention Rule.
  - Infrastructure round-2 cache already records WeChat as progress/intervention
    only, not proof.
contradictions_or_history:
  A successful WeChat send does not prove a simulation/controller/scene claim.
  A failed WeChat send should not be retried in a tight loop.
current_evidence_needed:
  Round 2 should verify current adapter behavior before any live notification
  workflow change.
formal_target_if_promoted:
  Already represented in `AGENTS.md`, CoAgent status, and infrastructure cache.
next_round_action:
  Likely already formalized.
```

### COAGENT-MEM-007 - Git Split Work Is A Separate DevOps Lane

```text
round: 1
status: candidate
risk: medium_high
candidate_statement:
  Broad Git split/ignore-drain work is a separate DevOps/GitIntegrator lane.
  The main agent owns scope and review; path-limited, small-batch, evidence-
  backed Git work should not block core engineering or be merged with unrelated
  task work.
known_sources:
  - `AGENTS.md` Git automation and Git split rules.
  - `CoAgent/STATUS.md` Git split helper descriptions.
  - `Docs/Workflows/agent_task_ledger.md` many Git split/drain rows.
contradictions_or_history:
  Visible-untracked count being zero is not sufficient completion; temporary
  ignore rules must be drained or justified.
current_evidence_needed:
  Round 2 should check current Git lane status before telling a future
  conversation to resume Git work.
formal_target_if_promoted:
  Already represented in `AGENTS.md` and task ledger.
next_round_action:
  Preserve as already formalized or cache-only recovery pointer.
```

## Rejected Or Superseded Historical Items

```text
REJ-COAGENT-001:
  Treating design-only CoAgent architecture documents as approval for runtime,
  transport, automation, MCP/tool, Git, or notification mutation is rejected.

REJ-COAGENT-002:
  Treating local-only shadow-home packet transport as visible department
  communication is rejected.

REJ-COAGENT-003:
  Treating Codex goal deletion/clearing as CoAgent runtime task cancellation is
  rejected.

REJ-COAGENT-004:
  Expanding app-server transport, unattended automation, new permanent
  departments, broad hooks, tool/MCP surface, or durable internal swarms
  without a current approved task is rejected.

REJ-COAGENT-005:
  Treating WeChat notifications as proof of project evidence is rejected.
```

## Round 2 Backlog

1. Re-read `CoAgent/STATUS.md`, `CoAgent/README.md`, and the current decision
   record before any formal CoAgent summary.
2. Check whether the current approved implementation task changed after this
   cache was written.
3. Verify whether active-visible department claims remain current through the
   documented checker only if the user requests CoAgent infrastructure review.
4. Classify old department-thread and architecture-design history as current,
   superseded, design-only, or gated.
5. Add only narrow round-3 map entries; do not use session-memory migration to
   authorize CoAgent implementation.

## Do Not Promote Yet

- Any new CoAgent implementation scope.
- Any current visible-thread health claim without re-running or re-reading the
  current checker output.
- Any routine live notification behavior beyond existing gated adapters.
- Any app-server, unattended automation, new permanent department, MCP/tool, or
  broad hook expansion.
