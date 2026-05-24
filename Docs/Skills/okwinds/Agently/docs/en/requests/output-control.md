---
title: Output Control
description: The output validation pipeline — strict output, ensure_keys, custom validate, retries, and events.
keywords: Agently, output, validate, ensure_keys, retry, max_retries
---

# Output Control

> Languages: **English** · [中文](../../cn/requests/output-control.md)

The validation pipeline runs the first time a structured response result is consumed, then caches the outcome on that response result. It has a fixed order, and each step contributes to the same retry budget.

For Agently `4.1.0.1+`, the default authoring path is: mark fixed required leaves directly in `.output(...)` with the third-slot `ensure` flag, then let the runtime compile those flags into `ensure_keys`. Pass `ensure_keys=` manually only when the required path is runtime-dependent, conditional, or easier to express outside the static schema.

## The pipeline

```text
   model returns text
        │
        ▼
1. parse / repair         ← extract structured object from text
        │
        ▼
2. strict output          ← match against .output(...) shape; ensure_all_keys checks if set
        │
        ▼
3. ensure_keys            ← per-leaf required-path checks (compiled from the ensure flag)
        │
        ▼
4. custom validate        ← .validate(handler) and validate_handler= business rules
        │
        ▼
   pass → return result   |   fail → retry (if budget remains) → top of pipeline
```

A failure at any step retries the request. Retries share one budget controlled by `max_retries` (default `3`). When the budget is exhausted:

- `raise_ensure_failure=True` (the default) — raises.
- `raise_ensure_failure=False` — returns the latest parsed result anyway.

## Where validate plugs in

`.validate(handler)` registers a custom check. It runs **after** strict output and `ensure_keys` have already passed, on a canonical dict snapshot of the result.

```python
def must_be_short(result, ctx):
    if len(result.get("answer", "")) > 280:
        return {"ok": False, "reason": "answer too long", "validator_name": "length"}
    return True

agent.input("Summarize.").output({
    "answer": (str, "answer", True),
}).validate(must_be_short).start()
```

The handler runs only on structured-result getters: `start()`, `async_start()`, `get_data()`, `async_get_data()`, `get_data_object()`, `async_get_data_object()`. It does **not** run on `get_text()` / `get_meta()` (those don't carry the parsed structure that validate would inspect).

You can also pass handlers per-call:

```python
agent.input("...").output({...}).start(validate_handler=must_be_short)
agent.input("...").output({...}).start(validate_handler=[check_a, check_b])
```

`.validate(...)` handlers run before `validate_handler=` handlers. Multiple `.validate(...)` calls preserve order.

## Handler return shape

| Return | Meaning |
|---|---|
| `True` | pass |
| `False` | fail — retry if budget remains |
| `dict` | structured result; see keys below |

Supported `dict` keys:

| Key | Effect |
|---|---|
| `ok` | `True` = pass, `False` = fail |
| `reason` | text shown in retry events / error messages |
| `payload` | structured details for downstream consumers |
| `validator_name` | tag the validator in events |
| `no_retry` / `stop` | fail but don't retry |
| `error` / `exception` / `raise` | fail with the given exception |

Anything not in this list becomes a `model.validation_error` and consumes retry budget.

## Async handlers

Both sync and async handlers are supported. An async handler signature:

```python
async def check_remote(result, ctx):
    ok = await some_external_check(result["answer"])
    return ok
```

## Context object

The second argument is an `OutputValidateContext` with at least:

- `value`, `input`, `agent_name`, `response_id`
- `attempt_index`, `retry_count`, `max_retries`
- `prompt`, `settings`, `request_run_context`, `model_run_context`
- `response_text`, `raw_text`, `parsed_result`, `result_object`, `typed`, `meta`

Use `ctx.attempt_index` if you want different behavior on later attempts (e.g., loosen the rule on retry).

Treat these fields as observational by default, but `ctx.prompt` and `ctx.settings` are live state objects for the current response-attempt chain. In advanced handlers, if you need to adjust the prompt / options / settings for a **later retry**, you can write back through them inside the validator.

For example, lower sampling parameters on the next retry:

```python
def check(result, ctx):
    if result.get("score", 0) < 0.8 and ctx.retry_count < ctx.max_retries:
        ctx.prompt.set("options", {"temperature": 0.2, "top_p": 0.7})
        return {"ok": False, "reason": "score too low"}
    return True
```

Or change settings:

```python
def check(result, ctx):
    if should_switch_mode(result):
        ctx.settings.set("my_plugin.some_flag", True)
        return False
    return True
```

Two caveats:

- These writes affect **later retries only**. They do not change the current attempt that has already completed.
- These writes also do **not** leak into later fresh requests. Each new `response` is created from a new prompt/settings snapshot at the request/agent layer, so validator write-backs stay inside the current response's retry chain.
- Do not rely on mutating `opts = ctx.prompt.get("options", {})` in place. `get()` returns a view/copy; use write APIs such as `ctx.prompt.set(...)`, `ctx.prompt.update(...)`, or `ctx.settings.set(...)` if you need the change to persist.

## Single execution per response

Validation runs **once** per `ModelResponseResult` and the outcome is cached. Repeated calls — `get_data()` then `get_data()` again, or `get_data()` then `get_data_object()` — do **not** rerun validators. If you try to inject a different handler on the same response after validation has already finalized, the new handler is ignored with a warning.

This means: don't expect to swap validators per consumer. If you need different validation for different consumers, run the request twice.

## Retry events and visibility

Validation contributes two new observation event types:

- `model.validation_failed` — handler returned a fail
- `model.validation_error` — handler raised, returned an unsupported value, etc.

There is intentionally **no** `model.validation_passed` event in phase 1 — passing is the silent default.

The standard `model.retrying` event picks up validation-specific fields when the retry came from validate:

- `retry_reason`, `validator_name`, `validation_reason`, `validation_payload`

Agently-DevTools consumes these defensively. New event keys are additive and should not break existing dashboards.

## Combining with ensure_keys

`ensure_keys` and `.validate(...)` are layered:

- `ensure_keys` handles **path presence** (compiled from the `ensure` flag in `.output(...)`).
- `.validate(...)` handles **value rules** that depend on the actual content.

For fixed required leaves, prefer `(TypeExpr, "description", True)` in `.output(...)` rather than manually repeating the same paths in `ensure_keys=`. Use manual `ensure_keys` for conditional or runtime-only paths. Use `.validate(...)` for "this field must satisfy this business rule".

## Common patterns

**Loosen on the last retry**:

```python
def check(result, ctx):
    if ctx.attempt_index == ctx.max_retries:
        return True  # accept whatever came back
    return strict_check(result)
```

**Fail without retrying** (e.g., validation reveals a permanent business issue):

```python
def policy_check(result, ctx):
    return {"ok": False, "reason": "policy violation", "no_retry": True}
```

**Raise a custom exception**:

```python
def policy_check(result, ctx):
    return {"ok": False, "raise": MyDomainError("rejected by policy")}
```

## See also

- [Schema as Prompt](schema-as-prompt.md) — `.output(...)` authoring and `ensure` flag
- [Model Response](model-response.md) — what cached vs re-runnable means in practice
- [Glossary: ensure](../reference/glossary.md#ensure-third-tuple-slot)
