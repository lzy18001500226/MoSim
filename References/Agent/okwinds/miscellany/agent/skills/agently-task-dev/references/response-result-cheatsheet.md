# Response/Result Cheatsheet（通用）

目标：让任务开发者正确使用 `get_response()` / `response.result.*`，避免重复请求，并更好地支持 streaming 与并发。

来源：
- `agently-exmaples/step_by_step/05-response_result.py`
- `agently-exmaples/step_by_step/06-streaming.py`
- `agently-exmaples/step_by_step/07-tools.py`（extra/tool_logs）

---

## 1) `start()` vs `get_response()`

### `start()`
- 适合：最短路径拿一次性结果（脚本/REPL）。
- 限制：不利于复用 response、做 streaming、做并发控制。

### `get_response()`
- 适合：你需要同时做这些事情之一：
  - streaming（delta/instant/specific）
  - 多次读取不同形态的结果（text/data/meta）
  - 把 tool_logs / extra 拿出来做审计

---

## 2) 常用 result API

```py
response = agent.input("...").output({"reply": (str,)}).get_response()

text = response.result.get_text()
data = response.result.get_data()
meta = response.result.get_meta()
extra = response.result.full_result_data.get("extra", {})
```

异步变体（服务端常用）：
- `await response.result.async_get_text()`
- `await response.result.async_get_data()`
- `await response.result.async_get_meta()`

---

## 3) streaming generator types（选择指南）

### `delta`
- 适合：用户可见“打字机”文本（token/小块）。

### `instant` / `streaming_parse`
- 适合：结构化字段的增量更新（path/wildcard_path/delta/is_complete）。
- 典型：UI 需要“边生成边渲染结构化卡片”。

### `specific`
- 适合：只挑你关心的事件（如 `delta`/`reasoning_delta`/`tool_calls`）。

---

## 4) 并发：`asyncio.gather`

服务端想提高吞吐，可以并发多个请求（注意 provider 的限流与并发上限）：

```py
import asyncio

async def ask(prompt: str):
  r = agent.input(prompt).get_response()
  return await r.result.async_get_text()

out1, out2 = await asyncio.gather(
  ask("..."),
  ask("..."),
)
```

---

## 5) 常见坑（快速对照）

- 在 web server 里用 `asyncio.run(...)`：改成 async API。
- 直接 `str(event)` 拼到正文：会把 `path='...'` 等元信息污染输出。
- streaming 失败又 fallback 重新 `start()`：容易导致“同一段两版文本”，用 `streaming_succeeded` 互斥。

更完整的坑清单见：
- `references/common-pitfalls.md`

