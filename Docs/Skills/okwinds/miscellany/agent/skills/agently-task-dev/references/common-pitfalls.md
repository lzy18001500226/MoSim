# Common Pitfalls & FAQs（通用）

来源：`agently-exmaples/step_by_step/14-common_pitfalls.md`，并结合本仓库的 demo 回归经验做“通用化表述”。

目标：把最常见的工程问题收敛成可复用的排障手册（不绑定业务场景）。

---

## 1) 流式卡住/没有输出

现象：
- 终端或 SSE 看起来“卡死”，没有任何输出。

常见原因：
- 在 async 上下文里使用 sync generator（或反之）。
- `get_runtime_stream(..., timeout=None)` 但忘记在合适的时机调用 `stop_stream()`。

修复建议：
- 在 async handler / web server 里使用 `get_async_generator(...)` + `async for`。
- TriggerFlow runtime stream 需要明确终止条件：在合适时机调用 `data.stop_stream()`（或触发 flow 结束链路）。

---

## 2) streaming label spam（每个 token 都重复输出标签）

现象：
- 每个 token 前都打印一次 `[thinking]` / `[answer]`，非常吵。

原因：
- 每次 delta 都打印 label。

修复：
- label 只在“切换事件类型 / 新字段开始”时输出一次，后续 delta 直接追加。
- 字段完成（`is_complete=True`）后补一个换行。

---

## 3) async 里出现 `asyncio.run() cannot be called from a running event loop`

原因：
- 在已有 event loop（比如 FastAPI/uvicorn）里使用 `asyncio.run(...)` 或使用 sync generator API。

修复：
- 用异步 API：`get_async_generator(...)`、`async_start(...)`、`await response.result.async_get_*()`。

---

## 4) TriggerFlow 返回 `None` / `wait_for_result` 超时

原因：
- 主链没有 `.end()`，或应该产出结果的分支没有 `set_result()`/`.end()`。
- `when(...)` 分支是事件驱动，默认不会“自动成为最终结果”。

修复：
- 把 `.end()` 放在你希望作为默认输出的链路上。
- 对 `when(...)` 分支：显式 `.end()` 或 `execution.set_result(...)`。

---

## 5) flow_data vs runtime_data（跨执行数据泄漏）

现象：
- A 请求的数据影响 B 请求（状态串了）。

原因：
- `flow_data` 是全局级别；`runtime_data` 才是 per-execution。

修复：
- per-request 状态放 `runtime_data`（`data.set_runtime_data(...)`）。
- 仅把真正跨执行共享的资源（连接池、KB 实例）放到外层缓存（或 flow_data，但要谨慎）。

---

## 6) loop flow 的入口事件错了（循环不触发/阻塞）

现象：
- loop 逻辑写了，但一直等不到 input/event。

原因：
- 没有 emit loop event，或者 `when("Loop")`/`when("UserInput")` 的链路组织不正确。

修复：
- 明确 loop 的“驱动事件”：例如 `start -> emit("Loop")`，然后 `when("Loop") -> get_input`。
- 退出路径要调用 `stop_stream()` 或结束主链。

---

## 7) Tools 不被调用 / 调错工具

原因：
- 工具列表太多、描述不清、参数 schema 模糊。

修复：
- 保持工具集精简（按阶段启用：Search→Browse→Summarize）。
- 清晰的 tool schema 与命名（尤其是 kwargs 结构）。
- 在 prompt/输出 schema 里显式要求“何时必须用工具”。

---

## 8) Knowledge Base 每回合都重建（慢、浪费）

原因：
- 每次请求都 new 一个 collection 并 add docs。

修复：
- KB 构建放在进程级缓存（或服务启动时），请求里只 query。
- 回归测试时用离线 stub + 小样本 KB，保证稳定可重复。

---

## 9) httpx/httpcore 日志太吵

修复：
- 调低 `runtime.httpx_log_level`（例如 WARNING/ERROR），避免淹没关键信息。

---

## 10) Settings 没生效

原因：
- 设置调用顺序不对（先 create_agent 再 set_settings），或混用全局/实例设置导致覆盖。

修复：
- 全局：`Agently.set_settings(...)` 在 create_agent 前设置默认值。
- 实例：`agent.set_settings(...)` 只用于覆盖某个 agent 的差异配置。

