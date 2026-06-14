# CoAgent Operating Migration Map

Status: current migration map, 2026-06-10 CST.

The migration boundary is `CoAgent/`. Project application workflows remain in
the host project unless they define reusable agent-OS behavior.

## Current Result

`CoAgent/docs/operating/` is now split-audited as the portable operating layer.
The former conservative no-loss copies have been reduced to reusable core
policy after their MoSim-specific semantics were verified in host adapters,
registry, board, ledgers, cache files, or indexes.

Do not delete the old `Docs/Workflows/*` compatibility paths. They are the
host-project landings for MoSim-specific details.

## Portable Operating Files

| CoAgent Path | Portable Role | Host Landing For Removed Local Detail |
|---|---|---|
| `CoAgent/docs/operating/agent_os_operating_model.md` | overall portable agent-OS model: shared core, role views, capability router, task packet scope | MoSim product direction and board state remain in `Docs/Workflows/new_conversation_context.md` and `Docs/Workflows/mainline_operations_board.md`. |
| `CoAgent/docs/operating/org_operating_model.md` | portable organization model, role catalogue, delegation, conflict ownership | `Docs/Workflows/org_operating_model.md`, `CoAgent/dispatch/department_threads.json`, `Docs/Workflows/mosim_visible_dispatch_adapter.md`. |
| `CoAgent/docs/operating/coagent_ops_patrol_workflow.md` | portable patrol, durable-start liveness, recovery, bounded dispatch, failover, SLO states | `Docs/Workflows/coagent_ops_patrol_workflow.md`, `Docs/Workflows/mosim_visible_dispatch_adapter.md`, `Docs/Workflows/mainline_operations_board.md`, `CoAgent/dispatch/department_threads.json`. |
| `CoAgent/docs/operating/agent_orchestration.md` | portable task graph, queue, dispatch, delegation, checkpoint, review, evidence, resume, Git ownership rules | `Docs/Workflows/agent_orchestration.md`, `Docs/Workflows/mosim_visible_dispatch_adapter.md`, `Docs/Workflows/agent_task_ledger.md`, `Docs/Index/external_learning_index.md`. |
| `CoAgent/docs/operating/coagent_meta_maintenance.md` | portable registry hygiene, capability inventory, automation records, stale-rule prevention, incident follow-up | `Docs/Workflows/coagent_meta_maintenance.md`, `Docs/Workflows/coagent_ops_patrol_workflow.md`, `CoAgent/dispatch/department_threads.json`, `Docs/Workflows/agent_task_ledger.md`. |
| `CoAgent/docs/operating/tooling_assets_governance.md` | portable native-surface policy, capability-card shape, tool intake, runtime boundaries, entry-document slimming | `Docs/Workflows/tooling_assets_governance.md`, `Docs/Index/capability_index.md`, `Docs/Index/api_index.md`, host domain skills. |
| `CoAgent/docs/operating/session_memory_migration.md` | portable cache-first, three-round memory promotion and anti-pollution workflow | `Docs/Workflows/session_memory_migration.md`, `Docs/Cache/session_memory_migration/`, `Docs/Index/project_work_memory_index.md`, host ledgers. |
| `CoAgent/docs/operating/context_documentation_governance.md` | portable context authority ladder, document responsibilities, documentation-secretary boundary, no-loss doc migration rule | `Docs/Workflows/new_conversation_context.md`, `Docs/Index/project_work_memory_index.md`, `Docs/Workflows/session_memory_migration.md`, `CoAgent/dispatch/department_threads.json`. |

## Audit And Review Records

| Path | Role |
|---|---|
| `CoAgent/docs/operating/PORTABILITY_REVIEW_20260610.md` | Review record for the portable boundary, durable-start dispatch rule, default no-thread-click heartbeat decision, and final split result. |
| `CoAgent/docs/operating/audits/no_loss_split_audit_20260610.md` | Deletion-to-landing rows for each portable split in this pass. |
| `CoAgent/docs/operating/audits/coagent_ops_efficiency_audit_20260609.md` | Historical Chinese audit/reference note, not executable policy. |

## No-Loss Migration Gate

The migration order remains mandatory for future slimming:

```text
1. create or verify the landing file
2. copy or restate the source block there
3. record deletion-to-landing status
4. update indexes and startup pointers
5. only then slim the old entry/source text
```

For any future large slimming, record each removed block with:

```text
source block:
landing file and section:
status: exact | equivalent | intentionally_host_local | obsolete_superseded | missing
reviewer:
date:
```

If the landing file is missing, the status is `missing`, or stop conditions are
weakened, restore the source block or patch the landing before reporting
completion.

## Host-Project Local By Design

These are not migrated into CoAgent as generic operating policy:

| MoSim Path | Reason |
|---|---|
| `Docs/Workflows/mainline_operations_board.md` | Current MoSim PMO board, not portable policy. |
| `Docs/Workflows/agent_task_ledger.md` | MoSim historical/recovery ledger. |
| `PROGRESS.md` | MoSim current project progress. |
| `Docs/Design/` | MoSim product/technical architecture. |
| `Docs/Skills/Mworks/`, `Docs/Skills/Unreal/`, `Docs/Skills/Sysplorer/` | Host domain execution skills. |
| `Models/`, `UE5/`, `Config/`, `Scripts/`, `References/`, `Results/` | MoSim application assets, tooling, and evidence. |
| `Docs/Workflows/mosim_visible_dispatch_adapter.md` | MoSim-specific visible-department domain gate adapter. |

## Already In CoAgent

| Path | Role |
|---|---|
| `CoAgent/dispatch/communication_contract.md` | Packet, dispatch, semantic boundary, planning, return/blocker, and SLO contract. |
| `CoAgent/dispatch/department_threads.json` | Host-project visible-route registry using portable schema; concrete ids are host-local. |
| `CoAgent/protocol/` | Packet schemas, templates, and protocol vocabulary. |
| `CoAgent/runtime/`, `task_health/`, `status_export/`, `review_queue/`, `result_router/` | Reusable local runtime/status/review machinery. |
| `CoAgent/hooks/`, `automation/`, `doctor/`, `transport/` | Reusable guardrail, automation, health-check, and transport boundaries. |

## Cleanup Candidates

These should be cleaned only after review:

```text
CoAgent/**/__pycache__/
CoAgent/**/*.pyc
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/
CoAgent/work_queue/audits/* dry-run outputs
CoAgent/docs/status/* obsolete one-off status snapshots
CoAgent/docs/research/* if superseded by current learning index
```

Do not delete `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/` until any still-useful
architecture conclusions are either already represented in `CoAgent/docs/` or
explicitly marked obsolete.

## Audited Split Rows

| Date | Source Block | Landing File And Section | Status | Reviewer |
|---|---|---|---|---|
| 2026-06-10 | `CoAgent/dispatch/communication_contract.md` old MoSim domain-dispatch specifics | `Docs/Workflows/mosim_visible_dispatch_adapter.md#4-domain-gates` | exact | Codex current turn |
| 2026-06-10 | `CoAgent/docs/operating/coagent_ops_patrol_workflow.md` MoSim owner/thread ids, board sections, incident refresh details, MWORKS/ROS2/UE host gates, and packet examples | `CoAgent/docs/operating/audits/no_loss_split_audit_20260610.md#deletion-to-landing-rows` | exact/equivalent | Codex current turn + subagent audit |
| 2026-06-10 | `CoAgent/docs/operating/org_operating_model.md` MoSim visible routes, route IDs, deleted route history, domain examples, local path boundary, and documentation-secretary aliases | `CoAgent/docs/operating/audits/no_loss_split_audit_20260610.md#deletion-to-landing-rows` | exact/equivalent | Codex current turn + subagent audit |
| 2026-06-10 | `CoAgent/docs/operating/agent_orchestration.md`, `coagent_meta_maintenance.md`, `tooling_assets_governance.md`, `session_memory_migration.md`, and new `context_documentation_governance.md` host-local details | `CoAgent/docs/operating/audits/no_loss_split_audit_20260610.md#deletion-to-landing-rows` | exact/equivalent | Codex current turn + subagent audit |

## Current Conclusion

No `CoAgent/docs/operating/*.md` file remains intentionally mixed as a
portable-core plus MoSim-adapter copy. Future work may still simplify wording,
add machine-readable capability cards, or retire obsolete audits, but the
portable operating split itself is complete for this pass.
