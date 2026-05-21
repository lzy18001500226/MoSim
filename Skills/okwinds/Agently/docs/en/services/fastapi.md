---
title: FastAPI Service Exposure
description: Exposing agents, requests, and TriggerFlow executions over HTTP, SSE, and WebSocket.
keywords: Agently, FastAPI, HTTP, SSE, WebSocket, FastAPIHelper
---

# FastAPI Service Exposure

> Languages: **English** · [中文](../../cn/services/fastapi.md)

`FastAPIHelper` is a `FastAPI` subclass. It stores a `response_provider`, then exposes it with explicit route builders: `use_post(...)`, `use_get(...)`, `use_sse(...)`, and `use_websocket(...)`.

## Minimum

```python
from agently import Agently
from agently.integrations.fastapi import FastAPIHelper

agent = Agently.create_agent()

app = FastAPIHelper(response_provider=agent)
app.use_post("/chat")
```

Run with `uvicorn module:app`. The default POST body shape is:

```json
{
  "data": {
    "input": "hello"
  },
  "options": {}
}
```

Constructing `FastAPIHelper(...)` does not register any routes by itself; call `use_post`, `use_get`, `use_sse`, or `use_websocket` explicitly.

## Default response shape

Successful responses:

```json
{
  "status": 200,
  "data": <serialized response>,
  "msg": null
}
```

Errors:

```json
{
  "status": 422,
  "data": null,
  "msg": "...error message...",
  "error": { "type": "ValueError", "message": "...", "args": [...] }
}
```

| Exception | Default status |
|---|---|
| `ValueError` | 422 |
| `TimeoutError` | 504 |
| anything else | 400 |

The wrapper is JSON-safe — values pass through `fastapi.encoders.jsonable_encoder`.

## TriggerFlow executions

When the response provider is a `TriggerFlow`, the helper builds an execution per request and the response shape depends on what the close snapshot looks like:

```python
flow = TriggerFlow(name="answer")
# ... define chunks ...

app = FastAPIHelper(response_provider=flow)
```

`data` in the response carries the **close snapshot** as-is. Earlier versions tried to coerce TriggerFlow output into a single `result` field via the contract — that's no longer the case. If you want a specific shape, project from the snapshot in your own response wrapper:

```python
def project_snapshot(response_or_exception):
    if isinstance(response_or_exception, Exception):
        return {"status": 400, "data": None, "msg": str(response_or_exception)}
    snapshot = response_or_exception
    if isinstance(snapshot, dict):
        return {"status": 200, "data": {"answer": snapshot.get("answer")}, "msg": None}
    return {"status": 200, "data": snapshot, "msg": None}

app = FastAPIHelper(response_provider=flow, response_warper=project_snapshot)
app.use_post("/answer")
```

Once you provide a custom `response_warper`, both success and exception paths belong to that function; the default `{status, data, msg, error}` wrapper is no longer layered on top.

`contract.initial_input` and `contract.stream` continue to act as input and stream constraints. The close-snapshot-as-`data` change only affects the result side.

## Streaming responses

Generator functions and async generators wrap into a `StreamingResponse`:

```python
async def stream_answer(request_data):
    response = (
        agent
        .input(request_data["data"])
        .output({"title": (str, "Title", True), "body": (str, "Body", True)})
        .get_response()
    )
    async for item in response.get_async_generator(type="instant"):
        if item.is_complete:
            yield {"path": item.path, "value": item.value}

app = FastAPIHelper(response_provider=stream_answer)
app.use_sse("/answer/stream")
```

Each yielded item is JSON-encoded and sent as a streaming chunk. Pair with `text/event-stream` for SSE consumers; the helper handles framing.

## WebSocket

Register a WebSocket route with `.use_websocket("/ws")`. Connect, send a JSON message with `{"data": ..., "options": {...}}`, and receive streamed items back. Useful for chat UIs and any case where a single connection carries many turns.

See `examples/fastapi/...` in the repository for runnable WS samples.

## Custom request model

The helper accepts a request body of `{"data": <input>, "options": {...}}` by default. You can subclass or substitute the request body model if the agent expects a richer shape — see the source of [agently/integrations/fastapi.py](../../../agently/integrations/fastapi.py) for the protocols and ParamSpec it exposes.

## Reusable response_warper

The response wrapper is a single function with the signature:

```python
def my_warper(response_or_exception):
    ...
    return serializable_dict
```

It's called for both success values and exceptions. If you swap it out, you own both paths — there's no separate error wrapper.

## Recipes

| You want | Wire |
|---|---|
| One agent, one endpoint | `FastAPIHelper(response_provider=agent).use_post("/chat")` |
| Streaming structured fields to UI | wrap a generator that uses `get_async_generator(type="instant")` |
| Long-running flow with progress events | `response_provider=flow` and consume `get_async_runtime_stream(...)` from a custom generator |
| Strict response schema | provide a custom `response_warper` that validates and reshapes |

## See also

- [TriggerFlow Events and Streams](../triggerflow/events-and-streams.md) — the runtime stream you'd forward to SSE
- [Async First](../start/async-first.md) — when to use async getters in the wrapper
- [Action Runtime](../actions/action-runtime.md) — when the agent your endpoint wraps uses tools
