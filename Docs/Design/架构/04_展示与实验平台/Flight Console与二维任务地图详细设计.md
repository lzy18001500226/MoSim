# MoSim Flight Console与二维任务地图详细设计

> 状态：产品与接口冻结设计，2026-07-17。
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
  run_id | Profile | 当前地图 | 任务 | Gazebo/PX4/MAVROS/定位/控制器 | 录制 | 急停

左侧
  预检 | 启动 | 解锁 | 起飞 | 开始/暂停任务 | 悬停 | 返航 | 降落

中央
  UE三维主视图
  -> 无飞机时自由视角
  -> 生成后默认环绕跟随
  -> 自由/环绕/跟随、飞机选择和距离调节彼此独立

右上角
  Factory二维任务小地图
  -> 飞机、朝向、目标、边界、实际/当前规划轨迹
  -> 点击展开完整任务地图

右侧
  逐机遥测 | 扰动/故障注入 | Safety/Failsafe | 请求值/实际值/ACK

底部
  事件时间线 | 告警 | 指标摘要 | 截图/录像 | 证据目录
```

点云RViz和三维栅格RViz保留为独立按钮，不常驻挤占UE或二维地图。地图、UE或RViz显示失败
只降低显示证据等级，不得阻塞控制和日志。

### 4.2 `MoSimMapView`三种状态

| 状态 | 用途 | 交互 |
| --- | --- | --- |
| `mini_monitor` | 右上角态势监视 | 选择飞机、全机适配、跟随、点击展开；禁止复杂编辑 |
| `expanded_plan` | 运行前任务与边界编辑 | 完整工具栏、图层、任务列表、属性编辑、校验和发布 |
| `expanded_monitor` | 飞行中二维监控 | 查看实时状态、规划、轨迹、告警；高风险编辑默认锁定 |

中央显示模式保留`UE 3D`、`2D Mission Map`和`UE + 2D split view`。小地图展开默认覆盖
中央区域而不是弹出第二个无管理窗口；需要对照时再使用split view。

### 4.3 快速实验、算法实验与学习训练

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

视觉风格可以像游戏小地图，但几何不可为美观随意变形。墙体、门和禁飞区需要高对比；
非任务装饰降低对比，避免与实时轨迹和告警争夺视觉层级。

### 7.2 坐标转换

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

### 7.3 最小校准门禁

- 三个非共线标定点在Gazebo、UE和二维地图中一一对应；
- 四角边界和至少一个内部地标对应；
- 已知长度比例尺误差通过门限；
- world-to-pixel-to-world往返误差通过门限；
- 飞机起点、机头方向和一段X/Y运动方向一致；
- QGC、UE、Gazebo使用同一`map_id/version/calibration_hash`；
- 地图超界、hash不一致或frame未知时禁止发布任务。

## 8. 图层和视觉规则

| 图层 | 默认 | 视觉规则 |
| --- | --- | --- |
| Factory静态结构 | 开 | 中性低饱和底图，不与实时状态竞争 |
| Mission area | 开 | 半透明边界和轻填充 |
| Geofence | 开 | 明确实线；越界风险时高亮 |
| Keep-out | 开 | 红色斜纹或半透明填充 |
| 逐机位置/朝向 | 开 | 稳定颜色、编号、机头箭头、高度标签 |
| 实际轨迹 | 开 | 连续实线，可选全量或尾迹长度 |
| 当前规划轨迹 | 开 | 与实际轨迹不同颜色/线型，显示有效期 |
| 候选轨迹 | 关 | 仅工程模式或算法声明时开启 |
| 学习规划诊断 | 按算法 | 推理延迟、评分/置信、artifact hash、输入新鲜度和fallback |
| Frontier/Coverage | 按能力 | 统一图例、定义和统计边界 |
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
- 遥测过期：飞机标记变为stale并停止外推，不保持绿色最后值；
- 坐标hash不一致：隐藏位置可能造成误导，禁止任务发布并显示具体版本；
- Planner未ready：草稿可以保存，发布或开始任务禁用；
- 部分多机ACK：显示逐机结果，团队动作整体不标记成功；
- QGC退出或重启：runtime不受影响，重启后按`run_id`重新附着；
- Orchestrator不可达：界面只读，不缓存危险命令等待恢复后自动发送；
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
- 在独立地图fixture验证缩放、平移、图层和坐标往返；
- 三点、边界、比例尺、机头和hash门禁通过。

### Q2 只读运行态小地图

- 接入单机位置、朝向、高度、实际轨迹和目标；
- 实现右上角mini、点击展开、跟随选中、全机适配；
- 再接入三机隔离、stale和逐机颜色；
- 只读通过后才开放任务编辑。

### Q3 单机任务编辑

- 目标点、航点、任务区域、Geofence、禁飞区、高度带和返航点；
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

## 12. 完成定义

只有以下条件全部满足，才能宣称Flight Console二维任务地图完成：

1. Factory底图来自受控几何和校准，不是任意截图；
2. 单机和三机位置、朝向、轨迹与Gazebo/UE使用同一坐标合同；
3. mini、expanded plan和expanded monitor三态行为通过；
4. 航点、任务区域、Geofence、禁飞区、高度和返航点可编辑、校验和持久化；
5. 地图操作生成结构化任务并由Orchestrator提交，不存在QML裸setpoint路径；
6. 未知探索无法读取完整operator display map；
7. 多机目标、分配、ACK、stale和失败按`vehicle_id`隔离；
8. 运行状态权限、悬停后改任务和紧急态锁定通过；
9. QGC退出、地图失败或UE失败不终止runtime和日志；
10. 至少一项单机任务和一项三机任务在同一Factory地图通过运行验收；
11. 第二张地图无需修改GUI核心即可接入，才证明地图接口可扩展；
12. 文档、源码、测试、证据、提交和推送满足项目closeout门禁。
