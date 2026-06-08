# UE/ROS2 参考栈合同摄取审计

生成时间：2026-06-09 CST

执行边界：本轮只做本地静态 source-first 审计，不派发工程任务，不重启秘书部，不触碰 MWORKS/ROS2/UE live runtime，不修改主线 workflow 文档。

## 一句话结论

你的判断是对的：本地爬取的 AirSim、RflySim、PX4/mavros-ros2、FAST-LIO 家族、SUPER/ROG map、UnrealCV 里已经有大量 UE 渲染、ROS2 topic/frame、planner setpoint、Mid360/FAST-LIO、command/status echo 模式。MoSim 不应该重复手写一套孤立的渲染/ROS2 机制。

但可复用的重点不是把这些项目直接作为 MoSim runtime，而是先冻结一批小合同：

1. UE 发出 operator intent，不直接改 UAV pose 或判定控制成功。
2. MWORKS/ROS2 adapter 必须 accept/reject/timestamp/echo。
3. ROS2 必须以真实 topic、TF、Livox/FAST-LIO 输出、RViz review 作为证据。
4. MWORKS 仍是 dynamics/controller/truth/metrics authority。

## 本轮证据样本

| 参考族 | 本地证据 | 可复用点 | 摄取判断 |
|---|---|---|---|
| AirSim ROS wrapper | `References/AirSim/AirSim/docs/airsim_ros_pkgs.md` | GPS、odom、camera、IMU、LiDAR `PointCloud2`、takeoff/land/reset、NED/ENU 参数 | adapt |
| AirSim Offboard API | `References/AirSim/AirSim/AirLib/include/vehicles/multirotor/firmwares/simple_flight/firmware/OffboardApi.hpp` | `requestApiControl` gate、goal timestamp、timeout hover、arm/disarm 状态机 | adapt |
| ProjectAirSim topic system | `References/AirSim/ProjectAirSim/client/cpp/AirSimClientDLL/src/Topics.cpp` | `/$topics` discovery、subscribe/unsubscribe、callback token invalidation | reference_only -> adapt later |
| UnrealCV command server | `References/AirSim/unrealcv-5.2/Source/UnrealCV/Private/Server/*.cpp` | URI-style command binding、handler registry、game-thread execution、request/reply status | adapt |
| UnrealCV sensors/views | `References/AirSim/unrealcv-5.2/Source/UnrealCV/Public/Sensor/CameraSensor/*.h` and `.../PlayerViewMode.cpp` | lit/depth/normal/optical_flow/object_mask/wireframe 等 sensor-oracle/review mode | adapt |
| PX4 mavros-ros2 | `References/PX4/mavros-ros2/...` | ROS2 Humble+ support、OFFBOARD、PositionTarget、State mode/armed/connected | adapt |
| FAST-LIO Mid360 | `References/Lab/FAST_LIO/config/mid360.yaml` and `src/laserMapping.cpp` | `/livox/lidar`、`/livox/imu`、Livox `CustomMsg`、`/cloud_registered`、`/Odometry`、`/path` | adopt contract, adapt runtime |
| SUPER planner/map | `References/Lab/SUPER/...` | ROS2 `PositionCommand`、`/planning/pos_cmd`、`/lidar_slam/odom`、PointCloud2 local/global map、`map_ego` TF | adapt |
| RflySim APIs | `References/RflySim/RflySimAdv3Full/.../RflySimAPIsPers.zip` | process split、inCtrlExt、parameter/fault/dynamic injection pattern | adapt/reference_only |

## 推荐优先合同队列

### P0-1 CommandStateEchoContract

目标：统一 UE console -> MWORKS/ROS2 adapter -> authoritative echo。

建议 owner：UE + MWORKS R1 + ROS2 R1，PMO 做合同验收。

最小字段：

- `run_id`, `seq`, `time_s`, `requested_by`
- `command.kind`, `command.payload`
- `guard.require_mworks_ack`
- `guard.require_ros2_ack`
- `reject_if_gate_open`
- `echo.accepted`, `echo.reason`, `echo.active_state`, `echo.evidence_level`

验收重点：

- UE 只能显示 echo 后的 accepted state。
- 任何 planner/perception/controller 成功都必须来自 MWORKS/ROS2 evidence。
- 禁止 `pose_override`、`teleport`、`actor_transform`、`keyboard_pose` 作为控制路径。

### P0-2 ROS2FrameTopicContract

目标：先冻结 ROS2 topic/frame 命名，再做 runtime gate。

建议 owner：ROS2 R1。

候选输入/输出：

- LiDAR input：`/livox/lidar` 或 MoSim adapter 映射后的等价 topic。
- IMU input：`/livox/imu` 或 MoSim adapter 映射后的等价 topic。
- FAST-LIO outputs：`/cloud_registered`、`/Odometry` 或当前 ROS2 candidate 的 `/odometry`、`/path`。
- Planner command：`mars_quadrotor_msgs/msg/PositionCommand` 风格或本地等价 setpoint。
- Frame：必须明确 `map/odom/base/imu/lidar` 关系，不能用 replay odometry 伪装 FAST-LIO 输出。

### P0-3 Mid360FastlioInputContract

目标：把 Mid360/Livox 的消息字段和时间语义写死，防止后续只做 `PointCloud2` display。

建议 owner：ROS2 R1 + UE sensor adapter。

必须保留：

- per-point offset time
- `x/y/z`
- intensity/reflectivity
- line/ring
- tag
- frame id
- monotonic timestamps
- explicit LiDAR/IMU extrinsics

验收重点：`/cloud_registered`、odometry、path 必须来自真实 FAST-LIO-family runtime；静态点云或 `/mosim/replay_odometry` 只能做 review/reference。

### P0-4 UESensorOracleContract

目标：把 UE 的 camera/depth/normal/segmentation/collision oracle 作为 sensor/review source，而不是 controller truth。

建议 owner：UE。

可复用 UnrealCV 模式：

- command handler registry
- camera sensor components
- depth/normal/object mask/optical flow view modes
- request/reply status
- game-thread execution约束

验收重点：UE 可输出图像、depth、mask、collision oracle；不能给 planner 偷喂完整全局真值地图。

### P0-5 PlannerSetpointContract

目标：把 planner 输出冻结成 MWORKS 可消费的 setpoint stream，而不是直接替换 plant/control。

建议 owner：ROS2 R1 + MWORKS R1。

参考：SUPER `PositionCommand`、PX4/mavros `PositionTarget`、AirSim local goal services。

验收重点：

- 20Hz setpoint/command stream。
- stale-command timeout。
- invalid localization fallback。
- mode/armed/connected/valid-odom 等 state echo。

### P1 SceneRunIdentityContract

目标：把 `scene_source_id / scene_id / map_id / run_id` 贯穿 UE、MWORKS、ROS2、Results。

建议 owner：UE + PMO。

验收重点：UE map visible 不等于 scenario accepted；只有 MWORKS scenario、ROS2 topic contract、truth artifacts、Results path 都绑定并 echo 后才算 scene switch 有效。

## 版本风险处理

采用四级复用策略：

| 决策 | 适用场景 | 本轮例子 |
|---|---|---|
| adopt | 消息字段/合同语义与 MoSim 目标直接吻合，或迁移成本极低 | Livox/Mid360 input fields、FAST-LIO output names as contract |
| adapt | 设计模式正确，但需要 ROS1->ROS2、UE 版本、项目命名、权限边界迁移 | UnrealCV command server、AirSim offboard timeout、PX4 offboard state |
| reference_only | 只能作为架构或产品流程参考，不能进入当前 runtime | RflySim process split、ProjectAirSim topic registry |
| reject | 会抢走 MoSim truth authority、引入不合适 runtime、或制造伪证据 | 直接采用 AirSim runtime、ROS1 FAST-LIO 当 ROS2 runtime、RflySim 参数当 Sunray150 truth |

## 应避免的重复工作

1. 不再手写临时 ROS2 topic 命名。先以 AirSim/PX4/SUPER/FAST-LIO 合同为基线，缺口再写 adapter。
2. 不再把 UE console 做成直接操控 actor 的游戏 UI。先实现 command/reject/echo。
3. 不再用浏览器/HTML 点云替代 RViz/FAST-LIO。ROS2/RViz 是 review authority。
4. 不再自己发明 LiDAR 字段。Mid360/Livox CustomMsg 和 FAST-LIO input 是优先参考。
5. 不再把 RflySim/CopterSim 参数直接搬到 MWORKS。RflySim 只提供结构、故障/参数注入、流程分层参考。

## 建议下一轮派发

在秘书部恢复前，可以由 PMO 或 CoAgentOps 将以下低风险 static/source-static 任务派发给活跃工程线程：

1. UE：冻结 `UECommandServerPattern` 与 `UESensorOracleContract` 的 source-static checklist，不跑 UE runtime。
2. ROS2 R1：冻结 `ROS2FrameTopicContract` + `Mid360FastlioInputContract`，只读本地 reference/source，不开 RViz/FAST-LIO runtime。
3. MWORKS R1：把 AirSim/RflySim actuator/offboard timeout/fault-injection 模式转成 MWORKS wrapper 设计草案，不跑 check_model/SimulateModel。
4. PMO：把 `CommandStateEchoContract` 作为跨层验收合同，要求后续 UE/ROS2/MWORKS return packet 都声明是否只完成 source/static 或 runtime evidence。

## 需要用户确认

1. 是否允许把本次矩阵中的 P0 合同提升为正式 workflow patch。当前主线 workflow 文档正在重构，本轮没有修改。
2. FAST-LIO 路线是否继续优先 ROS2 native candidate，而不是 ROS1 container/bridge。
3. UE sensor oracle 是否先做 camera/depth/mask，再做 LiDAR/collision oracle。
4. 是否接受 `SceneRunIdentityContract` 作为 UE console 下一批 UI/adapter 工作的前置门禁。

## 本轮未声明

- 未声明 UE runtime 已启动或 renderer 完成。
- 未声明 ROS2/FAST-LIO runtime 当前可用。
- 未声明 MWORKS check_model、SimulateModel、closed_loop 或 controller performance。
- 未声明 AirSim/RflySim/PX4/SUPER 任一 runtime 可直接替代 MoSim。
- 未修改主线 workflow 文档。
