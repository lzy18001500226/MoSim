# CoAgent No-Loss Split Audit 20260610

Status: active audit record, 2026-06-10 CST.

This audit records the second-pass split of mixed MoSim/CoAgent operating
documents. The rule is no-loss: a block may be slimmed from a portable CoAgent
document only after its host landing or portable replacement is named here.

## Split Scope

In scope for this pass:

```text
CoAgent/docs/operating/coagent_ops_patrol_workflow.md
CoAgent/docs/operating/org_operating_model.md
CoAgent/docs/operating/MIGRATION_MAP.md
CoAgent/docs/operating/PORTABILITY_REVIEW_20260610.md
CoAgent/docs/operating/agent_orchestration.md
CoAgent/docs/operating/coagent_meta_maintenance.md
CoAgent/docs/operating/tooling_assets_governance.md
CoAgent/docs/operating/session_memory_migration.md
CoAgent/docs/operating/context_documentation_governance.md
```

Out of scope for this pass:

```text
CoAgent runtime, automation, hooks, schemas, and visible-thread lifecycle
```

## Subagent Review Inputs

Two read-only explorer subagents were used because the main risk was silent
semantic loss.

| Subagent | Scope | Result |
|---|---|---|
| `019eb065-b9b3-7f21-ba95-975318c9daf4` | Audit mixed CoAgent operating docs for MoSim/host-local content and likely landing. | Produced source-area to landing-file map. |
| `019eb066-0095-7191-aecf-85cded33f193` | Audit host landing docs for preserved MoSim semantics. | Confirmed host landing structure was present; remaining context-governance gap was closed by creating `CoAgent/docs/operating/context_documentation_governance.md`. |
| `019eb07d-0f59-7a10-a8a0-34438ede8812` | Resume-pass audit of remaining mixed operating docs. | Confirmed host-local content categories and risk if removed without landing. |
| `019eb07d-2369-7f33-b9ae-bc50ed8e561c` | Resume-pass audit of host landing docs and indexes. | Confirmed host adapters and indexes preserve the removed MoSim semantics; noted capability-card/checker work as future enhancement, not a split blocker. |

## Deletion-To-Landing Rows

| Source File | Source Block / Semantic Area | Landing File And Section | Status | Reviewer | Date |
|---|---|---|---|---|---|
| `CoAgent/docs/operating/coagent_ops_patrol_workflow.md` | Concrete MoSim owner names, thread IDs, PMO/context-maintenance aliases, and refresh-only non-MoSim watch target. | `CoAgent/dispatch/department_threads.json`; `Docs/Workflows/coagent_ops_patrol_workflow.md#1-scope-and-owners`; `Docs/Workflows/org_operating_model.md#21-codex-app-operating-threads` | equivalent | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/coagent_ops_patrol_workflow.md` | MoSim patrol read order, PMO board update limits, active-visible engineering queue handling, and support-lane ordering. | `Docs/Workflows/coagent_ops_patrol_workflow.md#2-patrol-workflow`; `Docs/Workflows/mainline_operations_board.md`; `CoAgent/dispatch/department_threads.json` | equivalent | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/coagent_ops_patrol_workflow.md` | MoSim-specific `semantic_boundary.next_owner` examples such as MWORKS/ROS2/UE owner enums. | `Docs/Workflows/coagent_ops_patrol_workflow.md#3-semantic-boundary`; portable state classes remain in `CoAgent/docs/operating/coagent_ops_patrol_workflow.md#2-state-classification` | equivalent | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/coagent_ops_patrol_workflow.md` | Post-restart probe sweep wording with MoSim route examples and result packet path pattern. | `Docs/Workflows/coagent_ops_patrol_workflow.md#51-post-restart-probe-sweep`; generic restart validation remains in portable workflow. | equivalent | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/coagent_ops_patrol_workflow.md` | Incident-scoped thread-row refresh details: `MoSim｜` title region, 0.5s dwell, blank-pane skip, non-MoSim watch target. | `Docs/Workflows/coagent_ops_patrol_workflow.md#53-incident-scoped-thread-row-refresh-appendix` | exact | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/coagent_ops_patrol_workflow.md` | MWORKS/Sysplorer/Syslab window classification, activation/license evidence, background capture path, and MWORKS R2 review routing. | `Docs/Workflows/mosim_visible_dispatch_adapter.md#mworks--sysplorer--syslab`; `Docs/Workflows/coagent_ops_patrol_workflow.md#7-mworks-window-and-review-routing`; `Docs/Index/capability_index.md` | exact | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/coagent_ops_patrol_workflow.md` | MoSim R2/R3 failover classes and live-action prohibitions for MWORKS/ROS2/UE. | `Docs/Workflows/mosim_visible_dispatch_adapter.md#5-failover-adapter`; `Docs/Workflows/coagent_ops_patrol_workflow.md#61-r2r3-failover-lane`; `CoAgent/dispatch/department_threads.json` | exact | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/coagent_ops_patrol_workflow.md` | MoSim packet example fields naming PMO title/id and MWORKS checker command. | `Docs/Workflows/coagent_ops_patrol_workflow.md#8-packet-template`; portable template remains in `CoAgent/protocol/templates/visible_thread_dispatch_packet.json`; domain checker policy remains in `Docs/Workflows/mosim_visible_dispatch_adapter.md` | equivalent | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/org_operating_model.md` | Concrete MoSim visible-thread table, thread IDs, deleted WeChat route, old environment migration route, probe/learning route IDs, and current aliases. | `CoAgent/dispatch/department_threads.json`; `Docs/Workflows/org_operating_model.md#21-codex-app-operating-threads` | exact | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/org_operating_model.md` | MoSim domain examples: PX4 parameter identification, UE Fab import, AirSim batch migration, MWORKS/ROS2/UE runtime resource checks. | `Docs/Workflows/org_operating_model.md`; `Docs/Workflows/mosim_visible_dispatch_adapter.md`; `Docs/Workflows/agent_task_ledger.md` | equivalent | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/org_operating_model.md` | MoSim-specific path boundary `C:\Users\HP\Desktop\MoSim` and local status artifacts. | `AGENTS.md#1-hard-boundaries`; `Docs/Workflows/new_conversation_context.md`; `Docs/Workflows/org_operating_model.md#5-security-gate-boundary` | exact | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/org_operating_model.md` | Documentation-secretary/context-maintenance route naming and alias history. | `CoAgent/dispatch/department_threads.json`; `Docs/Workflows/org_operating_model.md#3-documentation-ownership-rule`; `Docs/Workflows/new_conversation_context.md` | exact | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/agent_orchestration.md` | MoSim P0 priority, MWORKS/ROS2/UE/Sunray domain dispatch gates, current route names/IDs, deleted WeChat route history, Codex++ restart path, and MoSim packet examples. | `Docs/Workflows/agent_orchestration.md`; `Docs/Workflows/mosim_visible_dispatch_adapter.md`; `Docs/Workflows/coagent_ops_patrol_workflow.md`; `CoAgent/dispatch/department_threads.json`; `Docs/Index/capability_index.md` | exact/equivalent | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/agent_orchestration.md` | Long Git and external-reference import examples including AirSim/RflySim/UE/Sunray path families and local batch paths. | `Docs/Workflows/agent_orchestration.md`; `Docs/Workflows/agent_task_ledger.md`; `Docs/Workflows/audit_external_repo.md`; `Docs/Index/external_learning_index.md` | equivalent | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/agent_orchestration.md` | MWORKS GUI/session reuse, activation, screenshot, live gate, and result-evidence specifics. | `Docs/Workflows/mosim_visible_dispatch_adapter.md`; `Docs/Workflows/coagent_ops_patrol_workflow.md`; `Docs/Skills/Mworks/*`; `Docs/Index/capability_index.md` | exact/equivalent | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/coagent_meta_maintenance.md` | Dated MoSim hotfix log, CoAgentOps heartbeat prompt details, deleted WeChat route incidents, Codex++ restart incidents, and MWORKS activation/window evidence incidents. | `Docs/Workflows/coagent_meta_maintenance.md`; `Docs/Workflows/agent_task_ledger.md`; `CoAgent/dispatch/department_threads.json`; `Docs/Workflows/coagent_ops_patrol_workflow.md` | exact | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/coagent_meta_maintenance.md` | MoSim automation inventory, removed detached cron/watchdog records, email-before-restart wording, and current route ownership table. | `Docs/Workflows/coagent_meta_maintenance.md`; `Docs/Index/capability_index.md`; `CoAgent/dispatch/department_threads.json` | exact/equivalent | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/tooling_assets_governance.md` | Host-local Codex config paths, plugin cache paths, Windows MCP/Win32 desktop policy, MWORKS/UE/ROS runtime adapters, local reference mirrors, and MoSim owner route names. | `Docs/Workflows/tooling_assets_governance.md`; `Docs/Index/capability_index.md`; `Docs/Index/api_index.md`; `CoAgent/dispatch/department_threads.json`; `Docs/Workflows/mosim_visible_dispatch_adapter.md` | exact/equivalent | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/tooling_assets_governance.md` | Entry-document slimming landing map with MoSim-specific startup docs, MWORKS/ROS/UE evidence boundaries, local filesystem boundary, and source-first reference families. | `Docs/Workflows/tooling_assets_governance.md#10-entry-document-slimming-rule`; `AGENTS.md`; `Docs/Workflows/new_conversation_context.md`; `Docs/Index/workflow_index.md` | exact/equivalent | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/session_memory_migration.md` | MoSim long-session names, project cache paths, promotion targets, MWORKS/ROS/UE risk examples, and MoSim completion definition. | `Docs/Workflows/session_memory_migration.md`; `Docs/Cache/session_memory_migration/`; `Docs/Index/project_work_memory_index.md`; `Docs/Workflows/agent_task_ledger.md` | exact | Codex current turn + subagent audit | 2026-06-10 |
| `CoAgent/docs/operating/context_documentation_governance.md` | Previously referenced but absent portable doc for context, prompt-stack, documentation secretary, capability-routing, and project-owned memory governance. | New portable core in `CoAgent/docs/operating/context_documentation_governance.md`; host details remain in `Docs/Workflows/new_conversation_context.md`, `Docs/Index/project_work_memory_index.md`, `Docs/Workflows/session_memory_migration.md`, `Docs/Workflows/tooling_assets_governance.md`, and `CoAgent/dispatch/department_threads.json` | equivalent | Codex current turn + subagent audit | 2026-06-10 |

## Deferred Split Rows

No `CoAgent/docs/operating/*.md` file remains intentionally mixed after this
pass. Future cleanup candidates are historical archives, oversized host
ledgers, and obsolete status snapshots, not portable operating split blockers.

## Current Conclusion

The files slimmed in this pass are safe to convert into portable core documents
because all MoSim-specific details removed from them remain in host adapters,
registry, board, ledger, cache, or capability/API/workflow indexes.
