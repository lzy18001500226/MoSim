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

## 下载后快速入口

GitHub 克隆和百度网盘源码包应得到相同的项目根目录。`MOSIM_ROOT` 必须指向
同时包含 `AGENTS.md`、`Models/` 和 `Config/` 的 `MoSim` 目录；不要把它指向
外层下载目录，也不要把项目解压成 `MoSim/MoSim/` 后误设根目录。

```powershell
$MOSIM_ROOT = (Resolve-Path '<包含 AGENTS.md、Models 和 Config 的 MoSim 目录>').Path
$env:MOSIM_ROOT = $MOSIM_ROOT
Test-Path "$MOSIM_ROOT\Models\MoSimQuadrotorModel\package.mo"
```

优先复现 APP 和 MWORKS 仿真时，按以下顺序操作：

1. 在已授权的 MWORKS Syslab 中加载 `Models/MoSimQuadrotorModel/package.mo`；
2. 在同一 Syslab 会话执行 `apps/model_studio/src/app.jl` 的 `include(...)` 入口；
3. 在 Studio 选择任务和控制器，点击“写入配置”，再点击“打开仿真模型”；
4. 在 MWORKS 原生窗口确认 FormalRunner、执行 CheckModel，再由用户手动启动仿真；
5. 在结果查看器读取 `Result.msr`，并用同次运行目录的指标和运行记录判定结果。

APP 不是普通 Julia 命令行程序，不要用 `julia src/app.jl` 代替 Syslab 入口。`Results/`
被源码仓库忽略，首次写入配置时会自动生成交接 JSON 和临时 harness；历史 Results
证据包是独立交付物，不是 APP 启动依赖。Gazebo、ROS、PX4 和 QGC 属于可选的运行时
扩展，不是 APP 或 MWORKS 单机仿真的前置条件。

依赖分层：基础 APP、写入配置、通过原生 `ModelingPy` 打开模型，以及用户在 MWORKS
窗口中执行 CheckModel/仿真，不要求安装 Sysplorer MCP wrapper。APP 中的自动“运行
MWORKS MIL”/批量回归和部分自动化证据脚本才使用 Sysplorer MCP；没有 wrapper 时这些
自动操作会明确返回阻断，不能当作控制器失败，也不会自动替代手动 MWORKS 流程。
MoSim 助手的本机 Codex 服务和 Gazebo/ROS/PX4 运行时同样是可选组件。

代码导航：

| 需要查找 | 首选路径 |
| --- | --- |
| 正式 Modelica 包根 | `Models/MoSimQuadrotorModel/package.mo` |
| 机体、动力学和装配 | `Models/MoSimQuadrotorModel/Vehicle/` |
| 控制器接口、Adapter 和实现 | `Models/MoSimQuadrotorModel/Control/` |
| 单机 FormalRunner | `Models/MoSimQuadrotorModel/Experiment/Runners/Formal/` |
| 三机/编队 Runner | `Models/MoSimQuadrotorModel/Experiment/Runners/Formation/` |
| 轨迹、障碍场和编队参考 | `Models/MoSimQuadrotorModel/Guidance/` |
| Studio 当前源码 | `apps/model_studio/src/app.jl` |
| Studio 路由权威表 | `Config/control_platform/model_studio_task_routes_v1.toml` |
| 写入配置/打开模型脚本 | `Scripts/ui/model_studio_task_config.py`、`Scripts/ui/open_model_studio_model.py` |

完整操作步骤见 [`apps/model_studio/README.md`](apps/model_studio/README.md) 和
[`Docs/报告/用户手册_正文骨架.md`](Docs/报告/用户手册_正文骨架.md)。
模型包的命名空间、入口类、子包职责和浏览器可见性见
[`Models/README.md`](Models/README.md)。

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
RViz / UE / QGC / MoSim Ground Control / Web / Results
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

UE、QGC 和 MoSim Ground Control 属于第三层；它们改善操作、展示和视频证据，但不拥有
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

Windows 双击操作入口都集中在 [`Scripts/cmd/`](Scripts/cmd/)，仓库根目录不再放置
`.cmd` 文件。该目录只保留已确认的 C99 单机复现入口、地面站启动和受管停止；完整清单
见 [`Scripts/cmd/README.md`](Scripts/cmd/README.md)。

| 目的 | 入口 |
| --- | --- |
| C99 本地环境准备 | [`Scripts/cmd/00_准备C99单机环境.cmd`](Scripts/cmd/00_准备C99单机环境.cmd) |
| C99 名义起飞-悬停-降落 | [`Scripts/cmd/01_运行C99单机起飞悬停降落.cmd`](Scripts/cmd/01_运行C99单机起飞悬停降落.cmd) |
| C99 风扰与电机故障恢复 | [`Scripts/cmd/02_运行C99风扰闭环.cmd`](Scripts/cmd/02_运行C99风扰闭环.cmd)；[`Scripts/cmd/03_运行C99电机故障恢复闭环.cmd`](Scripts/cmd/03_运行C99电机故障恢复闭环.cmd) |
| MoSim Ground Control / QGC 操作界面 | [`Scripts/cmd/启动MoSim地面站.cmd`](Scripts/cmd/启动MoSim地面站.cmd) |
| 停止当前受管仿真进程 | [`Scripts/cmd/停止所有仿真.cmd`](Scripts/cmd/停止所有仿真.cmd) |

当前正式 C99 记录只覆盖 px4ctrl 图形 C99 后端的单机生命周期、受限风扰注入和
转子效率故障恢复确认。它不代表规划器、多机、严格性能门、完整故障容错或 QGC/UE
显示闭环已通过。旧 FUEL、Diff 和三机入口保留在
[`Scripts/cmd/Archive/legacy_unverified/`](Scripts/cmd/Archive/legacy_unverified/)，只供追溯。

## 目录地图

| 路径 | 责任 |
| --- | --- |
| `Models/` | 项目拥有的 MWORKS/Sysplorer 模型；正式根为 `MoSimQuadrotorModel/`。 |
| `Config/` | 控制器、场景、ExperimentProfile、能力索引及机器可读协议。 |
| `Scripts/` | 运行编排、质量检查、结果提取、绘图与测试。 |
| `Scripts/cmd/` | 当前 Windows 双击入口；仅保留 C99 单机复现、地面站和受管停止。 |
| `apps/` | MoSim Ground Control、Model Studio 和项目应用代码。 |
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
`canonical_active` 表示注册表的活动路径已经指向 `src/`，并已通过项目本地
静态入口检查；它不等于已经通过运行时性能验收。`copied_pending_activation`
仍是注册表的保留状态，用于将来的迁移项，但下表九个组件不再使用该状态。

### 本批次已切换的九个组件

| 组件 | 源码路径 | 当前解析路径 | 状态 | 主要入口 |
| --- | --- | --- | --- | --- |
| Sunray 规划工具 | `src/integration/ros1_launch/sunray_planner_utils` | `src/integration/ros1_launch/sunray_planner_utils` | `canonical_active` | `Config/profiles/runtime_bindings.json#planner_adapter.launch`; `Config/runtime/ros1_local_source_manifest.v1.json#mission_adapter` |
| Sunray 任务适配器 | `src/planning/mission_adapters/sunray_tutorial` | `src/planning/mission_adapters/sunray_tutorial` | `canonical_active` | `Config/runtime/ros1_local_source_manifest.v1.json#mission_adapter` |
| FUEL | `src/planning/fuel` | `src/planning/fuel` | `canonical_active` | `Scripts/sunray/check_fuel_ros1_preflight.sh`; `Config/runtime/ros1_local_source_manifest.v1.json#fuel` |
| FALCON | `src/planning/falcon` | `src/planning/falcon` | `canonical_active` | `Scripts/sunray/check_falcon_ros1_preflight.sh`; `Config/runtime/ros1_local_source_manifest.v1.json#falcon` |
| RACER | `src/planning/racer` | `src/planning/racer` | `canonical_active` | `Scripts/sunray/build_racer_ros1_upstream_smoke.sh`; `Config/runtime/ros1_local_source_manifest.v1.json#racer` |
| Diff-Planner | `src/planning/diff_planner` | `src/planning/diff_planner` | `canonical_active` | `Scripts/sunray/setup_goal4_diff_planner_overlay.sh`; `Config/runtime/ros1_local_source_manifest.v1.json#diff_planner` |
| EGO-Planner Swarm | `src/planning/ego_planner_swarm` | `src/planning/ego_planner_swarm` | `canonical_active` | `Scripts/sunray/setup_goal4_ego_overlay.sh`; `Config/runtime/ros1_local_source_manifest.v1.json#ego_planner_swarm` |
| 固定编队 | `src/planning/fixed_formation` | `src/planning/fixed_formation` | `canonical_active` | `Scripts/sunray/build_swarm_formation_ros1_upstream_smoke.sh`; `Config/runtime/ros1_local_source_manifest.v1.json#fixed_formation` |
| QGroundControl 主体 | `src/ground_station/qgc/qgroundcontrol` | `src/ground_station/qgc/qgroundcontrol` | `canonical_active` | `Scripts/ui/build_flight_console.ps1`; `Scripts/ui/generate_qgc_vendor_manifest.py` |

### 其他项目本地活动路径

`src/simulation/gazebo/sunray`、`src/simulation/gazebo/plugins/sunray`、
`src/flight_stack/mavros/sunray_uav_control`、`src/common/utilities/ros1/sunray_common`、
`src/control/runtime_adapters/px4ctrl`、`src/integration/ros1_launch/quadrotor_msgs`、
`src/common/utilities/ros1/uav_utils`、`src/common/utilities/ros1/cmake_utils`、
`src/perception/fast_lio`、`src/perception/livox_ros_driver_compat` 和
`src/ground_station/qgc/mosim_extension` 也保持 `canonical_active`。其入口由
`Config/project_paths.json`、`Config/profiles/runtime_bindings.json` 与
`Config/runtime/ros1_local_source_manifest.v1.json` 共同约束。

### 交付与外部依赖

可移植源码包应包含 `Models/`、`Config/`、`Scripts/`、`apps/`、`src/`、`Docs/`、
`Scripts/cmd/`，以及需要展示时的 `UE5/`；报告复核所需的筛选后 `Results/` 作为独立
证据包交付。以上九个组件不再把
`References/` 作为活动源码输入。`References/` 在本机保留为上游追溯、回退和
Sunray 资产再物化来源，不能按目录整体删除。

源码包与证据包必须分开验证：根 `.gitignore` 排除了 `Results/`，因此干净 Git 克隆
默认不包含结果文件。源码包负责模型、配置、脚本、APP 和运行时输入；证据包负责
报告引用的指标、CSV/JSON、截图和运行记录。APP 首次点击“写入配置”时会在
`Results/ui_platform/model_studio_task_handoffs/` 自动生成 `latest.json` 与临时 harness，
干净源码包缺少这个文件是正常的，不应把历史交接文件当作仿真结果。证据包应携带
自己的发布 ID、相对路径清单和 `SHA256SUMS.txt`，不能依赖开发者机器的绝对路径。

Sunray 的大型运行资产已经物化到 `src/`，但因体积被 Git 忽略，最终压缩包必须带上：

| 内容 | 本地目标路径 | 规模 | 校验方式 |
| --- | --- | ---: | --- |
| Gazebo 网格、纹理、扫描数据与 Blender 源 | `src/simulation/gazebo/sunray/` | 487 文件，1,005,559,590 B | `ASSET_MANIFEST.json` |
| Livox 插件扫描时序 | `src/simulation/gazebo/plugins/sunray/` | 6 文件，156,521,030 B | `ASSET_MANIFEST.json` |

若不随源码包携带这些大文件，必须提供内容完全匹配两个资产清单的独立资产包；否则
Gazebo 包不能作为完整运行输入。外部运行环境也不属于源码包：MWORKS/Sysplorer、
Ubuntu 20.04、ROS Noetic、Gazebo Classic、MAVROS、PX4 工具链，以及 QGC 所需的
Qt 6.8.3、Visual Studio 2022 C++ Build Tools、Windows SDK 和 GStreamer 1.22.12。

执行下列检查可验证路径和资产，不会启动仿真：

```powershell
python Scripts/quality/check_project_path_registry.py --project-root . --require-canonical-active
python Scripts/quality/check_local_source_activation.py --project-root .
# Only when retained References/Sunray is available and large assets are absent:
python Scripts/quality/materialize_sunray_runtime_assets.py --materialize
python Scripts/quality/materialize_sunray_runtime_assets.py
```

详见 `Results/static_audits/local_source_activation_20260801/`。上述检查和构建预检
不等于 Gazebo/PX4/ROS/MAVROS、规划器、控制器或飞行运行时验收。

## 阅读与操作

建议按以下顺序进入项目：

1. [`Docs/README.md`](Docs/README.md)：文档职责和按角色的阅读路径。
2. [`Docs/Design/赛题.md`](Docs/Design/赛题.md)：比赛目标、评分和交付边界。
3. [`Docs/Design/架构.md`](Docs/Design/架构.md)：软件与证据权威边界。
4. [`Docs/Index/simulation_model_structure_index.md`](Docs/Index/simulation_model_structure_index.md)：模型、场景、runner 和结果的对应关系。
5. [`Docs/Workflows/mainline_operations_board.md`](Docs/Workflows/mainline_operations_board.md)：当前工程选择与下一项门。
6. [`Docs/Workflows/sunray_ros1_current_runtime_lane.md`](Docs/Workflows/sunray_ros1_current_runtime_lane.md) 和 [`Docs/Workflows/sunray_ros1_execution_checklist.md`](Docs/Workflows/sunray_ros1_execution_checklist.md)：ROS1/Sunray/Gazebo/PX4/RViz 运行约束。
7. [`Docs/报告/用户手册_正文骨架.md`](Docs/报告/用户手册_正文骨架.md)：MWORKS 操作与 C99 单机复现步骤、结果判据和阻断处理。

## 实验与归档边界

当前目录布局和模型/源码入口保持稳定，不执行大范围重构。经过依赖审计、哈希归档
和原路径留痕后，可以把明确无活动依赖的 `Results/` 或 `Config/` 子树移入
`MoSim_Archive/`；这不等于允许移动模型根、当前运行时配置、UI/UE 资产或活动证据。
`References/` 也不能按“已复制”整体删除，必须以本节路径表和实际消费者为准。

旧实验、兼容配置和历史结果的归档必须保留归档清单、SHA-256 和原路径说明。归档
只改变默认交付包的内容，不改变已声明的模型、控制器和证据结论。

### 当前归档收敛记录（2026-08-01）

- 已将 5 个无活动引用的旧 Codex/coagent GUI 与线程维护诊断目录归档到外部
  `MoSim_Archive/20260801_unreferenced_codex_gui_phase3/`（该目录不属于源码包，
  仅作为本机归档示例）。
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

最终竞赛包至少应包含完整模型和依赖、配置、脚本、独立的可复现证据包、用户手册、
仿真分析报告以及演示视频。提交前按
[`Docs/Workflows/pre_submit_check.md`](Docs/Workflows/pre_submit_check.md) 逐项检查；
报告写作源、图件和导出要求位于 `Docs/报告/`。
