# 任务契约（Task Contract）

> 目的：让“用 agently-task-dev 开发的任务”具备统一的可测试接口；测试通过才算交付成功。

---

## 最小契约（必须实现）

每个任务目录建议遵循：

```
agently_tasks/<task_name>/
  task.py
  asgi_app.py          # 可选：服务化（SSE/POST）
tests/
  test_<task_name>.py  # 回归测试（必须）
```

其中 `agently_tasks/<task_name>/task.py` 必须提供：

1) `run(question: str) -> dict`
- 返回 **结构化 dict**（用 `.output(schema)` 生成，不要拼字符串凑 JSON）
- 必须在内部使用 `.start(ensure_keys=..., max_retries=...)` 保证字段完整/可预测

2) `stream_instant(question: str)`
- 返回一个 generator/iterator，逐条产出 Agently `instant`（或 `streaming_parse`）事件（即 `StreamingData`）
- 用于 UI / 服务端 SSE 转发

推荐（服务端/异步框架）：

3) `stream_instant_async(question: str)`
- 返回 async generator，内部用 `response.result.get_async_generator(type="instant")`
- 避免在 ASGI/FastAPI 等运行中的事件循环里触发 `asyncio.run(...)` 报错

推荐（可选）：

4) `get_schema() -> dict`
- 返回该任务的 output schema，供测试直接引用

---

## 输出契约（建议）

为了让测试更稳定、任务更易复用，建议 schema 至少包含：

- `reply: str`（最终给用户的回答）
- `sources: list[{url: str, notes: str}]`（引用来源，或工具结果摘要）
- `meta?: dict`（可选：tokens、耗时、模型信息、debug 标记等）

---

## 服务化契约（可选，但强烈建议）

如果提供 `asgi_app.py`，建议暴露：
- `GET /sse?question=...`：返回 SSE（每条 `data: <json>\n\n`）
- `POST /ask`：一次性 JSON response（便于非流式客户端）

事件格式建议统一：
`{"type": "...", "data": ...}`

并至少包含这些 type：
- `status`（阶段变化：planning/tooling/summarizing/done）
- `thinking_delta` 或 `reply_delta`（可选：用户可见 token）
- `field`（结构化字段完成：path/value）
- `error`
