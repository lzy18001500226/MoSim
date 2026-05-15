# 库选择指南

本文件用于判断在 MWORKS / Sysplorer 中应优先使用哪个内置库构建系统。

## 目录

- `依赖与版本边界`：确认库之间的依赖关系和版本注意事项。
- `选哪个库`：按主物理域选择优先库。
- `联合使用两个库`：处理空气侧与液体侧耦合或跨域系统。
- `选择判断表`：按任务类型快速落到推荐库。
- `来源`：回溯手册来源。

## 依赖与版本边界

- `TYThermoFluidSys` 手册给出的依赖是 `Modelica 4.0.0.TY.1` 和 `TYMedia V1.4.0`。
- `TYAirTreatmentAndVentilation` 手册给出的依赖是 `Modelica 4.0.0.TY.1` 和 `TYMedia V1.4.0`。
- `TYMedia` 手册给出的依赖是 `Modelica 4.0.0.TY.1`。
- 若当前 Sysplorer 实际可用版本更新，以当前已连接环境中的官方工具返回为准。
- 若生成的是“系统模型库”，而不是单次验证模型，需把这些依赖落实到顶层 `package.mo` 的 `annotation(uses(...))` 中，而不是只依赖当前会话已加载状态。

## 选哪个库

### 优先选 `TYThermoFluidSys`

适合以下任务：

- 水、蒸汽、制冷剂、一般热流体回路建模
- 管网、阀门、容器、三通、弯头、泵、汽轮机、换热器、热组件建模
- 热流体系统的压力、流量、温度、换热、机械能与流体能量耦合分析

该库的主要分类包括：

- `Pipelines`
- `Valves`
- `Volumes`
- `Junctions`
- `Machines`
- `HeatExchangers`
- `Thermals`
- `Blocks`
- `Sources`
- `Sensors`
- `Interfaces`

手册中出现的典型模型包括：

- `TYThermoFluidSys.Machines.SteamTurbine`
- `TYThermoFluidSys.HeatExchangers.SimpleCondenser`
- `TYThermoFluidSys.Machines.SuterPump`
- `TYThermoFluidSys.HeatExchangers.Evaporator`
- `TYThermoFluidSys.Boundaries.BoundaryPressure`
- `TYThermoFluidSys.Boundaries.BoundaryHeatFlow`
- `TYThermoFluidSys.Sensors.SensorT`

### 优先选 `TYAirTreatmentAndVentilation`

适合以下任务：

- 空调、送风、排风、通风、空气品质控制系统
- 风机、压缩机、气体管路、湿度处理、CO2 处理、空气换热建模
- 建筑暖通、舱室环控、氧气供给、空气净化、除湿、增湿任务

该库的主要分类包括：

- `Valves`
- `Pipes`
- `CompressorsAndFans`
- `AirTreatment`
- `HeatExchangers`
- `Controllers`
- `Auxiliaries`
- `Sources`
- `Sensors`
- `Interfaces`
- `Media`

手册中出现的典型模型包括：

- `TYAirTreatmentAndVentilation.CompressorsAndFans.IdealFan`
- `TYAirTreatmentAndVentilation.Auxiliaries.FlowSplit`
- `TYAirTreatmentAndVentilation.Valves.VariableThrottleValve`
- `TYAirTreatmentAndVentilation.Sensors.TemperatureSensor`
- `TYAirTreatmentAndVentilation.Controllers.LimPID`
- `TYAirTreatmentAndVentilation.HeatExchangers.GenericHeatExchanger`
- `TYAirTreatmentAndVentilation.Auxiliaries.Volume_pTX`

### 联合使用两个库

以下场景可以联合使用：

- 空气侧与液体侧通过换热器耦合
- 通风系统中存在制冷剂回路或热流体二次回路
- 暖通主系统属于空气处理，但某些二次侧更适合用热流体库描述

联合建模时注意：

- 优先在各自擅长的物理域内选组件。
- 联合点先确认接口和介质类型是否兼容。
- 不要因为一个系统含空气和液体，就强行全部放进同一个库里。

## 选择判断表

| 任务类型 | 优先库 | 说明 |
| --- | --- | --- |
| 蒸汽动力循环、水箱系统、二回路系统 | `TYThermoFluidSys` | 属于典型热流体系统 |
| 空调系统、通风系统、除湿系统、氧气供给系统 | `TYAirTreatmentAndVentilation` | 属于典型空气处理与通风系统 |
| 泵、汽轮机、流体管道、容积、热组件 | `TYThermoFluidSys` | 设备与接口更贴合热流体回路 |
| 风机、压缩机、增湿器、干燥器、CO2 净化器 | `TYAirTreatmentAndVentilation` | 组件直接面向空气处理任务 |
| 介质物性本身 | `TYMedia` 或 `Modelica.Media` | 不是主系统库，但必须作为介质来源 |

## 来源

- `references/manuals/thermofluid-library-manual.md`
- `references/manuals/air-treatment-library-manual.md`
- `references/manuals/media-library-manual.md`
