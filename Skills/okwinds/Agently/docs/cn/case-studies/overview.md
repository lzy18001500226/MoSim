---
title: 案例研究
description: 真实场景，展示 Agently 能力如何组合解决具体问题。
keywords: Agently, 案例研究, 例子, KB dialog, daily news, talk to control
---

# 案例研究

> 语言：[English](../../en/case-studies/overview.md) · **中文**

每个案例研究是一次实际场景的简短走读：问题、解决它的结构、用到的 Agently 部件、驱动决策的取舍。

这些是**例子**，不是处方。突出真实应用中常见形态。如果某个案例大体匹配，跟着做；不匹配时 [能力地图](../reference/capability-map.md) 与 [Playbooks](../playbooks/overview.md) 是更好的起点。

## 可用案例

| 案例 | 组合 |
|---|---|
| [日常资讯收集器](daily-news-collector.md) | TriggerFlow + tool + 结构化输出 + 计划任务 |
| [Talk to Control](talk-to-control.md) | 对话 agent + 对域对象的 action + 流式 |
| [知识库对话](kb-dialog.md) | embedding + 检索 + 会话记忆 + 结构化回答 |
| [PRD → 测试用例](prd-testcases.md) | 长输入结构化输出 + ensure 标记必填字段 + 分段流式 |
| [问卷对话](survey-dialog.md) | 多轮 session + 动态 prompt + 分支跟进 |

## 每个案例覆盖什么

每页相同结构：

1. **问题** —— 实际需求是什么。
2. **形态** —— 部件如何拼在一起。
3. **走读** —— 相关代码 + 解释。
4. **为什么这么选** —— 取舍与备选成本。
5. **代码在哪** —— 仓库中可运行示例的指针（如有）。

## 阅读顺序

新手先读 [日常资讯收集器](daily-news-collector.md) —— 用最少篇幅覆盖最多。已经心里有特定形态（RAG、带 action 的对话、长输入解析），直接跳到对应案例。
