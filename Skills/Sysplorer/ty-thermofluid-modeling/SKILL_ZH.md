# TY 热流体建模

本文件是 `SKILL.md` 的中文阅读版。本 skill 只能作为 `ty-sysplorer-modeling-rules` 之后的领域薄补丁使用；父级 skill 负责分流、七门闸、布局时机、修复闭环和交付证据。

## 最小读取

| 需求 | 读取 |
|---|---|
| 需求分类 | `references/requirement-map.md` |
| 库/组件映射 | `references/library-selection.md`, `references/component-map.md` |
| 介质 | `references/media-selection.md` |
| 参数/建模规则 | `references/parameter-rules.md`, `references/modeling-rules.md` |
| 验证 | `references/validation-rules.md` |
| 修复 | `references/common-errors.md` |
| 验收 | `references/acceptance-checklist.md`, `references/output-contract.md` |
| 手册查询 | 仅在精简参考不足时读取 `references/manual-index.md` |

## 专项流程

- 从场景建模：`workflows/build-from-scenario.md`
- 修复现有模型：`workflows/repair-existing-model.md`
- 验证样例或现有模型：`workflows/verify-example.md`

## 领域增量

- 先判断任务类型：新建、修复、样例验证或结果复核。
- 提交拓扑前先确定介质和相态假设。
- 先搭最小能量/流体路径，再添加控制、传感器和次级回路。
- 明确实际使用的库和介质。
- 按任务验证压力、温度、流量、湿度、焓、换热率、压缩机功率、COP 或用户指定指标。
- 介质错误、边界/参考缺失、不可能的压力/温度、发散、关键变量未验证都视为验证失败。
- 图解任务仍由父级 Gate 6 控制布局时机与复检要求。

## 修复优先级

优先沿最短阻塞链排查：

`medium selection -> boundary/reference -> topology -> parameters -> discretization/resistance organization -> initialization -> translation -> simulation -> result interpretation`

保留已有有效结构，修复后回到失败的父级 Step/Gate。

## 交付增量

在父级交付证据基础上补充：

- 临时假设、介质假设、剩余风险、未解决项和下一步建议。
- 若交付库，说明顶层包和绑定依赖。
