---
title: Models Overview
description: How Agently organizes model providers behind three protocol-level requesters.
keywords: Agently, models, OpenAICompatible, AnthropicCompatible, providers
---

# Models Overview

Agently has three protocol-level request plugins, plus per-provider configuration recipes that select one of them.

## Layered view

```text
Application code
      │
      ▼
  ModelRequest  ──►  ModelResponse
      │
      ▼
ModelRequester plugin (the "protocol layer")
   ├── OpenAICompatible             ◄── most providers (Chat Completions)
   ├── OpenAIResponsesCompatible    ◄── Responses API variants
   └── AnthropicCompatible          ◄── Claude
      │
      ▼
HTTP to a model endpoint
```

The protocol plugin is what builds the HTTP request body and parses the wire response. Provider configuration is just a settings preset that targets one of these plugins.

## Why three plugins, not one

Earlier versions of the docs implied "every provider goes through `OpenAICompatible`". That is no longer accurate. `OpenAICompatible`, `OpenAIResponsesCompatible`, and `AnthropicCompatible` are separate requester plugins. Each one directly implements the `ModelRequester` protocol and owns its own protocol mapping. Anthropic in particular builds its own request bodies — `anthropic_version`, `anthropic_beta`, an explicit `max_tokens` requirement, and the `messages`/`system` field shape Claude expects. Those differences are real enough that lumping Claude under "OpenAICompatible" produces wrong configurations.

If you are pointing at `https://api.anthropic.com` (or a Claude-compatible proxy that speaks the same protocol), use [AnthropicCompatible](anthropic-compatible.md). For everything else (OpenAI, DeepSeek, Qwen, Ollama, Kimi, GLM, MiniMax, Doubao, SiliconFlow, Groq, ERNIE, Gemini's OpenAI-compat endpoint, plus any private gateway speaking the OpenAI Chat Completions API), use [OpenAICompatible](openai-compatible.md).

## Picking a plugin

| You're calling | Use plugin |
|---|---|
| OpenAI, Azure OpenAI, Gemini-via-OpenAI | `OpenAICompatible` |
| DeepSeek, Qwen, Kimi, GLM, MiniMax, Doubao, SiliconFlow, Groq, ERNIE | `OpenAICompatible` |
| Ollama or any other OpenAI-compatible local server | `OpenAICompatible` |
| Anthropic / Claude (native API) | `AnthropicCompatible` |
| A private gateway speaking the OpenAI Chat Completions API | `OpenAICompatible` |
| A private gateway speaking the OpenAI Responses API | `OpenAIResponsesCompatible` |
| A private gateway speaking the Anthropic Messages API | `AnthropicCompatible` |

## Minimal configuration

```python
from agently import Agently

# OpenAI-compatible
Agently.set_settings("OpenAICompatible", {
    "base_url": "https://api.openai.com/v1",
    "api_key": "${ENV.OPENAI_API_KEY}",
    "model": "${ENV.OPENAI_MODEL}",
})

# Or Anthropic
Agently.set_settings("AnthropicCompatible", {
    "base_url": "https://api.anthropic.com",
    "api_key": "${ENV.ANTHROPIC_API_KEY}",
    "model": "${ENV.ANTHROPIC_MODEL}",
    "max_tokens": 4096,
})
```

Per-provider recipes (env vars, common model names, base URLs) live in [Providers](providers/).

## Where the plugin code lives

- [agently/builtins/plugins/ModelRequester/OpenAICompatible.py](../../../agently/builtins/plugins/ModelRequester/OpenAICompatible.py)
- [agently/builtins/plugins/ModelRequester/OpenAIResponsesCompatible.py](../../../agently/builtins/plugins/ModelRequester/OpenAIResponsesCompatible.py)
- [agently/builtins/plugins/ModelRequester/AnthropicCompatible.py](../../../agently/builtins/plugins/ModelRequester/AnthropicCompatible.py)

If a provider is missing or speaks an incompatible protocol, you can add a new requester plugin — but in practice almost every commercial endpoint either ships an OpenAI-compatible mode, a Responses-style mode, or matches Anthropic's protocol, so these built-ins cover most cases.

## See also

- [OpenAICompatible details](openai-compatible.md)
- [AnthropicCompatible details](anthropic-compatible.md)
- [Providers](providers/) — per-provider recipes
- [Model Setup](../start/model-setup.md) — quickstart-level setup
- [Settings](../start/settings.md) — env placeholders and hierarchy
