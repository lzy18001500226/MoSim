# TY 机械建模

本文件是 `SKILL.md` 的中文阅读版。本 skill 只能作为 `ty-sysplorer-modeling-rules` 之后的领域薄补丁使用；父级 skill 负责分流、七门闸、布局时机、修复闭环和交付证据。

## 最小读取

| 需求 | 读取 |
|---|---|
| 需求分类 | `references/requirement-map.md` |
| 组件映射 | `references/component-map.md` |
| 参数 | `references/parameter-rules.md` |
| 验证 | `references/validation-rules.md` |
| 修复 | `references/common-errors.md`，再读 `references/error-repair-playbook.md` |
| 验收 | `references/acceptance-checklist.md` |
| 输入稀疏 | `templates/scenarios/user-input-minimum-form.md` |

## 专项流程

- 新建 TY 机械模型：`workflows/build-from-scenario.md`
- 修复现有模型：`workflows/repair-existing-model.md`
- 验证样例：`workflows/verify-example.md`

## 领域增量

- 先判断任务类型：新建 TY 机械模型、修复、样例验证或结果复核。
- 先判断运动维度：1D、2D 或 3D；这决定库选择。
- 多体模型必须存在 `TYMultibody.World` 或等价世界/参考组件。
- 平面闭环机构必须使用并报告切割铰策略。
- 先搭最小可检查机械闭环，再添加损失、接触、柔性体、监测或扩展工况。
- 赋值前先查询真实组件参数。
- 按任务验证位移、速度、角速度、力、力矩、反力、接触力、穿透、位姿、关节变量、约束反力、变形或模态响应。
- 多体交付物必须打开动画，并判断装配运动、闭环、体姿态、关节运动、干涉和异常跳变。

## 修复优先级

优先沿最短阻塞链排查：

`TY library boundary -> world/reference -> structural connection -> parameters -> initialization/constraints -> solver -> result interpretation`

保留已有有效结构，修复后回到失败的父级 Step/Gate。

## 交付增量

在父级交付证据基础上补充：

- TY 子库边界、选用组件、参数来源、已完成验证动作、已验证变量和已知风险。
- 如替换 TY 组件，说明替代理由和预期影响。
- 平面闭环机构说明切割铰细节。
- 多体模型说明动画状态和基于动画的判断。
