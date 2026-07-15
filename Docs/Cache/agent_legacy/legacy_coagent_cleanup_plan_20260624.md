# Legacy CoAgent Cleanup Plan 2026-06-24

> Cache/review material, not a routine startup workflow. Purpose: retire
> CoAgent / multi-thread dispatch concepts from active MoSim operation while
> preserving useful research history and avoiding broken hook, checker, or
> script references.

## 1. Cleanup Decision

The active MoSim project no longer uses the previous multi-thread operating
model. Current work is single-thread execution with compact startup docs and
topic-specific workflows.

The former CoAgent / AgentOS material is reclassified as legacy:

- architecture research;
- historical multi-agent operating design;
- packet/checker experiments;
- visible-thread dispatch design;
- dead-thread patrol and recovery experiments;
- documentation-governance research.

## 2. Active Keep Set

Keep these in the ordinary startup path:

```text
AGENTS.md
Docs/Workflows/new_conversation_context.md
Docs/Workflows/mainline_operations_board.md
Docs/Workflows/single_thread_operating_model.md
Docs/Workflows/sunray_ros1_current_runtime_lane.md
Docs/Index/sunray_migration_index.md
Docs/Index/workflow_index.md
Docs/Index/api_index.md
Docs/Index/project_work_memory_index.md
Docs/Skills/**
Docs/Design/**
Models/**
Scripts/**
Results/**
References/**
```

## 3. Legacy Set

Do not load these for normal project execution:

```text
CoAgent/docs/**
Docs/Workflows/agent_orchestration.md
Docs/Workflows/agent_task_ledger.md
Docs/Workflows/coagent_meta_maintenance.md
Docs/Workflows/coagent_ops_efficiency_audit_20260609.md
Docs/Workflows/coagent_ops_patrol_workflow.md
Docs/Workflows/mosim_visible_dispatch_adapter.md
Docs/Workflows/org_operating_model.md
Docs/Workflows/single_thread_longrun_execution_queue_20260610.md
```

These may be archived or deleted only after reference checks and user review.

## 4. Do Not Delete Yet

Do not delete these legacy implementation paths in the first cleanup pass:

```text
CoAgent/hooks/**
CoAgent/protocol/**
CoAgent/dispatch/**
CoAgent/skills/**
CoAgent/capabilities/**
CoAgent/doctor/**
CoAgent/tests/**
Scripts/quality/**
```

Reason: active hook/protocol/desktop-skill/capability entrypoints have been
migrated to `Scripts/`, `Config/`, and `Docs/Skills/`, but old copies may still
be fallback material or referenced by legacy tests, runtime wrappers, gateway
code, and cache documents. They need a final dependency audit before removal.

## 5. Cleanup Order

1. Remove CoAgent/dispatch language from active startup docs.
2. Mark `CoAgent/docs` as legacy/reference and do not recreate the discarded
   `Docs/AgentOS` copy unless the user explicitly reopens that migration.
3. Move CoAgent-related workflow rows in `Docs/Index/workflow_index.md` under
   a legacy section.
4. Run text scans for active references.
5. After user review, archive or delete legacy docs in a path-limited pass.
6. Separately audit remaining executable CoAgent runtime/gateway/test paths
   before moving or deleting code.

## 6. Success Criteria

- A normal MoSim startup does not require CoAgent/AgentOS docs.
- The board describes one active thread, not department dispatch.
- Multi-thread dispatch terms appear only in legacy/archive sections.
- The current Sunray/MWORKS/UE workflow remains reachable.
- No legacy hook/checker/runtime/gateway path is deleted without dependency
  proof.
