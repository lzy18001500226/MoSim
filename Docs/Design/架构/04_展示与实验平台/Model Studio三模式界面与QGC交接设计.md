# Model Studio 三模式界面与 QGC 交接设计

> 状态：界面设计基线，2026-07-28。本文冻结 Model Studio 与 QGC/Flight
> Console 的职责和第一版界面，不证明 MWORKS Live、Gazebo 或飞行运行已通过。

实现边界：本文是目标界面合同，不是当前 APP 的完成报告。2026-07-28 起，比赛与
交付主线不再依赖 Orchestrator：已发布 Profile 是配置事实来源，操作者在可见终端执行
QGC 复制出的受审计命令，`prepare_operator_run.py` 冻结 RunManifest；QGC 只读消费其
状态。目标中的“主控制器先选、环路 owner 自动解析、场景注入默认关闭”仍由独立 APP
任务实现。当前实现核对以 `MWORKS控制器关系与组合架构.md` 第 4 节和
`Docs/Design/架构.md` 第 7、8 节为准。

## 1. 产品定位

Model Studio 是控制器与实验 Profile 的设计、校验、发布和工程入口，不是飞行地面站。
QGC/Flight Console 是在线飞行操作入口。运行命令、日志和错误始终保留在操作者可见的
终端中，不能由任一 GUI 隐藏启动或接管。

```text
Model Studio
  -> 编辑、校验、发布 ExperimentProfile
  -> 打开 MWORKS 模型、结果和代码工程
  -> 不替用户启动模型仿真、代码导出或飞行运行时

QGC / Flight Console
  -> 选择已发布 Profile
  -> 连接、解锁、起飞、任务、悬停、降落和安全停止
  -> 显示 Factory 二维态势、故障 ACK 与运行身份
  -> 复制已审计的前台命令，不在后台执行

可见终端 / 既有运行脚本
  -> 执行 prepare_operator_run.py，冻结不可变 RunManifest
  -> 启动经 Profile 绑定的 ROS/Gazebo/PX4/MAVROS 运行入口
  -> 将后端 ACK、日志与遥测写回本次 run_id 的证据目录
```

高频控制数据不得经过两个 GUI、JSON 文件队列或 Orchestrator 控制面。ROS1 承载实时
状态、参考、控制命令、诊断和注入事件；标准 MAVLink 承载 PX4 飞行状态和标准 ACK。
GUI 只承载低频 Profile、命令复制、状态展示和人工确认。

## 2. 顶部三模式

界面顶部使用稳定的三段式模式控件：

| 模式 | Model Studio 权限 | 第一版状态 |
| --- | --- | --- |
| 离线建模验证 | 检查模型、MIL、代码生成、打开模型和结果 | 可用 |
| 实时联合仿真 | 编辑、校验、发布候选 Profile，读取运行状态，请求安全停止 | RT0 前可见禁用 |
| 生成代码部署 | 发布 generated-C Profile、prepare，并交接 QGC | 只开放已有门禁能力 |

三个模式共享控制链层级和 Profile 语义，但每个模块的可用性按执行方式分别判断。离线
可用不等于 MWORKS Live 或 Gazebo 可用，代码生成通过也不等于飞行验收通过。

## 3. 控制链配置

标准页面先选择一个主控制器/控制器方案，再由 Registry 和 Profile 自动解析每个
环路的职责。位置环、速度环、姿态环和角速度环在默认模式中必须可见但只读/禁用，
这样用户能看懂当前控制器替换了哪一层，又不会把四个环路误认为可以任意拼接。

```text
主控制器 / 控制器方案       [选择]
位置环                      [自动显示 owner，禁用]
速度环                      [自动显示 owner，禁用]
姿态环                      [自动显示 owner，禁用]
角速度环                    [自动显示 owner，禁用]
控制分配 / 输出边界          [自动显示 owner，禁用]
增强层                      [默认无；兼容项可选]
安全约束                    [默认基础限幅]
场景扰动 / 故障注入          [可见，默认关闭]
编队参考                    [仅多机启用]
```

`so3_attitude` 等内环模块不能直接伪装成完整主控制器。若选择它，Profile 必须
同时声明兼容的外环和输出边界；否则 APP 应显示不兼容并禁止运行。

### 3.1 ATTITUDE_THRUST v1

第一版实时联合仿真固定：

```text
controller_id = official_pid
UI 名称 = PX4CTRL 官方位置外环 PID
augmentation_ids = [] 或 [awff]
output_variant = ATTITUDE_THRUST
attitude_inner_owner = px4_builtin_attitude_rate_v1
```

`AWFF` 是增强层，不得登记为独立名义控制器。自研 INDI、SMC、Backstepping 等姿态
内环在第一版实时联合仿真中保持可见禁用。未来只有在输出边界切换到
`BODY_RATE_THRUST`、`WRENCH` 或 `ROTOR_COMMAND`，并完成新的 Adapter、安全和运行
门禁后才能开放。

### 3.2 坐标与命令字段

跨进程四元数字段使用：

```text
q_enu_from_flu_xyzw
frame_contract_id = mosim_enu_flu_quaternion_xyzw_v1
```

现有控制核心 ABI 的 `wxyz` 不原地修改，由 Adapter 显式完成 `wxyz <-> xyzw`、
`ENU/FLU <-> NED/FRD` 和推力换算。往返 fixture 必须覆盖归一化、NaN/Inf 拒绝、
小范数拒绝和四元数符号连续。

## 4. 故障注入区

第一版只提供固定方向的风速和四个独立电机效率滑块。它们属于场景扰动/故障注入，
不是标准控制链中的“故障容错层”。注入区保持可见，但默认关闭；关闭时滑块不可用，
且不改变控制器组合。滑块改变的是待应用值，不连续发送：

```text
拖动滑块
  -> 开启“场景注入”
  -> 更新 requested_value
  -> 点击“复制应用命令”
  -> 操作者在可见终端执行离散故障请求
  -> ROS sidecar 或运行端返回同一 run_id 的 applied/rejected ACK
  -> UI 更新 applied_value
```

界面必须并列显示请求值和实际值。`accepted` 只代表受理，不能显示为已生效。
“恢复正常”调用事务命令 `restore_all_injections`，只有风速为 0 且四个电机效率均为
1.0 时才显示恢复完成；部分恢复使用 `partial_failure`。

## 5. 操作按钮

离线模式：

```text
校验配置 | 打开模型 | 打开结果 | 打开代码工程
```

在线模式：

```text
校验配置 | 发布 Profile | 查看 QGC 交接状态 | 查看 Flight Console 入口
```

Model Studio 不提供“解锁”“起飞”“开始任务”或“请求安全停止”。飞行中的安全停止只能
通过 QGC 原生安全操作或已绑定任务运行时的安全停止语义完成；不得把杀进程或
`stop_run` 当作飞行安全停止。

## 6. RunManifest 与状态

ExperimentProfile 由 Model Studio/配置目录维护，MissionArtifact 由 QGC 任务侧维护；
操作者执行可见终端中的 `prepare_operator_run.py` 后，才生成最终不可变 RunManifest。
QGC 不创建、修改或补写该文件，只读取当前活动指针和本次运行状态。最小字段包括：

```text
run_id
profile_id / profile_version / profile_hash
mission_id / mission_revision / mission_hash
controller_backend / controller_id / augmentation_ids
output_variant / attitude_inner_owner / command_adapter_id
reference_authority / command_authority
frame_contract_id
nominal_rate_hz / deadline_ms / max_command_age_ms
fallback_profile_id / PX4 parameter snapshot hash
scenario_id / world_hash / vehicle_ids
connection_contract_id / target_host / resolved_target_addresses
rt1_udp_port / ros_master_uri / local_advertised_ip
requested_rate_hz / selected_rate_hz / protocol_version
preflight_id / preflight_result_hash
```

RunManifest 在 `launch_prepared` 后不可修改。运行状态、分阶段 ACK、故障事件和遥测进入
独立 RunStatus/Event 记录，不持续回写 Manifest。

QGC 的“冻结配置”与“运行反馈”必须分开显示。`controller_backend` 由已发布
ExperimentProfile 在生成 RunManifest 时冻结；运行端仅可在 `telemetry.json` 写入
`mosim.operator_runtime_status.v1`。该状态必须同时携带 `run_id`、`experiment_profile_id`、
`experiment_profile_hash`、`controller_backend`、`state`、`reason_code` 与更新时间。QGC 对这四项
身份逐项匹配后才显示运行反馈，任何不匹配状态只显示“身份不匹配，已忽略”，不能覆盖地图或
冻结配置。

运行状态中的 `observability` 是可选的实测字段：RTT（P95）、抖动、命令年龄和丢包率只在对应
RT1/运行端同一 `run_id` 的指标存在时显示数值；没有指标时统一显示“未测量”。`alerts` 缺失表示
“运行端未上报告警”，空列表才表示“运行端报告无告警”。QGC 不以主机网卡总流量、候选频率或
固定零值补齐这些字段。

## 7. 在线连接与频率能力口径

Model Studio 可以编辑目标主机、RT1 UDP端口、ROS Master URI、本机广播 IP 和
50/100/200 Hz候选频率，并把它们随候选 Profile 进入校验。发布后 QGC 只能显示冻结的
端点和健康状态，不能维护第二套地址或频率编辑器。真实连接测试由可见终端中的对应预检
执行；失败时必须记录阶段、reason code、耗时和建议动作。

当前能力分层为：

```text
50 Hz = 候选基线，必须由 RT0 结果确认
100 Hz = 候选值，未形成能力声明前不能发布为实时可用
200 Hz = 新目标，能力待验证，不能发布为实时可用
```

200 Hz目标需要5 ms周期，因此其deadline、command age和fallback阈值必须由新的RT0结果重新
冻结，不能沿用50 Hz参数，也不能原地修改既有 Profile 哈希。QGC只显示 RunManifest 冻结后的
端点、Profile、RT0状态、RTT、command age、丢包和fallback，不提供第二套端点编辑。

## 8. 第一版界面验收

纯界面审核版必须满足：

- 三模式可见，当前模式有明确选中状态；
- 第一行先选主控制器，位置/速度/姿态/角速度环的 owner 自动显示且默认禁用；
- ATTITUDE_THRUST v1 的 PX4 内环和控制分配 owner 锁定清楚；
- AWFF 位于增强层，自研姿态内环在实时模式可见禁用；
- 场景扰动/故障注入区可见但默认关闭，风速和四电机效率均使用稳定尺寸滑块；
- 请求值与实际值分开显示；
- 不包含合成曲线、静态整机拓扑预览或伪运行结果；
- 离线操作和 QGC 飞行操作不会混淆；
- Studio 中的候选地址可编辑，但 QGC 对已发布 Profile 只读；真实握手结果必须来自可见终端，
  未通过时对应运行入口保持禁用；
- 50/100/200 Hz候选值与已经过 RT0 验证的能力不会混为一个“实时可用”状态；
- 普通桌面和较小窗口下文字不重叠、不越界；
- 审核版不启动 MWORKS、Gazebo、QGC 或修改模型。
