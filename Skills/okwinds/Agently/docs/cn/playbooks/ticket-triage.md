---
title: 工单分流 Playbook
description: 分类输入、按结果路由、交接 —— 「结构化输入 → 结构化输出 → action」模板。
keywords: Agently, playbook, triage, classification, routing
---

# 工单分流 Playbook

> 语言：[English](../../en/playbooks/ticket-triage.md) · **中文**

## 何时用本 playbook

收到一串 item（工单、邮件、告警、请求）。每个需要：

1. 分类到一个小集合的类别。
2. 按分类选下游 handler。
3. 跑 handler（调 API、调模型、升级到人）。
4. 记录结果。

模型负责分类（可能也负责部分处理）。你想要稳定的类别、可预期的重试、决策的审计轨。

## 推荐结构

足够小，可以在两种形态间选：

- **单次请求** 类别简单且 handler 不需要流控时。
- **TriggerFlow** 每个分支需要多步、并行处理或 pause/resume。

### 单次请求形态

```python
from agently import Agently

agent = Agently.create_agent()

result = (
    agent
    .info({
        "categories": ["billing", "technical", "spam", "other"],
        "format": "仅按下面的 schema 回答。",
    }, always=True)
    .input(ticket_text)
    .output({
        "category": (str, "billing/technical/spam/other 之一", True),
        "severity": (str, "low/med/high", True),
        "summary": (str, "一行摘要", True),
    })
    .validate(ensure_known_category)
    .start()
)

route_to_handler(result["category"], result)
```

`info(always=True)` 让分类列表每次都对模型可见，不撑大每次请求。`.validate(...)` 强制 `category` 是允许字符串之一 —— 见 [输出控制](../requests/output-control.md)。

`route_to_handler(...)` 是普通 Python：一个 category → 函数的 dict。

### TriggerFlow 形态

每类处理本身有自己的步骤时：

```python
def build_flow():
    flow = TriggerFlow(name="triage")

    async def classify(data: TriggerFlowRuntimeData):
        return await classifier.input(data.input).output({
            "category": (str, "...", True),
            "severity": (str, "...", True),
            "summary": (str, "...", True),
        }).async_start()

    async def handle_billing(data):
        # 多步 billing flow ...
        await data.async_set_state("outcome", {"path": "billing", "ok": True})

    async def handle_technical(data):
        await data.async_set_state("outcome", {"path": "technical", "ok": True})

    async def handle_spam(data):
        await data.async_set_state("outcome", {"path": "spam", "ok": True})

    async def handle_other(data):
        await data.async_set_state("outcome", {"path": "other", "ok": True})

    (
        flow.to(classify)
        .match_on(lambda d: d.input["category"])
            .case("billing").to(handle_billing)
            .case("technical").to(handle_technical)
            .case("spam").to(handle_spam)
            .case_else().to(handle_other)
        .end_match()
    )

    return flow
```

每个分类处理可成长为自己的子流 —— 见 [Sub-Flow](../triggerflow/sub-flow.md)。

## 变体

### 高量 —— batch 并行

工单批量到达时 fan out 并行处理：

```python
flow.for_each(concurrency=8).to(triage_one_ticket).end_for_each().to(persist_results)
```

`concurrency` 设到模型限速与下游 API 能扛的程度。

### 部分类别需要人工批准

高风险类别（退款、关账户）暂停 flow 等人工：

```python
async def maybe_request_approval(data):
    if data.input["category"] == "refund" and data.input["amount"] > 1000:
        return await data.async_pause_for(
            type="approval",
            payload={"ticket_id": data.input["id"], "amount": data.input["amount"]},
            resume_to="next",
        )
    return data.input
```

execution 必须以 `auto_close=False` 创建（见 [Pause 与 Resume](../triggerflow/pause-and-resume.md)）。

### 审计轨

把每个决策推到 runtime stream 让外部 logger 记录：

```python
async def classify(data):
    result = await classifier.input(data.input).output({...}).async_start()
    await data.async_put_into_stream({"event": "classified", "result": result})
    return result
```

flow 之外消费 `execution.get_async_runtime_stream(...)`。

## 不要做什么

- handler 都是单步时不要加 TriggerFlow。直接 Python 路由 —— 上面单次请求形态够了。
- 不要让模型做路由逻辑（「现在告诉我要做什么」）。拿干净的结构化答案（`category`、`severity`、`summary`），让你的代码路由。模型擅长分类；编排逻辑属于代码。
- 不要把分类器模型名放进 `flow_data`。用 `runtime_resources`（或在模块级 pin 住 agent）。

## 交叉链接

- [输出控制](../requests/output-control.md) —— `.validate(...)` 强制类别
- [Schema as Prompt](../requests/schema-as-prompt.md) —— 分类字段的 `(type, "...", True)`
- [TriggerFlow 模式](../triggerflow/patterns.md) —— `match` 与 `case`
- [Sub-Flow](../triggerflow/sub-flow.md) —— 每分类处理变大时
