# MoSim实验前端与闭环架构

> 状态：架构决策草案，2026-07-15。
>
> 本文冻结 MoSim 的产品化方向：MWORKS 保持图形化建模与实验母体的地位，
> 新建 MoSim Frontend 负责把实验配置、运行、故障注入、结果回流和调参串成
> 一条可操作的闭环。本文不替代 MWORKS 模型规范、ROS1运行规范或具体控制器规范。

## 1. 目标

MoSim 不是若干独立软件的窗口集合，而是一个以 MWORKS 为中心的四旋翼控制实验平台：

```text
实验配置
  -> MWORKS图形化建模/快速仿真
  -> 参数筛选与控制器评价
  -> Gazebo/PX4工程验证
  -> RViz/UE运行展示
  -> 日志回流MWORKS/指标模块
  -> 失败诊断与参数优化
  -> 下一轮实验
```

前端的价值是减少多终端、多窗口和手工改配置的操作成本；前端不替代 MWORKS
图形化模型，也不把 GUI 变成高频控制环的一部分。

## 2. 角色边界

| 组件 | 负责 | 不负责 |
| --- | --- | --- |
| MWORKS/Sysblock/Syslab | 四旋翼模型、控制器、MIL/SIL、扰动/故障模型、参数优化、指标和结果查看 | 直接管理所有操作系统进程；不依赖 GUI 逐周期控制 Gazebo |
| MoSim Frontend | 算法/任务/profile选择、启动实验、运行控制、故障操作、状态和结果总览、窗口编排 | 不直接拼裸命令；不绕过 Profile Validator；不替代控制器 |
| MoSim Orchestrator | 校验 Profile、生成 Launch Plan、启动/停止运行组件、记录 Run Manifest、回收日志 | 不决定控制算法数学逻辑；不把显示画面当作指标 |
| Gazebo/Sunray | plant、执行器、传感器、truth、风扰和物理故障 | 不拥有 MWORKS 控制器设计权威 |
| PX4/MAVROS | 飞控模式、状态估计接口、failsafe、指令执行和人工接管通道 | 不拥有实验结果和控制器优化权威 |
| RViz | ROS1点云、轨迹、地图、坐标系和运行审核 | 不作为指标来源 |
| UE | 场景、渲染、视频和展示 | 不替代 Gazebo/PX4/RViz 运行证据 |

## 3. 一次实验的完整闭环

一次实验不是一次孤立启动，而是一个有 lineage 的 `ExperimentSession`：

```text
1. 前端选择 controller、trajectory、plant、disturbance、fault 和 metrics。
2. MWORKS/Registry 解析控制器与参数版本，生成 ExperimentProfile。
3. Validator 检查模型、控制器、场景、故障和输出目录的兼容性。
4. Orchestrator 生成 Launch Plan 和 Run Manifest。
5. MWORKS 先执行快速模型仿真或参数候选筛选。
6. 通过筛选的候选进入 Gazebo/PX4/MAVROS 工程验证。
7. RViz、UE 和前端只读订阅 DisplayFrame/StatusFrame；不阻塞控制器。
8. Logger 保存原始状态、参考、控制量、事件和故障时间戳。
9. MWORKS/指标模块计算 RMSE、最大误差、超调、调节时间、恢复时间、约束违规。
10. 诊断模块给出失败类别和参数候选；用户选择手动、批量或自动优化。
11. 新候选继承父 Run Manifest，生成下一轮实验并保留可追溯关系。
12. 最优候选再次经过 Gazebo 回归，随后固化为报告和演示证据。
```

第一阶段的调参默认采用“完成/停止本次运行后再调参再重跑”，不支持飞行中任意
改控制器参数。这样结果可复现，也避免把临时在线操作误当作正式实验。

## 4. 快速调参设计

前端提供三种模式：

### 4.1 手动快速调参

只暴露注册过的参数组，例如姿态增益、位置增益、阻尼、积分限幅、扰动补偿和
安全限幅。参数修改必须产生新版本，不覆盖历史结果。

### 4.2 MWORKS批量筛选

在完整 Gazebo 启动前，用 MWORKS 对候选参数进行快速仿真，按目标函数和安全约束
淘汰候选。目标函数至少应包含跟踪误差、超调、恢复时间、控制输入和约束违规。

### 4.3 Gazebo确认

将 MWORKS 筛选出的少量候选放入 Gazebo/PX4，确认模型优势是否在工程运行环境中
成立。没有 Gazebo 回归证据时，只能声明模型级候选，不能声明最终部署参数。

失败诊断可以给出“超调、振荡、响应迟缓、输出饱和、漂移、故障恢复慢”等类别，
但诊断建议必须带证据和参数范围，不能把启发式建议直接当作自动修复结果。

## 5. 故障和扰动闭环

前端负责选择故障，后端按故障对象注入：

| 故障/扰动 | 首选注入位置 |
| --- | --- |
| 电机推力下降、卡死、响应变慢 | Gazebo 执行器/电机插件 |
| IMU偏置、噪声、丢帧 | Gazebo 传感器插件或 SensorAdapter |
| GPS漂移/丢失 | GPS插件或状态适配层 |
| 通信延迟/丢包 | ROS/MAVROS bridge |
| 风场、质量和惯量变化 | Gazebo环境/动力学插件 |
| 控制器参数或控制律异常 | MWORKS模型或 ControllerHost |
| 故障检测、控制分配重构和安全限制 | Controller/SafetySupervisor |

MWORKS 先定义和验证故障 Profile，Gazebo 再执行相同 Profile 的物理验证。每次
故障必须记录 `fault_event`，并在结果中显示注入时间、检测时间、恢复时间和是否
违反安全约束。

## 6. 前端工作区

建议主窗口采用“实验工作台”而不是普通地面站菜单：

```text
左侧：实验Profile、算法、轨迹、扰动和故障配置
中央：MWORKS图形化仿真/结果视图或运行总览
右侧：状态、告警、控制器状态、故障事件和指标
底部：实验日志、Run lineage、候选参数和重跑按钮
嵌入/编排视图：RViz轨迹点云、UE场景、QGC飞控状态
```

前端最小命令集：`validate`、`start`、`pause`、`stop`、`land`、`inject_fault`、
`rerun`、`compare`、`promote`、`export_evidence`。所有命令都引用 Profile 和
Run ID，不接受任意裸 shell 字符串。

## 7. 现成前端调研结论

### QGroundControl

- 项目：[mavlink/qgroundcontrol](https://github.com/mavlink/qgroundcontrol)
- 定位：跨平台无人机地面站，适合 MAVLink 连接、飞行状态、模式、任务、参数和
  人工接管。
- 适合 MoSim：作为 QGC 状态/飞控操作参考，或后期作为外部飞控面板。
- 不适合直接承担：MWORKS 实验配置、故障 Profile、批量调参、Run lineage 和
  报告证据管理。
- 决策：第一阶段不 fork QGC 作为 MoSim 主界面；先通过 MAVLink/QGC 保留飞控
  操作能力，避免把实验平台绑定到大型地面站代码库。

### Foxglove

- 项目：[Foxglove](https://foxglove.dev/)，文档：[Foxglove Docs](https://docs.foxglove.dev/)
- 定位：机器人多模态日志、3D、时间序列、回放和可编排面板；文档提供 ROS1、
  自定义数据、布局、扩展和嵌入能力。
- 适合 MoSim：借鉴面板布局、时间轴、3D/曲线联动、日志回放和数据协议；可评估
  作为结果查看器或嵌入式可视化部件。
- 不适合直接承担：实验启动权限、Gazebo故障注入、控制器参数晋级和 MWORKS
  图形化模型。
- 决策：优先研究其数据协议和面板组织，暂不把完整 Foxglove 应用当作 MoSim
  主前端基座。

### PlotJuggler

- 项目：[PlotJuggler](https://github.com/PlotJuggler/PlotJuggler)
- 定位：时间序列分析和 ROS 数据曲线工具。
- 适合 MoSim：快速复用曲线拖拽、信号对比和回放分析思路。
- 不适合直接承担：3D场景、实验编排、故障操作和完整产品前端。
- 决策：可作为离线诊断工具或曲线模块参考，不作为主工作台。

### 机器狗 ROS/Gazebo 地面站

- 参考：[unitreerobotics/unitree_ros](https://github.com/unitreerobotics/unitree_ros)
- 可借鉴：机器人描述、Gazebo运行、ROS控制节点、外部扰动命令和 RViz 启动组织。
- 不应直接套用：它解决的是机器狗关节/机器人 ROS 仿真，不包含 MoSim 的 MWORKS
  控制器实验、四旋翼飞行任务和竞赛证据链。

## 8. 当前推荐技术路线

```text
MoSim Frontend：Qt/QML桌面工作台
Orchestrator：本地服务/API，统一管理Profile、Launch Plan和Run Manifest
MWORKS：图形化模型、快速仿真、调参和结果分析
ROS1/Gazebo/PX4：当前工程运行后端
RViz/UE/QGC：通过标准接口或受控子窗口接入
```

先做统一工作台和窗口编排，再做真正的进程内嵌入。Windows 前端直接嵌入 WSL
原生 RViz 具有跨桌面环境风险，第一版可采用“前端统一启动、定位、调整大小和
关闭”的受控子窗口；稳定后再评估 Qt 原生 RViz 集成、远程渲染或数据重绘方案。

## 9. 暂不承诺的能力

- 没有统一 MWORKS/Gazebo Profile 的，不能声称端到端实验闭环。
- 没有 Gazebo/PX4 回归的，只能声称 MWORKS 模型级结果。
- YOPO、强化学习和神经网络控制器属于后续扩展，必须先定义输入、输出、训练/推理
  运行时、固定尺寸、fallback 和安全边界。
- YOPO 应先按学习型规划器评估，不直接等同于强化学习控制器。
- 神经网络第一阶段只能作为受约束残差补偿或参数优化模块，不能替换官方控制基线。

## 10. 验收顺序

```text
F0 统一 ExperimentProfile、Run Manifest 和结果目录
F1 MWORKS 图形化最小四旋翼模型与 PID 基线
F2 前端选择 Profile 并启动一次 MWORKS 仿真
F3 MWORKS 指标、曲线和参数版本对比
F4 Gazebo/PX4 回灌同一 Profile
F5 RViz/UE/QGC 统一窗口和状态展示
F6 风扰与单一电机故障注入
F7 MWORKS 批量调参和 Gazebo 候选确认
F8 神经残差/学习型规划器等扩展
```

F0-F4 是“闭环成立”的最小条件；F5-F7 是完整演示和工程化增强；F8 不得提前
替代基础控制器验收。
