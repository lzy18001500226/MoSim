---
title: Requests 概览
description: 一次 Agently 请求的组成、发送与消费方式。
keywords: Agently, request, agent, response, output, validate, session
---

# Requests 概览

> 语言：[English](../../en/requests/overview.md) · **中文**

一次 Agently 请求由四个部分组成：

1. **Prompt** — 你说给模型的内容。由分层槽位组成：`role` / `system`、`info`、`instruct`、`input`、`output` schema。详见 [Prompt 管理](prompt-management.md)。
2. **Output schema** — 你想要的结构。由嵌套 dict + `(type, "desc", ensure)` 叶子构成。详见 [Schema as Prompt](schema-as-prompt.md)。
3. **Validation 流水线** — `output()` 严格解析 → `ensure_keys` → `.validate(...)` 自定义校验 → 重试。详见 [输出控制](output-control.md)。
4. **Response** — text、structured data、metadata、流式事件。可通过 `response.result` 复用。详见 [模型响应](model-response.md)。

## 最小写法

```python
from agently import Agently

agent = Agently.create_agent()

result = (
    agent
    .input("用三条要点总结这篇文章。")
    .output({
        "title": (str, "标题", True),
        "bullets": [(str, "要点", True)],
    })
    .start()
)
```

这一条链覆盖了上述四部分。`input()` 填 prompt 的 input 槽，`output()` 定义 schema（含 `ensure` 标记），`start()` 发送请求、跑 validation 流水线、必要时重试，并返回解析后的 dict。

## 该读哪一页

| 你想 … | 去看 |
|---|---|
| 在 agent 与单次请求间分层 prompt | [Prompt 管理](prompt-management.md) |
| 理解 `(type, "desc", True)` 叶子和 YAML 写法 | [Schema as Prompt](schema-as-prompt.md) |
| 加业务校验、控制重试、决定 fail open 还是 hard | [输出控制](output-control.md) |
| 一次响应同时用作 text + data + metadata，或字段流式消费 | [模型响应](model-response.md) |
| 多轮对话与 memo | [会话记忆](session-memory.md) |
| 干净地注入背景信息 | [Context Engineering](context-engineering.md) |

## Sync vs async

上面的链以 `.start()` 结尾，是同步。服务和流式 UI 用 `.async_start()`，或者拿一个 `response = ....get_response()` 复用，再 `await response.result.async_get_data()`。详见 [Async First](../start/async-first.md)。

## 这一层在栈里的位置

Request 是 Agently 提供的最小单位。多次请求可以共享一个 Session（多轮）。需要分支、并发、暂停恢复时升到 [TriggerFlow](../triggerflow/overview.md)。需要模型调工具或 MCP 时接入 [Action Runtime](../actions/action-runtime.md)。

但上层每一层最终都依赖 request 本身做对了事。先把这一层做对。
