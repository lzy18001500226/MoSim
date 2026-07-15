# Module Cards

本目录记录增强、观测、安全和故障分配模块。它们不是普通外环控制器的平级
替代项，必须通过 `augmentation_profile`、`safety_profile` 或后续分配层
进入系统。

首批模块入口：

| 文件 | 模块位置 |
| --- | --- |
| `INDI.md` | 增量动态逆增强或后续内环候选 |
| `L1.md` | L1自适应/扰动补偿增强 |
| `AWFF.md` | 气动/风扰前馈增强 |
| `DOB-ESO.md` | 扰动观测和扩张状态观测增强 |
| `ADRC.md` | ADRC/ESO类复合控制增强 |
| `Safety-Filter.md` | 发布前安全过滤 |
| `CBF.md` | 控制屏障函数安全约束 |
| `Reference-Governor.md` | 参考轨迹安全整形 |
| `Geofence.md` | 空间边界约束 |
| `Fault-Allocation.md` | 故障/饱和下的控制分配候选 |

模块不能用于掩盖基准控制器或状态源问题。任何模块启用都必须在 run packet
里记录对应 profile 和禁止声明。
