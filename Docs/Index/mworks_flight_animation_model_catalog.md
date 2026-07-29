# MWORKS / Sysplorer 四旋翼飞行动画模型目录

> 用途：给人工审看四旋翼飞行三维动画使用。这里的“飞行视频”指
> Sysplorer 结果查看器中的可播放三维动画；它不是现成的 MP4 文件。需要
> MP4 时，在动画窗口人工播放后再录屏。
>
> 本目录只列**完整飞行入口**：它们有完整机体、执行器、传感器，以及轨迹或
> 闭环控制链。结构图、控制器块、共享机体组件、hover smoke 和 UE 场景追踪
> smoke 都不算“给用户看的飞行场景”。本轮没有启动 MWORKS；“历史日志存在”
> 仅说明仓库留有以往 Sysplorer 记录，不等于今天已重新验证，也不构成控制器
> 性能结论。

## 1. 先加载什么，实际运行什么

### 1.1 现行源树：一个正式加载根

当前源树只需加载一个 package：

`C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\package.mo`

其中 `MoSimQuadrotorModel.Vehicle` 已包含官方四旋翼基线的模型、图标和 STL
资源。审查时不再加载外部官方包、单个 `.mo` 文件或任何旧包作为第二个库根。
当前只有这一棵项目模型树可作为审查或复现入口。

加载后，在 Sysplorer 的库树中选择本目录给出的**完整模型类名**，而不是双击
下方列出的控制器、`QuadChassis`、`OpenBlocksLinearMPCVehicle` 或结构图文件。

### 人工运行步骤

1. 打开上述项目 `package.mo`，确认库树中出现 `MoSimQuadrotorModel`，并可展开
   `Vehicle`。
2. 在库树中按本目录的类名找到一个**完整模型**，例如
   `MoSimQuadrotorModel.Experiment.Templates.Official.Example3AWFF`。
3. 对该模型执行 **Check Model**。失败时停在错误信息，不要用其它模型或旧结果
   顶替。
4. Check Model 通过后执行 **Simulate**。模型源码中的 `experiment(...)` 已设置
   仿真时长；首次可优先用表中较短的 50 s 场景。
5. 仿真完成后，在当前结果中打开 `Result.msr` 的结果查看器，并创建/打开三维
   动画窗口；动画窗口打开后由人工点击播放。只有无人机在三维窗口中真实运动，
   才算“看到了飞行画面”。模型结构图、单独曲线、桨叶静止图都不算。
6. 若要保存视频，保持当前动画窗口为前台并用本机录屏。不要把旧 `Result.msr`
   或旧动画窗口误当作刚运行模型的结果。

正常 GUI 路径会产生原生 `Result.msr`。项目脚本生成的外部结果路径不一定能被
结果查看器绑定；人工审看时优先使用当前 Sysplorer 会话生成的原生结果。相关
说明见 `C:\Users\HP\Desktop\MoSim\Docs\user_manual.md`。

## 2. 先看这几个

下表按“最容易看到有意义飞行画面”的顺序给出首次审核建议。`历史日志`是可追溯
的旧记录位置，便于发现库加载或模型版本不一致；不是本轮重新运行证明。

| 建议 | 完整模型类名 | 任务 / 场景 | 控制器 | 默认仿真时长 | 历史日志 |
|---|---|---|---|---:|---|
| 1 | `MoSimQuadrotorModel.Experiment.Templates.Official.Example3AWFFSysblockClosedLoop` | 单机 8 字轨迹，空白多体场景 | AWFF Sysblock | 120 s | `Results\official\example3_figure8\official_example3_awff_sysblock\logs\sysplorer_example3_awff_sysblock_full_20260510.jsonl` |
| 2 | `MoSimQuadrotorModel.Experiment.Templates.Official.Example2HelixTunedAWFFSysblockClosedLoop` | 单机螺旋爬升，空白多体场景 | 螺旋调参 AWFF | 50 s | `Results\official\example2_helix\official_example2_awff_sysblock_helix_tuned\logs\sysplorer_example2_awff_sysblock_helix_tuned_full_20260511.jsonl` |
| 3 | `MoSimQuadrotorModel.Experiment.Templates.Official.Example1HelicalFigure8TrailSysblockClosedLoop` | 起飞后螺旋 8 字，带原生轨迹留痕审看 | LinearMPC 风格外环 | 120 s | `Results\official\example1_helical_figure8\official_example1_helical_figure8_trail_sysblock\logs\sysplorer_example1_helical_figure8_trail_sysblock_full_20260514.jsonl` |
| 4 | `MoSimQuadrotorModel.Guidance.Planning.OpenBlocksLinearMPCVehicle` | 单机 OpenBlocks 静态障碍场 | LinearMPC 风格外环，规划参考 | 80.1247 s | `Results\planning\single_obstacle_astar_awff\sunray150_planning_open_blocks_linear_mpc_sysblock\logs\sysplorer_sunray150_planning_open_blocks_linear_mpc_sysblock_20260515.jsonl` |
| 5 | `MoSimQuadrotorModel.Guidance.Planning.Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop` | 单机走廊门控障碍场 | LinearMPC 风格外环，规划参考 | 23 s | `Results\planning\corridor_gate_astar_awff\sunray150_planning_corridor_gate_linear_mpc_sysblock\logs\sysplorer_sunray150_planning_corridor_gate_linear_mpc_sysblock_20260515.jsonl` |
| 6 | `MoSimQuadrotorModel.Guidance.Formation.TriangleFigure8LinearMPC` | 三机三角编队 8 字 | 三套 LinearMPC 风格 Sysblock | 80 s | `Results\formation\triangle_figure8\formation_triangle_figure8_linear_mpc_sysblock\logs\sysplorer_formation_triangle_figure8_linear_mpc_sysblock_20260515.jsonl` |
| 7 | `MoSimQuadrotorModel.Guidance.Planning.ThreeUavOpenBlocksReconfigurableFormationLinearMPC` | 三机 OpenBlocks 可重构编队 | 三套 LinearMPC 风格外环，规划参考 | 304.8405 s | 本目录只确认该完整源码入口；长仿真先人工 Check Model |

## 3. 完整飞行入口总表

### 3.1 嵌入官方原始基线：3 个

源码均在：
`C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\Plant\package.mo`

| 类名 | 任务 | 控制器 | 场景 | 时长 | 说明 |
|---|---|---|---|---:|---|
| `MoSimQuadrotorModel.Vehicle.Examples.Example1` | 阶梯爬升 | `Blocks.Controller.Controller` 六自由度 PID | 空白多体场景 | 50 s | 嵌入官方基线；这是唯一正式入口。 |
| `MoSimQuadrotorModel.Vehicle.Examples.Example2` | 螺旋爬升 | 同一六自由度 PID | 空白多体场景 | 50 s | 嵌入官方基线；这是唯一正式入口。 |
| `MoSimQuadrotorModel.Vehicle.Examples.Example3` | 8 字运动 | 同一六自由度 PID | 空白多体场景 | 120 s | 嵌入官方基线；这是唯一正式入口。 |

这三个是最朴素的参考动画：没有障碍物或城市地图，但能看到整机真实多体运动。

### 3.2 项目控制器基线：11 个

源码包：
`C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\Control\LegacyExamples\PidVariants\package.mo`

这些是单机空白多体场景；按名称即可判断任务和控制器。它们是完整模型别名，不要
点开 `AntiWindupFeedforwardCore`，后者只是控制器核心。

| 任务 | 可在库树直接选择的完整模型 | 控制器 | 历史任务族证据 |
|---|---|---|---|
| 阶梯爬升 | `Example1AWFFBaseline`、`Example1ImprovedPIDBaseline`、`Example1EnhancedPIDBaseline` | AWFF / 改进 PID / 增强 PID | `Results\official\example1_step\` |
| 螺旋爬升 | `Example2AWFFBaseline`、`Example2HelixTunedAWFFBaseline`、`Example2ImprovedPIDBaseline`、`Example2EnhancedPIDBaseline`、`Example2HelixTunedEnhancedPIDBaseline` | AWFF、螺旋调参 AWFF、改进 PID、增强 PID | `Results\official\example2_helix\` |
| 8 字轨迹 | `Example3AWFFBaseline`、`Example3ImprovedPIDBaseline`、`Example3EnhancedPIDBaseline` | AWFF / 改进 PID / 增强 PID | `Results\official\example3_figure8\` |

完整类名前缀为 `MoSimQuadrotorModel.Control.LegacyExamples.PidVariants.`。例如第一行的完整类名是
`MoSimQuadrotorModel.Control.LegacyExamples.PidVariants.Example1AWFFBaseline`。

### 3.3 正式单机任务模型：15 个

源码包：
`C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\Experiment\Templates\Official\package.mo`

| 任务 | 可在库树直接选择的完整模型 | 控制器 | 场景 / 时长 | 历史任务族证据 |
|---|---|---|---|---|
| 阶梯爬升 | `Example1AWFF`、`Example1INDI`、`Example1L1`、`Example1LinearMPC` | AWFF / INDI-L1 组合 / L1 残差 / LinearMPC 风格 | 空白多体场景，50 s（AWFF 原始包的短烟测为 1 s） | `Results\official\example1_step\` |
| 平面 8 字留痕 | `Example1PlanarFigure8Trail` | LinearMPC 风格外环 | 空白多体场景，120 s | `Results\official\example1_planar_figure8\official_example1_planar_figure8_trail_sysblock\logs\sysplorer_example1_planar_figure8_trail_sysblock_full_20260514.jsonl` |
| 螺旋 8 字留痕 | `Example1HelicalFigure8Trail` | LinearMPC 风格外环 | 空白多体场景，120 s | `Results\official\example1_helical_figure8\official_example1_helical_figure8_trail_sysblock\logs\sysplorer_example1_helical_figure8_trail_sysblock_full_20260514.jsonl` |
| 螺旋爬升 | `Example2AWFF`、`Example2HelixTunedAWFF`、`Example2INDI`、`Example2HelixTunedINDI`、`Example2LinearMPC` | AWFF / 调参 AWFF / INDI-L1 组合 / 调参 INDI-L1 / LinearMPC 风格 | 空白多体场景，50 s | `Results\official\example2_helix\` |
| 8 字轨迹 | `Example3AWFF`、`Example3INDI`、`Example3L1`、`Example3LinearMPC` | AWFF / INDI-L1 组合 / L1 残差 / LinearMPC 风格 | 空白多体场景，120 s | `Results\official\example3_figure8\` |

完整类名前缀为 `MoSimQuadrotorModel.Experiment.Templates.Official.`。这 15 个才是普通“阶跃、
螺旋、8 字”任务应优先打开的项目模型，不需要加载任何障碍场。

### 3.4 单机避障与多机场景：6 个

源码包：
`C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\Guidance\Planning\package.mo`

| 完整模型类名 | 场景 | 控制器 / 参考 | 时长 | 状态 |
|---|---|---|---:|---|
| `MoSimQuadrotorModel.Guidance.Planning.OpenBlocksAWFF` | OpenBlocks 静态障碍场 | AWFF，规划参考 | 16 s | 历史 Sysplorer 日志：`Results\planning\single_obstacle_astar_awff\sunray150_planning_open_blocks_awff_sysblock\logs\sysplorer_sunray150_planning_open_blocks_awff_sysblock_20260515.jsonl` |
| `MoSimQuadrotorModel.Guidance.Planning.OpenBlocksLinearMPC` | OpenBlocks 静态障碍场 | LinearMPC 风格外环，规划参考 | 80.1247 s | 历史 Sysplorer 日志：`Results\planning\single_obstacle_astar_awff\sunray150_planning_open_blocks_linear_mpc_sysblock\logs\sysplorer_sunray150_planning_open_blocks_linear_mpc_sysblock_20260515.jsonl` |
| `MoSimQuadrotorModel.Guidance.Planning.CorridorGateAWFF` | 走廊门控障碍场 | AWFF，规划参考 | 23 s | 完整源码入口；本目录未把它标为本轮已运行。 |
| `MoSimQuadrotorModel.Guidance.Planning.CorridorGateLinearMPC` | 走廊门控障碍场 | LinearMPC 风格外环，规划参考 | 23 s | 历史 Sysplorer 日志：`Results\planning\corridor_gate_astar_awff\sunray150_planning_corridor_gate_linear_mpc_sysblock\logs\sysplorer_sunray150_planning_corridor_gate_linear_mpc_sysblock_20260515.jsonl` |
| `MoSimQuadrotorModel.Guidance.Formation.TriangleFigure8LinearMPC` | 三机三角编队 8 字 | 三套 LinearMPC 风格 Sysblock | 80 s | 历史 Sysplorer 日志：`Results\formation\triangle_figure8\formation_triangle_figure8_linear_mpc_sysblock\logs\sysplorer_formation_triangle_figure8_linear_mpc_sysblock_20260515.jsonl` |
| `MoSimQuadrotorModel.Guidance.Planning.OpenBlocksThreeUavFormation` | 三机 OpenBlocks 可重构编队 | 三套 LinearMPC 风格外环，规划参考 | 304.8405 s | 完整源码入口；长仿真，先 Check Model，未在本轮重跑。 |

`OpenBlocksLinearMPCVehicle` 是给三机场景复用的**带输入端口整机组件**，不是可直接
选择的独立任务；不要把它当作第七个场景运行。

### 3.5 扰动、安全与故障动画入口：49 个

这些均是阶梯爬升任务的扰动/故障变体，仍有完整飞行器，但主要用于对比控制器。
源码级完整入口已经列全；除表中特别指出的历史路径外，先把它们当作“需要自己
Check Model 后再看的候选”，不要把名字或静态源码当成当前运行通过。

#### 一般扰动与安全：10 个

源码包：
`C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\Experiment\Scenarios\Robustness\package.mo`

| 扰动 / 任务 | 完整模型类名后缀 | 控制器 |
|---|---|---|
| 质量 +20% | `Mass20AWFFBaseline`、`Mass20AWFF`、`Mass20L1`、`Mass20LinearMPC` | AWFF 基线 / AWFF / L1 / LinearMPC 风格 |
| 横向阵风 | `WindGustAWFFBaseline`、`WindGustAWFF`、`WindGustL1`、`WindGustLinearMPC` | AWFF 基线 / AWFF / L1 / LinearMPC 风格 |
| 安全滤波、返航降落 | `SafetyQPNMPC`、`SafetyReturnLand` | QP/NMPC 风格安全控制；后者有返航和降落参考 |

完整类名前缀为 `MoSimQuadrotorModel.Experiment.Scenarios.Robustness.`。安全返航任务族留有历史
日志，例如：
`Results\official\example1_step\official_example1_qp_nmpc_safety_return_land_sysblock\logs\sysplorer_example1_qp_nmpc_safety_return_land_sysblock_full_20260514.jsonl`。

#### PID 对比基线：12 个

源码包：
`C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\Experiment\Scenarios\Robustness\PIDBaselines\package.mo`

完整类名前缀为 `MoSimQuadrotorModel.Experiment.Scenarios.Robustness.PIDBaselines.`：

```text
Mass20PID
Mass20ImprovedPID
Mass20EnhancedPID
WindGustPID
WindGustImprovedPID
WindGustEnhancedPID
Rotor1LossPID
Rotor1LossImprovedPID
Rotor1LossEnhancedPID
Rotor2LossPID
Rotor3LossPID
Rotor4LossPID
```

任务分别为质量 +20%、横向阵风和第 1 至第 4 号旋翼 15% 效率损失；控制器由类名的
`PID`、`ImprovedPID`、`EnhancedPID` 表示。

#### 旋翼损失 / 故障分配：27 个

源码包：
`C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\Experiment\Scenarios\Robustness\RotorLoss\package.mo`

完整类名前缀为 `MoSimQuadrotorModel.Experiment.Scenarios.Robustness.RotorLoss.`：

```text
Rotor1AWFF
Rotor1AWFFBaseline
Rotor1L1
Rotor1L1FaultAllocation
Rotor1L1OnlineFaultAllocation
Rotor1L1MultiFaultIsolation
Rotor1LinearMPC
Rotor1LinearMPCOnlineFaultAllocation
Rotor1WindGustAWFF
Rotor1WindGustAWFFFaultCompensation
Rotor1WindGustL1MultiFaultIsolation
Rotor1WindGustLinearMPCOnlineFaultAllocation

Rotor2AWFF
Rotor2L1MultiFaultIsolation
Rotor2WindGustAWFF
Rotor2WindGustL1MultiFaultIsolation
Rotor2WindGustLinearMPCOnlineFaultAllocation

Rotor3AWFF
Rotor3L1MultiFaultIsolation
Rotor3WindGustAWFF
Rotor3WindGustL1MultiFaultIsolation
Rotor3WindGustLinearMPCOnlineFaultAllocation

Rotor4AWFF
Rotor4L1MultiFaultIsolation
Rotor4WindGustAWFF
Rotor4WindGustL1MultiFaultIsolation
Rotor4WindGustLinearMPCOnlineFaultAllocation
```

含义：`RotorN` 是第 N 个旋翼 15% 效率损失；`WindGust` 叠加横向阵风；
`FaultAllocation` / `OnlineFaultAllocation` / `MultiFaultIsolation` 是故障分配或
隔离控制链。它们是完整飞行候选，不是“旋翼部件测试”。

## 4. 不应当作飞行视频入口的文件

| 路径 / 类别 | 为什么不该作为首选 |
|---|---|
| `C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\Experiment\Templates\Architecture\Sunray150CompleteSystemGraphical_Sysblock.mo` | 完整系统**结构图**，不是普通可播放飞行入口；当前应只从正式根加载。 |
| `C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\Vehicle\Sunray150Assembly.mo` | 共享机体组件，有外部旋翼命令输入，不是自带任务的闭环场景。 |
| `C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\Guidance\Planning\OpenBlocksLinearMPCVehicle.mo` | 多机规划场景的复用整机，有外部参考输入，不是独立实验。 |
| `Models\MoSimQuadrotorModel\Visualization\Diagnostics\FactoryTraceIso*.mo` | 接线/姿态/hover smoke，目的是诊断，不是给用户审看的飞行动画。 |
| `Models\MoSimQuadrotorModel\Visualization\Scenarios\*Smoke.mo` | UE 场景追踪 smoke；它们不能替代本目录的离线 MWORKS 飞行动画，也不该用于控制器或规划结论。 |
| `HoverSmoke`、`WrapperHoverSmoke`、`PhysicalWrenchHoverSmoke` | 动力学冒烟测试，不是“悬停飞行视频”。 |
| 控制器核心、`QuadChassis`、`Controller`、`QuinticReference`、`OpenBlocksColorMapReview`、`NavigationDisplay` | 组件、参考轨迹、地图审查或显示支撑，不包含完整可审看的飞行任务。 |

## 5. 选择建议

1. 只想先确认三维动画链路：选 `MoSimQuadrotorModel.Vehicle.Examples.Example3` 或
   `MoSimQuadrotorModel.Experiment.Templates.Official.Example3AWFF`。
2. 想看更有“飞行视频”感的单机画面：选 `Example1HelicalFigure8Trail` 或
   `Example2HelixTunedAWFF`。
3. 想看障碍环境：先选 `OpenBlocksLinearMPC`，再选 `CorridorGateLinearMPC`。
4. 想看多机：先选 `TriangleFigure8LinearMPC`；确认单机和三机基础动画均正常后，
   再运行 304.8405 s 的 `OpenBlocksThreeUavFormation`。
5. 想看抗扰或故障恢复画面：从 `WindGustAWFF`、`Mass20AWFF` 或 `Rotor1AWFF` 开始，
   每次只跑一个，先 Check Model。

本目录不声称任何模型当前已经通过实时、闭环、规划器或控制器性能验收；它只解决
“应该打开哪个完整模型、会看到什么飞行动画、以及正确的加载/播放顺序”。
