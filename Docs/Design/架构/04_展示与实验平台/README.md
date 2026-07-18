# 04 展示与实验平台

本组负责 RViz、Gazebo GUI、UE、Web、QGC 和实验平台的显示、操作和证据边界。

第一阶段控制成功判定仍以日志、metrics、truth对比和可复现运行包为准。
RViz/Gazebo/UE/Web/QGC只提供审核、操作和视频证据，不拥有控制器成功判定权。

## 文档入口

| 文档 | 用途 |
| --- | --- |
| `展示与实验平台接口.md` | 定义RViz/Gazebo/UE/Web/QGC职责、ExperimentProfile入口、多窗口布局、证据采集和禁止声明 |
| `UE渲染镜像桥接方案.md` | 定义Gazebo/PX4/ROS1到UE的单向渲染镜像路线、桥接帧契约、坐标/时间边界和验收门禁 |
| `Factory地图导入与全局态势视图.md` | 冻结Factory作为第一张正式UE地图，定义L2静态导入Gazebo、10Hz UE全局姿态轨迹和用户审核门禁 |
| `RViz与UE低延迟嵌入接口.md` | 定义RViz/UE暖进程复用、attach/detach、嵌入模式、DisplayFrame延迟字段和回退路径 |
| `双GUI与非AI系统闭环实施规划.md` | 冻结Syslab原生Model Studio、开源底座Flight Console、Orchestrator、统一运行状态、遥测字典、注入事务、结果对比、动态禁用、单机/三机闭环和3至9机扩展长期Goal；双GUI运行语义以此为权威 |
| `Flight Console与二维任务地图详细设计.md` | 冻结QGC 5.0.8复用审计、超维与其他开源项目取舍、UE主视图、右上角小地图/放大任务地图、航点/边界/多机任务编辑、坐标和Orchestrator发布合同 |
| `MWORKS实时联合仿真与双GUI接口设计.md` | 定义generated-C主线与MWORKS Live实验路径、定点/程控操作、实时I/O、Profile归属、QGC状态、fallback和RT0至RT5门禁 |
| `Model Studio三模式界面与QGC交接设计.md` | 冻结Model Studio三模式界面、ATTITUDE_THRUST v1控制层级、故障待应用语义、QGC交接和RunManifest所有权 |
| `../00_架构与任务/任务算法与场景地图注册接口.md` | 定义Flight Console消费的任务算法注册、场景地图包、Factory二维地图、地图切换和未知地图隔离契约 |
| `Flight Console开源选型调研.md` | 比较QGC、XTDrone、Prometheus、MRS、Aerostack2、PlotJuggler与RViz，冻结QGC主底座和XTDrone RViz参考路线 |
| `Model Studio Syslab原生APP能力门禁.md` | 确认TyAppDesigner原生APP路线、能力边界、单项禁用限制和D1运行/打包验收条件 |

## 第一阶段显示基线

```text
RViz:
  点云、累计地图、栅格地图、飞机三轴、参考轨迹、实际轨迹、TF树；

Gazebo:
  后台plant、模型装配、传感器安装和碰撞；GUI不常驻展示，只在诊断或人工要求时打开；

QGC:
  飞控连接、模式、解锁、参数和failsafe状态；

Web/脚本入口:
  只提交已注册ExperimentProfile，不直接拼裸命令；

UE:
  单机/多机第三视角、Global Overview 10Hz姿态轨迹和视频展示。
```

UE桥接的第一实现目标是单向渲染镜像。Gazebo/PX4/MAVROS/ROS1继续拥有
控制、plant、truth、日志和metrics权威；UE只消费状态帧并产出展示、视频和
人工审核证据。

Factory是第一张正式UE地图。当前目标是L2静态导入Gazebo：真实visual mesh、
分块collision mesh、semantic manifest、坐标契约、对齐报告和用户审核包。
