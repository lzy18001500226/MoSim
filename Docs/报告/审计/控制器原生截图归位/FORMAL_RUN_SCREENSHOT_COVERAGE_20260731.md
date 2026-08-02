# FormalRunner 运行与截图覆盖审计（2026-07-31）

## 口径

本审计针对报告准备，不改写 G2/G3 冻结矩阵，也不把“有结果文件”自动
升级为“性能通过”。当前报告运行分母为 **48**：

- **46** 条已有 MWORKS Control Profile，来源为
  `Results/control_platform/g6_controller_execution_20260724/G6_EXECUTION_EVIDENCE_AUDIT.json`；
- **1** 条独立 `px4ctrl` MWORKS 基线，来源为
  `Results/control_platform/phase2_full_48_climbpath/px4ctrl/`；
- **1** 条 `pid_awff_linear_eso` 原生 50 s 记录，来源为
  `Results/control_platform/pid_awff_linear_eso_baseline_20260731/RUN_RECORD.json`；
  它完成到 50 s，但终端位置误差 `3412.359226529184 m`，因此是性能失败的负证据。

这个 48 不是冻结 G2/G3 的性能通过数，也不是 48 条同一类型的整机闭环
证据。G6 审计明确记录其 46 条结果窗口截图，证据类别主要是
`internal_fixed_input_probe`；其中 5 条命名整机 Profile 另有
`whole_aircraft_minimum_closure` 类别。`smc_boundary_layer` 与
`nmpc_outer` 后续新增了隔离 Experimental 整机 FormalRunner 记录，但仍
不进入冻结 G2/G3 分母。

## 覆盖结果

| 检查项 | 当前覆盖 | 结论 |
|---|---:|---|
| 已完成运行证据分母 | 48/48 | 46 条 G6 记录 + 1 条 `px4ctrl` 基线 + 1 条 PID-AWFF-LINEAR-ESO 50 s 负证据 |
| `Results/` 中源结果窗口覆盖 | 48/48 控制器 | 46 条 G6 结果截图、`px4ctrl` 的 2 张结果窗口截图和 PID-AWFF-LINEAR-ESO 的 Runner/Result Viewer 截图均可追溯 |
| 报告目录结构图 | 48/48 | 48 张结构图均已归位并作为历史结构展示资产管理；详见 `CONTROLLER_SCREENSHOT_REBUILD_MANIFEST.json` |
| 报告目录当前源绑定的逐控制器结果图 | 0/48 | 尚未完成逐条复制、哈希、运行记录和证据类别绑定 |
| 当前 Experimental 整机记录 | 2 条 | `smc_boundary_layer` 与 `nmpc_outer` 各有独立 50 s `RUN_RECORD`、MSR 和 CSV |

## 两条新增 Experimental 记录

| 控制器 | FormalRunner | CheckModel | 50 s 结果 | 报告标注 |
|---|---|---|---|---|
| `nmpc_outer` | `Experimental.NmpcOuterFormalRunner` | 通过 | `terminal_position_error=0.142974 m`，通过 5 m 门 | 整机仿真通过；不进入冻结 G2/G3 分母 |
| `smc_boundary_layer` | `Experimental.SmcBoundaryLayerFormalRunner` | 通过 | `terminal_position_error=15.029941 m`，失败 5 m 门 | 整机仿真完成但性能门失败；不得标成通过 |

权威记录分别为：

- `Results/control_platform/tier1_formal_promotion_20260731/runs/nmpc_outer/RUN_RECORD.json`
- `Results/control_platform/tier1_formal_promotion_20260731/runs/smc_boundary_layer/RUN_RECORD.json`
- 共同的提升检查为 `Results/control_platform/tier1_formal_promotion_20260731/CHECK_MODEL_RECORD.json`

## 报告使用结论

现在不能写“48 张当前整机仿真截图已经全部归位”。准确表述是：**48
条运行证据可追溯，报告目录的 48 张结构图已归位，但逐控制器当前源绑定的
结果图尚未材料化；其中 G6 的多数结果截图属于固定输入探针，不能统一当作整机图。**

报告插图前必须对每条图片绑定：控制器 ID、FormalRunner、源哈希、运行记录、
结果文件、截图来源和证据类别。`pid_awff_linear_eso` 的结构图是 FormalRunner
接口面，因为其控制核心为 equation Modelica；它不冒充内部图形控制律。
