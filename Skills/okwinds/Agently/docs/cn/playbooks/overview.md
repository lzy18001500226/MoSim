---
title: Playbooks
description: 组合 Agently 能力解决常见 AI 应用问题的配方。
keywords: Agently, playbook, 配方, 编排, triage
---

# Playbooks

> 语言：[English](../../en/playbooks/overview.md) · **中文**

playbook 回答更高层的问题：*我有这类问题 —— 该组合哪些 Agently 能力，怎么组合？* 每个 playbook 引用底层页，但对特定场景有立场。

如果场景不匹配，回到 [能力地图](../reference/capability-map.md) 找对应层。

## 可用 playbook

| Playbook | 何时用 |
|---|---|
| [TriggerFlow 编排](triggerflow-orchestration.md) | 多步过程需要分支、fan-out、pause/resume —— 想要结构模板 |
| [工单分流](ticket-triage.md) | 分类输入、选路由、交接 —— 常见的「结构化输入 → 结构化输出 → action」形态 |

## 为什么有 playbook

文档的其他章节按页讲一种能力：

- [Schema as Prompt](../requests/schema-as-prompt.md) 讲 `output(...)` 怎么用。
- [Lifecycle](../triggerflow/lifecycle.md) 讲 `seal` 与 `close` 区别。

playbook 告诉你这些 —— 跨 request、session、action、TriggerFlow —— 哪种组合适合一个真实问题。比层页高一层。

## 一个好 playbook 长什么样

每页都按相同形态：

1. **问题描述** —— 用大白话讲场景，自然带出痛点。
2. **推荐结构** —— 代码骨架或流程图，把各部分放在合适位置。
3. **变体** —— 常见分叉（小流量 vs 大流量、sync vs async、有 / 无持久化）。
4. **不要做什么** —— 看起来相关但实际不该用的能力。
5. **交叉链接** —— 指回拥有各部分的层页。

## 何时不需要 playbook

如果你的问题是「让一次模型调用返回结构化对象」，不需要 playbook —— 需要 [快速开始](../start/quickstart.md) 与 [Schema as Prompt](../requests/schema-as-prompt.md)。playbook 是给「按这个顺序组合这三件事」类型的答案用的。
