---
title: TriggerFlow 概览
description: TriggerFlow 是什么、何时该用、它和单次请求与 action runtime 的关系。
keywords: Agently, TriggerFlow, workflow, 编排, durable execution
---

# TriggerFlow 概览

> 语言：[English](../../en/triggerflow/overview.md) · **中文**

TriggerFlow 是 Agently 的编排层，负责：

- 分支（`if/elif/else`、`match/case`）
- 并发（`batch`、`for_each`）
- 事件驱动分支（`when(...)`）
- runtime stream（向消费者发送 live 数据）
- 暂停 / 恢复（人工介入、外部事件）
- 保存 / 恢复（跨重启的 durable execution）
- 子流组合

它**位于** action runtime **之上** —— 你的 flow 可以在 chunk 内调 agent、tool、MCP 等。它**位于**应用代码**之下** —— 应用决定跑哪个 flow、传什么。

## 何时使用

| 你有 | 用 |
|---|---|
| 单次模型调用（带重试 / 校验） | 一个 request，不是 flow |
| 2-3 步线性管道、无 fan-out | 有时 flow 是 overkill；考虑纯 async |
| 基于中间结果的分支 | TriggerFlow `if_condition` 或 `match` |
| N 个输入的并发 | TriggerFlow `for_each` / `batch` |
| 长跑且有人工审批 | TriggerFlow `pause_for` |
| 需要跨进程重启存活 | TriggerFlow `save` / `load` |
| 给 UI / SSE 推 live 事件流 | TriggerFlow runtime stream |

右栏都不沾就留在 request 层。

Dynamic Task 是 Agently 独立的一等能力面，面向模型生成或应用提交的 DAG
数据。当计划本身需要规划、校验、裁剪和执行时，使用
`Agently.create_dynamic_task(...)`。Dynamic Task 内部以 TriggerFlow 作为执行
基座，但它不是 TriggerFlow 子 API。见 [Dynamic Task](../dynamic-task/README.md)。

## 心智模型

```text
┌──────────────────────────────────────┐
│ 应用代码                              │
│   create execution → start → close   │
└────────────────┬─────────────────────┘
                 │
   ┌─────────────▼──────────────┐
   │  TriggerFlow execution     │
   │  open → sealed → closed    │
   │   • state（snapshot）       │
   │   • runtime_resources       │  ◄── 注入的 live 对象
   │   • runtime stream          │  ◄── chunk 推出的 item
   │   • pending interrupts      │
   └─────────────┬──────────────┘
                 │
   chunk（你写的 async 函数）调 agent、tool、外部 API，
   再更新 state 和 / 或 emit 事件
```

`TriggerFlow` 对象是**定义** —— handler 链与分支。`execution` 是该定义的一次**运行**。同一个 flow 可以有多个并发 execution。

## Hello flow

```python
import asyncio
from agently import TriggerFlow, TriggerFlowRuntimeData


async def hello():
    flow = TriggerFlow(name="hello")

    async def greet(data: TriggerFlowRuntimeData):
        await data.async_set_state("greeting", f"Hello, {data.input}!")

    flow.to(greet)

    execution = flow.create_execution()
    await execution.async_start("World")
    snapshot = await execution.async_close()
    print(snapshot["greeting"])  # Hello, World!


asyncio.run(hello())
```

发生了什么：

1. `TriggerFlow(name=...)` 定义一个 flow。
2. `flow.to(greet)` 链入 handler。handler 收到 `data: TriggerFlowRuntimeData`，里面 `data.input` 是 `start()` 传入的值。
3. `flow.create_execution()` 创建可运行 execution。
4. `async_start("World")` 启动；`async_close()` 等所有事 drain 完，返回 close snapshot —— 一个 dict，含所有 handler 设置的 state。

## 隐式 execution 语法糖

不需要显式控制 execution 时，`flow.start(...)` / `flow.async_start(...)` 创建临时 execution、跑到 close、返回 snapshot：

```python
snapshot = await flow.async_start("World")
print(snapshot["greeting"])
```

脚本里用这个。flow 会暂停等待人工输入或依赖外部事件时**不要**用 —— 见 [Lifecycle](lifecycle.md)。

## chunk 能做什么

handler 内 `data` 暴露：

| API | 用途 |
|---|---|
| `data.input` | 流入的值（start 的 input，或上一 chunk 的返回） |
| `data.async_set_state(key, value)` / `get_state(key)` | execution-local 可序列化 state |
| `data.async_emit(event, payload)` | 触发 `when(event)` 分支 |
| `data.async_put_into_stream(item)` | 推到 runtime stream |
| `data.async_pause_for(type=..., resume_to=...)` | 暂停等待外部图恢复 |
| `data.require_resource(name)` | 取你注入的 live 对象 |
| `return value` | 成为下一 chunk 的 `data.input` |

完整词汇表见本节其余页。

## 接下来读哪

- [Lifecycle](lifecycle.md) —— open/sealed/closed 三态与 5 个入口
- [State 与 Resources](state-and-resources.md) —— 三种存储层与如何选
- [事件与流](events-and-streams.md) —— `emit`、`when`、runtime stream
- [模式](patterns.md) —— 分支、循环、batch、fan-out
- [Sub-Flow](sub-flow.md) —— flow 组合
- [持久化与 Blueprint](persistence-and-blueprint.md) —— save/load 与配置导出
- [Pause 与 Resume](pause-and-resume.md) —— 人工介入
- [模型集成](model-integration.md) —— 在 chunk 内调 agent
- [兼容](compatibility.md) —— 从 `.end()` / `set_result()` / `wait_for_result=` / 旧 `runtime_data` 迁移
