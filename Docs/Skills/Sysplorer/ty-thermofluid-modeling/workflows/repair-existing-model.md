# 修复现有模型

## 适用场景

- 用户已有模型在 `check`、`translate`、`simulate` 或结果验证阶段失败。
- 用户要求修复连接、介质、参数、边界、布局或控制逻辑问题。

## 推荐输入

- 模型名称或文件路径。
- 报错信息、异常现象和最近一次修改点。
- 必须保持不变的结构、接口或组件。

## 执行流程

### GATE 1：定位失败阶段

1. 先确认问题卡在 `check`、`translate`、`simulate` 还是结果解释阶段。
2. 用 `references/common-errors.md` 缩小最短排查路径。

### GATE 2：聚焦根因

1. 涉及介质时先查 `references/media-selection.md`。
2. 涉及拓扑、离散、边界或回路组织时查 `references/modeling-rules.md`。
3. 若是开口回路、悬空端口或初始化困难，优先补最小边界让模型先恢复到可执行状态。

### GATE 3：最小修复

1. 每次只改一类问题，不同时混改介质、拓扑和控制逻辑。
2. 修复后立即重跑受影响阶段；必要时退回开环或分段验证。
3. 若布局或连线可读性差，用 `references/diagram-routing-rules.md` 一并整理，但不要借机扩大修改范围。

### GATE 4：结果复核

1. 用 `references/validation-rules.md` 核验异常是否真正消除。
2. 输出前对照 `references/acceptance-checklist.md` 和 `references/output-contract.md`，说明修复范围、残留风险和新增临时边界。

## 输出重点

- 说明失败位置、根因判断和最小修复范围。
- 说明修复是否改变了介质、拓扑、参数或控制策略。
- 说明修复后的真实执行结果与残留风险。
