# 01 控制器平台

本组负责 MoSim 控制器核心、控制接口、增强模块、代码生成、配置管理和
PX4/MAVROS 接入边界。

当前第一阶段只实际释放：

```text
ATTITUDE_THRUST
px4ctrl
official_pid
se3_basic
```

高级控制器和增强模块可以先有规格卡片，但未通过 MWORKS/Gazebo/Sunray 证据
前不得声明为已闭环。

| 文档 | 用途 |
| --- | --- |
| `MWORKS控制器关系与组合架构.md` | 当前控制责任链、PX4/MWORKS替换点、Model Studio实际配置映射、自由组合与认证预设的边界；先读此文理解组合关系 |
| `控制平台接口与闭环实施规范.md` | 分层接口、类型化Frame、Registry、晋级门、Factory简化故障面和前端handoff边界；其原 G1-G7 编号仅供历史追溯 |
| `Docs/Workflows/controller_evidence_closeout.md` | 当前 G1-G7 控制器证据与模型迁移工作流；当前 48 个活动条目与历史 67 条分层路线必须分开读取，其中包括 47 个 MWORKS Control Profile（46 条原始路线和 1 条已物化但性能待评估的 ESO Profile）及 `px4ctrl` 工程/部署基线；七族实测胜出者和七场景矩阵以主线看板为准 |
| `G1_G6闭环验收矩阵.md` | 2026-07-16 历史 H1-H6（原 G1-G6）收尾矩阵，不定义当前任务状态 |
| `开源控制器复用与淘汰矩阵.md` | G4有许可证上游、固定commit、算法家族波次、禁止复制来源和止损规则 |
| `控制体系总览.md` | 算法家族、专题背景和历史控制器目录索引；不再作为当前组合关系权威 |
| `控制器组合与整机动画闭环设计.md` | MWORKS整机母模型、原生结果、曲线和三维动画证据；组合关系以新关系文档为准 |
| `统一控制接口.md` | State、Reference、ControlCommand、Adapter和频率语义 |
| `单机控制器实现.md` | px4ctrl、PID、SE3等单机控制器实现规范 |
| `控制器证据矩阵.md` | 历史 67 条分层路线的证据状态；当前 47 个 MWORKS Control Profile 的七族归属、补充 Runner 记录和报告口径以关系架构文档为准 |
| `代码生成与PX4部署.md` | MWORKS/Sysblock生成C/C++、IController包装和PX4部署门禁 |
| `控制器管理与配置.md` | ControllerProfile、参数版本、切换和回退规则 |
| `控制增强与容错.md` | INDI、L1、AWFF、DOB/ESO、安全过滤、故障容错 |
| `controllers/` | 名义控制器规格卡片 |
| `modules/` | 增强、安全和故障模块规格卡片 |
