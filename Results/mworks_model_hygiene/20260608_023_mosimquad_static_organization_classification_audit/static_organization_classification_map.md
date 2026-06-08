# 023 Static Organization Classification Map

| Category | Classification | Chinese annotation | Source | Next action |
|---|---|---|---|---|
| Baseline | formal_project_surface_keep | 官方基线适配：只包装官方 Example1/2/3 和 QuadChassis，用于回归对照。 | QuadrotorModel official package | 保持正式入口；后续 live check_model/package-browser 只验证可加载性，不改官方基线。 |
| Dynamics | formal_project_surface_migrate_to_real_source_later | Sunray150 动力学升级：旋翼/执行器/物理力矩接口与烟测入口。 | QuadrotorExperiments.DynamicsUpgrade | 保留当前 wrapper；后续单独任务再决定是否把真实实现迁出旧实验池。 |
| Parameters | formal_project_surface_keep | 参数来源与标定记录：记录 Sunray150 参数来源，不等同于参数验收。 | MoSimQuadrotorModel.Parameters | 后续 R1 参数/动力学验证后再补 live acceptance 证据。 |
| Missions | migrate_to_mosim_formal | 正式任务场景：官方轨迹任务和主控制器闭环对比入口。 | QuadrotorExperiments.OfficialScenarios | 优先迁移 YAML/scripts/docs authoritative references 到 MoSimQuadrotorModel.Missions。 |
| Controllers | formal_project_surface_keep_controller_library_reference | 控制器库入口：接入 QuadrotorControllerBlocks 的七个分类控制器包面。 | QuadrotorControllerBlocks | 保留控制器实现库所有权；MoSimQuadrotorModel.Controllers 只作为浏览入口。 |
| Robustness | migrate_to_mosim_formal_with_nested_batches | 鲁棒/故障/安全：质量扰动、阵风、电机损失、故障分配和安全返航。 | QuadrotorExperiments.RobustFaultScenarios | 拆成 Mass20、WindGust、RotorLoss、Safety 四批；PIDBaselines 保留为对比基线。 |
| Planning | mixed_migrate_and_review_helper | 规划与地图场景：轨迹参考、障碍场、走廊门控和地图审查辅助。 | QuadrotorExperiments.PlanningScenarios | 闭环规划场景迁入正式队列；NavigationDisplay/ColorMapReview 标为 review/support，不作为控制性能验收。 |
| SceneTrace | mixed_migrate_and_diagnostic_ladder | UE 场景 trace 与显示隔离：已接入场景和逐层隔离诊断入口。 | QuadrotorExperiments.SceneTraceScenarios + TraceIsolation | AcceptedScenes 可进入正式 trace 队列；TraceIsolation 01-30 保留诊断梯，不作为用户任务目录。 |
| System | migrate_as_alias_then_live_validate | 系统级图形和硬件抽象：完整系统故障场景与模块化接口。 | QuadrotorExperiments.SystemArchitecture + SystemModules | 后续 live 图形/走线审核优先检查 CompleteSystemGraphical 与模块 package-browser。 |
| Formation | migrate_to_mosim_formal_after_single_uav_gates | 多机编队扩展：三角编队与 8 字任务。 | QuadrotorExperiments.FormationScenarios | 单机任务/鲁棒包面通过后再进入 live 审核；当前只保留正式入口。 |
| Support | keep_as_support_not_user_mission | 支撑工具模型：trace 表、内联引用、lookup smoke、MCP 状态烟测。 | QuadrotorExperiments.SupportModels | 不混入 Missions/Planning；仅作为支撑包面和调试依赖。 |
| LegacyCompatibility | keep_compatibility_until_references_migrated | 旧入口兼容：保留历史脚本/证据路径，不作为新开发首选入口。 | QuadrotorExperiments root hidden aliases | 待 YAML/scripts/docs/live gates 全部迁移后，再决定哪些旧 alias 长期保留。 |
