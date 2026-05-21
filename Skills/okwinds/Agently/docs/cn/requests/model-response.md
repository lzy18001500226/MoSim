---
title: 模型响应
description: 从一次响应里读 text / data / metadata 与流式事件。
keywords: Agently, response, get_response, get_data, get_text, get_meta, generator, streaming
---

# 模型响应

> 语言：[English](../../en/requests/model-response.md) · **中文**

`agent.input(...).start()` 是便捷写法 —— 跑请求并直接返回解析后的 dict。其他更有意思的事（text、metadata、流式、复用）都走 `get_response()`。

## 两种消费方式

```python
# 方式 A：一次性，立即返回 parsed data
result = agent.input("...").output({...}).start()

# 方式 B：拿一个可复用的 response
response = agent.input("...").output({...}).get_response()
text = response.result.get_text()
data = response.result.get_data()
meta = response.result.get_meta()
```

非琐碎代码默认走方式 B。模型调用在你第一次从 `response.result` 消费时**懒触发**，结果**缓存**，后续读不会重发请求。

## 读取方法

| 方法 | 返回 |
|---|---|
| `response.result.get_text()` | 完整纯文本 |
| `response.result.get_data()` | 解析后的结构化 dict（用了 `output()` 时） |
| `response.result.get_data_object()` | Pydantic 实例（`output()` 接受 `BaseModel` 时） |
| `response.result.get_meta()` | usage / model 信息 / 时间等 |

每个都有 async 版本：`async_get_text()`、`async_get_data()`、`async_get_data_object()`、`async_get_meta()`。

混用没问题——它们都从同一份缓存里读：

```python
response = agent.input("...").output({...}).get_response()
data = response.result.get_data()        # 触发请求
text = response.result.get_text()        # 已缓存
meta = response.result.get_meta()        # 已缓存
```

`.validate(...)` 每个 response 也只跑一次——校验的就是这份缓存结果。

## 流式

`response.result.get_generator(type=...)`（sync）与 `get_async_generator(type=...)`（async）发流式事件。`type` 决定你看到什么：

| `type` | 你拿到的 | 适合 |
|---|---|---|
| `"delta"` | 原始 token delta | 终端打字机 UX |
| `"instant"` | 每个叶子解析完成后的结构化节点 | 字段级 UI 更新 |
| `"streaming_parse"` | 节点树就地增量更新 | 增量 dict 读取 |
| `"specific"` | `(event, data)` 元组，按事件过滤（`delta`、`reasoning_delta`、`tool_calls` 等） | 精确订阅特定事件 |
| `"original"` | 原始 provider 事件 | 调试 / passthrough |
| `"all"` | 所有事件带类型标签 | 完整日志 |

### Delta 例子

```python
gen = agent.input("讲个递归故事。").get_generator(type="delta")
for delta in gen:
    print(delta, end="", flush=True)
```

### Instant 例子（结构化）

```python
gen = (
    agent.input("给一个定义和三条 tips。")
    .output({
        "definition": (str, "定义", True),
        "tips": [(str, "tip", True)],
    })
    .get_generator(type="instant")
)
for item in gen:
    if item.is_complete:
        print(item.path, "=", item.value)
```

`item` 暴露 `.path`（如 `"tips[0]"`）、`.wildcard_path`（`"tips[*]"`）、`.value`、`.delta`、`.is_complete`。`.is_complete` 用来「叶子完整解析后才反应」。

### Specific 例子（事件）

```python
gen = agent.input("打个招呼。").get_generator(type="specific")
for event, data in gen:
    if event == "delta":
        print(data, end="", flush=True)
    elif event == "reasoning_delta":
        print("[reasoning]", data, end="", flush=True)
    elif event == "tool_calls":
        print("[tool call]", data)
```

## Async 流式

同样的 generator 改 async：

```python
import asyncio

async def main():
    response = agent.input("...").output({...}).get_response()
    async for item in response.get_async_generator(type="instant"):
        if item.is_complete:
            print(item.path, item.value)

asyncio.run(main())
```

服务和 TriggerFlow 场景应走 async —— 见 [Async First](../start/async-first.md)。

## 并发

因为 `get_response()` 只在你消费时才发请求，可以先建多个 response，再并发消费：

```python
import asyncio

async def ask(prompt):
    r = agent.input(prompt).get_response()
    return await r.result.async_get_text()

results = await asyncio.gather(
    ask("总结递归。"),
    ask("给一个 Python 例子。"),
)
```

这是标准 async 模式，Agently 没有特别封装。

## 能复用就别重发

```python
# 不好——同一请求跑了三次
text = agent.input("...").start()
data = agent.input("...").output({...}).start()
meta = agent.input("...").output({...}).get_response().result.get_meta()

# 好——跑一次，读三种视图
response = agent.input("...").output({...}).get_response()
text = response.result.get_text()
data = response.result.get_data()
meta = response.result.get_meta()
```

## 另见

- [Async First](../start/async-first.md) —— 何时切到 `get_async_generator(...)`
- [输出控制](output-control.md) —— 「模型返回」与「你读到」之间发生了什么
- [Schema as Prompt](schema-as-prompt.md) —— `output()` 能接受什么
