---
title: Glossary
description: Agently terminology reference, including newer terms like seal, runtime resources, ensure, and the action runtime layers.
keywords: Agently, glossary, terminology, lifecycle, runtime resources, ensure
---

# Glossary

Terms are listed alphabetically. Where a term has changed meaning compared with older docs, the entry says so.

## Action Runtime

The middle layer of Agently's three-layer action stack: `TriggerFlow` (top, orchestration) → `ActionRuntime` (planning + dispatch) → `ActionExecutor` (atomic backend execution). `ActionFlow` is the bridge between the runtime and the flow.

`ActionRuntime`, `ActionFlow`, and `ActionExecutor` are now the public plugin types. The older `ToolManager` plugin type is kept for legacy use only and emits deprecation warnings. See [Action Runtime](../actions/action-runtime.md).

## auto_close / auto_close_timeout

Settings on a TriggerFlow execution. With `auto_close=True` (the default), the execution closes itself after `auto_close_timeout` seconds of idle. Hidden execution sugar (`flow.start()` / `flow.async_start()`) defaults to `auto_close_timeout=0.0`. `flow.start(auto_close=False)` is illegal and raises.

## Close snapshot

The dict returned by `execution.close()` / `execution.async_close()`. It captures the final state of the execution. If a compatibility result was written via the deprecated `set_result()` or `.end()`, it appears as the `"$final_result"` key inside the snapshot. See [Lifecycle](../triggerflow/lifecycle.md).

## ensure (third tuple slot)

In `(TypeExpr, "description", True)` the third slot is the `ensure` flag — it marks a leaf as required. Ensure-marked leaves are compiled into `ensure_keys` (with array wildcards like `resources[*].url`). YAML / JSON form: `$ensure: true`.

This is **not** a default value. The older "default value as third slot" convention is no longer supported, and `$default` in YAML is gone. See [Schema as Prompt](../requests/schema-as-prompt.md).

## Execution

A single run of a TriggerFlow. Created by `flow.create_execution(...)`. Has lifecycle states `open → sealed → closed`.

## flow_data

Flow-scoped shared data. Calling `get_flow_data(...)` / `set_flow_data(...)` and friends emits a `RuntimeWarning` because the value is shared across all executions of the flow, which causes problems for concurrency, save/load, and distributed runs. Pass `no_warning=True` to suppress the warning when the shared scope is intentional. Prefer `state` for execution-local data.

## Hidden execution sugar

`flow.start()` / `flow.async_start()` create a temporary execution under the hood, run it to close, and return the close snapshot. Convenient for scripts and one-shot runs. Not appropriate for flows that pause for human input, expect external `emit()`s, or otherwise need an externally-controlled execution handle — use `flow.start_execution(...)` for those.

## OpenAICompatible / AnthropicCompatible

The three protocol-level model request plugins: `OpenAICompatible`, `OpenAIResponsesCompatible`, and `AnthropicCompatible`. Most Chat Completions compatible providers configure `OpenAICompatible`; Responses API-shaped endpoints use `OpenAIResponsesCompatible`; Claude configures `AnthropicCompatible`. See [Models Overview](../models/overview.md).

## Runtime resources

Execution-local storage for live objects — database clients, callbacks, sockets, function pointers, cache handles. Runtime resources are **not** serializable and **do not** enter close snapshots or save/load checkpoints; only their `resource_keys` are recorded. On resume after `load()`, the caller must re-inject them.

This is a distinct concept from `state` and `flow_data`. See [State and Resources](../triggerflow/state-and-resources.md).

## Runtime stream

A per-execution stream of items emitted by chunks via `data.put_into_stream(...)` / `data.async_put_into_stream(...)`. Consumed by `execution.get_runtime_stream(...)` / `execution.get_async_runtime_stream(...)`. The stream is closed as part of `execution.close()`.

## seal / sealed

The middle lifecycle state. `execution.seal()` / `execution.async_seal()` stops the execution from accepting new external events but lets already-accepted events, internal emit chains, and registered tasks finish. It does **not** close the runtime stream and does **not** freeze the close snapshot — that happens on `close()`.

## Schema as Prompt

The current name for Agently's prompt-side structured authoring style: nested dicts of leaves, where each leaf is `(TypeExpr, "description", True)` and the third slot is `ensure`. The older "Agently DSL" framing — which tried to be a unified IR for `.output()`, TriggerFlow contracts, and external schemas — is archived.

## state

Execution-local, serializable, snapshot-safe data. The recommended state surface is `data.async_set_state(...)` for writes and `data.get_state(...)` for reads. State is what populates close snapshots and what `save()` / `load()` round-trip.

## TriggerFlow

The orchestration layer. Owns branching, concurrency, batches, loops, sub-flows, pause/resume, persistence, and runtime stream. Sits above the Action Runtime and below your application code.

## $final_result

A reserved state key written by the deprecated `set_result()` and `.end()` paths. Its presence in a close snapshot indicates a compatibility result was provided. New code should rely on the snapshot itself rather than this key. See [TriggerFlow Compatibility](../triggerflow/compatibility.md).

## wait_for_result=

Deprecated parameter on `flow.start()`, `flow.async_start()`, `start_execution()`, `execution.start()`, and friends. The value is now **ignored** with a warning; return shape is controlled by `auto_close` (and the choice between hidden sugar and explicit execution).
