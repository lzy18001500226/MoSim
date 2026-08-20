#!/usr/bin/env python3
"""
Correct intelligent restoration of 46 controller cores from archive
"""
import json
import re
from pathlib import Path
import shutil

# Load catalog
catalog_path = Path('Config/control_platform/control_scheme_catalog.json')
data = json.load(open(catalog_path, encoding='utf-8'))
cores = [s['scheme_id'] for s in data.get('schemes', [])
         if s.get('execution_kind') == 'graphical_control_core']

# Archive root
archive_root = Path('E:/刘致远18001500226/MoSim_Archive/20260818_codex_legacy_architecture/Control_Implementations_Graphical')

# Target root
target_root = Path('Models/MoSimQuadrotorModel/Control')

# Corrected MAPPING: scheme_id -> actual Core or Sysblock file
MAPPING = {
    # Graphical cores (9 existing CoreSysblock.mo files)
    'official_pid': 'Graphical/PID/OfficialPidCoreSysblock.mo',
    'fixed_awff_pid': 'Graphical/AWFF/AwffFullControllerCoreSysblock.mo',
    'fixed_awff_l1_residual': 'Graphical/AWFF/AwffL1ResidualControllerCoreSysblock.mo',
    'fixed_awff_l1_indi': 'Graphical/AWFF/AwffL1IndiControllerCoreSysblock.mo',
    'fixed_linear_mpc_l1_indi': 'Graphical/LinearMPC/LinearMpcL1IndiControllerCoreSysblock.mo',
    'fixed_qp_nmpc_l1_indi_cbf': 'Graphical/QPNMPC/QpNmpcL1IndiCbfControllerCoreSysblock.mo',

    # PID family - use MIL models (they contain Sysblock instantiations)
    'cascade_pid': 'PidFamily/MoSim_PID_CASCADE_PID_GRAPHICAL_MIL.mo',
    'gain_scheduled_pid': 'PidFamily/MoSim_PID_GAIN_SCHEDULED_PID_GRAPHICAL_MIL.mo',
    'fuzzy_pid': 'PidFamily/MoSim_PID_FUZZY_PID_GRAPHICAL_MIL.mo',
    'neural_pid': 'PidFamily/MoSim_PID_NEURAL_PID_GRAPHICAL_MIL.mo',
    'fopid': 'ClassicRobust/MoSim_Classic_FOPID_MIL.mo',

    # ClassicRobust - use Sysblock base classes
    'lqr_baseline': 'ClassicRobust/MoSim_Classic_CFunction_Sysblock.mo',
    'lqi_baseline': 'ClassicRobust/MoSim_Classic_CFunction_Sysblock.mo',
    'lqg': 'ClassicRobust/MoSim_Classic_CFunction_Sysblock.mo',
    'h2_state_feedback': 'ClassicRobust/MoSim_Classic_CFunction_Sysblock.mo',
    'hinf_hover_wrench': 'ClassicRobust/MoSim_Classic_CFunction_Sysblock.mo',
    'pole_placement_luenberger': 'ClassicRobust/MoSim_Classic_CFunction_Sysblock.mo',
    'backstepping_baseline': 'ClassicRobust/MoSim_Classic_CFunction_Sysblock.mo',
    'adaptive_backstepping': 'ClassicRobust/MoSim_Classic_CFunction_Sysblock.mo',
    'feedback_linearization': 'ClassicRobust/MoSim_Classic_CFunction_Sysblock.mo',
    'mrac': 'ClassicRobust/MoSim_Classic_CFunction_Sysblock.mo',
    'ndi': 'ClassicRobust/MoSim_Classic_CFunction_Sysblock.mo',
    'passivity_based_control': 'ClassicRobust/MoSim_Classic_CFunction_Sysblock.mo',

    # SlidingMode - use Sysblock base classes
    'integral_smc': 'SlidingMode/MoSim_G5_SMC_DIRECT_CFunction_Sysblock.mo',
    'terminal_smc': 'SlidingMode/MoSim_G5_SMC_DIRECT_CFunction_Sysblock.mo',
    'nonsingular_terminal_smc': 'SlidingMode/MoSim_G5_SMC_DIRECT_CFunction_Sysblock.mo',
    'super_twisting_smc': 'SlidingMode/MoSim_G5_SMC_DIRECT_CFunction_Sysblock.mo',
    'adaptive_smc': 'SlidingMode/MoSim_G5_SMC_DIRECT_CFunction_Sysblock.mo',
    'fuzzy_smc': 'SlidingMode/MoSim_G5_SMC_DIRECT_CFunction_Sysblock.mo',
    'smc_boundary_layer': 'SlidingMode/MoSim_G5_SMC_DIRECT_CFunction_Sysblock.mo',

    # Optimization - use Sysblock base classes
    'linear_mpc': 'Optimization/MoSim_G5_MPC_DIRECT_CFunction_Sysblock.mo',
    'robust_mpc': 'Optimization/MoSim_G5_MPC_DIRECT_CFunction_Sysblock.mo',
    'adaptive_mpc': 'Optimization/MoSim_G5_MPC_DIRECT_CFunction_Sysblock.mo',
    'tube_mpc': 'Optimization/MoSim_G5_MPC_DIRECT_CFunction_Sysblock.mo',
    'explicit_gain_scheduled_mpc': 'Optimization/MoSim_G5_MPC_DIRECT_CFunction_Sysblock.mo',
    'ilqr': 'Optimization/MoSim_G5_MPC_DIRECT_CFunction_Sysblock.mo',
    'mppi': 'Optimization/MoSim_G5_MPC_DIRECT_CFunction_Sysblock.mo',
    'nmpc_outer': 'Optimization/MoSim_G5_MPC_DIRECT_CFunction_Sysblock.mo',

    # GeometricFlatness - use Sysblock base classes
    'se3_basic': 'GeometricFlatness/MoSim_G5_SE3_DIRECT_CFunction_Sysblock.mo',
    'dfbc_basic': 'GeometricFlatness/MoSim_G5_DFBC_DIRECT_CFunction_Sysblock.mo',
    'dfbc_high_order_attitude': 'GeometricFlatness/MoSim_G5_DFBC_DIRECT_CFunction_Sysblock.mo',
    'dfbc_high_order_bodyrate': 'GeometricFlatness/MoSim_G5_DFBC_DIRECT_CFunction_Sysblock.mo',
    'dfbc_smooth_robust_attitude': 'GeometricFlatness/MoSim_G5_DFBC_DIRECT_CFunction_Sysblock.mo',
    'dfbc_smooth_robust_bodyrate': 'GeometricFlatness/MoSim_G5_DFBC_DIRECT_CFunction_Sysblock.mo',

    # Learning - use Sysblock base classes
    'trained_neural_residual': 'Learning/MoSim_G5_LEARNING_DIRECT_CFunction_Sysblock.mo',
    'rl_gain_scheduler': 'Learning/MoSim_G5_LEARNING_DIRECT_CFunction_Sysblock.mo',
}

def scheme_id_to_package_name(scheme_id):
    """Convert scheme_id to PascalCase"""
    parts = scheme_id.split('_')
    special = {
        'pid': 'Pid', 'lqr': 'Lqr', 'lqi': 'Lqi', 'lqg': 'Lqg',
        'h2': 'H2', 'hinf': 'Hinf', 'mrac': 'Mrac', 'ndi': 'Ndi',
        'smc': 'Smc', 'mpc': 'Mpc', 'ilqr': 'Ilqr', 'mppi': 'Mppi',
        'nmpc': 'Nmpc', 'qp': 'Qp', 'se3': 'Se3', 'dfbc': 'Dfbc',
        'rl': 'Rl', 'awff': 'Awff', 'l1': 'L1', 'indi': 'Indi',
        'cbf': 'Cbf', 'fopid': 'Fopid',
    }
    return ''.join([special.get(p, p.capitalize()) for p in parts])

def fix_within_path(content, old_within, new_within):
    """Replace within statement"""
    pattern = r'within\s+' + re.escape(old_within) + r'\s*;'
    replacement = f'within {new_within};'
    return re.sub(pattern, replacement, content, count=1)

if __name__ == '__main__':
    # First, check which files exist
    missing_files = []
    for scheme_id, rel_path in MAPPING.items():
        full_path = archive_root / rel_path
        if not full_path.exists():
            missing_files.append((scheme_id, rel_path))

    if missing_files:
        print(f'ERROR: {len(missing_files)} mapped files not found in archive:')
        for scheme_id, rel_path in missing_files:
            print(f'  - {scheme_id}: {rel_path}')
        print('\nCannot proceed. Please fix MAPPING.')
        exit(1)

    print(f'All {len(MAPPING)} source files verified in archive.')
    print('Starting restoration...\n')

    created_packages = []
    failed = []

    for scheme_id in cores:
        if scheme_id not in MAPPING:
            failed.append((scheme_id, 'Not in MAPPING'))
            continue

        pkg_name = scheme_id_to_package_name(scheme_id)
        archive_rel = MAPPING[scheme_id]
        archive_path = archive_root / archive_rel

        # Read source file
        content = archive_path.read_text(encoding='utf-8')

        # Fix within statement
        within_match = re.search(r'within\s+([\w\.]+)\s*;', content)
        if within_match:
            old_within = within_match.group(1)
            new_within = f'MoSimQuadrotorModel.Control.{pkg_name}'
            content = fix_within_path(content, old_within, new_within)

        # Determine target filename (always XXXCore.mo)
        pkg_dir = target_root / pkg_name
        pkg_dir.mkdir(exist_ok=True)

        target_file = pkg_dir / f'{pkg_name}Core.mo'
        target_file.write_text(content, encoding='utf-8')

        # Create package.mo
        pkg_file = pkg_dir / 'package.mo'
        pkg_file.write_text(
            f'within MoSimQuadrotorModel.Control;\n'
            f'package {pkg_name} "{scheme_id} controller implementation"\n'
            f'  annotation(__MWORKS(hide = false));\n'
            f'end {pkg_name};\n',
            encoding='utf-8'
        )

        # Create package.order
        order_file = pkg_dir / 'package.order'
        order_file.write_text(f'{pkg_name}Core\n', encoding='utf-8')

        created_packages.append(pkg_name)

    print(f'Successfully created {len(created_packages)} packages')
    if failed:
        print(f'Failed: {len(failed)}')
        for scheme_id, reason in failed:
            print(f'  - {scheme_id}: {reason}')
