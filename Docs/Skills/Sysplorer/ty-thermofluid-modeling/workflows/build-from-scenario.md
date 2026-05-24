# 从场景新建模型

## 适用场景

- 用户要求从零搭建热流体、换热、空气处理或通风系统。
- 用户需要最小可运行骨架，并继续扩展到可检查、可翻译、可仿真和可验证的模型。

## 推荐输入

- 系统目标、主要设备和介质类型。
- 边界工况、控制目标和关键结果变量。
- 必须保留的结构、组件或接口约束。

## 执行流程

### GATE 1：需求收口

1. 先用 `references/requirement-map.md` 判断任务类型与默认路径。
2. 若介质、相态、关键边界或控制目标缺失，先补问；若不能补问，明确写出临时假设。

### GATE 2：库与组件映射

1. 用 `references/library-selection.md` 选择优先库。
2. 用 `references/component-map.md` 确定核心设备、边界、传感器和控制器映射。
3. 用 `references/media-selection.md` 确认介质和介质约束。

### GATE 3：最小骨架

1. 先搭主能量链路和主回路，再补边界、测点和必要控制。
2. 若系统暂时无法闭环，优先补最小等效边界，使模型先可 `check` / `translate`。
3. 需要骨架模板时，优先参考 `templates/model-skeletons/` 和 `templates/scenarios/`。

### GATE 4：参数化与布局

1. 按 `references/parameter-rules.md` 设定参数，确保关键设备和控制阈值可配置。
2. 按 `references/modeling-rules.md` 复核拓扑、边界和求解可行性。
3. 按 `references/diagram-routing-rules.md` 整理布局、对齐接口并清理低质量连线。

### GATE 5：验证闭环

1. 按父级闭环执行完整验证。
2. 用 `references/validation-rules.md` 核验关键变量、方向性和量纲是否合理。
3. 若最小闭环可运行但 KPI、图面可审查性或用户目标未达成，回到父级优化循环，不直接交付。
4. 输出前对照 `references/acceptance-checklist.md` 和 `references/output-contract.md`，说明哪些边界是临时等效、哪些结构已达到交付状态。

## 输出重点

- 说明采用的库、介质、组件映射和模板来源。
- 说明已完成的真实执行阶段，以及仍依赖的临时假设或等效边界。
- 说明关键结果变量和验证结论。
