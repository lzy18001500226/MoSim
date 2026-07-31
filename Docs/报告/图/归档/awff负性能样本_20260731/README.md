# awff 负性能样本归档（2026-07-31）

## 归档原因

`awff` 已跑通 50 s 爬升路径仿真，但**终端位置误差 48.8183 m**，远超 5 m 验收门限，
判定为性能未达标。本目录 4 张图为其 2026-07-31 的 Python 绘图产物（`mosim.plot_results.v1`），
不进入正文第 10 章的 28 条达标控制器详图集合。

## 证据指标

| 项 | 值 |
|---|---|
| controller_id | `awff` |
| status | `fail` |
| failure_class | `terminal_position_error_exceeds_5m` |
| 终端位置误差 | 48.8183 m（门限 5 m） |
| 位置 RMSE | 7.2580 m |
| runner_class | `MoSimQuadrotorModel.Experiment.Runners.Formal.AwffFormalRunner` |
| effective_source | `g3_latest` |
| 运行记录 | `Results/control_platform/phase2_full_48_climbpath/g3_repair/awff/RUN_RECORD.json` |

指标来源：`Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_STATUS.json`

## 口径说明

- `awff` 计入 **ran_to_completion = 38**（跑通），不计入 **performance_accepted = 28**（达标）。
- 归档不等于删除。该样本是"跑通但未达标"这一区间的真实证据，
  如正文需要论述负性能案例，应引用本目录并同时给出上表指标。
- 本目录图为 Python 脚本 `Scripts/results/plot_results.py` 产物，非 Syslab 输出，
  因此即便日后引用也不能算作 Syslab 绘图证据。

口径权威：`Config/control_platform/climbpath_baseline_count_definition.json`
