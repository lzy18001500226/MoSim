# RViz 规划到 QGC 航迹显示: 阶段一人工测试教程

> 适用对象: 已具备本项目 Windows QGC 构建与 WSL Ubuntu 20.04 / ROS1 Noetic 运行环境的操作者。
> 本教程从干净的项目操作状态开始，完成第一次人工测试: `RViz 2D Nav Goal -> 规划器 -> QGC future path / actual track`。
> 它不启动真实飞行器，也不验证 QGC 自己发起规划。QGC `Plan Goal` 属于阶段二，不能在本教程中使用。

## 1. 本次测试要证明什么

阶段一只有一个人工输入和一个人工观察：

1. 在 RViz 中使用一次 `2D Nav Goal`。
2. 在 QGC 中观察**同一 `run_id`**的 future path 与 actual track。

运行端会自动记录 RViz topic、规划器输出和 sidecar 遥测；人工观察仍需操作者完成。即使自动结果为
`automated_evidence_ready`，它也不代表 QGC 发起规划、飞行成功或控制器通过验收。

## 2. 窗口与前置条件

本次测试需要三个可见窗口：

| 窗口 | 用途 | 不可替代原因 |
| --- | --- | --- |
| Windows PowerShell | 启动并保留 QGC 启动输出 | QGC 仅是操作/显示面，不在后台启动运行时 |
| QGC / MoSim Ground Control | 选择 Profile，并观察 Factory L2 上的航迹 | 人工视觉确认的唯一操作面 |
| WSL Ubuntu 20.04 终端 | 执行 QGC 复制出的运行命令，并保留 ROS、Gazebo、PX4、规划器与 sidecar 日志 | 运行证据必须来自可见终端与结果包 |

开始前确认没有另一个同类运行仍在使用该项目。若 `Results/ui_platform/qgc_active_run.json` 的
`state` 是 `running`，先回到该运行原来的可见 WSL 终端处理它；不要直接启动第二个运行或删除结果目录。
若该终端已经结束，保留其状态文件和日志，并先按本教程第 8 节的停止/清理规则处理活动指针。

本教程使用的已发布 Profile 为：

```text
RViz规划-QGC航迹显示（阶段一）
profile_id: px4ctrl_graphical_c99_factory_rviz_qgc_display_phase1_v1
runtime_profile_id: sunray_ros1_factory_l2_graphical_px4ctrl_c99_rviz_qgc_display_phase1_v1
```

它的唯一目标输入是 `/move_base_simple/goal`，运行后端会把该目标交给规划器的 `/goal_with_id`。

## 3. 从项目根目录进行只读预检

在 **Windows PowerShell** 中执行：

```powershell
Set-Location C:\Users\HP\Desktop\MoSim
.\Scripts\ui\run_flight_console.ps1 -ResolveOnly
(Get-Content -LiteralPath Results\ui_platform\flight_console_windows_toolchain_preflight.json -Raw | ConvertFrom-Json).status
wsl.exe -d Ubuntu-20.04 -- bash -lc "source /opt/ros/noetic/setup.bash && command -v roscore && command -v roslaunch && command -v rviz"
```

预期结果：

- 第一条 QGC 检查输出 `MoSimGroundControl.exe` 的绝对路径。
- 预检报告输出 `ready`。
- WSL 命令分别输出 `roscore`、`roslaunch` 和 `rviz` 的路径。

若 QGC 预检不是 `ready`、可执行文件不存在，或 WSL 中没有 Noetic 命令，**不要开始人工测试**。先修复
对应环境；QGC 构建入口是 `Scripts\ui\build_flight_console.ps1`，但它只构建和校验已安装的工具链，
不会安装 Windows 或 WSL 系统依赖。

## 4. 启动 QGC

仍在项目根目录的 Windows PowerShell 中执行：

```powershell
.\Scripts\cmd\启动MoSim地面站.cmd
```

等待输出包含 `Started MoSim Ground Control` 和 `main window ready`。随后应看到 MoSim Ground Control/QGC
窗口及 Factory L2 二维底图。

这一动作**只启动 QGC**。此时不应同时启动 ROS、Gazebo、PX4、MAVROS、规划器、sidecar 或 RViz；没有活动
遥测时地图只显示底图和任务草案也是正常现象。若 QGC 已在运行，启动器会复用该实例，不会再启动一个副本。

## 5. 在 QGC 中创建阶段一运行

1. 打开 QGC 的“任务”页。
2. 选择控制器 `px4ctrl`。
3. 选择已发布 Profile **“RViz规划-QGC航迹显示（阶段一）”**。
4. 确认这是阶段一 Profile。此时 QGC 的角色仅是显示，不能使用 `Plan Goal`。
5. 点击“复制启动命令”。这会生成带有新的 `run_id`、冻结 Profile 和地图快照的命令，但不会执行它。
6. 打开一个可见的 WSL Ubuntu 20.04 终端，粘贴并执行**刚从 QGC 复制的完整命令**。

不要以手写的 `bash Scripts/sunray/run_qgc_diff_realtime_goal_gate.sh ...` 替代复制出的命令。复制命令会先创建
`Results/runs/<run_id>/RUN_MANIFEST.json`，写入环境变量 `MOSIM_OPERATOR_RUN_ID`、
`MOSIM_OPERATOR_RUN_DIR` 与 `MOSIM_OPERATOR_RUN_MANIFEST`，再调用运行脚本。缺少这些运行身份时，脚本会拒绝启动。

## 6. 等待阶段一就绪

保持 WSL 终端打开，等待其输出：

```text
Phase 1 RViz-to-QGC display test is ready. Use RViz 2D Nav Goal once,
then observe the same run in QGC; Plan Goal is intentionally disabled.
```

运行端此时会启动 RViz，并写入本次 `run_id` 的人工包。可在另一个 Windows PowerShell 中检查，而不关闭运行终端：

```powershell
Set-Location C:\Users\HP\Desktop\MoSim
$active = Get-Content -LiteralPath Results\ui_platform\qgc_active_run.json -Raw | ConvertFrom-Json
$runId = $active.run_id
Get-Content -LiteralPath "Results\sunray_ros1\$runId\RVIZ_QGC_DISPLAY_PHASE1_RUNTIME_STATUS.json" -Raw
Get-Content -LiteralPath "Results\sunray_ros1\$runId\RVIZ_QGC_DISPLAY_PHASE1_MANUAL_TEST.json" -Raw
```

就绪条件必须同时满足：

- 活动指针的 `state` 为 `running`，且 Profile 与阶段一 Profile 一致。
- 运行状态的 `state` 为 `running`，`reason_code` 为 `rviz_qgc_display_phase1_ready_for_rviz_goal`。
- 人工包的 `status` 为 `awaiting_rviz_goal`，并列出 RViz 配置、`/move_base_simple/goal`、
  `/goal_with_id` 和同一 `run_id` 的 `telemetry.json` 路径。

如果终端报错、状态为 `blocked`，或人工包不存在，不要点击 RViz。保留该终端输出以及运行状态 JSON，用它们排查
启动失败；不要手工启动另一个 RViz、QGC 或第二条运行命令来掩盖问题。

## 7. 执行唯一的人工动作并观察 QGC

### 7.1 在 RViz 中发送目标

运行端会使用人工包中记录的 RViz 配置启动 RViz，当前配置为：

```text
Config/rviz/sunray_ros1_goal4_diff_pointcloud_review.rviz
```

在 RViz 工具栏中选择 `2D Nav Goal`，在当前机位附近、Factory L2 的无障碍区域单击并拖出一个短距离目标方向。
只操作一次即可。

不要做以下操作：

- 不要在 QGC 中选择或点击 `Plan Goal`。
- 不要用 QGC 解锁、起飞、上传任务、切换飞行模式或发送其他飞控命令。
- 不要为了重试而并行打开第二个 RViz 或重复启动运行脚本。

### 7.2 在 QGC 中完成视觉确认

回到**同一个 QGC 实例**，观察 Factory L2 地图。RViz 目标被规划器接收后，应在同一 `run_id` 的显示数据中看到：

1. 更新后的 future path。
2. 更新中的 actual track。

建议记录 `run_id`、观察时间，以及 future path / actual track 是否都可见；正式汇报需要视觉证据时，保留包含
QGC 地图的截图。不要把“QGC 窗口打开”“底图出现”或单独的截图作为规划、飞行或控制器验收。

运行完成后，运行端会写入：

```text
Results/sunray_ros1/<run_id>/RVIZ_QGC_DISPLAY_PHASE1_ACCEPTANCE.json
```

其中 `status=automated_evidence_ready` 仅表示自动检查已验证 RViz topic 转发、规划器输出和 sidecar 地图数据。
该文件的 `manual_observation.status` 仍会是 `pending`，直到操作者完成并报告上面的 QGC 视觉确认。因此，阶段一的
人工结论必须单独写明“已在 QGC 观察到同一 run 的 future path 与 actual track”。

## 8. 停止、清理和结果保留

### 正常完成

1. 等待 WSL 运行终端自行结束，或确认它已生成自动验收 JSON。
2. 保留运行目录和终端日志，不要删除 `Results/runs/<run_id>` 或 `Results/sunray_ros1/<run_id>`。
3. 运行已结束后，在 QGC 的“任务”页复制“清除运行清单命令”，并在**同一个可见终端**执行它。该命令只把活动指针标为已结束，不删除结果。

### 中止

如果需要中止，在启动本次运行的可见 WSL 终端按 `Ctrl+C`。阶段一运行命令明确把该操作定义为人工停止方式。
保留终端输出、`RVIZ_QGC_DISPLAY_PHASE1_RUNTIME_STATUS.json` 和人工包，再决定是否修复后重新测试。

不要仅因 QGC 没有刷新就启动第二个实例。只有确认没有其他实验仍在运行时，才可按项目已审计的
`Scripts/cmd/停止所有仿真.cmd` 路径处理全局清理。

## 9. 本次测试应保留的证据

| 文件 | 何时出现 | 用途 |
| --- | --- | --- |
| `Results/runs/<run_id>/RUN_MANIFEST.json` | QGC 复制命令执行后 | 冻结本次 Profile、地图和运行身份 |
| `Results/sunray_ros1/<run_id>/RVIZ_QGC_DISPLAY_PHASE1_RUNTIME_STATUS.json` | 启动期间 | 判断是否真正到达 RViz 人工门 |
| `Results/sunray_ros1/<run_id>/RVIZ_QGC_DISPLAY_PHASE1_MANUAL_TEST.json` | RViz 就绪后 | 固定人工动作、topic、RViz 配置与遥测路径 |
| `Results/sunray_ros1/<run_id>/runtime/clicked_goal_adapter.json` | RViz 目标发送后 | 记录 `/move_base_simple/goal -> /goal_with_id` 转发 |
| `Results/sunray_ros1/<run_id>/runtime/EGO_SINGLE_METRICS.json` | 运行结束后 | 记录规划器和任务端自动指标 |
| `Results/runs/<run_id>/telemetry.json` | sidecar 运行后 | QGC 同一运行的地图数据来源 |
| `Results/sunray_ros1/<run_id>/RVIZ_QGC_DISPLAY_PHASE1_ACCEPTANCE.json` | 自动检查完成后 | 区分自动证据状态与仍需人工完成的 QGC 观察 |

## 10. 常见停止点

| 现象 | 正确处理 |
| --- | --- |
| QGC 启动器找不到可执行文件或预检不是 `ready` | 停在第 3 节，修复 Windows QGC 工具链；不要直接绕过启动器运行未知二进制。 |
| QGC 中 Profile 不可选 | 不修改配置强行运行。记录禁用原因，检查该 Profile 的发布与兼容性。 |
| WSL 终端没有出现就绪提示 | 读取本次运行状态 JSON 和可见终端日志；尚未就绪前不得发送 RViz 目标。 |
| RViz 没有打开 | 视为启动未完成。保留终端日志，不用任意 RViz 配置创建替代窗口。 |
| QGC 只有底图 | 在目标发送前或 sidecar 遥测不完整时这是预期现象。仅在同一 `run_id` 的状态已就绪、RViz 目标已发送后判断 future path / actual track。 |
| 自动验收 JSON 已生成但人工观察尚未记录 | 报告为“自动证据就绪，QGC 视觉确认待完成”，不要升级为完整 QGC 输入闭环或飞行验收。 |

## 11. 阶段边界

本教程完成后，才能进入第二阶段的 QGC `Plan Goal` 人工测试。第二阶段需要 QGC 写入同一 `run_id` 的目标请求、
目标桥转发并观察规划器重新规划；阶段一的 RViz 点击不替代这些证据。

总操作流程及其他 QGC 功能见 [qgc_ue_operator_startup.md](qgc_ue_operator_startup.md)。
