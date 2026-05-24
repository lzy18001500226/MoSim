---
name: ty-sysblock-diagram-modeling
description: 使用 SysplorerEmbeddedCoder 库在 Sysplorer 中执行嵌入式控制系统 Sysblock 框图建模。当用户提出新建 Sysblock 框图模型、修复现有模型、参数整定或仿真验证等任务时触发。覆盖信号源、数学运算、连续/离散系统、逻辑运算和观测器组件。不适用于 Modelica 物理建模。先决：必须先应用 `ty-sysplorer-modeling-rules`，本技能只作为 Sysblock 控制框图领域补充。
---

# Sysblock Block Diagram Modeling

Use this only after `ty-sysplorer-modeling-rules` routes the task to the Sysblock path. The parent skill owns session health, routing, seven gates, layout timing, repair loop, and delivery evidence.

## Scope

- New Sysblock control-system block diagrams.
- Existing Sysblock model repair.
- Parameter tuning and simulation verification.
- Embedded control systems using `SysplorerEmbeddedCoder`.

Do not use for Modelica physical modeling, FMU work, HDL/Verilog generation, or pure API lookup.

## Non-Negotiable Sysblock Rules

- Build and edit topology only through official Sysplorer APIs via `call_code(mode="run_script")`.
- Never use `SetModelText`, hand-written `.mo` text, text patches, `connect()` equations, or `AddConnection` for Sysblock topology.
- Use `ConnectPort` for wiring.
- Use full component paths such as `SysplorerEmbeddedCoder.xxx.ComponentName`.
- Use correct port suffixes: `.y`, `.u`, `.u1`, `.u2`, etc.
- Set simulation parameters such as `StopTime` and `Interval` before simulation.

## Minimal Reading

| Need | Read |
|---|---|
| Parent Sysblock rules | `ty-sysplorer-modeling-rules/references/sysblock_style_guide.md` |
| Requirement mapping | `references/requirement-mapper.md` |
| Component/template mapping | `references/component-mapping.md` |
| Common errors | `references/common-errors.md` |
| Acceptance | `references/acceptance-checklist.md` |
| Large docs | `docs/README.md` only when concrete block docs are needed |

## API Map

| Need | API / Tool |
|---|---|
| Create Sysblock model | `ModelingPy.NewModel(name, "Sysblock")` |
| Open model | `ModelingPy.OpenModel(name)` |
| Add block | `ModelingPy.AddComponent(type, model, name, x, y)` |
| Wire ports | `ModelingPy.ConnectPort(model, src_port, dst_port)` |
| Set parameters | `ModelingPy.SetModelParamValue(model, block, param, value)` |
| Check / translate / simulate | `check_model`, `translate_model`, `simulate_model` |
| Read results | `result_manager` |

## Domain Additions

- Form a minimum runnable control loop before expanding complex logic.
- For repairs, locate the shortest failure chain and make only the minimum repair needed for the next parent gate.
- Verify steady-state value, rise time, overshoot, settling time, or user-specified control metrics.
- If the model runs but user objectives are not met, return to the parent optimization loop rather than declaring completion.

## Delivery Additions

In addition to parent delivery evidence, state:

- Model name/path, task type, `SysplorerEmbeddedCoder` scope, simulation parameters, key variables, verification table, and risks.
