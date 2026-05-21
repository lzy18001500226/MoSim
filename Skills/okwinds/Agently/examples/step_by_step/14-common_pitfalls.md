# Common Pitfalls & FAQs (Agently Dev)

## 1) Stream hangs or no output
- Symptom: terminal appears stuck after input.
- Cause: using sync generators inside an async context, or consuming an execution runtime stream without closing the execution.
- Fix:
  - In async handlers, use `get_async_generator(...)` and `async for`.
  - Start with `await execution.async_start(...)`, consume `execution.get_async_runtime_stream(...)`, and finish with `execution.async_close()`.

## 1.1) Streaming output labels spam
- Symptom: every token prints its own label (e.g., repeated `[thinking]`).
- Cause: printing labels on every delta.
- Fix: print the label once, then append deltas on the same line; add a newline on completion.

## 1.2) Streaming inside async loop throws `asyncio.run` error
- Symptom: `asyncio.run() cannot be called from a running event loop`.
- Cause: using sync `get_response().get_generator(...)` inside an async handler.
- Fix: use `request.get_async_generator(...)` with `async for`.

## 2) TriggerFlow result shape is unexpected
- Symptom: close returns a full state snapshot instead of a single scalar.
- Cause: execution lifecycle now treats close as the reliable completion boundary.
- Fix:
  - Store user-facing output under a stable state key, such as `result` or `final`.
  - Use `set_result(...)` only as a compatibility override when integrating old callers.

## 3) when() branch output is missing
- Symptom: state does not contain the branch output you expected.
- Cause: `when()` branches are event-driven and only update state if a handler writes state.
- Fix: call `data.async_set_state(...)` in event handlers and close the execution after pending tasks drain.

## 4) Concurrency wrapper issues
- Symptom: wrong handler called in batch/for_each.
- Cause: closure binding in loops.
- Fix: bind handler per chunk (factory or default argument).

## 5) Flow data vs runtime data
- Symptom: data leaks across executions.
- Cause: `flow_data` is global.
- Fix: use execution state (`data.get_state`, `data.async_set_state`) for per-execution state.

## 6) Wrong entry point in loop flows
- Symptom: input never arrives or loop blocks.
- Cause: starting with `to(get_input)` and waiting on events that are never emitted.
- Fix: emit a loop event (e.g., `Loop`) at start, then `when("Loop") -> get_input`.

## 6) Instant stream is noisy
- Symptom: each token prints a label.
- Fix: print label once, then stream tokens on the same line; print newline on completion.

## 7) Tools not called or wrong tool
- Symptom: model ignores tools or calls invalid tool.
- Fix:
  - ensure tool names and schemas are clear in `.output()` or `.info()`
  - keep tool list concise

## 8) Knowledge base rebuild every turn
- Symptom: repeated slow initialization.
- Fix: build KB once and reuse (e.g., cached collection in outer scope).

## 9) httpx INFO spam
- Symptom: noisy httpx/httpcore logs.
- Fix: set `runtime.httpx_log_level` to `WARNING` or `ERROR`.

## 10) Settings not applied as expected
- Symptom: model config seems ignored.
- Fix:
  - call `Agently.set_settings(...)` before creating agents
  - check runtime mappings (`debug` toggles multiple flags)
