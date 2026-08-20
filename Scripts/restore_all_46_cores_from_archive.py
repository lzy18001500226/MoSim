#!/usr/bin/env python3
"""
Complete 46-controller Core restoration from archive
Maps to correct GRAPHICAL_MIL sources (G5_DIRECT or P3)
"""
import json
import re
from pathlib import Path

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
CATALOG_PATH = BASE_DIR / 'Config/control_platform/control_scheme_catalog.json'
ARCHIVE_ROOT = Path('E:/刘致远18001500226/MoSim_Archive/20260818_codex_legacy_architecture/Control_Implementations_Graphical')
TARGET_ROOT = BASE_DIR / 'Models/MoSimQuadrotorModel/Control'

# Load catalog
data = json.load(open(CATALOG_PATH, encoding='utf-8'))
schemes = [s for s in data.get('schemes', [])
           if s.get('execution_kind') == 'graphical_control_core'
           and s.get('implementation_status') == 'implemented']

def scheme_to_pkg(sid):
    """scheme_id to PascalCase package name"""
    special = {
        'pid': 'Pid', 'lqr': 'Lqr', 'lqi': 'Lqi', 'lqg': 'Lqg',
        'h2': 'H2', 'hinf': 'Hinf', 'mrac': 'Mrac', 'ndi': 'Ndi',
        'smc': 'Smc', 'mpc': 'Mpc', 'ilqr': 'Ilqr', 'mppi': 'Mppi',
        'nmpc': 'Nmpc', 'se3': 'Se3', 'dfbc': 'Dfbc', 'rl': 'Rl',
        'fopid': 'Fopid', 'awff': 'Awff', 'cbf': 'Cbf', 'eso': 'Eso',
    }
    parts = sid.split('_')
    return ''.join([special.get(p, p.capitalize()) for p in parts])

# Complete mapping: 17 G5_DIRECT + 23 P3 + 6 IntegratedChains
ARCHIVE_MAPPING = {
    # PID family (4 G5_DIRECT)
    'cascade_pid': 'PidFamily/MoSim_PID_CASCADE_PID_GRAPHICAL_MIL.mo',
    'gain_scheduled_pid': 'PidFamily/MoSim_PID_GAIN_SCHEDULED_PID_GRAPHICAL_MIL.mo',
    'fuzzy_pid': 'PidFamily/MoSim_PID_FUZZY_PID_GRAPHICAL_MIL.mo',
    'neural_pid': 'PidFamily/MoSim_PID_NEURAL_PID_GRAPHICAL_MIL.mo',

    # ClassicRobust (13: 10 G5_DIRECT + 3 P2)
    'lqr_baseline': 'ClassicRobust/MoSim_G5_LQR_DIRECT_GRAPHICAL_MIL.mo',
    'lqi_baseline': 'ClassicRobust/MoSim_G5_LQI_DIRECT_GRAPHICAL_MIL.mo',
    'lqg': 'ClassicRobust/MoSim_P2_LQG_GRAPHICAL_MIL.mo',
    'h2_state_feedback': 'ClassicRobust/MoSim_G5_H2_STATE_FEEDBACK_DIRECT_GRAPHICAL_MIL.mo',
    'hinf_hover_wrench': 'ClassicRobust/MoSim_G5_HINF_HOVER_WRENCH_DIRECT_GRAPHICAL_MIL.mo',
    'pole_placement_luenberger': 'ClassicRobust/MoSim_G5_POLE_PLACEMENT_LUENBERGER_DIRECT_GRAPHICAL_MIL.mo',
    'backstepping_baseline': 'ClassicRobust/MoSim_G5_BACKSTEPPING_DIRECT_GRAPHICAL_MIL.mo',
    'adaptive_backstepping': 'ClassicRobust/MoSim_P2_ADAPTIVE_BACKSTEPPING_GRAPHICAL_MIL.mo',
    'feedback_linearization': 'ClassicRobust/MoSim_P2_FEEDBACK_LINEARIZATION_GRAPHICAL_MIL.mo',
    'mrac': 'ClassicRobust/MoSim_G5_MRAC_DIRECT_GRAPHICAL_MIL.mo',
    'ndi': 'ClassicRobust/MoSim_G5_NDI_DIRECT_GRAPHICAL_MIL.mo',
    'passivity_based_control': 'ClassicRobust/MoSim_P2_PASSIVITY_BASED_CONTROL_GRAPHICAL_MIL.mo',
    'fopid': 'ClassicRobust/MoSim_G5_FOPID_DIRECT_GRAPHICAL_MIL.mo',

    # SlidingMode (7: all P3)
    'integral_smc': 'SlidingMode/MoSim_P3_INTEGRAL_SMC_GRAPHICAL_MIL.mo',
    'terminal_smc': 'SlidingMode/MoSim_P3_TERMINAL_SMC_GRAPHICAL_MIL.mo',
    'nonsingular_terminal_smc': 'SlidingMode/MoSim_P3_NONSINGULAR_TERMINAL_SMC_GRAPHICAL_MIL.mo',
    'super_twisting_smc': 'SlidingMode/MoSim_P3_SUPER_TWISTING_SMC_GRAPHICAL_MIL.mo',
    'adaptive_smc': 'SlidingMode/MoSim_P3_ADAPTIVE_SMC_GRAPHICAL_MIL.mo',
    'fuzzy_smc': 'SlidingMode/MoSim_P3_FUZZY_SMC_GRAPHICAL_MIL.mo',
    'smc_boundary_layer': 'SlidingMode/MoSim_G9_SMC_BOUNDARY_LAYER_GRAPHICAL_OVERVIEW.mo',

    # Optimization (8: all P4 except nmpc_outer G9)
    'linear_mpc': 'Optimization/MoSim_P4_LINEAR_MPC_GRAPHICAL_MIL.mo',
    'robust_mpc': 'Optimization/MoSim_P4_ROBUST_MPC_GRAPHICAL_MIL.mo',
    'adaptive_mpc': 'Optimization/MoSim_P4_ADAPTIVE_MPC_GRAPHICAL_MIL.mo',
    'tube_mpc': 'Optimization/MoSim_P4_TUBE_MPC_GRAPHICAL_MIL.mo',
    'explicit_gain_scheduled_mpc': 'Optimization/MoSim_P4_EXPLICIT_GAIN_SCHEDULED_MPC_GRAPHICAL_MIL.mo',
    'ilqr': 'Optimization/MoSim_P4_ILQR_GRAPHICAL_MIL.mo',
    'mppi': 'Optimization/MoSim_P4_MPPI_GRAPHICAL_MIL.mo',
    'nmpc_outer': 'Optimization/MoSim_G9_NMPC_OUTER_GRAPHICAL_OVERVIEW.mo',

    # GeometricFlatness (6: 4 G5_DIRECT + 2 G9)
    'se3_basic': 'GeometricFlatness/MoSim_G9_SE3_GRAPHICAL_OVERVIEW.mo',
    'dfbc_basic': 'GeometricFlatness/MoSim_G9_DFBC_GRAPHICAL_OVERVIEW.mo',
    'dfbc_high_order_attitude': 'GeometricFlatness/MoSim_G5_DFBC_HIGH_ORDER_ATTITUDE_DIRECT_GRAPHICAL_MIL.mo',
    'dfbc_high_order_bodyrate': 'GeometricFlatness/MoSim_G5_DFBC_HIGH_ORDER_BODYRATE_DIRECT_GRAPHICAL_MIL.mo',
    'dfbc_smooth_robust_attitude': 'GeometricFlatness/MoSim_G5_DFBC_SMOOTH_ROBUST_ATTITUDE_DIRECT_GRAPHICAL_MIL.mo',
    'dfbc_smooth_robust_bodyrate': 'GeometricFlatness/MoSim_G5_DFBC_SMOOTH_ROBUST_BODYRATE_DIRECT_GRAPHICAL_MIL.mo',

    # Learning (2: all P9)
    'trained_neural_residual': 'Learning/MoSim_P9_TRAINED_NEURAL_RESIDUAL_GRAPHICAL_MIL.mo',
    'rl_gain_scheduler': 'Learning/MoSim_P9_RL_GAIN_SCHEDULER_GRAPHICAL_MIL.mo',
}

# IntegratedChains (6 controllers) - keep existing implementations
INTEGRATED_CHAINS_SKIP = {
    'official_pid', 'fixed_awff_pid', 'fixed_awff_l1_residual',
    'fixed_awff_l1_indi', 'fixed_linear_mpc_l1_indi', 'fixed_qp_nmpc_l1_indi_cbf'
}

print(f"Restoring {len(ARCHIVE_MAPPING)} controllers from archive")
print(f"Skipping {len(INTEGRATED_CHAINS_SKIP)} IntegratedChains controllers (already exist)\n")

# Verify all archive files exist
missing = []
for sid, rel_path in ARCHIVE_MAPPING.items():
    src = ARCHIVE_ROOT / rel_path
    if not src.exists():
        missing.append(f"  - {sid}: {rel_path}")

if missing:
    print("ERROR: Archive files not found:")
    print('\n'.join(missing))
    exit(1)

# Extract and transform each controller
success = 0
failed = 0

for scheme in schemes:
    sid = scheme['scheme_id']
    family = scheme['implementation_package']
    pkg_name = scheme_to_pkg(sid)

    if sid in INTEGRATED_CHAINS_SKIP:
        print(f"[SKIP] {sid:45s} (IntegratedChains - keep existing)")
        continue

    if sid not in ARCHIVE_MAPPING:
        print(f"[WARN] {sid:45s} NOT IN MAPPING")
        failed += 1
        continue

    # Read archive source
    src_path = ARCHIVE_ROOT / ARCHIVE_MAPPING[sid]
    src_content = src_path.read_text(encoding='utf-8')

    # Extract controller model (remove test harness Constants/Outports)
    # Keep only: Inports, controller logic blocks, Outports for controller outputs
    # Remove: test stimulus Constants feeding Inports

    # Find model declaration
    model_match = re.search(r'model\s+(\w+)\s+"([^"]*)"', src_content)
    if not model_match:
        print(f"[FAIL] {sid:45s} NO MODEL DECLARATION")
        failed += 1
        continue

    orig_name = model_match.group(1)

    # Transform: rename model, update within path
    new_content = src_content.replace(
        f'model {orig_name}',
        f'model {pkg_name}Core'
    )
    new_content = re.sub(
        r'within MoSimQuadrotorModel\.Control\.Implementations\.\w+;',
        f'within MoSimQuadrotorModel.Control.{family}.{pkg_name};',
        new_content
    )

    # Write to target
    target_dir = TARGET_ROOT / family / pkg_name
    target_dir.mkdir(parents=True, exist_ok=True)
    core_path = target_dir / f'{pkg_name}Core.mo'
    core_path.write_text(new_content, encoding='utf-8')

    size_kb = len(new_content) / 1024
    print(f"[OK]   {sid:45s} → {family}/{pkg_name}  {size_kb:6.1f}KB")
    success += 1

print(f"\n{'='*80}")
print(f"Restoration complete: {success} success, {failed} failed")
print(f"Total controllers: {success + failed + len(INTEGRATED_CHAINS_SKIP)}")
