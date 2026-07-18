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
| `控制平台接口与闭环实施规范.md` | G1-G7短权威入口：分层接口、类型化Frame、Registry、晋级门、Factory简化故障面和前端handoff边界 |
| `开源控制器复用与淘汰矩阵.md` | G4有许可证上游、固定commit、算法家族波次、禁止复制来源和止损规则 |
| `控制体系总览.md` | 控制链路分层、控制器族索引和实现覆盖矩阵入口 |
| `控制器组合与整机动画闭环设计.md` | AWFF边界、控制器分层组合、整机母模型、三维动画验收和剩余工作 |
| `统一控制接口.md` | State、Reference、ControlCommand、Adapter和频率语义 |
| `单机控制器实现.md` | px4ctrl、PID、SE3等单机控制器实现规范 |
| `控制器证据矩阵.md` | 控制器覆盖、Simulink/MWORKS可实现性、开源/资料证据和Gazebo接入门禁 |
| `代码生成与PX4部署.md` | MWORKS/Sysblock生成C/C++、IController包装和PX4部署门禁 |
| `控制器管理与配置.md` | ControllerProfile、参数版本、切换和回退规则 |
| `控制增强与容错.md` | INDI、L1、AWFF、DOB/ESO、安全过滤、故障容错 |
| `controllers/` | 名义控制器规格卡片 |
| `modules/` | 增强、安全和故障模块规格卡片 |
