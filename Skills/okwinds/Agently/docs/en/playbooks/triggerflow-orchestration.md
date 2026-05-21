---
title: TriggerFlow Orchestration Playbook
description: A structural template for multi-step AI processes with branching, fan-out, persistence.
keywords: Agently, TriggerFlow, orchestration, playbook, fan-out, persistence
---

# TriggerFlow Orchestration Playbook

> Languages: **English** · [中文](../../cn/playbooks/triggerflow-orchestration.md)

## When to use this playbook

You have a process with three or more discrete stages. At least one of these is true:

- Branching depends on intermediate model output.
- You need to fan out (process N items in parallel) and then collect.
- A human or external system has to approve / supply input mid-flow.
- The process can take long enough that you need to survive a process restart.
- You want to stream progress events to a UI as the process runs.

If none of those apply, stay in the request layer — see [Quickstart](../start/quickstart.md) and [Output Control](../requests/output-control.md).

## Recommended structure

```text
Application
   │
   ▼
TriggerFlow definition  (one Python module per flow)
   ├── prepare         ← validate / normalize input
   ├── classify        ← model call: route by type
   ├── (branch on classification)
   │     ├── handle_A → … → finalize
   │     ├── handle_B → … → finalize
   │     └── handle_C → … → finalize
   ├── for_each items  ← if a list comes back from any handler, fan out
   ├── pause_for(...)  ← optional human approval
   └── finalize        ← write final state, push to runtime stream

Outside the flow:
   • create_execution(auto_close=False, runtime_resources={...})
   • async_start(...)
   • consume runtime stream for live UI
   • async_close() → close snapshot for the API response
```

## Skeleton

```python
from agently import TriggerFlow, TriggerFlowRuntimeData


def build_flow():
    flow = TriggerFlow(name="orchestration")

    async def prepare(data: TriggerFlowRuntimeData):
        # validate / normalize input
        await data.async_set_state("input", data.input)
        return data.input

    async def classify(data: TriggerFlowRuntimeData):
        agent = data.require_resource("agent")
        return await agent.input(data.input).output({
            "category": (str, "Category", True),
        }).async_start()

    async def handle_default(data: TriggerFlowRuntimeData):
        # ...
        await data.async_set_state("answer", "...")

    (
        flow.to(prepare)
            .to(classify)
            .match()
                .case("A").to(handle_default)
                .case("B").to(handle_default)
                .case_else().to(handle_default)
            .end_match()
    )

    return flow


async def run(input_value, agent):
    flow = build_flow()
    execution = flow.create_execution(
        auto_close=False,
        runtime_resources={"agent": agent},
    )
    await execution.async_start(input_value)
    return await execution.async_close()
```

A few choices baked into this skeleton:

- **`auto_close=False`** — the application controls close explicitly. Use this whenever you might want to consume runtime stream items or pause for external input.
- **Agent injected as runtime resource** — the agent isn't in `state` (it's a live object) and isn't in `flow_data` (which is shared and risky). See [State and Resources](../triggerflow/state-and-resources.md).
- **`match()` over classification result** — discrete categories use `match`; predicate branches use `if_condition`.
- **Each handler reads `data.input` and writes to state** — handlers should be small and have one job each.

## Variations

### Need to fan out

Replace a single handler with a `for_each`:

```python
async def list_subtasks(data):
    return data.input["subtasks"]   # a list

async def handle_one(data):
    return await some_agent.input(data.input).async_start()

(
    flow.to(list_subtasks)
        .for_each(concurrency=4)
            .to(handle_one)
        .end_for_each()
        .to(collect)
)
```

See [Patterns](../triggerflow/patterns.md) for `batch`, `for_each`, and concurrency caps.

### Need human approval

Add a `pause_for` step. The execution must be created with `auto_close=False`; resume with `continue_with` and an explicit `resume_to` target.

```python
async def ask(data):
    return await data.async_pause_for(
        type="approval",
        payload={"summary": data.input["summary"]},
        resume_to="next",
    )
```

See [Pause and Resume](../triggerflow/pause-and-resume.md).

### Need to survive a restart

Save the execution state at meaningful checkpoints (typically when a `pause_for` is outstanding), persist the result somewhere durable, and restore by `flow.create_execution(...).load(saved)`.

```python
saved = execution.save()
db.put(execution_id, saved)

# later, possibly in a different process:
restored = flow.create_execution(auto_close=False, runtime_resources={...})
restored.load(db.get(execution_id))
```

Re-inject runtime resources on the restore side. See [Persistence and Blueprint](../triggerflow/persistence-and-blueprint.md).

### Need a streaming UI

Consume `execution.get_async_runtime_stream(...)` from a FastAPI or WebSocket handler. Have your chunks push items via `data.async_put_into_stream(...)`. See [FastAPI Service Exposure](../services/fastapi.md) and [Events and Streams](../triggerflow/events-and-streams.md).

## What to skip

- Don't reach for sub-flows just to organize code. Inline shorter handlers; only use sub-flow when the child has a real reusable contract — see [Sub-Flow](../triggerflow/sub-flow.md).
- Don't wrap the agent call in extra retries inside chunks — `.start()` already retries via the validation pipeline. See [Output Control](../requests/output-control.md).
- Don't store live clients in `state`. Use `runtime_resources` and re-inject on `load()`.

## Cross-links

- [TriggerFlow Lifecycle](../triggerflow/lifecycle.md) — `auto_close` and the five entry APIs
- [TriggerFlow Patterns](../triggerflow/patterns.md) — branching, fan-out, loops
- [Model Integration](../triggerflow/model-integration.md) — calling agents from inside chunks
- [Action Runtime](../actions/action-runtime.md) — when chunks need tools or MCP
