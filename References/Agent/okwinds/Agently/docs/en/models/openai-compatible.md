---
title: OpenAICompatible
description: The protocol-level plugin used for OpenAI and every provider that speaks the same API.
keywords: Agently, OpenAICompatible, OpenAI, DeepSeek, Qwen, Ollama, model
---

# OpenAICompatible

> Languages: **English** · [中文](../../cn/models/openai-compatible.md)

`OpenAICompatible` is one of the three protocol-level model request plugins (see [Models Overview](overview.md)). It handles any endpoint that speaks the OpenAI Chat Completions API — which today covers most commercial providers and most local model servers.

## Settings

```python
from agently import Agently

Agently.set_settings("OpenAICompatible", {
    "base_url": "https://api.openai.com/v1",
    "api_key": "${ENV.OPENAI_API_KEY}",
    "model": "${ENV.OPENAI_MODEL}",
})
```

| Key | Meaning |
|---|---|
| `base_url` | the API root, e.g. `https://api.openai.com/v1` |
| `api_key` | bearer token; omit for local servers that don't require auth |
| `model` | provider-specific model name |
| `model_type` | `"chat"` (default) or `"completion"` for legacy completion endpoints |
| `request_options` | extra dict forwarded to the underlying HTTP client (timeouts, headers) |

The full set lives in [agently/builtins/plugins/ModelRequester/OpenAICompatible.py](../../../agently/builtins/plugins/ModelRequester/OpenAICompatible.py).

## Responses API variant

Some providers (and OpenAI itself for newer models) speak the Responses API rather than Chat Completions. Agently has a sibling plugin:

```python
Agently.set_settings("OpenAIResponsesCompatible", {
    "base_url": "https://api.openai.com/v1",
    "api_key": "${ENV.OPENAI_API_KEY}",
    "model": "${ENV.OPENAI_RESPONSES_MODEL}",
})
```

`OpenAIResponsesCompatible` is a sibling of `OpenAICompatible`; pick whichever matches the protocol your endpoint exposes. Both plugins directly implement `ModelRequester`; neither plugin inherits from the other.

## What "OpenAI-compatible" actually covers

A provider qualifies as OpenAI-compatible when its endpoint:

- Accepts a JSON body with `messages: [{"role": ..., "content": ...}, ...]`.
- Returns either a JSON response or an SSE stream of token deltas.
- Uses standard fields like `model`, `temperature`, `max_tokens`, `tools`, etc.

Providers that fit:

- OpenAI / Azure OpenAI
- DeepSeek (`https://api.deepseek.com/v1`)
- Qwen / DashScope's compatibility mode (`https://dashscope.aliyuncs.com/compatible-mode/v1`)
- Kimi / Moonshot (`https://api.moonshot.cn/v1`)
- GLM (`https://open.bigmodel.cn/api/paas/v4/`)
- MiniMax, Doubao, ERNIE — most ship an OpenAI-compatible mode
- SiliconFlow, Groq — both expose OpenAI-compatible endpoints
- Gemini — via OpenAI-compat endpoint
- Ollama (local) — `http://127.0.0.1:11434/v1`
- vLLM, LM Studio, llama.cpp server (local)
- Most internal gateways teams build over commercial models

For per-provider recipes, see [Providers](providers/).

## Per-agent overrides

Agent-level settings override the global preset:

```python
agent = Agently.create_agent()
agent.set_settings("OpenAICompatible", {"model": "${ENV.OPENAI_MODEL_FAST}"})
```

You can also set request-level overrides via the request chain — see [Settings](../start/settings.md).

## Streaming and tools

`OpenAICompatible` handles both streaming responses (used by `get_generator(...)` / `get_async_generator(...)`) and tool calling (used by the action runtime). You don't need to enable these per-provider — they're on as the protocol allows.

If a particular provider doesn't fully implement OpenAI semantics for one of these (e.g., a quirky streaming format), the underlying plugin tries to be tolerant; report concrete cases via issues.

## See also

- [Models Overview](overview.md) — protocol picking
- [AnthropicCompatible](anthropic-compatible.md) — the other protocol plugin
- [Providers](providers/) — recipes per provider
- [Model Setup](../start/model-setup.md) — quickstart-level walkthrough
