---
title: 模型集成
description: 在 TriggerFlow chunk 内调 agent 与 model request。
keywords: Agently, TriggerFlow, agent, model, request, async, instant
---

# 模型集成

> 语言：[English](../../en/triggerflow/model-integration.md) · **中文**

chunk handler 是普通 async 函数。你可以在里面调任何 agent / request / response API。好的模式集中在三件事：async（因为周围 flow 是 async）、结构化输出（因为下一 chunk 期望已知结构）、用户真受益时再 streaming。

## 最小模式

```python
from agently import Agently, TriggerFlow, TriggerFlowRuntimeData

agent = Agently.create_agent()


async def classify(data: TriggerFlowRuntimeData):
    result = await (
        agent
        .input(data.input)
        .output({
            "category": (str, "分类", True),
            "confidence": (float, "0.0 到 1.0"),
        })
        .async_start()
    )
    await data.async_set_state("classification", result)
    return result


flow = TriggerFlow(name="classify")
flow.to(classify)
```

agent 在模块层创建以便跨 execution 复用。`await ... async_start()` 返回解析后的 dict。dict 进 state 进 close snapshot，也作为返回值传给下一 chunk 的 `data.input`。

## 永远用 async

周围 flow 是 async。chunk 内调 sync `start()` 能跑但会阻塞 event loop，损失并发。用 `async_start()` / `async_get_data()` / `get_async_generator(...)`。详见 [Async First](../start/async-first.md)。

## 把结构化字段流向 runtime stream

消费 runtime stream 的 UI 受益于增量更新时，把已完成的结构化字段推出去：

```python
async def draft_with_streaming(data: TriggerFlowRuntimeData):
    response = (
        agent
        .input(data.input)
        .output({
            "title": (str, "标题", True),
            "body": (str, "正文", True),
        })
        .get_response()
    )

    async for item in response.get_async_generator(type="instant"):
        if item.is_complete:
            await data.async_put_into_stream({"path": item.path, "value": item.value})

    final = await response.async_get_data()
    await data.async_set_state("draft", final)
    return final
```

`type="instant"` 在每叶子完成解析时发事件 —— runtime stream 消费者看到 `title` 完成时 `body` 还没好。stream 结束后 `async_get_data()` 返回缓存的解析 dict（不再发请求）。

## 在一个 chunk 内复用 response

调一次 `get_response()`，从 `response.result` 读 text + data + meta 不再发请求。详见 [模型响应](../requests/model-response.md)：

```python
async def step(data):
    response = agent.input(data.input).output({...}).get_response()
    text = await response.result.async_get_text()
    obj = await response.result.async_get_data()
    meta = await response.result.async_get_meta()
    await data.async_set_state("text", text)
    await data.async_set_state("obj", obj)
    await data.async_set_state("meta", meta)
```

## 按 execution 定制 agent

flow 的 chunk 需要按 execution 用不同模型配置时，通过 runtime resource 注入：

```python
execution = flow.create_execution(
    runtime_resources={"agent": Agently.create_agent().set_settings(...)},
)


async def step(data):
    agent = data.require_resource("agent")
    return await agent.input(data.input).async_start()
```

不要把 agent 放进 `state` —— agent 持有网络 client，不适合 snapshot。用 `runtime_resources`（见 [State 与 Resources](state-and-resources.md)）。

## 校验、重试、结构化输出

`.validate(...)` 与 `ensure_keys` 在 chunk 内的工作方式与 request 层一样。retry 预算按 request 算，chunk 内的模型重试不影响 flow 其他部分。详见 [输出控制](../requests/output-control.md)。

```python
async def step(data):
    return await (
        agent
        .input(data.input)
        .output({"answer": (str, "answer", True)})
        .validate(custom_business_check)
        .async_start(max_retries=5)
    )
```

## 不要把模型 state 放进 flow_data

`flow_data` 跨 flow 所有 execution 共享并发 warning。不要用它「记住上次模型答案」 —— execution-local 用 `state`；多轮对话用真正的 session，详见 [会话记忆](../requests/session-memory.md)。

## 单 flow 多 agent

多个 chunk 可以用多个 agent —— 不同 provider、不同 prompt、不同 toolset：

```python
classifier = Agently.create_agent().set_settings("OpenAICompatible", {"model": "${ENV.CLASSIFIER_MODEL}"})
writer = Agently.create_agent().set_settings("OpenAICompatible", {"model": "${ENV.WRITER_MODEL}"})

async def classify(data):
    return await classifier.input(data.input).output({...}).async_start()

async def draft(data):
    return await writer.input(data.input).async_start()

flow.to(classify).to(draft)
```

这就是 TriggerFlow 扮演编排角色的方式：flow 持有连线，每个 agent 仍是小而聚焦的单元。

## 另见

- [Async First](../start/async-first.md) —— 为什么每个 chunk 都该用 async
- [模型响应](../requests/model-response.md) —— `get_response()` 与 `result` 缓存
- [输出控制](../requests/output-control.md) —— chunk 内 validate / retry 行为
- [State 与 Resources](state-and-resources.md) —— agent 该放哪
