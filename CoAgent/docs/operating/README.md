# CoAgent Operating Docs

This folder is the portable operating layer for the CoAgent agent OS.

Migration status: the operating files in this folder are split-audited
portable cores as of 2026-06-10. Treat `MIGRATION_MAP.md` as the authority on
the host landing for any MoSim-specific text that was removed from the portable
core. Do not slim or delete old compatibility documents until the migration map
records a deletion-to-landing audit row.

Current split-audited portable cores:

```text
CoAgent/docs/operating/agent_os_operating_model.md
CoAgent/docs/operating/org_operating_model.md
CoAgent/docs/operating/coagent_ops_patrol_workflow.md
CoAgent/docs/operating/agent_orchestration.md
CoAgent/docs/operating/coagent_meta_maintenance.md
CoAgent/docs/operating/tooling_assets_governance.md
CoAgent/docs/operating/session_memory_migration.md
CoAgent/docs/operating/context_documentation_governance.md
CoAgent/docs/operating/project_bootstrap.md
```

Use it for rules that should move with `CoAgent/` into another project:

- organization and owner boundaries;
- visible-thread routing and dispatch contracts;
- patrol, recovery, failover, and dispatch SLO workflows;
- task graph, checkpoint, sub-agent, and review rules;
- tooling/native-surface governance that belongs to the agent OS;
- session-memory promotion rules that prevent chat history from becoming
  unreviewed project truth;
- context/documentation governance, including the documentation-secretary
  boundary and no-loss doc migration rule;
- new host-project CoAgent adapter bootstrapping, while keeping reusable core
  capability separate from project-local state.

Keep project-local application workflows outside this folder. For MoSim,
MWORKS/ROS2/UE engineering workflows, PMO board state, active ledgers, packet
evidence, and competition-specific technical directions remain under
`Docs/Workflows/`, `Docs/Design/`, `Results/`, and other MoSim project folders.

## Reading Order

For CoAgent operating-system work, read:

```text
1. CoAgent/docs/operating/agent_os_operating_model.md
2. CoAgent/docs/operating/org_operating_model.md
3. CoAgent/dispatch/communication_contract.md
4. CoAgent/docs/operating/coagent_ops_patrol_workflow.md
5. CoAgent/docs/operating/agent_orchestration.md only when full task graph,
   queue, delegation, checkpoint, review, or resume rules are needed
6. CoAgent/docs/operating/tooling_assets_governance.md when tool, skill,
   MCP/plugin, hook, checker, or capability routing is involved
7. CoAgent/docs/operating/context_documentation_governance.md when context
   authority, documentation-secretary, memory, or no-loss migration boundaries
   are involved
8. CoAgent/docs/operating/session_memory_migration.md when old conversation
   memory may influence current project truth
9. CoAgent/docs/operating/project_bootstrap.md when creating or auditing a
   new host project's `CoAgent/` adapter scaffold
```

MoSim compatibility entrypoints may still live under `Docs/Workflows/`, but
they should point here for portable CoAgent OS rules.
