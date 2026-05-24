---
description: 修复 Modelica 模型库中图形视图、连线注解和布局可见性问题
---

# 修复图面注解

## 适用场景

用户反馈模型“图上没线”“连线不可见”“端口悬空”“布局很乱”，或者需要补齐图形视图注解后再交付。

## 步骤

1. 先读 `references/shared-standards.md` 和 `references/ai-execution-spec.md`
2. 读 `references/requirement-mapper.md`
3. 读 `references/common-errors.md`
4. 读 `references/workflow-checklist.md`
5. 先检查 connector 实例的 `Placement(...)` 和 `iconTransformation(...)`
6. 再检查每条 `connect(...)` 是否带 `annotation(Line(...))`
7. 明确按“`connect(...)` 只建立语义连接，`annotation(Line(...))` 才负责图上可见连线”的规则修补系统模型图面，不把语义连接当作已出图
8. 对照 Modelica 标准库风格检查图标层：接口贴边、主体居中、左右或上下对称、文字不压端口
9. 对照 Modelica 标准库风格检查图形层：主链路清楚、控制链与测量链分层、传感器短支路接入、连线尽量正交
10. 最后检查是否缺 `Diagram(coordinateSystem(...))` 或图面布局说明
11. 按 `references/input-output-contract.md` 说明修复范围、验证状态和剩余风险

## 模板优先级

优先级从高到低：

1. 现有模型里可保留的图面注解
2. 已整理好的同类模型图面风格
3. Modelica 标准库中同语义组件的图标与图面布局
4. 通用图面修复规则

## 输出重点

1. 缺失的是哪类图面注解
2. 本次修补了哪些位置
3. 是否已经消除了“只有 `connect(...)`、没有 `annotation(Line(...))`、图上看不到线”的问题
4. 是否已经达到“接口贴边、主链路清楚、标签不压线”的最低交付标准
5. 还有哪些图面风险未闭环
