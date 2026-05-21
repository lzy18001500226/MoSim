---
title: AnthropicCompatible
description: The protocol-level plugin for Claude and Anthropic-compatible endpoints.
keywords: Agently, AnthropicCompatible, Claude, Anthropic, model
---

# AnthropicCompatible

> Languages: **English** · [中文](../../cn/models/anthropic-compatible.md)

`AnthropicCompatible` is the protocol-level plugin for Claude. It speaks Anthropic's Messages API — distinct enough from OpenAI Chat Completions that mapping it through `OpenAICompatible` would produce wrong configurations. Use this plugin when you point at `https://api.anthropic.com` or any Claude-compatible proxy.

## Settings

```python
from agently import Agently

Agently.set_settings("AnthropicCompatible", {
    "base_url": "https://api.anthropic.com",
    "api_key": "${ENV.ANTHROPIC_API_KEY}",
    "model": "${ENV.ANTHROPIC_MODEL}",
    "max_tokens": 4096,
})
```

| Key | Meaning |
|---|---|
| `base_url` | `https://api.anthropic.com` (or a proxy) |
| `api_key` | bearer token |
| `model` | Claude model id; use Anthropic's current model list when wiring it up |
| `max_tokens` | **required** by the Anthropic API; defaults sensibly but pin it for predictable cost |
| `anthropic_version` | API version header (defaults to a recent stable version) |
| `anthropic_beta` | optional beta-feature header (string or list of strings) |
| `request_options` | extra dict forwarded to the underlying HTTP client |

The class lives at [agently/builtins/plugins/ModelRequester/AnthropicCompatible.py](../../../agently/builtins/plugins/ModelRequester/AnthropicCompatible.py).

## Why a separate plugin

Claude differs from OpenAI in concrete ways the plugin handles:

- The request body uses a `system` field at the top level, not as a message in `messages`.
- `max_tokens` is mandatory.
- Headers include `anthropic-version` and (when applicable) `anthropic-beta`.
- The streaming event shape uses `message_start`, `content_block_delta`, `message_delta`, etc., not OpenAI's `chat.completion.chunk`.
- Tool calling has Anthropic's own request/response shape.

`AnthropicCompatible` directly implements `ModelRequester`. The request body construction and parsing are Anthropic-specific. Don't think of it as "OpenAI with a different URL" — it isn't.

## Per-agent overrides

Same pattern as any other plugin's settings:

```python
agent = Agently.create_agent()
agent.set_settings("AnthropicCompatible", {"model": "${ENV.ANTHROPIC_MODEL_FAST}"})
```

## Tool calling

`AnthropicCompatible` supports Claude's tool-use protocol natively. Tools registered via `@agent.action_func` / `agent.use_actions(...)` are exposed in the format Claude expects, and tool call results round-trip through the Messages API correctly.

## Streaming

`response.get_generator(type="delta")` / `get_async_generator(type="delta")` yields incremental text. `type="instant"` for structured streaming works the same way as on `OpenAICompatible` — the difference is purely upstream parsing.

## Beta features

If you need a beta feature (long context, custom tool variants, etc.), set `anthropic_beta`:

```python
Agently.set_settings("AnthropicCompatible", {
    "base_url": "https://api.anthropic.com",
    "api_key": "${ENV.ANTHROPIC_API_KEY}",
    "model": "${ENV.ANTHROPIC_MODEL}",
    "max_tokens": 4096,
    "anthropic_beta": "tools-2024-04-04",  # or a list
})
```

The header is forwarded as-is. Check Anthropic's current beta documentation for valid values.

## See also

- [Models Overview](overview.md) — protocol picking and the OpenAI vs Anthropic split
- [OpenAICompatible](openai-compatible.md) — the other protocol plugin
- [Action Runtime](../actions/action-runtime.md) — tool calling above the protocol layer
- [Model Setup](../start/model-setup.md) — quickstart-level walkthrough
