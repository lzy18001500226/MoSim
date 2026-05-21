---
title: Context Engineering
description: 怎么把背景知识送到模型面前但不撑爆 prompt。
keywords: Agently, context, info, session, KB, retrieval, instruct
---

# Context Engineering

> 语言：[English](../../en/requests/context-engineering.md) · **中文**

模型只看得见上下文窗口里的内容。Context engineering 就是决定「放什么、放哪、不放什么」的纪律。

## 上下文从哪来

| 来源 | 落在哪 | 生命周期 |
|---|---|---|
| `role` / `system` 槽 | system 消息 | agent 持久 |
| `info` 槽 | system 或 user（实现细节） | 持久或单次 |
| `instruct` 槽 | user 消息 | 持久或单次 |
| `input` 槽 | user 消息 | 单次 |
| Session chat history | user/assistant 消息 | 跨请求累积 |
| Session memo | system 消息 | 持久，由自定义 resize handler 写入 |
| 知识库检索 | 检索代码注入 | 单次按需 |
| 工具 / MCP 结果 | tool 消息 | 单次工具循环内累积 |

按职责选槽：

- **role / system** —— 模型是谁、硬性规则（语气、人设、拒绝模式）。
- **info** —— 跨调用不变的事实（产品目录、严重度等级、格式约定）。
- **instruct** —— 这类请求该怎么做（步骤、顺序、输出风格）。
- **input** —— 每次调用都变的单一 payload。
- **chat history** —— 当前会话里用户与模型说过的话。
- **memo** —— 应用自定义压缩后的长期上下文。
- **KB** —— 大规模、不总是相关的知识。

不要全往 `input` 塞。也不要把每次都变的 payload 写进 `info`。

## 何时用什么

| 你有的内容 | 放进 |
|---|---|
| agent 的人设、语气、能力规则 | `role`（`always=True`） |
| 模型必须知道的固定枚举（如严重度代码） | `info`（`always=True`） |
| 一类任务的步骤指令 | `instruct`（`always=True` 当 agent 只做这类任务） |
| 一次调用的可变 payload | `input` |
| 上几轮对话 | session chat history |
| 100k tokens 公司文档 | KB + 检索，**不**放进 prompt |
| 当前轮检索到的相关事实 | 仅本次请求的 `info` |

## 让 info 可 diff

`info` 接受 dict，框架渲染。这比手工把 JSON 拼进 prompt 好 —— diff 可读，框架可一致地渲染成 YAML / JSON / 伪表格。

```python
agent.info({
    "severities": ["P0", "P1", "P2", "P3"],
    "format": "用 markdown bullet，无开场白。",
}, always=True)
```

## 不要手抄工具目录

用了 actions / tools 后，框架会在模型规划工具调用时自动注入工具目录。不要手工把工具描述抄进 `info`。详见 [Action Runtime](../actions/action-runtime.md)。

## Session vs KB vs `info`

| 场景 | 最合适的位置 |
|---|---|
| 「记住用户在这次对话里报的姓名」 | session chat history |
| 「跨多次对话记住用户偏好」 | 自定义 session resize / memo，或应用层用户画像 |
| 「从知识库里查到相关片段」 | KB 检索 → 把片段放进单次 `info` |
| 「模型每次都要看的固定列表」 | `info(always=True)` |
| 「用户刚发了 500 字的问题」 | `input` |

## 压缩优于截断

上下文窗口快满时：

- 默认 session 只按 `session.max_length` 做窗口裁剪；需要摘要时，注册自定义 resize handler，把摘要写入 session `memo`。详见 [会话记忆](session-memory.md)。
- 一次性长输入，先摘要再请求，不要中间截断。

## 单次 info 而不污染 agent

```python
result = (
    agent
    .info({"retrieved_snippets": chunks}, always=False)  # 仅本次
    .input(question)
    .output({...})
    .start()
)
```

不传 `always=True`，`info` 仅本次有效。

## 另见

- [Prompt 管理](prompt-management.md) —— 槽位语义详解
- [会话记忆](session-memory.md) —— chat history 与 memo
- [知识库](../knowledge/knowledge-base.md) —— 检索-后-prompt 模式
- [Action Runtime](../actions/action-runtime.md) —— 工具目录是自动注入的
