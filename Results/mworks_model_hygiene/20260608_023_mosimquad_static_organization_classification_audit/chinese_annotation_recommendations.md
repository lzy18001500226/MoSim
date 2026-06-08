# Chinese Annotation Recommendations

## Package-level wording

- `Baseline`: 官方基线适配：只包装官方 Example1/2/3 和 QuadChassis，用于回归对照。
- `Dynamics`: Sunray150 动力学升级：旋翼/执行器/物理力矩接口与烟测入口。
- `Parameters`: 参数来源与标定记录：记录 Sunray150 参数来源，不等同于参数验收。
- `Missions`: 正式任务场景：官方轨迹任务和主控制器闭环对比入口。
- `Controllers`: 控制器库入口：接入 QuadrotorControllerBlocks 的七个分类控制器包面。
- `Robustness`: 鲁棒/故障/安全：质量扰动、阵风、电机损失、故障分配和安全返航。
- `Planning`: 规划与地图场景：轨迹参考、障碍场、走廊门控和地图审查辅助。
- `SceneTrace`: UE 场景 trace 与显示隔离：已接入场景和逐层隔离诊断入口。
- `System`: 系统级图形和硬件抽象：完整系统故障场景与模块化接口。
- `Formation`: 多机编队扩展：三角编队与 8 字任务。
- `Support`: 支撑工具模型：trace 表、内联引用、lookup smoke、MCP 状态烟测。
- `LegacyCompatibility`: 旧入口兼容：保留历史脚本/证据路径，不作为新开发首选入口。

## Legacy wording rules

- `QuadrotorExperiments` root: 标注为旧实验池与兼容入口，提醒新工作优先使用 `MoSimQuadrotorModel`。
- PID baseline entries: 标注为对比基线，不写成新控制算法成果。
- Trace isolation ladder: 标注为逐层诊断/接线隔离，不写成正式任务或仿真验收。
- Display/review helpers: 标注为图形/地图审查支撑，不声明 controller performance。
- Controller block backups: 标注为内部升级备份，不进入 public package.order。
