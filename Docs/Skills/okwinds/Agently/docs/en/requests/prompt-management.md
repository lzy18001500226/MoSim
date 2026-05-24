---
title: Prompt Management
description: Layered prompt slots, agent vs request scope, YAML/JSON loading, and placeholders.
keywords: Agently, prompt, role, system, info, instruct, input, configure_prompt
---

# Prompt Management

> Languages: **English** · [中文](../../cn/requests/prompt-management.md)

Agently splits a prompt into named slots. The slots compose, so you can set persistent agent context once and only fill request-specific slots per call.

## Slot map

| Slot | Where it ends up | Typical use |
|---|---|---|
| `role` / `system` | system message | persona, capability boundaries |
| `info` | system or user (impl detail) | background facts, inventories, tool catalogs |
| `instruct` | user message | step-by-step instructions for this kind of request |
| `input` | user message | the actual question or payload |
| `output` | user message + parser | the schema you want back |

Setting a slot persistently:

```python
agent = (
    Agently.create_agent()
    .role("You are an Agently support assistant.", always=True)
    .info({"product": "Agently 4.x"}, always=True)
)
```

`always=True` keeps the slot at the agent level so it carries to every request the agent runs.

Setting a slot for one request:

```python
result = (
    agent
    .instruct(["Reply in fewer than 80 words.", "Never invent product names."])
    .input("How do I configure a model?")
    .output({"answer": (str, "answer", True)})
    .start()
)
```

`instruct(...)` here is per-request because `always=True` was not passed.

## Agent vs request scope

| Scope | API |
|---|---|
| Agent (persists for every future request) | `.role(...)`, `.info(...)`, `.instruct(...)`, `.set_agent_prompt(key, value)` |
| Request (one call only) | `.input(...)`, `.output(...)`, `.set_request_prompt(key, value)` |

The slot you set last wins for that scope, so you can override agent defaults in one request without mutating the agent.

## YAML / JSON prompt files

Same slot model, written declaratively:

```yaml
# prompts/triage.yaml
$ensure_all_keys: true
.agent:
  system: You are a ticket triage assistant.
  info:
    severities: ["P0", "P1", "P2", "P3"]
.request:
  instruct: Classify the ticket text.
  output:
    severity:
      $type: str
      $desc: One of P0/P1/P2/P3
      $ensure: true
    rationale:
      $type: str
      $desc: One-line reason
      $ensure: true
```

Loading:

```python
agent = Agently.create_agent().load_yaml_prompt("prompts/triage.yaml")

result = (
    agent
    .set_request_prompt("input", "Login fails for all users in EU region.")
    .start()
)
```

`load_json_prompt(...)` is the same API for JSON. Both accept either a path or a raw string body. Pick one config file per prompt or stack multiple prompts with `prompt_key_path="demo.output_control"` to select inside a multi-prompt file.

`$ensure_all_keys: true` at the top makes all leaves required regardless of per-leaf `$ensure`. Use it when the entire schema must come back complete.

## Round-tripping

You can convert a Python-built prompt back to YAML/JSON for review or storage:

```python
agent.role("You are an Agently agent.", always=True).input("Say hello.").output({
    "reply": (str, "reply", True),
})
print(agent.get_yaml_prompt())
print(agent.get_json_prompt())
print(agent.get_prompt_text())  # the rendered text the model will see
```

This round-trip is the canonical way to compare "what I think I'm sending" against "what the framework actually sends".

## Placeholders

Inside any prompt slot, `{name}` references another slot by key, and `${name}` is replaced by `mappings={"name": "value"}` at load time. Common patterns:

- `instruct: "Reply {input} politely."` — pulls the request `input` into the instruct text.
- `${ENV.OPENAI_API_KEY}` in *settings* (not prompts) is replaced by the env var; prompts use `${name}` with explicit mappings.

To trigger placeholder substitution while loading, pass `mappings=...` explicitly:

```python
agent.load_yaml_prompt(yaml_text, mappings={"product_name": "Agently"})
```

## Where each layer's prompt comes from

When a request runs, Agently composes the final prompt by stacking:

1. Agent-level slots (set with `always=True` or `set_agent_prompt`)
2. Request-level slots (set without `always=True`)
3. Slots populated by framework extensions or application code (Session injects chat history; retrieval code usually puts snippets into per-request `info(...)`)

Use `agent.get_prompt_text()` to see the merged result before sending.

## See also

- [Schema as Prompt](schema-as-prompt.md) — leaf authoring, `$ensure`
- [Output Control](output-control.md) — what happens after parsing
- [Project Framework](../start/project-framework.md) — file layout for managing many prompts
