---
title: Schema as Prompt
description: Authoring structured output as nested dicts of typed leaves with ensure flags.
keywords: Agently, schema, output, ensure, type, description, YAML
---

# Schema as Prompt

> Languages: **English** · [中文](../../cn/requests/schema-as-prompt.md)

Agently's `.output(...)` is **prompt-native**: the structure you author is rendered both as a textual hint to the model and as a parser/validator on the way back. There's no separate JSON Schema file to maintain — the same nested dict drives both.

## The leaf

A leaf is a tuple:

```python
(TypeExpr, "description", True)
```

| Slot | Meaning |
|---|---|
| 1. `TypeExpr` | Python type, typing expression, `Enum` class, `BaseModel`, or a string token like `"str"`, `"list[str]"` |
| 2. description | Soft hint to the model and to humans |
| 3. ensure | `True` marks the leaf as required and adds it to `ensure_keys` |

> The third slot is the **ensure flag**, not a default value. The older "default value as third slot" convention is no longer supported, and YAML's `$default` is gone with it.

Shorthand forms:

```python
(str,)                        # type only
(str, "short description")    # type + description
"description only"            # equivalent to (Any, "description only")
```

## Object and array nodes

Nest dicts and lists to compose:

```python
{
    "title": (str, "Article title", True),
    "tags": [(str, "Tag", True)],
    "sections": [
        {
            "heading": (str, "Heading", True),
            "body": (str, "Body text", True),
        }
    ],
}
```

| Container | Meaning |
|---|---|
| `dict` | object node — field order matters and is preserved |
| `list` with one item | homogeneous array — write **one** prototype |
| `list` with multiple items | examples / illustrative; the standard way is one prototype |

## Field order is part of the contract

The model emits fields in the order you define them. If you explicitly expose fields such as `notes` or `analysis`, they appear before `answer` and are consumed downstream in that order. Reorder fields, and you change behavior — there is no "best order" the model figures out for you. Do not ask the model to expose hidden reasoning; only expose fields your application actually needs to store.

## Ensure compiles to ensure_keys

Every `True` in the third slot adds the leaf's path to the `ensure_keys` list at parse time:

```python
{
    "title": (str, "Title", True),
    "items": [
        {
            "name": (str, "Name", True),
            "value": (str, "Value"),  # NOT ensured
        }
    ],
}
```

Compiles to:

```python
ensure_keys = ["title", "items[*].name"]
```

Array wildcards like `items[*]` are part of the path syntax. If `title` is missing or any `items[i].name` is missing in parse output, the request retries (subject to `max_retries`). `value` is allowed to be missing.

For "the entire schema must come back complete", set `ensure_all_keys: True` on the agent or use `$ensure_all_keys: true` at the top of a YAML/JSON prompt — it overrides per-leaf decisions.

## YAML / JSON form

```yaml
output:
  title:
    $type: str
    $desc: Title
    $ensure: true
  items:
    $type:
      - name:
          $type: str
          $desc: Name
          $ensure: true
        value:
          $type: str
          $desc: Value
```

Conventions:

- `$type` — the type expression (string token or nested structure)
- `$desc` — description
- `$ensure: true` (or `$ensure: 1`) — the ensure flag
- Aliases `.type` / `.desc` are accepted by the loader but `$`-prefixed keys are recommended

`$default` is **not supported** — defaults are no longer part of authoring.

## Type tokens in YAML

Common string tokens:

| Token | Meaning |
|---|---|
| `"str"`, `"int"`, `"bool"`, `"float"` | scalar Python types |
| `"list[str]"`, `"dict[str, int]"` | typing-style |
| `"Literal[open, closed]"` | literal values |
| `"Optional[str]"` | optional types |

## Pydantic and Enum

You can also mix in Pydantic models and Enum classes anywhere a `TypeExpr` is allowed:

```python
from enum import Enum
from pydantic import BaseModel

class Severity(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"

class Ticket(BaseModel):
    severity: Severity
    rationale: str

agent.output(Ticket)  # equivalent to expanding the BaseModel into nested leaves
```

`get_data_object()` on the response returns a Pydantic instance when `output()` was given a `BaseModel`.

## Plain text

When you want plain text rather than structured output, **don't** use `output()` — just `agent.input("...").start()` returns a string, or use `response.result.get_text()`. Schema as Prompt is for structured outputs.

## Out of scope

Schema as Prompt is the **authoring** layer for one model request. It is not:

- A replacement for JSON Schema for external API contracts.
- The same thing as a TriggerFlow contract (TriggerFlow uses its own `set_contract(...)` shape).
- A UI form definition.

The earlier attempt to unify `.output()`, TriggerFlow contracts, and external schemas into a single DSL ("Agently DSL") has been archived. Each consumer keeps its own surface; only the prompt-side authoring is what this page covers.

## See also

- [Output Control](output-control.md) — what happens after parsing
- [Prompt Management](prompt-management.md) — slots and YAML/JSON loading
- [Glossary: ensure](../reference/glossary.md#ensure-third-tuple-slot)
