# Drift, Duplicate, Obsolete Surface Report

## Drift from prior evidence

- `R2 015`: partially_stale - 015 formal package map had older counts. Current root package.order has 12 categories including Parameters and current ordered child entries are regenerated from source.
- `R2 021`: current_for_static_parser_boundary - 021 corrected sibling .mo false positives and remains the boundary for static extends resolution, but 023 focuses on user-facing classification, not parser correction.
- `R2 022`: still_blocks_live_audit - 022 live route blocker remains: approved reusable attach-existing/no-start foreground route is missing.

## Duplicate or confusing surfaces

- `MoSimQuadrotorModel.Missions versus QuadrotorExperiments.OfficialScenarios`: intentional_duplicate_alias_surface - Use MoSimQuadrotorModel as user-facing formal surface; keep legacy for compatibility.
- `MoSimQuadrotorModel.Robustness.PIDBaselines versus ControllerBaselines`: baseline_overlap - Keep both as baseline/reference; do not promote PID baseline variants as new control achievements.
- `Planning display/review helpers mixed with closed-loop planning entries`: classification_risk - Future package-surface cleanup should separate review helpers from closed-loop planning models.
- `SceneTrace AcceptedScenes and TraceIsolation`: diagnostic_ladder_risk - Keep Isolation visible only as diagnostic, and do not overpopulate the first live audit batch.

## Rejected/obsolete/review helper candidates

- `QuadrotorExperiments.TraceIsolation.FactoryTraceIso01..FactoryTraceIso30`: diagnostic_ladder_not_obsolete_but_not_primary_surface - 在中文说明中标为 trace/接线逐层诊断，后续 package browser 可放到 SceneTrace.Isolation 折叠入口，不进入 Missions/Planning 主线。
- `QuadrotorExperiments.PlanningScenarios.PlanningNavigationDisplay`: review_display_helper - 保留为 Planning 支撑/显示审查对象；不能当作规划闭环性能验收。
- `QuadrotorExperiments.PlanningScenarios.Sunray150PlanningOpenBlocksColorMapReview`: review_display_helper - 保留为地图/颜色审查入口；下一步 live 图形审核只检查显示完整性，不声明控制性能。
- `Any user-observed white/blank package/browser or diagram tiles`: live_graphical_review_required - 静态审查不能解释白色/空白 GUI；等待 approved no-start MWORKS route 后由 R2 做截图和 written observation。
- `QuadrotorControllerBlocks *_backup/upgrade`: private_backup_not_public_package_surface - 继续排除在 public package.order 和 MoSimQuadrotorModel.Controllers 分类入口之外。
