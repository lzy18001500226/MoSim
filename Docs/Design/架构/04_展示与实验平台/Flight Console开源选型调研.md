# Flight Console开源选型调研
> 状态：D2选型和D5原生GUI门禁已通过，2026-07-17。
>
> 本文记录MoSim Flight Console的本地源码审计和GitHub候选比较。当前产品行为、
> QGC复用点、二维任务地图和实现门禁以`双GUI与非AI系统闭环实施规划.md`和
> `Flight Console与二维任务地图详细设计.md`为准。

## 1. 需求摘要

Flight Console需要同时满足：

- Windows桌面运行；
- 复用PX4/MAVLink连接、模式、解锁、failsafe和多机状态；
- Qt/QML可扩展页面；
- 接入MoSim Orchestrator，不直接拼ROS/MAVROS命令；
- 管理RViz和UE视图；
- 显示实时遥测、注入、事件、指标和证据；
- 预留3至9机，但首版只开放3机；
- 上游源码复制到项目自有路径后再二次开发，不修改`References/`。

## 2. 候选快照

GitHub元数据于2026-07-17通过公开API读取；star只作为社区信号，不作为单独决策依据。

| 候选 | GitHub | Stars快照 | 许可证 | 主要价值 | 主要问题 | 结论 |
| --- | --- | ---: | --- | --- | --- | --- |
| QGroundControl | https://github.com/mavlink/QGroundControl | 4768 | Apache-2.0 | Qt6/QML、Windows、MAVLink/PX4、多机、视频、官方Custom Build | 完整源码约94.6 MB；与ROS1 RViz跨OS/Qt版本不同 | 主底座 |
| XTDrone | https://github.com/robin-shaun/XTDrone | 1695 | MIT；本地ROS包声明BSD | 现成Qt `rviz::RenderPanel`、ROS1、多机地面站示例 | 旧Melodic/Qt5、Linux/catkin、界面和生命周期较旧 | RViz集成参考，不作主底座 |
| Prometheus | https://github.com/amov-lab/Prometheus | 3203 | Apache-2.0 | ROS无人机栈、MID360/RViz、多机和消息设计 | 本地未发现成熟UAV桌面GCS；整体约1 GB | 消息/布局参考，不复制整仓 |
| MRS UAV System | https://github.com/ctu-mrs/mrs_uav_system | 623 | BSD-3-Clause | 成熟多机ROS生态和状态工具 | 不是Windows PX4地面站；系统耦合较重 | 多机状态参考 |
| Aerostack2 | https://github.com/aerostack2/aerostack2 | 361 | BSD-3-Clause | 模块化任务执行和多机架构 | ROS2，不匹配当前ROS1主线 | 架构参考 |
| PlotJuggler | https://github.com/PlotJuggler/plotjuggler | 6045 | MPL-2.0 | 高性能实时曲线、插件和数据源 | 不是飞控地面站；许可证与集成边界需隔离 | 曲线交互参考，首版不复制 |
| ROS1 RViz | https://github.com/ros-visualization/rviz | 968 | BSD-3-Clause | 原生RenderPanel和Display插件 | 当前运行于Ubuntu 20.04/WSL，不能直接链接进Windows Qt6 QGC | WSL侧视图权威 |

`foxglove/studio`当前公开仓库已归档，且不提供QGC/PX4飞控操作主链，不作为候选。

## 3. 本地源码证据

### 3.1 QGroundControl

本地路径：`References/PX4/qgroundcontrol/`。

已确认：

- README声明面向MAVLink无人机；
- `custom-example/`提供正式Custom Build模板；
- `CustomPlugin`、`QGCOptions`和QML覆盖点可隐藏原界面、增加设置页和替换Fly View层；
- 使用Qt6，包含Windows CMake preset；
- `multiVehicleManager.activeVehicle`等多机能力可复用；
- 本地快照约3353个文件、94.6 MB，最大单文件约6.1 MB。

这比从零实现PX4连接、MAVLink状态机、参数、模式和failsafe风险更低。

### 3.2 XTDrone

本地路径：
`References/UAVStacks/XTDrone/control/XTDGroundControl/cplusplus/xtdgroundcontrol/`。

`qrviz.cpp`明确使用：

```text
rviz::RenderPanel
rviz::VisualizationManager
rviz::ToolManager
manager->createDisplay(...)
```

这证明“Qt桌面窗口内嵌RViz”有现成ROS1实现模式。但该包依赖catkin、ROS Melodic、
Qt5和Linux，不能把代码直接链接进Windows Qt6 QGC。可复用的是ViewDescriptor、
Display配置和WSL侧RenderPanel服务设计，不是二进制或源码直接拼接。

### 3.3 Prometheus

本地存在大量RViz配置、MID360和多机仿真入口，但未发现可替代QGC的成熟UAV桌面
控制台。整仓体积约1 GB，不适合作为Flight Console源码底座。

## 4. 冻结组合

```text
主应用:
  QGroundControl Custom Build / CustomPlugin

MoSim专属页面:
  ExperimentProfile
  Run Control
  Telemetry
  Injection
  Evidence
  Display Sessions

RViz:
  Ubuntu 20.04 / ROS1侧RenderPanel或独立RViz
  -> 第一版managed external
  -> 后续稳定流式/RenderPanel endpoint

UE:
  Windows packaged runtime
  -> 第一版managed external
  -> 对比原生窗口/共享纹理与Pixel Streaming后再嵌入

实时曲线:
  首版使用Qt Charts或QGC已有图表能力
  -> 不把PlotJuggler整体嵌入主进程
```

选择QGC不表示直接修改`References/PX4/qgroundcontrol`。正式开发必须先建立项目自有
源码副本和上游追踪信息。

## 5. 源码复制门禁

目标结构：

```text
apps/flight_console/
  UPSTREAM.md
  LICENSES/
  vendor/qgroundcontrol/
  mosim/
```

复制前必须完成：

1. 记录上游URL、commit/tag、许可证和本地快照来源；
2. 确认当前快照是否完整包含Windows构建所需文件；
3. 排除测试缓存、构建目录、移动端目录和本Goal不需要的巨大资产，但不能删掉
   Windows/QML/MAVLink/视频/Custom Build依赖；
4. 生成文件清单与SHA256；
5. 在副本上完成无MoSim修改的Windows基线构建；
6. 只在`mosim/`和官方允许的Custom Build覆盖点开发；
7. 保留上游同步脚本或清晰的手工更新流程。

如果裁剪导致QGC无法基线构建，回退到完整源码副本，不允许用无法复现的本机安装包
替代源码门禁。

## 6. D2与D5验收结果

当前已完成：

- 主底座冻结为官方稳定版QGroundControl `v5.0.8`；
- release commit冻结为`e0816c957602789200ae5ba0af45217f0f2f1db4`；
- 唯一子模块冻结为`a458e8e86a8ffa3b7f52f4601adcdaaff0db5f42`；
- 官方归档、许可证、项目自有完整源码副本和2638文件SHA256清单已形成；
- `References/PX4/qgroundcontrol/`保持未修改，产品源码位于
  `apps/flight_console/vendor/qgroundcontrol/`。

早期工具链阻断记录保留在
`Results/ui_platform/qgc_d2_gate_20260717/PREFLIGHT.json`，但不再代表当前状态。项目已在
`.tools/flight-console/`冻结Qt 6.8.3、Ninja 1.13.0、GStreamer 1.22.12和兼容的
PX4-GPSDrivers，并使用VS2022 Community、MSVC 14.44和Windows SDK 10.0.26100完成
325/325 Release构建，产物为：

```text
build/flight-console-qgc/Release/MoSimFlightConsole.exe
```

Run、Telemetry、Injection、Displays和Evidence五页已在2560x1440、125% DPI下完成原生
可见性复核。证据位于：

```text
Results/ui_platform/flight_console_native_review_20260717/
```

因此D2选型/来源门禁和D5原生GUI门禁均已通过。该结论不证明MAVLink连接、Gazebo飞行、
实时注入、UE/RViz绑定或二维任务地图完成；这些能力仍分别由D6/D7和Q1-Q5 runtime门禁证明。
