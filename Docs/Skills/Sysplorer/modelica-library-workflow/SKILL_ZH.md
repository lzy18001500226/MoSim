# Modelica 库工作流

本文件是 `SKILL.md` 的中文阅读版。使用本 skill 前必须先应用 `ty-sysplorer-modeling-rules`；父级 skill 负责分流、七门闸、布局时机、修复闭环和交付证据。本 skill 只补充 Modelica 库/包级工作流规则。

## 使用范围

- 用于 Modelica 库或模型的创建、修复、扩展、结构规范化、评审、本地化和交付准备。
- 适用于 `TYComponentsTemplate`、同类模板、已有骨架、包结构规范化、示例/测试、图解修复和中文本地化。
- 不用于纯理论讨论、纯 API 查询，或没有具体制品目标的宽泛讨论。

## 最小读取

| 需求 | 读取 |
|---|---|
| 任务分类 | `references/requirement-mapper.md` |
| 模板/顶层包设计 | `references/template-package-scheme.md` |
| 跨领域业务包命名 | `references/cross-domain-business-package-strategy.md` |
| 最小可运行验证 | `references/executor-base.md` |
| 静态检查/常见错误 | `references/workflow-checklist.md`, `references/common-errors.md` |
| 验收/交付 | `references/acceptance-checklist.md`, `references/input-output-contract.md` |

## 专项流程

| 流程 | 路径 |
|---|---|
| 基于模板建库 | `workflows/build-from-template.md` |
| 扩展已有库 | `workflows/extend-existing-library.md` |
| 评审已有库 | `workflows/review-existing-library.md` |
| 规范化库结构 | `workflows/normalize-library-structure.md` |
| 中文本地化 | `workflows/chinese-localization.md` |
| 修复图解注解 | `workflows/repair-diagram-annotations.md` |

## 领域增量

- 保持 `package.mo` 与 `package.order` 同步。
- 当模板或项目结构支持时，保留 `Interfaces`、`Utilities`、`Sources`、`Sensors` 作为共享层。
- 区分 `Examples` 和 `Tests`：示例展示用法，测试验证行为。
- 不把官方示例改名后直接作为交付物；只能作为参考或验证基线。
- 图解相关任务仍由父级 Gate 6 决定布局时机与复检要求。

## 交付增量

在父级交付证据基础上补充：

- 完成层级：`plan-complete`、`files-modified`、`structure-level-verified` 或 `run-level-verified`。
- 包结构决策、公共层决策、本地化范围、图面状态、验证深度和剩余风险。
- 只有用户明确要求成套文档时，才使用模板生成包装材料。
