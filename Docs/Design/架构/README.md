# MoSim架构专题文档树

> 状态：当前专题入口，2026-06-24。

本目录是 `Docs/Design/` 下唯一正式专题文档树。根入口仍是：

```text
Docs/Design/README.md
Docs/Design/需求.md
Docs/Design/架构.md
Docs/Design/赛题.md
```

进入专题前，先用 `Docs/Workflows/mainline_operations_board.md` 选择当前
下一步，再用 `00_架构与任务/任务路线图.md` 判断任务属于哪个能力块，最后
读取对应一级目录的 `README.md` 和一个具体规范或算法卡片。路线图定义能力
和门禁，不替代看板选择今天要做哪一步。

## 一级目录

| 目录 | 负责 | 不负责 |
| --- | --- | --- |
| `00_架构与任务/` | 任务路线、系统集成、Profile、架构问题追踪 | 控制律细节 |
| `01_控制器平台/` | 控制接口、控制器实现、增强模块、代码生成、管理配置 | 规划器复现细节 |
| `02_感知定位与规划集群/` | FAST-LIO、点云/地图、Diff-Planner当前入口、EGO/EGOv2/EGO-Swarm参考、编队接口 | 控制器数学推导 |
| `03_测试调参与证据/` | 指标、调参、真机化、C++化、证据包 | 新控制律设计 |
| `04_展示与实验平台/` | RViz/Gazebo/UE/Web/QGC显示和实验平台入口 | 控制成功判定 |

## 路线图摘要

以下是能力/门禁摘要。当前执行入口以
`Docs/Workflows/mainline_operations_board.md` 的 Next Action 为准：

```text
Goal 1  Sunray/PX4/MAVROS/Gazebo/RViz基础链路和px4ctrl起飞悬停降落
Goal 2  非FAST-LIO状态源下的单机控制基准：阶跃、8字、螺旋、圆形等
Goal 3  FAST-LIO独立建图评价 + Diff-Planner单机 + Diff-Planner swarm三机工程基线
Goal 4  px4ctrl、官方PID、SE3 Basic代表控制器模板
Goal 5  MWORKS px4ctrl Golden Slice：core抽取、离线一致性、生成C/C++、回灌
Goal 6  MWORKS版控制器先回接Diff-Planner单机链路复核，再按结果扩展到三机
FL-EKF  后置状态源替换分支：FAST-LIO经PX4 EKF融合后做A/B对比
G9      控制器族工程模板：官方PID、SE3、DFBC、SMC、PID-INDI、NMPC逐个释放
G9.5/6  论文级高性能名义控制和抗风鲁棒控制复现
G10     增强层矩阵：DOB/ESO、L1/AWFF、INDI、安全过滤、故障分配等消融
G11     全控制器/增强组合MWORKS代码生成闭环，不只做单一最佳候选
G12+    UE真值地图/渲染、QGC二次开发和报告展示，后置于控制器/codegen闭环
```

旧 `P0-P14`、`R1/R2/R3`、visible-thread dispatch、多Agent任务卡等语义不再
作为当前 `Docs/Design` 执行入口。若历史材料需要追溯，只能从
`Docs/Cache/design/` 读取，并且必须以本目录当前文档树重新落地后才可执行。

旧草案、迁移方案和被吸收材料位于 `Docs/Cache/design/`。这些文档只供追溯，
不能作为当前执行入口。
