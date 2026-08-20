# Phase 1 启动手册（4 个终端）

当前状态：指针已清除，端口已释放，预检全绿，可以直接启动。

---

## 终端 1 — 清理检查（随时用，不用保持）

```powershell
Set-Location C:\Users\HP\Desktop\MoSim
# 查进程
wsl.exe -d Ubuntu-20.04 --exec bash -lc "ps -eo pid,args | grep -E 'gzserver|roscore|px4|mavros|rviz|fastlio|ego_planner' | grep -v grep || echo clean"
# 查端口
wsl.exe -d Ubuntu-20.04 --exec bash -lc "ss -ltnp | grep -E ':11345|:11311' || echo ports_free"
# 查活动指针
Get-Content -LiteralPath .\Results\ui_platform\qgc_active_run.json -Raw | ConvertFrom-Json | Select state,run_id,terminal_reason_code
```

如需强制清除终态指针：
```powershell
Set-Location C:\Users\HP\Desktop\MoSim
wsl.exe -d Ubuntu-20.04 --exec bash -lc "cd /mnt/c/Users/HP/Desktop/MoSim && python3 Scripts/ui/prepare_operator_run.py --clear-active"
```

---

## 终端 2 — QGC 地面站（独立窗口，可选）

```powershell
Set-Location C:\Users\HP\Desktop\MoSim
.\Scripts\cmd\启动MoSim地面站.cmd
```

看到地图后保持窗口，不要在 QGC 里点 Plan Goal / 解锁 / 上传任务。

---

## 终端 3 — Runtime（Gazebo / PX4 / MAVROS / FAST-LIO / 规划器）

**最重要，不能关。**

```powershell
Set-Location C:\Users\HP\Desktop\MoSim
wsl.exe -d Ubuntu-20.04 --exec bash -lc "cd /mnt/c/Users/HP/Desktop/MoSim && PX4CTRL_PARAM_GET_TIMEOUT_S=30 PX4CTRL_PARAM_GET_ATTEMPTS=4 PX4CTRL_PARAM_SET_TIMEOUT_S=30 bash Scripts/sunray/start_factory_l2_rviz_qgc_phase1.sh"
```

正常启动会先输出：
```
Prepared Factory L2 Phase 1 runtime run: qgc-...
Run manifest: .../Results/runs/qgc-.../RUN_MANIFEST.json
```

看到 `Prepared ...` 后**立即**打开终端 4，不要等。

---

## 终端 4 — Display / 双 RViz（悬停就绪后自动弹窗）

```powershell
Set-Location C:\Users\HP\Desktop\MoSim
wsl.exe -d Ubuntu-20.04 --exec bash -lc "cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/start_factory_l2_rviz_qgc_phase1_display.sh"
```

它会等 Runtime 就绪门，然后自动打开：
- **RViz 1**（点云）：观察 `/uav1/livox_world` 点云、无人机位置
- **RViz 2**（栅格地图）：`2D Nav Goal` 工具 → 地图上点目标

终端出现以下提示即可操作：
```
Phase 1 Display/RViz terminal is ready. Use RViz 2D Nav Goal once, then observe the same run in QGC.
```

---

## 操作流程

1. 等两个 RViz 窗口弹出，无人机悬停
2. 切到 **RViz 2**（栅格地图窗口）
3. 工具栏点 `2D Nav Goal`
4. 在无障碍区域**单击并拖**出目标方向（只发一次）
5. 观察规划轨迹和飞行

---

## 报错快速诊断（在终端 1 执行）

出现问题先查这几个日志，`RUN_ID` 从终端 3 的输出里找：

```powershell
$id = "qgc-..."   # 替换成终端3输出的 run_id
$d = "C:\Users\HP\Desktop\MoSim\Results\sunray_ros1\$id"

# 主运行日志（inner gate 所有子进程输出汇总在这里）
Get-Content "$d\qgc_diff_inner_runtime.log" -Tail 80

# 各子系统日志
Get-Content "$d\runtime\sunray_gazebo.log" -Tail 40
Get-Content "$d\runtime\ego_single_px4ctrl_goal4.log" -Tail 40
Get-Content "$d\runtime\fastlio_mapping.log" -Tail 40 -ErrorAction SilentlyContinue
Get-Content "$d\runtime\px4ctrl.log" -Tail 40 -ErrorAction SilentlyContinue

# 运行状态
Get-Content "$d\RVIZ_QGC_DISPLAY_PHASE1_RUNTIME_STATUS.json" -Raw | ConvertFrom-Json
```

---

## 正常停止

在**终端 3** 按 `Ctrl+C`，等提示符回来。
