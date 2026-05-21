---
title: TriggerFlow Execution Result
description: 用 state 视图、兼容结果、intervention 和 metadata 读取同一个 execution 结果。
keywords: Agently, TriggerFlow, execution.result, close snapshot, result, metadata
---

# Execution Result

> 语言：[English](../../en/triggerflow/execution-result.md) · **中文**

`execution.result` 是 TriggerFlow execution 结果的多视图读取入口。
它不创建第二份结果存储，而是读取 execution 已经拥有的 state、兼容 result、
intervention ledger 和 lifecycle metadata。

简单脚本继续直接读 close snapshot：

```python
snapshot = await flow.async_start(input_data)
```

服务、UI、runtime stream 消费者，或需要从同一个 execution 读多种结果视图
的代码，保留 execution handle 并从 `execution.result` 读取：

```python
execution = flow.create_execution(auto_close=False)
await execution.async_start(input_data)
snapshot = await execution.async_close()

result = execution.result
report = result.get_state("report")
late = result.get_interventions(status="expired")
meta = result.get_meta()
```

## Readers

| Reader | 返回 |
|---|---|
| `execution.result.get_state(key=None, default=None)` | close 前读实时 state；close 后读冻结的 close snapshot。支持 dot path。 |
| `await execution.result.async_get_final_result(timeout=None)` | 兼容 final result：先读 `"$final_result"`，再读显式内部 result，close 后回退 close snapshot。 |
| `execution.result.get_final_result(timeout=None)` | `async_get_final_result(...)` 的同步包装。 |
| `execution.result.get_interventions(...)` | 启用 intervention ledger 时返回 ledger 记录；否则返回空列表。 |
| `execution.result.get_latest_intervention(default=None, **filters)` | 最后一条匹配的 intervention 记录，或 `default`。 |
| `execution.result.get_meta()` | execution id、flow name、status、lifecycle state、时间戳、close reason、state version 等 metadata。 |

## Snapshot 与 Final Result

close snapshot 仍然是 TriggerFlow 的规范完成态：

```python
snapshot = await execution.async_close()
```

`async_get_final_result()` 用于兼容旧 `.end()` 和 `set_result()` flow。它保留旧
查找顺序，但让兼容读取意图更明确：

```python
final = await execution.result.async_get_final_result()
```

新代码优先使用有意义的 state key 和 close snapshot。只有桥接兼容代码时才读
final result。

实时进度事件继续使用 `execution.get_async_runtime_stream(...)`。
`execution.result` 不再新增第二套 stream generator 入口。

## Metadata

metadata 不写入 close snapshot：

```python
meta = execution.result.get_meta()
```

它适合服务日志、UI 标签和 lifecycle 诊断，不会把系统字段混入应用 state。

## 另见

- [Lifecycle](lifecycle.md) - start、seal、close 与 close snapshot
- [State 与 Resources](state-and-resources.md) - 选择 state key
- [Runtime Intervention](runtime-intervention.md) - intervention ledger 如何写入
- [兼容](compatibility.md) - 从 `.end()` 与 `set_result()` 迁移
