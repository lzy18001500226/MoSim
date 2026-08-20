#!/usr/bin/env python3
"""
Validate the 4 fixed controllers after Core/Runner migration:
- awff_l1_indi
- awff_l1_residual
- linear_mpc_l1_indi
- qp_nmpc_l1_indi_cbf

Steps:
1. Verify new Core files exist
2. Verify new GraphicalRunner files exist
3. Run Sysplorer CheckModel on all 4 cores
4. Run 50s ClimbPath simulation on all 4 runners
"""
import json
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')

# Controller definitions (without "fixed_" prefix)
CONTROLLERS = [
    {
        'id': 'awff_l1_indi',
        'display_name': 'AWFF L1 INDI',
        'core_file': 'Models/MoSimQuadrotorModel/Control/IntegratedChains/AwffL1Indi/AwffL1IndiCore.mo',
        'core_class': 'MoSimQuadrotorModel.Control.IntegratedChains.AwffL1Indi.AwffL1IndiCore',
        'runner_file': 'Models/MoSimQuadrotorModel/Experiment/IntegratedChains/AwffL1IndiGraphicalRunner.mo',
        'runner_class': 'MoSimQuadrotorModel.Experiment.IntegratedChains.AwffL1IndiGraphicalRunner',
    },
    {
        'id': 'awff_l1_residual',
        'display_name': 'AWFF L1 Residual',
        'core_file': 'Models/MoSimQuadrotorModel/Control/IntegratedChains/AwffL1Residual/AwffL1ResidualCore.mo',
        'core_class': 'MoSimQuadrotorModel.Control.IntegratedChains.AwffL1Residual.AwffL1ResidualCore',
        'runner_file': 'Models/MoSimQuadrotorModel/Experiment/IntegratedChains/AwffL1ResidualGraphicalRunner.mo',
        'runner_class': 'MoSimQuadrotorModel.Experiment.IntegratedChains.AwffL1ResidualGraphicalRunner',
    },
    {
        'id': 'linear_mpc_l1_indi',
        'display_name': 'Linear MPC L1 INDI',
        'core_file': 'Models/MoSimQuadrotorModel/Control/IntegratedChains/LinearMpcL1Indi/LinearMpcL1IndiCore.mo',
        'core_class': 'MoSimQuadrotorModel.Control.IntegratedChains.LinearMpcL1Indi.LinearMpcL1IndiCore',
        'runner_file': 'Models/MoSimQuadrotorModel/Experiment/IntegratedChains/LinearMpcL1IndiGraphicalRunner.mo',
        'runner_class': 'MoSimQuadrotorModel.Experiment.IntegratedChains.LinearMpcL1IndiGraphicalRunner',
    },
    {
        'id': 'qp_nmpc_l1_indi_cbf',
        'display_name': 'QP NMPC L1 INDI CBF',
        'core_file': 'Models/MoSimQuadrotorModel/Control/IntegratedChains/QpNmpcL1IndiCbf/QpNmpcL1IndiCbfCore.mo',
        'core_class': 'MoSimQuadrotorModel.Control.IntegratedChains.QpNmpcL1IndiCbf.QpNmpcL1IndiCbfCore',
        'runner_file': 'Models/MoSimQuadrotorModel/Experiment/IntegratedChains/QpNmpcL1IndiCbfGraphicalRunner.mo',
        'runner_class': 'MoSimQuadrotorModel.Experiment.IntegratedChains.QpNmpcL1IndiCbfGraphicalRunner',
    },
]

print("="*80)
print("VALIDATION: 4 Fixed Controllers (Core + Runner Migration)")
print("="*80)
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# Step 1: Verify files exist
# ============================================================================
print("Step 1: Verifying file existence...")
print("-"*80)

all_files_exist = True
for ctrl in CONTROLLERS:
    core_path = BASE_DIR / ctrl['core_file']
    runner_path = BASE_DIR / ctrl['runner_file']

    core_exists = core_path.exists()
    runner_exists = runner_path.exists()

    status = "OK" if (core_exists and runner_exists) else "FAIL"
    print(f"{status:4s} {ctrl['id']:30s} Core: {str(core_exists):5s} Runner: {str(runner_exists):5s}")

    if not core_exists:
        print(f"  ERROR: Core file missing: {ctrl['core_file']}")
        all_files_exist = False
    if not runner_exists:
        print(f"  ERROR: Runner file missing: {ctrl['runner_file']}")
        all_files_exist = False

if not all_files_exist:
    print("\nFAIL: File verification failed. Aborting.")
    sys.exit(1)

print("\nOK: All files verified\n")

# ============================================================================
# Step 2: Sysplorer CheckModel (would need MCP connection)
# ============================================================================
print("="*80)
print("Step 2: Sysplorer CheckModel Validation")
print("="*80)
print("NOTE: This requires Sysplorer MCP connection")
print("Manual command for each controller:\n")

for ctrl in CONTROLLERS:
    print(f"# {ctrl['display_name']}")
    print(f"sysplorer.check_model(")
    print(f"    model_name='{ctrl['core_class']}',")
    print(f"    model_type='Modelica'")
    print(f")\n")

# ============================================================================
# Step 3: Generate validation report
# ============================================================================
print("="*80)
print("Step 3: Generating Validation Report")
print("="*80)

report = {
    'generated_at': datetime.now().isoformat(),
    'task': 'validate_4_fixed_controllers',
    'controllers': [],
    'summary': {
        'total': len(CONTROLLERS),
        'files_verified': len(CONTROLLERS) if all_files_exist else 0,
        'checkmodel_status': 'requires_sysplorer_mcp',
        'simulation_status': 'requires_sysplorer_mcp',
    }
}

for ctrl in CONTROLLERS:
    report['controllers'].append({
        'controller_id': ctrl['id'],
        'display_name': ctrl['display_name'],
        'core_class': ctrl['core_class'],
        'runner_class': ctrl['runner_class'],
        'files_verified': True,
        'checkmodel_result': 'pending',
        'simulation_result': 'pending',
    })

output_dir = BASE_DIR / 'Results/control_platform/validate_4_fixed_controllers'
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / 'validation_report.json'

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\nOK: Validation report saved: {output_file}")
print("\nNext steps:")
print("1. Connect Sysplorer MCP server")
print("2. Run CheckModel on all 4 Core files")
print("3. Run 50s ClimbPath simulation on all 4 GraphicalRunner files")
print("4. Update phase4_phase5_complete_report.json with results")
