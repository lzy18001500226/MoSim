---
description: 评审现有 Modelica 模型库的结构、归位、文案和交付完整性
---

# 评审现有模型库

## 适用场景

用户给了已有模型库，希望找出结构问题、缺口、错位项和整改顺序。

## 步骤

1. 先读 `references/shared-standards.md` 和 `references/ai-execution-spec.md`
2. 读 `references/requirement-mapper.md`
3. 读 `references/workflow-checklist.md`
4. 读 `references/common-errors.md`
5. 逐项检查顶层包、归位、公用层、业务包、样例、测试、中文化和图面
6. 按严重度整理为“保留项 / 缺口 / 错位项 / 修补顺序”
7. 交付前对照 `references/acceptance-checklist.md` 和 `references/input-output-contract.md`

## 模板优先级

优先级从高到低：

1. 现有真实库结构
2. 模板包结构方案
3. 通用检查清单

## 输出重点

1. 哪些结构值得保留
2. 哪些问题会阻塞后续扩展
3. 哪些问题只是文案层，哪些已经影响验证与交付
4. 首批整改顺序
