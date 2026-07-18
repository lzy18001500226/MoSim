# MWORKS实时联合仿真与双GUI接口设计

> 状态：设计冻结、能力待验证，2026-07-18。
>
> 本文定义MWORKS实时控制器实验路径、Model Studio配置归属、Flight Console操作语义、
> Orchestrator状态机和安全回退。本文不证明MWORKS已达到实时频率，也不证明任何实时
> 联合仿真飞行已经通过。

## 1. 目标与非目标

目标是在不改变Gazebo/PX4/MAVROS运行权威的前提下，增加一条可选的`MWORKS Live`
控制器执行路径，使同一控制器可以按统一Profile完成：

```text
MWORKS MIL/SIL
  -> generated-C部署验证
  -> MWORKS Live实时联合仿真
  -> 同场景、同参考、同指标A/B比较
```

第一版只支持单机，固定控制输出边界为“期望姿态 + 总推力”。它不负责：

- 用MWORKS替代Gazebo plant、PX4、MAVROS或传感器链；
- 让UE、QGC或Model Studio承载高频控制数据；
- 飞行中热切换控制器模型、Solver或通信参数；
- 在未通过实时门禁前把`MWORKS Live`显示为可用能力；
- 以界面出现、端口连通或模型开始计算代替闭环飞行证据。

第一版 `ATTITUDE_THRUST` 的名义控制器固定为位置/平动外环
`official_pid`，UI 显示名为“PX4CTRL 官方位置外环 PID”。PX4 内置姿态/角速度环拥有
姿态内环，`attitude_inner_owner = px4_builtin_attitude_rate_v1`。`AWFF` 只能作为
`augmentation_ids = [awff]` 的增强层；自研 INDI、SMC、Backstepping 等姿态内环在该
输出边界下可见禁用，不能宣称已经在线执行。

## 2. 与generated-C主线的关系

`generated-C`仍是正式部署和比赛演示的默认主线。`MWORKS Live`是显式选择的实验后端，
用于缩短控制器调试与Gazebo闭环验证之间的迭代时间，不取代生成代码门禁。

| 执行方式 | 控制器运行位置 | 用途 | 默认状态 |
| --- | --- | --- | --- |
| `deployed_controller` | px4ctrl/生成代码runtime | 正式部署、长测、比赛演示 | 主线 |
| `mworks_live` | MWORKS实时模型，经Adapter接入MAVROS | 快速联合调试、A/B验证 | 实验、门禁通过后开放 |

两条路径必须使用同一控制器语义、参数版本、状态/参考定义和评价指标。若两者命令边界不同，
必须由各自`CommandAdapter`显式转换，不能在报告中直接比较未对齐结果。

## 3. 三个独立选择维度

界面和Profile必须分开表达以下三个维度，禁止把它们合并成一个“模式”下拉框：

| 维度 | 第一版选项 | 含义 |
| --- | --- | --- |
| `control_mode` | `position_manual`、`programmed` | 参考指令由人工定点输入还是任务程序产生 |
| `mission_mode` | `hover`、`figure8`、`waypoint`、已验收规划任务 | 程控模式下具体运行什么任务；定点模式固定为悬停/平移 |
| `controller_backend` | `deployed_controller`、`mworks_live` | 控制律实际在哪个后端执行 |

控制器/Profile必须在起飞前选好并冻结。起飞后：

- 定点模式先悬停，再允许`W/A/S/D`产生受限水平参考；
- 程控模式也先悬停，只有用户显式点击任务按钮后才开始8字、航点或探索；
- `W/A/S/D`和程控任务不能同时拥有参考指令权威；
- 飞行中不得通过GUI切换控制器后端。

## 4. 用户操作流程

### 4.1 通用流程

```text
选择控制器/Profile
  -> 选择定点模式或程控模式
  -> 程控模式选择任务
  -> 选择deployed controller或MWORKS Live
  -> 环境预检
  -> 准备Gazebo/PX4/MAVROS/控制器/UE
  -> 一键解锁并起飞
  -> 到达固定悬停高度
  -> 定点W/A/S/D或显式开始程控任务
  -> 悬停/降落/安全停止
  -> 结果与证据回传
```

`一键解锁并起飞`只执行解锁、起飞和到达Profile声明的悬停高度，不自动开始任何任务。
按钮在一次请求未终止前保持禁用并显示阶段、进度、已等待时间和当前组件，避免重复点击。

### 4.2 定点模式

`W/A/S/D`只产生受限的水平位置/速度参考，控制器仍由起飞前选定的后端执行。松键、输入
过期或Flight Console失焦时，参考速度归零并保持当前位置。键盘输入不是模拟PX4摇杆，
也不绕过Orchestrator直接发布MAVROS setpoint。

### 4.3 程控模式

到达悬停后，Flight Console显示当前Profile允许的任务按钮。点击任务按钮产生幂等Action，
经Orchestrator确认唯一参考权威后才启动。任务停止或失败后先进入受控悬停，不自动重启。

## 5. 端到端数据链

```text
Gazebo/PX4/MAVROS
        |
        | 带时间戳的ROS状态
        v
MWORKS Realtime Adapter
        |
        | 标准StateFrame + ReferenceFrame
        v
MWORKS实时控制器模型
        |
        | AttitudeThrustCommand
        v
MWORKS Realtime Adapter
        |
        | 坐标/单位/限幅/新鲜度校验
        v
MAVROS -> PX4 -> Gazebo

UE <---- DisplayFrame ---- Orchestrator/ROS
QGC <--- 状态、动作、日志 --- Orchestrator
```

Gazebo/PX4/MAVROS拥有plant、传感器、执行器和飞行状态权威。MWORKS只计算控制输出；UE只
消费显示帧；QGC只选择、启动、监控和发送受控动作。关闭QGC或UE不得中断高频控制链。

## 6. 标准输入输出合同

第一版使用结构化Schema，不使用无版本裸`float[]`。字段至少包括：

### 6.1 `StateFrame`

| 字段 | 单位/语义 |
| --- | --- |
| `schema_version`, `run_id`, `sequence` | 版本、运行隔离和单调序号 |
| `source_stamp`, `receive_stamp` | 仿真时间和Adapter接收时间 |
| `frame_id`, `child_frame_id` | 坐标系显式声明 |
| `position[3]` | m |
| `velocity[3]` | m/s |
| `attitude_quaternion[4]` | 顺序和旋转方向由Schema固定 |
| `body_rate[3]` | rad/s |
| `acceleration[3]` | m/s^2，可用性由Profile声明 |
| `armed`, `flight_mode`, `validity` | 飞行状态与逐字段有效性 |

### 6.2 `ReferenceFrame`

至少包含参考位置、速度、加速度、航向、航向角速度、参考来源、任务revision和有效期。
`position_manual`与`programmed`使用同一Schema，但`reference_authority`不同。

### 6.3 `AttitudeThrustCommand`

第一版固定包含期望姿态、可选期望角速度、总推力、命令时间戳、有效期、限幅状态和控制器
诊断。推力归一化、N或加速度语义必须由Profile和Command Adapter共同声明，禁止隐式换算。

坐标系、四元数顺序、推力方向和ENU/NED转换必须复用项目统一控制接口，并由往返测试证明；
本文不另建第二套坐标合同。

## 7. Model Studio与Profile持久化

Model Studio原生APP是实时控制配置的编辑和校验入口，但不是配置唯一存储位置。流程固定为：

```text
Model Studio APP编辑
  -> Schema校验
  -> 保存项目内版本化JSON
  -> 发布Profile/hash
  -> QGC和Orchestrator只读消费
```

建议权威目录：

```text
Config/control_platform/  控制模块、I/O Schema、Adapter和能力注册
Config/profiles/          已发布实验与实时联合仿真Profile
```

Model Studio配置项包括：控制器模型和参数、固定步长、目标频率、输入输出端口、状态/参考
映射、Solver和初始化、接口类型、输出边界、延迟/超时阈值、fallback控制器，以及MIL、
实时联合仿真或代码生成执行方式。

QGC不编辑ROS topic、UDP端口、Solver和模型内部参数。它只选择已经发布且与当前场景兼容的
Profile，并显示版本、hash、证据状态和禁用原因。

Model Studio 可直接执行离线模型检查、MIL、代码生成、打开模型和结果；在线飞行只允许
`validate/publish/prepare` 并引导进入 QGC。QGC 执行连接、解锁、起飞、任务、悬停、
降落和安全停止。两个 GUI 都可以显示只读运行状态并请求同一个幂等 `safe_stop`，但
Orchestrator 是唯一命令裁决者，任何 GUI 都不得直接发布高频控制命令。

ExperimentProfile 由 Model Studio 发布，MissionArtifact 由 QGC 任务侧维护，Orchestrator
校验二者与运行环境后生成不可变 RunManifest。RunManifest 在 `ready_on_ground` 后冻结；
运行状态、ACK、事件和遥测写入独立 RunStatus/Event，不持续改写 Manifest。

## 8. Flight Console界面

运行前配置区至少显示：

- 控制器/Profile；
- 参考模式：定点或程控；
- 程控任务；
- 执行方式：部署控制器或MWORKS Live；
- 悬停高度和只读安全限制摘要。

运行状态区至少显示：

```text
Gazebo | PX4 | MAVROS | 状态源 | 控制器后端 | MWORKS Adapter | UE
```

当选择`mworks_live`时，额外显示模型名、计算频率、输入/输出新鲜度、往返延迟、丢帧、
超时次数和fallback状态。未通过门禁时选项保持可见禁用，并给出下一步验证动作。

QGC保留原生MAVLink Console用于PX4 shell；另增加精简的`MoSim Runtime Console`：

- 默认只显示运行阶段、控制器、模式、任务、连接和首要错误；
- 展开后显示Orchestrator、px4ctrl、MAVROS、Gazebo和MWORKS Adapter日志；
- 支持按组件过滤和导出当前`run_id`日志；
- 不在普通模式暴露端口、topic和任意终端命令执行。

## 9. Orchestrator状态机

```text
draft
  -> validated
  -> preparing
  -> ready_on_ground
  -> arming
  -> taking_off
  -> hovering
  -> manual_active | mission_active
  -> hovering
  -> landing
  -> completed

任意安全故障 -> fallback_hover -> landing或safe_stop
```

关键约束：

- `ready_on_ground`前冻结Profile、控制器后端和参考权威；
- `taking_off`完成只进入`hovering`，不隐式进入任务；
- 同一飞机任一时刻只有一个参考来源和一个控制命令发布者；
- 起飞后基础设施不得自动重启任务或控制器；
- 所有按钮请求携带`request_id`并幂等，重复点击返回同一动作状态。

## 10. 实时性、时钟与数据新鲜度

第一版目标控制频率为50至100 Hz，但该数字是验证目标，不是当前能力声明。RT0必须测出
MWORKS在当前比赛电脑上的稳定单步执行频率、抖动和最坏延迟，再决定是否开放实时路径。

每一帧必须携带仿真时间、接收时间和序号。Adapter至少统计：

- 输入频率、控制器计算频率和输出发布频率；
- 平均、P95、P99和最大端到端延迟；
- 乱序、重复、丢帧、输入过期和输出超时；
- Gazebo仿真时间相对墙钟速度；
- 连续超时次数和最近一次有效命令年龄。

不得只用QGC刷新率或UE帧率推断控制回路频率。运行前由Profile冻结超时阈值；阈值修改必须
产生新Profile/hash。

## 11. 安全与fallback

`MWORKS Live`失联、输出过期、数值无效、频率持续低于门限或命令越界时：

1. Adapter立即停止接受MWORKS新命令并记录结构化故障；
2. Controller Manager按已验收切换合同转入本地`px4ctrl`悬停；
3. Flight Console显示红色故障状态、触发时间、原因和当前fallback；
4. 空中不自动重启MWORKS、不恢复原任务；
5. 用户只能继续悬停、降落或安全停止。

fallback不是简单启动第二个发布者。切换前后必须证明命令权威唯一、参考连续性和无旧命令
重放。若本地悬停fallback尚未通过同run故障注入门禁，`MWORKS Live`不得开放飞行控制。

## 12. 技术验证阶梯

| 门禁 | 验证内容 | 通过条件摘要 |
| --- | --- | --- |
| RT0 能力探针 | 外部输入、单步执行、输出和可达频率 | 当前电脑稳定达到目标频率，延迟/抖动有证据 |
| RT1 离线循环 | 固定输入经MWORKS得到输出 | 与MIL基准数值一致，Schema/单位/坐标往返通过 |
| RT2 影子模式 | 读取Gazebo状态但不控制飞机 | 同run记录MWORKS输出、频率、延迟和部署后端差异 |
| RT3 悬停闭环 | MWORKS控制起飞后悬停 | 悬停稳定，断连能唯一切换本地px4ctrl |
| RT4 定点模式 | `W/A/S/D`参考跟踪 | 前后左右、松键保持、失焦超时和降落通过 |
| RT5 程控模式 | 8字或等价固定参考 | 与generated-C同场景A/B，轨迹和安全指标通过 |

若RT0不能稳定达到50 Hz，停止实时飞行界面实现，只保留离线/影子诊断路径。每一级失败都
形成明确blocker，不得跳级用UE动画、预录轨迹或QGC状态代替控制证据。

## 13. 实施拆分与完成定义

建议工作包：

1. RT0能力探针和结构化测量；
2. `StateFrame`、`ReferenceFrame`、`AttitudeThrustCommand` Schema及离线fixture；
3. MWORKS Realtime Adapter影子模式；
4. Model Studio Profile编辑、发布和禁用原因；
5. Flight Console选择器、状态卡和Runtime Console；
6. 悬停fallback与故障注入；
7. RT3至RT5同run运行证据和generated-C A/B报告。

只有以下条件全部满足，才能宣称“MWORKS实时联合仿真完成”：

- RT0至RT5逐级通过，证据均绑定同一`run_id`和Profile hash；
- 实测频率、P95/P99延迟、丢帧和超时满足冻结阈值；
- 定点与程控参考权威唯一，起飞只进入悬停；
- MWORKS断连能可靠切换本地px4ctrl悬停，空中无自动重启；
- QGC关闭、UE关闭或显示降级不影响控制闭环；
- generated-C与MWORKS Live在同场景、同参考、同指标下完成A/B；
- 运行日志、配置、hash、metrics和人工审核材料可复跑。
