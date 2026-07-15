# CoAgent Deprecation Selection Review 2026-06-24

> Cache document, not an active workflow. Purpose: decide which parts of the
> legacy `CoAgent/docs/**` tree are worth extracting into current MoSim project
> documents after the project returned to single-thread execution.

## 1. Current Decision

CoAgent is deprecated as an active MoSim operating architecture. It does not
need to be deleted. Its documentation should not be bulk-migrated. Only content
that helps current single-thread MoSim execution should be extracted into
project docs.

Current active entry remains:

```text
AGENTS.md
Docs/Workflows/new_conversation_context.md
Docs/Workflows/mainline_operations_board.md
Docs/Workflows/single_thread_operating_model.md
```

## 2. Selection Criteria

Migrate only if the content:

- prevents a repeated project failure;
- improves current single-thread task execution;
- clarifies where docs, hooks, skills, MCPs, screenshots, logs, or memory rules
  belong;
- supports the current Sunray/MWORKS/UE evidence workflow;
- can become a short workflow, index row, checklist, or tool-use rule.

Keep as legacy if the content is useful history but not current workflow.

Ignore if the content is obsolete, specific to the abandoned multi-thread
architecture, or only records old approval/status history.

## 3. Recommended Destinations

| Content Type | Destination |
|---|---|
| Current single-thread task habits | `Docs/Workflows/single_thread_operating_model.md` |
| Documentation placement and context hygiene | future `Docs/Workflows/documentation_governance.md`, or merge into `Docs/Workflows/tooling_assets_governance.md` |
| Tool / skill / MCP / hook routing | `Docs/Index/capability_index.md`, `Docs/Index/api_index.md`, `Docs/Workflows/tooling_assets_governance.md` |
| Session memory and old-chat promotion | `Docs/Workflows/session_memory_migration.md` |
| Useful research notes not ready for active rules | `Docs/Cache/research/` or this cache note |
| Abandoned CoAgent design | leave in `CoAgent/docs/**` as legacy reference |

## 4. File-Level Selection Table

Decision values:

- `migrate_candidate`: extract useful fragments after reading the source file.
- `legacy_reference`: leave in `CoAgent/docs`; do not load during normal work.
- `ignore_obsolete`: do not migrate unless the user explicitly asks for history.

| Source File | Decision | Possible Destination | Reason |
|---|---|---|---|
| `CoAgent/docs/README.md` | legacy_reference | none | Old CoAgent doc map; current entry is now single-thread docs. |
| `CoAgent/docs/architecture/agent_concept_boundaries.md` | migrate_candidate | `Docs/Cache/research/agent_project_terms.md` or glossary section | May contain useful vocabulary boundaries for agent/project discussions. |
| `CoAgent/docs/architecture/ARCHITECTURE.md` | legacy_reference | none | CoAgent architecture overview; not current MoSim workflow. |
| `CoAgent/docs/architecture/coagent_agent_design_protocol.md` | legacy_reference | none | Multi-agent design protocol. |
| `CoAgent/docs/architecture/coagent_architecture_issue_register.md` | legacy_reference | none | Historical unresolved AgentOS issues. |
| `CoAgent/docs/architecture/coagent_complexity_control.md` | migrate_candidate | `Docs/Workflows/documentation_governance.md` | May contain anti-bloat rules relevant to current docs. |
| `CoAgent/docs/architecture/coagent_concrete_agent_design.md` | legacy_reference | none | Concrete multi-agent roles are no longer active. |
| `CoAgent/docs/architecture/coagent_conversation_mapping.md` | legacy_reference | none | Conversation/department mapping is deprecated. |
| `CoAgent/docs/architecture/coagent_department_capability_model.md` | legacy_reference | none | Department capability model is deprecated. |
| `CoAgent/docs/architecture/coagent_directory_merge_design_20260610.md` | legacy_reference | none | Historical directory migration design. |
| `CoAgent/docs/architecture/coagent_dynamic_agent_codex_feature_gap_2026_05_29.md` | legacy_reference | none | Research on dynamic agent teams; not current execution. |
| `CoAgent/docs/architecture/coagent_dynamic_task_team_v2_design.md` | legacy_reference | none | Dynamic task-team design is deprecated. |
| `CoAgent/docs/architecture/coagent_minimal_closed_loop_protocol.md` | legacy_reference | none | Closed-loop CoAgent proof protocol, not current MoSim loop. |
| `CoAgent/docs/architecture/coagent_open_source_adoption_plan.md` | migrate_candidate | `Docs/Index/external_learning_index.md` or cache | May contain useful external-source review discipline. |
| `CoAgent/docs/architecture/coagent_portable_core_mosim_adapter_design_20260610.md` | legacy_reference | none | Portable-core/MoSim adapter split is no longer the active direction. |
| `CoAgent/docs/architecture/coagent_problem_driven_operating_model.md` | migrate_candidate | `Docs/Workflows/single_thread_operating_model.md` | May contain problem-first execution habits worth extracting. |
| `CoAgent/docs/architecture/coagent_review_merge_protocol.md` | legacy_reference | none | Multi-agent review/merge protocol. |
| `CoAgent/docs/architecture/coagent_solution_synthesis.md` | legacy_reference | none | CoAgent solution synthesis; too broad for current docs. |
| `CoAgent/docs/architecture/coagent_task_surface_model.md` | migrate_candidate | `Docs/Workflows/single_thread_operating_model.md` | May clarify task surface vs runtime/tool surface. |
| `CoAgent/docs/architecture/coagent_task_team_architecture.md` | legacy_reference | none | Task-team architecture is deprecated. |
| `CoAgent/docs/architecture/coagent_user_intervention_ux.md` | migrate_candidate | `Docs/Workflows/single_thread_operating_model.md` | May contain useful ask-user/blocker/email escalation habits. |
| `CoAgent/docs/architecture/coagent_vendor_gap_review_2026_05_29.md` | legacy_reference | none | Historical vendor-pattern research. |
| `CoAgent/docs/architecture/coagent_vendor_pattern_mapping.md` | legacy_reference | none | Historical vendor-pattern mapping. |
| `CoAgent/docs/architecture/COMPONENT_MAP.md` | legacy_reference | none | CoAgent component map; not current project structure. |
| `CoAgent/docs/architecture/enterprise_to_agent_mapping.md` | ignore_obsolete | none | Enterprise/agent analogy does not support current execution. |
| `CoAgent/docs/architecture/local_runtime_design_matrix.md` | migrate_candidate | `Docs/Index/api_index.md` or cache | May contain useful local-runtime/tool-surface comparisons. |
| `CoAgent/docs/architecture/README.md` | legacy_reference | none | Folder map only. |
| `CoAgent/docs/architecture/task_intake_and_governance.md` | migrate_candidate | `Docs/Workflows/single_thread_operating_model.md` | May contain useful task-intake and stop-condition rules. |
| `CoAgent/docs/architecture/technical_enterprise_operating_system_closure.md` | ignore_obsolete | none | Old architecture closure note. |
| `CoAgent/docs/architecture/technical_enterprise_operating_system.md` | ignore_obsolete | none | Enterprise OS metaphor is not current workflow. |
| `CoAgent/docs/decisions/coagent_design_decision_record.md` | legacy_reference | none | Old decision record. |
| `CoAgent/docs/decisions/coagent_design_discussion_packet.md` | legacy_reference | none | Old design discussion packet. |
| `CoAgent/docs/decisions/coagent_design_review_brief.md` | legacy_reference | none | Old review brief. |
| `CoAgent/docs/decisions/coagent_design_review_brief.zh.md` | legacy_reference | none | Old review brief. |
| `CoAgent/docs/decisions/coagent_goal_readiness_audit.md` | legacy_reference | none | Old readiness audit. |
| `CoAgent/docs/decisions/coagent_impl_03_07_completion_audit.md` | legacy_reference | none | Old implementation audit. |
| `CoAgent/docs/decisions/coagent_miniloop_01_human_review.md` | ignore_obsolete | none | Old mini-loop review packet. |
| `CoAgent/docs/decisions/coagent_miniloop_02_human_review.md` | ignore_obsolete | none | Old mini-loop review packet. |
| `CoAgent/docs/decisions/coagent_miniloop_03_human_review.md` | ignore_obsolete | none | Old mini-loop review packet. |
| `CoAgent/docs/decisions/coagent_post_approval_backlog.md` | legacy_reference | none | Old CoAgent backlog. |
| `CoAgent/docs/decisions/coagent_task_cancellation_policy.md` | migrate_candidate | `Docs/Workflows/single_thread_operating_model.md` | May contain useful cancellation/stop-condition rules. |
| `CoAgent/docs/decisions/README.md` | legacy_reference | none | Folder map only. |
| `CoAgent/docs/operating/agent_orchestration.md` | legacy_reference | none | Multi-agent orchestration is deprecated. |
| `CoAgent/docs/operating/agent_os_operating_model.md` | legacy_reference | none | AgentOS model is deprecated for current MoSim. |
| `CoAgent/docs/operating/coagent_meta_maintenance.md` | legacy_reference | none | CoAgent meta-maintenance is deprecated. |
| `CoAgent/docs/operating/coagent_ops_patrol_workflow.md` | ignore_obsolete | none | Patrol/recovery/dispatch workflow is explicitly abandoned. |
| `CoAgent/docs/operating/context_documentation_governance.md` | migrate_candidate | `Docs/Workflows/documentation_governance.md` | Likely contains useful context/document-placement rules. |
| `CoAgent/docs/operating/MIGRATION_MAP.md` | legacy_reference | none | Historical CoAgent migration map. |
| `CoAgent/docs/operating/org_operating_model.md` | legacy_reference | none | Organization/department model is deprecated. |
| `CoAgent/docs/operating/PORTABILITY_REVIEW_20260610.md` | legacy_reference | none | Historical portability review. |
| `CoAgent/docs/operating/project_bootstrap.md` | ignore_obsolete | none | New host CoAgent bootstrap is no longer current. |
| `CoAgent/docs/operating/README.md` | legacy_reference | none | Folder map only. |
| `CoAgent/docs/operating/session_memory_migration.md` | migrate_candidate | `Docs/Workflows/session_memory_migration.md` | May contain useful old-chat promotion/rejection rules. |
| `CoAgent/docs/operating/tooling_assets_governance.md` | migrate_candidate | `Docs/Workflows/tooling_assets_governance.md` | Likely contains useful hook/skill/MCP placement rules. |
| `CoAgent/docs/operating/audits/coagent_ops_efficiency_audit_20260609.md` | ignore_obsolete | none | CoAgentOps efficiency audit is tied to abandoned multi-thread workflow. |
| `CoAgent/docs/operating/audits/no_loss_split_audit_20260610.md` | legacy_reference | none | Historical no-loss audit. |
| `CoAgent/docs/research/agentic_software_engineering_operating_model_synthesis_20260610.md` | migrate_candidate | `Docs/Cache/research/agentic_software_engineering_notes.md` | May contain useful high-level agent-project lessons. |
| `CoAgent/docs/research/agentic_software_engineering_operating_research_plan_20260610.md` | ignore_obsolete | none | Old research plan; no need to migrate. |
| `CoAgent/docs/research/agentic_workflow_orchestration_glossary_20260610.md` | migrate_candidate | `Docs/Cache/research/agentic_terms.md` | Useful terminology reference if compressed. |
| `CoAgent/docs/research/context_documentation_governance_research_20260610.md` | migrate_candidate | `Docs/Workflows/documentation_governance.md` or cache | Useful background for document placement. |
| `CoAgent/docs/research/LEARNING_STRATEGY.md` | migrate_candidate | `Docs/Index/external_learning_index.md` or `Docs/Workflows/audit_external_repo.md` | May contain reusable external-project learning rules. |
| `CoAgent/docs/research/multi_agent_learning_urls.md` | legacy_reference | none | URL seed list; keep as history unless refreshing research. |
| `CoAgent/docs/research/README.md` | legacy_reference | none | Folder map only. |
| `CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md` | migrate_candidate | `Docs/Index/external_learning_index.md` | Compare with current external-learning index before merging. |
| `CoAgent/docs/research/THREE_ROUND_STUDY_AND_DISCUSSION.md` | ignore_obsolete | none | Old study process. |
| `CoAgent/docs/status/cc_connect_weixin_smoke_2026_05_31.md` | ignore_obsolete | none | WeChat path is deleted/historical. |
| `CoAgent/docs/status/codex_cli_entrypoint.md` | legacy_reference | none | Codex CLI status snapshot; not current MoSim workflow. |
| `CoAgent/docs/status/codex_visible_thread_sop.md` | ignore_obsolete | none | Visible-thread SOP is deprecated. |
| `CoAgent/docs/status/MIGRATION_STATUS.md` | legacy_reference | none | Historical migration status. |
| `CoAgent/docs/status/README.md` | legacy_reference | none | Folder map only. |

## 5. First Extraction Batch

Do not extract all candidates at once. First batch should be small:

1. `context_documentation_governance.md`
2. `tooling_assets_governance.md`
3. `session_memory_migration.md`
4. `task_intake_and_governance.md`
5. `coagent_user_intervention_ux.md`

Expected output:

- short rules merged into existing current docs;
- no long CoAgent prose copied verbatim;
- no new active CoAgent/AgentOS entrypoint;
- no dispatch/visible-thread/R1-R2-R3 material revived.

## 6. Open Review Questions

1. Whether to create `Docs/Workflows/documentation_governance.md` or merge
   extracted rules into `Docs/Workflows/tooling_assets_governance.md`.
2. Done: current window screenshot/action skills now live under
   `Docs/Skills/Desktop/`; old CoAgent skill copies are legacy fallback only.
3. Whether external learning notes should stay in `Docs/Cache/research/` or be
   compressed into `Docs/Index/external_learning_index.md`.
