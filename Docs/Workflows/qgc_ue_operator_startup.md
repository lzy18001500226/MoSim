# MoSim Ground Control 二维任务操作流程

> 当前入口：`Scripts/cmd/启动MoSim地面站.cmd` 只启动 MoSim Ground Control/QGC，并默认显示
> Factory L2 二维底图。它不启动 UE、Gazebo、PX4、MAVROS、RViz、ROS 节点或
> Orchestrator。所有运行命令均由用户在一个可见终端执行。

本流程的目标是让操作者不依赖 Codex 或隐藏后台进程，也能看到每一步的命令、日志、错误和
停止信号。MoSim Ground Control 是操作和显示面，不是运行时编排器。

## 1. 启动地面站

1. 双击 `Scripts/cmd/启动MoSim地面站.cmd`。
2. 等待 MoSim Ground Control 打开。Factory L2 二维底图、右侧操作页和原生 QGC 飞控工具应可见。
3. 没有活动 RunManifest 时，二维图只显示底图和任务草案，不显示飞机、轨迹或演示坐标。

启动入口会在最多 15 秒内检查主窗口是否出现。只有输出 `main window ready` 才表示地面站已启动；
若进程提前退出或超时未创建主窗口，入口会直接报错，不能将仅有 PID 的输出视为成功。

`Scripts/ui/run_qgc_with_ue.ps1` 是旧的 UE/Orchestrator 编排脚本，不属于当前默认流程，
不得作为比赛演示入口。

## 2. 选择并启动任务

1. 在“任务”页先选择控制器族和控制器，再选择已发布任务 Profile。控制器下拉框完整显示目录，
   但只有存在兼容已发布 Profile 的条目可选；未发布或未验收的条目保持可见并显示禁用原因。
   选择控制器只会绑定同一控制器已有的 Profile，不会临时组合控制算法。
2. 点击“复制启动命令”。QGC 会生成已审计的 PowerShell 或 WSL 命令，但不会执行它。
3. 打开或复用一个可见 PowerShell 终端，粘贴并执行该命令。保持该终端处于前台或易于查看的
   位置，直到任务结束。
4. 复制出的命令先在该可见终端运行 `prepare_operator_run.py`：它创建本次
   `Results/runs/<run_id>/RUN_MANIFEST.json` 并更新
   `Results/ui_platform/qgc_active_run.json`，随后才调用既有运行脚本。QGC 自动读取
   `run_id`、冻结 Profile，并禁止切换任务或再次复制启动命令。
5. 若运行时写入真实 `telemetry.json`，二维图才显示飞机、航向、实际轨迹、未来路径和任务边界。

每个命令都包含 Profile、控制器、机数、任务和运行入口元数据，并导出
`MOSIM_OPERATOR_RUN_ID`、`MOSIM_OPERATOR_RUN_DIR` 和
`MOSIM_OPERATOR_RUN_MANIFEST` 供后续运行端接入。准备清单或命令复制成功不表示 Gazebo、PX4、
MAVROS、控制器、规划器或飞行任务已经成功；以可见终端日志、后端 ACK 和结果包为准。

任务已经降落、解除武装并结束后，在“任务”页复制“清除运行清单命令”，在同一个可见终端执行。
该命令只将 QGC 活动指针标为已结束，不删除 RunManifest、遥测、故障请求或结果文件。

### 单机定点操纵

“单机定点操纵”只启动地面待命链路。飞机连接后使用 QGC 原生解锁、起飞、模式和降落功能。
控制器和任务 Profile 必须在起飞前选定；禁止空中切换。若后续启用 Position/WASD 操纵，它仍属于
QGC 原生飞控交互，不得与程控任务并行争抢控制权。

### 自动任务

单机 8 字、生成代码 8 字、FUEL 单机探索和三机固定编队分别由其已审计的自助运行脚本执行。QGC
只显示 Profile、地图状态、告警和原生飞控遥测。脚本或任务 Adapter 拥有自动任务的解锁、起飞、
执行、降落和安全停止语义；QGC 不额外发送竞争性控制指令。

## 3. Factory 二维地图与航点草案

- Map Registry 的 `default_map_id` 当前固定为 `factory_l2`。首次打开时先选择与默认地图兼容的
  已发布 Profile；后续新增城市或楼层地图时，只有显式登记的 Map/Profile 组合才可切换。
  Fly View 和 Plan View 共用完整 Factory L2 底图；FUEL 64 m 区域仅作为任务叠层，不替代完整工厂边界。
- 飞机、航向、实际轨迹、预期/未来轨迹、任务边界和编队目标只消费同一 `run_id` 的权威
  `map_state`。无数据、身份不匹配或坐标契约未通过时必须隐藏动态元素。
- 需要实时二维态势时，运行 sidecar 的可见终端必须提供与本次冻结地图快照匹配的
  `--coordinate-evidence <路径>`。sidecar 只转换证据声明源 frame 的里程计和路径；缺少证据时
  QGC 只显示底图，源 frame 不匹配时显示“实时地图坐标系与证据不匹配”，但不会重启或干预飞控。
- Plan View 可编辑原生 QGC 航点和边界草案。Factory 世界坐标到地理坐标的往返门禁未通过前，
  禁止把 Upload 视为飞控任务发布或飞行执行。
- Fly View 地图的“定位轨迹”只根据当前已接受的实际轨迹、任务路径和任务终点调整本地视口；“全图”
  恢复地图视野。两者都不启动命令、不发送飞控指令，也不改变任务发布门禁。
- 对保存的 QGC `Plan` 文件执行离线几何门时，在可见终端运行：
  `python Scripts/ui/validate_qgc_factory_waypoint_roundtrip.py --plan <Plan文件> --map-config Config/control_platform/operator_map_catalog.json --require-task-boundary --output <结果JSON>`。
  `status=offline_round_trip_passed` 只证明支持的 `SimpleItem` 全局航点、Home、Factory L2 边界和
  经纬度往返误差满足阈值；复杂任务项会被拒绝。即使通过，`mission_publication.allowed` 仍必须保持
  `false`，直到同一运行的地理锚点和坐标契约完成 runtime 验证。
- 新城市地图或其他楼层必须新增 Map Registry 条目和坐标契约；不得用截图、临时比例尺或 FUEL
  子区域替换 Factory L2。

### 在线航点显示审核夹具

需要审核 QGC 的在线路径叠加而不启动飞控时，在可见 PowerShell 中运行：

```text
.\Scripts\ui\start_qgc_online_waypoint_audit.ps1
```

该入口会为本次审核创建 `Results/` 内的独立活动指针，启动受控的只读 ROS1 发布器和 sidecar，并打开独立
QGC 实例。审核应确认 Factory L2 上同时出现任务预期路径和更新中的未来路径；结束时关闭夹具终端或按
`Ctrl+C`。它不启动 PX4、Gazebo、MAVROS 控制、任务上传或规划器验收，不能据此声称飞行或规划成功。

### 第一阶段：RViz 规划与 QGC 航迹显示

已发布的“RViz规划-QGC航迹显示（阶段一）”Profile 是阶段一的固定配置事实来源。操作者按
[阶段一人工测试教程](../Guides/qgc_rviz_phase1_manual_test_tutorial.md) 的独立 WSL 包装器启动同一条
ROS1/Gazebo/PX4/规划器/sidecar 运行；QGC 不选择 Profile、不复制启动命令，只显示同一 `run_id` 的
未来路径和实际轨迹。RViz 的 `2D Nav Goal` 是唯一目标输入，运行后端声明为 `rviz_2d_nav_goal`，
因此 QGC 的 `Plan Goal` 控件和实时目标桥不会在此阶段出现，避免把第二阶段输入混入第一阶段。

运行端达到就绪后会生成 `RVIZ_QGC_DISPLAY_PHASE1_MANUAL_TEST.json`，其中固定了 RViz 配置、目标 topic、
sidecar telemetry 和结果路径。操作者只需在 RViz 使用一次 `2D Nav Goal`，然后在 QGC 观察同一运行的
future path 与 actual track。自动产物可以核对 RViz topic、规划器输出和 sidecar 地图数据，但人工的 QGC
视觉观察仍须由操作者确认；这一步不证明 QGC 发起规划、飞行成功或控制器验收。

### 第二阶段：实时规划目标桥

已发布的“QGC实时目标单机规划闭环”Profile 才会显示并接受 `Plan Goal`；普通 8 字任务、手动定点任务、回放运行以及仅供诊断的 Diff-Planner Profile 都不会把它作为交付入口。当前源内的 Planner Adapter 仍是 Diff-Planner，这只是实现后端事实，不会把 QGC 输入、路径回显或本闭环的验收范围降格为“Diff 测试”。

QGC Plan View 中的 `Plan Goal` 是一条独立于原生 Mission Waypoint 草案的单点输入：操作者先复制并在
一个可见 WSL 终端运行实时目标桥命令，待 QGC 显示“实时目标桥接：就绪”后，在 Factory L2 图上点击一次。
QGC 只向当前 `run_id` 的 `operator_goal/REQUEST.json` 原子写入地图身份、经纬度和提交时间；它不上传
Mission、不调用 rosbag，也不直接发送 PX4、MAVROS 或电机命令。

目标桥使用 QGC 当前活动指针（不回退到其他 run），并必须同时核验该指针为 `running`、冻结 `RUN_MANIFEST.json` 和同一快照的
`OPERATOR_MAP_COORDINATE_EVIDENCE.json=status: verified`。通过后它把 QGC 的地理坐标转换为 Factory
世界坐标，并实时发布与 RViz `2D Nav Goal` 相同的
`geometry_msgs/PoseStamped` 到 `/move_base_simple/goal`。消息是地平面目标；运行中的规划器 Adapter
仍拥有目标飞行高度和后续重规划语义。

`forwarded` 仅表示桥看到该 ROS topic 的订阅者并已发布输入。实时规划的后续验收还必须在同一 `run_id`
观察到规划器的目标接收、更新后的未来轨迹/路径时间戳和运行日志；它不能由 QGC 页面、请求文件或 rosbag
回放代替。请求超过 5 秒、坐标契约不匹配、运行不再是 `running` 或没有规划器订阅者时，桥必须拒绝而不是
延迟回放旧目标。

RViz 的 `2D Nav Goal` 可作为一次性下游诊断：它和桥发布到同一 `/move_base_simple/goal`，因此能检查规划器输出是否能被 sidecar 写入并由 QGC 显示未来/实际轨迹。该检查不证明 QGC 的请求写入、桥接或地图点击；正式闭环必须再完成 QGC `Plan Goal` 的同运行验证。

## 4. rosbag 回放

1. 当前运行目录必须已有冻结的 `RUN_MANIFEST.json` 和 `operator_map_snapshot`。
2. 在可见终端执行 QGC “复制回放命令”生成的 `replay_rosbag_operator_map.py` 命令，并填写真实
   bag、里程计 topic 和坐标证据路径。若 bag 同时记录了 `nav_msgs/Path` 的任务预期路径或
   `visualization_msgs/Marker` 的 B-Spline 未来轨迹，显式补充 `--expected-path-topic` 和
   `--future-marker-topic`；未记录的字段保持隐藏，不能用手写坐标替代。
3. QGC 只轮询回放器写入的 `telemetry.json`，显示 `rosbag_replay` 状态、真实位置、实际航迹和
   已到达 bag 时间的任务路径；它不会启动回放器。

回放器把 Odom 与已录制的路径事件按 bag 时间合并成状态更新。`OPERATOR_MAP_REPLAY_MANIFEST.json`
中的 `frame_count` 是合并后的地图更新数，`odom_frame_count` 单独保留里程计帧数，避免把路径更新
误计为飞行遥测采样。

回放可用于复盘、截图和二维态势审核，不得被标注为实时运行、控制器成功或规划器成功。

## 5. 故障与恢复

1. 在“故障”页选择飞机并设置风速或电机效率。滑块只生成 QGC 内存中的待应用值，不连续发送。
2. 点击“复制应用命令”，在可见终端执行。命令写入当前运行目录的故障请求文件。
3. 只有 ROS sidecar 或运行端返回同一 `run_id` 的 ACK、遥测和日志后，才能宣称故障已经生效。
4. “复制恢复正常命令”会生成风扰归零、四电机效率恢复 100% 的离散恢复请求。逐项 ACK 不完整时
   必须保留部分失败状态。

## 6. UE 与 RViz

UE 保持独立展示窗口，不嵌入 MoSim Ground Control，也不承担控制、地图或操作焦点。其鼠标进入后应能
通过 `Esc` 或失焦释放；该输入问题由独立 UE 路线处理。点云、栅格和 TF 的权威审核面仍是 RViz。

当前构建只注册 `MoSimOperatorBridge`；历史 `MoSimOrchestratorBridge` 源码保留用于追溯，
但不在 CMake 源清单、插件注册或 QML 操作面中，不能作为地面站启动的必需依赖。

## 7. 停止与故障排查

1. 自动任务或自主探索异常时，首先使用其运行脚本的安全停止/降落路径；不要因为 QGC 没有刷新而
   重复启动第二个实例。
2. 手动任务使用 QGC 原生降落和解除武装后，在启动它的可见终端按 `Ctrl+C` 结束相关进程。
3. 保存运行终端日志、RunManifest、遥测和结果目录。若需全局清理，只使用经审核的
   `Scripts/cmd/停止所有仿真.cmd`，并确认没有其他实验仍在运行。

## 8. 证据边界

QGC 的静态界面、地图、命令复制和 rosbag 回放只证明操作面/数据合同。运行成功必须由对应的
Gazebo、PX4、MAVROS、ROS、任务 Adapter、日志和结果包独立验收；MWORKS 控制器正确性仍由
MWORKS 模型、原生结果和代码生成一致性证据判定。

## 9. 尚未执行的运行时验收清单

以下是后续单独开放运行时权限后才执行的清单，不是当前静态 UI 或 Windows 构建的完成声明。
每一项失败都保留当前终端、日志和 `run_id`，停止后续飞行操作，不通过重启隐藏进程规避错误。

| Gate | 操作者动作 | 必须观察到的证据 | 不得据此声称 |
| --- | --- | --- | --- |
| Q0 地面站独立启动 | 双击 `Scripts/cmd/启动MoSim地面站.cmd` | MoSim Ground Control/QGC 打开，显示 Factory L2 底图；没有自动启动 UE、Gazebo、ROS、PX4、MAVROS 或 RViz | 已连接飞机、已启动仿真或已生成 RunManifest |
| Q1 Profile 与地图 | 在 QGC 选择一个已发布 Profile，确认控制器、机数、任务和地图由同一条目派生 | 无活动运行时，图上只有底图和任务草案；禁用 Profile 不可选择并给出原因 | 控制器已加载、任务已开始或飞机已起飞 |
| Q2 运行准备 | 在 QGC 点击“复制启动命令”，由操作者在一个可见终端执行 | `Results/runs/<run_id>/RUN_MANIFEST.json` 与 `Results/ui_platform/qgc_active_run.json` 身份、Profile hash 和地图快照一致 | 后端 launcher、ROS、Gazebo、PX4、MAVROS、控制器或规划器已接受执行 |
| Q3 二维坐标门禁 | 由同一可见终端启动已绑定 run_id 的地图 sidecar，并提供匹配的坐标证据 | `map_state` 的 run/profile/map 快照一致且 `coordinate_contract_status=verified`；之后才可显示飞机、航向、实际/未来轨迹与边界 | 原生 QGC 航点已经发布到飞控 |
| Q4 rosbag 回放 | 在 QGC 复制回放命令，再由可见终端对真实 bag 执行 | QGC 显示 `rosbag_replay` 的播放/暂停/结束状态及同一 run_id 的派生几何 | 实时飞行、控制器成功或规划器成功 |
| Q5 原生飞控与任务 | 仅在 Sunray ROS1 运行时预检通过且该任务已明确授权后，使用 QGC 原生连接、解锁、起飞、模式和降落工具 | 可见 Gazebo/PX4/MAVROS 日志、车辆遥测和任务运行端日志同属一个 run_id；QGC 不发送竞争性第二控制链 | MWORKS 控制器已完成联合仿真或任意规划器已经通过 |
| Q6 故障与恢复 | 在活动 run 内暂存故障，复制并在可见终端执行应用/恢复命令 | 运行端或 sidecar 写回同一 run_id 的 ACK、当前生效值和失败原因；恢复 ACK 证明风扰归零、四电机效率为 100% | 命令复制或请求文件写入即代表故障已生效 |
| Q7 Plan View 发布 | 编辑航点或边界草案，并执行世界坐标与经纬度往返验收 | 未通过往返门禁时上传明确保持阻止；通过后才允许单独审核任务发布 | 二维底图或草案可见即代表飞控航点已发布 |
| Q8 UE 独立展示 | 仅在需要视频/展示且相关运行时已授权后单独打开 UE | UE 不嵌入 QGC；鼠标可通过 `Esc` 或失焦释放；其画面与 run bundle 对应 | UE 画面替代 Gazebo/PX4/MAVROS/RViz 的运行真值 |
| Q9-P1 RViz 规划与 QGC 显示 | 按阶段一人工测试教程的独立 WSL 包装器启动，在 RViz 使用一次 `2D Nav Goal`，并在 QGC 观察同一 run | `RVIZ_QGC_DISPLAY_PHASE1_MANUAL_TEST.json`、RViz adapter、规划器未来轨迹、sidecar actual track，以及操作者的 QGC 视觉确认 | QGC 发起规划、QGC `Plan Goal`、飞行或控制器验收 |
| Q9-P2 QGC 实时规划目标 | 启动已发布的 QGC 实时目标单机规划闭环，复制桥接命令后在 Plan View 选择 `Plan Goal` 并点击一次 | 同一 `run_id` 的 `STATUS.json=forwarded`、规划器更新后的未来路径/轨迹、sidecar 的实际轨迹和 QGC 地图显示 | 单独 RViz 目标、请求文件、桥接就绪状态或 QGC 截图即代表闭环、飞行或控制器验收 |

Q5 至 Q8 的控制、规划、避障、故障容错和显示结论分别由各自运行工作流的日志、指标和结果包
判定。一次 QGC 页面刷新、回放画面或 UE 视频都不跨越这些证据边界。

对已完成的单机 QGC run 及独立 Diff 评审包，可执行下列只读审计以生成单机、多机和 Diff
变体的并列矩阵：

```text
python Scripts/ui/audit_qgc_variant_acceptance_matrix.py --qgc-run-dir Results/runs/<run_id> --diff-review Results/sunray_ros1/<diff-review>/FACTORY_L2_C99_DIFF_SINGLE_AND_SWARM_REVIEW.json --output Results/ui_platform/qgc_variant_acceptance_matrix_<run_id>.json
```

该矩阵只比较 QGC 发布状态、实时传输证据与独立 ROS1 运行包；它不会将 Diff 的运行通过、
二维遥测文件或 QGC 截图升级为另一条控制、规划或 GUI 验收结论。
