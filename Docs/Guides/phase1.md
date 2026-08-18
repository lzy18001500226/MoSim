# Factory L2 阶段一从零可执行教程：RViz 目标到 QGC 航迹显示

> 本教程只做一件事：用 RViz 发送一次 `2D Nav Goal`，然后在同一个 QGC 窗口观察该运行的 future path 和 actual track。
> 阶段一不使用 QGC `Plan Goal`，不上传任务，不解锁，不起飞，也不把 QGC 画面当成控制器或飞行验收。

## 0. 先确认入口

本教程只使用一个阶段一运行入口：

```text
Scripts/sunray/start_factory_l2_rviz_qgc_phase1.sh
```

它会固定使用以下已发布 Profile，并自动加载 RViz 配置：

```text
profile_id: px4ctrl_graphical_c99_factory_rviz_qgc_display_phase1_v1
runtime_profile_id: sunray_ros1_factory_l2_graphical_px4ctrl_c99_rviz_qgc_display_phase1_v1
rviz_config: Config/rviz/sunray_ros1_goal4_diff_realtime_combined_review.rviz
```

不要先手工启动 Gazebo、PX4、MAVROS、规划器或 RViz，也不要直接把 `.rviz` 文件路径粘贴到 PowerShell。

本教程需要使用 `Ubuntu-20.04 / ROS1 Noetic / Gazebo Classic`。不要替换成裸 `wsl`、Ubuntu-22.04 或 ROS2。

## 1. 你要打开的窗口

从全关状态开始，需要下面四个窗口：

| 窗口 | 用途 |
| --- | --- |
| PowerShell 1 | 清理旧运行、预检和读取状态 |
| PowerShell 2 | 启动并保留 QGC 显示窗口 |
| PowerShell 3 | 前台运行阶段一 WSL 启动命令，不能关闭 |
| QGC / MoSim Ground Control | 观察 Factory L2 地图和航迹 |

PowerShell 1 和 2 可以是两个标签页。PowerShell 3 必须保持在前台，因为它显示阶段一启动日志；
运行端自动启动 RViz，不需要再开第四个 ROS/RViz 终端。

## 2. 第一步：从零清理旧运行

在新的 **Windows PowerShell** 中执行：

```powershell
Set-Location C:\Users\HP\Desktop\MoSim

$activePath = Join-Path (Get-Location) 'Results\ui_platform\qgc_active_run.json'
if (Test-Path -LiteralPath $activePath) {
    $active = Get-Content -LiteralPath $activePath -Raw | ConvertFrom-Json
    [pscustomobject]@{
        state = $active.state
        run_id = $active.run_id
        source = $active.source
        reason = $active.terminal_reason_code
    }
} else {
    'No qgc_active_run.json exists'
}

Write-Output '--- Gazebo master port 11345 ---'
wsl.exe -d Ubuntu-20.04 --exec bash -lc "ss -ltnp | grep -E ':11345$' || true"

Write-Output '--- possible Phase 1 processes ---'
wsl.exe -d Ubuntu-20.04 --exec bash -lc "ps -eo pid,ppid,args | grep -E 'gzserver|px4|mavros|rviz|run_qgc_diff_realtime_goal_gate|run_px4ctrl_ego_single_gate' | grep -v grep || true"
```

### 2.1 如果终端还在

如果 `qgc_active_run.json` 的 `state` 是 `running` 或 `launch_prepared`，回到该运行的 PowerShell 3，
只按一次 `Ctrl+C`，等待它返回 PowerShell 提示符。不要启动第二次，也不要手工删活动指针。

### 2.2 如果所有终端都已关闭

若上面的进程检查仍显示本阶段进程，先从当前 PowerShell 按 `run_id` 执行项目提供的精确停止入口：

```powershell
$active = Get-Content -LiteralPath .\Results\ui_platform\qgc_active_run.json -Raw | ConvertFrom-Json
$runId = [string]$active.run_id
if ($active.state -in @('running', 'launch_prepared')) {
    wsl.exe -d Ubuntu-20.04 --exec bash -lc "cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/stop_factory_l2_rviz_qgc_phase1.sh '$runId'"
}
```

这个停止入口只接受 `qgc-...` 的阶段一 `run_id`，只匹配带有相同 `MOSIM_OPERATOR_RUN_ID` 的阶段一进程，
不会按名称随机结束其他 ROS/Gazebo 运行。不要使用 `pkill`、`kill -9`，也不要在本流程使用
`Scripts/cmd/停止所有仿真.cmd`；那个入口读取的是另一套编排运行记录。

如果停止入口提示没有当前 `run_id` 的进程，但随后报告 `11345` 仍被占用，说明端口属于另一条运行。
读取占用者的命令行和环境后，不要用阶段一停止脚本接管它：

```powershell
wsl.exe -d Ubuntu-20.04 --exec bash -lc "ss -ltnp | grep -E ':11345$' || true"
wsl.exe -d Ubuntu-20.04 --exec bash -lc "ps -eo pid,ppid,pgid,args | grep -E 'gzserver|roslaunch|rviz' | grep -v grep || true"
```

若占用者的 `RUN_ID`、结果目录或启动入口不是当前 `qgc-...`，先按那条运行自己的停止入口结束它，或等待它完成；
在 `11345` 仍占用时，阶段一必须停在预检门，不能换端口或并行启动。

### 2.3 清理完成判定

再次执行下面的检查。只有端口和阶段一进程都没有输出，才允许继续：

```powershell
Set-Location C:\Users\HP\Desktop\MoSim

$port = wsl.exe -d Ubuntu-20.04 --exec bash -lc "ss -ltnp | grep -E ':11345$' || true"
if (-not [string]::IsNullOrWhiteSpace(($port -join ''))) {
    throw 'Gazebo master port 11345 is still in use. Do not start Phase 1.'
}

$processes = wsl.exe -d Ubuntu-20.04 --exec bash -lc "ps -eo pid,ppid,args | grep -E 'gzserver|px4|mavros|rviz|run_qgc_diff_realtime_goal_gate|run_px4ctrl_ego_single_gate' | grep -v grep || true"
if (-not [string]::IsNullOrWhiteSpace(($processes -join ''))) {
    $processes
    throw 'A previous ROS/Gazebo process is still present. Do not start Phase 1.'
}

if (Test-Path -LiteralPath .\Results\ui_platform\qgc_active_run.json) {
    $active = Get-Content -LiteralPath .\Results\ui_platform\qgc_active_run.json -Raw | ConvertFrom-Json
    if ($active.state -in @('running', 'launch_prepared')) {
        throw "The active Phase 1 pointer is still live: $($active.run_id)"
    }
    if ($active.state -in @('blocked', 'completed', 'failed')) {
        wsl.exe -d Ubuntu-20.04 --exec bash -lc "cd /mnt/c/Users/HP/Desktop/MoSim && python3 Scripts/ui/prepare_operator_run.py --clear-active"
    }
}

'CLEAN_START_CHECK=PASS'
```

`blocked`、`completed` 和 `failed` 是终态，可以在确认没有进程、端口已释放后清除指针；`running` 和
`launch_prepared` 不是终态，不能清除。清除动作只更新指针，不删除 `Results` 证据。

## 3. 第二步：运行启动前预检

仍在项目根目录执行：

```powershell
Set-Location C:\Users\HP\Desktop\MoSim

$qgcExe = & .\Scripts\ui\run_flight_console.ps1 -ResolveOnly
$qgcExe
$qgcReport = Get-Content -LiteralPath .\Results\ui_platform\flight_console_windows_toolchain_preflight.json -Raw | ConvertFrom-Json
if ($qgcReport.status -ne 'ready') {
    throw "MoSim Ground Control preflight is not ready: $($qgcReport.status)"
}

if (-not (Test-Path -LiteralPath .\Scripts\sunray\start_factory_l2_rviz_qgc_phase1.sh)) {
    throw 'Phase 1 launcher is missing.'
}
if (-not (Test-Path -LiteralPath .\Config\rviz\sunray_ros1_goal4_diff_realtime_combined_review.rviz)) {
    throw 'Phase 1 RViz configuration is missing.'
}

wsl.exe -d Ubuntu-20.04 --exec bash -lc "source /opt/ros/noetic/setup.bash && command -v roscore && command -v roslaunch && command -v rviz"
wsl.exe -d Ubuntu-20.04 --exec bash -lc "cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/check_sunray_ros1_runtime_preflight.sh"

'PHASE1_PREFLIGHT=PASS'
```

必须同时满足：

- QGC 可执行文件路径能解析，`flight_console_windows_toolchain_preflight.json` 的 `status` 是 `ready`；
- 两个阶段一文件检查不报错；
- WSL 能找到 `roscore`、`roslaunch`、`rviz`；
- 最后一条检查输出 `SUNRAY_ROS1_PREFLIGHT=PASS`。

任何一项失败都停在这里。不要用手工启动命令绕过预检。

## 4. 第三步：只启动 QGC 显示窗口

在第二个 PowerShell 标签页执行：

```powershell
Set-Location C:\Users\HP\Desktop\MoSim
& .\Scripts\cmd\启动MoSim地面站.cmd
```

看到 `Started MoSim Ground Control` 和 `main window ready` 后，保持一个 QGC 窗口打开并停留在 Factory L2
地图。QGC 启动器发现已有正式实例时会复用它；不要同时启动候选构建和正式构建两个实例。

这一步只打开显示面。不要进入 QGC `Plan Goal`，不要解锁、起飞、上传任务或切换飞行模式。

## 5. 第四步：启动阶段一受管运行

在第三个 PowerShell 标签页执行下面这一整条命令，并保持该窗口前台运行：

```powershell
Set-Location C:\Users\HP\Desktop\MoSim
wsl.exe -d Ubuntu-20.04 --exec bash -lc "cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/start_factory_l2_rviz_qgc_phase1.sh"
```

不要把这条命令拆成多个终端，也不要直接调用 `run_qgc_diff_realtime_goal_gate.sh`。

启动包装器先检查 `GAZEBO_MASTER_URI`（默认 `http://127.0.0.1:11345`）和监听者，再创建新的 `run_id`、
`RUN_MANIFEST.json` 和活动指针。只有端口空闲时才会看到：

```text
Prepared Factory L2 Phase 1 run: qgc-...
Run manifest: .../Results/runs/qgc-.../RUN_MANIFEST.json
```

如果第一屏直接出现：

```text
BLOCKER gazebo_master_port_in_use: 11345
```

说明启动尚未创建新的运行。回到第 2 节处理端口，不要重复执行启动命令。

看到 `Prepared ...` 只表示运行身份创建完成，不表示 RViz 已就绪。冷启动可能需要几分钟；不要在等待期间关闭
PowerShell 3，也不要手工再开 Gazebo、RViz 或第二套 PX4。

## 6. 第五步：等待就绪，不要提前点击 RViz

在 PowerShell 1 读取当前运行状态：

```powershell
Set-Location C:\Users\HP\Desktop\MoSim
$active = Get-Content -LiteralPath .\Results\ui_platform\qgc_active_run.json -Raw | ConvertFrom-Json
$runId = [string]$active.run_id
$resultDir = Join-Path (Get-Location) "Results\sunray_ros1\$runId"
$runtimePath = Join-Path $resultDir 'RVIZ_QGC_DISPLAY_PHASE1_RUNTIME_STATUS.json'
$manualPath = Join-Path $resultDir 'RVIZ_QGC_DISPLAY_PHASE1_MANUAL_TEST.json'

if (-not (Test-Path -LiteralPath $runtimePath)) {
    throw "Runtime status is not written yet for $runId. Keep PowerShell 3 running."
}
if (-not (Test-Path -LiteralPath $manualPath)) {
    throw "Manual packet is not written yet for $runId. Keep PowerShell 3 running."
}

$runtime = Get-Content -LiteralPath $runtimePath -Raw | ConvertFrom-Json
$manual = Get-Content -LiteralPath $manualPath -Raw | ConvertFrom-Json
[pscustomobject]@{
    active_state = $active.state
    run_id = $runId
    runtime_state = $runtime.state
    reason_code = $runtime.reason_code
    manual_status = $manual.status
    rviz_config = $manual.entrypoints.rviz_config
}

if ($active.state -ne 'running' -or
    $runtime.state -ne 'running' -or
    $runtime.reason_code -ne 'rviz_qgc_display_phase1_ready_for_rviz_goal' -or
    $manual.status -ne 'awaiting_rviz_goal') {
    throw 'Phase 1 is not ready. Do not click RViz; preserve the JSON and PowerShell 3 output.'
}

'PHASE1_READY_FOR_RVIZ_GOAL'
```

同时，PowerShell 3 必须打印以下完整提示：

```text
Phase 1 RViz-to-QGC display test is ready. Use RViz 2D Nav Goal once, then observe the same run in QGC; Plan Goal is intentionally disabled.
```

只有活动指针为 `running`、运行状态为 `running`、`reason_code` 为
`rviz_qgc_display_phase1_ready_for_rviz_goal`、人工包为 `awaiting_rviz_goal`，并且 RViz 窗口已经出现时，
才进入下一节。状态为 `blocked`、文件尚未出现或 RViz 未打开时，都不能点击目标。

## 7. 第六步：在 RViz 发送一次目标

阶段一会自动打开下面的 RViz 配置：

```text
/mnt/c/Users/HP/Desktop/MoSim/Config/rviz/sunray_ros1_goal4_diff_realtime_combined_review.rviz
```

在 RViz 中确认这些显示项存在：

- `Goal4 Planner Input Live Cloud`，topic `/uav1/livox_world`；
- `3D Inflated Occupancy Diagnostic`，topic `/drone_0_ego_planner_node/grid_map/occupancy_inflate`；
- `UAV Truth Trajectory`、`Diff Position Command Path`、`Mission Target Segment`。

`3D Inflated Occupancy Diagnostic` 是 3D boxes 诊断，不是二维 `nav_msgs/OccupancyGrid`；`World Grid` 只是坐标参考网格。

在 RViz 工具栏选择 `2D Nav Goal`，在无人机附近的无障碍区域单击并拖出短目标方向。阶段一只发送一次。

禁止以下动作：

- 在 QGC 中点击 `Plan Goal`；
- 在 QGC 中解锁、起飞、上传任务或切换飞行模式；
- 再次点击 RViz 目标；
- 手工启动第二个 RViz、Gazebo、PX4、MAVROS 或规划器。

运行端会把 RViz 的 `/move_base_simple/goal` 转发到规划器的 `/goal_with_id`，但这个转发记录不等于 QGC 发起规划。

## 8. 第七步：在同一个 QGC 观察

发送目标后回到第 4 节打开的同一个 QGC 窗口，观察 Factory L2 地图：

1. future path 出现或更新；
2. actual track 出现或更新；
3. 记录观察时间和本次 `run_id`。

底图出现、QGC 窗口打开或单独一张截图都不算阶段一结论。人工结论必须明确写成：

```text
在同一 run_id=<run_id> 的 QGC 窗口中人工观察到 future path 和 actual track。
```

运行端自动文件 `RVIZ_QGC_DISPLAY_PHASE1_ACCEPTANCE.json` 的 `status=automated_evidence_ready` 只说明自动检查通过；
其中 `manual_observation.status` 仍然需要人工观察，不能用自动 JSON 代替。

## 9. 第八步：正常结束、清除指针和保留证据

完成观察后，回到 PowerShell 3：

1. 如果终端仍在运行，按一次 `Ctrl+C`；
2. 等待它返回 PowerShell 提示符；
3. 不要在运行仍为 `running` 或 `launch_prepared` 时清除指针。

在 PowerShell 1 执行：

```powershell
Set-Location C:\Users\HP\Desktop\MoSim
$active = Get-Content -LiteralPath .\Results\ui_platform\qgc_active_run.json -Raw | ConvertFrom-Json
if ($active.state -in @('running', 'launch_prepared')) {
    throw "Phase 1 is still active: $($active.run_id). Stop PowerShell 3 first."
}

$port = wsl.exe -d Ubuntu-20.04 --exec bash -lc "ss -ltnp | grep -E ':11345$' || true"
if (-not [string]::IsNullOrWhiteSpace(($port -join ''))) {
    $port
    throw 'Gazebo master port 11345 is still in use. Do not clear the pointer.'
}
wsl.exe -d Ubuntu-20.04 --exec bash -lc "cd /mnt/c/Users/HP/Desktop/MoSim && python3 Scripts/ui/prepare_operator_run.py --clear-active"

'PHASE1_CLEANUP=PASS'
```

如果清理前的 `ss` 仍有输出，先不要清除指针，回到第 2.2 节按 `run_id` 停止阶段一，再重新检查。

至少保留本次 `run_id` 对应的：

```text
Results/runs/<run_id>/RUN_MANIFEST.json
Results/runs/<run_id>/telemetry.json
Results/sunray_ros1/<run_id>/RVIZ_QGC_DISPLAY_PHASE1_COMMAND.txt
Results/sunray_ros1/<run_id>/RVIZ_QGC_DISPLAY_PHASE1_RUNTIME_STATUS.json
Results/sunray_ros1/<run_id>/RVIZ_QGC_DISPLAY_PHASE1_MANUAL_TEST.json
Results/sunray_ros1/<run_id>/RVIZ_QGC_DISPLAY_PHASE1_ACCEPTANCE.json
Results/sunray_ros1/<run_id>/qgc_diff_inner_runtime.log
Results/sunray_ros1/<run_id>/runtime/ros_log/
```

确认指针已清除、端口为空后，才关闭 QGC 窗口。不要删除本次结果目录。

## 10. 失败处理表

| 现象 | 正确处理 |
| --- | --- |
| 启动第一屏出现 `gazebo_master_port_in_use` | 这次没有创建新运行；读取 `ss`/`ps`。若占用者属于当前阶段一才按 `run_id` 停止；若属于其他运行，按其他运行自己的入口处理，不能并行启动。 |
| 出现 `operator_run_already_active` | 读取 `qgc_active_run.json`；若仍有进程，按其 `run_id` 停止；若无进程且状态是终态，才清除指针。 |
| 只有 `Prepared ...`，长时间没有就绪提示 | 在 PowerShell 1 读取同一 `run_id` 的 runtime status 和 `qgc_diff_inner_runtime.log`；不要手工启动 RViz。 |
| runtime status 为 `blocked` | 不要点击 RViz；保留 JSON、`qgc_diff_inner_runtime.log`、`runtime/sunray_gazebo.log` 和 `runtime/ros_log/`。 |
| RViz 没打开但状态不是 ready | 视为启动未完成，不要另开 RViz；先看 PowerShell 3 输出。 |
| RViz 有点云但 occupancy boxes 显示 `No messages received` | 检查显示项的 topic 和 Status；不要用 `World Grid` 冒充占据地图。 |
| QGC 只有底图 | 先确认 RViz 目标确实只发送了一次，再检查同一 run 的 `telemetry.json`；不要点击 QGC `Plan Goal`。 |
| 终端全关后 `11345` 仍被占用 | 使用第 2.2 节的 `stop_factory_l2_rviz_qgc_phase1.sh <run_id>`；停止后端口仍不为空就停在现场，不要随机杀进程。 |
| QGC 关闭后仍有 Gazebo | QGC 是显示面，不能代替阶段一运行的停止；按 `run_id` 停止阶段一并重新验证端口。 |

## 11. 阶段边界

本教程最多支持以下结论：阶段一是否到达 RViz 就绪门、RViz 是否发送过一次目标，以及操作者是否在同一
QGC 窗口观察到 future path 和 actual track。它不证明 QGC 原生规划、控制器通过、PX4 飞行成功、定位成功、
自主避障成功或最终场景验收。

需要独立诊断 ROS1/Gazebo/PX4/MAVROS 基础链路时，必须先完全结束本教程运行、释放 `11345`，再使用对应基础诊断工作流；
基础诊断和阶段一不能共享 ROS master、Gazebo master、PX4 或 MAVROS 进程。
