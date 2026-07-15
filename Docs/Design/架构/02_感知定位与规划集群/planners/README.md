# Planner Cards

本目录记录规划器和集群算法规格。每个文档必须说明源码位置、上游版本、输入、
输出、是否依赖 FAST-LIO、是否经 Trajectory Server、验收场景和禁止声明。

当前卡片：

```text
EGO-Planner-v1.md
EGO-Planner-v2.md
Diff-Planner.md
EGO-Swarm.md
FUEL.md
RACER.md
HighStar.md
CERLAB-UAV-Autonomy.md
TARE-GBPlanner.md
MADER-RMADER.md
Fast-Multi-Robot-Exploration.md
Swarm-Formation.md
Skybrush.md
自主探索与集群规划实施路线.md
```

当前Goal 3主入口：

```text
Diff-Planner.md
  -> 单机目标点规划
  -> uav1/uav2/uav3三机swarm目标点规划
```

## 参考源分层

当前本地参考源已经足够覆盖多机探索和集群展示的主要路线，不再默认继续爬
同类仓库。后续先读本地源码和 README，再决定是否需要补源。

| 类别 | 本地参考 | MoSim用途 |
| --- | --- | --- |
| 当前工程入口 | `References/Lab/planning_local/Diff-Planner` | 已知目标点单机和三机最小规划闭环 |
| 单机/局部规划 | `References/Lab/planning_local/ego-planner`, `References/Lab/planning_local/EGO-Planner-v2`, `References/Lab/planning_local/Fast-Planner`, `References/Lab/planning_local/GCOPTER`, `References/Lab/planning_local/SUPER`, `References/Lab/planning_local/faster`, `References/Lab/planning_local/far_planner-melodic-noetic` | 轨迹优化、局部重规划、地图接口和对照实验 |
| 自主探索 | `References/Lab/exploration_coverage/FUEL`, `References/Lab/exploration_coverage/RACER`, `References/Lab/exploration_coverage/FALCON-ros1-noetic`, `References/Lab/exploration_coverage/HighStar`, `References/Lab/exploration_coverage/CERLAB-UAV-Autonomy`, `References/Lab/exploration_coverage/gbplanner_ros-gbplanner2`, `References/Lab/exploration_coverage/uav_frontier_exploration_3d`, `References/Lab/exploration_coverage/nbvplanner`, `References/Lab/exploration_coverage/ExplorationRRT`, `References/Lab/exploration_coverage/tare_planner-melodic-noetic`, `References/Lab/exploration_coverage/fast_multi_robot_exploration`, `References/Lab/exploration_coverage/3dmr`, `References/Lab/exploration_coverage/MGGPlanner` | 未知地图探索、覆盖、任务分配、共享探索图和多机器人巡检参考 |
| 覆盖/重建规划 | `References/Lab/exploration_coverage/FC-Planner`, `References/Lab/exploration_coverage/SOAR`, `References/Lab/exploration_coverage/exploration-algorithms` | 已知/半已知三维场景覆盖、重建拍照任务和探索算法族索引；不直接证明 MoSim runtime |
| 多机轨迹协商/避碰 | `References/Lab/swarm_coordination/ego-planner-swarm`, `References/Lab/swarm_coordination/mader`, `References/Lab/swarm_coordination/rmader`, `References/Lab/swarm_coordination/Swarm-Formation` | 多机轨迹去冲突、通信延迟鲁棒、编队/队形穿越和密集环境避碰参考 |
| 集群实验/地面站 | `References/Lab/experiment_platforms/skybrush-server`, `References/Lab/experiment_platforms/aerostack2`, `References/Lab/experiment_platforms/crazyswarm2`, `References/Lab/experiment_platforms/crazychoir` | 集群管理、任务接口、地面站/服务端、实验组织方式；不替代当前 ROS1/Sunray/PX4 权威链 |
| 可视化辅助 | `References/Lab/visualization/visualize_uav_trajectory` | 轨迹复盘、报告图和展示素材辅助 |

FUEL、RACER、FALCON、HighStar、CERLAB-UAV-Autonomy、GBPlanner2、UAV Frontier、NBVPlanner、
ExplorationRRT、fast multi-robot exploration、3DMR、MGGPlanner 属于第二阶段
自主探索候选。FC-Planner、SOAR 和 exploration-algorithms 属于覆盖/重建规划
与算法族调研候选。MADER/RMADER 属于多机轨迹协商和通信鲁棒候选。Skybrush、
Aerostack2、Crazyswarm2、CrazyChoir 属于集群实验管理和接口参考。它们只有在
当前三机最小闭环和控制器/codegen回灌稳定后，才进入实现门禁。

规划器只提供参考轨迹或规划结果，不直接发布最终控制命令。

## 取舍规则

1. 先用 `Diff-Planner.md` 保持当前已知目标点三机工程基线。
2. 要做未知地图探索时，先按 `自主探索与集群规划实施路线.md` 推进：
   先复核 FUEL/RACER 的已有 Factory blocker，再优先审计
   `FALCON-ros1-noetic`、`HighStar`、`CERLAB-UAV-Autonomy`、`FC-Planner`、`gbplanner_ros-gbplanner2`、
   `uav_frontier_exploration_3d`、`nbvplanner`、
   `ExplorationRRT` 和 `exploration-algorithms`；不要从零手写探索栈。
3. 要做通信延迟、多机轨迹冲突和鲁棒避碰时，优先读
   `MADER-RMADER.md`。
4. 要做队形/集群规划时，先读 `Swarm-Formation.md`，确认它不是自主探索
   入口，再通过 Planner Adapter 接入。
5. 要做 QGC/UE/网页实验平台或集群状态面板时，优先读 `Skybrush.md`，
   再决定是否参考 Aerostack2/Crazyswarm2/CrazyChoir。
6. 任何规划/探索/集群参考都必须通过 Planner Adapter、Trajectory Server、
   控制器和 Gazebo/PX4/RViz 证据链；不得直接拥有 MAVROS 控制发布权。
