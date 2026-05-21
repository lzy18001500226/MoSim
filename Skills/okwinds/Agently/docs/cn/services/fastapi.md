---
title: FastAPI 服务封装
description: 把 agent、request、TriggerFlow execution 暴露为 HTTP / SSE / WebSocket。
keywords: Agently, FastAPI, HTTP, SSE, WebSocket, FastAPIHelper
---

# FastAPI 服务封装

> 语言：[English](../../en/services/fastapi.md) · **中文**

`FastAPIHelper` 是 `FastAPI` 的子类。它保存一个 `response_provider`，再通过 `use_post(...)`、`use_get(...)`、`use_sse(...)`、`use_websocket(...)` 把 `Agent`、`ModelRequest`、`TriggerFlow`、`TriggerFlowExecution` 或 generator 函数暴露成路由。

## 最小

```python
from agently import Agently
from agently.integrations.fastapi import FastAPIHelper

agent = Agently.create_agent()

app = FastAPIHelper(response_provider=agent)
app.use_post("/chat")
```

用 `uvicorn module:app` 跑。POST body 的默认形态是：

```json
{
  "data": {
    "input": "你好"
  },
  "options": {}
}
```

只创建 `FastAPIHelper(...)` 不会自动注册路由；需要显式调用 `use_post` / `use_get` / `use_sse` / `use_websocket`。

## 默认响应形态

成功：

```json
{
  "status": 200,
  "data": <序列化后的响应>,
  "msg": null
}
```

错误：

```json
{
  "status": 422,
  "data": null,
  "msg": "...错误信息...",
  "error": { "type": "ValueError", "message": "...", "args": [...] }
}
```

| 异常 | 默认状态码 |
|---|---|
| `ValueError` | 422 |
| `TimeoutError` | 504 |
| 其他 | 400 |

包装是 JSON-safe —— 值经 `fastapi.encoders.jsonable_encoder`。

## TriggerFlow execution

`response_provider` 是 `TriggerFlow` 时，helper 每个请求 build 一个 execution，响应形态由 close snapshot 决定：

```python
flow = TriggerFlow(name="answer")
# ... 定义 chunk ...

app = FastAPIHelper(response_provider=flow)
```

响应中的 `data` 直接承载 **close snapshot**。早期版本试图把 TriggerFlow 输出经契约约束成单一 `result` 字段 —— 已不再如此。需要特定形态时在自己的 response wrapper 里投影：

```python
def project_snapshot(response_or_exception):
    if isinstance(response_or_exception, Exception):
        return {"status": 400, "data": None, "msg": str(response_or_exception)}
    snapshot = response_or_exception
    if isinstance(snapshot, dict):
        return {"status": 200, "data": {"answer": snapshot.get("answer")}, "msg": None}
    return {"status": 200, "data": snapshot, "msg": None}

app = FastAPIHelper(response_provider=flow, response_warper=project_snapshot)
app.use_post("/answer")
```

传入自定义 `response_warper` 后，成功与异常两条路径都由这个函数负责；默认 `{status, data, msg, error}` 包装不再自动叠加。

`contract.initial_input` 与 `contract.stream` 仍约束输入与流。close-snapshot-as-`data` 改动只影响结果侧。

## 流式响应

generator 函数与 async generator 包装为 `StreamingResponse`：

```python
async def stream_answer(request_data):
    response = (
        agent
        .input(request_data["data"])
        .output({"title": (str, "标题", True), "body": (str, "正文", True)})
        .get_response()
    )
    async for item in response.get_async_generator(type="instant"):
        if item.is_complete:
            yield {"path": item.path, "value": item.value}

app = FastAPIHelper(response_provider=stream_answer)
app.use_sse("/answer/stream")
```

每条 yield 项 JSON 编码后作为流式 chunk 发送。配 `text/event-stream` 给 SSE 消费者；helper 处理分帧。

## WebSocket

用 `.use_websocket("/ws")` 注册 WebSocket 路由。连接、发 JSON `{"data": ..., "options": {...}}`，接收 stream 项。聊天 UI 与单连接多轮场景适用。

可运行 WS 样例见仓库的 `examples/fastapi/...`。

## 自定义 request model

helper 默认接受 `{"data": <input>, "options": {...}}` 的请求体。agent 期望更丰富形态时可子类化或替换 request body model —— 见 [agently/integrations/fastapi.py](../../../agently/integrations/fastapi.py) 源码暴露的 protocol 与 ParamSpec。

## 可重用 response_warper

response wrapper 是单个函数，签名：

```python
def my_warper(response_or_exception):
    ...
    return serializable_dict
```

成功值与异常都调它。换掉时两条路径都由你拥有 —— 没有独立错误 wrapper。

## 配方

| 你想要 | 接 |
|---|---|
| 一个 agent，一个端点 | `FastAPIHelper(response_provider=agent).use_post("/chat")` |
| 把结构化字段流向 UI | 包一个用 `get_async_generator(type="instant")` 的 generator |
| 长跑 flow 带进度事件 | `response_provider=flow` 并从自定义 generator 消费 `get_async_runtime_stream(...)` |
| 严格响应 schema | 提供自定义 `response_warper` 校验并整形 |

## 另见

- [TriggerFlow 事件与流](../triggerflow/events-and-streams.md) —— 转发到 SSE 的 runtime stream
- [Async First](../start/async-first.md) —— wrapper 中何时用 async getter
- [Action Runtime](../actions/action-runtime.md) —— 端点包装的 agent 用 tool 时
