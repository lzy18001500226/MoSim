# 输出约定

本文档用于把用户输入稳定转换为可执行中间结构，并约束最终交付的最小字段。

## 支持输入

### 自然语言

至少提取以下信息：

- 系统类型：液压 / 热液压 / 气动 / 混合
- 组件类型与数量
- 关键参数
- 负载与边界条件
- 控制方式
- 用户意图：仅映射 / 从零建模 / 修复现有模型 / 检查仿真 / 调曲线

### 表格、CSV 或 Markdown 清单

建议归一化列名：

| 规范字段 | 可接受表头 |
|---|---|
| `component_type` | 组件类型, 类型, component, type |
| `quantity` | 数量, qty, quantity, count |
| `parameters` | 参数, params, parameter, parameters |
| `tag` | 位号, tag, id |
| `notes` | 备注, notes, description |

## 中间结构

输出一个等价于如下结构的中间对象：

```yaml
runtime_target: "sysplorer26a"
library_scope: "builtin TY fluid libraries only"
delivery_mode: "from_scratch_builtin_model | example_based | guidance_only"
task_type: "build | repair | verify_example | review_results"
system_type: "hydraulic | thermal_hydraulic | pneumatic | mixed"
components:
  - id: "V1"
    normalized_type: "directional_valve"
    selected_block:
      library_name: "TYHydraulics"
      package_path: "TYHydraulics.Valves.DirectionalValves"
      model_name: "DirectionalValve34_O"
      selection_reason: "user asked for a 4/3 directional valve with open-center behavior"
connections:
  - from: "source.port_B"
    to: "directionalValve.port_P"
    provenance: "derived"
diagram_layout:
  reference_style: "Modelica.Blocks.Examples.PID_Controller"
  major_flow: "left_to_right"
  extent_policy: "uniform_symmetric"
  routing: "orthogonal_first"
line_routes:
  - connection: "source.port_B -> directionalValve.port_P"
    points: "{{-100,40},{-50,40},{-50,20},{-12,20}}"
    annotation_required: true
validation_targets:
  - "all_planned_connections_realized"
  - "no_hidden_or_visually_broken_wires"
  - "no_distorted_hydraulic_symbols"
  - "graphical_layer_displays_normally"
```

## 版本输出规则

- 过程中的迭代版本、草稿版本、分步版本默认不输出。
- 默认只输出最终版本。
- 若流程未完全闭环，也只输出当前可交付的最终版本，并在其中说明阻塞点，不按时间顺序罗列每轮迭代版本。
- 只有用户明确要求查看版本演进、过程草稿或逐轮差异时，才额外提供中间版本信息。

## 最终输出最少字段

1. 系统概述
2. 建模假设与待确认项
3. 实际软件版本与库选择说明
4. 精确块映射表
5. 拓扑连接表
6. 参数表
7. 自建或修复动作清单
8. 图面布局计划
9. 连线与版式校核结果
10. 仿真观测变量与导图项
11. 实际 MWORKS 落地结果
12. 风险项、阻塞点与下一步建议

## 图形实例化规则

- 只要任务包含实际创建模型，就必须把模型实例化到图形图面中。
- 不允许只保留拓扑描述、参数表或隐藏结构而不在图形界面展示实例化模型。
- 图形图面中的实例化结果必须让用户能直观看到主要元件、连线关系和系统结构。
- 创建模型任务中的每条计划可见连接都必须有 `annotation(Line(points=...))`，不能只保留无图面注解的 `connect(...)`。
- 最终输出应说明计划连接数、真实 `connect(...)` 数、带 `Line(points=...)` 的连接数和图中可见关键连线数。
- 只有模型树正确而图形层不可见，不算创建完成。
- 若当前流程未能完成图形实例化或图形层未正常显示，必须在最终版本中明确说明阻塞点。

## 图面布局计划最少字段

| 实例名 | 角色 | 建议区域 | 旋转 | `extent` 规则 | 说明 |
|---|---|---|---|---|---|
| `directionalValve` | 主控阀 | 中央 | `0 / 90 / 180 / 270` | 对称等比例 | 避免竖向拉伸图标 |

## 连线与版式校核结果最少字段

| 校核项 | 结果 | 说明 |
|---|---|---|
| `planned_connection_count_vs_connect_count` | 通过 / 不通过 | 计划连接数与真实 `connect(...)` 数是否一致 |
| `diagram_layout_preflight` | 通过 / 不通过 | 是否运行并通过 `scripts/check_modelica_diagram_layout.ps1 <model.mo> -Json` |
| `connect_count_vs_line_annotation_count` | 通过 / 不通过 | 计划可见连接是否都有 `annotation(Line(points=...))` |
| `line_annotation_preflight` | 通过 / 不通过 | 是否运行并通过 `scripts/check_modelica_line_annotations.ps1 <model.mo> -Json` |
| `visible_instance_count_matches_plan` | 通过 / 不通过 | 图面中可见实例数是否与计划一致 |
| `visible_connection_count_matches_plan` | 通过 / 不通过 | 图面中可见关键连线数是否与计划一致 |
| `critical_wires_visible` | 通过 / 不通过 | 关键连线在图面上是否可见 |
| `hydraulic_symbol_scaling` | 通过 / 不通过 | 液压元件是否保持等比例缩放 |
| `layout_reference_style` | 通过 / 不通过 | 是否遵循 `PID_Controller` 风格的清晰布局 |
| `graphical_layer_displays_normally` | 通过 / 不通过 | 图形层是否对用户正常显示实例化模型 |

## MWORKS 落地项最少字段

| 项目 | 内容 |
|---|---|
| `model_name` | 用户模型名 |
| `implementation_mode` | 默认 `from_scratch_builtin_model` |
| `create_or_repair_actions` | 新建模型、放置元件、修复连线、设置参数等 |
| `graphical_instantiation` | 是否已在图形界面实例化展示模型，用户是否可直观看到 |
| `graphical_layer_status` | 图形层是否正常显示，若异常则说明现象和阻塞点 |
| `check_and_simulate_actions` | 检查模型、按需翻译、仿真、定位结果变量 |
| `plot_targets` | 用户目标曲线对应变量 |

## 报告规则

- 猜测值不能写成确认值。
- 用户要求实际建模时，默认交付必须是从零装配的用户模型，而不是官方示例 wrapper。
- 只有工具成功返回后，才能声称已经创建、检查、翻译、仿真或导图。
- 当任务包含修复断线、修复图面或修复尺寸变形时，必须输出图面布局计划和连线 / 版式校核结果。
- 当任务包含创建模型时，最终版本必须说明模型是否已在图形界面完成实例化展示，以及图形层是否正常显示。
- 如果图形层仍未正常显示，不得把任务写成“已建模完成”，而必须写成“图形层未闭环”并说明阻塞点。
- 除非用户明确要求查看过程版本，否则报告与交付中不得附带中间迭代版本，默认只保留最终版本。
