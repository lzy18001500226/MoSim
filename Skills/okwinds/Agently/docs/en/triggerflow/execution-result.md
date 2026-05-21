---
title: TriggerFlow Execution Result
description: Reading one execution outcome as state, compatibility result, interventions, and metadata.
keywords: Agently, TriggerFlow, execution.result, close snapshot, result, metadata
---

# Execution Result

> Languages: **English** · [中文](../../cn/triggerflow/execution-result.md)

`execution.result` is the multi-view reader for a TriggerFlow execution outcome.
It does not create a second result store. It reads state, compatibility result,
intervention ledger, and lifecycle metadata already owned by the execution.

For simple scripts, keep using the close snapshot:

```python
snapshot = await flow.async_start(input_data)
```

For services, UIs, runtime stream consumers, and code that needs several views
of the same execution, keep the execution handle and read through
`execution.result`:

```python
execution = flow.create_execution(auto_close=False)
await execution.async_start(input_data)
snapshot = await execution.async_close()

result = execution.result
report = result.get_state("report")
late = result.get_interventions(status="expired")
meta = result.get_meta()
```

## Readers

| Reader | What it returns |
|---|---|
| `execution.result.get_state(key=None, default=None)` | Live state before close; frozen close snapshot after close. Dot paths are supported. |
| `await execution.result.async_get_final_result(timeout=None)` | Compatibility final result: `"$final_result"` first, explicit internal result second, close snapshot fallback after close. |
| `execution.result.get_final_result(timeout=None)` | Sync wrapper for `async_get_final_result(...)`. |
| `execution.result.get_interventions(...)` | Intervention ledger records when that ledger is enabled; otherwise an empty list. |
| `execution.result.get_latest_intervention(default=None, **filters)` | Last matching intervention record or `default`. |
| `execution.result.get_meta()` | Execution metadata such as id, flow name, status, lifecycle state, timestamps, close reason, and state version. |

## Snapshot vs Final Result

The close snapshot remains TriggerFlow's canonical completed state:

```python
snapshot = await execution.async_close()
```

`async_get_final_result()` is for compatibility with older `.end()` and
`set_result()` flows. It preserves the old lookup order but expresses that intent
directly:

```python
final = await execution.result.async_get_final_result()
```

New code should prefer meaningful state keys plus the close snapshot. Use the
final-result reader only when you are bridging compatibility code.

For live progress events, keep using
`execution.get_async_runtime_stream(...)`. `execution.result` does not add a
second stream generator surface.

## Metadata

Metadata is intentionally outside the close snapshot:

```python
meta = execution.result.get_meta()
```

Use it for service logs, UI labels, and lifecycle diagnostics without adding
system fields to application state.

## See Also

- [Lifecycle](lifecycle.md) - start, seal, close, and close snapshots
- [State and Resources](state-and-resources.md) - choosing state keys
- [Runtime Intervention](runtime-intervention.md) - how the intervention ledger is populated
- [Compatibility](compatibility.md) - migrating from `.end()` and `set_result()`
