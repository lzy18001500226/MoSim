# 02 感知定位与规划集群

本组负责 FAST-LIO、点云/地图、规划器复现和多机/编队接口。

当前边界：

```text
FAST-LIO先做独立定位评价；
FAST-LIO经PX4 EKF融合后再作为状态源替换实验；
当前最小闭环优先使用Diff-Planner单机和Diff-Planner swarm三机；
EGO/EGOv2/EGO-Swarm作为参考和后续对照，不作为当前三机硬门槛；
FUEL/RACER属于第二阶段自主探索候选，不进入当前最小闭环验收；
Diff/EGO/EGOv2/EGO-Swarm/FUEL/RACER只输出轨迹、目标或探索参考；
规划器不得直接拥有MAVROS控制发布权。
```

当前三机最小闭环冻结：

```text
车辆编号：uav1 / uav2 / uav3
主实现入口：Diff-Planner swarm
目标输入：预设目标点/脚本自动发布为主，RViz手点只用于人工审核
任务流程：三机同时起飞 -> 分别到达三个预设目标点 -> 避障/避机 -> 悬停 -> 降落
定位链路：每架飞机独立MID360 + FAST-LIO + 状态链路
控制链路：每架飞机独立px4ctrl / MAVROS / PX4
暂不做：自主探索、任务分配、覆盖探索、队形保持、相机第一视角、Point-LIO
```

| 文档 | 用途 |
| --- | --- |
| `FASTLIO定位闭环.md` | FAST-LIO、点云、状态源替换、truth和Hybrid-Z实验分组 |
| `规划与编队控制接口.md` | Diff-Planner当前最小闭环、EGO/EGOv2/EGO-Swarm参考、FUEL/RACER第二阶段探索、Trajectory Server、多机隔离和编队接口 |
| `planners/` | 规划器和集群算法规格卡片；`自主探索与集群规划实施路线.md` 是G10后单机探索、多机探索和队形/集群规划的执行入口 |
