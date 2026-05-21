---
title: Model Integration
description: Calling agents and model requests from inside TriggerFlow chunks.
keywords: Agently, TriggerFlow, agent, model, request, async, instant
---

# Model Integration

> Languages: **English** · [中文](../../cn/triggerflow/model-integration.md)

A chunk handler is a regular async function. You can call any agent, request, or response API inside it. The good patterns concentrate on three things: async (because the surrounding flow is async), structured output (because the next chunk expects a known shape), and streaming when the user actually benefits.

## Minimal pattern

```python
from agently import Agently, TriggerFlow, TriggerFlowRuntimeData

agent = Agently.create_agent()


async def classify(data: TriggerFlowRuntimeData):
    result = await (
        agent
        .input(data.input)
        .output({
            "category": (str, "Category", True),
            "confidence": (float, "0.0 to 1.0"),
        })
        .async_start()
    )
    await data.async_set_state("classification", result)
    return result


flow = TriggerFlow(name="classify")
flow.to(classify)
```

The agent is created at module scope so it's reused across executions. `await ... async_start()` returns the parsed dict. The dict goes into state for the close snapshot, and is also returned so the next chunk receives it as `data.input`.

## Use async, always

The surrounding flow is async. Calling sync `start()` inside a chunk works but blocks the event loop while the model request is in flight, hurting concurrency. Use `async_start()` / `async_get_data()` / `get_async_generator(...)`. See [Async First](../start/async-first.md).

## Streaming structured fields into the runtime stream

When the UI consuming the runtime stream benefits from incremental updates, push completed structured fields out as they arrive:

```python
async def draft_with_streaming(data: TriggerFlowRuntimeData):
    response = (
        agent
        .input(data.input)
        .output({
            "title": (str, "Title", True),
            "body": (str, "Body", True),
        })
        .get_response()
    )

    async for item in response.get_async_generator(type="instant"):
        if item.is_complete:
            await data.async_put_into_stream({"path": item.path, "value": item.value})

    final = await response.async_get_data()
    await data.async_set_state("draft", final)
    return final
```

`type="instant"` yields per-leaf events as each field finishes parsing — the consumer of the runtime stream sees `title` complete before `body` is done. After the stream ends, `async_get_data()` returns the cached parsed dict (no second request).

## Reusing one response across the chunk

Call `get_response()` once, then read text + data + meta from `response.result` without re-issuing. See [Model Response](../requests/model-response.md):

```python
async def step(data):
    response = agent.input(data.input).output({...}).get_response()
    text = await response.result.async_get_text()
    obj = await response.result.async_get_data()
    meta = await response.result.async_get_meta()
    await data.async_set_state("text", text)
    await data.async_set_state("obj", obj)
    await data.async_set_state("meta", meta)
```

## Per-execution agent customization

If the flow's chunks need different model configuration per execution, inject the configured agent via runtime resources:

```python
execution = flow.create_execution(
    runtime_resources={"agent": Agently.create_agent().set_settings(...)},
)


async def step(data):
    agent = data.require_resource("agent")
    return await agent.input(data.input).async_start()
```

Don't put the agent in `state` — agents hold network clients and aren't snapshot-friendly. Use `runtime_resources` (see [State and Resources](state-and-resources.md)).

## Validation, retries, and structured output

`.validate(...)` and `ensure_keys` work the same way inside a chunk as they do at the request layer. The retry budget is per-request, so a chunk that needs to retry the model call doesn't affect the rest of the flow. See [Output Control](../requests/output-control.md).

```python
async def step(data):
    return await (
        agent
        .input(data.input)
        .output({"answer": (str, "answer", True)})
        .validate(custom_business_check)
        .async_start(max_retries=5)
    )
```

## Don't put model state in flow_data

`flow_data` is shared across all executions of the flow and emits a warning. Don't use it to "remember the last model answer" — use `state` for execution-local memory, or a real session if it's a multi-turn conversation. See [Session Memory](../requests/session-memory.md).

## Multi-agent inside one flow

Multiple chunks can use multiple agents — different model providers, different prompt configurations, different tool sets:

```python
classifier = Agently.create_agent().set_settings("OpenAICompatible", {"model": "${ENV.CLASSIFIER_MODEL}"})
writer = Agently.create_agent().set_settings("OpenAICompatible", {"model": "${ENV.WRITER_MODEL}"})

async def classify(data):
    return await classifier.input(data.input).output({...}).async_start()

async def draft(data):
    return await writer.input(data.input).async_start()

flow.to(classify).to(draft)
```

This is how TriggerFlow plays the orchestration role: the flow keeps the wiring; each agent stays a small, focused unit.

## See also

- [Async First](../start/async-first.md) — why every chunk should use async APIs
- [Model Response](../requests/model-response.md) — `get_response()` and the `result` cache
- [Output Control](../requests/output-control.md) — validate / retry behavior inside a chunk
- [State and Resources](state-and-resources.md) — where the agent should live
