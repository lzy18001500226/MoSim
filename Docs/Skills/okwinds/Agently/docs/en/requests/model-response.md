---
title: Model Response
description: Reading text, structured data, metadata, and streaming events from one response.
keywords: Agently, response, get_response, get_data, get_text, get_meta, generator, streaming
---

# Model Response

> Languages: **English** · [中文](../../cn/requests/model-response.md)

`agent.input(...).start()` is a convenience that runs the request and returns the parsed dict. For everything more interesting — text, metadata, streaming, reuse — go through `get_response()`.

## Two consumption styles

```python
# Style A: one shot, return parsed data immediately
result = agent.input("...").output({...}).start()

# Style B: hold a reusable response
response = agent.input("...").output({...}).get_response()
text = response.result.get_text()
data = response.result.get_data()
meta = response.result.get_meta()
```

Style B is the default for non-trivial code. The actual model call runs lazily when you first consume from `response.result`, then results are **cached** — multiple reads do not re-issue the request.

## Reader methods

| Method | Returns |
|---|---|
| `response.result.get_text()` | full plain text |
| `response.result.get_data()` | parsed structured dict (when `output()` was used) |
| `response.result.get_data_object()` | Pydantic instance (when `output()` was given a `BaseModel`) |
| `response.result.get_meta()` | dict of usage / model info / timing |

Each has an async sibling: `async_get_text()`, `async_get_data()`, `async_get_data_object()`, `async_get_meta()`.

Mixing readers is fine — they all consume from the same cached result:

```python
response = agent.input("...").output({...}).get_response()
data = response.result.get_data()        # triggers the request
text = response.result.get_text()        # already cached
meta = response.result.get_meta()        # already cached
```

This is also how `.validate(...)` runs only once per response — the cached result is what gets validated.

## Streaming

`response.result.get_generator(type=...)` (sync) and `get_async_generator(type=...)` (async) yield streaming events. The `type` parameter selects what you see:

| `type` | What you get | Use it for |
|---|---|---|
| `"delta"` | raw token deltas | terminal-style typing UX |
| `"instant"` | structured nodes after each leaf finishes parsing | field-level UI updates |
| `"streaming_parse"` | the same node tree, updated in place as it grows | incremental dict reads |
| `"specific"` | `(event, data)` tuples filtered by event type (`delta`, `reasoning_delta`, `tool_calls`, etc.) | pick exactly the events you care about |
| `"original"` | raw provider events | debugging / passthrough |
| `"all"` | every event with type tag | exhaustive logging |

### Delta example

```python
gen = agent.input("Tell me a recursion story.").get_generator(type="delta")
for delta in gen:
    print(delta, end="", flush=True)
```

### Instant example (structured)

```python
gen = (
    agent.input("Give me a definition and three tips.")
    .output({
        "definition": (str, "Definition", True),
        "tips": [(str, "Tip", True)],
    })
    .get_generator(type="instant")
)
for item in gen:
    if item.is_complete:
        print(item.path, "=", item.value)
```

`item` exposes `.path` (e.g. `"tips[0]"`), `.wildcard_path` (`"tips[*]"`), `.value`, `.delta`, and `.is_complete`. Use `.is_complete` to react only when a leaf has fully parsed.

### Specific example (events)

```python
gen = agent.input("Hello.").get_generator(type="specific")
for event, data in gen:
    if event == "delta":
        print(data, end="", flush=True)
    elif event == "reasoning_delta":
        print("[reasoning]", data, end="", flush=True)
    elif event == "tool_calls":
        print("[tool call]", data)
```

## Async streaming

Same generators in async form:

```python
import asyncio

async def main():
    response = agent.input("...").output({...}).get_response()
    async for item in response.get_async_generator(type="instant"):
        if item.is_complete:
            print(item.path, item.value)

asyncio.run(main())
```

For services and TriggerFlow usage, async is the recommended path — see [Async First](../start/async-first.md).

## Concurrency

Because `get_response()` only kicks off the actual request when you consume it, you can build many responses up front and consume them in parallel:

```python
import asyncio

async def ask(prompt):
    r = agent.input(prompt).get_response()
    return await r.result.async_get_text()

results = await asyncio.gather(
    ask("Summarize recursion."),
    ask("Give one Python example."),
)
```

This is a standard async pattern; nothing in Agently is special about it.

## Don't re-issue when you can re-read

```python
# bad — runs the request three times
text = agent.input("...").start()
data = agent.input("...").output({...}).start()
meta = agent.input("...").output({...}).get_response().result.get_meta()

# good — runs once, reads three views
response = agent.input("...").output({...}).get_response()
text = response.result.get_text()
data = response.result.get_data()
meta = response.result.get_meta()
```

## See also

- [Async First](../start/async-first.md) — when to switch to `get_async_generator(...)`
- [Output Control](output-control.md) — what runs between "model returned" and "you read"
- [Schema as Prompt](schema-as-prompt.md) — what `output()` accepts
