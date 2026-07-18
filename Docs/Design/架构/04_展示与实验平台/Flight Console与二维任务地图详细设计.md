# MoSim Flight Console与二维任务地图详细设计

> 状态：产品与接口冻结设计，2026-07-18。
>
> 本文细化`双GUI与非AI系统闭环实施规划.md`中的Flight Console，并定义
> `MoSimMapView`的产品行为、任务编辑、坐标合同和QGroundControl复用边界。
> 本文不证明地图、任务规划、多机控制或完整运行闭环已经通过runtime验收。

## 1. 冻结结论

1. MoSim Flight Console继续基于官方QGroundControl `v5.0.8` Custom Build二次开发，
   不另起一套通用地面站，也不直接修改`References/`或冻结的vendor上游源码。
2. UE必须真正嵌入Flight Console主窗口并作为默认三维主视图；受控外部UE窗口只用于
   调试和显示故障降级。二维地图不是装饰性缩略图，而是任务规划、空间约束配置和
   二维态势显示的正式操作面。
3. 二维地图默认以右上角小地图显示，点击后展开为完整任务地图；编辑完成后收回，
   不与UE长期争夺中央区域。
4. Factory使用项目自有离线米制地图，不依赖高德、Google、Bing或其他在线地图服务。
   后续室外地图可以增加地理配准离线Provider，但不能改变任务接口。
5. 优先复用QGC原生Mission、GeoFence、Rally Point编辑器、数据模型和MAVLink事务。
   `MissionDraft`是MoSim统一任务信封，不是重新实现一套QGC Mission系统。
6. 所有任务必须经坐标、边界、能力、安全、Profile和运行状态校验，再由Orchestrator
   选择任务Adapter。普通航点/围栏进入`PX4MissionAdapter`并复用QGC/MAVLink原生上传、下载
   和ACK；探索、覆盖与编队进入对应Planner/Formation Adapter。Orchestrator不重写规划器。
7. QML不得绕过Orchestrator直接发布ROS/MAVROS setpoint或任意MAVLink控制命令。
8. MWORKS不进入Gazebo快速控制回路。主闭环是MWORKS模型/MIL/SIL/codegen，生成控制核心
   进入PX4/Gazebo/Sunray运行时，运行结果回流MWORKS分析和迭代。

## 2. 系统叙事与报告口径

### 2.1 MWORKS与Gazebo分工

```text
MWORKS Model Studio
  -> 控制器/模型设计
  -> MIL/SIL与代码生成一致性
  -> 发布已验证ExperimentProfile

Orchestrator
  -> 冻结run、hash、场景、任务、控制器和参数
  -> 启动Gazebo/PX4/MAVROS/控制器运行时

Gazebo/PX4/Sunray
  -> plant、传感器链、执行器动态、扰动、故障、碰撞和多机通信
  -> 运行日志与评价truth

Flight Console / UE / RViz
  -> 操作、二维任务、三维展示和工程审核

MWORKS结果回传
  -> MIL/SIL/generated-C/Gazebo并列比较
  -> 参数与控制律下一轮迭代
```

不把“MWORKS在线UDP发送控制量”作为主线。在线联合仿真只保留为后续可选研究项，
且最多承担低频高层参考，不得形成MWORKS和PX4两个最终控制权威。

### 2.2 参数证据口径

报告不得仅凭真机或仪器照片把全部模型参数表述为实测真值。参数应分为：

| 类别 | 例子 | 最小证据 |
| --- | --- | --- |
| 真机实测 | 质量、轴距、重心、可执行的推力/力矩测试 | 设备、过程照片、原始记录、单位、日期、误差或重复次数 |
| 系统辨识 | 电机时滞、阻力、执行器响应 | 激励、输入输出、辨识方法、拟合和验证结果 |
| 资料/模型先验 | 未完成实测的惯量、气动或执行器参数 | 来源、版本、采用理由和不确定性 |

推荐报告表述：

> 基于云纵Sunray150真机开展质量、几何尺寸、重心及动力系统等参数测量，并结合设备资料、
> Gazebo模型参数和系统辨识结果，建立硬件约束一致的无人机模型。模型级仿真用于验证控制律
> 和生成代码一致性，同一生成控制核心进一步进入PX4/Gazebo/Sunray运行链，在传感器、
> 执行器、环境扰动、故障、碰撞和多机通信条件下开展更高工程保真度的系统级验证。

不得使用“所有参数均为真机实测”“Gazebo等同真实飞行”或“完整数字孪生”等超过证据的表述。

## 3. 外部资料审计

调研快照日期为2026-07-17。GitHub stars只用于粗略判断社区规模，会随时间变化；产品选型
仍以接口、许可证、维护和本项目适配性为准。

### 3.1 官方QGroundControl `v5.0`

来源：

- [QGC Custom Builds](https://docs.qgroundcontrol.com/Stable_V5.0/en/qgc-dev-guide/custom_build/custom_build.html)
- [QGC Plan View](https://docs.qgroundcontrol.com/Stable_V5.0/en/qgc-user-guide/plan_view/plan_view.html)
- [QGC Fly View](https://docs.qgroundcontrol.com/Stable_V5.0/en/qgc-user-guide/fly_view/fly_view.html)
- [QGC Offline Maps](https://docs.qgroundcontrol.com/Stable_V5.0/en/qgc-user-guide/settings_view/offline_maps.html)
- [QGC Custom MAVLink Actions](https://docs.qgroundcontrol.com/Stable_V5.0/en/qgc-user-guide/custom_actions/custom_actions.html)
- [mavlink/QGroundControl](https://github.com/mavlink/qgroundcontrol)

官方可直接复用的能力：

- Custom Build插件、资源覆盖、Fly View overlay、工具栏、导航和高级模式；
- Plan View航点编辑、拖动、任务列表、上传/下载、保存和恢复；
- Survey与Structure Scan等复杂几何任务生成；
- GeoFence、Rally Point、Planned Home和任务统计；
- Fly View多机位置、任务显示、Go To/Orbit、暂停和任务继续；
- Map/Video画中画、切换、独立窗口和录像；
- `MultiVehicleManager`、任务控制器、地图Polyline/Polygon和车辆图标；
- 离线瓦片缓存及地图Provider基础设施；
- 自定义MAVLink Action文件，但MoSim只允许经过白名单和状态门禁的动作。

官方离线地图是“缓存在线地图瓦片”，不能直接解决Factory本地米制坐标问题。MoSim应复用
QML地图交互、图层和任务控制思想，使用项目自有`local_metric_map` Provider和变换合同。

### 3.2 超维空间科技QGC二次开发

本地来源：`References/超维空间科技/`。

实际新增能力：

- 在Analyze区域新增`Swarm`页面；
- 使用QGC `MultiVehicleManager`和MAVLink消息聚合三机状态；
- 按`vehicle_id/sysid`向三架飞机分别发送命令；
- QGC通过UDP `8080/8081`与MATLAB交换位置和速度；
- MATLAB计算Leader-Follower速度参考；
- 自定义`SP_LOCAL` MAVLink消息进入PX4 swarm模块。

可借鉴：

- 多机状态按`vehicle_id`隔离；
- 一个控制台统一显示逐机位置、速度、连接和命令状态；
- 高层算法、QGC显示和PX4执行的模块边界；
- 专用页面接入QGC导航和资源系统的方法。

不得复用：

- 固定三机数组、固定端口、固定`z=-5`和约5 Hz命令路径；
- 裸`float[]` UDP及缺少版本、时间戳、序号、CRC、超时和过期命令策略；
- QGC成为MATLAB与PX4之间的控制路由器；
- 直接修改MAVLink `common.xml`；
- 无速度限幅、避障、最小间距、安全状态和物理ACK的命令发送；
- 把Analyze页面或QGC进程存在当作任务ready。

MoSim仅吸收其多机聚合和QGC页面扩展经验。控制和任务请求统一进入Orchestrator，
QGC退出不得导致控制链断开。

### 3.3 其他开源项目

| 项目 | 调研价值 | MoSim取舍 |
| --- | --- | --- |
| [CubePilot/qgroundcontrol-herelink](https://github.com/CubePilot/qgroundcontrol-herelink) | QGC硬件产品化、设备定制和长期维护分支 | 参考Custom Build维护、设备状态和精简普通模式，不引入Herelink硬件耦合 |
| [Auterion/qgroundcontrol](https://github.com/Auterion/qgroundcontrol) | 商业产品下游fork和上游同步 | 只参考fork治理，不依赖其未公开产品能力 |
| [Blue Robotics QGC](https://github.com/bluerobotics/qgroundcontrol) | 特定载具插件、定制操作面 | 参考车辆专用插件和简化页面，不复制水下机器人语义 |
| [DeepWaterExploration QGC](https://github.com/DeepWaterExploration/qgroundcontrol) | 多路H.264视频扩展 | 为以后多机相机/UE流保留多流选择接口，当前无相机不实现 |
| [OpenHD/QOpenHD](https://github.com/OpenHD/QOpenHD) | Qt/QML遥测、视频、OSD和链路健康 | 参考显示链路质量、延迟、码率、丢帧和stale状态，不作为QGC底座 |
| [ArduPilot Mission Planner](https://github.com/ArduPilot/MissionPlanner) | 成熟任务、围栏、日志和参数工作流 | 参考任务编辑和日志回看交互；技术栈与PX4主线不同，不移植代码 |
| [mavsdk_drone_show](https://github.com/alireza787b/mavsdk_drone_show) | 多机编队任务、逐机状态和批量操作 | 参考舰队分组、逐机失败隔离和批量操作确认，不替代当前三机运行链 |

结论：官方QGC仍是唯一主底座。其他项目只提供功能和交互参考，不能因为某个单点功能
引入第二套地面站框架。

## 4. 产品工作区

### 4.1 默认布局

```text
顶部
  run_id | Profile | 当前地图 | 任务 | Gazebo/PX4/MAVROS/定位/控制器 | UE录制状态 | 急停

左侧
  预检 | 准备仿真环境 | QGC原生解锁/起飞/任务控制 | 悬停 | 返航 | 降落

中央
  UE三维主视图
  -> 无飞机时自由视角
  -> 生成后默认环绕跟随
  -> 自由/环绕/跟随、飞机选择和距离调节彼此独立

右上角
  Factory二维任务小地图
  -> 飞机位置、机头方向、飞行状态、关键航点、实际轨迹、未来预期轨迹
  -> 不承担FUEL/Diff边界编辑或frontier等工程诊断图层
  -> 点击展开完整任务地图

右侧
  逐机遥测 | 扰动/故障注入 | Safety/Failsafe | 请求值/实际值/ACK

底部
  事件时间线 | 告警 | 指标摘要 | 截图 | 开始/停止UE录制 | 证据目录
```

点云RViz和三维栅格RViz保留为独立按钮，并提供`关闭全部RViz`，不常驻挤占UE或二维地图。
该关闭动作只清理由MoSim启动或已被当前run接管的RViz会话，不按进程名误关其他项目窗口。
UE视频默认不录制；用户点击`开始UE录制`后显示红色录制状态、已用时间、目标文件和磁盘余量，
再次点击执行flush并停止。地图、UE、RViz或录像失败只降低显示证据等级，不得阻塞控制和日志。

QGC原生Fly/Mission操作继续拥有解锁、起飞和开始/暂停任务语义。MoSim不复制第二套飞行按钮，
只增加`准备仿真环境`，负责Profile预检以及Gazebo、PX4、MAVROS、定位、控制器和显示消费者
进入`ready`；到达`ready`后，飞行操作交还QGC原生流程。

### 4.2 `MoSimMapView`三种状态

| 状态 | 用途 | 交互 |
| --- | --- | --- |
| `mini_monitor` | 右上角实时飞行态势 | 显示飞机位置/方向/状态、关键航点、实际轨迹和未来预期轨迹；选择飞机、全机适配、跟随、点击展开；禁止边界和规划参数编辑 |
| `expanded_plan` | 运行前任务与边界编辑 | 完整工具栏、图层、任务列表、属性编辑、校验和发布 |
| `expanded_monitor` | 飞行中二维监控 | 查看实时状态、规划、轨迹、告警；高风险编辑默认锁定 |

中央显示模式保留`UE 3D`、`2D Mission Map`和`UE + 2D split view`。小地图展开默认覆盖
中央区域而不是弹出第二个无管理窗口；需要对照时再使用split view。

`mini_monitor`不是缩小版工程诊断地图。它默认只提供驾驶员需要的飞行态势，不显示FUEL
全部frontier候选、覆盖栅格、Diff内部优化节点或其他高密度调试对象。FUEL、Diff等算法的
边界、起点、目标、参数和诊断图层统一进入`expanded_plan`；运行后如需复核，再由
`expanded_monitor`按图层开关显示。

### 4.3 地图轨迹术语与断连行为

Flight Console只向普通操作员暴露两类轨迹：

| 名称 | 含义 | 默认显示 |
| --- | --- | --- |
| `actual_trajectory` | 飞机已经真实走过的历史路径 | 开 |
| `expected_future_trajectory` | 当前任务或规划器从当前位置开始、尚未执行的未来路径及关键航点 | 开 |

界面不再把`reference trajectory`、`planner trajectory`、`current plan`等相近术语同时暴露给
普通模式。算法内部仍可保留原始字段，但必须由Adapter转换成上述两类显示语义。两条轨迹
需要视觉可区分，以便判断未来路径和已经走过的路径，但不把它包装成控制器参考/实际误差
对比工具；详细跟踪误差属于Telemetry、RViz或MWORKS结果查看器。

飞机位置必须来自当前run的新鲜Gazebo/ROS状态，并同时携带`run_id`、`vehicle_id`、
`frame_id`和时间戳。Gazebo/ROS连接不存在、位置超过新鲜度门限、run不一致或坐标合同不
匹配时，小地图和Plan View都隐藏飞机、实际轨迹和未来预期轨迹，并显示`未连接`或具体
失效原因。不得保留最后位置、继续外推或用UE窗口仍在运行来冒充实时飞行状态。

### 4.4 快速实验、算法实验与学习训练

Flight Console右侧工作区提供三个由注册表驱动的模式：

| 模式 | 面向对象 | 核心操作 |
| --- | --- | --- |
| Quick Experiment | 普通演示与重复实验 | 选择已发布Profile，准备、启动、注入、停止、分析 |
| Algorithm Lab | 规划/控制算法对比 | 选择任务算法、传感器路线、参数集、对照算法和验证矩阵 |
| Learning Training | 学习规划器开发 | 生成训练配置、启动Isaac训练、查看曲线、导出并注册策略、运行Gazebo验证 |

YOPO训练表单至少包含：算法、训练Backend、Factory/随机障碍场景、前向深度相机Profile、
速度范围、并行环境数量、训练步数、seed、Domain Randomization和PyTorch/ONNX/TensorRT导出
格式。对应按钮固定为：

```text
生成训练配置 | 开始Isaac训练 | 打开训练曲线
导出ONNX/TensorRT | 注册策略 | 运行Gazebo验证 | 对比经典规划器
```

按钮只生成统一Action对象，不直接启动进程。YOPO、Isaac或深度相机尚未满足当前Profile门禁
时，控件保持可见但禁用，并显示`disabled_reason`、缺失依赖和解锁动作。界面不得用静态
训练曲线、示例策略或伪ACK替代真实后端。

右侧同时提供`Live Inspector`入口，底部提供全局`Operation Center`。前者复用QGC Fact System、
MAVLink Inspector和图表基础能力，并接入ROS、控制器、规划器、安全与故障信号；后者显示
Gazebo/PX4/UE/RViz、codegen、训练和自动调参的真实阶段。完整合同见
`参数信号自动调参与运行可观测性详细设计.md`。

## 5. 二维地图工具与任务语义

### 5.1 工具栏

```text
选择/平移
目标点
航点路线
探索区域
已知覆盖区域
Geofence
禁飞区
起飞点/降落点/返航点
编队中心路线
测距
撤销/重做
删除选中/清空草稿
图层
适配全图/跟随选中/跟随全机
校验任务
发布任务
```

工具使用Lucide或QGC现有图标并提供tooltip。工具激活状态必须清楚；右键或`Esc`退出当前
绘制，`Ctrl+Z/Ctrl+Y`只作用于未发布草稿，不能撤销已经执行的飞行命令。

### 5.2 空间对象

以下对象不能混为一个“边界”：

| 对象 | 作用 | 是否可由未知探索读取 |
| --- | --- | --- |
| `mission_area` | 本次要求探索、覆盖或执行任务的区域 | 可以，仅作为任务允许范围 |
| `geofence` | 飞机不可越出的安全边界 | 可以，作为安全约束 |
| `keep_out_zone` | 边界内部不得进入的禁飞区 | 可以，作为安全约束 |
| `operator_display_map` | 完整Factory静态底图 | 不可以 |
| `planner_prior_map` | 已知地图任务的规划先验 | 仅known-map任务 |
| `live_occupancy_map` | MID360/建图前端实时占据 | 未知探索的环境输入 |

未知探索可以知道“允许在哪个外框和高度带内搜索”，但不能从完整Factory显示底图取得墙体、
门或障碍物几何。

### 5.3 各任务的地图输入

#### 单点与航点任务

- 点击创建目标，显示`x/y/z/yaw`和目标合法性；
- 航点可拖动、插入、删除、重排，并显示距离、预计时间和高度剖面；
- 发布前运行边界、净空、速度/加速度、锐角和轨迹表示兼容性检查；
- Diff/EGO等规划器收到标准`GoalSet`，而不是QML裸坐标。

#### 单机未知探索

- 用户绘制`mission_area`、高度范围、起点和结束条件；
- FUEL等算法只读取实时占据地图和允许边界；
- FUEL分别提供`fuel_mid360_fastlio_v1`工程路线和
  `fuel_upstream_depth_camera_v1`上游深度相机复现路线；
- 两条路线的传感器、参数、地图前端和证据完全隔离，不允许自动互相替代；
- 地图显示frontier、候选收益、当前B样条、已探索/未知区域和覆盖率定义；
- 算法停止、无frontier或输入过期必须显示原因，不能只让飞机图标停住。

#### 已知地图覆盖

- 用户绘制覆盖多边形、排除区、扫描间距、方向和高度；
- 覆盖算法可以按Profile读取`planner_prior_map`；
- 显示未覆盖、已分配、已覆盖和重扫区域，并保留实际轨迹与计划扫描线区别。

#### 多机任务

- 支持“团队任务自动分配”和“选择飞机后逐机设置”两种方式；
- 每个目标、区域和轨迹必须带`vehicle_id`、owner、租约和有效期；
- 地图按飞机稳定配色，显示团队最小间距、分配冲突、通信stale和掉队状态；
- 批量解锁、起飞、开始、暂停和降落必须显示逐机ACK，不以部分成功冒充团队成功。

#### 编队任务

- 地图编辑的是编队中心/Leader路线、队形类型、间距和朝向规则；
- 同时显示中心参考、slot、成员实际位置和编队误差；
- 单机目标线不能冒充编队轨迹，三机同时到达也不能冒充编队保持通过。

#### 学习局部规划

- YOPO读取前向深度图、状态和目标方向，通过Runtime Adapter输出候选轨迹与评分；
- 界面显示选中轨迹、工程模式下的候选轨迹、置信/评分、推理延迟、策略版本/hash和回退状态；
- YOPO提议必须经过Trajectory Validator和Trajectory Server，不能直接发布电机命令；
- 深度相机失效、输入过期、推理超时或轨迹校验失败时，显示具体原因并执行Profile声明的
  经典规划器回退或安全悬停，不静默沿用过期轨迹。

## 6. 草稿、校验与发布

### 6.1 `MissionDraft`

```yaml
draft_id: uuid
base_profile_hash: sha256
map_id: factory_l2
map_version: v1
coordinate_contract_hash: sha256
mission_kind: waypoint | exploration | known_coverage | formation
vehicle_scope: [uav1, uav2, uav3]
home_or_spawn: {...}
goals_or_waypoints: [...]
mission_areas: [...]
geofence: {...}
keep_out_zones: [...]
altitude_bands: [...]
termination: {...}
created_at: timestamp
revision: integer
```

地图保存的是米制世界坐标和frame，不把像素坐标作为任务真值。`world_to_pixel`只用于渲染
和鼠标反算，任务文件必须携带地图与坐标合同hash。

### 6.2 发布流水线

```text
地图编辑
  -> MissionDraft本地几何检查
  -> world/pixel往返误差检查
  -> SceneMap与任务类型兼容性
  -> 车辆数/算法/传感器/状态源/轨迹表示检查
  -> geofence/keep-out/高度/出生点/净空检查
  -> Trajectory Validator或任务级可达性预检
  -> 生成MissionFrame/GoalSet/Scenario override
  -> 生成新revision和hash
  -> 人工确认摘要
  -> Orchestrator幂等提交
  -> 按mission_kind选择任务Adapter
     waypoint/geofence/rally -> PX4MissionAdapter -> QGC/MAVLink原生事务
     exploration            -> ExplorationPlannerAdapter
     known_coverage         -> CoveragePlannerAdapter
     formation              -> FormationAdapter
  -> Adapter结构化ACK
```

确认摘要至少显示：地图、任务类型、车辆、目标/区域、总距离或面积、高度范围、Geofence、
禁飞区、算法、控制器、风险提示和将被替换的旧任务revision。

### 6.3 运行中修改

| 运行状态 | 地图权限 |
| --- | --- |
| `draft/validated` | 可完整编辑和校验 |
| `prepared/starting/ready` | 地图与Profile冻结；取消run后才能换地图 |
| `armed/airborne/mission_running` | 默认只读；只允许预先验收的Go To或任务变更流程 |
| `holding` | 可以创建新草稿，但必须验证新轨迹后人工确认恢复 |
| `landing/emergency` | 禁止普通任务修改，只保留确定性安全动作 |
| `completed/failed` | 只读回放；修改必须派生新run |

飞行中任务修改必须先进入安全悬停、停止旧轨迹生产者、清理待执行轨迹、验证新任务首条轨迹，
再人工确认恢复。不能在同一时刻保留两个最终轨迹生产者。

## 7. Factory地图与坐标合同

### 7.1 地图资产

Factory二维地图由已验收几何和坐标标定产物生成，禁止使用手工裁剪截图作为权威底图：

```text
floorplan.png
  稳定的游戏式底图、区域颜色和简化视觉

structure.geojson
  墙体、门、柱、区域、边界和交互命中

world_to_pixel.json
  bounds、meters_per_pixel、原点、轴向、3x3变换和逆变换

scene_map.json
  Gazebo/UE/QGC资产、出生点、任务区域、高度带、geofence和全部hash
```

### 7.2 Factory L2底图工具选型

2026-07-18对现成UE制图工具进行一次有界调研，结论如下：

| 方案 | 能力 | 结论 |
|---|---|---|
| `Minimap Capture Pro` | UE 5.4/5.5 Windows编辑器插件；按关卡Capture Volume生成128至8192方形纹理；支持直接材质、高度和多层制图合成 | **拒绝**。Fab标准许可从19.99美元起；用户于2026-07-18明确要求不购买 |
| UE `World Partition Minimap Builder` | 官方生成World Partition编辑器导航缩略图 | 不作为主线。它服务World Partition编辑窗口，不等价于可发布的QGC任务地图资产，且当前Factory关卡未证明采用World Partition |
| UE `SceneCapture2D + Render Target` | UE 5.5官方内置正交场景捕获，可离线得到彩色Render Target | **未来可选增强**。它不是现成地图生成器，当前不为美化底图新建捕获框架 |
| Fab `Ako Minimap System` | 免费、UE 5.2至5.7；基于Spline绘制赛道、标记和跟踪，明确不使用SceneCapture | **拒绝**。不能从Factory关卡生成底图；QGC也已有运行态标记层 |
| `UE4_Minimap` | GPLv3、Blueprint纹理Widget，支持POI、跟踪和缩放 | **拒绝**。依赖预制底图、面向UE4且不负责关卡捕获 |
| `Metis-Map-System` | 未完成的UE5地图Widget原型 | **拒绝**。主要地图功能仍在待办，且仓库未提供明确LICENSE |

调研来源：

- Epic `World Partition in Unreal Engine`：`https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition-in-unreal-engine`
- Epic `Scene Capture 2D`：`https://dev.epicgames.com/documentation/en-us/unreal-engine/1.7---scene-capture-2d?application_version=4.27`
- `Minimap Capture Pro`文档：`https://github.com/Palax/MinimapCapturePro_Docs`
- Fab `Ako Minimap System`：`https://www.fab.com/listings/bfb0cced-ffcf-4254-bf52-379e90951995`
- `UE4_Minimap`纹理Widget参考：`https://github.com/DamirPorobic/UE4_Minimap`
- `Metis-Map-System`：`https://github.com/jamesmckibbin/Metis-Map-System`

没有找到免费、开源且能直接把当前Factory关卡生成高质量可发布底图的成熟工具，候选核验
到此停止。当前主线继续使用`Scripts/ui/build_factory_l2_2d_map.py`对已接受的Factory L2
STL做水平截面，先生成完整范围、坐标正确且可稳定复现的操作员底图；不把它扩展为通用
游戏地图渲染器。`SceneCapture2D + Render Target`只保留为未来视觉美化选项，不阻塞QGC
接入。若未来采用其他出图Adapter，不得改变`world_to_pixel.json`、`structure.geojson`、
`scene_map.json`的坐标合同和图层接口。

Factory完整底图范围与任务范围必须分离：

```text
完整低地面地图边界（底图范围）
  x: [-608.09999, 587.89997] m
  y: [-284.65, 246.35] m
  size: 1195.99996 m x 531.0 m

室内wall/fence边界（FUEL/当前任务叠层）
  x: [-98.40496, 77.25491] m
  y: [-51.36291, 12.63665] m
  size: 175.65987 m x 63.99956 m
```

右上角小地图和Plan View都显示完整Factory底图；当前室内范围只能作为任务边界叠层，不能
用于裁剪底图。`Scripts/ui/build_factory_l2_2d_map.py`及当前
`apps/flight_console/mosim/custom/maps/factory_l2/v1/`必须生成`1196 x 531 m`完整底图，
室内`175.66 x 64 m`范围只作为任务边界叠加；生成后仍需通过视觉与坐标门禁才能接入QGC。

碰撞truth中的组件AABB只能用于语义和校准，不能直接作为底图几何：Spline Blueprint等
Actor的世界AABB会覆盖整段运动范围并生成错误的大实心块。无论底图由插件还是官方捕获
生成，结构/碰撞真值、底图像素和坐标合同仍须分别保存，不能用视觉纹理反推碰撞边界。

视觉风格可以像游戏小地图，但几何不可为美观随意变形。墙体、门和禁飞区需要高对比；
非任务装饰降低对比，避免与实时轨迹和告警争夺视觉层级。

### 7.3 坐标转换

```text
Gazebo/PX4/MAVROS状态
  -> 声明原始frame和ENU/NED语义
  -> State Adapter统一到MoSim world (meter, z-up)
  -> world_to_pixel 3x3仿射变换
  -> QML像素位置和朝向

地图点击像素
  -> pixel_to_world逆变换
  -> world坐标与高度/yaw属性
  -> MissionDraft
```

不得在QML内散落`x/y`交换、符号翻转、固定offset或角度补偿。所有转换由版本化Adapter完成，
并与Gazebo-to-UE变换共同写入SceneMapRegistry。

### 7.4 最小校准门禁

- 三个非共线标定点在Gazebo、UE和二维地图中一一对应；
- 四角边界和至少一个内部地标对应；
- 已知长度比例尺误差通过门限；
- world-to-pixel-to-world往返误差通过门限；
- 飞机起点、机头方向和一段X/Y运动方向一致；
- QGC、UE、Gazebo使用同一`map_id/version/calibration_hash`；
- 地图超界、hash不一致或frame未知时禁止发布任务。

### 7.5 Plan地图与Fly小地图职责

`Plan View`保留QGC原生航点、围栏、Survey、Mission Item和MAVLink上传/ACK能力，是任务
编辑面。`Fly View`右上角地图采用游戏小地图形态，默认只显示Factory底图、飞机位置与
朝向、飞行状态、关键航点、实际轨迹、未来预期轨迹和必要告警；点击后展开为只读态势图，
不复制航点或边界编辑工具。FUEL探索边界、Diff规划边界、起点/目标、Geofence、禁飞区和
规划器参数统一在`Plan View`配置。两者必须加载同一个`scene_map.json`和坐标合同，不能各自
维护地图图片、offset或轴向变换。

Fly小地图与Plan地图必须共用同一个`MoSimMapViewport`交互核心：

- 鼠标滚轮以当前指针位置为中心缩放，不得固定放大左上角；
- 左键拖动平移，`+/-`作为备用缩放入口；
- 限制最小/最大缩放并提供适配全图、跟随选中飞机和返回全机视图；
- 缩放、平移、全图适配不能改变world/pixel坐标合同；
- 小地图点击展开时保留中心与缩放上下文，返回后恢复小地图默认态势视角；
- QML上层、UE原生子窗口或QGC默认`FlightMap`不得吞掉地图滚轮和拖动事件。

在项目内权威PX4/QGC全局经纬度原点尚未确认前，地图允许静态显示和world/pixel审核，
但必须禁用MAVLink任务发布。不得用PX4常见SITL默认经纬度代替当前运行链证据。

## 8. 图层和视觉规则

| 图层 | 默认 | 视觉规则 |
| --- | --- | --- |
| Factory静态结构 | 开 | 中性低饱和底图，不与实时状态竞争 |
| Mission area | Plan View开；小地图关 | 半透明边界和轻填充 |
| Geofence | Plan View开；小地图仅告警时显示 | 明确实线；越界风险时高亮 |
| Keep-out | Plan View开；小地图关 | 红色斜纹或半透明填充 |
| 逐机位置/朝向 | 开 | 稳定颜色、编号、机头箭头、高度标签 |
| 实际轨迹 | 开 | 连续实线，可选全量或尾迹长度 |
| 未来预期轨迹/关键航点 | 开 | 只显示尚未执行的有效路径段；与实际轨迹可辨识并显示有效期 |
| 候选轨迹 | 关 | 仅工程模式或算法声明时开启 |
| 学习规划诊断 | 按算法 | 推理延迟、评分/置信、artifact hash、输入新鲜度和fallback |
| Frontier/Coverage | Plan View按能力；小地图关 | 统一图例、定义和统计边界 |
| Assignment/Formation | 按任务 | owner颜色、slot和连接关系 |
| 点云/占据投影 | 关 | 只作二维摘要，不替代RViz三维审核 |
| 告警/故障 | 事件触发 | 不闪烁整屏；定位到飞机和时间线 |

地图必须显示比例尺、北向/世界轴、当前frame、地图版本和数据新鲜度。二维地图不显示假的
三维高度；每架飞机通过高度数字、颜色带或高度剖面表达Z轴。

## 9. QGC复用与项目自有模块

### 9.0 复用原则与任务权威

QGC原生能力是第一选择。MoSim不重写航点列表、地图拖拽、Mission Item序列化、围栏、
Rally Point、MAVLink任务协议或逐项ACK。`MissionDraft`只在原生任务数据外增加地图/坐标合同、
ExperimentProfile、任务算法、车辆范围、安全约束、revision和证据字段。

Orchestrator是任务执行所有权的唯一协调者，但不是航迹规划器或MAVLink替代实现。它负责
校验当前run只存在一个任务authority，选择并授权Adapter，记录提交与ACK，并阻止QGC原生
Mission、ROS Planner和Formation Controller同时向同一车辆争夺控制。普通PX4任务仍走
QGC/MAVLink原生链；只有PX4无法表达的探索、覆盖和编队语义才由项目Adapter接入既有开源
算法。任何项目Adapter都应保持薄层兼容，不得复制上游规划器核心。

### 9.1 优先复用

```text
QGCCorePlugin / Custom Build
FlyViewCustomLayer / ToolStrip / toolbar indicators
MultiVehicleManager / MultiVehicleSelector
MissionController / GeoFenceController / RallyPointController
QGCMapPolyline / QGCMapPolygon / vehicle map item
Plan item list、拖动、插入、删除、撤销交互
VideoManager / 画中画和流健康
Fact System / 参数元数据和单位
MAVLink连接、状态和日志基础能力
```

### 9.2 项目自有

```text
apps/flight_console/mosim/custom/
  map/
    MoSimMapView.qml
    MoSimMiniMap.qml
    MoSimExpandedMap.qml
    layers/
    tools/
  mission/
    MissionDraftModel
    MissionDraftValidatorClient
    PX4MissionAdapter
    ExplorationPlannerAdapter
    CoveragePlannerAdapter
    FormationAdapter
  scene/
    SceneMapRegistryClient
    LocalMetricMapProvider
  fleet/
    MoSimVehicleModel
    TeamActionModel
  orchestration/
    现有MoSimOrchestratorBridge扩展
```

目标目录仅在实现真实源码时创建。项目自有层可以调用官方扩展点，但不能依赖对vendor源码的
临时补丁；若官方扩展点不足，先记录缺口、最小补丁和上游同步成本，再决定是否开放vendor patch。

## 10. 失败、降级与安全

- 二维地图加载失败：UE和runtime可以继续，任务编辑禁用，只允许打开已发布任务摘要；
- UE失败：二维地图与runtime继续，标记display degraded；
- Gazebo/ROS未连接、遥测过期、run不一致或frame/hash不匹配：隐藏飞机标记、实际轨迹和
  未来预期轨迹，显示明确失效原因；不得显示旧位置或继续外推；
- 坐标hash不一致：隐藏位置可能造成误导，禁止任务发布并显示具体版本；
- Planner未ready：草稿可以保存，发布或开始任务禁用；
- 部分多机ACK：显示逐机结果，团队动作整体不标记成功；
- QGC退出或重启：runtime不受影响，重启后按`run_id`重新附着；
- Orchestrator不可达：界面只读，不缓存危险命令等待恢复后自动发送；
- ROS、UE或RViz基础设施启动失败：仅自动重试一次并显示两次尝试结果，仍失败则等待人工处理；
- 代码生成、自动调参或任务执行失败：不自动重跑，保留失败上下文并等待人工确认；
- airborne后禁止自动重启任务或runtime，只允许悬停、降落或安全停止；
- UE录制默认关闭；录制失败不影响runtime，停止run前必须尝试flush并报告媒体证据状态；
- `关闭全部RViz`只终止当前MoSim拥有的RViz会话，并逐项显示关闭和残留检查结果；
- 未知探索缺少frontier/coverage：显示`not_available`，不得生成示意数据。
- 训练Backend不可达：训练按钮禁用，已注册经典规划与飞行功能不受影响；
- 深度相机Profile未通过：YOPO和FUEL深度路线禁用，MID360路线不自动替代其输入合同；
- 策略Schema/hash/归一化不匹配：禁止加载，显示期望值与实际值；
- 推理超时或候选轨迹无一通过校验：执行声明的回退规划器或安全悬停并记录结构化事件。

## 11. 实施阶段

### Q0 文档和上游审计

- 本文、总规划、地图注册和索引一致；
- 冻结官方QGC复用点、超维边界和外部项目取舍；
- 不改变D5已验收二进制和当前D6/D7主线。

### Q1 Factory静态任务地图

- 从已验收Factory资产生成栅格、矢量和变换；
- 抽出Fly小地图和Plan地图共用的`MoSimMapViewport`，在独立fixture验证鼠标中心滚轮缩放、
  平移、全图适配、图层和坐标往返；
- 三点、边界、比例尺、机头和hash门禁通过。

### Q2 只读运行态小地图

- 接入单机位置、朝向、飞行状态、高度、实际轨迹、未来预期轨迹和关键航点；
- 实现右上角mini、点击展开、跟随选中、全机适配；
- 断开Gazebo/ROS、超时、run不一致或坐标合同不匹配时隐藏全部动态对象；
- 再接入三机隔离、失效隐藏和逐机颜色；
- 只读通过后才开放任务编辑。

### Q3 单机任务编辑

- 目标点、航点、FUEL/Diff任务边界、Geofence、禁飞区、高度带和返航点；
- 第一版提供矩形和多边形边界，FUEL与Diff配置分别保存并由当前Planner Adapter消费；
- MissionDraft、撤销/重做、校验摘要和Orchestrator幂等提交；
- 同一Factory依次验证Waypoint、Diff、FUEL和known coverage合同。

### Q4 多机和编队任务

- 自动分配/逐机分配、团队ACK、最小间距和通信stale；
- 编队中心、slot、FormationReference和误差图层；
- 首版仅开放已验收三机，4至9机保持可见禁用。

### Q5 第二地图和扩展证明

- 新增城市或园区资产包和坐标合同；
- 不修改`MoSimMapView`核心页面完成地图切换；
- 室外地图再决定是否启用GeoTIFF/离线瓦片和ENU/WGS84转换。

### Q6 学习规划工作区与YOPO门禁

- 接入TrainingBackendRegistry、PolicyArtifactRegistry和学习规划器能力过滤；
- 先保持YOPO、Isaac和前向深度相机控件`visible_disabled`，验证原因与解锁动作显示；
- 深度相机、训练、导出、注册、推理Adapter和Gazebo验证逐门通过后再开放按钮；
- 验证YOPO当前/候选轨迹、延迟、artifact hash和fallback图层，不允许策略绕过轨迹校验器。

### 11.1 2026-07-18实施工作量基线

以下是基于当前约671行Flight定制QML、约1070行Plan定制QML、现有UE输入Pawn、
`WindowContainer`嵌入和Orchestrator骨架的有效工程工时估算。它包括定向自动测试和一次
人工审核，不把只画按钮或只显示静态示意图算作完成。

| 工作包 | 有效工时 | 验收边界 |
| --- | ---: | --- |
| UE嵌入方向键焦点和鼠标拖动环绕 | 5至10小时 | 嵌入前后`M/N`、方向键、鼠标环绕一致，且不抢QGC设置/飞行操作输入 |
| 小地图层级、尺寸、滚轮缩放和平移 | 4至8小时 | 小地图不挤占UE/原生面板，滚轮以指针为中心缩放 |
| Plan地图滚轮缩放、平移和共享视口 | 3至6小时 | 与小地图复用同一变换，不出现默认在线底图事件层干扰 |
| 飞机位置、方向、状态和失效隐藏 | 4至8小时 | 只显示当前run的新鲜状态；断连后按门限隐藏 |
| 实际轨迹、未来预期轨迹和关键航点 | 6至12小时 | 坐标一致、语义明确、无历史run残留 |
| Plan View矩形/多边形边界编辑 | 8至14小时 | 可绘制、修改、删除、校验、保存和恢复 |
| FUEL/Diff配置、任务序列化和Adapter接入 | 16至32小时 | 不是静态画框；边界和目标真正进入对应运行链并返回未来轨迹/状态 |
| 生命周期、取消/失败、回归和人工审核 | 10至18小时 | 无重复启动、旧会话、假ACK或断连残影 |

预计里程碑：

```text
FC-Q1  当前UE输入、布局和双地图缩放修复       1至2个工作日
FC-Q2  实时飞机状态、实际/未来轨迹完成         累计3至5个工作日
FC-Q3  Plan View边界与FUEL/Diff真实闭环        累计7至12个工作日
```

上述时间不包含重新解决FUEL或Diff算法本身的规划失败、控制器失稳、Gazebo性能或地图坐标
错误。若运行适配时暴露这些后端问题，必须单独形成blocker，不得通过前端模拟状态缩短工期。

## 12. UE原生子窗口与QGC浮层规则

第一版使用`WindowContainer`接管UE的Windows原生窗口。QGC设置抽屉、指示器抽屉或关键
消息弹窗出现时，UE容器必须暂时隐藏并把输入与Z序完全让给QGC；浮层关闭后再恢复同一个
UE会话，不能启动第二个UE进程。该规则防止UE覆盖QGC原生解锁、起飞、任务和设置界面。

键盘视角命令由Flight Console主窗口转发。鼠标拖动环绕只有在真实native子窗口输入测试
通过后才能验收；若QML事件层无法稳定接收输入，使用Qt事件过滤/native mouse capture，
不得通过提高QML `z`值绕过原生子窗口边界。

输入焦点合同固定为：

- 用户点击UE区域后，仅该区域获得相机输入焦点；`M/N`调整环绕距离，方向键调整环绕方向，
  按住鼠标拖动调整环绕视角；
- `Esc`或点击QGC面板释放UE鼠标捕获并把输入交还QGC；
- UE嵌入和受控外部窗口使用同一套相机语义，不能出现嵌入后只有`M/N`有效的半连接状态；
- 地图区域获得焦点时，滚轮只缩放地图，不能改变UE相机距离；
- 不允许全局事件过滤器吞掉QGC原生解锁、起飞、任务、设置和紧急操作。

Display session必须按`run_id`恢复且attach/detach幂等。重复Prepare/Attach不能留下多个
UE bridge或UE进程，GUI重启不得终止runtime。stale session的detach失败必须保留明确
reason code和残留PID证据，不能静默创建新session掩盖问题。

## 13. 完成定义

只有以下条件全部满足，才能宣称Flight Console二维任务地图完成：

1. Factory底图来自受控几何和校准，不是任意截图；
2. 单机和三机位置、朝向、轨迹与Gazebo/UE使用同一坐标合同；
3. mini、expanded plan和expanded monitor三态行为通过，Fly小地图不承担FUEL/Diff边界编辑；
4. 航点、任务区域、Geofence、禁飞区、高度和返航点可编辑、校验和持久化；
5. 地图操作生成结构化任务并由Orchestrator提交，不存在QML裸setpoint路径；
6. 未知探索无法读取完整operator display map；
7. 多机目标、分配、ACK、stale和失败按`vehicle_id`隔离；
8. 运行状态权限、悬停后改任务和紧急态锁定通过；
9. QGC退出、地图失败或UE失败不终止runtime和日志；
10. 至少一项单机任务和一项三机任务在同一Factory地图通过运行验收；
11. 第二张地图无需修改GUI核心即可接入，才证明地图接口可扩展；
12. QGC原生飞行控制得到复用，MoSim后台准备与QGC解锁/起飞/任务语义没有重复；
13. UE录制默认关闭且可显式开始/停止，全部MoSim RViz会话可一键关闭并完成残留检查；
14. 文档、源码、测试、证据、提交和推送满足项目closeout门禁。
15. UE嵌入前后相机输入语义一致，双地图滚轮缩放和平移通过，断连后不显示飞机或旧轨迹；
16. 实际轨迹和未来预期轨迹来自当前run真实数据，不使用静态示意线或历史run残留。
