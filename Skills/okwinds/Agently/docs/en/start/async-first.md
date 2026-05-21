---
title: Async First
description: When async is the default path, and which APIs to reach for.
keywords: Agently, async, async_get, get_async_generator, async_start
---

# Async First

Agently is async-native at the runtime layer. Sync methods are convenience wrappers generated from the async ones via `FunctionShifter.syncify()`. For real services, async should be the default path.

## When sync is fine

- One-off scripts, notebooks, teaching demos.
- Code that doesn't share an event loop with anything else.

## When async is the default

- Inside FastAPI, ASGI workers, SSE / WebSocket handlers, or any code already running in `asyncio`.
- Streaming UI where you want to react to fields as they complete instead of waiting for the full response.
- Combining model output with TriggerFlow events, runtime stream, or external pubsub.

## Recommended pairing

The combination worth learning first:

- `response.get_async_generator(type="instant")` — yields completed structured nodes (not raw tokens).
- `data.async_emit(...)` — turns nodes into TriggerFlow signals.
- `data.async_put_into_stream(...)` — forwards intermediate state to UI / SSE / logs.

`instant` events are field-level: each item arrives only after its leaf has fully parsed, so downstream code never sees a half-string.

## API surface map

| Sync | Async equivalent |
|---|---|
| `agent.start()` / `request.start()` | `agent.async_start()` / `request.async_start()` |
| `response.get_data()` | `response.async_get_data()` |
| `response.get_text()` | `response.async_get_text()` |
| `response.get_meta()` | `response.async_get_meta()` |
| `response.get_generator(type=...)` | `response.get_async_generator(type=...)` |
| `flow.start()` | `flow.async_start()` |
| `execution.start()` / `execution.close()` | `execution.async_start()` / `execution.async_close()` |
| `data.set_state(...)` / `data.emit(...)` | `data.async_set_state(...)` / `data.async_emit(...)` |

## Minimal async example

```python
import asyncio
from agently import Agently

agent = Agently.create_agent()


async def main():
    response = (
        agent
        .input("Give me a title and two bullets.")
        .output({
            "title": (str, "Title", True),
            "items": [(str, "Bullet point", True)],
        })
        .get_response()
    )

    async for item in response.get_async_generator(type="instant"):
        if item.is_complete:
            print(item.path, item.value)

    final = await response.async_get_data()
    print(final)


asyncio.run(main())
```

`get_response()` returns a reusable `ModelResponse`. You can pull text, structured data, and metadata from the same response without re-issuing the request — see [Model Response](../requests/model-response.md).

## Async + TriggerFlow

For event-driven orchestration, prefer:

- `flow.async_start(...)` for hidden execution sugar (returns the close snapshot).
- `flow.async_start_execution(...)` for explicit, long-lived executions you want to control yourself.
- `data.async_emit(...)` and `data.async_put_into_stream(...)` inside chunks.

See [TriggerFlow Lifecycle](../triggerflow/lifecycle.md).

## Don't oversell async

Async First improves concurrency, service composition, and progressive UX. It does **not** make a single isolated model request faster. The wall-clock latency of one request is bounded by the model, not by sync vs async.
