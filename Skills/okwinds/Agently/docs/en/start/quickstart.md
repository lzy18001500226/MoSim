---
title: Quickstart
description: Install Agently, configure a model, and run a structured request in five minutes.
keywords: Agently, quickstart, structured output, OpenAICompatible, AnthropicCompatible
---

# Quickstart

The goal is to get one minimal end-to-end request running, then point you at the right next step.

## Install

```bash
pip install -U agently
```

`uv pip install -U agently` works the same way.

## Configure a model

Agently ships three protocol-level request plugins: `OpenAICompatible` (Chat Completions compatible endpoints), `OpenAIResponsesCompatible` (Responses API shape), and `AnthropicCompatible` (Claude / Anthropic Messages API). Pick the one that matches the endpoint you are pointing at.

```python
from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "https://api.openai.com/v1",
        "api_key": "${ENV.OPENAI_API_KEY}",
        "model": "${ENV.OPENAI_MODEL}",
    },
)
```

For Claude:

```python
Agently.set_settings(
    "AnthropicCompatible",
    {
        "base_url": "https://api.anthropic.com",
        "api_key": "${ENV.ANTHROPIC_API_KEY}",
        "model": "${ENV.ANTHROPIC_MODEL}",
        "max_tokens": 4096,
    },
)
```

For Ollama or any other OpenAI-compatible local server, set `base_url` to that server (for Ollama: `http://127.0.0.1:11434/v1`) and set `model` to the local model name. `api_key` can be omitted for local-only setups that don't require it.

See [Model Setup](model-setup.md) for the full provider list and `${ENV.*}` placeholders.

## Run one structured request

```python
from agently import Agently

agent = Agently.create_agent()

result = (
    agent
    .input("Write a one-line positioning statement and two highlights for Agently.")
    .output({
        "positioning": (str, "One-line positioning", True),
        "highlights": [
            {
                "title": (str, "Highlight title", True),
                "detail": (str, "One-line detail", True),
            }
        ],
    })
    .start()
)

print(result)
```

Each leaf is `(type, description, ensure)`. The third slot is the **`ensure` flag** — set to `True` to guarantee the field is present in the parsed result, retrying the request if needed. See [Schema as Prompt](../requests/schema-as-prompt.md).

## What to read next

- Building a service, streaming UI, or workflow → [Async First](async-first.md)
- More providers and env-driven settings → [Model Setup](model-setup.md)
- Stronger output guarantees and validation → [Output Control](../requests/output-control.md)
- Reading text, data, and metadata from one response → [Model Response](../requests/model-response.md)
- Project layout for non-trivial apps → [Project Framework](project-framework.md)
- Branching, loops, pause/resume → [TriggerFlow Overview](../triggerflow/overview.md)

## Common pitfalls

- Building a custom JSON parser before trying `output()`.
- Jumping into TriggerFlow before getting a single request right.
- Mixing prompt definition, settings, and business logic in one script — see [Project Framework](project-framework.md).
