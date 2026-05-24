# 验证规则

本文件用于约束液压、热液压、气动任务中的结果验证、连线验证和图面验证。

## 结果验证规则

| 场景 | 关键变量 | 判断标准 | 风险提示 |
|---|---|---|---|
| 阀控缸基础回路 | `cylinder displacement` | 位移方向与命令和负载设定一致 | 反向时优先检查负载方向、A/B 腔连接、阀口语义 |
| 阀控缸基础回路 | `pressure at supply / A / B / return` | 压力水平与回路拓扑一致，无明显物理矛盾 | 压力异常时优先查边界、溢流支路、回油闭合性 |
| 阀控缸基础回路 | `flow rate` | 有动作时主工作线不应长期为零 | 零流量时优先查介质、边界、阀芯状态、断线 |
| 泵阀系统 | `pump outlet pressure` | 与负载和阀状态变化一致 | 不合理高压常见于回路堵塞或回油缺失 |
| 热液压系统 | `temperature` | 温度变化与热边界和工况一致 | 温度无变化时优先查是否误用普通液压库 |
| 热液压系统 | `enthalpy / heat-transfer related variables` | 与热交换对象和边界一致 | 结果缺失时优先查热端口和热边界 |
| 气动回路 | `cylinder position` | 动作方向与阀状态和负载设定一致 | 不动作时优先查气源、排气、阀位 |
| 气动回路 | `gas pressure` | 压力变化符合充气、放气与节流逻辑 | 压力不变时优先查边界和排气路径 |

## 图面与连线验证规则

| 校核项 | 必须通过的标准 | 失败时优先排查 |
|---|---|---|
| `planned_connection_count_vs_connect_count` | 拓扑连接表与真实 `connect(...)` 数量一致 | 漏连、误连、连接表未更新 |
| `placement_annotations_present` | 每个关键实例都有 `annotation(Placement(...))` | 图面缺失、悬空端点、红色虚线 |
| `diagram_layout_preflight_passed` | `scripts/check_modelica_diagram_layout.ps1 <model.mo> -Json` 已通过 | 组件重叠、拥挤、超出图面坐标系 |
| `line_annotations_present` | 创建模型任务中每条计划可见的 `connect(...)` 都带 `annotation(Line(points=...))` | 导图无连线、折线异常 |
| `line_annotation_preflight_passed` | `scripts/check_modelica_line_annotations.ps1 <model.mo> -Json` 已通过 | 大模型漏写 Line 注解、零长度连线 |
| `diagram_annotation_present` | 模型中存在 `Diagram(coordinateSystem(...))` | 导图布局失控 |
| `graphical_instances_present` | 创建任务中的关键元件已经实例化并在图形图面中可见 | 只写了文本结构、未完成图形实例化、图面中看不到模型主体 |
| `visible_instance_count_matches_plan` | 图面中可见的关键实例数与计划实例数一致或差异已解释 | 模型树里有元件，但图面里缺实例 |
| `visible_connection_count_matches_plan` | 图面中可见的关键连线与计划连线一致或差异已解释 | 文本里有连接，图面中看不到关键连线 |
| `critical_wires_visible` | 关键压力线、工作线、回油 / 回气线、控制线在图中可见 | 连线被图标或文字完全遮挡 |
| `layer_separation` | 主流体回路和控制线分层清晰 | 就近最短线导致交叉混乱 |
| `symbol_scaling` | 阀、缸、主要流体元件保持等比例缩放 | `extent` 非等比拉伸 |
| `connector_anchor_quality` | 对外暴露的 connector 实例带 `Placement` 和 `iconTransformation` | 红色虚线、悬空端点、端口锚点异常 |
| `capacitor_resistive_topology_checked` | `TYHydraulics` / `TYHydraulicComponents` 模型已按 `references/capacitor-resistive-check.md` 运行自动或人工容阻检查 | 阻性件直连、容性件直连、接口容腔开关不当、自建端口缺容阻标识 |

## 图形层正常显示最低要求

1. 关键元件实例在图形图面中可见，而不只是在模型树中存在。
2. 关键连线在图形图面中可见，而不只是在文本 `connect(...)` 中存在。
3. 图面布局在导图或图形复核时可正常阅读，没有主体缺失。
4. 若任一项不满足，则该创建任务仍视为图形层未闭环。

## 图面复核最低要求

1. 只要任务涉及实际建模或图面修复，就必须至少导出并复核一次图面。
2. 对创建模型任务，必须确认关键元件实例已经在图形图面中可见，用户可直观看到模型结构。
3. 对创建模型任务，必须确认关键连线在图形图面中可见，而不是只有模型树或文本结构正确。
4. 图面复核要明确写出是否检查了 `Placement`、`Line`、`Diagram` 三类注解。
5. 必须确认长标签没有遮挡阀、缸或关键端口。
6. 必须确认没有关键断线、明显乱线或明显拉伸变形图元。
7. 必须确认 `Line(points=...)` 至少有两个不同坐标点，且坐标落在 `Diagram(coordinateSystem(...))` 范围内。
8. 必须确认 `.mo` 源码级布局预检查和连线预检查均已通过；未通过时不得进入 `check_model` 或声明图形层完成。

## 结果通过阈值

1. 关键变量已经命名并可读取。
2. 关键变量与用户目标存在直接映射关系。
3. 变量变化趋势与拓扑和参数设定一致。
4. 图形层对用户可见且可读。
5. 若结果不满足预期，或图形层未正常显示，必须明确说明阻塞点，不得只写“已完成仿真”或“已创建模型”。
