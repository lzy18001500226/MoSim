---
title: 术语表
description: Agently 术语参考，含 seal、runtime resources、ensure、action runtime 三层等较新概念。
keywords: Agently, 术语表, lifecycle, runtime resources, ensure
---

# 术语表

> 语言：[English](../../en/reference/glossary.md) · **中文**

按字母顺序排列。如果某个术语相对旧文档发生了语义变化，词条里会指出。

## Action Runtime

Agently 三层 Action 栈的中间层：`TriggerFlow`（顶，编排）→ `ActionRuntime`（规划 + 派发）→ `ActionExecutor`（原子后端执行）。`ActionFlow` 是 runtime 与 flow 之间的桥。

`ActionRuntime`、`ActionFlow`、`ActionExecutor` 是当前的公开 plugin type。旧的 `ToolManager` plugin type 仅作为遗留兼容保留并发出 deprecation 警告。详见 [Action Runtime](../actions/action-runtime.md)。

## auto_close / auto_close_timeout

TriggerFlow execution 的设置。`auto_close=True`（默认）时，execution 在空闲超过 `auto_close_timeout` 秒后自动关闭。隐式 execution 语法糖（`flow.start()` / `flow.async_start()`）默认 `auto_close_timeout=0.0`。`flow.start(auto_close=False)` 是非法用法，会直接报错。

## Close snapshot

`execution.close()` / `execution.async_close()` 返回的 dict，封装该 execution 的最终 state。如果通过已弃用的 `set_result()` 或 `.end()` 写入了兼容结果，它会以 `"$final_result"` key 出现在 snapshot 里。详见 [Lifecycle](../triggerflow/lifecycle.md)。

## ensure（第三槽）

`(TypeExpr, "description", True)` 中第三槽是 `ensure` 标记——表明该叶子是必需字段。带 `ensure` 的叶子会被编译进 `ensure_keys`（含数组通配如 `resources[*].url`）。YAML / JSON 形式：`$ensure: true`。

它**不是**默认值。旧的「第三槽 = default value」约定已不再支持，YAML 里也不再支持 `$default`。详见 [Schema as Prompt](../requests/schema-as-prompt.md)。

## Execution

TriggerFlow 的一次执行实例。由 `flow.create_execution(...)` 创建。生命周期状态：`open → sealed → closed`。

## flow_data

Flow scope 的共享数据。调用 `get_flow_data(...)` / `set_flow_data(...)` 等会触发 `RuntimeWarning`，因为该值在 flow 的所有 execution 之间共享，会引发并发、保存恢复、分布式调度上的问题。明确希望共享时可传 `no_warning=True` 关掉警告。execution-local 数据请用 `state`。

## Hidden execution sugar（隐式 execution 语法糖）

`flow.start()` / `flow.async_start()` 内部创建一次性 execution、跑到 close、返回 close snapshot。适合脚本和 one-shot。不适合需要 pause 等待人工输入、依赖外部 `emit()`、或需要外部持有 execution handle 的 flow——这些场景请用 `flow.start_execution(...)`。

## OpenAICompatible / AnthropicCompatible

三个协议层 Model Request 插件：`OpenAICompatible`、`OpenAIResponsesCompatible`、`AnthropicCompatible`。多数 Chat Completions 兼容 provider 配置 `OpenAICompatible`；Responses API 形态用 `OpenAIResponsesCompatible`；Claude 配置 `AnthropicCompatible`。详见 [模型概览](../models/overview.md)。

## Runtime resources

Execution-local 的活对象存储——数据库 client、回调、socket、函数指针、cache 句柄。Runtime resources **不**可序列化、**不**进 close snapshot，也**不**进 save/load checkpoint；只记录 `resource_keys`。`load()` 后调用方必须重新注入。

这是和 `state`、`flow_data` 不同的第三类概念。详见 [State 与 Resources](../triggerflow/state-and-resources.md)。

## Runtime stream

每个 execution 一条流，由 chunk 通过 `data.put_into_stream(...)` / `data.async_put_into_stream(...)` emit；通过 `execution.get_runtime_stream(...)` / `execution.get_async_runtime_stream(...)` 消费。该流在 `execution.close()` 时关闭。

## seal / sealed

中间生命周期状态。`execution.seal()` / `execution.async_seal()` 拒收新外部事件，但允许已接受事件、内部 emit 链与已注册 task 继续 drain。它**不**关 runtime stream，也**不**冻结 close snapshot——后两者发生在 `close()`。

## Schema as Prompt

Agently prompt 侧结构化 authoring 的当前命名方式：嵌套 dict + 叶子 `(TypeExpr, "description", True)`，第三槽是 `ensure`。旧版「Agently DSL」试图把 `.output()`、TriggerFlow contract、外部 schema 统一成同一 IR 的方向已归档。

## state

Execution-local、可序列化、可快照的数据面。推荐入口：`data.async_set_state(...)` 写入、`data.get_state(...)` 读取。State 是 close snapshot 的来源，也是 `save()` / `load()` 往返的主体。

## TriggerFlow

编排层。负责分支、并发、批处理、循环、子流、暂停恢复、持久化、runtime stream。位于 Action Runtime 之上、应用代码之下。

## $final_result

被 deprecated 的 `set_result()` / `.end()` 写入的保留 state key。它出现在 close snapshot 里说明存在一份兼容结果。新代码应直接依赖 snapshot 本身，不要依赖这个 key。详见 [TriggerFlow 兼容](../triggerflow/compatibility.md)。

## wait_for_result=

`flow.start()`、`flow.async_start()`、`start_execution()`、`execution.start()` 等接口上 deprecated 的参数。值现在被**忽略**并发 warning；返回值形态由 `auto_close` 与「隐式语法糖 vs 显式 execution」决定。
