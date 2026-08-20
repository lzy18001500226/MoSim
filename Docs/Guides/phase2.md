# 阶段二：QGC 多航点实时规划闭环人工测试

> 本流程按多终端操作组织。命令行只负责启动运行时、自动起飞并保持悬停；航点由操作者在 QGC 中手动规划和提交。

## 1. 测试边界

- Profile：`QGC实时目标单机规划闭环`
- Profile ID：`px4ctrl_graphical_c99_factory_qgc_realtime_goal_v1`
- ROS1 输入：`/move_base_simple/goal`
- QGC 入口：Plan View 的 `Submit Waypoints`
- 不使用 QGC 原生 Mission Upload，不由 QGC 发送起飞、降落或电机命令。
- 不打开 RViz 和 UE；本流程只审核 QGC 地图、规划器未来轨迹和实际轨迹。
- QGC 请求、桥接转发、规划器接受和车辆运动是四类不同证据，不能用截图相互替代。

## 2. 终端分工

从全关状态开始，打开四个可见 PowerShell 窗口，再打开一个 QGC 窗口：

| 窗口 | 只负责什么 | 结束方式 |
| --- | --- | --- |
| QGC | 手动画航点、点击 `Submit Waypoints`、观察地图 | 关闭 QGC |
| Terminal 1 Runtime | 启动 ROS/Gazebo/PX4/MAVROS/规划器，自动起飞并保持悬停 | 最后按 `Ctrl+C` |
| Terminal 2 Bridge | 读取同一 `run_id` 的 QGC 请求并逐点发布 ROS1 目标 | `Ctrl+C` |
| Terminal 3 Telemetry | 写入同一 `run_id` 的未来轨迹和实际轨迹 | `Ctrl+C` |
| Terminal 4 Evidence | 只读查看状态和日志，不发送控制命令 | 关闭窗口 |

不要把下面命令拼成一条长命令，也不要在 Terminal 1 中手工再启动 Bridge 或 Telemetry。

## 3. 启动顺序

### 3.1 打开 QGC

在一个独立 PowerShell 中执行：

```powershell
Set-Location C:\Users\HP\Desktop\MoSim
.\Scripts\cmd\启动MoSim地面站.cmd
```

QGC 只打开显示和操作面，不会启动 ROS、Gazebo、PX4、MAVROS 或规划器。

### 3.2 Terminal 1：运行时、起飞、悬停

在 Terminal 1 执行下面这一条命令，保持窗口可见：

```powershell
Set-Location C:\Users\HP\Desktop\MoSim
wsl.exe -d Ubuntu-20.04 --exec bash -lc "cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/start_qgc_realtime_manual_backend.sh"
```

等待终端同时出现以下事实：

```text
Runtime backend is ready: takeoff and hover are complete.
Manual QGC planning is separate; start the bridge and telemetry terminals now.
```

这表示运行时已完成起飞和悬停保持，不表示任何航点已提交、规划器已接受或飞行任务已完成。

### 3.3 Terminal 2：单独启动 Bridge

在 Terminal 2 执行：

```powershell
Set-Location C:\Users\HP\Desktop\MoSim
wsl.exe -d Ubuntu-20.04 --exec bash -lc "cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/start_qgc_realtime_manual_bridge.sh"
```

看到 `QGC bridge terminal attached to run qgc-...` 后，该窗口只保留请求校验和 ROS1 目标发布。

### 3.4 Terminal 3：单独启动 Telemetry

在 Terminal 3 执行：

```powershell
Set-Location C:\Users\HP\Desktop\MoSim
wsl.exe -d Ubuntu-20.04 --exec bash -lc "cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/start_qgc_realtime_manual_telemetry.sh"
```

看到 `QGC telemetry terminal attached to run qgc-...` 后，等待 QGC 地图出现同一运行的飞机状态和底图状态。

### 3.5 Terminal 4：只读观察

等 Terminal 1、2、3 就绪后，在 Terminal 4 执行：

```powershell
Set-Location C:\Users\HP\Desktop\MoSim
$active = Get-Content -Raw Results\ui_platform\qgc_active_run.json | ConvertFrom-Json
$runId = $active.run_id
$request = Get-Content -Raw "Results\runs\$runId\operator_goal\REQUEST.json" -ErrorAction SilentlyContinue | ConvertFrom-Json
$status = Get-Content -Raw "Results\runs\$runId\operator_goal\STATUS.json" -ErrorAction SilentlyContinue | ConvertFrom-Json
[pscustomobject]@{
    run_id = $runId
    active_state = $active.state
    request_waypoint_count = if ($request) { @($request.waypoints).Count } else { 0 }
    bridge_state = if ($status) { $status.state } else { 'waiting_for_bridge' }
    forwarded_waypoint_count = if ($status) { $status.details.forwarded_waypoint_count } else { 0 }
}
```

这条命令只读文件，不会向 ROS、PX4、MAVROS 或 QGC 发送任何操作。

## 4. 手动规划和提交

Terminal 1 报告悬停、Terminal 2 报告 bridge 已连接、Terminal 3 已开始写遥测后，在 QGC 中操作：

1. 进入 Plan View，确认显示 Factory L2 地图。
2. 选择 `Waypoint`，在任务边界内手动添加至少 3 个普通航点。
3. 检查每个航点的顺序和高度。
4. 点击一次 `Submit Waypoints`。

提交前覆盖层会将普通航点重编号为连续的 `1..N` 协议序列，避免 QGC 原生序列中的起飞项或其他非航点项导致首个航点被跳过。

预期观察顺序：

1. QGC 显示本次航点数量和橙色原始航点路线。
2. Bridge 的 `STATUS.json` 先显示请求身份，再显示 `forwarded_waypoint_count` 递增。
3. 任务节点在每个航点之间重新报告 `mission_ready`。
4. QGC 地图中的蓝色未来轨迹和绿色实际轨迹更新。

不要在上一条航点序列完成前再次提交新序列。不要点击 QGC 原生 Upload、Arm、Takeoff、Land 或切换飞行模式。

## 5. 结果检查

在同一个 Terminal 4 中重新读取：

```powershell
$status = Get-Content -Raw "Results\runs\$runId\operator_goal\STATUS.json" | ConvertFrom-Json
$telemetry = Get-Content -Raw "Results\runs\$runId\telemetry.json" | ConvertFrom-Json
[pscustomobject]@{
    run_id = $runId
    bridge_state = $status.state
    forwarded_waypoint_count = $status.details.forwarded_waypoint_count
    next_waypoint_sequence = $status.details.next_waypoint_sequence
    telemetry_run_id = $telemetry.run_id
    future_path_state = $telemetry.map_state.task_paths.future.status
    actual_track_state = $telemetry.map_state.actual_tracks.uav1.status
}
```

只有在以下身份和链路都相同的时候，才记录为一次有效的人工测试：

- QGC 请求、活动指针、运行清单和 `STATUS.json` 使用同一个 `run_id`；
- `forwarded_waypoint_count` 等于桥接器生成的航点数；
- 任务节点有逐点 handoff；
- 规划器有未来轨迹和 position command；
- sidecar 写出了同一运行的实际轨迹；
- QGC 视觉观察由操作者单独记录。

这些条件仍然只证明这条人工规划运行链路，不等于 MWORKS 控制器性能、完整规划器验收或真实飞行成功。

## 6. 停止顺序

1. 在 QGC 中先使用已经授权的安全降落和解除武装路径。
2. Terminal 2 按 `Ctrl+C` 停止 Bridge。
3. Terminal 3 按 `Ctrl+C` 停止 Telemetry。
4. Terminal 1 最后按 `Ctrl+C`，由 Runtime 终止同一运行的 ROS/Gazebo/PX4/MAVROS/规划器进程。
5. 确认 Terminal 1 已退出后，在 Terminal 4 清除活动指针：

```powershell
wsl.exe -d Ubuntu-20.04 --exec bash -lc "cd /mnt/c/Users/HP/Desktop/MoSim && python3 Scripts/ui/prepare_operator_run.py --clear-active"
```

若任一终端报错，保留该终端输出、`run_id`、`RUN_MANIFEST.json`、`QGC_REALTIME_GOAL_RUNTIME_STATUS.json`、`operator_goal/STATUS.json` 和 `telemetry.json`，不要并行启动第二套运行。
