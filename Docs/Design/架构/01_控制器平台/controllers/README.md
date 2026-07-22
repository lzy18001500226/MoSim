# Controller Cards

> 历史说明：下文 G8/G9/G10/G11 是此前控制器研究与证据波次的标签。它们保留
> source/profile/evidence 追溯价值，但不定义当前 G1-G7 的执行顺序，也不授权在
> G1-G4 启动 MWORKS、Gazebo、代码生成或部署。当前入口是
> `Docs/Workflows/controller_evidence_closeout.md`。

本目录记录名义控制器规格。每个文档必须先说明控制链路位置、输入、输出层级、
是否复用PX4内环、MWORKS/codegen路线和当前证据状态。

状态含义：

```text
BACKLOG: 已列入路线，但没有实现承诺
DESIGNED: 链路位置和接口已设计
IMPLEMENTED: 已有代码或模型入口
MEASURED: 有指标结果
ACCEPTED: 用户审核通过并冻结为基线
```

`Config/profiles/catalog.json`中的`implementation_status`使用机器可检查状态：

```text
planned: 已登记，但不能作为active ExperimentProfile运行，必须被C-CTRL-01拒绝
implemented: 代码/模型和接口检查已通过，但运行证据未冻结
accepted: 用户审核通过并冻结为可复用基线
```

卡片状态和Profile状态不是同一字段。卡片可以处于`DESIGNED`，但只要Profile仍是
`planned`，对应ExperimentProfile就只能放在`Config/profiles/candidates/`。

## 历史批次边界

| 批次 | 卡片 | 说明 |
| --- | --- | --- |
| 冻结基线 | `px4ctrl.md` | G8生成core、Gazebo A/B、Diff单机/三机回归模板 |
| G9首批 | `PID.md`、`SE3.md`、`DFBC.md`、`SMC.md`、`NMPC.md` | 通过统一ATTITUDE_THRUST接口逐个证明控制器替换能力 |
| G9.5/G9.6论文复现 | `DFBC.md`、`NMPC.md`及对应论文证据 | 先复现高性能名义控制和抗风鲁棒DFBC，判断是否显著优于Basic外环 |
| G9增强 | `PID-INDI.md`、`../modules/INDI.md`，后续`DOB-ESO`、`L1`等 | 作为augmentation/safety/observer层，不默认等同名义控制器core |
| G10增强层矩阵 | `../控制增强与容错.md`、`../modules/` | DOB/ESO、L1/AWFF、INDI、安全过滤、故障分配、参数调度等关键类别逐个门禁和消融 |
| G11全控制器codegen | `../代码生成与PX4部署.md` | 所有implemented/accepted控制器和增强组合都走MWORKS模型、生成代码、离线一致性和ROS/Sunray回灌 |
| 代表扩展 | `LQI.md`、`LMPC.md`、`Backstepping.md`、`Feedback-Linearization.md` | 覆盖线性积分、优化控制、递推设计和反馈线性化路线 |
| 经典/现代候选 | `LQR-LQG.md`、`H-Infinity.md`、`Mu-Synthesis.md`、`SO3-Attitude.md`、`Feedback-Linearization.md`、`NDI.md`、`Backstepping.md`、`Passivity-Based.md` | 用于补全控制理论覆盖，不自动进入第一阶段实现 |
| 智能/复合候选 | `Fuzzy.md`、`ANFIS.md`、`Neural-Compensation.md`、`ILC.md`、`RL-Policy.md` | 优先作为调参、补偿、残差、重复轨迹学习或研究路线，不直接替代安全关键闭环 |
| MPC族候选 | `Robust-MPC.md`、`Adaptive-MPC.md`、`Tube-MPC.md`、`Learning-MPC.md`、`Distributed-MPC.md`、`MPC-Variants.md` | 先冻结模型、约束、实时性和求解器边界，再逐个释放 |

研究/候选卡片只代表需求和架构位置已记录，不代表当前实现承诺。任何卡片进入
实施前，都必须补充实验Profile、参考实现、参数、门禁和证据目录。

历史控制器路线不是“G10后冻结一个最佳栈”。历史 G11 要求所有进入`implemented`或
`accepted`的控制器、以及被批准的控制器+增强组合，都完成MWORKS/codegen
闭环；只跑通最佳候选不能代表平台控制器族完成。

历史 G9 首批机器入口：

```text
Config/profiles/experiments/g9_official_pid_figure8_v1.json
Config/profiles/experiments/g9_se3_basic_figure8_v1.json
Config/profiles/experiments/g9_dfbc_basic_figure8_v1.json
Config/profiles/experiments/g9_smc_boundary_layer_figure8_v1.json
Config/profiles/experiments/g9_pid_indi_figure8_v1.json
Config/profiles/experiments/g9_nmpc_outer_figure8_v1.json
```

以下 `g9_*` 条目是历史 `implemented` 证据入口，不是当前运行命令。`g9_official_pid_figure8_v1`当前是`implemented`入口：C++ ATTITUDE_THRUST
后端、静态门禁、单机Gazebo任务、Diff单机和Diff三机证据已存在；用户冻结
验收、MWORKS生成代码验收和PX4-native部署仍需后续证据。

`g9_se3_basic_figure8_v1`当前是`implemented`入口：C++ ATTITUDE_THRUST
后端、静态门禁、Gazebo基础轨迹、Diff单机和Diff三机证据已存在；用户冻结验收、
MWORKS生成代码验收和PX4-native部署仍需后续证据。当前运行参数固定记录为
`PX4CTRL_CORE_PROFILE=se3_basic`、`PX4CTRL_KP_XY=12`、`PX4CTRL_KP_Z=5`、
`PX4CTRL_KV_XY=6.5`、`PX4CTRL_KV_Z=4`，不得污染G8或PID默认参数。

`g9_dfbc_basic_figure8_v1`当前是`implemented`入口：C++ ATTITUDE_THRUST
后端、静态门禁、Gazebo基础轨迹、Diff单机和Diff三机证据已存在；用户冻结验收、
MWORKS生成代码验收和PX4-native部署仍需后续证据。当前运行参数固定记录为
`PX4CTRL_CORE_PROFILE=dfbc_basic`、`PX4CTRL_KP_XY=12`、`PX4CTRL_KP_Z=5`、
`PX4CTRL_KV_XY=6.5`、`PX4CTRL_KV_Z=4`。当前只代表DFBC Basic的
`p/v/a/yaw -> attitude/thrust`映射，不代表jerk/snap高阶DFBC、body-rate或
torque-level控制器。

`g9_smc_boundary_layer_figure8_v1`当前是`implemented`入口：C++ ATTITUDE_THRUST
后端、静态门禁、Gazebo基础轨迹、Diff单机和Diff三机证据已存在；用户冻结验收、
MWORKS生成代码验收和PX4-native部署仍需后续证据。当前运行参数固定记录为
`PX4CTRL_CORE_PROFILE=smc_boundary_layer`、`PX4CTRL_KP_XY=12`、
`PX4CTRL_KP_Z=5`、`PX4CTRL_KV_XY=6.5`、`PX4CTRL_KV_Z=4`、
`PX4CTRL_SMC_ETA_XY=0.1`、`PX4CTRL_SMC_ETA_Z=0.05`、
`PX4CTRL_SMC_PHI_XY=0.4`、`PX4CTRL_SMC_PHI_Z=0.35`。当前只代表一阶
boundary-layer SMC外环加速度增强，不代表terminal/super-twisting、body-rate、
torque-level或rotor-level SMC。

`g9_pid_indi_figure8_v1`当前是`implemented`入口：C++ ATTITUDE_THRUST
后端、静态门禁、Gazebo基础轨迹、Diff单机和Diff三机证据已存在；用户冻结验收、
MWORKS生成代码验收和PX4-native部署仍需后续证据。当前运行参数固定记录为
`PX4CTRL_CORE_PROFILE=pid_indi`、`PX4CTRL_KP_XY=12`、`PX4CTRL_KP_Z=5`、
`PX4CTRL_KV_XY=6.5`、`PX4CTRL_KV_Z=4`、`PX4CTRL_INDI_GAIN_XY=0.12`、
`PX4CTRL_INDI_GAIN_Z=0.06`、`PX4CTRL_INDI_INCREMENT_LIMIT_XY=0.35`、
`PX4CTRL_INDI_INCREMENT_LIMIT_Z=0.15`。当前只代表PID外环上的有界
平动加速度残差增强，不代表独立INDI、body-rate、torque-level或rotor-level
INDI。

`g9_nmpc_outer_figure8_v1`当前是`implemented`入口：C++ ATTITUDE_THRUST
后端、静态门禁、Gazebo基础轨迹、Diff单机和Diff三机证据已存在；用户冻结验收、
MWORKS生成代码验收和PX4-native部署仍需后续证据。当前运行参数固定记录为
`PX4CTRL_CORE_PROFILE=nmpc_outer`、`PX4CTRL_KP_XY=12`、`PX4CTRL_KP_Z=5`、
`PX4CTRL_KV_XY=6.5`、`PX4CTRL_KV_Z=4`、`PX4CTRL_NMPC_HORIZON_S=0.25`、
`PX4CTRL_NMPC_POSITION_WEIGHT_XY=2.0`、`PX4CTRL_NMPC_CONTROL_WEIGHT_XY=0.0002`。
当前只代表短视界约束外环加速度优化后端，不代表完整非线性在线求解器、
rotor-level NMPC或硬实时可行性证明。

实施入口固定为`Docs/Workflows/add_controller.md`。不要绕过source-basis packet、
ControllerProfile、candidate ExperimentProfile和静态拒绝证明直接写控制器代码。
