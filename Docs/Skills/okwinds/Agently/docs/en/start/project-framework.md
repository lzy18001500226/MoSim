---
title: Project Framework
description: Recommended layout for a non-trivial Agently project.
keywords: Agently, project layout, settings, prompts, workflow, FastAPI
---

# Project Framework

Once you go past one script, the wins from separating concerns are large:

- Settings live in files, not in code that has to be edited per environment.
- Prompts live in YAML / JSON and can be reviewed by non-engineers.
- Business logic doesn't import keys or model names directly.

## Recommended layout

```text
my-agently-app/
  pyproject.toml              # or requirements.txt
  .env                        # local secrets (gitignored)
  settings.yaml               # global model and runtime settings
  prompts/
    summarize.yaml            # one prompt per file
    triage.yaml
  flows/
    triage.py                 # TriggerFlow definitions
  app/
    api.py                    # FastAPI entrypoint
    agents.py                 # agent factories
    actions.py                # action / tool registrations
    main.py
  tests/
    test_triage_flow.py
```

Only `settings.yaml` and `prompts/*` are required for this layout to be useful — the rest is a starting shape.

## settings.yaml

```yaml
plugins:
  ModelRequester:
    OpenAICompatible:
      base_url: ${ENV.OPENAI_BASE_URL}
      api_key: ${ENV.OPENAI_API_KEY}
      model: ${ENV.OPENAI_MODEL}
debug: false
```

Loading at startup:

```python
from agently import Agently

Agently.load_settings("yaml_file", "settings.yaml", auto_load_env=True)
```

`auto_load_env=True` reads `.env` first so the `${ENV.*}` placeholders resolve.

## Prompts in files

```yaml
# prompts/summarize.yaml
.request:
  instruct: |
    You are a concise editor. Keep facts intact.
  output:
    title:
      $type: str
      $ensure: true
    body:
      $type: str
      $ensure: true
```

Loading and using:

```python
from agently import Agently

agent = Agently.create_agent().load_yaml_prompt("prompts/summarize.yaml")
result = agent.input(article_text).start()
```

`$ensure: true` is the YAML form of the `(type, "desc", True)` tuple's third slot — see [Schema as Prompt](../requests/schema-as-prompt.md). Legacy `$default` is no longer supported.

## Agent factories

Centralize creation so call sites don't repeat configuration:

```python
# app/agents.py
from agently import Agently


def make_summarizer():
    return Agently.create_agent().load_yaml_prompt("prompts/summarize.yaml")
```

## Where flows live

Define each TriggerFlow in its own module under `flows/`. Import the flow object, build an execution from it in your service code, and keep the flow definition decoupled from FastAPI / queue plumbing. See [TriggerFlow Overview](../triggerflow/overview.md).

## Where actions live

If your agent calls tools / MCP servers / sandboxes, put the registrations next to your agent factories or in a dedicated `actions.py`. Use the action-first surface (`@agent.action_func`, `agent.use_actions(...)`) for new code; the `tool_func` / `use_tools` / `use_mcp` / `use_sandbox` family is kept as a compatibility surface but the [Action Runtime](../actions/action-runtime.md) page is the recommended path.

## See also

- [Settings](settings.md)
- [Prompt Management](../requests/prompt-management.md)
- [Schema as Prompt](../requests/schema-as-prompt.md)
- [TriggerFlow Overview](../triggerflow/overview.md)
- [FastAPI Service Exposure](../services/fastapi.md)
