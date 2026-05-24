---
description: 统一 Modelica 模型库中的用户可见中文内容并保留必要兼容性
---

# 中文化修订

## 适用场景

用户希望把模型库中的说明、文档、示例和测试入口统一成中文。

## 步骤

1. 先读 `references/shared-standards.md` 和 `references/ai-execution-spec.md`
2. 读 `references/requirement-mapper.md`
3. 读 `references/executor-base.md`
4. 先区分“用户可见内容”和“技术标识符”
5. 优先修订类说明、参数说明、文档说明
6. 再修订 `UsersGuide`、`ReleaseNotes`、示例和测试说明
7. 用 `references/common-errors.md` 检查是否出现中英混用或误改标识符
8. 用 `references/input-output-contract.md` 说明本次中文化覆盖范围和未覆盖范围

## 模板优先级

优先级从高到低：

1. 现有中文文案规范
2. 已修订过的同类组件说明
3. 通用中文输出模板

## 输出重点

1. 本次中文化覆盖范围
2. 保留英文标识符的原因
3. 是否同步修订了示例、测试和文档入口
4. 剩余未统一项
