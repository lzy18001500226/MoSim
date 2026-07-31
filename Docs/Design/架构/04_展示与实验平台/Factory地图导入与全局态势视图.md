# Factory地图导入与全局态势视图

> 状态：展示与实验平台专题设计，2026-07-01。
>
> 本文冻结第一张正式UE场景、Gazebo导入精度、前台窗口策略和UE全局姿态轨迹视图。

## 1. 冻结决策

当前第一张正式UE地图使用Factory。目标不是在Gazebo里重搭简化积木，而是从
Factory UE场景导出接近无损的静态地图，导入Gazebo作为后台物理/碰撞世界，
并用RViz和UE分别承担工程审核与展示。

2026-07-01人工确认的源场景：

```text
source_project: References/UnrealScenes/FactoryEnvironmentCollect/FactoryEnvironmentCollect.uproject
source_scene_id: local_factoryenvironmentcollect
source_map_package: /Game/Maps/Demonstration
renderer_project: UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject
renderer_map_asset: UE5/MoSimSceneLibrary/Content/Maps/Demonstration.umap
review_result: user visually confirmed this is the intended Factory scene
```

但Factory静态导入只解决Scene Base，不解决UE运行时数据进入问题。UE平台必须同时
具备Data Bridge：从ROS1/Gazebo/PX4/MAVROS/Sunray的run bundle或live topics读取
状态、姿态、轨迹和事件，驱动UE显示。没有Data Bridge的Factory导入只能算场景底座，
不能算UE展示系统完成。

冻结口径：

```text
scene_id: factory
static_import_level: L2
live_ue_truth: disabled
gazebo_gui_persistent_window: disabled
rviz_evidence: point cloud + occupancy/grid + TF + trajectory
ue_display: per-UAV third-person views + Global Overview attitude trails
human_review_required_after_L2_import: true
data_bridge_required_for_ue_runtime_display: true
first_review_surface: Gazebo only
first_review_priority: physical geometry and collision fidelity
visual_material_priority: low
planner_prior_map_access: forbidden
```

Gazebo GUI不再作为常驻展示窗口。Gazebo仍然保留后台物理、碰撞、传感器和PX4
运行职责；前台审核看RViz，前台展示看UE。

但第一版Factory导入审核先只看Gazebo中的静态物理地图：比例、通道、墙/柱/障碍物、
地面和出生点free-space。RViz点云/栅格、UE Global Overview和轨迹残影放到后续阶段。
Gazebo中的地图对SLAM/规划算法必须保持未知；算法只能通过传感器观测建图，不得读取
导入用的全局collision、semantic、occupancy或UE truth。

## 2. L2静态导入定义

Factory的L2导入必须至少包含：

| 项 | L2要求 | 不足时的状态 |
| --- | --- | --- |
| visual mesh | 来自已确认Factory UE源场景的真实静态网格或等价导出，不用手搭积木替代；材质可简化 | blocker |
| collision mesh | 分块导出的碰撞网格或足够接近的简化mesh；优先保证物理空间/障碍/通道接近无损；AABB/box proxy只能作L0/L1 smoke | blocker |
| semantic manifest | 至少区分floor/ground、wall、building、obstacle、start/goal、no-fly或review marker | blocker |
| coordinate contract | 明确UE cm到Gazebo/ROS m、轴向、origin、frame_id和单位转换 | blocker |
| alignment report | UE source、Gazebo world、collision mesh、PCD/occupancy bbox和起终点free-space检查 | blocker |
| review bundle | 导入后给用户审核的截图/视频/manifest，不直接声称接受 | review_required |

L2通过不等于完整最终地图验收；当前第一验收只表示Gazebo物理地图足以给用户审核。
正式运行证据仍需后续Gazebo/PX4日志、传感器输出、自主探索建图、轨迹和metrics。

## 3. 导入流水线

目标流水线：

```text
Factory UE source scene
  -> static mesh / collision mesh / semantic export
  -> coordinate and scale conversion
  -> Gazebo model/world assets
  -> ROS/RViz map artifacts: PCD, occupancy/grid, manifest
  -> alignment checker
  -> user review bundle
  -> accepted_factory_l2_scene_profile
```

执行原则：

```text
tool_first: true
scene_geometry_source: UE Factory source assets only
agent_script_role: orchestration, filtering, manifest, validation only
forbidden: hand-built scene geometry, manually invented obstacles, visual-only fake maps
```

优先使用官方或成熟工具链：

| 阶段 | 首选工具/资料 | 用途 |
| --- | --- | --- |
| UE场景导出 | Unreal glTF Exporter / Python scripting | 导出Level、Actor或Static Mesh资产；保留UE源资产链路 |
| 格式转换/减面/预览 | Blender headless Python；必要时再评估Assimp或meshoptimizer | 批处理导入、减面、材质代理、离屏预览和格式转换 |
| Gazebo装配 | Gazebo Classic model structure；SDFormat mesh/include规范 | `model.config`、`model.sdf`、`meshes/`、world include和SDF校验 |
| 第一版工程审核 | Gazebo GUI静态地图审核 | 证明物理地图比例、通道、障碍物和出生点free-space可信 |
| 后续工程审核 | RViz/PCD/occupancy/grid/TF/trajectory | 证明地图进入机器人审核面，不用Gazebo GUI截图替代RViz/日志证据 |

允许写项目脚本，但脚本只能编排上述工具、记录manifest、做路径/单位/坐标转换、
筛选已导出的UE对象、运行校验和产出证据。脚本不得自己发明厂房结构、障碍物布局或
可视语义；若官方/成熟工具链无法导出可用资产，应返回blocker并说明缺失工具或导出
限制，而不是手搓替代地图。

旧脚本中的AABB truth可以保留为诊断层，但不得作为L2完成证据：

```text
Scripts/UE5/export_unreal_scene_truth.py
  current truth_method: component_world_aabb_collision_proxy_v1
  allowed use: L0/L1 collision smoke, ROI planning debug, validation oracle prototype
  forbidden use: claim near-lossless Gazebo import or final Factory map acceptance
```

## 3.1 2026-07-01执行状态

本轮已经完成第一版Factory到Gazebo Classic的静态审核包生成，并在用户打开Gazebo
review world后完成Gazebo-only视觉接受。该接受只覆盖第一版静态物理地图底座，不覆盖
ROS/PX4/MAVROS/RViz、SLAM、planner、UE Data Bridge或控制器闭环；2026-07-02发现
该第一版包含非物理`SkySphereMesh`后，clean candidate必须重新走UE-only同源校准框人工审核，
不得直接继承第一版的接受结论。

可复用执行流程已经沉淀到：

```text
Docs/Workflows/ue_to_gazebo_static_scene_import.md
Docs/Skills/Unreal/ue-gazebo-static-scene-import/SKILL.md
```

本文只保留Factory专题设计、已验收证据和后续阶段边界；导出、转换、SDF校验、
Gazebo-only人工审核、scene profile提升和可逆Sunray入口步骤以workflow为准。

实际产物：

```text
UE source GLB:
  Results/unreal_scene_mapping/factory_l2_static_import/assets/local_factoryenvironmentcollect_level.glb

Blender chunked STL conversion:
  Results/unreal_scene_mapping/factory_l2_static_import/assets/chunked_stl/
  Results/unreal_scene_mapping/factory_l2_static_import/manifests/blender_chunked_stl_conversion.json

Gazebo Classic review bundle:
  Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/MANIFEST.json
  Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/VERIFICATION.json
  Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/worlds/factoryenvironmentcollect_l2_static_review.sdf
  Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/models/
  Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/screenshots/factory_l2_user_accepted_20260701.png

Sunray optional entry:
  Scripts/sunray/factory_l2_sunray_px4_gazebo.launch
  Config/gazebo/scene_profiles/factory_l2_static_sunray_scene.json
```

执行结论：

```text
source_geometry: UE GLTFExporter level GLB
gazebo_format: chunked STL models generated by Blender from the same GLB
chunk_count: 69
sdf_check: passed with Gazebo Classic / SDF 1.6
gazebo_process_probe: gzserver and gzclient ran on isolated GAZEBO_MASTER_URI=http://127.0.0.1:11391
x11_window_probe: xwininfo reported Gazebo mapped windows
gui_screenshot: user-provided Gazebo screenshot copied into project evidence
status: factory_l2_static_map_user_accepted
```

边界：

```text
not_claimed:
  - ROS/PX4/SLAM/runtime success
  - planner/localization acceptance
  - UE runtime display completion
  - spawn/free-space/sensor acceptance
```

下一步是在clean candidate通过后台源数据检查和UE-only同源校准框人工审核并提升为主Factory scene profile后，
再把它作为Sunray ROS1/Gazebo的入口使用，先做spawn/free-space和MID360/RViz传感器检查，
再进入自主探索、SLAM或UE Data Bridge。
不得把本轮Gazebo-only接受回写成运行闭环、定位、规划或UE展示系统完成。

## 4. 实时窗口策略

第一版不常驻显示Gazebo GUI：

| 窗口 | 是否常驻 | 用途 |
| --- | --- | --- |
| Gazebo GUI | no | 只在碰撞/模型装配诊断或人工要求时打开 |
| RViz | yes | 点云、累计点云、occupancy/grid、TF、轨迹、姿态审核 |
| UE per-UAV third-person | yes when display task is active | 每架飞机第三视角、视频素材、人工展示 |
| UE Global Overview | yes when display task is active | 全局姿态轨迹、轨迹残影、可选低频地图背景 |
| QGC/Web | optional | 模式、failsafe、Profile和人工操作入口 |

Gazebo后台卡顿或渲染窗口问题不能影响控制链路；Gazebo GUI截图不能替代RViz、
日志和metrics。

UE显示窗口也不能只靠静态地图验收。每个UE显示review bundle必须绑定
`mosim.ue_render_stream_manifest.v1`或等价manifest，说明输入run、topic/replay文件、
坐标转换、时间基准、车辆资产和claim boundary。没有manifest的UE截图或视频只能作为
临时观察，不能作为正式UE运行时展示证据。

## 5. UE Global Overview姿态轨迹

UE全局态势视图第一版只显示真实状态流驱动的姿态轨迹，不从视频里反推轨迹。

默认参数：

```text
update_rate_hz: 10
source: ROS1/PX4/MAVROS/Gazebo state or replay manifest
render_objects:
  - current UAV mesh per vehicle
  - attitude axes or heading marker per vehicle
  - configurable sampled trail / time-lapse trail per vehicle
  - color per vehicle
  - optional start/goal and event markers
```

轨迹采样/残影间隔必须可配置，参考
`References/Lab/visualization/visualize_uav_trajectory` 的参数思想，但不复用其视频帧差
作为实时轨迹来源：

| 参数 | 用途 |
| --- | --- |
| `trail_sample_interval_frames` | 每隔多少个10Hz状态帧追加一个轨迹节点 |
| `trail_max_points` | 每架飞机最多保留多少历史轨迹节点 |
| `trail_time_window_s` | 只显示最近多少秒轨迹，0表示全量 |
| `trail_alpha_start` / `trail_alpha_end` | 残影透明度渐变 |
| `trail_width_m` | 轨迹带宽或线宽 |
| `trail_color_profile` | 单机/多机颜色方案 |
| `show_attitude_axes` | 是否显示姿态坐标轴 |
| `show_body_mesh_at_samples` | 是否在采样点显示小机体姿态残影 |

`visualize_uav_trajectory` 的正式定位是后期素材工具：

```text
allowed:
  final recording -> time-lapse trajectory cover image/video
  report/PPT/demo video visual enhancement

forbidden:
  runtime pose source
  trajectory accuracy evaluation
  collision/planning/localization evidence
```

## 6. 点云/栅格与展示色彩

RViz中的点云和栅格是工程审核面。UE Global Overview可以后续消费同一份累计点云
或occupancy摘要做展示增强，但第一版不要求实时高密度点云进入UE。

Factory自主探索显示遵循“规划层有界、审核层可高上限累计”的规则：

```text
planner/internal map:
  FUEL/RACER内部地图按任务阶段设定有限box和resolution
  不因为RViz想看全局累计就把planner map设成无限

review accumulation:
  /mosim/goal4/livox_world_accumulated
  /mosim/goal4/occupancy_accumulated
  只服务RViz人工审核、metrics代理和展示素材

review source semantics:
  两个累计审核topic都来自同一份/uav1/livox_world世界点云
  点云窗口按0.08 m体素显示，栅格窗口按0.20 m boxes显示
  两者使用相同z范围和相同姿态/速度质量门禁，保证高度逐体素对应
  /sdf_map/occupancy_all仍是FUEL内部规划占据图，不冒充全高度审核地图
```

历史 Factory FUEL 单机探索审核入口已归档，不能作为当前支持入口：

```text
Scripts/cmd/Archive/legacy_unverified/启动Factory单机FUEL自主探索审核.cmd
Config/rviz/sunray_ros1_factory_fuel_pointcloud_review.rviz
Config/rviz/sunray_ros1_factory_fuel_grid3d_review.rviz
```

该历史入口曾默认同时启动Factory UE live mirror，并将FUEL随机采样种子固定为
`1`。UE只订阅`/uav1/mavros/local_position/odom`和`/position_cmd`：红线是
实际odom轨迹，绿线是规划命令轨迹；它不向ROS、PX4、MAVROS、FUEL或Gazebo
回写任何状态。可用`-NoUnreal`关闭UE，或用`-FuelRandomSeed -1`恢复FUEL的
`random_device`行为。固定种子只稳定FUEL内部随机采样序列，不能保证ROS调度、
传感器到达时序和每一帧轨迹完全相同。

推荐的短时审核命令：

```powershell
powershell -ExecutionPolicy Bypass -File Scripts/sunray/start_factory_fuel_single_exploration_review.ps1 -Foreground -ExplorationExecuteS 60 -FuelRandomSeed 1
```

运行证据目录应包含`ue_live_mirror_launch.json`、`ue_live_mirror_config.json`、
`ue_live_mirror.log`以及两个RViz日志；这些文件只证明显示链路已启动，不证明
FUEL覆盖率或完整自主探索成功。

默认显示策略：

| 窗口 | 默认内容 | 边界 |
| --- | --- | --- |
| 点云窗口 | live world cloud、累计world cloud、实际轨迹、执行命令轨迹、机体三轴 | 不显示局部B-spline、frontier、viewpoint或coverage叠加，避免将当前规划段误认为累计轨迹 |
| 栅格窗口 | 由world cloud实时体素化的累计非膨胀boxes、实际/命令轨迹、一条FUEL当前动态B-spline、机体三轴 | 不显示膨胀地图；FUEL内部occupancy只供规划，frontier/viewpoint/coverage仅作临时诊断层 |

默认可视尺寸为：红色实际轨迹`0.12 m`、绿色执行命令轨迹`0.09 m`、
青色FUEL当前B-spline约`0.08 m`。两个窗口的机体三轴都使用`0.60 m`长度、
`0.035 m`杆径、`0.10 m`箭头直径和`0.14 m`箭头长度，以便在Factory大地图
缩放下继续辨认当前位姿。

累计上限是显示压力测试参数。默认先用点云200万体素、栅格100万体素；若需要可将
`--max-accumulated-points`设为`0`做不裁剪压力测试。任何“不裁剪”结果都必须同时记录
运行时长、点数、RViz是否卡顿、日志是否丢帧和任务是否正常结束。

默认rosbag是审核回放包：记录累计点云、审核栅格、实际/命令轨迹、FUEL动态曲线、
机体三轴、TF、状态和时钟，不重复记录高带宽原始MID360与逐帧world cloud。只有
明确需要传感器离线诊断时才加 `-RecordRawSensorTopics`；此时必须检查
`rosbag record buffer exceeded`，出现丢帧不能称为完整原始传感器录制。

若实现UE全局点云展示，颜色规则必须写入manifest：

```text
height_colormap
semantic_colormap
occupancy_or_esdf_colormap
intensity_colormap
```

不得把后处理彩色点云图当作实时LiDAR原始点云，也不得把漂亮的UE/Open3D/
CloudCompare渲染图当作FAST-LIO或planner成功。

## 7. 验收和人工审核

L2静态导入第一版完成后必须先给用户做Gazebo-only审核：

```text
1. Factory UE源场景截图或资产清单；
2. Gazebo导入后的visual/collision/semantic manifest；
3. bbox/scale/origin/frame对齐报告；
4. Gazebo静态地图截图或短视频，重点看比例、墙/柱/障碍物、通道和出生点free-space；
5. 明确禁止声明：not final closed-loop, not localization/planner acceptance, not prior map access.
```

用户未审核前，只能标记为`factory_l2_import_review_required`，不能标记为
`factory_scene_accepted`。

2026-07-01本轮Gazebo-only审核已经通过，当前 durable evidence 是
`Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review/` 和
`Config/gazebo/scene_profiles/factory_l2_static_sunray_scene.json`。后续阶段可以进入
RViz/传感器/自主探索建图/UE展示，但必须重新产出对应层级的证据，不得回头改写第一版
物理地图验收含义。

## 8. 2026-07-02坐标清理状态

后续检查发现，第一版Gazebo静态导入把UE中的`SkySphereMesh`一起转成了Gazebo STL。
这个对象是天空/背景显示资产，不是物理厂房几何；它的缩放会把Gazebo全局mesh边界
污染到约`+/-16384 m`。因此，第一版F1-F8仍然是旧静态底座上的历史运行证据，但不能
作为“Factory全局坐标已经完全清理干净”的证据。

当前坐标合同保持不变：

```text
UE_X_cm = MWORKS_X_m * 100
UE_Y_cm = -MWORKS_Y_m * 100
UE_Z_cm = MWORKS_Z_m * 100

MWORKS_X_m = UE_X_cm / 100
MWORKS_Y_m = -UE_Y_cm / 100
MWORKS_Z_m = UE_Z_cm / 100
```

已生成clean candidate：

```text
clean_conversion:
  Results/unreal_scene_mapping/factory_l2_static_import/manifests/blender_chunked_stl_conversion_clean.json
clean_gazebo_review:
  Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/
clean_scene_profile:
  Config/gazebo/scene_profiles/factory_l2_static_sunray_scene_clean_candidate.json
coordinate_audit:
  Results/unreal_scene_mapping/factory_l2_coordinate_audit_20260702_104942/FACTORY_L2_COORDINATE_AUDIT.json
anchor_points:
  Results/unreal_scene_mapping/factory_l2_coordinate_audit_20260702_104942/factory_l2_anchor_points.csv
calibration_frame_review:
  Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/FACTORY_L2_CALIBRATION_FRAME_CONTRACT.json
landmark_review:
  Results/unreal_scene_mapping/factory_l2_landmark_review_20260702_111256/FACTORY_L2_LANDMARK_REVIEW.json
```

clean audit结论：

```text
status: passed
filtered_mesh_objects: SkySphereMesh
polluted_chunk_count: 0
UE collision truth bounds size: [1720.5291200000001, 844.60824, 228.63028] m
clean Gazebo chunk bounds size: [1720.5291137695312, 844.6082458496094, 228.6302719116211] m
```

门是否打开、车间外是否可飞，不再靠猜测决定。坐标层先用
`factory_l2_anchor_points.csv`中的世界原点、Factory AABB min/max/center、默认三机出生点
做数值审计；再把同源校准框、预期轨迹和实际轨迹镜像到UE，由用户只审核UE画面，
避免“起点错了但轨迹自洽”的问题。

仅有AABB、出生点、门、柱、机器等具名对象仍然不够证明UE地图正确映射到Gazebo地图：
语义对象有厚度，边界不好界定，且大地图里整体偏移不容易肉眼看出。因此主验收面改为
在默认`uav1`出生点附近塞入一套项目自定义的非对称三维标定架。该标定架不依赖
Factory建筑本身，由同一个JSON合同同时生成UE actor、Gazebo visual-only world、
RViz MarkerArray和CSV审核表。

```text
calibration_contract:
  Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/FACTORY_L2_CALIBRATION_FRAME_CONTRACT.json
segments_csv:
  Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/factory_l2_calibration_segments.csv
calibration_markers_csv:
  Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/factory_l2_calibration_markers.csv
gazebo_calibration_world:
  Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/worlds/factoryenvironmentcollect_l2_static_calibration_review.sdf
rviz_config:
  Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/rviz/factory_l2_calibration_frames.rviz
ue_placement_script:
  Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/ue/place_factory_l2_calibration_frames.py
rviz_marker_publisher:
  Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/ros/publish_factory_l2_calibration_frames.py
rviz_marker_topic:
  /mosim/factory_l2/calibration_frame_markers
```

标定架合同是唯一来源。默认原点为clean scene profile里的`uav1`出生点
`[0.0, 120.0, 0.2] m`，对应UE坐标`[0.0, -12000.0, 20.0] cm`。三面框为
XY/XZ/YZ矩形，X为红色、Y为绿色、Z为蓝色，并带有非对称正方向tick。标定块包括
白色原点块、红色`+X 1m`块、绿色`+Y 2m`块、蓝色`+Z 1m`块、紫色`[+2,+1,+0.5]`
三维偏移块和橙色`[-1,-1,+0.25]`负Y防镜像块。若UE与Gazebo/RViz存在原点偏移、
尺度错误、Y轴符号错误、XYZ轴交换、镜像或90/180度旋转，agent先从后台数据定位
问题；用户只需要在UE里看这套自塞标定架是否在预期位置、方向和尺度上成立。

具名landmark审核包降级为辅助参考：

```text
packet:
  Results/unreal_scene_mapping/factory_l2_landmark_review_20260702_111256/FACTORY_L2_LANDMARK_REVIEW.json
anchor_csv:
  Results/unreal_scene_mapping/factory_l2_landmark_review_20260702_111256/factory_l2_landmark_anchors.csv
gazebo_landmark_world:
  Results/unreal_scene_mapping/factory_l2_landmark_review_20260702_111256/worlds/factoryenvironmentcollect_l2_static_landmark_review.sdf
rviz_config:
  Results/unreal_scene_mapping/factory_l2_landmark_review_20260702_111256/rviz/factory_l2_coordinate_landmarks.rviz
rviz_marker_topic:
  /mosim/factory_l2/anchor_markers
```

这些landmark来自UE collision truth中的具名对象，不从Gazebo反推，包括东西两侧gate、
office door、混凝土柱、南侧column、售货机/回收机、楼梯、装配线角点、地面块和室外
hangar。它只能辅助解释场景，不再作为主坐标验收标准。

提升规则：

```text
1. clean candidate只表示源/静态坐标审计和SDF校验通过；
2. agent后台源数据检查通过、用户在UE中接受同源校准框/预期轨迹/实际轨迹之前，不替换主Factory scene profile；
3. 接受后再提升clean profile，并重跑最小runtime回归门：
   spawn/sensor -> takeoff-hover-land -> 单机/多机planner抽样；
4. 不允许用旧F1-F8直接声称clean地图下的完整闭环已经通过。
```
