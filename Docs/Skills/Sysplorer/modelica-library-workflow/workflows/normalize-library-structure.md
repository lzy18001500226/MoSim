---
description: 整理 Modelica 模型库的 package 分层、归位规则和业务包命名
---

# 整理模型库结构

## 适用场景

用户希望把已有库从“能用但混乱”整理成“结构清晰、可扩展、可交付”的状态。

## 步骤

1. 先读 `references/shared-standards.md` 和 `references/ai-execution-spec.md`
2. 读 `references/requirement-mapper.md`
3. 读 `references/template-package-scheme.md`
4. 读 `references/executor-base.md`
5. 先整理顶层 package 和正式包名
6. 再收口 `Interfaces` / `Utilities` / `Sources` / `Sensors`
7. 再处理业务包、`Basics` 和 `package.order`
8. 最后补 `Examples`、`Tests` 和文档入口
9. 对照 `references/workflow-checklist.md` 检查是否还有错位项

## 模板优先级

优先级从高到低：

1. 现有顶层结构中可保留的部分
2. 模板包结构方案
3. 通用 package 骨架模板

## 输出重点

1. 哪些内容被迁移或归位
2. 哪些包名被正式化
3. 哪些 `package.order` 被补齐或需要补齐
4. 结构整理后还缺什么
