# Naming Cleanup Recommendations

Request: `PMO-MWORKS-R2-MOSIMQUAD-STATIC-CLASSIFICATION-LIVE-AUDIT-QUEUE-20260608-015`

These are non-destructive recommendations only. 015 did not rename, move, delete, archive, or edit model implementation files.

| Priority | Area | Recommendation | Why not done in 015 |
|---|---|---|---|
| P0_before_next_live_audit | Package browser visibility | Use MoSimQuadrotorModel root and the 11 ordered categories as the user-facing entry; keep QuadrotorExperiments visible only as legacy compatibility/reference pool. | Requires live package-browser review, not a file move. |
| P0_next_static_or_live_batch | QuadrotorExperiments old flat aliases | Do not delete old flat aliases yet. After scenario YAML/scripts/docs migrate to MoSimQuadrotorModel names and live checks pass, mark selected aliases as permanent legacy or retire candidate. | Retirement would break historical scripts/evidence without reference update and live gates. |
| P1_migration_batch | Dynamics naming | Treat MoSimQuadrotorModel.Dynamics.RotorActuatorCore and PhysicalWrenchAdapter as future canonical names; keep source labels linking to QuadrotorExperiments.DynamicsUpgrade until check_model/smoke evidence is rerun. | Canonical implementation migration requires explicit .mo moves/renames and live checks. |
| P1_migration_batch | Robustness nested grouping | If users need browsable subfolder-style entries for PIDBaselines and RotorLoss, create real subpackage directories in a later task or accept embedded package declarations as current static surface. | 015 forbids creating/moving implementation directories. |
| P1_controller_library | QuadrotorControllerBlocks backup directories | Keep five *_backup directories out of package.order and public controller categories. Later decide archive/delete only with explicit permission and hash evidence. | 015 forbids move/delete/archive. |
| P1_graphical_review | White/blank GUI surfaces reported by user | Queue graphical/layout review for System.Architecture, SceneTrace.Isolation, Planning display/map, and controller graphical blocks with foreground/maximized evidence owned by PMO/CoAgentOps when live review is authorized. | Needs live GUI screenshots and cannot be resolved statically. |
| P2_cleanup | LegacyCompatibility naming | Keep LegacyExperimentPool as a single aggregate until the project chooses permanent aliases. Avoid flattening all 100+ legacy names under formal package surface. | Flattening would obscure canonical categories and may create duplicate names. |
