# 正式 PID 结果体检摘要

检查时间：2026-05-11

本次体检未重新运行 MWORKS 仿真，仅基于 `scenarios/official/*.yaml` 中 `active: true` 的正式场景指向的已有真实 MWORKS MCP 结果重新执行质量门禁，并生成汇总表：

- CSV：`results/summaries/official_pid_health_check/official_pid_health_check.csv`
- Markdown：`results/summaries/official_pid_health_check/official_pid_health_check.md`

## 结论

- `official_example1`：6/6 通过。当前最优 RMSE 为 `official_example1_l1_residual_sysblock`，`position_rmse_m=0.248070`，`total_health_score=55.7823`。
- `official_example2`：5/5 通过。旧版 `enhanced_pid`、`awff_pid`、`awff_sysblock` 已标记为 `active: false`，保留为历史诊断证据；正式矩阵使用对应 `helix_tuned` 分支。
- `official_example3`：5/5 通过。8 字形不是当前主要问题；质量门禁中的形状检查通过，相关性约 `0.99998/0.99994`，XY 轨迹误差约 `0.11 m`。

## 当前推荐使用的正式证据

| 场景 | 推荐结果 | controller | position_rmse_m | total_health_score | 说明 |
|---|---|---|---:|---:|---|
| Example1 阶跃 | `official_example1_l1_residual_sysblock` | l1_residual_sysblock | 0.248070 | 55.7823 | 当前 RMSE 最低，适合作为 P1 创新控制器证据 |
| Example2 螺旋 | `official_example2_awff_pid_helix_tuned` | awff_pid | 0.474799 | 47.9431 | helix_tuned 分支中 RMSE 最低 |
| Example2 螺旋 Sysblock | `official_example2_awff_sysblock_helix_tuned` | awff_sysblock | 0.474850 | 47.9081 | Sysblock 版与 AWFF PID 结果基本一致，可用于结构图支撑 |
| Example3 8字 | `official_example3_awff_pid` | awff_pid | 0.164733 | 60.4183 | RMSE 最低且 8 字形状检查通过 |

## 需要继续优化的点

1. Example2 旧分支保留为 inactive 历史证据；如需复查，可在批量运行或汇总时显式使用 `--include-inactive`。
2. Example3 8 字形当前不需要优先返工；若后面录视频，优先检查三维展示和曲线同步，而不是继续调轨迹本身。
3. 下一阶段可以围绕 `l1_residual_sysblock` 做 P1 鲁棒场景扩展：风扰、质量摄动、旋翼退化，并补消融对比。
