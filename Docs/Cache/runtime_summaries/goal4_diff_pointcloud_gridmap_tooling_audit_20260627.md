# Goal4 Diff 点云与栅格地图成熟工具调研记录

> Scope: Goal4 / Diff-Planner review 中 `/uav1/livox/lidar`
> -> `/uav1/livox_world` -> `plan_env/grid_map` -> RViz 点云/栅格显示异常。
> This is a cache investigation note, not runtime acceptance evidence.

## 1. 结论

当前不应继续把点云变换当成自研数学脚本随手调参。

成熟路线已经存在：

1. ROS / PCL 路线：
   `pcl_ros::transformPointCloud` 可以把 `sensor_msgs::PointCloud2`
   按 TF 或显式刚体变换转换到目标坐标系。
2. ROS / tf2 路线：
   `tf2_sensor_msgs` 是 ROS 中处理传感器消息 TF 变换的标准包；如果
   Python 侧不可用，应优先转 C++ / PCL，而不是继续扩展 Python 手写矩阵。
3. OctoMap 路线：
   OctoMap 是成熟的 C++ 3D occupancy mapping 参考实现，可作为三维占据语义
   参考；当前 Diff/EGO 使用自身局部 `grid_map`，不等价于全局 OctoMap。
4. Sunray 本地上游路线：
   `References/Sunray/General_Module/sunray_planner_utils/src/point_cloud_transform.cpp`
   已经用 `pcl_ros::transformPointCloud` 和完整 odom pose 做 local cloud
   -> world cloud。该实现应作为 Goal4/Diff world cloud adapter 的第一参考。
5. Diff-Planner 当前 `plan_env/grid_map` 路线：
   `References/Lab/planning_local/Diff-Planner/src/diff_planner/plan_env/src/grid_map.cpp`
   的 `cloudCallback` 把输入点云当成已经在 world frame 下的点，然后再执行
   raycast/local occupancy update。也就是说 `/uav1/livox_world` 必须已经正确。

因此，项目规则是：

```text
先用或对齐 ROS/PCL/TF/Sunray 上游工具
  -> 再做最小兼容 adapter
  -> 最后才允许手写矩阵或自研映射逻辑
```

## 2. 本地证据

当前自有脚本：

```text
Scripts/sunray/goal4_pointcloud_to_world_node.py
```

问题修复前的运行入口默认值：

```text
Scripts/sunray/run_px4ctrl_ego_single_gate.sh
POINTCLOUD_ROTATION_MODE="${POINTCLOUD_ROTATION_MODE:-yaw_only}"
```

脚本虽然支持：

```text
rotation_mode=full
```

但默认仍是：

```text
rotation_mode=yaw_only
```

这会在无人机存在 roll/pitch 时只用 yaw 旋转点云。对于移动中的四旋翼，
这不是完整刚体变换。

2026-06-27 静态修复后，`goal4_pointcloud_to_world_node.py`、
`run_px4ctrl_ego_single_gate.sh` 和 `run_px4ctrl_ego_swarm_gate.sh` 的默认值
已改为：

```text
rotation_mode=full
```

`yaw_only` 仅保留为显式诊断模式。

对比 Sunray 上游：

```text
References/Sunray/General_Module/sunray_planner_utils/src/point_cloud_transform.cpp
```

其逻辑是从 odom 读取完整 position + quaternion，并调用：

```text
pcl_ros::transformPointCloud(...)
```

## 3. 已发现的高概率问题

上一次 Goal4/Diff live audit：

```text
Results/sunray_ros1/review_diff_liveaudit_20260627_203924/RUN_MANIFEST.json
```

记录：

```text
pointcloud_to_world.rotation_mode = yaw_only
pointcloud_to_world.mount_mode = sensor_to_body
pointcloud_to_world.min_world_z_m = 0.50
```

对应 history：

```text
Results/sunray_ros1/review_diff_liveaudit_20260627_203924/pointcloud_to_world_history.jsonl
```

静态统计：

```text
accepted_rows = 37
max_abs_roll_deg ~= 20.85
max_abs_pitch_deg ~= 9.94
max_abs_cloud_odom_dt_s ~= 0.023
```

如果只用 yaw 而忽略 pitch/roll，10 deg 倾角在 4.5 m 量程会产生约 0.78 m
垂向投影误差，在 8 m 量程会产生约 1.39 m 误差。20 deg 量级会更大。
这足以造成地面杂点、边缘散点、栅格小方块和障碍物位置膨胀/漂移。

所以当前首要嫌疑不是 RViz 点大小，也不是控制器参数，而是：

```text
点云 world-frame 变换没有使用完整姿态
```

## 4. Header 与 mount 的注意事项

不要仅凭 `PointCloud2.header.frame_id` 判断点是否已经在 base/world frame。
当前 Livox Gazebo plugin 可能把 frame_id 标成 `uav1/base_link`，但点坐标仍来自
传感器本地 ray axis。是否需要应用 MID360 -> body mount，应以 plugin 源码、
SDF joint/include pose 和可控静态测试共同确认。

当前已知 mount：

```text
mount_xyz = -0.000005 0.032295 0.050167
mount_rpy = 0 0 4.712389
```

应验证只应用一次，不得重复应用。

## 5. 下一步检查顺序

在重新开 live 仿真前，先按这个顺序处理：

1. 静态确认 `goal4_pointcloud_to_world_node.py` 的矩阵顺序是否等价于：

```text
world_T_sensor = world_T_body * body_T_sensor
```

2. 已将 Goal4/Diff 的默认 `POINTCLOUD_ROTATION_MODE` 从 `yaw_only` 改为
   `full`。
3. 保留 `yaw_only` 只作为诊断模式，不作为默认 planner input。
4. 若 `full` 仍不对，再做 Python 输出与 Sunray C++/PCL 输出的同输入对比。
5. 若 C++/PCL 与 Python full 都不对，再查：
   timestamp/TF interpolation、mount 重复应用、Livox plugin frame 语义、Diff
   `grid_map` local ring-buffer 参数。

## 6. 已调研外部参考

Web / upstream references checked:

```text
ROS tf2_sensor_msgs:
  https://index.ros.org/p/tf2_sensor_msgs/
  Package description says it transforms sensor_msgs, notably PointCloud2.

ROS perception_pcl / pcl_ros:
  https://github.com/ros-perception/perception_pcl
  PCL-ROS bridge for n-D point clouds and 3D geometry processing.

OctoMap ROS package:
  https://index.ros.org/p/octomap_server/
  https://github.com/OctoMap/octomap_mapping
  Provides incremental 3D OctoMap building and saving.

EGO-Planner:
  https://github.com/ZJU-FAST-Lab/ego-planner
  ESDF-free local planner; planner/map input correctness is still required.

EGO point-cloud/frame issue reference:
  https://github.com/ZJU-FAST-Lab/ego-planner/issues/106
  Similar symptom class: point cloud direction/frame does not follow system yaw.
```

Interpretation:

- ROS/PCL `pcl_ros::transformPointCloud` remains the preferred C++ path for
  transforming PointCloud2 in this ROS1 lane.
- OctoMap is a mature C++ three-dimensional occupancy mapping reference, but
  current Diff/EGO uses its own local voxel/raycast `plan_env/grid_map`, so
  OctoMap is a semantic reference, not a drop-in replacement for this gate.
- EGO-Planner / EGO-Swarm confirm that planner success depends on correct
  point-cloud/depth + odometry/frame input; community issues show similar
  failure modes when the point cloud does not follow vehicle orientation.
- 2D `pointcloud_to_grid` class tools are not a direct substitute because this
  gate needs 3D local voxel/raycast semantics.

## 7. 禁止项

在该问题未收口前，不要通过以下方式掩盖问题：

```text
调大/调小 RViz 点大小
只隐藏 ground/clutter layer
继续调 occupancy voxel size 让画面看起来正常
修改 px4ctrl 参数
修改 planner cost weights
绕过真实 Livox 点云输入
```
