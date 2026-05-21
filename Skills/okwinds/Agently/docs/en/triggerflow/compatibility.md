---
title: TriggerFlow Compatibility
description: Migrating from .end(), set_result(), wait_for_result=, and runtime_data to the new lifecycle.
keywords: Agently, TriggerFlow, compatibility, deprecated, end, set_result, wait_for_result, runtime_data
---

# Compatibility

> Languages: **English** · [中文](../../cn/triggerflow/compatibility.md)

This is the **only** page where deprecated TriggerFlow APIs appear as recommended starting points — for migration purposes. Everywhere else in the documentation should already be on the new APIs.

The high-level shift is: the new lifecycle treats the **close snapshot** as the canonical return value. Older APIs that tried to compute a single "result" — `.end()`, `set_result()`, `get_result()`, `wait_for_result=` — are kept as compatibility surfaces but are not recommended for new code.

Deprecation warnings are emitted once per deprecated API per Python process. Repeated calls keep working without repeating the same warning, while different deprecated APIs still warn independently. If production needs to silence Agently deprecation warnings globally, set `runtime.show_deprecation_warnings=False`.

## .end() — definition-time DSL, not a lifecycle action

`.end()` was historically used as the way to "finish" a flow. Its actual current behavior is narrower:

- It is a **definition-time** DSL — it appends a compatibility result sink to the flow at build time.
- It is **not** equivalent to `seal()`.
- It is **not** equivalent to `close()`.
- All it does at runtime is write whatever value flowed into it to the reserved state key `"$final_result"`.

Status: **Deprecated** — calls emit a deprecation warning.

### Old

```python
flow.to(step_a).to(step_b).end()  # writes step_b's return into "$final_result"
result = flow.start("input")
```

### New

```python
flow.to(step_a).to(step_b)  # no .end()
snapshot = flow.start("input")
# step_b's return value lands in whatever state key step_b wrote to,
# or you can capture it explicitly:

async def step_b(data):
    await data.async_set_state("answer", do_work(data.input))
```

If you have flow configs that still call `.end()`, they keep working — the value just lands in `snapshot["$final_result"]` instead of being framework-mediated.

## set_result() / get_result() — compatibility writer/reader

`set_result(value)` writes to the same `"$final_result"` state key. `get_result()` reads it (or falls back to the close snapshot).

Status: **Deprecated** — both emit deprecation warnings.

When you must bridge compatibility code, prefer
`await execution.result.async_get_final_result()` over adding new
`get_result()` call sites. It keeps the same lookup order while making the
compatibility intent explicit.

### Old

```python
async def worker(data):
    data.set_result({"answer": ...})
```

```python
result = execution.get_result()  # waits and returns
```

### New

```python
async def worker(data):
    await data.async_set_state("answer", ...)
```

```python
snapshot = await execution.async_close()
answer = snapshot["answer"]
```

If a single canonical result really is what you want and the rest of the snapshot is noise, just project it on the way out:

```python
async def project_answer(execution):
    snapshot = await execution.async_close()
    return snapshot["answer"]
```

## wait_for_result= — value is now ignored

`wait_for_result=True` / `False` was the old way to control whether `start(...)` waited for a result. The new lifecycle controls return type with `auto_close` instead.

Status: **Deprecated** — value is **ignored** with a warning.

### Old

```python
result = flow.start("input", wait_for_result=True)   # the parameter no longer matters
```

### New

For "wait and give me the close snapshot", use the hidden sugar:

```python
snapshot = await flow.async_start("input")           # always returns close snapshot
```

For "give me the execution and I'll close it myself":

```python
execution = flow.create_execution(auto_close=False)
await execution.async_start("input")                 # returns execution
# ... do work ...
snapshot = await execution.async_close()
```

See [Lifecycle](lifecycle.md) for the full table of entry APIs.

## runtime_data — old name for state

The old `runtime_data` API surface (`get_runtime_data`, `set_runtime_data`, `append_runtime_data`, `del_runtime_data`) is now an alias of the modern `state` API. It still works but emits deprecation warnings.

Status: **Deprecated** alias of `state`.

### Old

```python
async def step(data):
    await data.set_runtime_data("count", 1)
    n = data.get_runtime_data("count")
```

### New

```python
async def step(data):
    await data.async_set_state("count", 1)
    n = data.get_state("count")           # sync read also exists
```

The semantics haven't changed — just the names. See [State and Resources](state-and-resources.md).

## flow_data — risky-default, not deprecated

`flow_data` is a third storage layer with a different problem: it's flow-scoped (shared across **all** executions of the flow). It still works, but every call emits a `RuntimeWarning` because of the concurrency / save-load risks.

Status: **Risky-default** — works, but warns. Not the same as deprecation.

If you intentionally need shared scope, suppress the warning:

```python
flow.set_flow_data("shared_counter", 0, no_warning=True)
```

For 99% of use cases the right answer is `state` (per-execution) or `runtime_resources` (live objects). See [State and Resources](state-and-resources.md).

## $final_result in close snapshots

Even after migration, you'll see `"$final_result"` in close snapshots if any `.end()` or `set_result()` ran during the execution — including inside sub-flows or shared library code you don't control. The bridge logic in `to_sub_flow(...)` deliberately checks for `$final_result` first when resolving `result.<path>` write-backs, exactly so legacy children continue to work alongside new state-first parents. See [Sub-Flow](sub-flow.md).

## Migration checklist

For each flow:

1. Remove `.end()` from definitions. Decide which state key carries the value you actually want.
2. Replace `set_result(x)` with `async_set_state("answer", x)` (or whatever the meaningful key is).
3. Replace `get_result()` with reading the relevant key from the close snapshot.
4. Drop `wait_for_result=` arguments — they don't do anything anymore.
5. Replace `set_runtime_data` / `get_runtime_data` with `async_set_state` / `get_state`.
6. Audit `flow_data` calls. Most should be `state`; the rest should suppress the warning intentionally.
7. Audit live objects in state. Move them to `runtime_resources`.

## See also

- [Lifecycle](lifecycle.md) — the new entry APIs
- [State and Resources](state-and-resources.md) — where to put what
- [Sub-Flow](sub-flow.md) — how the bridge handles legacy children
