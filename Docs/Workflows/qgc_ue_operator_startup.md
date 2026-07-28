# MoSim Flight Console 二维任务操作流程

> 当前入口：`cmd/启动MoSim地面站.cmd` 只启动 Flight Console/QGC，并默认显示
> Factory L2 二维底图。它不启动 UE、Gazebo、PX4、MAVROS、RViz、ROS 节点或
> Orchestrator。所有运行命令均由用户在一个可见终端执行。

本流程的目标是让操作者不依赖 Codex 或隐藏后台进程，也能看到每一步的命令、日志、错误和
停止信号。Flight Console 是操作和显示面，不是运行时编排器。

## 1. 启动地面站

1. 双击 `cmd/启动MoSim地面站.cmd`。
2. 等待 Flight Console 打开。Factory L2 二维底图、右侧操作页和原生 QGC 飞控工具应可见。
3. 没有活动 RunManifest 时，二维图只显示底图和任务草案，不显示飞机、轨迹或演示坐标。

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

任务已经降落、解除武装并结束后，在“任务”页复制“结束当前运行命令”，在同一个可见终端执行。
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

- Fly View 和 Plan View 共用 Map Registry 中的完整 Factory L2 底图；FUEL 64 m 区域仅作为
  任务叠层，不替代完整工厂边界。
- 飞机、航向、实际轨迹、预期/未来轨迹、任务边界和编队目标只消费同一 `run_id` 的权威
  `map_state`。无数据、身份不匹配或坐标契约未通过时必须隐藏动态元素。
- 需要实时二维态势时，运行 sidecar 的可见终端必须提供与本次冻结地图快照匹配的
  `--coordinate-evidence <路径>`。sidecar 只转换证据声明源 frame 的里程计和路径；缺少证据时
  QGC 只显示底图，源 frame 不匹配时显示“实时地图坐标系与证据不匹配”，但不会重启或干预飞控。
- Plan View 可编辑原生 QGC 航点和边界草案。Factory 世界坐标到地理坐标的往返门禁未通过前，
  禁止把 Upload 视为飞控任务发布或飞行执行。
- 新城市地图或其他楼层必须新增 Map Registry 条目和坐标契约；不得用截图、临时比例尺或 FUEL
  子区域替换 Factory L2。

## 4. rosbag 回放

1. 当前运行目录必须已有冻结的 `RUN_MANIFEST.json` 和 `operator_map_snapshot`。
2. 在可见终端执行 QGC “复制回放命令”生成的 `replay_rosbag_operator_map.py` 命令，并填写真实
   bag、里程计 topic 和坐标证据路径。
3. QGC 只轮询回放器写入的 `telemetry.json`，显示 `rosbag_replay` 状态和轨迹；它不会启动回放器。

回放可用于复盘、截图和二维态势审核，不得被标注为实时运行、控制器成功或规划器成功。

## 5. 故障与恢复

1. 在“故障”页选择飞机并设置风速或电机效率。滑块只生成 QGC 内存中的待应用值，不连续发送。
2. 点击“复制应用命令”，在可见终端执行。命令写入当前运行目录的故障请求文件。
3. 只有 ROS sidecar 或运行端返回同一 `run_id` 的 ACK、遥测和日志后，才能宣称故障已经生效。
4. “复制恢复正常命令”会生成风扰归零、四电机效率恢复 100% 的离散恢复请求。逐项 ACK 不完整时
   必须保留部分失败状态。

## 6. UE 与 RViz

UE 保持独立展示窗口，不嵌入 Flight Console，也不承担控制、地图或操作焦点。其鼠标进入后应能
通过 `Esc` 或失焦释放；该输入问题由独立 UE 路线处理。点云、栅格和 TF 的权威审核面仍是 RViz。

## 7. 停止与故障排查

1. 自动任务或自主探索异常时，首先使用其运行脚本的安全停止/降落路径；不要因为 QGC 没有刷新而
   重复启动第二个实例。
2. 手动任务使用 QGC 原生降落和解除武装后，在启动它的可见终端按 `Ctrl+C` 结束相关进程。
3. 保存运行终端日志、RunManifest、遥测和结果目录。若需全局清理，只使用经审核的
   `cmd/停止所有仿真.cmd`，并确认没有其他实验仍在运行。

## 8. 证据边界

QGC 的静态界面、地图、命令复制和 rosbag 回放只证明操作面/数据合同。运行成功必须由对应的
Gazebo、PX4、MAVROS、ROS、任务 Adapter、日志和结果包独立验收；MWORKS 控制器正确性仍由
MWORKS 模型、原生结果和代码生成一致性证据判定。
