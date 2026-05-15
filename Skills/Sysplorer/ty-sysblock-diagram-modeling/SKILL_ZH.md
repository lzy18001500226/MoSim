# Sysblock 框图建模

本文件是 `SKILL.md` 的中文阅读版。只有当 `ty-sysplorer-modeling-rules` 将任务分流到 Sysblock 路径后，才使用本 skill。父级 skill 负责会话健康、分流、七门闸、布局时机、修复闭环和交付证据。

## 范围

- 新建 Sysblock 控制系统框图。
- 修复已有 Sysblock 模型。
- 参数整定和仿真验证。
- 使用 `SysplorerEmbeddedCoder` 的嵌入式控制系统。

不用于 Modelica 物理建模、FMU、HDL/Verilog 生成或纯 API 查询。

## Sysblock 硬规则

- 拓扑构建和编辑只能通过官方 Sysplorer API，经 `call_code(mode="run_script")` 执行。
- 禁止用 `SetModelText`、手写 `.mo` 文本、文本补丁、`connect()` 方程或 `AddConnection` 构建 Sysblock 拓扑。
- 连线使用 `ConnectPort`。
- 使用完整组件路径，例如 `SysplorerEmbeddedCoder.xxx.ComponentName`。
- 使用正确端口后缀：`.y`、`.u`、`.u1`、`.u2` 等。
- 仿真前设置 `StopTime`、`Interval` 等仿真参数。

## 最小读取

| 需求 | 读取 |
|---|---|
| 父级 Sysblock 规则 | `ty-sysplorer-modeling-rules/references/sysblock_style_guide.md` |
| 需求映射 | `references/requirement-mapper.md` |
| 组件/模板映射 | `references/component-mapping.md` |
| 常见错误 | `references/common-errors.md` |
| 验收 | `references/acceptance-checklist.md` |
| 大文档 | 仅在需要具体块文档时读取 `docs/README.md` |

## API 映射

| 需求 | API / 工具 |
|---|---|
| 新建 Sysblock 模型 | `ModelingPy.NewModel(name, "Sysblock")` |
| 打开模型 | `ModelingPy.OpenModel(name)` |
| 添加块 | `ModelingPy.AddComponent(type, model, name, x, y)` |
| 端口连线 | `ModelingPy.ConnectPort(model, src_port, dst_port)` |
| 设置参数 | `ModelingPy.SetModelParamValue(model, block, param, value)` |
| 检查/翻译/仿真 | `check_model`, `translate_model`, `simulate_model` |
| 读取结果 | `result_manager` |

## 领域增量

- 先形成最小可运行控制闭环，再扩展复杂逻辑。
- 修复时定位最短失败链，只做进入下一个父级门闸所需的最小修复。
- 验证稳态值、上升时间、超调、调节时间或用户指定控制指标。
- 若模型能运行但用户目标未满足，回到父级优化循环，不直接声明完成。

## 交付增量

在父级交付证据基础上补充：

- 模型名/路径、任务类型、`SysplorerEmbeddedCoder` 范围、仿真参数、关键变量、验证表和风险。
