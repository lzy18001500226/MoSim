# MWORKS UE Scene Smoke Status

Generated models consume accepted UE scene navigation references through `PlannedQuinticReference`.
They are controller-interface smoke models, not final performance scenarios.

| Scene | Model | Segments | Stop Time | MCP Evidence | Quality | Raw / Metrics |
|---|---|---:|---:|---|---|---|
| `factoryenvironmentcollect` | `QuadrotorExperiments.Sunray150UEFactoryLinearMPCSysblockSmoke` | 33 | 31.3258252147 | check_model+simulate_model passed | `smoke_only` | `Results/unreal_scene_mapping/factoryenvironmentcollect/mworks_smoke/raw/sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.csv` / `Results/unreal_scene_mapping/factoryenvironmentcollect/mworks_smoke/metrics/sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.json` |
| `derelictcorridormegascans` | `QuadrotorExperiments.Sunray150UEDerelictLinearMPCSysblockSmoke` | 44 | 39.6 | check_model+simulate_model passed | `smoke_only` | `Results/unreal_scene_mapping/derelictcorridormegascans/mworks_smoke/raw/sunray150_ue_derelictcorridormegascans_linear_mpc_smoke.csv` / `Results/unreal_scene_mapping/derelictcorridormegascans/mworks_smoke/metrics/sunray150_ue_derelictcorridormegascans_linear_mpc_smoke.json` |

Use these outputs to verify that each accepted UE scene can drive the MWORKS controller interface.
Do not report them as completed autonomous navigation or FAST-LIO localization evidence.
