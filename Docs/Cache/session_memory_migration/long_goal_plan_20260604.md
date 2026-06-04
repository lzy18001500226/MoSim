# Long Goal Plan - Session Memory Migration

Date: 2026-06-04 CST

Scope: long-running recovery plan for migrating the `MoSim|四旋翼无人机仿真系统`
conversation into project-local memory.

This file is cache-only. It is a task plan and recovery surface, not formal
technical truth. It must not be used to promote parameters, scene acceptance,
FAST-LIO status, MWORKS evidence, CoAgent capability, or infrastructure state
without the round gates below.

## Goal

```text
objective:
  Preserve the important history, final useful decisions, rejected routes,
  current evidence boundaries, and recovery rules from the long MoSim
  conversation so future Codex conversations can start fresh without becoming
  blind or repeating old mistakes.

hard_rule:
  Every historical item must pass at least three rounds before entering formal
  project documents:
    round 1: cache candidate or rejected/superseded history
    round 2: verify against current project files, result artifacts, and
             contradictions
    round 3: re-read current evidence and the target document, then patch
             narrowly or reject/supersede

current_state:
  The currently identified topic set has round-1 capture and topic-specific
  round-2 evidence review. Round-3 application remains open, with
  parameter-identification provenance clarified once and no numeric parameter
  promoted. MWORKS codegen/SIL has also been rechecked in round 3 with no
  formal patch because existing workflow and architecture docs already carry
  the safe boundary. UE scene-source/renderer state has a round-3
  disambiguation patch in `Docs/Workflows/unreal_renderer.md`. ROS2/FAST-LIO
  runtime setup has a round-3 source-priority patch in
  `Docs/Workflows/ros2_runtime_setup.md`: the 2026-06-01 apt/key and rosbridge
  notes are prior infrastructure evidence, current FAST-LIO answers use the
  latest route-specific `*_CURRENT` gate first, and stale helper-script
  references were replaced with scripts present in this checkout. CoAgent
  operating history has been rechecked in round 3 with no formal patch because
  the existing CoAgent docs and orchestration workflow already carry the gate;
  this migration did not authorize implementation or live visibility claims.
  External reference learning has also been rechecked in round 3 with no
  formal patch because existing indexes/workflows already require
  reference-index-first routing and explicit approval plus local evidence before
  direct runtime adoption. A completion audit now closes the currently
  identified topic set for migration purposes; newly surfaced historical claims
  must start again at round 1.
```

## Recovery Entry Points

Read in this order:

```text
1. PROGRESS.md
2. Docs/Workflows/agent_task_ledger.md
   row: SESSION-MEMORY-MIGRATION-20260604
3. Docs/Workflows/session_memory_migration.md
4. Docs/Cache/session_memory_migration/coverage_matrix_20260604.md
5. Docs/Cache/session_memory_migration/round3_promotion_rejection_map_20260604.md
6. Docs/Cache/session_memory_migration/completion_audit_20260604.md
7. The topic-specific round-2 cache file for the item being worked
```

Do not read external Codex session files, home directories, tokens, browser
profiles, or personal data for this migration unless the user makes a fresh
infrastructure request.

## Topic Lanes

| Lane | Current Cache State | Round-3 Direction |
|---|---|---|
| Codex App / VSCode / CLI / MCP infrastructure | round-2 infrastructure cache | Keep machine-specific repair history as infrastructure memory; do not touch external `.codex` files unless explicitly requested. |
| MWORKS evidence and smoke boundaries | round-2 controller-evidence cache | Patch only if a workflow lacks `smoke_only`, source label, or check/simulate boundary wording. |
| MWORKS codegen and generated runtime | round-3 rechecked, no formal patch | Existing docs already keep the `GenerateModelCode` route and PID-demo-only SIL evidence; do not claim per-controller runtime authority. |
| UE / ROS2 / FAST-LIO runtime | round-3 source-priority patch applied | Use latest matching `*_CURRENT` gate and linked runtime directory first; manual review and final product acceptance remain separate. |
| UE scene source and renderer | round-3 state-disambiguation patch applied | Keep registry policy primary, active content links, manual-review target, Gate-B/runtime readiness, smoke evidence, and final acceptance separate. |
| Sunray150 assets and materials | round-2 Sunray cache | Preserve accepted source-chain facts and rejected material/proxy routes; no UE export until accepted review evidence exists. |
| Sunray150 parameter identification | round-3 no-numeric-promotion disposition | Keep all current numeric values as `source=SDF_migration` seeds unless a complete identification bundle appears. |
| CoAgent operating history | round-3 rechecked, no formal patch | Guardrail only; no implementation, live visibility claim, transport, automation, department, notification, schema, or tool expansion from this migration. |
| External references / skills / agent systems | round-3 rechecked, no formal patch | Use indexes and audit workflow; external projects are contracts/patterns unless separately approved and proven locally. |
| Git split / large worktree hygiene | infrastructure cache plus ledger | Keep as a separate GitIntegrator lane; no broad Git cleanup inside migration. |

## Round-3 Work Queue

Pick one item per round:

```text
1. ROS2/FAST-LIO status-source-priority note:
   completed for migration round 3 on 2026-06-04. Current disposition:
   `Docs/Workflows/ros2_runtime_setup.md` now marks the 2026-06-01 apt/key and
   rosbridge notes as prior infrastructure evidence, routes current FAST-LIO
   answers through the latest matching `*_CURRENT` gate and linked runtime
   directory, and removes current-command references to missing helper scripts.
   Factory Gate B is `ready_for_manual_rviz_ue_review`; it does not prove final
   controller integration, planner performance, or product acceptance.

2. Scene-source state disambiguation:
   completed for migration round 3 on 2026-06-04. Current disposition:
   `Docs/Workflows/unreal_renderer.md` now separates registry policy primary,
   active renderer links, manual-review target, Gate-B/runtime readiness,
   smoke evidence, and final acceptance. No scene was promoted to final product
   acceptance.

3. Parameter provenance check:
   rerun project-local evidence search, re-read current model fields, then
   either keep cache-only or correct a formal doc that mislabels SDF seeds as
   identified values.

4. Codegen/SIL boundary:
   completed for migration round 3 on 2026-06-04. Current disposition:
   workflow and architecture docs already cover the boundary; no newer
   time-varying or target-controller SIL artifact was found under
   `Results/codegen_probe`; no formal patch was made.

5. CoAgent scope gate:
   completed for migration round 3 on 2026-06-04. Current disposition:
   CoAgent docs already carry the gate, so no formal patch was needed. Recover
   direction from `CoAgent/STATUS.md`, `CoAgent/README.md`, decisions, SOPs,
   orchestration workflow, and ledgers. This migration does not authorize
   implementation, live visibility-health claims, app-server transport,
   unattended automation, department expansion, schema changes, real routine
   notifications, or tool/MCP expansion.

6. External-reference boundary:
   completed for migration round 3 on 2026-06-04. Current disposition:
   external learning index, audit workflow, reference index, agent
   classification, real-UAV reuse matrix/source audit, UE renderer workflow,
   and architecture doc already carry the boundary. No formal patch was needed.
   External projects remain contracts, patterns, source material, or candidates
   unless an approved integration has local build/runtime/test evidence.

7. Completion audit:
   completed for migration closeout on 2026-06-04. Current disposition:
   `Docs/Cache/session_memory_migration/completion_audit_20260604.md` records
   that the current identified topic set has round-3 dispositions and that a
   new conversation can recover from project-local docs/cache without the old
   chat transcript. This does not certify unknown external session lines; any
   newly surfaced claim must enter round 1.
```

After this checkpoint, the currently identified round-2 topic set has round-3
dispositions and a completion audit. The next safe work is ordinary project
execution; if a future historical claim appears uncovered, route it through the
same three-round cache workflow instead of promoting it directly.

## Completion Criteria

The migration can be marked complete only when:

```text
all_identified_topics:
  - have round-1 cache entries or are explicitly out of scope

all_high_risk_items:
  - are promoted through round 3, rejected, superseded, or blocked on explicit
    user review/current evidence

formal_docs:
  - contain only narrow current-evidence-backed statements
  - do not contain old numeric parameters, visual acceptance, simulation claims,
    FAST-LIO status, Codex repair facts, or CoAgent capabilities from chat
    memory alone

recovery:
  - PROGRESS.md, agent_task_ledger.md, workflow_index.md, coverage matrix, and
    round-3 map all point to the final migration state
  - a new conversation can continue without reading the old transcript
```

Do not mark the goal complete just because the cache exists. Completion requires
round-3 disposition of high-risk items.
