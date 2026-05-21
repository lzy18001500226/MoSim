---
title: Requests Overview
description: How a single Agently request is shaped, sent, and consumed.
keywords: Agently, request, agent, response, output, validate, session
---

# Requests Overview

> Languages: **English** · [中文](../../cn/requests/overview.md)

A single Agently request has four moving parts:

1. **Prompt** — what you say to the model. Built from layered slots: `role` / `system`, `info`, `instruct`, `input`, `output` schema. See [Prompt Management](prompt-management.md).
2. **Output schema** — the structure you want back. Authored as nested dicts of `(type, "desc", ensure)` leaves. See [Schema as Prompt](schema-as-prompt.md).
3. **Validation pipeline** — `output()` strict parse → `ensure_keys` → `.validate(...)` custom handlers → retry. See [Output Control](output-control.md).
4. **Response** — text, structured data, metadata, and streaming events. Reusable via `response.result`. See [Model Response](model-response.md).

## The minimum shape

```python
from agently import Agently

agent = Agently.create_agent()

result = (
    agent
    .input("Summarize this article in three bullets.")
    .output({
        "title": (str, "Title", True),
        "bullets": [(str, "Bullet point", True)],
    })
    .start()
)
```

This single chain covers all four parts. `input()` fills the prompt's input slot, `output()` defines the schema (with `ensure` flags), and `start()` runs the request, applies the validation pipeline, retries if needed, and returns the parsed dict.

## When to reach for which page

| You want to … | Read |
|---|---|
| Layer prompts across the agent and one request | [Prompt Management](prompt-management.md) |
| Understand the `(type, "desc", True)` leaf and YAML form | [Schema as Prompt](schema-as-prompt.md) |
| Add custom business validation, control retries, fail open or hard | [Output Control](output-control.md) |
| Reuse one response for text + data + metadata, or stream fields | [Model Response](model-response.md) |
| Carry chat history and memo across turns | [Session Memory](session-memory.md) |
| Inject background information cleanly | [Context Engineering](context-engineering.md) |

## Sync vs async

The chain above is sync because it ends in `.start()`. For services and streaming UI, use `.async_start()` or pull a reusable `response = ....get_response()` and consume it with `await response.result.async_get_data()`. See [Async First](../start/async-first.md).

## Where this fits in the stack

A request is the smallest unit Agently ships. Multiple requests can share a Session (multi-turn). When you need branching, concurrency, or pause/resume across requests, you graduate to [TriggerFlow](../triggerflow/overview.md). When you need the model to call out to tools or MCP servers, you wire in [Action Runtime](../actions/action-runtime.md).

But every layer above eventually lives or dies on the request layer doing its job. Get this layer right first.
