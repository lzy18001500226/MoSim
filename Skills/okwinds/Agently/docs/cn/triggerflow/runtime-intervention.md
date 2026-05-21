---
title: Runtime Intervention
description: 在不暂停、不改写运行中 graph 的前提下，向 TriggerFlow execution 补充上下文。
keywords: Agently, TriggerFlow, runtime intervention, intervention_point, 人工上下文
---

# Runtime Intervention

> Languages: [English](../../en/triggerflow/runtime-intervention.md) · **中文**

Runtime intervention 让外部代码在 execution 仍然 open 时补充上下文。TriggerFlow 会立刻记录这条上下文，然后在安全边界让后续 chunk 可见。

用户在 workflow 运行中补充备注、修正、附件摘要或其他上下文时，用 runtime intervention。workflow 必须停下来等待外部答案时，用 [Pause 与 Resume](pause-and-resume.md)。

## 模式

Runtime intervention 默认关闭，除非创建 execution 时显式开启，或 flow 声明了显式 intervention point：

```python
execution = flow.create_execution(
    auto_close=False,
)
```

`intervention_mode="planned"` 只在显式 intervention point 插入 pending 上下文：

```python
(
    flow
    .to(extract_terms)
    .intervention_point(name="before_risk", target="before_risk")
    .to(risk_assessment)
)
```

flow 声明了 `intervention_point(...)` 时，如果 `create_execution(...)` 省略 `intervention_mode`，TriggerFlow 会推断为 planned 模式。只有在明确希望本次 execution 禁用 intervention 时，才传 `intervention_mode=None`。

`intervention_mode="auto"` 会在 chunk dispatch 前检查 pending intervention。带 target 的 intervention 会在第一个匹配 operator id、name、kind、group id 或 group kind 的 operator 前插入；不带 target 的 intervention 会在下一个 chunk 边界插入。声明了 `intervention_point(...)` 的 flow 不能用 auto 模式。

## 添加上下文

```python
await execution.async_intervene(
    {"text": "Attachment A is the latest price table."},
    author="reviewer",
    target="before_risk",
)
```

`intervene(...)` 只记录 pending ledger item。它不会 emit 事件，不会暂停 graph，也不会改写 `data.input` 或 `data.value`。

## 读取与消费

chunk 通过 `data.interventions` 或 `data.get_interventions(...)` 读取已经插入的 intervention：

```python
async def risk_assessment(data: TriggerFlowRuntimeData):
    supplements = data.get_interventions(status="inserted", target="before_risk")
    result = await assess_with_model(
        {
            "terms": data.input,
            "supplements": [item["payload"] for item in supplements],
        }
    )
    for item in supplements:
        await data.async_mark_intervention_consumed(
            item["id"],
            status="applied",
        )
    return result
```

读取不会自动消费。用 `mark_intervention_consumed(...)` 写入按 consumer 记录的审计项，status 支持 `"applied"` 和 `"ignored"`。Runtime data 会默认把 `consumer` 填成当前 chunk 名；execution 级调用仍需要显式传入 consumer。

## Close 与持久化

`close()` 时仍然 pending 的 intervention 会变成 `"expired"`。ledger 仍可通过 `execution.result.get_interventions(...)` 读取，也会放进 close snapshot 的 `"$interventions"`。

`execution.save()` / `execution.load()` 会保留 intervention mode、ledger、version counter、插入 metadata、过期状态和 consumer metadata。运行时 policy callable 不会序列化；恢复 auto-mode execution 时，如果没有重新传入 callable，会使用内置 policy。

## Runtime Stream

intervention 生命周期会进入 fail-open runtime stream item：

```python
{
    "type": "intervention",
    "action": "append",  # append | insert | expire | consume | reject
    "execution_id": execution.id,
    "intervention": {...},
}
```

旧版 stream consumer 可以忽略未知 `type`。Observation event 使用 `triggerflow.intervention_received`、`triggerflow.intervention_inserted`、`triggerflow.intervention_expired`、`triggerflow.intervention_consumed` 和 `triggerflow.intervention_rejected`。

## 参见

- `examples/step_by_step/11-triggerflow-21_document_review_runtime_intervention.py` —— planned 模式文档审查场景
- `examples/step_by_step/11-triggerflow-22_ticket_triage_auto_intervention.py` —— auto 模式工单分级场景
- [Pause 与 Resume](pause-and-resume.md) —— 必须等待外部答案并恢复 graph
- [事件与流](events-and-streams.md) —— stream 消费
- [Execution Result](execution-result.md) —— result 侧 intervention reader
