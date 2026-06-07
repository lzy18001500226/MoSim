# QuadrotorExperiments Reference Migration Risk Register

Request: `RFLY-MOSIM-MWORKS-R2-QUADROTOR-EXPERIMENTS-ORGANIZATION-20260606-004`

This register separates current project references from historical temporary result references. `Results/tmp` hits are evidence-history noise and must not by themselves block display cleanup, but they do explain why old flat paths should remain loadable as compatibility aliases.

## High-Risk Protected Families

- `FactoryTraceIso*` and `FactoryLiteTraceSmoke`: current trace isolation and result-context evidence chain; keep flat paths loadable and add missing category aliases before any browser cleanup.
- `Sunray150RflyStyleRotorDynamics`, `Sunray150Dynamics*`, `Sunray150PhysicalWrench*`: current dynamics upgrade and yaw/wrench evidence chain; must not delete or move without R1 validation.
- `Sunray150CompleteSystem*`: scenario config YAMLs and run workflow docs reference these full paths; protect until configs and docs migrate.
- `Sunray150Planning*`, `Sunray150UE*`, `FormationTriangle*`: current planning/scene/GUI-review surfaces; protect until PMO updates scenarios and evidence docs.
- support models `TraceInlineReference`, `TraceTableReference`, `TraceLookupStandaloneSmoke`, `PlanningNavigationDisplay`, `PlannedQuinticReference`, `EchoMcpStateSmoke`: shared utility surfaces, must remain available.

## Current Formal Reference Samples

### `Example1AWFFSysblockClosedLoop`
- `Config/controllers/awff_sysblock/default.yaml`
- `Config/scenarios/official/example1_awff_sysblock.yaml`
- `Docs/Design/02_模型接口与运行流程.md`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example1AWFFSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/model_checks/awff_sysblock/logs/sysplorer_awff_equation_sysblock_closed_loop_recheck_20260510_summary.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`

### `Example1HelicalFigure8TrailSysblockClosedLoop`
- `Config/scenarios/official/example1_helical_figure8_trail_sysblock.yaml`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example1HelicalFigure8TrailSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`
- `Results/official/example1_helical_figure8/official_example1_helical_figure8_trail_sysblock/replay/official_example1_helical_figure8_trail_sysblock.json`

### `Example1INDISysblockClosedLoop`
- `Config/controllers/awff_indi_sysblock/default.yaml`
- `Config/scenarios/official/example1_awff_indi_sysblock.yaml`
- `Docs/Design/03_控制系统架构.md`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example1INDISysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`

### `Example1L1SysblockClosedLoop`
- `Config/controllers/l1_residual_sysblock/default.yaml`
- `Config/scenarios/official/example1_l1_residual_sysblock.yaml`
- `Docs/Design/03_控制系统架构.md`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example1L1SysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`

### `Example1LinearMPCSysblockClosedLoop`
- `Config/controllers/linear_mpc_sysblock/default.yaml`
- `Config/scenarios/official/example1_linear_mpc_sysblock.yaml`
- `Docs/Workflows/agent_task_ledger.md`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example1LinearMPCSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ACTUATOR-WIRING-ISOLATION-20260606-007.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`

### `Example1Mass20AWFFSysblockClosedLoop`
- `Config/scenarios/robustness/example1_mass20_awff_sysblock.yaml`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example1Mass20AWFFSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`
- `Results/robustness/mass20_example1/robust_mass20_example1_awff_sysblock/replay/robust_mass20_example1_awff_sysblock.json`

### `Example1Mass20L1SysblockClosedLoop`
- `Config/controllers/l1_residual_sysblock/default.yaml`
- `Config/scenarios/robustness/example1_mass20_l1_residual_sysblock.yaml`
- `Docs/Design/03_控制系统架构.md`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example1Mass20L1SysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`

### `Example1Mass20LinearMPCSysblockClosedLoop`
- `Config/controllers/linear_mpc_sysblock/default.yaml`
- `Config/scenarios/robustness/example1_mass20_linear_mpc_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Mass20LinearMPCSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/mass20_example1/robust_mass20_example1_linear_mpc_sysblock/replay/robust_mass20_example1_linear_mpc_sysblock.json`

### `Example1PlanarFigure8TrailSysblockClosedLoop`
- `Config/scenarios/official/example1_planar_figure8_trail_sysblock.yaml`
- `Docs/Design/03_控制系统架构.md`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example1PlanarFigure8TrailSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`
- `Results/official/example1_planar_figure8/official_example1_planar_figure8_trail_sysblock/replay/official_example1_planar_figure8_trail_sysblock.json`

### `Example1QPNMPCSafetyReturnLandSysblockClosedLoop`
- `Config/scenarios/official/example1_qp_nmpc_safety_return_land_sysblock.yaml`
- `Docs/Design/03_控制系统架构.md`
- `Docs/Design/04_安全故障与容错.md`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example1QPNMPCSafetyReturnLandSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`

### `Example1QPNMPCSafetySysblockClosedLoop`
- `Config/controllers/nmpc_indi_l1/default.yaml`
- `Config/scenarios/official/example1_qp_nmpc_safety_sysblock.yaml`
- `Docs/Design/03_控制系统架构.md`
- `Docs/Design/04_安全故障与容错.md`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example1QPNMPCSafetySysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`

### `Example1Rotor1Loss15AWFFSysblockClosedLoop`
- `Config/scenarios/robustness/example1_rotor1_loss15_awff_sysblock.yaml`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example1Rotor1Loss15AWFFSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-ECHO-ADAPTER-CONTRACT-20260606-001.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`
- `Results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_awff_sysblock/replay/robust_rotor1_loss15_example1_awff_sysblock.json`

### `Example1Rotor1Loss15L1FaultAllocationSysblockClosedLoop`
- `Config/controllers/l1_fault_allocation_sysblock/default.yaml`
- `Config/scenarios/robustness/example1_rotor1_loss15_l1_fault_allocation_sysblock.yaml`
- `Docs/Design/03_控制系统架构.md`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example1Rotor1Loss15L1FaultAllocationSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`

### `Example1Rotor1Loss15L1MultiFaultIsolationSysblockClosedLoop`
- `Config/controllers/l1_multi_fault_isolation_sysblock/default.yaml`
- `Config/scenarios/robustness/example1_rotor1_loss15_l1_multi_fault_isolation_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor1Loss15L1MultiFaultIsolationSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_l1_multi_fault_isolation_sysblock/replay/robust_rotor1_loss15_example1_l1_multi_fault_isolation_sysblock.json`

### `Example1Rotor1Loss15L1OnlineFaultAllocationSysblockClosedLoop`
- `Config/controllers/l1_online_fault_allocation_sysblock/default.yaml`
- `Config/scenarios/robustness/example1_rotor1_loss15_l1_online_fault_allocation_sysblock.yaml`
- `Docs/Design/03_控制系统架构.md`
- `Docs/Design/04_安全故障与容错.md`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example1Rotor1Loss15L1OnlineFaultAllocationSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`

### `Example1Rotor1Loss15L1SysblockClosedLoop`
- `Config/controllers/l1_residual_sysblock/default.yaml`
- `Config/scenarios/robustness/example1_rotor1_loss15_l1_residual_sysblock.yaml`
- `Docs/Design/03_控制系统架构.md`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example1Rotor1Loss15L1SysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`

### `Example1Rotor1Loss15LinearMPCOnlineFaultAllocationSysblockClosedLoop`
- `Config/controllers/linear_mpc_online_fault_allocation_sysblock/default.yaml`
- `Config/scenarios/robustness/example1_rotor1_loss15_linear_mpc_online_fault_allocation_sysblock.yaml`
- `Docs/Design/03_控制系统架构.md`
- `Models/QuadrotorExperiments/Example1Rotor1Loss15LinearMPCOnlineFaultAllocationSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_linear_mpc_online_fault_allocation_sysblock/replay/robust_rotor1_loss15_example1_linear_mpc_online_fault_allocation_sysblock.json`

### `Example1Rotor1Loss15LinearMPCSysblockClosedLoop`
- `Config/controllers/linear_mpc_sysblock/default.yaml`
- `Config/scenarios/robustness/example1_rotor1_loss15_linear_mpc_sysblock.yaml`
- `Docs/Design/03_控制系统架构.md`
- `Models/QuadrotorExperiments/Example1Rotor1Loss15LinearMPCSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor1_loss15_example1/robust_rotor1_loss15_example1_linear_mpc_sysblock/replay/robust_rotor1_loss15_example1_linear_mpc_sysblock.json`

### `Example1Rotor1Loss15WindGustAWFFFaultCompensationSysblockClosedLoop`
- `Config/controllers/awff_fault_compensation_sysblock/default.yaml`
- `Config/scenarios/robustness/example1_rotor1_loss15_wind_gust_awff_fault_compensation_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor1Loss15WindGustAWFFFaultCompensationSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor1_loss15_wind_gust_example1/robust_rotor1_loss15_wind_gust_example1_awff_fault_compensation_sysblock/replay/robust_rotor1_loss15_wind_gust_example1_awff_fault_compensation_sysblock.json`

### `Example1Rotor1Loss15WindGustAWFFSysblockClosedLoop`
- `Config/scenarios/robustness/example1_rotor1_loss15_wind_gust_awff_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor1Loss15WindGustAWFFSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-ECHO-ADAPTER-CONTRACT-20260606-001.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor1_loss15_wind_gust_example1/robust_rotor1_loss15_wind_gust_example1_awff_sysblock/replay/robust_rotor1_loss15_wind_gust_example1_awff_sysblock.json`

### `Example1Rotor1Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop`
- `Config/scenarios/robustness/example1_rotor1_loss15_wind_gust_l1_multi_fault_isolation_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor1Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor1_loss15_wind_gust_example1/robust_rotor1_loss15_wind_gust_example1_l1_multi_fault_isolation_sysblock/native_result/native_result_manifest.json`
- `Results/robustness/rotor1_loss15_wind_gust_example1/robust_rotor1_loss15_wind_gust_example1_l1_multi_fault_isolation_sysblock/replay/robust_rotor1_loss15_wind_gust_example1_l1_multi_fault_isolation_sysblock.json`

### `Example1Rotor1Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop`
- `Config/controllers/linear_mpc_online_fault_allocation_sysblock/default.yaml`
- `Config/scenarios/robustness/example1_rotor1_loss15_wind_gust_linear_mpc_online_fault_allocation_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor1Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor1_loss15_wind_gust_example1/robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock/native_result/native_result_manifest.json`
- `Results/robustness/rotor1_loss15_wind_gust_example1/robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock/replay/robust_rotor1_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock.json`

### `Example1Rotor2Loss15AWFFSysblockClosedLoop`
- `Config/scenarios/robustness/example1_rotor2_loss15_awff_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor2Loss15AWFFSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor2_loss15_example1/robust_rotor2_loss15_example1_awff_sysblock/replay/robust_rotor2_loss15_example1_awff_sysblock.json`

### `Example1Rotor2Loss15L1MultiFaultIsolationSysblockClosedLoop`
- `Config/controllers/l1_multi_fault_isolation_sysblock/default.yaml`
- `Config/scenarios/robustness/example1_rotor2_loss15_l1_multi_fault_isolation_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor2Loss15L1MultiFaultIsolationSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor2_loss15_example1/robust_rotor2_loss15_example1_l1_multi_fault_isolation_sysblock/replay/robust_rotor2_loss15_example1_l1_multi_fault_isolation_sysblock.json`

### `Example1Rotor2Loss15WindGustAWFFSysblockClosedLoop`
- `Config/scenarios/robustness/example1_rotor2_loss15_wind_gust_awff_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor2Loss15WindGustAWFFSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor2_loss15_wind_gust_example1/robust_rotor2_loss15_wind_gust_example1_awff_sysblock/replay/robust_rotor2_loss15_wind_gust_example1_awff_sysblock.json`

### `Example1Rotor2Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop`
- `Config/scenarios/robustness/example1_rotor2_loss15_wind_gust_l1_multi_fault_isolation_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor2Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor2_loss15_wind_gust_example1/robust_rotor2_loss15_wind_gust_example1_l1_multi_fault_isolation_sysblock/native_result/native_result_manifest.json`
- `Results/robustness/rotor2_loss15_wind_gust_example1/robust_rotor2_loss15_wind_gust_example1_l1_multi_fault_isolation_sysblock/replay/robust_rotor2_loss15_wind_gust_example1_l1_multi_fault_isolation_sysblock.json`

### `Example1Rotor2Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop`
- `Config/controllers/linear_mpc_online_fault_allocation_sysblock/default.yaml`
- `Config/scenarios/robustness/example1_rotor2_loss15_wind_gust_linear_mpc_online_fault_allocation_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor2Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor2_loss15_wind_gust_example1/robust_rotor2_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock/native_result/native_result_manifest.json`
- `Results/robustness/rotor2_loss15_wind_gust_example1/robust_rotor2_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock/replay/robust_rotor2_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock.json`

### `Example1Rotor3Loss15AWFFSysblockClosedLoop`
- `Config/scenarios/robustness/example1_rotor3_loss15_awff_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor3Loss15AWFFSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor3_loss15_example1/robust_rotor3_loss15_example1_awff_sysblock/replay/robust_rotor3_loss15_example1_awff_sysblock.json`

### `Example1Rotor3Loss15L1MultiFaultIsolationSysblockClosedLoop`
- `Config/controllers/l1_multi_fault_isolation_sysblock/default.yaml`
- `Config/scenarios/robustness/example1_rotor3_loss15_l1_multi_fault_isolation_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor3Loss15L1MultiFaultIsolationSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor3_loss15_example1/robust_rotor3_loss15_example1_l1_multi_fault_isolation_sysblock/replay/robust_rotor3_loss15_example1_l1_multi_fault_isolation_sysblock.json`

### `Example1Rotor3Loss15WindGustAWFFSysblockClosedLoop`
- `Config/scenarios/robustness/example1_rotor3_loss15_wind_gust_awff_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor3Loss15WindGustAWFFSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor3_loss15_wind_gust_example1/robust_rotor3_loss15_wind_gust_example1_awff_sysblock/replay/robust_rotor3_loss15_wind_gust_example1_awff_sysblock.json`

### `Example1Rotor3Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop`
- `Config/scenarios/robustness/example1_rotor3_loss15_wind_gust_l1_multi_fault_isolation_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor3Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor3_loss15_wind_gust_example1/robust_rotor3_loss15_wind_gust_example1_l1_multi_fault_isolation_sysblock/native_result/native_result_manifest.json`
- `Results/robustness/rotor3_loss15_wind_gust_example1/robust_rotor3_loss15_wind_gust_example1_l1_multi_fault_isolation_sysblock/replay/robust_rotor3_loss15_wind_gust_example1_l1_multi_fault_isolation_sysblock.json`

### `Example1Rotor3Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop`
- `Config/controllers/linear_mpc_online_fault_allocation_sysblock/default.yaml`
- `Config/scenarios/robustness/example1_rotor3_loss15_wind_gust_linear_mpc_online_fault_allocation_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor3Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor3_loss15_wind_gust_example1/robust_rotor3_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock/native_result/native_result_manifest.json`
- `Results/robustness/rotor3_loss15_wind_gust_example1/robust_rotor3_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock/replay/robust_rotor3_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock.json`

### `Example1Rotor4Loss15AWFFSysblockClosedLoop`
- `Config/scenarios/robustness/example1_rotor4_loss15_awff_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor4Loss15AWFFSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor4_loss15_example1/robust_rotor4_loss15_example1_awff_sysblock/replay/robust_rotor4_loss15_example1_awff_sysblock.json`

### `Example1Rotor4Loss15L1MultiFaultIsolationSysblockClosedLoop`
- `Config/controllers/l1_multi_fault_isolation_sysblock/default.yaml`
- `Config/scenarios/robustness/example1_rotor4_loss15_l1_multi_fault_isolation_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor4Loss15L1MultiFaultIsolationSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor4_loss15_example1/robust_rotor4_loss15_example1_l1_multi_fault_isolation_sysblock/replay/robust_rotor4_loss15_example1_l1_multi_fault_isolation_sysblock.json`

### `Example1Rotor4Loss15WindGustAWFFSysblockClosedLoop`
- `Config/scenarios/robustness/example1_rotor4_loss15_wind_gust_awff_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor4Loss15WindGustAWFFSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor4_loss15_wind_gust_example1/robust_rotor4_loss15_wind_gust_example1_awff_sysblock/replay/robust_rotor4_loss15_wind_gust_example1_awff_sysblock.json`

### `Example1Rotor4Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop`
- `Config/scenarios/robustness/example1_rotor4_loss15_wind_gust_l1_multi_fault_isolation_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor4Loss15WindGustL1MultiFaultIsolationSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor4_loss15_wind_gust_example1/robust_rotor4_loss15_wind_gust_example1_l1_multi_fault_isolation_sysblock/native_result/native_result_manifest.json`
- `Results/robustness/rotor4_loss15_wind_gust_example1/robust_rotor4_loss15_wind_gust_example1_l1_multi_fault_isolation_sysblock/replay/robust_rotor4_loss15_wind_gust_example1_l1_multi_fault_isolation_sysblock.json`

### `Example1Rotor4Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop`
- `Config/controllers/linear_mpc_online_fault_allocation_sysblock/default.yaml`
- `Config/scenarios/robustness/example1_rotor4_loss15_wind_gust_linear_mpc_online_fault_allocation_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1Rotor4Loss15WindGustLinearMPCOnlineFaultAllocationSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/rotor4_loss15_wind_gust_example1/robust_rotor4_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock/native_result/native_result_manifest.json`
- `Results/robustness/rotor4_loss15_wind_gust_example1/robust_rotor4_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock/replay/robust_rotor4_loss15_wind_gust_example1_linear_mpc_online_fault_allocation_sysblock.json`

### `Example1WindGustAWFFSysblockClosedLoop`
- `Config/scenarios/robustness/example1_wind_gust_awff_sysblock.yaml`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example1WindGustAWFFSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-ECHO-ADAPTER-CONTRACT-20260606-001.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`
- `Results/robustness/wind_gust_example1/robust_wind_gust_example1_awff_sysblock/replay/robust_wind_gust_example1_awff_sysblock.json`

### `Example1WindGustL1SysblockClosedLoop`
- `Config/controllers/l1_residual_sysblock/default.yaml`
- `Config/scenarios/robustness/example1_wind_gust_l1_residual_sysblock.yaml`
- `Docs/Design/03_控制系统架构.md`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example1WindGustL1SysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`

### `Example1WindGustLinearMPCSysblockClosedLoop`
- `Config/controllers/linear_mpc_sysblock/default.yaml`
- `Config/scenarios/robustness/example1_wind_gust_linear_mpc_sysblock.yaml`
- `Models/QuadrotorExperiments/Example1WindGustLinearMPCSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/robustness/wind_gust_example1/robust_wind_gust_example1_linear_mpc_sysblock/replay/robust_wind_gust_example1_linear_mpc_sysblock.json`

### `Example2AWFFSysblockClosedLoop`
- `Config/controllers/awff_sysblock/default.yaml`
- `Config/scenarios/official/example2_awff_sysblock.yaml`
- `Docs/Design/02_模型接口与运行流程.md`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example2AWFFSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/Example2HelixTunedAWFFSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`

### `Example2HelixTunedAWFFSysblockClosedLoop`
- `Config/controllers/awff_sysblock/default.yaml`
- `Config/scenarios/official/example2_awff_sysblock_helix_tuned.yaml`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example2HelixTunedAWFFSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`
- `Results/official/example2_helix/official_example2_awff_sysblock_helix_tuned/replay/official_example2_awff_sysblock_helix_tuned.json`

### `Example2HelixTunedINDISysblockClosedLoop`
- `Config/controllers/awff_indi_sysblock/default.yaml`
- `Config/scenarios/official/example2_awff_indi_sysblock_helix_tuned.yaml`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example2HelixTunedINDISysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`
- `Results/official/example2_helix/official_example2_awff_indi_sysblock_helix_tuned/replay/official_example2_awff_indi_sysblock_helix_tuned.json`

### `Example2INDISysblockClosedLoop`
- `Config/controllers/awff_indi_sysblock/default.yaml`
- `Config/scenarios/official/example2_awff_indi_sysblock.yaml`
- `Models/QuadrotorExperiments/Example2HelixTunedINDISysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/Example2INDISysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`

### `Example2LinearMPCSysblockClosedLoop`
- `Config/controllers/linear_mpc_sysblock/default.yaml`
- `Config/scenarios/official/example2_linear_mpc_sysblock.yaml`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example2LinearMPCSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`
- `Results/official/example2_helix/official_example2_linear_mpc_sysblock/replay/official_example2_linear_mpc_sysblock.json`

### `Example3AWFFSysblockClosedLoop`
- `Config/controllers/awff_sysblock/default.yaml`
- `Config/scenarios/official/example3_awff_sysblock.yaml`
- `Docs/Design/02_模型接口与运行流程.md`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example3AWFFSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`

### `Example3INDISysblockClosedLoop`
- `Config/controllers/awff_indi_sysblock/default.yaml`
- `Config/scenarios/official/example3_awff_indi_sysblock.yaml`
- `Docs/Design/03_控制系统架构.md`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example3INDISysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`

### `Example3L1SysblockClosedLoop`
- `Config/controllers/l1_residual_sysblock/default.yaml`
- `Config/scenarios/official/example3_l1_residual_sysblock.yaml`
- `Docs/Design/03_控制系统架构.md`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example3L1SysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`

### `Example3LinearMPCSysblockClosedLoop`
- `Config/controllers/linear_mpc_sysblock/default.yaml`
- `Config/scenarios/official/example3_linear_mpc_sysblock.yaml`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Example3LinearMPCSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`
- `Results/official/example3_figure8/official_example3_linear_mpc_sysblock/replay/official_example3_linear_mpc_sysblock.json`

### `FactoryLiteTraceSmoke`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/FactoryLiteTraceSmoke.mo`
- `Models/QuadrotorExperiments/FactoryTraceIso01FullDisplaySmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-INCREMENTAL-TRACE-ISOLATION-20260606-006.json`
- `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-CONTROL-NEXT-SENSOR-DISPLAY-GROUP-20260606-017.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-FACTORY-LITE-TRACE-20260606-005.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-POSITION-BRIDGE-20260606-016.json`

### `FactoryTraceIso01FullDisplaySmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso01FullDisplaySmoke.mo`
- `Models/QuadrotorExperiments/FactoryTraceIso02ControllerOnlySmoke.mo`
- `Models/QuadrotorExperiments/FactoryTraceIso03PlantHoverStackSmoke.mo`
- `Models/QuadrotorExperiments/FactoryTraceIso05CleanHoverSumSmoke.mo`
- `Models/QuadrotorExperiments/FactoryTraceIso06CleanControllerPlantWiringSmoke.mo`
- `Models/QuadrotorExperiments/FactoryTraceIso07CleanControllerOpenFeedbackSmoke.mo`
- `Models/QuadrotorExperiments/FactoryTraceIso08PositionFeedbackSmoke.mo`
- `Models/QuadrotorExperiments/FactoryTraceIso09PositionAttitudeFeedbackSmoke.mo`

### `FactoryTraceIso02ControllerOnlySmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso02ControllerOnlySmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-INCREMENTAL-TRACE-ISOLATION-20260606-006.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_trace_consumption/incremental_trace_isolation_20260606_006/incremental_trace_isolation_probe.json`
- `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`

### `FactoryTraceIso03PlantHoverStackSmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso03PlantHoverStackSmoke.mo`
- `Models/QuadrotorExperiments/FactoryTraceIso04ControllerPlantWiringSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-ACTUATOR-WIRING-ISOLATION-20260606-007.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-INCREMENTAL-TRACE-ISOLATION-20260606-006.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_trace_consumption/incremental_trace_isolation_20260606_006/incremental_trace_isolation_probe.json`
- `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`

### `FactoryTraceIso04ControllerPlantWiringSmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso04ControllerPlantWiringSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-ACTUATOR-WIRING-ISOLATION-20260606-007.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-INCREMENTAL-TRACE-ISOLATION-20260606-006.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_trace_consumption/incremental_trace_isolation_20260606_006/incremental_trace_isolation_probe.json`
- `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`

### `FactoryTraceIso05CleanHoverSumSmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso05CleanHoverSumSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ACTUATOR-WIRING-ISOLATION-20260606-007.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_trace_consumption/actuator_wiring_isolation_20260606_007/actuator_wiring_isolation_probe.json`
- `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`

### `FactoryTraceIso06CleanControllerPlantWiringSmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso06CleanControllerPlantWiringSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-SENSOR-FEEDBACK-ISOLATION-20260606-008.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ACTUATOR-WIRING-ISOLATION-20260606-007.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_trace_consumption/actuator_wiring_isolation_20260606_007/actuator_wiring_isolation_probe.json`
- `Results/mworks_trace_consumption/sensor_feedback_isolation_20260606_008/sensor_feedback_isolation_probe.json`
- `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`

### `FactoryTraceIso07CleanControllerOpenFeedbackSmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso07CleanControllerOpenFeedbackSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-SENSOR-FEEDBACK-ISOLATION-20260606-008.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ACTUATOR-WIRING-ISOLATION-20260606-007.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_trace_consumption/actuator_wiring_isolation_20260606_007/actuator_wiring_isolation_probe.json`
- `Results/mworks_trace_consumption/sensor_feedback_isolation_20260606_008/sensor_feedback_isolation_probe.json`
- `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`

### `FactoryTraceIso08PositionFeedbackSmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso08PositionFeedbackSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-ISOLATION-20260606-009.json`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-INTERMEDIARY-20260606-010.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-SENSOR-FEEDBACK-ISOLATION-20260606-008.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_trace_consumption/attitude_feedback_isolation_20260606_009/attitude_feedback_isolation_probe.json`
- `Results/mworks_trace_consumption/attitude_intermediary_20260606_010/attitude_intermediary_probe.json`

### `FactoryTraceIso09PositionAttitudeFeedbackSmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso09PositionAttitudeFeedbackSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-ISOLATION-20260606-009.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-SENSOR-FEEDBACK-ISOLATION-20260606-008.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_trace_consumption/attitude_feedback_isolation_20260606_009/attitude_feedback_isolation_probe.json`
- `Results/mworks_trace_consumption/sensor_feedback_isolation_20260606_008/sensor_feedback_isolation_probe.json`
- `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`

### `FactoryTraceIso10RollFeedbackSmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso10RollFeedbackSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-INTERMEDIARY-20260606-010.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-ISOLATION-20260606-009.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_trace_consumption/attitude_feedback_isolation_20260606_009/attitude_feedback_isolation_probe.json`
- `Results/mworks_trace_consumption/attitude_feedback_isolation_20260606_009/attitude_feedback_mcp_log.json`
- `Results/mworks_trace_consumption/attitude_intermediary_20260606_010/attitude_intermediary_probe.json`

### `FactoryTraceIso11PitchFeedbackSmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso11PitchFeedbackSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-ISOLATION-20260606-009.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_trace_consumption/attitude_feedback_isolation_20260606_009/attitude_feedback_isolation_probe.json`
- `Results/mworks_trace_consumption/attitude_feedback_isolation_20260606_009/attitude_feedback_mcp_log.json`
- `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`

### `FactoryTraceIso12RollFeedbackNegatedSmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso12RollFeedbackNegatedSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-ISOLATION-20260606-009.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_trace_consumption/attitude_feedback_isolation_20260606_009/attitude_feedback_isolation_probe.json`
- `Results/mworks_trace_consumption/attitude_feedback_isolation_20260606_009/attitude_feedback_mcp_log.json`
- `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`

### `FactoryTraceIso13PitchFeedbackNegatedSmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso13PitchFeedbackNegatedSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-ISOLATION-20260606-009.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_trace_consumption/attitude_feedback_isolation_20260606_009/attitude_feedback_isolation_probe.json`
- `Results/mworks_trace_consumption/attitude_feedback_isolation_20260606_009/attitude_feedback_mcp_log.json`
- `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`

### `FactoryTraceIso14ConstantAttitudeInputSmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso14ConstantAttitudeInputSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-DECOUPLING-20260606-011.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-INTERMEDIARY-20260606-010.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_trace_consumption/attitude_intermediary_20260606_010/attitude_intermediary_mcp_log.json`
- `Results/mworks_trace_consumption/attitude_intermediary_20260606_010/attitude_intermediary_probe.json`
- `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`

### `FactoryTraceIso15TableAttitudeInputSmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso15TableAttitudeInputSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-DECOUPLING-20260606-011.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-INTERMEDIARY-20260606-010.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_trace_consumption/attitude_intermediary_20260606_010/attitude_intermediary_mcp_log.json`
- `Results/mworks_trace_consumption/attitude_intermediary_20260606_010/attitude_intermediary_probe.json`
- `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`

### `FactoryTraceIso16RealExpressionAngleSmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso16RealExpressionAngleSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-DECOUPLING-20260606-011.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-INTERMEDIARY-20260606-010.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_trace_consumption/attitude_intermediary_20260606_010/attitude_intermediary_mcp_log.json`
- `Results/mworks_trace_consumption/attitude_intermediary_20260606_010/attitude_intermediary_probe.json`
- `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`

### `FactoryTraceIso17SampleHoldAngleSmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso17SampleHoldAngleSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-DECOUPLING-20260606-011.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_trace_consumption/attitude_decoupling_20260606_011/attitude_decoupling_mcp_log.json`
- `Results/mworks_trace_consumption/attitude_decoupling_20260606_011/attitude_decoupling_probe.json`
- `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`

### `FactoryTraceIso18ProjectAttitudeEstimatorSmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso18ProjectAttitudeEstimatorSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-DECOUPLING-20260606-011.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_trace_consumption/attitude_decoupling_20260606_011/attitude_decoupling_mcp_log.json`
- `Results/mworks_trace_consumption/attitude_decoupling_20260606_011/attitude_decoupling_probe.json`
- `Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json`

### `FactoryTraceIso19RollPitchEstimatorSmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso19RollPitchEstimatorSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-YAW-RATE-DECOUPLING-20260606-013.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-PITCH-DECOUPLING-20260606-012.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_trace_consumption/pitch_decoupling_20260606_012/pitch_decoupling_mcp_log.json`
- `Results/mworks_trace_consumption/pitch_decoupling_20260606_012/pitch_decoupling_probe.json`
- `Results/p0_runs/rfly_mosim_p0_slice_20260606/P0_BUNDLE_AUDIT.json`

### `FactoryTraceIso20RollPitchYawEstimatorSmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso20RollPitchYawEstimatorSmoke.mo`
- `Models/QuadrotorExperiments/FactoryTraceIso21ControllerRateAliasSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-RATE-FEEDBACK-ISOLATION-20260606-014.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-RATE-FEEDBACK-ISOLATION-20260606-014.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-YAW-RATE-DECOUPLING-20260606-013.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_trace_consumption/rate_feedback_isolation_20260606_014/rate_feedback_isolation_probe.json`

### `FactoryTraceIso21ControllerRateAliasSmoke`
- `Models/QuadrotorExperiments/FactoryTraceIso21ControllerRateAliasSmoke.mo`
- `Models/QuadrotorExperiments/FactoryTraceIso22SensorDisplayReconnectSmoke.mo`
- `Models/QuadrotorExperiments/FactoryTraceIso23PositionSampleHoldBridgeSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-POSITION-BRIDGE-20260606-016.json`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-SENSOR-BUS-RECONNECT-20260606-015.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-POSITION-BRIDGE-20260606-016.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-RATE-FEEDBACK-ISOLATION-20260606-014.json`

### `FactoryTraceIso22SensorDisplayReconnectSmoke`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/FactoryTraceIso22SensorDisplayReconnectSmoke.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-POSITION-BRIDGE-20260606-016.json`
- `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-CONTROL-SENSOR-BUS-RECONNECT-20260606-015.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/category_migration_table.md`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/implementation_strategy.md`
- `Results/mworks_trace_consumption/position_bridge_20260606_016/position_bridge_probe.json`

### `FactoryTraceIso23PositionSampleHoldBridgeSmoke`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/FactoryTraceIso23PositionSampleHoldBridgeSmoke.mo`
- `Models/QuadrotorExperiments/FactoryTraceIso24DirectAttitudeFeedbackSmoke.mo`
- `Models/QuadrotorExperiments/FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-BRIDGE-20260606-019.json`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-FIRST-CONTROL-FEEDBACK-GROUP-20260606-018.json`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-NEXT-SENSOR-DISPLAY-GROUP-20260606-017.json`

### `FactoryTraceIso24DirectAttitudeFeedbackSmoke`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/FactoryTraceIso24DirectAttitudeFeedbackSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-BRIDGE-20260606-019.json`
- `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-CONTROL-FIRST-CONTROL-FEEDBACK-GROUP-20260606-018.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-BRIDGE-20260606-019.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-R2-STATIC-GUI-REVIEW-PREP-20260606-003.json`
- `Results/mworks_model_hygiene/20260606_003_static_gui_review_prep/manual_gui_review_checklist.md`

### `FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/FactoryTraceIso25SampleHoldAttitudeFeedbackSmoke.mo`
- `Models/QuadrotorExperiments/FactoryTraceIso26ControllerOutputAliasSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-DOWNSTREAM-OUTPUT-GROUP-20260606-020.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ATTITUDE-FEEDBACK-BRIDGE-20260606-019.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-DOWNSTREAM-OUTPUT-GROUP-20260606-020.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-R2-STATIC-GUI-REVIEW-PREP-20260606-003.json`

### `FactoryTraceIso26ControllerOutputAliasSmoke`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/FactoryTraceIso26ControllerOutputAliasSmoke.mo`
- `Models/QuadrotorExperiments/FactoryTraceIso27ActuatorInputAliasSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-ACTUATOR-PREFLIGHT-GROUP-20260606-021.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-ACTUATOR-PREFLIGHT-GROUP-20260606-021.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-DOWNSTREAM-OUTPUT-GROUP-20260606-020.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-R2-STATIC-GUI-REVIEW-PREP-20260606-003.json`

### `FactoryTraceIso27ActuatorInputAliasSmoke`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/FactoryTraceIso27ActuatorInputAliasSmoke.mo`
- `Models/QuadrotorExperiments/FactoryTraceIso28ActuatorToWrenchBridgeSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-010.json`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-012.json`
- `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-010.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-RESUME-20260606-014.json`

### `FactoryTraceIso28ActuatorToWrenchBridgeSmoke`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/FactoryTraceIso28ActuatorToWrenchBridgeSmoke.mo`
- `Models/QuadrotorExperiments/FactoryTraceIso29ExternalFrameWrenchBoundarySmoke.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-WRENCH-TO-EXTERNAL-FRAME-BOUNDARY-20260606-015.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-RESUME-20260606-014.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-R2-STATIC-GUI-REVIEW-PREP-20260606-003.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-WRENCH-TO-EXTERNAL-FRAME-BOUNDARY-20260606-015.json`
- `Results/mworks_dynamics_upgrade/20260606_014_actuator_to_wrench_bridge_resume/EVIDENCE_SUMMARY.md`

### `FactoryTraceIso29ExternalFrameWrenchBoundarySmoke`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/FactoryTraceIso29ExternalFrameWrenchBoundarySmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-WRENCH-TO-EXTERNAL-FRAME-BOUNDARY-20260606-015.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-POST-ISO29-ONE-BOUNDARY-20260606-016.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-R2-STATIC-GUI-REVIEW-PREP-20260606-003.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-WRENCH-TO-EXTERNAL-FRAME-BOUNDARY-20260606-015.json`
- `Results/mworks_dynamics_upgrade/20260606_015_wrench_to_external_frame_boundary/EVIDENCE_SUMMARY.md`

### `FactoryTraceIso30ExternalBodyStateBoundarySmoke`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-DYNAMICS-YAW-TRANSIENT-EVIDENCE-GATE-20260606-017.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-DYNAMICS-YAW-TRANSIENT-EVIDENCE-GATE-20260606-017.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-POST-ISO29-ONE-BOUNDARY-20260606-016.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-R2-GRAPHICAL-MODEL-AUDIT-INVENTORY-20260606-002.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-R2-STATIC-GUI-REVIEW-PREP-20260606-003.json`
- `Results/mworks_dynamics_upgrade/20260606_016_post_iso29_one_boundary/EVIDENCE_SUMMARY.md`

### `EchoMcpStateSmoke`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/EchoMcpStateSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-ECHO-LIVE-DOWNLINK-PREFLIGHT-20260606-004.json`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-POST-GUI-SENTINEL-HEALTH-GATE-20260606-009.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-ECHO-LIVE-DOWNLINK-PREFLIGHT-20260606-004.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-ECHO-MCP-STATE-SMOKE-20260606-002.json`
- `Results/mworks_echo_producer_smoke/20260606_002_mcp_state/echo_mcp_state_mcp_log.json`

### `PlannedQuinticReference`
- `Config/scenarios/planning/sunray150_planning_corridor_gate_awff_sysblock.yaml`
- `Config/scenarios/planning/sunray150_planning_corridor_gate_linear_mpc_sysblock.yaml`
- `Config/scenarios/planning/sunray150_planning_open_blocks_awff_sysblock.yaml`
- `Config/scenarios/planning/sunray150_planning_open_blocks_linear_mpc_sysblock.yaml`
- `Config/scenarios/planning/sunray150_ue_derelictcorridormegascans_linear_mpc_smoke.yaml`
- `Config/scenarios/planning/sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.yaml`
- `Docs/Design/05_路径规划与轨迹生成.md`
- `Docs/Design/11_RflySim式MoSim最小闭环架构审核.md`

### `PlanningNavigationDisplay`
- `Config/scenarios/planning/sunray150_planning_corridor_gate_linear_mpc_sysblock.yaml`
- `Config/scenarios/planning/sunray150_planning_open_blocks_linear_mpc_sysblock.yaml`
- `Config/scenarios/planning/sunray150_ue_derelictcorridormegascans_linear_mpc_smoke.yaml`
- `Config/scenarios/planning/sunray150_ue_factory_trace_table_linear_mpc_smoke.yaml`
- `Config/scenarios/planning/sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.yaml`
- `Docs/Design/05_路径规划与轨迹生成.md`
- `Docs/Workflows/agent_task_ledger.md`
- `Docs/Workflows/run_simulation.md`

### `TraceInlineReference`
- `Config/scenarios/planning/sunray150_ue_factory_trace_table_linear_mpc_smoke.yaml`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/FactoryLiteTraceSmoke.mo`
- `Models/QuadrotorExperiments/Sunray150UEFactoryTraceTableLinearMPCSysblockSmoke.mo`
- `Models/QuadrotorExperiments/TraceInlineReference.mo`
- `Models/QuadrotorExperiments/TraceLookupStandaloneSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-FACTORY-LITE-TRACE-20260606-005.json`

### `TraceLookupStandaloneSmoke`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/TraceLookupStandaloneSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-FACTORY-TRACE-RECONNECT-20260606-004.json`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-TRACELOOKUP-DIAG-20260606-003.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-TRACELOOKUP-DIAG-20260606-003.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`

### `TraceTableReference`
- `Models/QuadrotorExperiments/TraceTableReference.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-CONTROL-TRACE-CONSUME-20260606-002.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-ECHO-ADAPTER-CONTRACT-20260606-001.json`
- `Results/mworks_model_hygiene/20260606_002_graphical_audit_inventory/inventory.json`
- `Results/mworks_model_hygiene/20260606_002_graphical_audit_inventory/review_priority.md`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/reference_migration_risk_register.md`

### `Sunray150PlanningCorridorGateAWFFSysblockClosedLoop`
- `Config/scenarios/planning/sunray150_planning_corridor_gate_awff_sysblock.yaml`
- `Models/QuadrotorExperiments/Sunray150PlanningCorridorGateAWFFSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`

### `Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop`
- `Config/scenarios/planning/sunray150_planning_corridor_gate_linear_mpc_sysblock.yaml`
- `Docs/Design/05_路径规划与轨迹生成.md`
- `Models/QuadrotorExperiments/Sunray150PlanningCorridorGateLinearMPCSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_002_graphical_audit_inventory/review_priority.md`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/planning/corridor_gate_astar_awff/sunray150_planning_corridor_gate_linear_mpc_sysblock/replay/sunray150_planning_corridor_gate_linear_mpc_sysblock.json`

### `Sunray150PlanningOpenBlocksAWFFSysblockClosedLoop`
- `Config/scenarios/planning/sunray150_planning_open_blocks_awff_sysblock.yaml`
- `Docs/Design/05_路径规划与轨迹生成.md`
- `Models/QuadrotorExperiments/Sunray150PlanningOpenBlocksAWFFSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/planning/single_obstacle_astar_awff/sunray150_planning_open_blocks_awff_sysblock/replay/sunray150_planning_open_blocks_awff_sysblock.json`

### `Sunray150PlanningOpenBlocksColorMapReview`
- `Docs/Design/05_路径规划与轨迹生成.md`
- `Docs/Workflows/run_simulation.md`
- `Models/QuadrotorExperiments/Sunray150PlanningOpenBlocksColorMapReview.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/coagent_knowledge/knowledge_index.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`

### `Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop`
- `Config/scenarios/planning/sunray150_planning_open_blocks_linear_mpc_sysblock.yaml`
- `Docs/Cache/session_memory_migration/round2_parameter_identification_memory_20260604.md`
- `Docs/Design/05_路径规划与轨迹生成.md`
- `Docs/Workflows/run_simulation.md`
- `Docs/simulation_report.md`
- `Models/QuadrotorExperiments/Sunray150PlanningOpenBlocksColorMapReview.mo`
- `Models/QuadrotorExperiments/Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`

### `Sunray150UEFactoryLinearMPCSysblockSmoke`
- `Config/scenarios/planning/sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.yaml`
- `Docs/Cache/session_memory_migration/round2_parameter_identification_memory_20260604.md`
- `Docs/Workflows/agent_task_ledger.md`
- `Docs/Workflows/unreal_renderer.md`
- `Models/QuadrotorExperiments/Sunray150UEFactoryLinearMPCSysblockSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-TRACE-CONSUME-20260606-002.json`
- `Results/diagnostics/smoke/sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke/replay/sunray150_ue_factoryenvironmentcollect_linear_mpc_smoke.json`

### `Sunray150UEFactoryTraceTableLinearMPCSysblockSmoke`
- `Config/scenarios/planning/sunray150_ue_factory_trace_table_linear_mpc_smoke.yaml`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/Sunray150UEFactoryTraceTableLinearMPCSysblockSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-FACTORY-LITE-TRACE-20260606-005.json`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-FACTORY-TRACE-RECONNECT-20260606-004.json`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-INCREMENTAL-TRACE-ISOLATION-20260606-006.json`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-CONTROL-TRACELOOKUP-DIAG-20260606-003.json`

### `Sunray150UEDerelictLinearMPCSysblockSmoke`
- `Config/scenarios/planning/sunray150_ue_derelictcorridormegascans_linear_mpc_smoke.yaml`
- `Docs/Workflows/agent_task_ledger.md`
- `Docs/Workflows/unreal_renderer.md`
- `Models/QuadrotorExperiments/Sunray150UEDerelictLinearMPCSysblockSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/diagnostics/smoke/sunray150_ue_derelictcorridormegascans_linear_mpc_smoke/replay/sunray150_ue_derelictcorridormegascans_linear_mpc_smoke.json`
- `Results/mworks_model_hygiene/20260606_004_quadrotor_experiments_organization/flat_entry_inventory.json`
- `Results/unreal_scene_mapping/MWORKS_UE_SCENE_SMOKE_STATUS.md`

### `Sunray150RflyStyleRotorDynamics`
- `Docs/Workflows/agent_task_ledger.md`
- `Docs/Workflows/identify_quadrotor_parameters.md`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-010.json`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-012.json`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-DYNAMICS-WRAPPER-INTEGRATION-20260606-006.json`
- `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-010.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-DYNAMICS-MIN-UPGRADE-20260606-005.json`

### `Sunray150DynamicsUpgradeHoverSmoke`
- `Docs/Workflows/identify_quadrotor_parameters.md`
- `Docs/Workflows/rfly_mosim_p0_10h_execution_plan.md`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-DYNAMICS-WRAPPER-INTEGRATION-20260606-006.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-DYNAMICS-MIN-UPGRADE-20260606-005.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-QUADROTOR-EXPERIMENTS-CLASSIFICATION-20260606-013.json`
- `Results/coagent_gateway/packets/sunray150_dynamics_model_check_complete_20260605.json`
- `Results/coagent_gateway/packets/uav_arch_sync_and_chassis_recheck_20260606.json`

### `Sunray150DynamicsUpgradeYawStepSmoke`
- `Docs/Workflows/identify_quadrotor_parameters.md`
- `Docs/Workflows/rfly_mosim_p0_10h_execution_plan.md`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-DYNAMICS-WRAPPER-INTEGRATION-20260606-006.json`
- `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-010.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-DYNAMICS-MIN-UPGRADE-20260606-005.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-QUADROTOR-EXPERIMENTS-CLASSIFICATION-20260606-013.json`
- `Results/coagent_gateway/packets/sunray150_dynamics_model_check_complete_20260605.json`

### `Sunray150DynamicsWrapperSurface`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-010.json`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-012.json`
- `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-010.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-RESUME-20260606-014.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-DYNAMICS-WRAPPER-INTEGRATION-20260606-006.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-PHYSICAL-WRENCH-WRAPPER-20260606-007.json`

### `Sunray150DynamicsWrapperHoverSmoke`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-010.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-DYNAMICS-WRAPPER-INTEGRATION-20260606-006.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-WRAPPER-SOURCE-RECOVERY-20260606-011.json`
- `Results/mworks_dynamics_upgrade/20260606_006_wrapper_integration/EVIDENCE_SUMMARY.md`
- `Results/mworks_dynamics_upgrade/20260606_006_wrapper_integration/mcp_wrapper_smoke_summary.json`
- `Results/mworks_dynamics_upgrade/20260606_011_wrapper_source_recovery/EVIDENCE_SUMMARY.md`

### `Sunray150DynamicsWrapperYawStepSmoke`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-DYNAMICS-YAW-TRANSIENT-EVIDENCE-GATE-20260606-017.json`
- `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-010.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-DYNAMICS-WRAPPER-INTEGRATION-20260606-006.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-DYNAMICS-YAW-TRANSIENT-EVIDENCE-GATE-20260606-017.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-WRAPPER-SOURCE-RECOVERY-20260606-011.json`
- `Results/mworks_dynamics_upgrade/20260606_006_wrapper_integration/EVIDENCE_SUMMARY.md`

### `Sunray150PhysicalWrenchFrameAdapter`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/FactoryTraceIso28ActuatorToWrenchBridgeSmoke.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-010.json`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-012.json`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-WRENCH-TO-EXTERNAL-FRAME-BOUNDARY-20260606-015.json`
- `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-010.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-RESUME-20260606-014.json`

### `Sunray150PhysicalWrenchHoverSmoke`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-POST-GUI-SENTINEL-HEALTH-GATE-20260606-009.json`
- `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-010.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-RESUME-20260606-014.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-PHYSICAL-WRENCH-WRAPPER-20260606-007.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-POST-GUI-SENTINEL-HEALTH-GATE-20260606-009.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-WRAPPER-SOURCE-RECOVERY-20260606-011.json`

### `Sunray150PhysicalWrenchYawStepSmoke`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/RFLY-MOSIM-MWORKS-DYNAMICS-YAW-TRANSIENT-EVIDENCE-GATE-20260606-017.json`
- `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-ACTUATOR-TO-WRENCH-BRIDGE-20260606-010.json`
- `Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-YAW-SIGN-MOTOR-ORDER-AUDIT-20260606-008-GUI-CRASH-REPORT.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-DYNAMICS-YAW-TRANSIENT-EVIDENCE-GATE-20260606-017.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-PHYSICAL-WRENCH-WRAPPER-20260606-007.json`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-WRAPPER-SOURCE-RECOVERY-20260606-011.json`

### `FormationTriangleFigure8LinearMPCSysblockClosedLoop`
- `Config/scenarios/formation/formation_triangle_figure8_linear_mpc_sysblock.yaml`
- `Docs/Design/06_多机编队控制.md`
- `Docs/Index/project_work_memory_index.md`
- `Docs/Workflows/agent_task_ledger.md`
- `Models/QuadrotorExperiments/FormationTriangleFigure8LinearMPCSysblockClosedLoop.mo`
- `Models/QuadrotorExperiments/package.mo`
- `Results/agent_packets/returns/RFLY-MOSIM-MWORKS-R2-GRAPHICAL-MODEL-AUDIT-INVENTORY-20260606-002.json`
- `Results/formation/triangle_figure8/formation_triangle_figure8_linear_mpc_sysblock/replay/formation_triangle_figure8_linear_mpc_sysblock.json`

## Search Caveat

- Inaccessible or intentionally skipped path samples during static search: 1. These were not used as deletion evidence.
- Future write tasks should use a bounded reference search that excludes build/cache/symlink directories such as `.venv`, ROS2 `build/install/log`, and `Results/tmp` unless historical provenance is explicitly needed.

## Delete/Migration Gate

No flat entry may be deleted or real-definition-moved until a later write task proves all of the following: full reference search clean or intentionally migrated, category alias exists, flat compatibility alias remains or PMO approves breaking change, targeted Sysplorer load/check passes, and result packet records non-claims.
