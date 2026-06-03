# Round 1 Candidate Cache - MoSim Long Session Memory

Date: 2026-06-04 CST

Scope: first pass over the current visible conversation context plus current
project recovery docs. This is cache-only. Nothing in this file is promoted as
formal project truth unless it later passes round 2 and round 3 under
`Docs/Workflows/session_memory_migration.md`.

## Status

```text
round: 1
status: not_promoted
formal_docs_patched_this_round:
  - Docs/Workflows/session_memory_migration.md
cache_files:
  - Docs/Cache/session_memory_migration/round1_candidate_cache_20260604.md
next_required_round:
  round 2 source/evidence verification against current files and result artifacts
```

## Extraction Principles Used In This Round

- Current project files and result artifacts outrank old chat history.
- Historical values are preserved as candidates only when they help locate the
  final evidence.
- Numeric asset/model parameters and simulation claims are high risk.
- Rejected historical routes are important memory because they prevent a new
  conversation from repeating old mistakes.
- Codex/App/CLI infrastructure fixes are not normal project engineering facts;
  keep them in debug/recovery workflows.

## Candidate Items

### MEM-001 - Durable State Must Live In Repo Docs, Not Chat Sync

```text
topic: Codex session policy / project memory
round: 1
status: candidate
risk: medium
candidate_statement:
  For MoSim, chat/session sync is a convenience layer only. New conversations
  should recover from repository docs, ledgers, PROGRESS, and cache files, not
  from VSCode/App/CLI live transcript continuity.
known_sources:
  - AGENTS.md section 3.3.1 says do not rely on App/VSCode live session sync as durable task ledger.
  - Docs/Index/codex_app_session_research.md records WSL/App session behavior and current policy.
  - PROGRESS.md has repeated session-sync and Codex App repair notes.
contradictions_or_history:
  Earlier work explored App-visible department threads and manual SQLite/JSONL
  handoff. Manual App-local thread creation was rejected for normal use.
current_evidence_needed:
  Re-read Docs/Index/codex_app_session_research.md, AGENTS.md, and current
  session storage notes; confirm no newer doc changed the policy.
formal_target_if_promoted:
  Already appears mostly promoted in AGENTS.md and Docs/Index/codex_app_session_research.md.
next_round_action:
  Round 2 should verify wording and decide whether this cache item only points
  to existing docs rather than patching more formal docs.
```

### MEM-002 - Three-Round Gate For Long-Session Memory Migration

```text
topic: documentation anti-pollution
round: 1
status: candidate
risk: medium
candidate_statement:
  Historical conversation content must go through three rounds before entering
  formal MoSim docs: cache capture, evidence verification, then formal doc
  promotion with a diff/check gate.
known_sources:
  - User explicitly requested at least three iterations before formal docs.
  - Docs/Workflows/audit_external_repo.md already defines three-round learn-and-update expectations.
  - Docs/Workflows/agent_orchestration.md and agent_task_ledger.md define WAL/review recovery.
  - Docs/Workflows/session_memory_migration.md was added in this round.
contradictions_or_history:
  PROGRESS.md contains many old entries, some intentionally superseded; direct
  promotion from there can pollute current design docs.
current_evidence_needed:
  Round 2 docs-quality review should check that session_memory_migration.md
  does not conflict with existing TaskSecretary and audit workflows.
formal_target_if_promoted:
  Docs/Workflows/session_memory_migration.md, Docs/Index/workflow_index.md,
  Docs/Workflows/agent_task_ledger.md.
next_round_action:
  Add workflow-index and ledger pointers after reviewing for duplication and
  consistency.
```

### MEM-003 - Codex App / Windows CLI Shared-State Repair

```text
topic: Codex infrastructure / Windows App repair
round: 1
status: candidate
risk: medium
candidate_statement:
  The Windows Codex App/CLI shared-home route was repaired on 2026-06-03 by
  aligning the CLI runtime version and fixing SQLx migration checksums in
  `state_5.sqlite` after backup.
known_sources:
  - PROGRESS.md current focus.
  - Docs/Workflows/debug_mcp.md section on Windows Codex App runtime/state repair.
contradictions_or_history:
  Earlier isolation into `C:\Users\HP\.codex-cli` was discussed but rejected by
  the user because Windows CLI/App/VSCode should not be isolated.
current_evidence_needed:
  Round 2 should re-read debug_mcp.md and current PROGRESS. Do not re-open or
  mutate external Codex DBs unless the user asks for infrastructure repair.
formal_target_if_promoted:
  Already belongs in Docs/Workflows/debug_mcp.md; this cache should point there.
next_round_action:
  Verify whether no further formal patch is needed beyond a workflow-index
  pointer to session memory migration.
```

### MEM-004 - Codex App Hang Is Multi-Cause, Not Only WSL

```text
topic: Codex App troubleshooting
round: 1
status: candidate
risk: medium
candidate_statement:
  Codex App `未响应` hangs are likely a combination of huge active session
  files, packaged-App localhost/loopback behavior, startup probes, plugins/MCP,
  and residual plugin host processes; not simply WSL vs Windows.
known_sources:
  - PROGRESS.md current focus.
  - Docs/Workflows/debug_mcp.md section 4.2.
  - Current visible conversation around CheckNetIsolation commands.
contradictions_or_history:
  Earlier theories focused on WSL isolation. Later evidence showed Windows App
  can hang even after moving to Windows runtime and repairing SQLite.
current_evidence_needed:
  Round 2 should verify the latest debug_mcp.md commands and distinguish
  evidence from inference.
formal_target_if_promoted:
  Docs/Workflows/debug_mcp.md only.
next_round_action:
  Confirm the final CheckNetIsolation command uses `openai.codex_2p2nqsd0c76g0`
  or the mapped SID, and keep it out of design docs.
```

### MEM-005 - Active Long Goal: Session Memory Migration Itself

```text
topic: current long-running documentation task
round: 1
status: candidate
risk: low
candidate_statement:
  The user wants the long MoSim conversation fully translated into project-local
  memory so future new conversations can start safely without losing context.
known_sources:
  - Current user instruction on 2026-06-04.
  - Active Codex goal for this thread.
current_evidence_needed:
  Add or update a ledger row so the work survives another context refresh.
formal_target_if_promoted:
  Docs/Workflows/agent_task_ledger.md, PROGRESS.md, and cache files.
next_round_action:
  Add a long-running ledger row with current checkpoint and recovery instruction.
```

### MEM-006 - Sunray150 Geometry/Assembly Facts Are High-Risk

```text
topic: Sunray150 asset and assembly memory
round: 1
status: candidate
risk: high
candidate_statement:
  Sunray150 geometry and material state contains several accepted/rejected
  details, but only the latest evidence artifacts and manual review outcomes
  should be trusted. Historical parameter values must not be copied directly
  into formal docs.
known_sources:
  - PROGRESS.md current focus around Sunray150 DAE/MID-360/propeller/material review.
  - Results/unreal_scene_mapping/SUNRAY150_MID360_MATERIAL_AUDIT_PACKAGE_20260603.md
  - Results/unreal_scene_mapping/SUNRAY150_COMPONENT_MATERIAL_EVIDENCE_20260604.md
contradictions_or_history:
  User explicitly warned that many historical assembly parameters were wrong
  and only final parameters are valid. PROGRESS records rejected material
  candidates and rejected manual propeller tuning.
current_evidence_needed:
  Round 2 must re-read the latest Sunray result manifests, source asset scripts,
  and any manual-review packets before stating final geometry/material facts.
formal_target_if_promoted:
  Relevant UE/asset workflow docs or a dedicated Sunray evidence document,
  not this cache.
next_round_action:
  Create a separate high-risk round-2 Sunray evidence audit item. Do not promote
  `MID-360 uniform_scale`, propeller Z, material acceptance, or final asset
  source chain until current files prove them.
```

### MEM-007 - UE/ROS2/FAST-LIO Route Had Rejected Toy-Mapping History

```text
topic: UAV simulation architecture correction
round: 1
status: candidate
risk: high
candidate_statement:
  The project moved away from keyboard/grid-step/static-point-cloud/2D-only
  mapping demos toward a Factory-first continuous UAV stack with MWORKS state,
  ROS2 LiDAR/IMU/TF, RViz2 windows, and real FAST-LIO/planner evidence.
known_sources:
  - Docs/Workflows/agent_task_ledger.md active rows for UE-UAV architecture.
  - Docs/Design/09_UE_ROS_MWORKS无人机仿真架构重构.md.
  - PROGRESS.md entries around 2026-06-01 and 2026-06-02.
contradictions_or_history:
  Many earlier generated maps, HTML point clouds, and keyboard loops are
  explicitly smoke-only or rejected. Do not revive them as product evidence.
current_evidence_needed:
  Round 2 should re-read the active architecture design and ledger rows, then
  separate accepted direction from unproven implementation claims.
formal_target_if_promoted:
  Existing architecture/design docs and unreal_renderer workflow if a gap is found.
next_round_action:
  Verify current active state, especially FAST-LIO runtime status and which
  claims are still blocked.
```

### MEM-008 - MWORKS Evidence Boundary Is Non-Negotiable

```text
topic: simulation evidence classification
round: 1
status: candidate
risk: high
candidate_statement:
  MWORKS/Sysplorer simulation evidence must be separated from offline scripts;
  formal controller claims need MWORKS/MCP or explicit manual MWORKS evidence
  and, for controllers, behavior-equivalent graphical Sysblock models.
known_sources:
  - AGENTS.md section 3.6 Simulation Evidence Rule.
  - Docs/Workflows/produce_simulation_evidence.md and run_simulation.md.
contradictions_or_history:
  Some early demo outputs may have been offline or smoke-only. They must not be
  reinterpreted as formal MWORKS evidence in a new conversation.
current_evidence_needed:
  Round 2 should check whether current report/user manual clearly enforces
  source labels and graphical Sysblock counterpart requirements.
formal_target_if_promoted:
  Probably already promoted in AGENTS.md and workflows; cache may only point.
next_round_action:
  Verify no formal doc still labels offline generated artifacts as MWORKS evidence.
```

### MEM-009 - WeChat Gateway Is Progress Channel, Not Proof Channel

```text
topic: WeChat notification / CoAgent gateway
round: 1
status: candidate
risk: medium
candidate_statement:
  WeChat milestone notifications are useful for long-running progress and
  intervention, but failures must be diagnosed and recorded locally; WeChat
  sends are not simulation proof or task completion proof.
known_sources:
  - AGENTS.md section 3.2.1.
  - PROGRESS.md WeChat gateway recovery notes.
contradictions_or_history:
  Several sends failed with `no active session found` or `ret=-2`; repeated
  retry loops are forbidden.
current_evidence_needed:
  Round 2 should verify the current adapter path and latest failure/success
  policy if this is promoted.
formal_target_if_promoted:
  Already in AGENTS.md; detailed recovery in relevant workflow/gateway docs.
next_round_action:
  Keep as context pointer unless a later cache extraction finds a missing route.
```

### MEM-010 - Git Work Must Stay Small-Batch And Path-Scoped

```text
topic: Git hygiene / huge repo recovery
round: 1
status: candidate
risk: medium
candidate_statement:
  MoSim's repository is large and has active split-Git work; future changes
  should avoid full-tree Git scans/adds and use path-limited, small reviewed
  batches, delegating slow Git to GitIntegrator when needed.
known_sources:
  - AGENTS.md Git automation and parallel-agent rules.
  - Docs/Workflows/agent_task_ledger.md active DevOps rows.
  - PROGRESS.md around Git divide and gitignore drain.
contradictions_or_history:
  Earlier broad Git operations caused slow/large surfaces. Current policy is
  deliberately narrow.
current_evidence_needed:
  Round 2 should check the latest DevOps rows before adding any new Git rule.
formal_target_if_promoted:
  Already in AGENTS.md and agent_task_ledger.md.
next_round_action:
  Do not run broad Git status as part of session memory extraction; use targeted diffs.
```

## Rejected Or Superseded Historical Themes To Preserve

These are not formal facts, but they are important warnings for future sessions.

```text
REJ-001:
  Manual Codex App-only thread creation by directly inserting SQLite rows and
  short JSONL files is rejected for normal work. Create real WSL/VSCode runtime
  conversations first if visibility is needed.

REJ-002:
  Treating Windows CLI/App separation as the preferred permanent fix is
  superseded for the user's current preference. The user wants shared Windows
  state unless they explicitly ask for isolation.

REJ-003:
  Reusing rejected Sunray150 material candidates as final UE assets is rejected.
  Latest material status needs direct evidence review before export/import.

REJ-004:
  Fixing Sunray propeller placement by manual yaw/Z/XY tuning is rejected.
  The user reframed it as an assembly/mating constraint problem.

REJ-005:
  Keyboard/grid-step/static point-cloud/2D-only mapping demos are smoke-only or
  rejected as product architecture. They must not become final UAV simulation
  evidence.

REJ-006:
  Browser HTML point-cloud/map previews are not accepted as active robotics map
  review surfaces. Use RViz/RViz2 or native robotics visualization for active
  point-cloud/map review.
```

## Round 2 Backlog

1. Verify `Docs/Workflows/session_memory_migration.md` against existing
   TaskSecretary, audit, and orchestration docs for duplication or conflict.
2. Add the workflow to `Docs/Index/workflow_index.md` if review passes.
3. Add a long-running ledger row for the session-memory migration task.
4. Extract a second cache file focused only on high-risk Sunray150 asset memory,
   reading current result manifests and source scripts first.
5. Extract a second cache file focused only on UE/ROS2/FAST-LIO architecture
   memory, reading the active design doc and ledger rows first.
6. Extract a second cache file focused only on MWORKS/controller/evidence
   memory, reading current workflow/report files first.
7. Decide which items are already fully represented in formal docs and should
   remain as pointers rather than new formal patches.

## Do Not Promote Yet

- Any final Sunray150 assembly or material parameter.
- Any claim that FAST-LIO, RViz2, or planner integration is complete.
- Any claim that Codex App hangs have a single root cause.
- Any controller performance result not tied to current evidence artifacts.
- Any old task status from chat unless the ledger/PROGRESS/current files agree.
