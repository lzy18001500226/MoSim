# 控制器截图说明

本目录按 `类别/控制器ID/` 组织。每条已实现路线优先复制两张图片：

- `01_图形模型.png`：MWORKS/Sysplorer图形化模型。
- `02_仿真结果.png`：结果查看器或对应MIL结果。

当前状态：

- 权威路线：67条。
- 已归档模型图和结果图：65条，共130张。
- 明确阻塞：`mu_synthesis`、`neural_smc`。

## 字节级重复组

以下图片内容完全相同，不能直接作为各路线的独立证明。

模型图重复：

1. `pole_placement_luenberger`、`mrac`、`ndi`、`h2_state_feedback`
2. `dfbc_high_order_attitude`、`dfbc_high_order_bodyrate`
3. `terminal_smc`、`nonsingular_terminal_smc`
4. `dfbc_smooth_robust_attitude`、`dfbc_smooth_robust_bodyrate`、`dfbc_dob_eso_disabled`

结果图重复：

1. `dfbc_basic`、`nmpc_outer`
2. `awff`、`ilc`
3. `terminal_smc`、`nonsingular_terminal_smc`
4. `fopid`、`h2_state_feedback`
5. `official_pid`、`se3_basic`

最低补截量为7张模型图和5张结果图。补截前必须打开对应模型，确认窗口标题、模型内部标题、结果树变量和控制器ID一致。

## 使用边界

固定输入MIL截图用于证明模型可检查、可执行和变量可观测，不自动证明整机轨迹性能通过。正文中的性能结论仍应引用对应的整机仿真、指标文件或Gazebo部署证据。
