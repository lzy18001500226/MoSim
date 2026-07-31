# MoSim: 四旋翼无人机自适应鲁棒位姿控制与智能仿真验证系统

MoSim 是面向 A8 四旋翼无人机位姿控制系统设计优化赛题的完整工程。项目以
MWORKS 为控制器建模、仿真和量化分析主线，并把生成代码或已冻结控制接口接入
PX4/Gazebo 验证链路。目标不是搭建通用机器人导航演示，而是可复现地回答：控制器
是否改善了四旋翼在典型轨迹、扰动、故障与多机任务中的位置精度、姿态稳定性和鲁棒性。

赛题原始要求、交付物和报告口径见
[`Docs/Design/赛题.md`](Docs/Design/赛题.md)。

## 赛题主线

1. 以官方 PID 为可追溯基线，设计并比较改进 PID、鲁棒控制、预测控制或受控复合方案。
2. 在 MWORKS.Sysblock / Sysplorer 中完成控制器与四旋翼系统模型集成，使用 Syslab 或等价脚本完成量化分析。
3. 覆盖阶跃、螺旋、8 字、参数摄动、风扰、执行器退化等场景；多机编队是单机闭环稳定后的扩展任务。
4. 交付完整源文件、用户手册、仿真分析报告和演示材料，所有结论必须能追溯到模型、配置、日志、指标或图件。

## 三层架构

README 以三个产品责任域组织项目；其中运行验证层内部的控制运行时、PX4/MAVROS、
plant 与 ROS 算法权威边界，仍以
[`Docs/Design/架构.md`](Docs/Design/架构.md) 为准。

```text
第一层：建模与控制器设计
MWORKS / Sysblock / Syslab
  -> 四旋翼模型、控制器、MIL/SIL、参数优化、代码生成、离线一致性与指标分析

第二层：部署与运行验证
Controller Core / Generated C or C++ / Adapter / PX4 / MAVROS / Gazebo / Sunray / ROS
  -> 命令语义、飞控接口、plant、执行器、传感器、真值、定位、规划和故障环境

第三层：展示、实验操作与审核
RViz / UE / QGC / Flight Console / Web / Results
  -> ExperimentProfile 选择、状态展示、点云与轨迹审核、录屏、报告和结果追溯
```

三层之间只通过明确的 frame、profile、manifest 和 adapter 连接。控制器核心不直接
依赖 ROS、MAVROS、Gazebo、UE 或 GUI；显示层不能回写控制状态或替代指标来源。
当前 P0 运行验证链路是：

```text
Ubuntu-20.04 / ROS1 Noetic
  -> Sunray150 + MID360 / Gazebo Classic
  -> PX4 + MAVROS + px4ctrl
  -> RViz 点云、轨迹、地图与坐标系审核
```

UE、QGC 和 Flight Console 属于第三层；它们改善操作、展示和视频证据，但不拥有
控制闭环、定位或规划成功的最终判定权。

## 正式模型架构

唯一活动 Modelica 根是
[`Models/MoSimQuadrotorModel/`](Models/MoSimQuadrotorModel/)。从
`package.mo` 加载，并在 `MoSimQuadrotorModel.*` 命名空间中创建新的模型、
Profile 和人工打开入口。

```text
MoSimQuadrotorModel/
  Parameters/               Sunray150 参数来源与识别边界
  Vehicle/                  机体、执行器、传感器、动力学与可视化装配
  Control/                  基线、接口、分配器、适配器和图形化控制器实现
  Experiment/               Runner、探针、正式测试壳、任务模板与鲁棒场景
  Guidance/                 参考轨迹、规划、障碍场与编队参考
  Deployment/               MWORKS Live 受控实时桥接入口
  Visualization/            场景留痕、诊断和展示模型
  Common/                   可复用的非业务通用模型
```

推荐的离线打开链路是：

```text
Model Studio / ExperimentProfile
  -> MoSimQuadrotorModel.Experiment.Runners.*
  -> typed Adapter
  -> MoSimQuadrotorModel.Control.*
  -> Experiment.* 或 Guidance.* 场景/参考
  -> Vehicle shared plant / result contract
```

`Models/` 下不保留控制器、实验或 Live 的第二个 Modelica 包根。自动恢复副本和
旧命名的历史证据只保留在 `Docs/Cache/`、`Results/` 中，均不得作为加载入口。
参数目录中的 SDF、Gazebo 或参考项目数值必须保留来源标签，在获得称重、台架、ULog
或有效系统辨识证据前不得写成真实机体参数。

更完整的控制责任、输出边界和兼容入口说明见
[`Docs/Design/架构/01_控制器平台/MWORKS控制器关系与组合架构.md`](Docs/Design/架构/01_控制器平台/MWORKS控制器关系与组合架构.md)。

## 启动入口

仓库根目录的 Windows 双击操作入口都集中在 [`cmd/`](cmd/)，根目录不再放置 `.cmd`
文件。`Scripts/`、技能和工具目录中的内部 wrapper 保持原位，不属于这个入口层。
入口按用途分组，完整清单见 [`cmd/README.md`](cmd/README.md)。

| 目的 | 入口 |
| --- | --- |
| Flight Console / QGC 操作界面 | [`cmd/启动MoSim地面站.cmd`](cmd/启动MoSim地面站.cmd) |
| 受管 Gazebo/PX4 运行时 | [`cmd/启动Gazebo飞行仿真.cmd`](cmd/启动Gazebo飞行仿真.cmd) |
| 停止当前受管仿真进程 | [`cmd/停止所有仿真.cmd`](cmd/停止所有仿真.cmd) |
| Sunray ROS1 基础链路自检 | [`cmd/01_启动Sunray基础自检.cmd`](cmd/01_启动Sunray基础自检.cmd) |
| Sunray Gazebo 可视化审核 | [`cmd/02_启动Sunray基础可视化审核.cmd`](cmd/02_启动Sunray基础可视化审核.cmd) |
| 只停止基础链路 | [`cmd/00_停止Sunray基础仿真.cmd`](cmd/00_停止Sunray基础仿真.cmd) |

基础自检只证明 Gazebo、PX4、MAVROS 与非空 MID360 点云可启动，且飞行器保持
地面、未解锁状态。它不是 FAST-LIO、控制器、规划器或编队任务的通过结论。

## 目录地图

| 路径 | 责任 |
| --- | --- |
| `Models/` | 项目拥有的 MWORKS/Sysplorer 模型；正式根为 `MoSimQuadrotorModel/`。 |
| `Config/` | 控制器、场景、ExperimentProfile、能力索引及机器可读协议。 |
| `Scripts/` | 运行编排、质量检查、结果提取、绘图与测试。 |
| `cmd/` | Windows 双击入口；只做启动和停止转发。 |
| `apps/` | Flight Console、Model Studio 和项目应用代码。 |
| `src/` | 可复用的项目编排代码；不能绕过 `Models/`、`Config/` 或运行时权威边界。 |
| `Docs/Skills/Mworks/mworks-mcp-operations/wrappers/` | Sysplorer MCP 兼容性启动包装器；配置与具体工具说明仍以 `Docs/Skills/` 和 API 索引为准。 |
| `build/` | 本地应用构建或候选目录；不是模型、配置或正式证据的唯一来源。 |
| `Tools/` | 外部工具与运行支持资产；不作为竞赛算法或模型实现入口。 |
| `image/` | 原始视觉资产；报告采用的图件必须仍能追溯到 `Results/` 或 `Docs/报告/`。 |
| `UE5/` | UE 显示、场景与桥接工程；属于展示/审核层，不替代运行时证据。 |
| `Results/` | 可追溯的日志、指标、图件、回放、数据包与审核资产。 |
| `Docs/Design/` | 赛题、架构、控制器、接口和证据设计。 |
| `Docs/Workflows/` | 正常工程操作、质量门和当前运行链路，不承担仓库说明或历史日志。 |
| `Docs/Index/` | 模型、文档、工作流和外部参考入口。 |
| `References/` | 上游案例、外部仓库和参考资料；不是项目正式实现根。 |
| `Docs/Cache/agent_legacy/coagent_root_20260727/` | 已退役的多线程 AgentOS 材料，仅供依赖审计与历史追溯。 |

`.agents/`、`.codex/`、`.tmp/`、`.tools/`、`.venv/` 和类似隐藏目录是本机工作
状态或工具缓存，不是项目阅读、运行或提交入口。

## 源码路径与运行入口对应表

`Config/project_paths.json` 是组件路径的机器可读权威源。表中的
`canonical_active` 表示注册表的活动路径已经指向 `src/`（并可被项目本地
预检发现）；它不等于已经通过运行时性能验收。`copied_pending_activation`
表示源码已经复制到 `src/`，但仍有至少一个当前入口解析到旧的
`References/` 或 vendor 路径。**源码复制完成不等于运行入口切换完成。**

### 项目本地活动路径

| 组件 | 源码路径 | 当前解析路径 | 状态 | 主要入口 |
| --- | --- | --- | --- | --- |
| Sunray Gazebo 仿真 | `src/simulation/gazebo/sunray` | `src/simulation/gazebo/sunray` | `canonical_active` | `Config/profiles/runtime_bindings.json#sunray_gazebo.launch`; `Scripts/sunray/check_sunray_ros1_runtime_preflight.sh` |
| Sunray Gazebo 插件 | `src/simulation/gazebo/plugins/sunray` | `src/simulation/gazebo/plugins/sunray` | `canonical_active` | `Scripts/sunray/check_sunray_ros1_runtime_preflight.sh`; `Scripts/sunray/prepare_local_ros1_runtime_overlay.sh` |
| Sunray MAVROS 控制 | `src/flight_stack/mavros/sunray_uav_control` | `src/flight_stack/mavros/sunray_uav_control` | `canonical_active` | `Config/profiles/runtime_bindings.json#mavros_command_adapter.launch`; `Scripts/sunray/sync_assembled_model_into_sunray_ros1.py` |
| Sunray 公共工具 | `src/common/utilities/ros1/sunray_common` | `src/common/utilities/ros1/sunray_common` | `canonical_active` | `Config/runtime/ros1_local_source_manifest.v1.json#foundation`; `Scripts/sunray/prepare_local_ros1_workspace.sh` |
| px4ctrl 运行适配器 | `src/control/runtime_adapters/px4ctrl` | `src/control/runtime_adapters/px4ctrl` | `canonical_active` | `Config/profiles/runtime_bindings.json#controller_host.launch`; `Scripts/sunray/run_px4ctrl_basic_gate.sh` |
| quadrotor 消息 | `src/integration/ros1_launch/quadrotor_msgs` | `src/integration/ros1_launch/quadrotor_msgs` | `canonical_active` | `Config/runtime/ros1_local_source_manifest.v1.json#controller` |
| UAV 公共工具 | `src/common/utilities/ros1/uav_utils` | `src/common/utilities/ros1/uav_utils` | `canonical_active` | `src/control/runtime_adapters/px4ctrl` |
| CMake 公共工具 | `src/common/utilities/ros1/cmake_utils` | `src/common/utilities/ros1/cmake_utils` | `canonical_active` | `Config/runtime/ros1_local_source_manifest.v1.json#controller` |
| FAST-LIO | `src/perception/fast_lio` | `src/perception/fast_lio` | `canonical_active` | `Config/profiles/runtime_bindings.json#fastlio_review_or_ekf_bridge.launch`; `Scripts/sunray/run_px4ctrl_fastlio_hover_gate.sh` |
| Livox 兼容驱动 | `src/perception/livox_ros_driver_compat` | `src/perception/livox_ros_driver_compat` | `canonical_active` | `Config/runtime/ros1_local_source_manifest.v1.json#foundation` |
| MoSim QGC 扩展 | `src/ground_station/qgc/mosim_extension` | `src/ground_station/qgc/mosim_extension` | `canonical_active` | `Scripts/ui/materialize_qgc_custom_overlay.py`; `Scripts/ui/build_flight_console.ps1` |

### 已复制但仍待切换的入口

| 组件 | 源码路径 | 当前解析路径 | 状态 | 主要入口 |
| --- | --- | --- | --- | --- |
| Sunray 规划工具 | `src/integration/ros1_launch/sunray_planner_utils` | `References/Sunray/General_Module/sunray_planner_utils` | `copied_pending_activation` | `Config/profiles/runtime_bindings.json#planner_adapter.launch` |
| Sunray 任务适配器 | `src/planning/mission_adapters/sunray_tutorial` | `References/Sunray/General_Module/sunray_tutorial` | `copied_pending_activation` | `Scripts/sunray/run_sunray_ros1_default_stack_gate.sh`; `Scripts/sunray/run_sunray_ros1_native_mission_gate.sh` |
| FUEL | `src/planning/fuel` | `References/Lab/exploration_coverage/FUEL` | `copied_pending_activation` | `Scripts/sunray/check_fuel_ros1_preflight.sh`; `Scripts/sunray/fuel_single_px4ctrl_goal4.launch` |
| FALCON | `src/planning/falcon` | `References/Lab/exploration_coverage/FALCON-ros1-noetic` | `copied_pending_activation` | `Scripts/sunray/check_falcon_ros1_preflight.sh`; `Scripts/sunray/build_falcon_f1_minimal_build_probe.sh` |
| RACER | `src/planning/racer` | `References/Lab/exploration_coverage/RACER` | `copied_pending_activation` | `References/Lab/exploration_coverage/RACER/swarm_exploration/exploration_manager/launch/*.launch` |
| Diff-Planner | `src/planning/diff_planner` | `References/Lab/planning_local/Diff-Planner` | `copied_pending_activation` | `Scripts/sunray/setup_goal4_diff_planner_overlay.sh`; `Scripts/sunray/diff_*_px4ctrl_*.launch` |
| Ego-Planner Swarm | `src/planning/ego_planner_swarm` | `References/Sunray/External_Module/ego-planner-swarm` | `copied_pending_activation` | `Scripts/sunray/setup_goal4_ego_overlay.sh`; `Scripts/sunray/run_px4ctrl_ego_*_gate.sh` |
| 固定编队 | `src/planning/fixed_formation` | `References/Lab/swarm_coordination/Swarm-Formation` | `copied_pending_activation` | `Scripts/sunray/build_swarm_formation_ros1_upstream_smoke.sh`; `Scripts/sunray/swarm_formation_swarm_px4ctrl_d3.launch` |

### 外部 vendor / 展示例外

| 组件 | 项目源码路径 | 当前入口 | 状态 | 说明 |
| --- | --- | --- | --- | --- |
| QGroundControl 主体 | `src/ground_station/qgc/qgroundcontrol` | `apps/flight_console/vendor/qgroundcontrol` | `copied_pending_activation` | 构建入口仍由 `apps/flight_console/mosim/custom/CMakeLists.txt` 管理；不归入 MWORKS 控制器证据。 |
| UE / 外部展示资产 | `UE5/` 与经审计的 `References/` 资产 | 按 UE 工程清单解析 | 交付例外 | 仅保留实际被 UE 工程/场景清单引用的资产；不能把 Reference 资产当作项目控制源码。 |

表中 `References/` 路径不是都可以直接删除：当前配置、规划入口和部分
运行脚本仍有明确引用。`UPSTREAM.md`、`PATCHES.md` 等仅用于来源追溯的文字
引用不构成运行依赖。清理时按“活动入口、证据路径、来源追溯”三类分别判断，
不得按目录名或文件日期整体删除。

交付时，项目源码包包含 `Models/`、`Config/`、`Scripts/`、`apps/`、`src/`
和必要文档；`Results/` 作为单独筛选的证据集合；用户在完成最终审核后自行
压缩。归档到 `MoSim_Archive/` 的历史/缓存内容不作为默认运行输入。

## 阅读与操作

建议按以下顺序进入项目：

1. [`Docs/README.md`](Docs/README.md)：文档职责和按角色的阅读路径。
2. [`Docs/Design/赛题.md`](Docs/Design/赛题.md)：比赛目标、评分和交付边界。
3. [`Docs/Design/架构.md`](Docs/Design/架构.md)：软件与证据权威边界。
4. [`Docs/Index/simulation_model_structure_index.md`](Docs/Index/simulation_model_structure_index.md)：模型、场景、runner 和结果的对应关系。
5. [`Docs/Workflows/mainline_operations_board.md`](Docs/Workflows/mainline_operations_board.md)：当前工程选择与下一项门。
6. [`Docs/Workflows/sunray_ros1_current_runtime_lane.md`](Docs/Workflows/sunray_ros1_current_runtime_lane.md) 和 [`Docs/Workflows/sunray_ros1_execution_checklist.md`](Docs/Workflows/sunray_ros1_execution_checklist.md)：ROS1/Sunray/Gazebo/PX4/RViz 运行约束。

## 实验与归档边界

当前目录布局和模型/源码入口保持稳定，不执行大范围重构。经过依赖审计、哈希归档
和原路径留痕后，可以把明确无活动依赖的 `Results/` 或 `Config/` 子树移入
`MoSim_Archive/`；这不等于允许移动模型根、当前运行时配置、UI/UE 资产或活动证据。
`References/` 也不能按“已复制”整体删除，必须以本节路径表和实际消费者为准。

旧实验、兼容配置和历史结果的归档必须保留归档清单、SHA-256 和原路径说明。归档
只改变默认交付包的内容，不改变已声明的模型、控制器和证据结论。

### 当前归档收敛记录（2026-08-01）

- 已将 5 个无活动引用的旧 Codex/coagent GUI 与线程维护诊断目录归档到
  `C:\Users\HP\Desktop\MoSim_Archive\20260801_unreferenced_codex_gui_phase3\`。
  共 8 个文件、847,079 字节，归档清单 SHA-256 为
  `ced1cd97ba438fcb2b2d8493a7ec545436d0eb7029e4c562532645a09c8a1c81`；原路径保留
  `ARCHIVED_EXTERNALLY.md` 留痕。
- `Config/` 本批次不移动。对 16 个顶层配置目录的引用扫描均发现仓库内消费者；
  尤其 `control_platform`、`profiles`、`runtime`、`scenarios/system`、
  `legacy` 和 `protocol` 不能按目录名整体归档。
- `Results/agent_packets`、`Results/agent_runtime`、`Results/control_platform`、
  `Results/official`、`Results/robustness`、运行时/UI 目录和当前报告证据均保留。
  这些目录要么有活动消费者，要么属于证据/另一条运行责任线。

## 交付物

最终竞赛包至少应包含完整模型和依赖、配置、脚本、可复现结果、用户手册、仿真分析
报告以及演示视频。提交前按
[`Docs/Workflows/pre_submit_check.md`](Docs/Workflows/pre_submit_check.md) 逐项检查；
报告写作源、图件和导出要求位于 `Docs/报告/`。
