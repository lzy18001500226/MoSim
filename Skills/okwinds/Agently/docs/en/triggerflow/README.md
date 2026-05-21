# TriggerFlow

Suggested reading order:

1. [Overview](overview.md): boundaries, mental model, and a minimal flow.
2. [Lifecycle](lifecycle.md): open / sealed / closed, and start / close entrypoints.
3. [State and Resources](state-and-resources.md): choosing state, flow_data, and runtime_resources.
4. [Events and Streams](events-and-streams.md): `emit` / `when` and runtime stream.
5. [Patterns](patterns.md): branching, match, batch, for_each, event-driven loops.
6. [Sub-Flow](sub-flow.md): parent-child flow composition.
7. [Persistence and Blueprint](persistence-and-blueprint.md): save/load and definition export.
8. [Pause and Resume](pause-and-resume.md): human intervention and external resume.
9. [Runtime Intervention](runtime-intervention.md): adding supplemental context without pausing or mutating the graph.
10. [Model Integration](model-integration.md): calling agents / requests inside chunks.
11. [Execution Result](execution-result.md): reading snapshots, state, compatibility results, interventions, and metadata.
12. [Compatibility](compatibility.md): migrating old `.end()`, `set_result()`, and `runtime_data`.

Dynamic Task is documented separately as an application-level facade:
[Dynamic Task](../dynamic-task/). It uses TriggerFlow as the execution
substrate, but ordinary users should start from `Agently.create_dynamic_task(...)`.
