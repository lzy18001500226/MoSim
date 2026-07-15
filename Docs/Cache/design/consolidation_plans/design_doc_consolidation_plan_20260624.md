# MoSim设计文档合并与索引重构方案

> 日期：2026-06-24
> 位置：`Docs/Cache/design/`
> 性质：最终执行版迁移方案。本文用于指导 `Docs/Design/架构/` 原地重构；
> 不代表文件移动已经执行。

## 1. 当前结论

当前文档的问题不是“内容不够”，而是入口和任务选择不够硬：

```text
文档数量偏多
多个文档都在讲当前阶段
多个文档都在讲控制器分类
多个文档都在讲MWORKS/PX4/Gazebo关系
多个文档都在讲FAST-LIO/EGO边界
Agent容易从长文档局部内容出发，而不是从项目任务主表出发
```

所以本次重构目标不是为了减少文件数量本身，而是建立：

```text
一个入口
一张任务主表
少量分域规范
明确的废弃/参考文档
可用rg快速验证的索引规则
```

当前最终决策：

```text
不再新建第三套并行架构目录；
不在 Docs/Design 根目录继续平铺专题长文档；
直接把 Docs/Design/架构/ 原地重构成唯一正式专题文档树；
Docs/Design/旧架构/ 和被吸收文档退出 active source；
Docs/Cache/design/ 只保留迁移方案、历史草稿和被吸收材料。
```

## 2. 对两个争议文档的判断

| 文档 | 当前判断 | 建议处理 |
| --- | --- | --- |
| `Docs/Design/架构/MoSim体系.md` | 旧版研究草案，内容像百科，不应作为执行入口 | 唯一内容抽取后归档到 `Docs/Cache/design/superseded/`；不再出现在正式入口 |
| `Docs/Design/架构.md` | 当前系统架构短入口，不应直接废弃 | 暂时保留，但压缩为“系统架构+当前路线+禁止边界”；不再承载详细任务清单、控制器百科或门禁细节 |

因此：

```text
MoSim体系.md = 建议废弃/归档
架构.md = 建议保留为短入口，但要去重
```

## 3. 我对项目的任务理解

MoSim不是单纯控制器项目，也不是单纯EGO/FAST-LIO复现项目。

项目目标应理解为：

```text
基于MWORKS完成四旋翼控制系统建模、仿真、优化和代码生成；
通过Sunray/PX4/Gazebo完成真实飞控接口下的工程闭环验证；
通过MID360/FAST-LIO/EGO/EGO-Swarm接入自主飞行能力；
最终通过RViz/Gazebo/UE/前端和报告材料完成可审查、可演示、可复现的比赛交付。
```

对应工作块：

| 编号 | 工作块 | 是否当前最小闭环必须 |
| --- | --- | --- |
| S0 | 赛题范围、系统口径、禁止路线 | 是 |
| S1 | Sunray/PX4/Gazebo/MAVROS运行基线 | 是 |
| S2 | 状态源、MID360、FAST-LIO、Gazebo truth边界 | 是，先做定位评价子集 |
| S3 | px4ctrl单机基础控制基准 | 是 |
| S4 | 起飞、悬停、8字、螺旋、阶跃、目标点轨迹接口 | 是 |
| S5 | EGO/EGOv2/Diff-Planner单机规划闭环 | 是 |
| S6 | EGO-Swarm 2/3机官方工程基线 | 是 |
| S7 | MWORKS Golden Slice与生成C/C++回灌 | 是 |
| S8 | PID/SE3/DFBC/NMPC/INDI/L1控制器族扩展 | 后续 |
| S9 | 鲁棒、安全、故障容错、控制分配 | 后续 |
| S10 | 真机化、C++化、Orin NX/V6X部署边界 | 后续但需提前约束代码形态 |
| S11 | RViz/Gazebo/UE/前端展示 | 后续展示，不拥有控制成功判定 |
| S12 | 自动评估、报告、视频、提交包 | 后续交付 |

推进策略：

```text
先收口S1-S7，形成最小大系统验证台；
再用该验证台逐个释放S8控制器族；
随后进入S9/S10/S11/S12。
```

## 3.1 重构前必须处理的问题清单

本节记录 2026-06-24 重构前复审发现的硬问题。它们不是新的功能需求，而是
文档重构时必须同步消除的执行歧义。若这些问题未处理，即使文件移动完成，
后续 Agent 仍可能读错入口、选错任务顺序或混淆实验指标。

### 3.1.1 WF-01 Goal顺序必须和系统架构统一

当前根 `架构.md` 已经采用：

```text
最小大系统闭环
  -> 代表控制器模板
  -> MWORKS Golden Slice
  -> 批量控制器扩展
```

本轮复审前，`MoSim研发工作流与Agent任务编排规范.md` 中存在旧顺序残留：

```text
Goal 1 / Goal 2: px4ctrl 基础和轨迹参数冻结
Goal 3: px4ctrl Golden Slice代码链
Goal 4: EGO单机最小闭环
Goal 5: EGO-Swarm 2/3机官方链路基线
Goal 6: MWORKS版px4ctrl接入自主飞行链路
```

这类残留会让后续执行再次先进入 MWORKS/codegen，而不是先把 Sunray/PX4/
Gazebo/RViz/FAST-LIO/EGO/Swarm 最小大系统验证台收口。2026-06-24 复审已
把 WF-01 入口顺序改为下列顺序；后续重构必须保持一致。

重构时建议统一为：

```text
Goal 1: Sunray/PX4/MAVROS/px4ctrl 起飞-悬停-降落基线
Goal 2: 8字、螺旋、阶跃、参数与误差基线收口
Goal 3: FAST-LIO独立评价 + EGO/EGOv2/Diff单机 + EGO-Swarm 2/3机工程基线
Goal 4: px4ctrl / official PID / SE3 Basic 代表控制器模板
Goal 5: MWORKS Golden Slice，离线一致性 + 生成C/C++ + Gazebo回灌
Goal 6: MWORKS版控制器接回EGO/Swarm链路
```

若保留 EGO 与 MWORKS 并行推进，也必须写成显式并行分支，而不是让 Goal 编号
表达出相反的主线顺序。

### 3.1.2 Profile槽位和旧字段必须清零

正式 `ExperimentProfile` 槽位必须统一为：

```text
scenario_profile
plant_profile
sensor_profile
state_source_profile
height_source_profile
truth_profile
frequency_profile
trajectory_profile
planner_profile
controller_profile
augmentation_profile
safety_profile
adapter_profile
fault_profile
disturbance_profile
display_profile
evaluation_profile
```

重构时必须消除或明确降级以下旧字段：

```text
vehicle_profile
vehicle_profile_id
trajectory_or_planner_profile
```

`reference_shaper_profile` 需要单独决策：若保留，必须加入正式槽位表，并说明
它和 `trajectory_profile`、`planner_profile`、`safety_profile` 的边界；若不
保留，则只允许在历史/cache文档中出现。

禁止在正式入口里继续把 plant、sensor、state、truth、height 合成一个
`vehicle_profile`。否则控制误差无法判断来自 plant、传感器、定高、状态估计
还是控制器。

### 3.1.3 上游版本、许可证和本地patch必须形成活动证据入口

需求文档已经列出上游版本、license、patch 和复现/自研边界需求，但正式文档
树还缺一个活动证据入口。重构时必须指定一个位置记录：

```text
upstream_project
local_path
upstream_commit_or_version
license
local_patch_summary
modified_files
launch_or_param_changes
reproduction_status
prohibited_claims
evidence_path
```

覆盖对象至少包括：

```text
Sunray
PX4
FAST-LIO
EGO-Planner-v1
EGO-Planner-v2
Diff-Planner
EGO-Swarm
px4ctrl upstream / Sunray工程版
主要控制器论文或开源实现
UE/Gazebo/模型资产来源
```

没有这张清单，后续答辩无法说明哪些是上游复现、工程适配、参数优化、
MWORKS重建或自研控制器。

### 3.1.4 Orchestrator、Profile Registry、Launch Plan和Run Packet落点必须固定

当前架构已经明确“前端只提交 ExperimentProfile，不能直接拼裸 `sh` 命令”，
但重构时还必须把以下落点写清楚：

```text
Profile schema 存放位置
Profile registry 存放位置
Launch template 存放位置
Launch plan 生成和留存位置
Run packet / manifest / metrics / evidence 目录结构
Profile Validator 的最小检查规则
不兼容组合的拒绝/降级格式
```

第一阶段前端/脚本只允许选择已注册 Profile。按钮、下拉框、滑块最终都必须
映射到 `ExperimentProfile` 字段，不允许绕过 Orchestrator 直接拥有控制发布权。

### 3.1.5 FAST-LIO、Gazebo truth、Gazebo Z定高替身表述必须防止混报

正式文档必须保持以下实验组隔离：

```text
A组: PX4/MAVROS融合状态 -> 控制，Gazebo truth -> 评价
B组: Gazebo truth debug state -> 控制器极限能力诊断，不能进主排行榜
C组: FAST-LIO直接输出 -> 定位独立评价，不能宣称闭环控制成功
D组: FAST-LIO -> PX4 EKF -> MAVROS local position -> 控制闭环
E组: FAST-LIO XY/Yaw + Gazebo/激光定高替身 Z -> Hybrid-Z 单独标注
```

`vision_pose`、`external odometry`、`PX4 EKF fusion` 等术语要写清楚它们是
把外部位姿观测送入 PX4 估计器的路径，不是 MoSim 另一个控制器状态源。若使用
Gazebo Z 作为真机激光定高替身，必须进入 `height_source_profile`，不能静默
混入 FAST-LIO 后宣称“纯FAST-LIO定位闭环”。

### 3.1.6 控制器文档必须按控制链路位置组织

重构后的控制器文档不能只是算法百科。每个控制器或模块必须先声明：

```text
属于 nominal controller / augmentation / safety / allocation / trajectory
插在 PX4/MoSim 控制链路哪一环
需要哪些输入阶次：p/v/a/jerk/snap、状态、扰动估计、故障状态
输出层级：ATTITUDE_THRUST / BODY_RATE_THRUST / WRENCH / ROTOR / 补偿项
是否复用 PX4 姿态环、角速度环和控制分配
MWORKS建模和C/C++生成路径
Gazebo/Sunray验收场景
当前状态和禁止声明
```

特别注意：

```text
INDI、L1、DOB/ESO、AWFF 不是普通外环控制器的平级替代，优先属于增强模块。
CBF、Safety Filter、Reference Governor 属于安全/约束层，不应写入控制器内部状态。
Fault Allocation 属于分配/执行器层，第一阶段 ATTITUDE_THRUST 不正式释放。
DFBC-Full 才强依赖 jerk/snap；不能给所有控制器文档都机械加 jerk/snap 需求。
SMC、Backstepping、Fuzzy、NN/RBF、RL 等可以先建 BACKLOG/DESIGNED 规格，但不能宣称已闭环。
```

### 3.1.7 正式入口与cache/reference边界必须可被rg验证

重构完成后，正式入口不得再把以下路径作为 active source：

```text
Docs/Design/旧架构/
Docs/Cache/design/
Docs/Design/架构/MoSim体系.md
Docs/Design/架构/架构.md
旧 ROS2/PX4 x500 路线
```

这些路径可以在 cache、迁移方案和历史追踪中出现，但不能出现在正式
`README.md`、根 `架构.md`、任务路线图、Workflow 或 Index 中作为当前执行入口。

建议重构验收增加：

```powershell
rg -n "MoSim体系\\.md|Docs/Design/旧架构|Docs/Cache/design|ROS2/PX4 x500|trajectory_or_planner_profile|vehicle_profile" Docs/Design/README.md Docs/Design/架构.md Docs/Design/架构/MoSim研发工作流与Agent任务编排规范.md Docs/Workflows Docs/Index -g "*.md"
```

允许命中项必须逐条分类为：

```text
cache/reference 合法命中
迁移方案合法命中
正式入口非法命中，需要修复
```

## 4. 建议目标文档结构

不建议把所有内容合并成一份大文档。目标结构应按“入口/任务/分域规范”分层。
考虑到根目录平铺文件过多不利于审核，正式重构采用“`Docs/Design/架构/`
原地文件夹化”的方式。

主体目录只允许一层。`controllers/`、`modules/`、`planners/` 是算法卡片
子目录，允许存在，但不能继续无限嵌套。每个一级文件夹和算法卡片子目录
必须有 `README.md`，说明本组负责什么、不负责什么、当前阶段应读哪个文件。

### 4.1 保留为正式入口

| 文档 | 目标职责 | 调整建议 |
| --- | --- | --- |
| `README.md` | 唯一设计目录入口 | 只保留读文档顺序、当前正式/参考文档列表和证据边界 |
| `架构.md` | 系统级架构入口 | 只保留四层架构、当前运行线、最小大系统边界、禁止路线；删除/迁出详细任务和重复控制器路线 |
| `MoSim研发工作流与Agent任务编排规范.md` | 唯一任务清单和执行选择入口 | 保留S0-S12任务主表、6个Goal、附录A/B；不写控制理论细节 |

### 4.2 保留为正式分域规范

| 文档 | 目标职责 | 是否建议合并 |
| --- | --- | --- |
| `赛题.md` | 赛题原文、提交要求、答辩口径 | 保留独立 |
| `MoSim统一控制接口规范.md` | 状态、轨迹、输出层级、Adapter、频率、坐标系 | 保留独立 |
| `MoSim单机控制器实现规范.md` | px4ctrl、PID、SE3等单机控制器实现 | 保留，但删掉与总览/调参重复的长列表 |
| `MoSim控制器代码生成与PX4部署规范.md` | MWORKS代码生成、C/C++包装、PX4/MAVROS部署 | 保留，可吸收 `真机化收尾` 的可部署约束 |
| `MoSim控制系统测试与评价规范.md` | 场景、指标、评价、横向对比、报告证据 | 保留独立 |
| `MoSim_FASTLIO定位闭环与规划复现基础方案.md` | FAST-LIO、状态源替换、点云地图、PX4 EKF融合 | 保留独立 |
| `MoSim规划与编队控制接口规范.md` | EGO/EGO-Swarm、轨迹、编队、多机隔离 | 保留独立 |
| `MoSim控制增强与容错规范.md` | INDI、L1、DOB、故障、分配、安全过滤 | 保留为后续/backlog规范 |

### 4.3 建议合并或降级

| 文档 | 建议处理 | 理由 |
| --- | --- | --- |
| `MoSim体系.md` | 归档/删除正式入口 | 与控制体系总览、架构、接口规范重复，且已标为旧草案 |
| `MoSim控制体系总览.md` | 从“正式入口”降级为“控制器族索引/百科”或吸收入 `架构.md` + 控制器实现规范 | 现在既是入口又是百科，容易和WF-01、架构.md重复 |
| `MoSim控制器管理与配置规范.md` | 阶段性降级为未来Controller Manager规范，当前只保留关键Profile字段到接口/工作流 | 当前最小闭环不需要完整Manager体系，长文档容易让Agent抢跑 |
| `MoSim控制器调参与参数优化规范.md` | 与测试评价规范建立强互链，后续可合并为“测试、调参与评价规范” | 调参和评价高度耦合，当前分开后容易重复阈值和场景 |
| `MoSim真机化收尾与C++化重构方案.md` | 合并到代码生成/PX4部署规范，保留一节“T0/T1/T2/T3代码形态约束” | 文档较短，内容属于部署和代码形态边界 |

### 4.4 建议文件夹结构

最终目标结构：

```text
Docs/Design/
  README.md
  需求.md
  架构.md
  赛题.md

  架构/
    README.md

    00_架构与任务/
      README.md
      系统架构.md
      任务路线图.md
      系统集成接口与编排.md

    01_控制器平台/
      README.md
      统一控制接口.md
      单机控制器实现.md
      代码生成与PX4部署.md
      控制增强与容错.md
      controllers/
        README.md
        px4ctrl.md
        PID.md
        LQI.md
        LQR-LQG.md
        SE3.md
        DFBC.md
        Backstepping.md
        SMC.md
        Fuzzy.md
        Neural-Compensation.md
        RL-Policy.md
        LMPC.md
        NMPC.md
      modules/
        README.md
        INDI.md
        L1.md
        AWFF.md
        DOB-ESO.md
        Safety-Filter.md
        Fault-Allocation.md

    02_感知定位与规划集群/
      README.md
      FASTLIO定位闭环.md
      规划与编队控制接口.md
      planners/
        README.md
        EGO-Planner-v1.md
        EGO-Planner-v2.md
        Diff-Planner.md
        EGO-Swarm.md

    03_测试调参与证据/
      README.md
      测试与评价.md
      调参与参数优化.md
      真机化与C++化.md

    04_展示与实验平台/
      README.md
      RViz与Gazebo审核.md
      UE展示与传感器显示.md
      前端实验编排.md

    archive_index.md

  cache/
    README.md
    superseded/
    migration_plans/
    old_architecture/
```

说明：

```text
根目录只放总入口、需求、架构入口、赛题原始口径和架构文件夹。
cache作为单独归档区，但cache内部也必须有README和分类目录。
所有被废弃、吸收、历史路线、旧方案、旧架构都进入cache，不再留在根目录。
```

### 4.5 控制器算法文档策略

控制器算法很多，但本项目需要提前把“要做的控制器、增强模块、
安全模块和故障分配模块”全部建立可索引规格。关键不是每份文档
现在都实现，也不是先写控制理论长文，而是每份文档必须先讲清楚：

```text
它属于控制器、增强模块、安全模块还是故障分配模块；
它插在PX4/MoSim控制链路的哪一环；
它需要什么输入；
它输出到哪个控制层级；
它是否依赖PX4内环；
它如何进入MWORKS建模、生成代码和Gazebo验证。
```

推荐策略：

```text
controllers/ 管单机控制器核心
modules/ 管增强、观测器、安全过滤和故障分配模块
每个计划要做的核心算法都提前建立独立规格
每份规格先完成链路定位矩阵，再决定是否进入实现
文档可处于DESIGNED/BACKLOG状态，但必须说明链路位置和接口需求
只有完成门禁后才允许标记IMPLEMENTED/MEASURED/ACCEPTED
```

最小必入文档范围：

```text
控制器核心：
px4ctrl、PID、LQI、SE3、DFBC、SMC、LMPC、NMPC

增强/观测/安全/故障模块：
INDI、L1、AWFF、DOB-ESO、Safety-Filter、Fault-Allocation
```

其中LMPC、LQI、SMC、AWFF、DOB/ESO、安全过滤、故障分配不能只出现在
任务总览或backlog列表中；它们必须有独立文档，并在文档首页说明自己
对应的PX4/MoSim控制链路位置。后续实现顺序可以延后，但索引和边界必须
先固定。

#### 4.5.1 当前控制器覆盖审计结论

本次重构必须把“文档覆盖”和“工程实现覆盖”分开记录。不能因为某类
控制器出现在总览或backlog中，就把它当成已实现或已验证。

当前可从工程目录直接看到的控制器/模块入口主要集中在：

```text
Config/controllers/
  pid
  improved_pid
  enhanced_pid
  awff_pid
  awff_sysblock
  awff_indi_sysblock
  awff_fault_compensation_sysblock
  awff_complete_system
  l1_residual_sysblock
  l1_fault_allocation_sysblock
  l1_online_fault_allocation_sysblock
  l1_multi_fault_isolation_sysblock
  linear_mpc_sysblock
  linear_mpc_online_fault_allocation_sysblock
  nmpc_indi_l1

Models/QuadrotorControllerBlocks/
  AWFF_*.mo
  AWFF_INDIControllerEquation_Sysblock.mo
  AWFF_L1*.mo
  AWFF_LinearMPC*.mo
  AWFF_QPNMPCSafetyController_Sysblock.mo
  PX4CTRL_Core_*.mo
```

因此当前实现侧更接近：

```text
PID / Improved PID / Enhanced PID
AWFF
AWFF + INDI
L1 residual / L1 fault allocation
Linear MPC
NMPC-INDI-L1组合入口
px4ctrl core抽取/探针入口
```

而以下控制器族目前主要是设计或backlog覆盖，不能宣称已有可运行闭环：

```text
SMC / Super-Twisting SMC / Terminal SMC
Backstepping / Adaptive Backstepping
SE3 Basic / SO3
LQI
Fuzzy PID / Fuzzy-SMC
NN/RBF compensation
RL gain scheduler / RL residual / end-to-end RL
```

这意味着当前控制器覆盖的判断应写成：

```text
文档视野：较宽，但仍需要按PX4/MoSim链路位置重排。
工程实现：尚不全面，SMC、Backstepping、SE3、LQI、Fuzzy、NN/RBF、RL缺少已确认实现。
仿真验证：每个控制器必须单独给出MWORKS/Gazebo/Sunray证据，不能继承同类或组合控制器的结论。
```

SMC必须列为明确缺口，而不是只出现在“现代控制算法”或“鲁棒控制候选”
文字中。第一版建议按以下路线进入正式文档：

```text
SMC v1:
  位置/速度外环鲁棒控制
  输出ATTITUDE_THRUST
  复用PX4姿态环和角速度环
  重点处理边界层、饱和、抖振和采样频率

SMC v2:
  Super-Twisting SMC或Terminal SMC
  仍优先外环输出ATTITUDE_THRUST
  通过基础验收后再研究姿态/角速度层

SMC v3:
  姿态层或BODY_RATE_THRUST层SMC
  只有在ATTITUDE_THRUST模板、状态源、频率和安全限制稳定后才允许进入
```

INDI也必须重新定位。INDI不是普通外环控制器的平替，而是更适合放在：

```text
姿态/角速度内环增强
加速度或角速度增量动态逆
高动态轨迹跟踪补偿
与DFBC、NMPC、AWFF或L1组合的增强模块
```

因此 `modules/INDI.md` 必须说明：

```text
它是否复用PX4姿态/角速度内环；
是否要求BODY_RATE_THRUST；
是否只是作为AWFF/PID/DFBC/NMPC的增强模块；
不能把INDI直接当成一个和PID/SMC/SE3同层级的外环控制器。
```

智能控制相关内容必须分层，不允许笼统写“神经网络控制器”或“RL控制器”：

```text
Fuzzy PID / Fuzzy-SMC:
  增益调度或边界层调节，优先作为传统控制器增强。

NN/RBF compensation:
  扰动、未建模非线性或Backstepping/SMC/SE3补偿项。
  训练不进入实时闭环，部署时应冻结小模型或查表/显式函数。

RL gain scheduler:
  输出PID/SMC/MPC参数或权重，必须有传统控制器fallback。

RL residual:
  输出有界残差，必须接Safety Filter和fallback。

End-to-end RL:
  只作为远期研究候选，第一批不进入控制闭环验收。
```

重构后必须新增或补齐一张“控制器实现覆盖矩阵”，每行至少包含：

```text
控制器/模块名称
类别：控制器 / 增强模块 / 安全模块 / 故障分配 / 调参模块
PX4/MoSim链路位置
输入需求
输出层级
是否替换PX4某一环
MWORKS模型是否存在
C/C++生成是否存在
Gazebo/Sunray闭环是否存在
指标证据是否存在
当前状态：BACKLOG / DESIGNED / IMPLEMENTED / MEASURED / ACCEPTED
禁止声明
```

这张矩阵应作为后续Agent执行入口之一，防止后续再次把“规划中的控制器”
误判成“已有实现的控制器”。

建议第一批独立规格：

| 类别 | 文档 | PX4/MoSim链路位置 |
| --- | --- | --- |
| 基准控制器 | `controllers/px4ctrl.md` | 外环生成 attitude/thrust，复用PX4姿态/角速度内环 |
| 经典控制器 | `controllers/PID.md` | 位置/速度/高度外环，输出 ATTITUDE_THRUST |
| 线性现代控制 | `controllers/LQI.md` | 增广状态反馈外环或姿态/位置环，输出层级需明确 |
| 几何控制 | `controllers/SE3.md` | SE(3)外环，通常输出 ATTITUDE_THRUST 或 BODY_RATE_THRUST |
| 微分平坦 | `controllers/DFBC.md` | 使用p/v/a/jerk/snap，至少需要 BODY_RATE_THRUST 才能充分发挥 |
| 滑模控制 | `controllers/SMC.md` | 外环或姿态环鲁棒控制，需明确是否替换PX4姿态环 |
| 线性MPC | `controllers/LMPC.md` | 外环优化控制，输出加速度/姿态/推力或BodyRate |
| 非线性MPC | `controllers/NMPC.md` | 高阶状态约束优化，输出层级可到 BODY_RATE/WRENCH |
| 增量动态逆 | `modules/INDI.md` | 角速度/加速度内环增强，通常需要更底层接口 |
| L1自适应 | `modules/L1.md` | 扰动/模型不确定性补偿模块，叠加在外环或内环 |
| AWFF | `modules/AWFF.md` | 加速度/扰动前馈补偿模块，服务轨迹跟踪 |
| DOB/ESO | `modules/DOB-ESO.md` | 扰动观测与补偿，输出补偿项给控制核心 |
| 安全过滤 | `modules/Safety-Filter.md` | 控制输出后处理或参考轨迹过滤，优先级高于性能 |
| 故障分配 | `modules/Fault-Allocation.md` | WRENCH到电机/旋翼分配，处理执行器故障和饱和 |

每份规格模板必须固定包含：

```text
算法目标
PX4/MoSim控制链路位置
输入需求：p/v/a/jerk/snap、状态、模型参数、扰动估计或故障状态
输出层级：ATTITUDE_THRUST / BODY_RATE_THRUST / WRENCH / ROTOR
是否需要PX4内环
是否替换PX4某一环
是否需要控制分配
是否可由MWORKS生成C/C++
MWORKS建模状态
C/C++生成状态
Gazebo/Sunray验收状态
参数Profile
指标结果
已知问题
禁止声明
```

因此，当前建议提前建立以下文档：

```text
01_控制器平台/controllers/README.md
01_控制器平台/controllers/px4ctrl.md
01_控制器平台/controllers/PID.md
01_控制器平台/controllers/LQI.md
01_控制器平台/controllers/SE3.md
01_控制器平台/controllers/DFBC.md
01_控制器平台/controllers/SMC.md
01_控制器平台/controllers/LMPC.md
01_控制器平台/controllers/NMPC.md
01_控制器平台/modules/README.md
01_控制器平台/modules/INDI.md
01_控制器平台/modules/L1.md
01_控制器平台/modules/AWFF.md
01_控制器平台/modules/DOB-ESO.md
01_控制器平台/modules/Safety-Filter.md
01_控制器平台/modules/Fault-Allocation.md
```

这些文档可以先处于DESIGNED或BACKLOG状态，但必须把输入、输出层级、
MWORKS建模路线、Gazebo验收路线和禁止声明写清楚。

### 4.6 规划器与编队文档策略

规划和编队同样不应全部塞进一个长文档。`规划与编队控制接口.md`
负责公共接口、Topic、轨迹语义、命名空间和多机隔离；具体规划器和集群
算法使用独立规格文档。

建议先建立：

```text
02_感知规划集群/planners/README.md
02_感知规划集群/planners/EGO-Planner-v1.md
02_感知规划集群/planners/EGO-Planner-v2.md
02_感知规划集群/planners/Diff-Planner.md
02_感知规划集群/planners/EGO-Swarm.md
```

每个规划器文档必须固定包含：

```text
源码位置
上游版本/commit
输入：点云、里程计、目标点、地图
输出：bspline/trajectory/position_cmd
是否依赖FAST-LIO状态源
是否经过Trajectory Server统一求值
是否直接控制MAVROS：必须为否
单机或多机适用范围
Gazebo/RViz验收场景
已知问题和禁止声明
```

### 4.7 全量任务文档策略

本次文档重构不能只整理“当前正在做的东西”。后续明确要做的能力也必须
现在落到文档中，只是详细接口、参数、代码路径可以标记为 `TBD`，等进入
实现批次后补齐。

也就是说，设计文档至少要回答：

```text
我们最终要做哪些模块
每个模块为什么要做
它属于哪个系统能力块
依赖哪些前置门禁
做到什么程度才算完成
当前状态是BACKLOG、DESIGNED、IMPLEMENTED、MEASURED还是ACCEPTED
哪些细节允许TBD
```

推荐新增一个全量任务总表：

```text
00_架构与任务/任务总览.md
```

该文档不是执行日志，而是项目工作地图。它应覆盖以下全部任务族：

| 任务族 | 必须落文档的对象 |
| --- | --- |
| 运行基线 | Sunray ROS1、PX4/MAVROS、Gazebo Classic、RViz、模型装配、启动命令、频率 |
| 状态源与传感器 | PX4/MAVROS融合状态、Gazebo truth、MID360点云、Livox IMU、FAST-LIO、未来Point-LIO、定高替身、摄像头 |
| 基础飞行动作 | 起飞、悬停、降落、阶跃、8字、螺旋、圆形、目标点、异常中断 |
| 控制器族 | px4ctrl、PID、增强PID、SE3/SO3、DFBC、LMPC、NMPC、INDI、L1、LQI、SMC、AWFF、DOB/ESO、安全过滤、故障容错分配 |
| 轨迹接口 | Trajectory Server、p/v/a/jerk/snap、B-spline、minimum snap、时间同步、参考切换 |
| 规划器 | EGO-Planner-v1、EGO-Planner-v2、Diff-Planner、EGO-Swarm、SUPER/Fast-Planner等候选参考 |
| 多机与编队 | EGO-Swarm官方链路、2机/3机隔离、Leader-Follower、一致性、虚拟结构、编队CBF、任务分配、故障成员退出 |
| MWORKS与代码生成 | px4ctrl Golden Slice、PID/SE3/DFBC/NMPC模型、生成C/C++、SIL、IController包装、PX4 Adapter、PX4 Module候选 |
| 鲁棒与安全 | 风扰、拖曳、地效、负载变化、饱和、延迟补偿、failsafe、安全包络、故障注入 |
| 真机化 | Orin NX 16G、雷迅V6X、C++化、实时线程、日志、参数Profile、真机传感器替代关系 |
| 可视化与交付 | RViz点云/栅格/轨迹、Gazebo动画、UE真值地图、前端、摄像头窗口、报告、视频、提交包 |

每个对象至少应有一条任务卡：

```text
ID:
名称:
所属任务族:
目标:
当前状态:
前置依赖:
输入:
输出:
验收:
当前TBD:
禁止声明:
目标文档:
```

如果对象足够复杂或将要进入实现批次，则从任务卡升级为独立规格文档。

因此，文档策略应调整为：

```text
所有明确要做的东西都必须先进入任务总览。
核心控制器、核心规划器、核心集群能力提前建独立规格。
远期候选可以先是任务卡，但不能完全没有记录。
接口细节可以TBD，但任务存在性、依赖和验收不能TBD。
```

这也解释了控制器文档粒度：

```text
px4ctrl、PID、LQI、SE3、DFBC、SMC、LMPC、NMPC 必须提前独立成文档。
INDI、L1、AWFF、DOB/ESO、安全过滤、故障分配必须提前独立成文档。
这些文档可以先是BACKLOG/DESIGNED，但不能只停留在任务总览。
真正远期且尚未纳入路线图的候选算法，才允许先只做任务卡。
```

### 4.8 控制链路位置与实验平台联动策略

控制器文档不能只回答“这个算法叫什么、理论上多高级”。每个控制器、
增强模块和安全/故障模块都必须先放进完整 PX4/MoSim 大系统闭环中，
说明它作用于哪一环，以及最终实验界面如何选择、配置、注入扰动和验收。

推荐把完整闭环拆成以下可索引对象：

| 链路对象 | 作用 | 典型可选项 | 前端/实验平台暴露方式 |
| --- | --- | --- | --- |
| 场景/地图 | 决定障碍物、赛题环境和真值地图 | 空场、柱体、窄通道、多障碍、UE真值地图 | 地图下拉选择、场景重载按钮 |
| 状态源 | 给控制器提供状态反馈 | PX4/MAVROS融合状态、Gazebo truth评价、FAST-LIO经PX4融合、FAST-LIO直连对照 | 状态源Profile显示，实验锁定后不可随意切换 |
| 轨迹/任务发生器 | 给控制器提供参考 | 起飞/悬停/降落、阶跃、8字、螺旋、圆形、目标点、EGO轨迹 | 任务下拉、目标点输入、轨迹参数面板 |
| 外环控制器 | 位置/速度/加速度跟踪 | px4ctrl、PID、LQI、SE3、DFBC、LMPC、NMPC、SMC | 控制器选择器、参数Profile选择 |
| 增强/补偿模块 | 提高鲁棒性或跟踪精度 | INDI、L1、AWFF、DOB/ESO | 模块开关、增益/带宽参数、诊断曲线 |
| 安全过滤 | 约束参考或控制输出 | CBF、Reference Governor、Safety Filter | 安全开关、距离/速度/倾角约束滑块 |
| 执行器/故障模块 | 注入故障或处理分配 | 电机失效、推力衰减、控制分配重构、Fault-Allocation | 故障注入开关、故障比例滑块、故障时刻输入 |
| 扰动模块 | 注入环境扰动 | 风扰、阵风、地效、拖曳、负载变化 | 风速/方向/阵风滑块、扰动Profile选择 |
| Adapter/PX4接口 | 把控制输出送入飞控 | ATTITUDE_THRUST第一阶段，BODY_RATE/WRENCH后续 | 输出层级只读显示，禁止实验中混用 |
| 评价与展示 | 判断是否通过 | RMSE、Max、稳态窗口、轨迹偏差、清障距离、能耗、故障恢复时间 | 曲线、表格、RViz/Gazebo/UE/前端同步显示 |

因此，每个独立控制器或模块文档必须增加一节：

```text
系统链路位置:
  属于外环控制器 / 增强模块 / 安全过滤 / 故障分配 / 扰动注入 / Adapter。

接口层级:
  输入：状态、轨迹、模型参数、扰动估计、故障状态。
  输出：ATTITUDE_THRUST / BODY_RATE_THRUST / WRENCH / ROTOR / 补偿项 / 安全过滤后参考。

PX4关系:
  复用PX4姿态/角速度内环，还是替换其中一环。

前端实验入口:
  是否可被控制器选择器直接选择。
  是否暴露参数Profile。
  是否有滑块/开关用于扰动、故障或安全约束。

评价指标:
  对哪些任务有效：起飞悬停降落、8字、螺旋、阶跃、EGO、Swarm、故障/风扰。
  必须输出哪些曲线和指标。

禁止声明:
  未接入该链路位置前，不得声称完成该算法的系统闭环。
```

最终系统界面不只是“选择控制器”。它至少应覆盖：

```text
控制器选择：
  px4ctrl / PID / LQI / SE3 / DFBC / SMC / LMPC / NMPC

增强模块选择：
  INDI / L1 / AWFF / DOB-ESO，可单独开关或绑定到某些控制器Profile

安全与故障：
  Safety Filter开关，电机故障/推力衰减滑块，故障开始时间，恢复策略

环境扰动：
  风速、风向、阵风、负载变化、地效/拖曳Profile

地图和任务：
  地图选择，起飞/悬停/降落/8字/螺旋/阶跃/EGO/Swarm任务选择

显示窗口：
  RViz点云累计地图、栅格地图、飞机三轴/轨迹、Gazebo动画、
  多机摄像头第一视角、UE/前端状态面板

评价输出：
  每次实验生成统一Run ID、参数Profile、轨迹误差、稳态误差、
  安全距离、故障恢复、控制输出、报告图表和可回放证据
```

这意味着文档重构后的任务总览不能只按算法分类，还必须同时有一张
“实验平台对象矩阵”。每个对象都要映射到：

```text
目标文档
链路位置
前端控件
运行参数
验收指标
当前实现状态
```

## 5. 最终迁移表

本轮不再采用“阶段A/B/C试探式收缩”。迁移目标是直接形成唯一正式
`Docs/Design/架构/` 文档树，但执行时仍按“先建新树和README、再移动/改链、
最后归档候选”的顺序降低风险。

| 当前路径 | 目标路径 | 处理方式 |
| --- | --- | --- |
| `Docs/Design/README.md` | `Docs/Design/README.md` | 保留为根入口，更新为新树索引 |
| `Docs/Design/需求.md` | `Docs/Design/需求.md` | 保留为需求入口 |
| `Docs/Design/架构.md` | `Docs/Design/架构.md` | 保留为短系统架构入口，同时指向 `架构/00_架构与任务/` |
| `Docs/Design/赛题.md` | `Docs/Design/赛题.md` | 保留为赛题和答辩口径入口 |
| `Docs/Design/架构/架构.md` | `Docs/Design/架构/00_架构与任务/系统架构.md` | 合并或移动，去掉与根 `架构.md` 重复内容 |
| `Docs/Design/架构/MoSim研发工作流与Agent任务编排规范.md` | `Docs/Design/架构/00_架构与任务/任务路线图.md` | 保留S0-S12、Goal、验收矩阵，删除旧多线程/派发口径 |
| `Docs/Design/架构/MoSim系统集成接口与编排架构.md` | `Docs/Design/架构/00_架构与任务/系统集成接口与编排.md` | 保留Frame/Profile/Manifest/Orchestrator |
| `Docs/Design/架构/MoSim统一控制接口规范.md` | `Docs/Design/架构/01_控制器平台/统一控制接口.md` | 移动，作为控制接口权威 |
| `Docs/Design/架构/MoSim单机控制器实现规范.md` | `Docs/Design/架构/01_控制器平台/单机控制器实现.md` | 移动，保留px4ctrl/PID/SE3实现边界 |
| `Docs/Design/架构/MoSim控制器代码生成与PX4部署规范.md` | `Docs/Design/架构/01_控制器平台/代码生成与PX4部署.md` | 移动，吸收真机化代码形态约束 |
| `Docs/Design/架构/MoSim控制增强与容错规范.md` | `Docs/Design/架构/01_控制器平台/控制增强与容错.md` | 移动，作为增强/安全/故障模块权威 |
| `Docs/Design/架构/MoSim_FASTLIO定位闭环与规划复现基础方案.md` | `Docs/Design/架构/02_感知定位与规划集群/FASTLIO定位闭环.md` | 移动，保留状态源/真值实验组 |
| `Docs/Design/架构/MoSim规划与编队控制接口规范.md` | `Docs/Design/架构/02_感知定位与规划集群/规划与编队控制接口.md` | 移动，保留EGO/EGO-Swarm/formation边界 |
| `Docs/Design/架构/MoSim控制系统测试与评价规范.md` | `Docs/Design/架构/03_测试调参与证据/测试与评价.md` | 移动，作为指标和证据权威 |
| `Docs/Design/架构/MoSim控制器调参与参数优化规范.md` | `Docs/Design/架构/03_测试调参与证据/调参与参数优化.md` | 移动，与测试评价强互链 |
| `Docs/Design/架构/MoSim真机化收尾与C++化重构方案.md` | `Docs/Design/架构/03_测试调参与证据/真机化与C++化.md` | 先移动，后续可并入代码生成文档 |
| `Docs/Design/架构/MoSim控制体系总览.md` | `Docs/Design/架构/archive_index.md` 或拆分进入 `controllers/README.md`、`modules/README.md` | 降级，不再作为正式入口 |
| `Docs/Design/架构/MoSim控制器管理与配置规范.md` | `Docs/Design/架构/archive_index.md` 或抽取Profile字段进接口/编排文档 | 降级为未来Controller Manager参考 |
| `Docs/Design/架构/MoSim系统架构问题与决策矩阵.md` | `Docs/Design/架构/00_架构与任务/架构问题与决策追踪.md` | 保留为索引，不作为唯一执行规范 |
| `Docs/Design/架构/MoSim体系.md` | `Docs/Cache/design/superseded/MoSim体系.md` | 唯一内容抽取后归档 |
| `Docs/Design/旧架构/` | `Docs/Cache/design/old_architecture/` | 归档，不进入正式索引 |

算法卡片新建规则：

| 类别 | 目标目录 | 首批卡片 |
| --- | --- | --- |
| 名义控制器 | `Docs/Design/架构/01_控制器平台/controllers/` | px4ctrl、PID、LQI、LQR-LQG、SE3、DFBC、Backstepping、SMC、Fuzzy、Neural-Compensation、RL-Policy、LMPC、NMPC |
| 增强/安全/故障模块 | `Docs/Design/架构/01_控制器平台/modules/` | INDI、L1、AWFF、DOB-ESO、Safety-Filter、Fault-Allocation |
| 规划器和集群 | `Docs/Design/架构/02_感知定位与规划集群/planners/` | EGO-Planner-v1、EGO-Planner-v2、Diff-Planner、EGO-Swarm |

算法卡片只要求第一版说明链路位置、输入输出、接口层级、状态和验收入口；
不要求一次写成完整论文综述。

## 6. 执行顺序

### Step 1：建立新树骨架

创建：

```text
Docs/Design/架构/README.md
Docs/Design/架构/00_架构与任务/README.md
Docs/Design/架构/01_控制器平台/README.md
Docs/Design/架构/02_感知定位与规划集群/README.md
Docs/Design/架构/03_测试调参与证据/README.md
Docs/Design/架构/04_展示与实验平台/README.md
Docs/Design/架构/01_控制器平台/controllers/README.md
Docs/Design/架构/01_控制器平台/modules/README.md
Docs/Design/架构/02_感知定位与规划集群/planners/README.md
```

README必须先写清楚：

```text
本组负责什么；
本组不负责什么；
当前阶段先读哪个文档；
哪些文档是backlog或reference-only。
```

### Step 2：移动正式文档并更新互链

按迁移表移动正式文档。移动后立即更新：

```text
Docs/Design/README.md
Docs/Design/架构.md
Docs/Design/架构/README.md
各一级目录README
```

正式入口不得再指向旧路径作为执行源。

### Step 3：抽取并降级候选文档

候选文档不直接删除。先抽取唯一内容：

| 候选文档 | 抽取目标 |
| --- | --- |
| `MoSim控制体系总览.md` | 控制器族索引、代表性组合、开源参考实现索引 |
| `MoSim控制器管理与配置规范.md` | Profile字段、参数版本、Last Known Good规则 |
| `MoSim真机化收尾与C++化重构方案.md` | Python/C++分层、Orin NX/V6X约束、传感器真机假设 |
| `MoSim体系.md` | 正式文档尚未覆盖的历史术语或范围说明 |

抽取完成后，候选文档进入：

```text
Docs/Cache/design/superseded/
```

### Step 4：建立算法卡片

先建立最小卡片模板，不写长篇理论：

```text
Status:
Layer:
Replaces:
Inputs:
Outputs:
PX4 dependency:
MWORKS/codegen route:
Gazebo/Sunray validation:
Current gate:
References:
```

控制器、增强模块和规划器卡片必须能被 `rg` 通过算法名命中。

### Step 5：引用扫描与验收

每轮移动后运行：

```powershell
rg -n "MoSim体系\\.md|MoSim控制体系总览\\.md|MoSim控制器管理与配置规范\\.md|Docs/Design/旧架构|Docs/Design/架构/MoSim" Docs -g "*.md"
git diff --check -- Docs/Design Docs/Index Docs/Workflows
```

允许cache、迁移方案和历史归档中出现旧路径；不允许正式入口、Workflow、
Index继续把旧路径作为active source。

## 7. 重构后Agent索引规则

重构完成后，Agent处理设计或实现任务时必须按以下顺序：

```text
1. Docs/Design/README.md
2. Docs/Design/需求.md
3. Docs/Design/架构.md
4. Docs/Design/架构/README.md
5. Docs/Design/架构/00_架构与任务/任务路线图.md
6. 任务对应的一个一级目录README
7. 任务对应的一个专题规范或算法卡片
8. 必要时再读测试/评价或工作流附录
```

禁止：

```text
从MoSim体系.md开始；
从控制器百科章节开始；
从cache旧方案开始；
从旧架构目录开始；
从历史ROS2/PX4/x500路线开始；
为了完成任务临时切换主线。
```

## 8. 本方案的下一步

下一步可以直接执行文档重构，但执行必须分小步提交给用户审核：

```text
1. 建立新目录和README骨架；
2. 移动根架构、任务路线图、系统集成三类架构任务文档；
3. 移动控制器平台文档；
4. 移动感知定位、规划集群文档；
5. 移动测试调参和展示平台文档；
6. 建立首批controller/module/planner卡片；
7. 做引用扫描和diff检查；
8. 等用户确认后再归档或删除候选旧文档。
```

不建议在同一步里完成移动、合并、删除和内容重写。重构目标是让Agent索引
稳定，不是制造一次大范围不可审查的文档改动。
