---
title: MCP
description: Calling MCP servers from an Agently agent.
keywords: Agently, MCP, Model Context Protocol, use_mcp, MCPActionExecutor
---

# MCP

> Languages: **English** · [中文](../../cn/actions/mcp.md)

MCP (Model Context Protocol) is a protocol for hosted servers that expose tools to AI agents. Agently wires MCP servers into the action runtime via `MCPActionExecutor` so the model sees MCP tools and your own `@agent.action_func` actions through the same interface.

## Minimal example

```python
import os
import asyncio
from dotenv import load_dotenv, find_dotenv
from agently import Agently

load_dotenv(find_dotenv())

Agently.set_settings("OpenAICompatible", {
    "base_url": "${ENV.OPENAI_BASE_URL}",
    "api_key": "${ENV.OPENAI_API_KEY}",
    "model": "${ENV.OPENAI_MODEL}",
})

agent = Agently.create_agent()


async def main():
    result = (
        await agent.use_mcp(f"https://mcp.amap.com/mcp?key={os.environ.get('AMAP_API_KEY')}")
        .input("What's the weather like in Shanghai today?")
        .async_start()
    )
    print(result)


asyncio.run(main())
```

`use_mcp(url)` registers all tools the MCP server exposes. The agent then plans tool calls against the union of {`@agent.action_func`, `use_tool`, `use_mcp` tools} as if they were one set.

## API

| Method | Behavior |
|---|---|
| `await agent.use_mcp(url)` | connect to the server, list tools, register them; returns the agent for chaining |
| `await agent.use_mcp(url, headers={...})` | with custom HTTP headers (auth tokens, etc.) |

The exact signature matches whatever the active `MCPActionExecutor` plugin expects — for the default executor, a URL plus optional headers covers the common case.

## Mixing MCP with custom actions

```python
@agent.action_func
async def lookup_internal(id: str):
    """Look up a record in the internal database."""
    ...


await agent.use_mcp("https://example-mcp/server")
agent.use_actions(lookup_internal)

# The model now sees MCP tools + lookup_internal in the same plan
result = await agent.input(question).async_start()
```

There's no precedence between MCP-provided tools and locally-defined actions. The model picks based on names, descriptions, and the prompt context.

## Inspecting what was called

After a request, see what tools the model actually invoked:

```python
records = agent.get_action_result()
for r in records:
    print(r)
```

Action records are also written to `extra.action_logs` (or `extra.tool_logs` on the compat surface).

## Common pitfalls

- **Forgetting `await`**: `use_mcp(...)` is async because it lists tools from the server. Forgetting `await` returns a coroutine and the registration silently doesn't happen.
- **Passing secrets in URLs**: prefer headers and env vars. URL query params end up in logs.
- **Treating MCP as identical to local actions**: hosted MCP servers can be slow or rate-limited. For latency-sensitive or high-volume calls, prefer local action functions.

## See also

- [Action Runtime](action-runtime.md) — `MCPActionExecutor` is one of the bundled executors
- [Tools](tools.md) — `use_mcp(...)` is the same on the compat surface
