---
title: TriggerFlow 编排 Playbook
description: 多步 AI 过程的结构模板，含分支、fan-out、持久化。
keywords: Agently, TriggerFlow, 编排, playbook, fan-out, 持久化
---

# TriggerFlow 编排 Playbook

> 语言：[English](../../en/playbooks/triggerflow-orchestration.md) · **中文**

## 何时用本 playbook

过程有 3 个或更多离散阶段。下列任一为真：

- 分支依赖中间模型输出。
- 需要 fan out（并行处理 N 个 item）然后收集。
- 中途需要人工或外部系统批准 / 提供输入。
- 过程足够长以致需要跨进程重启存活。
- 想在过程进行中流进度事件给 UI。

都不沾，留在 request 层 —— 见 [快速开始](../start/quickstart.md) 与 [输出控制](../requests/output-control.md)。

## 推荐结构

```text
应用
   │
   ▼
TriggerFlow 定义（一个 flow 一个 Python 模块）
   ├── prepare         ← 校验 / 归一化输入
   ├── classify        ← 模型调用：按类型路由
   ├── （按分类分支）
   │     ├── handle_A → … → finalize
   │     ├── handle_B → … → finalize
   │     └── handle_C → … → finalize
   ├── for_each items  ← 任一 handler 返回 list 时 fan out
   ├── pause_for(...)  ← 可选人工批准
   └── finalize        ← 写最终 state，推到 runtime stream

flow 之外：
   • create_execution(auto_close=False, runtime_resources={...})
   • async_start(...)
   • 消费 runtime stream 给 live UI
   • async_close() → 给 API 响应的 close snapshot
```

## 骨架

```python
from agently import TriggerFlow, TriggerFlowRuntimeData


def build_flow():
    flow = TriggerFlow(name="orchestration")

    async def prepare(data: TriggerFlowRuntimeData):
        # 校验 / 归一化输入
        await data.async_set_state("input", data.input)
        return data.input

    async def classify(data: TriggerFlowRuntimeData):
        agent = data.require_resource("agent")
        return await agent.input(data.input).output({
            "category": (str, "分类", True),
        }).async_start()

    async def handle_default(data: TriggerFlowRuntimeData):
        # ...
        await data.async_set_state("answer", "...")

    (
        flow.to(prepare)
            .to(classify)
            .match()
                .case("A").to(handle_default)
                .case("B").to(handle_default)
                .case_else().to(handle_default)
            .end_match()
    )

    return flow


async def run(input_value, agent):
    flow = build_flow()
    execution = flow.create_execution(
        auto_close=False,
        runtime_resources={"agent": agent},
    )
    await execution.async_start(input_value)
    return await execution.async_close()
```

骨架里的几个选择：

- **`auto_close=False`** —— 应用显式控制 close。任何可能消费 runtime stream item 或暂停等外部输入的场景都用这个。
- **agent 作为 runtime resource 注入** —— agent 不在 `state`（live 对象），不在 `flow_data`（共享且风险）。见 [State 与 Resources](../triggerflow/state-and-resources.md)。
- **`match()` 走分类结果** —— 离散类别用 `match`；predicate 分支用 `if_condition`。
- **每个 handler 读 `data.input`、写 state** —— handler 应小且单一职责。

## 变体

### 需要 fan out

把单 handler 替换为 `for_each`：

```python
async def list_subtasks(data):
    return data.input["subtasks"]   # list

async def handle_one(data):
    return await some_agent.input(data.input).async_start()

(
    flow.to(list_subtasks)
        .for_each(concurrency=4)
            .to(handle_one)
        .end_for_each()
        .to(collect)
)
```

`batch`、`for_each` 与并发上限见 [模式](../triggerflow/patterns.md)。

### 需要人工批准

加 `pause_for` 步骤。execution 必须用 `auto_close=False` 创建；通过 `continue_with` 和显式 `resume_to` 目标恢复。

```python
async def ask(data):
    return await data.async_pause_for(
        type="approval",
        payload={"summary": data.input["summary"]},
        resume_to="next",
    )
```

见 [Pause 与 Resume](../triggerflow/pause-and-resume.md)。

### 需要跨重启存活

在有意义的 checkpoint 保存 execution state（通常在 `pause_for` 未决时），把结果持久化到耐久存储，用 `flow.create_execution(...).load(saved)` 恢复。

```python
saved = execution.save()
db.put(execution_id, saved)

# 后续，可能在另一进程：
restored = flow.create_execution(auto_close=False, runtime_resources={...})
restored.load(db.get(execution_id))
```

恢复侧重新注入 runtime resource。见 [持久化与 Blueprint](../triggerflow/persistence-and-blueprint.md)。

### 需要流式 UI

在 FastAPI / WebSocket handler 内消费 `execution.get_async_runtime_stream(...)`。chunk 通过 `data.async_put_into_stream(...)` 推 item。见 [FastAPI 服务封装](../services/fastapi.md) 与 [事件与流](../triggerflow/events-and-streams.md)。

## 不要做什么

- 不要为「整理代码」就用子流。短 handler 内联；只有 child 有真复用契约时才用子流 —— 见 [Sub-Flow](../triggerflow/sub-flow.md)。
- 不要在 chunk 内套额外重试 —— `.start()` 已经经校验流水线重试。见 [输出控制](../requests/output-control.md)。
- 不要把 live client 放进 `state`。用 `runtime_resources`，`load()` 时重新注入。

## 交叉链接

- [TriggerFlow Lifecycle](../triggerflow/lifecycle.md) —— `auto_close` 与 5 个入口 API
- [TriggerFlow 模式](../triggerflow/patterns.md) —— 分支、fan-out、loop
- [模型集成](../triggerflow/model-integration.md) —— 在 chunk 内调 agent
- [Action Runtime](../actions/action-runtime.md) —— chunk 需要 tool 或 MCP 时
