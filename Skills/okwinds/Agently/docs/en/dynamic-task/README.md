# Dynamic Task

Dynamic Task is a first-class Agently task surface for model-generated or
app-generated DAGs. It exposes a compact app-facing API, validates a `TaskDAG`,
resolves task handlers, and compiles the graph to ordinary TriggerFlow
execution as an implementation substrate.

```python
task = Agently.create_dynamic_task(target="review policy")
result = await task.async_start()
```

When the caller already has a plan, pass the `TaskDAG` directly and skip model
planning:

```python
async def local_handler(context):
    return {
        "task_id": context.task.id,
        "deps": dict(context.dependency_results),
    }

task = Agently.create_dynamic_task(
    target="review policy",
    plan={
        "graph_id": "review",
        "task_schema_version": "task_dag/v1",
        "tasks": [
            {"id": "extract", "kind": "local", "binding": "local_handler"},
            {
                "id": "final",
                "kind": "local",
                "binding": "local_handler",
                "depends_on": ["extract"],
            },
        ],
        "semantic_outputs": {"final": "final"},
    },
    handlers={"local_handler": local_handler},
)
snapshot = await task.async_start(timeout=10)
```

Agent instances expose the same facade:

```python
task = agent.create_dynamic_task(target="review policy")
```

For model tasks, use Agently's request output pipeline instead of parsing model
text in handlers or examples. `output_schema` applies to semantic output model
tasks; node-level `inputs.output_schema` can override it for a specific model
task.

```python
task = Agently.create_dynamic_task(
    target="write an incident briefing",
    output_schema={
        "brief": (str, "customer-facing briefing", True),
        "next_update": (str, "next update timing", True),
    },
)
snapshot = await task.async_start(timeout=120)
_, output = next(iter(snapshot["semantic_outputs"].items()))
brief = output["result"]["brief"]
```

## Architecture

Dynamic Task is split into four stages:

- `AgentlyTaskDAGPlanner` generates deterministic `TaskDAG` data with Agently
  output schema, `ensure_keys`, and validation retry.
- `TaskDAGValidator` validates DAG syntax, dependencies, schema version,
  semantic outputs, side-effect policy, and resolver availability.
- `DynamicTaskResolver` maps `task.binding`, `task.id`, then `task.kind` to a
  runnable handler.
- `TaskDAGExecutor` compiles the validated DAG to ordinary TriggerFlow chunks
  and runs it through TriggerFlow lifecycle, stream, pause/resume, result, and
  runtime resource mechanics.

`bindings` is not part of the public facade. Use `handlers` for custom local
functions. Use explicit resource slots such as `planner`, `model`, `actions`,
and `skills` when a task may use them; `actions` and `skills` are not exposed to
the planner unless passed by the caller.

## Resolver Semantics

Custom handlers should use clear names ending in `_handler`:

```python
task = Agently.create_dynamic_task(
    target="review policy",
    plan=task_dag,
    handlers={"risk_check_handler": risk_check_handler},
)
```

In the DAG:

```python
{"id": "check_risk", "kind": "local", "binding": "risk_check_handler"}
```

Unknown optional handlers may be safely pruned by the validator when they do not
affect required semantic outputs, required downstream nodes, approvals, or
side-effect policy. Pruned nodes are recorded in `diagnostics`; unknown required
handlers fail closed before execution.

## Lower-Level Control

Use the low-level classes only when a framework integration needs staged
control:

```python
from agently.builtins.plugins import AgentlyTaskDAGPlanner
from agently.core import DynamicTaskResolver, TaskDAGExecutor, TaskDAGValidator

resolver = DynamicTaskResolver({"risk_check_handler": risk_check_handler})
validator = TaskDAGValidator(resolver)
planner = AgentlyTaskDAGPlanner(validator=validator)

graph = await planner.async_plan(planner_agent, {"target": "review policy"})
validation = validator.validate(graph, strict_schema_version=True)
snapshot = await TaskDAGExecutor(resolver, validator=validator).async_run(graph)
```

The executor does not depend on Agent. Model and action access belong to the
facade or resolver adapters, while TriggerFlow remains the execution substrate
under Dynamic Task rather than the owner API.

## Examples

Use the examples in `examples/dynamic_task/` by layer:

- `01_dynamic_task_basic.py`: submitted `TaskDAG` smoke example with local
  handlers only.
- `02_support_response_module_model.py`: model-powered support module with a
  simple `SupportResponseModule.respond(ticket)` facade, backend fan-out/join
  stages, structured model outputs, mocked business-system lookups, and a
  printed customer-facing response.
- `03_contract_risk_review_business.py`: contract risk review business example
  with a simple `ContractRiskReviewService.review(contract)` facade,
  deterministic local handlers, backend risk scoring, and a printed risk memo.
- `04_incident_briefing_auto_plan.py`: auto-planned incident briefing example
  with a simple `IncidentBriefingService.brief(report)` facade. The model
  creates the `TaskDAG`; Dynamic Task validates and executes it, while the
  frontstage briefing shape is enforced through Agently `output_schema`.
- `05_enterprise_renewal_complex_auto_plan.py`: complex auto-planned renewal
  example where the model planner creates several independent analysis roots,
  joins them into a synthesis stage, and produces a structured recovery package.
