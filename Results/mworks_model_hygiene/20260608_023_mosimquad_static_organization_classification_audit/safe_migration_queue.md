# Safe Migration Queue

| Batch | Scope | Targets | Action | Risk |
|---|---|---|---|---|
| 023-A missions authority references | YAML/scripts/docs/report references only after live package load/check succeeds | MoSimQuadrotorModel.Missions.* | migrate authoritative references from QuadrotorExperiments.OfficialScenarios to MoSimQuadrotorModel.Missions; keep legacy aliases | medium_requires_live_check_model |
| 023-B robustness nested review | Robustness Mass20/WindGust/Safety/RotorLoss split | MoSimQuadrotorModel.Robustness.* | create user-facing Chinese sub-buckets in future package surface if PMO approves source/package edits; keep PIDBaselines labeled as baseline | medium_large_surface_requires_serialized_live |
| 023-C planning helper separation | Planning closed-loop scenarios versus display/review helpers | MoSimQuadrotorModel.Planning | mark NavigationDisplay and ColorMapReview as review/support; migrate OpenBlocks/CorridorGate closed-loop references after live review | medium_user_visible_category_semantics |
| 023-D scene trace diagnostic folding | SceneTrace AcceptedScenes and Isolation | MoSimQuadrotorModel.SceneTrace | keep FactoryTraceIso01-30 as diagnostic ladder; live review only first/last and representative wiring stages before broader acceptance | high_requires_graphical_evidence |
| 023-E system graphical audit | SystemArchitecture and SystemModules | MoSimQuadrotorModel.System | queue CompleteSystemGraphical, GPSDropout, BatteryLow, OffboardLoss, MissionFailure, GeofenceBreach and module diagrams for R2 live graphical review | high_requires_no_start_route_and_layout_review |
| 023-F legacy compatibility cleanup | QuadrotorExperiments root hidden aliases | QuadrotorExperiments package.mo hidden aliases | after all references migrate, decide permanent report-reproducibility aliases versus deprecated hidden aliases; no deletion in static audit | high_breaks_old_evidence_if_done_early |
