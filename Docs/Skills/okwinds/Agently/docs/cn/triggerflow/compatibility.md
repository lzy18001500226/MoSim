---
title: TriggerFlow 兼容
description: 从 .end()、set_result()、wait_for_result=、runtime_data 迁移到新 lifecycle。
keywords: Agently, TriggerFlow, 兼容, deprecated, end, set_result, wait_for_result, runtime_data
---

# 兼容

> 语言：[English](../../en/triggerflow/compatibility.md) · **中文**

这是文档中**唯一**把 deprecated TriggerFlow API 当作起点出现的页 —— 仅用于迁移。其他页应该都已经在新 API 上。

高层转变：新 lifecycle 把 **close snapshot** 当作规范返回值。试图算单一「result」的旧 API —— `.end()`、`set_result()`、`get_result()`、`wait_for_result=` —— 作为兼容入口保留，但不推荐用于新代码。

Deprecation warning 按 deprecated API 在每个 Python 进程内只发一次。重复调用继续工作但不重复刷同一条 warning；不同 deprecated API 仍会各自提示一次。如果生产环境需要全局关闭 Agently deprecation warning，设置 `runtime.show_deprecation_warnings=False`。

## .end() —— 定义期 DSL，不是 lifecycle 动作

`.end()` 历史上被用作「结束」flow 的方式。它当前实际行为更窄：

- 它是 **定义期** DSL —— 在 build time 给 flow 追加一个兼容 result sink。
- **不**等价于 `seal()`。
- **不**等价于 `close()`。
- 运行期它做的事就是把流入的值写到保留 state key `"$final_result"`。

状态：**Deprecated** —— 调用发 deprecation 警告。

### 旧

```python
flow.to(step_a).to(step_b).end()  # 把 step_b 的返回写进 "$final_result"
result = flow.start("input")
```

### 新

```python
flow.to(step_a).to(step_b)  # 不要 .end()
snapshot = flow.start("input")
# step_b 的返回值落到它写入的 state key，
# 或显式捕获：

async def step_b(data):
    await data.async_set_state("answer", do_work(data.input))
```

仍调 `.end()` 的 flow 配置继续可用 —— 值会落在 `snapshot["$final_result"]`，只是不再被框架特殊调度。

## set_result() / get_result() —— 兼容写读

`set_result(value)` 写到同一 `"$final_result"` state key。`get_result()` 读它（或回退 close snapshot）。

状态：**Deprecated** —— 都发警告。

必须桥接兼容代码时，优先用
`await execution.result.async_get_final_result()`，不要新增 `get_result()`
调用点。它保留同样的查找顺序，但兼容意图更明确。

### 旧

```python
async def worker(data):
    data.set_result({"answer": ...})
```

```python
result = execution.get_result()  # 等待并返回
```

### 新

```python
async def worker(data):
    await data.async_set_state("answer", ...)
```

```python
snapshot = await execution.async_close()
answer = snapshot["answer"]
```

如果你确实只想要单一规范结果，离场时映射一下：

```python
async def project_answer(execution):
    snapshot = await execution.async_close()
    return snapshot["answer"]
```

## wait_for_result= —— 值现在被忽略

`wait_for_result=True` / `False` 是 `start(...)` 是否等结果的旧开关。新 lifecycle 由 `auto_close` 控制返回类型。

状态：**Deprecated** —— 值被**忽略**并 warn。

### 旧

```python
result = flow.start("input", wait_for_result=True)   # 参数已无意义
```

### 新

「等并给 close snapshot」用隐式糖：

```python
snapshot = await flow.async_start("input")           # 总返回 close snapshot
```

「给我 execution 我自己 close」：

```python
execution = flow.create_execution(auto_close=False)
await execution.async_start("input")                 # 返回 execution
# ... 做事 ...
snapshot = await execution.async_close()
```

完整入口表见 [Lifecycle](lifecycle.md)。

## runtime_data —— state 的旧名

旧 `runtime_data` API（`get_runtime_data`、`set_runtime_data`、`append_runtime_data`、`del_runtime_data`）现在是现代 `state` API 的别名。仍能用但发 deprecation 警告。

状态：**Deprecated** —— `state` 别名。

### 旧

```python
async def step(data):
    await data.set_runtime_data("count", 1)
    n = data.get_runtime_data("count")
```

### 新

```python
async def step(data):
    await data.async_set_state("count", 1)
    n = data.get_state("count")           # 同步读也存在
```

语义没变，只是改名。详见 [State 与 Resources](state-and-resources.md)。

## flow_data —— risky-default，未 deprecated

`flow_data` 是另一种存储层，问题不同：flow scope（在该 flow 的**所有** execution 之间共享）。仍能用，但每次调用发 `RuntimeWarning`，因为有并发 / save-load 风险。

状态：**Risky-default** —— 能用但 warn。和 deprecation 不同。

确实需要共享 scope 时关 warning：

```python
flow.set_flow_data("shared_counter", 0, no_warning=True)
```

99% 场景对的答案是 `state`（execution-local）或 `runtime_resources`（live 对象）。详见 [State 与 Resources](state-and-resources.md)。

## close snapshot 中的 $final_result

迁移完成后，只要 execution 跑过任何 `.end()` 或 `set_result()`（包括子流或你不控的共享库代码），close snapshot 中仍会出现 `"$final_result"`。`to_sub_flow(...)` 的桥逻辑在解析 `result.<path>` write-back 时故意先查 `$final_result`，正是为让旧子流与新 state-first 父流并存。详见 [Sub-Flow](sub-flow.md)。

## 迁移清单

每个 flow：

1. 从定义中移除 `.end()`。决定哪个 state key 承载你真正想要的值。
2. 把 `set_result(x)` 替换为 `async_set_state("answer", x)`（或有意义的 key）。
3. 把 `get_result()` 替换为读 close snapshot 中相关 key。
4. 删 `wait_for_result=` 参数 —— 它已经什么都不做。
5. 把 `set_runtime_data` / `get_runtime_data` 替换为 `async_set_state` / `get_state`。
6. 审计 `flow_data` 调用。多数应改为 `state`；其余应有意 suppress warning。
7. 审计 state 中的 live 对象。挪到 `runtime_resources`。

## 另见

- [Lifecycle](lifecycle.md) —— 新入口
- [State 与 Resources](state-and-resources.md) —— 什么放哪
- [Sub-Flow](sub-flow.md) —— 桥如何处理旧子流
