---
description: 扩展现有 Modelica 模型库的业务包、组件族、样例或测试入口
---

# 扩展已有模型库

## 适用场景

用户已经有一个模型库，但希望继续补组件族、细分子包、增加 `Examples`、增加 `Tests`，或把临时结构扩成可持续维护的正式结构。

## 步骤

1. 先读 `references/shared-standards.md` 和 `references/ai-execution-spec.md`
2. 读 `references/requirement-mapper.md`
3. 读 `references/template-package-scheme.md`
4. 读 `references/executor-base.md`
5. 先确认现有顶层结构、已落地的公用层和可扩展位置
6. 再确定新增业务包、子包或 `Basics` 的归位
7. 评估是否需要同步补 `Examples`、`Tests`、文档与 `package.order`
8. 用 `references/workflow-checklist.md` 做结构级自检
9. 用 `references/acceptance-checklist.md` 判断是“方案级完成”还是“文件级完成”

## 模板优先级

优先级从高到低：

1. 现有库中已验证的同类业务包结构
2. 模板包结构方案
3. 通用 business package 骨架模板

## 输出重点

1. 新增内容应该放在哪一层
2. 是否需要新增 `Basics`、`Examples`、`Tests`
3. 是否需要同步整理 `Interfaces`、`Utilities` 或 `package.order`
4. 扩展后对现有结构的影响
