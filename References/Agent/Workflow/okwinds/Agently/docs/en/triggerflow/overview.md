---
title: TriggerFlow Overview
description: What TriggerFlow is, when you should reach for it, and how it relates to single requests and the action runtime.
keywords: Agently, TriggerFlow, workflow, orchestration, durable execution
---

# TriggerFlow Overview

> Languages: **English** · [中文](../../cn/triggerflow/overview.md)

TriggerFlow is Agently's orchestration layer. It owns:

- branching (`if/elif/else`, `match/case`)
- concurrency (`batch`, `for_each`)
- event-driven branches (`when(...)`)
- runtime stream (live items emitted to consumers)
- pause / resume (human-in-the-loop, external events)
- save / load (durable execution across restarts)
- sub-flow composition

It sits **above** the action runtime — your flow can call agents, tools, MCP servers, or anything else inside its handlers. It sits **below** your application code — the application decides which flow to run and what to pass in.

## When to use it

| You have | Use |
|---|---|
| One model call (with retries / validation) | a request, not a flow |
| Linear pipeline of 2–3 steps with no fan-out | sometimes a flow is overkill; consider plain async |
| Branches based on intermediate results | TriggerFlow `if_condition` or `match` |
| Concurrency across N inputs | TriggerFlow `for_each` / `batch` |
| Long-running with human approval | TriggerFlow `pause_for` |
| Needs to survive process restart | TriggerFlow `save` / `load` |
| Live event stream to UI / SSE | TriggerFlow runtime stream |

If none of the right column applies, stay in the request layer.

Dynamic Task is a separate first-class Agently surface for model-generated or
app-generated DAG data. Use `Agently.create_dynamic_task(...)` when the plan
itself must be planned, validated, pruned, and executed. Dynamic Task uses
TriggerFlow as its execution substrate, but it is not a TriggerFlow sub-API.
See [Dynamic Task](../dynamic-task/README.md).

## Mental model

```text
┌──────────────────────────────────────┐
│ application code                     │
│   create execution → start → close   │
└────────────────┬─────────────────────┘
                 │
   ┌─────────────▼──────────────┐
   │  TriggerFlow execution     │
   │  open → sealed → closed    │
   │   • state (snapshot)       │
   │   • runtime_resources      │  ◄── live objects you inject
   │   • runtime stream         │  ◄── items chunks emit
   │   • pending interrupts     │
   └─────────────┬──────────────┘
                 │
   chunks (async functions you write) call agents, tools,
   external APIs, then update state and/or emit events
```

A `TriggerFlow` object is the **definition** — the chain of handlers and branches. An `execution` is one **run** of that definition. You can have many concurrent executions of the same flow.

## Hello flow

```python
import asyncio
from agently import TriggerFlow, TriggerFlowRuntimeData


async def hello():
    flow = TriggerFlow(name="hello")

    async def greet(data: TriggerFlowRuntimeData):
        await data.async_set_state("greeting", f"Hello, {data.input}!")

    flow.to(greet)

    execution = flow.create_execution()
    await execution.async_start("World")
    snapshot = await execution.async_close()
    print(snapshot["greeting"])  # Hello, World!


asyncio.run(hello())
```

What happened:

1. `TriggerFlow(name=...)` defines a flow.
2. `flow.to(greet)` chains a handler. The handler receives `data: TriggerFlowRuntimeData` with `data.input` (= the value passed to `start()`).
3. `flow.create_execution()` makes one runnable execution.
4. `async_start("World")` starts it; `async_close()` waits for everything to drain and returns the close snapshot — a dict of all state set by handlers.

## Hidden execution sugar

When you don't need to control the execution explicitly, `flow.start(...)` / `flow.async_start(...)` create a temporary execution, run it to close, and return the snapshot:

```python
snapshot = await flow.async_start("World")
print(snapshot["greeting"])
```

Use this for scripts. Don't use it when the flow pauses for human input or expects external events — see [Lifecycle](lifecycle.md).

## What chunks can do

Inside a chunk handler, `data` exposes:

| API | Purpose |
|---|---|
| `data.input` | the value flowing in (start input, or previous chunk's return) |
| `data.async_set_state(key, value)` / `get_state(key)` | execution-local serializable state |
| `data.async_emit(event, payload)` | trigger `when(event)` branches |
| `data.async_put_into_stream(item)` | push to runtime stream |
| `data.async_pause_for(type=..., resume_to=...)` | pause for external graph resumption |
| `data.require_resource(name)` | fetch a live object you injected |
| `return value` | becomes the next chunk's `data.input` |

The full vocabulary lives in the rest of this section.

## Where to read next

- [Lifecycle](lifecycle.md) — open/sealed/closed states and the five entry APIs
- [State and Resources](state-and-resources.md) — three storage layers and which to use
- [Events and Streams](events-and-streams.md) — `emit`, `when`, runtime stream
- [Patterns](patterns.md) — branches, loops, batches, fan-out
- [Sub-Flow](sub-flow.md) — composing flows
- [Persistence and Blueprint](persistence-and-blueprint.md) — save/load and config export
- [Pause and Resume](pause-and-resume.md) — human-in-the-loop
- [Model Integration](model-integration.md) — calling agents from inside chunks
- [Compatibility](compatibility.md) — migrating off `.end()`, `set_result()`, `wait_for_result=`, old `runtime_data`
