# QuadrotorExperiments Migration Disposition Matrix

| Legacy package | Target surface | Disposition | Reason | Keep legacy policy |
|---|---|---|---|---|
| QuadrotorExperiments.OfficialScenarios | MoSimQuadrotorModel.Missions | migrate_to_mosim_formal | 这些是正式任务/控制器闭环对比入口，已经有 MoSimQuadrotorModel.Missions wrapper 和中文说明。 | 保留旧路径作为 compatibility alias/source until YAML/scripts/docs and live checks migrate. |
| QuadrotorExperiments.ControllerBaselines | MoSimQuadrotorModel.Controllers and legacy ControllerBaselines compatibility | keep_legacy_reference_or_baseline | 这些是 PID/AWFF 对比基线，不应被当作新主线任务；控制器正式库入口已经转到 QuadrotorControllerBlocks。 | 长期保留对比/报告复现实验入口，后续只补清晰中文注释和旧入口说明。 |
| QuadrotorExperiments.RobustFaultScenarios | MoSimQuadrotorModel.Robustness | migrate_to_mosim_formal_with_nested_batches | 质量扰动、阵风、安全滤波和故障场景是工程价值主线，应分批归入 Robustness。 | 旧路径保留，PIDBaselines 子包保持对比基线而非正式控制改进成果。 |
| QuadrotorExperiments.RobustFaultScenarios.RotorLoss | MoSimQuadrotorModel.Robustness.RotorLoss | migrate_to_mosim_formal | 单/多电机损失、故障分配、阵风叠加是鲁棒控制核心场景。 | 保留旧路径直到 live package-browser/check_model 和结果脚本完成迁移。 |
| QuadrotorExperiments.RobustFaultScenarios.PIDBaselines | MoSimQuadrotorModel.Robustness.PIDBaselines | keep_legacy_reference_or_baseline | 这些是扰动/故障下的 PID 对照，不应包装成新控制成果。 | 保留为 baseline/reference，中文注释标明对比基线。 |
| QuadrotorExperiments.PlanningScenarios | MoSimQuadrotorModel.Planning | mixed_migrate_and_review_helper | OpenBlocks/CorridorGate 闭环可迁入正式规划场景；NavigationDisplay/ColorMapReview 是审查辅助。 | 保留旧路径；review helper 后续可放 Support/Planning.ReviewTools，不能声明控制验收。 |
| QuadrotorExperiments.SceneTraceScenarios | MoSimQuadrotorModel.SceneTrace.AcceptedScenes | migrate_to_mosim_formal_after_live_review | UE Factory/Derelict trace smoke 有工程价值，但需 live 图形/trace 证据才能升级为 accepted scene。 | 保留旧路径和 smoke 标签，避免误称 UE runtime acceptance。 |
| QuadrotorExperiments.TraceIsolation | MoSimQuadrotorModel.SceneTrace.Isolation | diagnostic_ladder_keep_out_of_primary_user_surface | FactoryTraceIso01-30 是逐层接线/显示隔离诊断梯，不是正式任务场景。 | 保留为诊断工具；后续 package-browser 可折叠或中文标明诊断用途。 |
| QuadrotorExperiments.DynamicsUpgrade | MoSimQuadrotorModel.Dynamics | migrate_to_mosim_formal_source_later | 动力学升级是正式包核心，但 023 不移动真实实现；021 已修正隐藏 sibling .mo 静态解析边界。 | 保留旧实现文件直到 R1/R2 live gates 和 source migration task 明确允许。 |
| QuadrotorExperiments.SystemArchitecture | MoSimQuadrotorModel.System.Architecture | migrate_as_alias_then_live_validate | 完整系统图形和故障场景需要 R2 live 图形/走线审核；当前仅可作为静态 alias surface。 | 保留旧路径；CompleteSystemGraphical 是优先 live 审核对象。 |
| QuadrotorExperiments.SystemModules | MoSimQuadrotorModel.System.Modules | migrate_as_alias_then_live_validate | Perception/FlightController/MissionComputer 等模块是系统包面候选，但需要图形/端口 live 审核。 | 保留模块旧路径和中文接口说明，禁止未经审核改连线。 |
| QuadrotorExperiments.SupportModels | MoSimQuadrotorModel.Support | keep_as_support_not_user_mission | trace/MCP/lookup helper 是工具依赖，不应显示为正式任务或控制结果。 | 保留旧路径并标注工具/支撑用途。 |
| QuadrotorExperiments.FormationScenarios | MoSimQuadrotorModel.Formation | migrate_to_mosim_formal_after_single_uav_gates | 编队场景有展示价值，但应排在单机动力学/鲁棒/规划 gates 之后。 | 保留旧路径到 formation live audit 通过。 |
