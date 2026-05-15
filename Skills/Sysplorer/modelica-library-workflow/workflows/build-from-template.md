---
description: 基于模板或顶层骨架从 0 到 1 搭建 Modelica 模型库
---

# 从模板建库

## 适用场景

用户给了 `TYComponentsTemplate.mo`、同类模板、顶层骨架目录，或者明确要求“按流程建一个模型库”。

## 步骤

1. 先读 `references/shared-standards.md` 和 `references/ai-execution-spec.md`
2. 读 `references/requirement-mapper.md`
3. 读 `references/template-package-scheme.md`
4. 读 `references/executor-base.md`
5. 固定顶层 package、正式包名和首轮交付粒度
6. 收口 `Interfaces`、`Utilities`、`Sources`、`Sensors`
7. 安排第一个业务包及其 `Basics`
8. 补一个 `Examples` 入口和一个 `Tests` 入口
9. 对照 `references/workflow-checklist.md` 做结构级自检
10. 若用户要求首版可用或已验证，再进入 Sysplorer 并按父级闭环验证
11. 按 `references/acceptance-checklist.md` 和 `references/input-output-contract.md` 判断完成层级并组织交付

## 模板优先级

优先级从高到低：

1. 用户提供的模板 `.mo`
2. 已验证的顶层 package 骨架
3. 通用模板结构方案
4. 从零自由设计

## 输出重点

1. 采用了哪种模板结构
2. 正式包名如何替换
3. 公用层如何归位
4. 第一阶段做到什么程度
5. 首个案例和首个测试是否都已通过结构级或运行级验证
