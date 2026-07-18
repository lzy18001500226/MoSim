# Model Studio 三模式界面与 QGC 交接设计

> 状态：界面设计基线，2026-07-18。本文冻结 Model Studio、QGC 与
> Orchestrator 的职责和第一版界面，不证明 MWORKS Live、Gazebo 或飞行运行已通过。

## 1. 产品定位

Model Studio 是控制器与实验 Profile 的设计、校验和发布入口，不是飞行地面站。
QGC/Flight Console 是在线飞行操作入口。Orchestrator 是唯一运行状态机和命令裁决者。

```text
Model Studio
  -> 编辑、校验、发布 ExperimentProfile
  -> 执行离线模型检查、MIL、代码生成和结果打开
  -> 请求 prepare_run

QGC / Flight Console
  -> 选择已发布 Profile
  -> 连接、解锁、起飞、任务、悬停、降落和安全停止

Orchestrator
  -> 校验 Profile、MissionArtifact 和运行环境
  -> 生成不可变 RunManifest
  -> 裁决所有运行命令、ACK、状态和冲突
```

高频控制数据不得经过两个 GUI、JSON 文件队列或 Orchestrator 控制面。ROS1 承载实时
状态、参考、控制命令、诊断和注入事件；标准 MAVLink 承载 PX4 飞行状态和标准 ACK。

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

界面按层级展开，不使用一个含混的“控制器”下拉框：

```text
任务轨迹
位置 / 平动外环
姿态 / 角速度内环
增强与扰动补偿
安全层
故障与控制分配
输出边界
```

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

第一版只提供固定方向的风速和四个独立电机效率滑块。滑块改变的是待应用值，不连续发送：

```text
拖动滑块
  -> 更新 requested_value
  -> 点击“应用”
  -> Orchestrator 受理
  -> Gazebo 插件返回 applied/rejected
  -> UI 更新 applied_value
```

界面必须并列显示请求值和实际值。`accepted` 只代表受理，不能显示为已生效。
“恢复正常”调用事务命令 `restore_all_injections`，只有风速为 0 且四个电机效率均为
1.0 时才显示恢复完成；部分恢复使用 `partial_failure`。

## 5. 操作按钮

离线模式：

```text
校验配置 | 打开模型 | 运行 MWORKS MIL | 生成 C 代码 | 打开结果
```

在线模式：

```text
校验配置 | 发布 Profile | 准备运行 | 进入 QGC | 请求安全停止
```

Model Studio 不提供“解锁”“起飞”或“开始任务”。“请求安全停止”与 QGC 调用同一个
幂等 Orchestrator `safe_stop`，不得直接发布 ROS/MAVROS/PX4 命令，也不得把杀进程或
`stop_run` 当作飞行安全停止。

## 6. RunManifest 与状态

ExperimentProfile 由 Model Studio 维护，MissionArtifact 由 QGC 任务侧维护，最终不可变
RunManifest 由 Orchestrator 生成。最小字段包括：

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
```

RunManifest 在 `ready_on_ground` 后不可修改。运行状态、分阶段 ACK、故障事件和遥测进入
独立 RunStatus/Event 记录，不持续回写 Manifest。

## 7. RT0 前界面口径

以下数值是候选 Profile 默认值，不是已验证能力：

```text
nominal_rate_hz = 100
deadline_ms = 10
degraded_after_consecutive_misses = 3
max_command_age_ms = 50
failsafe_escalation_ms = 100
```

RT0 前 `mworks_live` 必须显示“候选值 / 能力待验证”并保持禁用。若 RT0 只能稳定达到
50 Hz，发布新的 Profile version/hash，并重新冻结整组频率和超时参数，禁止原地修改。

## 8. 第一版界面验收

纯界面审核版必须满足：

- 三模式可见，当前模式有明确选中状态；
- 控制链按层级展开，ATTITUDE_THRUST v1 的 PX4 内环锁定清楚；
- AWFF 位于增强层，自研姿态内环在实时模式可见禁用；
- 风速和四电机效率均使用稳定尺寸滑块；
- 请求值与实际值分开显示；
- 不包含合成曲线、静态整机拓扑预览或伪运行结果；
- 离线操作和 QGC 飞行操作不会混淆；
- 普通桌面和较小窗口下文字不重叠、不越界；
- 审核版不启动 MWORKS、Gazebo、QGC 或修改模型。
