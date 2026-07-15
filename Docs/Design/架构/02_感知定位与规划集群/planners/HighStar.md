# HighStar

## 定位

HighStar 是 `References/Lab/exploration_coverage/HighStar` 下的单机/多机高速
UAV 在线自主探索候选。上游仓库为 NKU-MobFly-Robotics/HighStar，README
声明开发环境是 Ubuntu 20.04 + ROS Noetic，默认仿真平台是修改版 RotorS。

MoSim 中 HighStar 只能作为自主探索候选，不是当前已证明的 Factory 全覆盖
主线。它必须经过 Sunray / Gazebo Classic / PX4 / MAVROS / px4ctrl / RViz
运行证据链；不得直接拥有 MAVROS 控制发布权。

## MoSim 适配状态

当前入口：

```text
Scripts/sunray/highstar_mosim_dry_run.launch
Scripts/sunray/run_px4ctrl_ego_single_gate.sh with PLANNER_VARIANT=highstar
Results/build/highstar_overlay_ws_20260708_try1
```

当前有效输入路线是 depth adapter：

```text
/uav1/livox/lidar
  -> Scripts/sunray/highstar_pointcloud_depth_adapter.py
  -> /mosim/highstar/depth + /mosim/highstar/camera_info
  -> HighStar block_map/frontier/murder
  -> /Murder/Traj
  -> Scripts/sunray/highstar_swarmtraj_position_cmd_bridge.py
  -> MoSim PositionCommand safety adapter
  -> px4ctrl
```

direct pointcloud 路线当前不作为主线。运行诊断显示 direct pointcloud 下
LowResMap 大量候选节点没有连续 free space，`obstacle` 日志实际混合了
unknown/free-space contract 失败，不能简单解释为真实障碍。

## 当前证据

HighStar depth adapter baseline：

```text
Results/sunray_ros1/sunray_ros1_goal4_ego_single_20260708_162408
EGO_SINGLE_METRICS.json status=passed
/Murder/Traj input_count=4
planner_position_cmd=260
coverage packet blocked, merged_sensor_footprint_coverage_ratio=0.0220
```

HighStar depth baseline 复现：

```text
Results/sunray_ros1/sunray_ros1_goal4_ego_single_20260708_164717
EGO_SINGLE_METRICS.json status=passed
/Murder/Traj input_count=1
planner_position_cmd=69
position_cmd=5820
raw_lidar=1441
world_cloud=1441
position_cmd_safety_adapter jump_rejected_count=110
coverage packet blocked, merged_sensor_footprint_coverage_ratio=0.0192
```

结论：HighStar 已证明可以在 Factory L2 clean scene 中启动、建局部图、输出
轨迹并由 px4ctrl 执行；但没有证明 Factory 室内完整未知探索覆盖。

## 当前 blocker

当前 blocker 不是依赖缺失，也不是 Gazebo/PX4/MAVROS 启动失败，而是：

```text
coverage expansion + trajectory quality
```

具体表现：

1. depth adapter 能显著改善 LowResMap free voxel，但覆盖仍停留在 2% 级。
2. 日志中出现 `low quality trajectory, do not use it` 和 `cover traj fail!`。
3. 部分运行 `/Murder/Traj` 数量少，后续探索不能持续扩张。
4. 盲调 sensor range、LowRes node size、frontier scale 会导致 target search
   退化为 `fail find target`，不得继续沿该方向粗暴调参。

## 下一步门禁

下一步只允许做窄变量 A/B：

```text
HSTAR-A1: 固定 depth adapter、Factory clean world、map/LowRes/frontier 参数；
          只调 HighStar 原生 opt/MaxVel, opt/MaxAcc, opt/MaxJer,
          opt/WeiCover, opt/AdoptCoverThresh，观察轨迹质量和 jump reject。
HSTAR-A2: 若 A1 无改善，回看上游 issue/README/论文约束，确认 RotorS depth
          camera、map bounds、free-space 初始化、cover trajectory 的必要契约。
HSTAR-A3: 若仍无法扩张，冻结 HighStar 为 source-backed local exploration
          fallback，转入 CERLAB 或其他候选审计。
```

每次运行必须汇报：

```text
run path
EGO_SINGLE_METRICS status/blockers
/Murder/Traj input_count
planner_position_cmd / position_cmd
coverage ratio
safety adapter jump/clamp
是否继续或冻结
```

## 禁止声明

不得把 HighStar 的局部 command-stream pass 声明为 Factory 室内全覆盖建图完成。
不得把 direct pointcloud 失败解释成控制器问题。不得用 UE 截图、静态地图或
headless topic 非空替代 Gazebo/PX4/MAVROS/RViz/log/coverage packet 证据。
