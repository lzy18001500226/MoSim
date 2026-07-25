# Results 结果与证据

`Results/` 保存可追溯实验产出，不存放新的模型源码、控制器实现或配置副本。实验证据按
`Results/<group>/<scene>/<experiment>/{raw,metrics,logs,figures,replay,screenshots}/`
组织：`scene` 只负责场景归类，不能直接共享 `raw/`、`metrics/`或 `figures/`。每个控制器或实验必须有自己的资产目录和清楚的源模型/配置绑定。

## 读取边界

| 目录类型 | 角色 |
|---|---|
| `official/`、`robustness/`、`planning/`、`formation/` | 与赛题、鲁棒性、规划和编队相关的证据路径。 |
| `control_platform/`、`mworks_simulation/`、`generated_mworks/` | MWORKS 控制器、图形化审查和生成码相关证据。 |
| `sunray_ros1/`、`px4_gazebo/`、`gazebo_review/` | 当前 ROS1/Sunray/Gazebo/PX4 运行时证据与审查资产。 |
| `diagnostics/`、`quality/`、`model_checks/`、`static_audits/` | 有界的排障、质量门和静态审计产出，不等同于性能通过。 |
| `agent_*`、`coagent_*`、`codex_*`、`tmp/`、`_quarantine/` | 历史或临时运维资产；不进入正式报告结论，除非被显式引用为 blocker 证据。 |

正式结论仍以具体实验目录中的配置、原始结果、指标、截图
清单和绑定的模型哈希为准。旧运行目录不会因为存在而自动成为当前证据。

`figures/` 只在实验目录下存在，例如 `Results/official/example3_figure8/official_example3_awff_sysblock/figures/`。不要再创建 `Results/official/example3_figure8/figures/` 这种场景级共享图目录，否则 8 字形、螺旋、阶跃、鲁棒性图会重新混在一起。

## 分类规则

| 分类 | 用途 | 审核优先级 |
|---|---|---|
| `official/example3_figure8/` | 官方 Example3 8 字形轨迹，视频与报告高优先级素材 | high |
| `official/example2_helix/` | 官方 Example2 螺旋爬升 | medium |
| `official/example1_step/` | 官方 Example1 阶梯爬升和控制器对比 | medium |
| `robustness/mass20_example1/` | 质量摄动鲁棒性 | medium |
| `robustness/wind_gust_example1/` | 横向阵风鲁棒性 | medium |
| `robustness/rotor1_loss15_example1/` | 单旋翼效率下降鲁棒性 | medium |
| `smoke/` | 0-1 s MCP 链路烟雾验证，只证明流程通，不作为最终展示素材 | low |

## 当前数量

实验数量以 `人工审核清单.csv`、`Results/test_reports/evidence_bundle_audit_*.json` 和目录扫描为准，不在本文档手工维护固定数字，避免结果重生成或新增控制器后出现过期统计。

## 人工审核要求

1. 优先审核 `official/example3_figure8/*/figures/`、`official/example3_figure8/*/raw/`、`official/example3_figure8/*/metrics/`、`official/example3_figure8/*/replay/`。这才是 8 字形轨迹相关证据。
2. `smoke/` 目录默认不进入演示视频和正式报告主图，只保留为自动化链路证据。
3. 每次新增或重生成图后，运行 `Scripts/quality/audit_evidence_bundle.py` 自动刷新 `人工审核清单.csv`，再人工更新 `review_status` 和 `notes`。
4. 图不合格时不要删除同组 raw/metrics/replay/logs；在清单里标注原因，再决定是否重新生成。
