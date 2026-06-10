# CoAgent Operating Docs

This folder is the portable operating layer for the CoAgent agent OS.

Migration status: this folder currently contains both clean portable overview
files and conservative no-loss landing copies seeded from MoSim workflows on
2026-06-10. Treat `MIGRATION_MAP.md` as the authority on which files are fully
portable and which still contain MoSim adapter text. Do not slim or delete old
compatibility documents until the migration map records a deletion-to-landing
audit row.

Use it for rules that should move with `CoAgent/` into another project:

- organization and owner boundaries;
- visible-thread routing and dispatch contracts;
- patrol, recovery, failover, and dispatch SLO workflows;
- task graph, checkpoint, sub-agent, and review rules;
- tooling/native-surface governance that belongs to the agent OS;
- session-memory promotion rules that prevent chat history from becoming
  unreviewed project truth.

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
   ledger, sub-agent, long Git, or external-learning rules are needed
```

MoSim compatibility entrypoints may still live under `Docs/Workflows/`, but
they should point here for portable CoAgent OS rules.
