# Phase 0：自己打开点云和栅格地图

本教程只打开 ROS1 运行端和两个 RViz 窗口，供最后一次人工检查使用。
它不会解锁、起飞、上传任务，也不会替代 MWORKS 或 ROS1 运行验收。

## 1. 需要的窗口

准备两个 Windows PowerShell 窗口：

- **终端 1：Runtime**，启动 Gazebo、PX4、MAVROS、规划器和传感器；必须保持运行。
- **终端 2：Display/RViz**，等待 Runtime 就绪后自动打开点云窗口和栅格窗口。

使用 `Ubuntu-20.04 / ROS1 Noetic`。不要直接在 PowerShell 中运行 `rviz -d`，也不要打开参考目录中的旧 `.rviz` 文件。

如果屏幕上已经有两个 RViz 窗口，不要重复启动；直接从第 5 节检查即可。

## 2. 启动前检查

在任意 PowerShell 窗口执行：

```powershell
Set-Location C:\Users\HP\Desktop\MoSim

wsl.exe -d Ubuntu-20.04 --exec bash -lc 'source /opt/ros/noetic/setup.bash; printf "%s\n" "--- Gazebo/ROS/RViz processes ---"; ps -eo pid,args | grep -E "[g]zserver|[r]oscore|[p]x4|[m]avros|[r]viz" || true; printf "%s\n" "--- ports ---"; ss -ltnp | grep -E ":11345$|:11311$" || true'
```

如果已经有一套本项目运行，先确认它就是本次运行；不要使用 `pkill`、`kill -9` 或“停止所有仿真”。同一套运行已经有两个 RViz 时，跳过第 3、4 节。

## 3. 启动 Runtime

在 **终端 1** 执行下面整条命令，并保持窗口前台运行：

```powershell
Set-Location C:\Users\HP\Desktop\MoSim
wsl.exe -d Ubuntu-20.04 --exec bash -lc "cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/start_factory_l2_rviz_qgc_phase1.sh"
```

看到类似下面的输出后，说明本次运行身份已经建立；这不等于 RViz 已经就绪：

```text
Prepared Factory L2 Phase 1 run: qgc-...
Run manifest: .../Results/runs/qgc-.../RUN_MANIFEST.json
```

如果提示 `gazebo_master_port_in_use`，不要换端口，也不要重复启动。先处理占用 11345 的原运行。

## 4. 打开两个 RViz 窗口

在 **终端 2** 执行下面整条命令：

```powershell
Set-Location C:\Users\HP\Desktop\MoSim
wsl.exe -d Ubuntu-20.04 --exec bash -lc "cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/start_factory_l2_rviz_qgc_phase1_display.sh"
```

这个脚本会等待同一个 `qgc-...` 运行达到显示就绪门，然后自动打开两个窗口：

```text
点云窗口：Config/rviz/sunray_ros1_goal4_diff_pointcloud_review.rviz
栅格窗口：Config/rviz/sunray_ros1_goal4_diff_grid3d_review.rviz
```

不要再手工启动第三个 RViz。终端 2 看到下面的提示后即可操作：

```text
Phase 1 Display/RViz terminal is ready.
```

## 5. 窗口内检查项

### 点云窗口

左侧 `Displays` 中确认以下显示项为 Enabled：

```text
Goal4 Planner Input Accumulated Cloud
Topic: /mosim/goal4/livox_world_accumulated

Goal4 Planner Input Live Cloud
Topic: /uav1/livox_world
```

### 栅格窗口

左侧 `Displays` 中确认以下显示项为 Enabled：

```text
3D Accumulated Raw Occupancy Review
Topic: /mosim/goal4/occupancy_accumulated
Style: Boxes
```

`World Grid` 只是灰色的坐标参考网格，不是栅格地图。真正的栅格地图是上面的 `PointCloud2` 方块显示。

两个窗口的 `Global Options -> Fixed Frame` 都应为：

```text
world
```

## 6. 最后一次黄色目标线检查

在点云窗口或栅格窗口左侧确认：

```text
Mission Target Segment
Topic: /mosim/goal4/target_path
Color: yellow
```

在栅格窗口使用工具栏的 `2D Nav Goal`，在无障碍区域发送一次目标。规划成功后，飞机当前位置和目标点之间应出现黄色连线；到达目标并保持到达条件后，连线应清除。

这里的黄色线只表示当前目标段，不是完整规划轨迹；绿色线是执行命令路径，红色线是真实轨迹。

## 7. 不看窗口时的 topic 检查

在第三个临时 PowerShell 窗口执行：

```powershell
Set-Location C:\Users\HP\Desktop\MoSim
wsl.exe -d Ubuntu-20.04 --exec bash -lc 'source /opt/ros/noetic/setup.bash; for t in /mosim/goal4/livox_world_accumulated /mosim/goal4/occupancy_accumulated /mosim/goal4/target_path; do echo "--- $t ---"; rostopic type "$t"; timeout 5s rostopic echo -n 1 "$t/header/frame_id" | head -n 1; done'
```

正常情况下，点云和栅格 topic 类型为 `sensor_msgs/PointCloud2`，帧为 `world`；目标线 topic 的帧也应为 `world`。

## 8. 正常停止

1. 在终端 2 按一次 `Ctrl+C`，关闭两个 RViz 和显示脚本。
2. 等终端 2 返回提示符后，在终端 1 按一次 `Ctrl+C`，停止 Runtime。
3. 不要删除 `Results` 下的运行目录和证据文件。
