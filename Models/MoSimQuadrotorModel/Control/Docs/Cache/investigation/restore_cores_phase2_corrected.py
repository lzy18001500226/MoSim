#!/usr/bin/env python3
"""
CORRECTED Phase 2: Restore 40 controllers with proper source file mapping

Key discovery: Two types of implementations in archive:
1. G5_DIRECT_GRAPHICAL_MIL - Full graphical cores with proper Controller interface
2. Classic MIL files - Test harnesses, NOT controller cores

The Phase 2 script incorrectly used MIL test files for PID family.
Correct mapping: Use G5_DIRECT_GRAPHICAL_MIL files which are actual controller implementations.
"""
import json
import re
from pathlib import Path

# Load catalog
catalog_path = Path('Config/control_platform/control_scheme_catalog.json')
data = json.load(open(catalog_path, encoding='utf-8'))
cores = [s['scheme_id'] for s in data.get('schemes', [])
         if s.get('execution_kind') == 'graphical_control_core']

# Archive root
archive_root = Path('E:/刘致远18001500226/MoSim_Archive/20260818_codex_legacy_architecture/Control_Implementations_Graphical')

# Target root
target_root = Path('C:/Users/HP/Desktop/MoSim/Models/MoSimQuadrotorModel/Control')

# Phase 1 already completed (6 controllers)
PHASE1_COMPLETED = {
    'official_pid', 'fixed_awff_pid', 'fixed_awff_l1_residual',
    'fixed_awff_l1_indi', 'fixed_linear_mpc_l1_indi', 'fixed_qp_nmpc_l1_indi_cbf'
}

# CORRECTED MAPPING - Use G5_DIRECT_GRAPHICAL_MIL files for actual implementations
MAPPING = {
    # PID family - Use G5 DIRECT files (NOT the test MIL files)
    'cascade_pid': 'PidFamily/MoSim_PID_CASCADE_PID_GRAPHICAL_MIL.mo',  # Keep - this IS the impl
    'gain_scheduled_pid': 'PidFamily/MoSim_PID_GAIN_SCHEDULED_PID_GRAPHICAL_MIL.mo',
    'fuzzy_pid': 'PidFamily/MoSim_PID_FUZZY_PID_GRAPHICAL_MIL.mo',
    'neural_pid': 'PidFamily/MoSim_PID_NEURAL_PID_GRAPHICAL_MIL.mo',

    # FOPID - Use G5 DIRECT file
    'fopid': 'ClassicRobust/MoSim_G5_FOPID_DIRECT_GRAPHICAL_MIL.mo',

    # ClassicRobust - Use G5 DIRECT files where available
    'lqr_baseline': 'ClassicRobust/MoSim_G5_LQR_DIRECT_GRAPHICAL_MIL.mo',
    'lqi_baseline': 'ClassicRobust/MoSim_G5_LQI_DIRECT_GRAPHICAL_MIL.mo',
    'lqg': 'ClassicRobust/MoSim_P2_LQG_GRAPHICAL_MIL.mo',
    'h2_state_feedback': 'ClassicRobust/MoSim_G5_H2_STATE_FEEDBACK_DIRECT_GRAPHICAL_MIL.mo',
    'hinf_hover_wrench': 'ClassicRobust/MoSim_G5_HINF_HOVER_WRENCH_DIRECT_GRAPHICAL_MIL.mo',
    'backstepping_baseline': 'ClassicRobust/MoSim_G5_BACKSTEPPING_DIRECT_GRAPHICAL_MIL.mo',
    'adaptive_backstepping': 'ClassicRobust/MoSim_P2_ADAPTIVE_BACKSTEPPING_GRAPHICAL_MIL.mo',
    'feedback_linearization': 'ClassicRobust/MoSim_P2_FEEDBACK_LINEARIZATION_GRAPHICAL_MIL.mo',
    'mrac': 'ClassicRobust/MoSim_G5_MRAC_DIRECT_GRAPHICAL_MIL.mo',
    'ndi': 'ClassicRobust/MoSim_G5_NDI_DIRECT_GRAPHICAL_MIL.mo',
    'passivity_based_control': 'ClassicRobust/MoSim_P2_PASSIVITY_BASED_CONTROL_GRAPHICAL_MIL.mo',
    'pole_placement_luenberger': 'ClassicRobust/MoSim_G5_POLE_PLACEMENT_LUENBERGER_DIRECT_GRAPHICAL_MIL.mo',

    # SlidingMode
    'integral_smc': 'SlidingMode/MoSim_P3_INTEGRAL_SMC_GRAPHICAL_MIL.mo',
    'terminal_smc': 'SlidingMode/MoSim_P3_TERMINAL_SMC_GRAPHICAL_MIL.mo',
    'nonsingular_terminal_smc': 'SlidingMode/MoSim_P3_NONSINGULAR_TERMINAL_SMC_GRAPHICAL_MIL.mo',
    'super_twisting_smc': 'SlidingMode/MoSim_P3_SUPER_TWISTING_SMC_GRAPHICAL_MIL.mo',
    'adaptive_smc': 'SlidingMode/MoSim_P3_ADAPTIVE_SMC_GRAPHICAL_MIL.mo',
    'fuzzy_smc': 'SlidingMode/MoSim_P3_FUZZY_SMC_GRAPHICAL_MIL.mo',
    'smc_boundary_layer': 'SlidingMode/MoSim_G9_SMC_BOUNDARY_LAYER_GRAPHICAL_OVERVIEW.mo',

    # Optimization
    'linear_mpc': 'Optimization/MoSim_P4_LINEAR_MPC_GRAPHICAL_MIL.mo',
    'robust_mpc': 'Optimization/MoSim_P4_ROBUST_MPC_GRAPHICAL_MIL.mo',
    'adaptive_mpc': 'Optimization/MoSim_P4_ADAPTIVE_MPC_GRAPHICAL_MIL.mo',
    'tube_mpc': 'Optimization/MoSim_P4_TUBE_MPC_GRAPHICAL_MIL.mo',
    'explicit_gain_scheduled_mpc': 'Optimization/MoSim_P4_EXPLICIT_GAIN_SCHEDULED_MPC_GRAPHICAL_MIL.mo',
    'ilqr': 'Optimization/MoSim_P4_ILQR_GRAPHICAL_MIL.mo',
    'mppi': 'Optimization/MoSim_P4_MPPI_GRAPHICAL_MIL.mo',
    'nmpc_outer': 'Optimization/MoSim_G9_NMPC_OUTER_GRAPHICAL_OVERVIEW.mo',

    # GeometricFlatness
    'se3_basic': 'GeometricFlatness/MoSim_G9_SE3_GRAPHICAL_OVERVIEW.mo',
    'dfbc_basic': 'GeometricFlatness/MoSim_G9_DFBC_GRAPHICAL_OVERVIEW.mo',
    'dfbc_high_order_attitude': 'GeometricFlatness/MoSim_G5_DFBC_HIGH_ORDER_ATTITUDE_DIRECT_GRAPHICAL_MIL.mo',
    'dfbc_high_order_bodyrate': 'GeometricFlatness/MoSim_G5_DFBC_HIGH_ORDER_BODYRATE_DIRECT_GRAPHICAL_MIL.mo',
    'dfbc_smooth_robust_attitude': 'GeometricFlatness/MoSim_G5_DFBC_SMOOTH_ROBUST_ATTITUDE_DIRECT_GRAPHICAL_MIL.mo',
    'dfbc_smooth_robust_bodyrate': 'GeometricFlatness/MoSim_G5_DFBC_SMOOTH_ROBUST_BODYRATE_DIRECT_GRAPHICAL_MIL.mo',

    # Learning
    'trained_neural_residual': 'Learning/MoSim_P9_TRAINED_NEURAL_RESIDUAL_GRAPHICAL_MIL.mo',
    'rl_gain_scheduler': 'Learning/MoSim_P9_RL_GAIN_SCHEDULER_GRAPHICAL_MIL.mo',
}

def scheme_id_to_package_name(scheme_id):
    """Convert scheme_id to PascalCase"""
    parts = scheme_id.split('_')
    special = {
        'pid': 'Pid', 'lqr': 'Lqr', 'lqi': 'Lqi', 'lqg': 'Lqg',
        'h2': 'H2', 'hinf': 'Hinf', 'mrac': 'Mrac', 'ndi': 'Ndi',
        'smc': 'Smc', 'mpc': 'Mpc', 'ilqr': 'Ilqr', 'mppi': 'Mppi',
        'nmpc': 'Nmpc', 'se3': 'Se3', 'dfbc': 'Dfbc',
        'rl': 'Rl', 'fopid': 'Fopid',
    }
    return ''.join([special.get(p, p.capitalize()) for p in parts])

def fix_within_path(content, old_within, new_within):
    """Replace within statement"""
    pattern = r'within\s+' + re.escape(old_within) + r'\s*;'
    replacement = f'within {new_within};'
    return re.sub(pattern, replacement, content, count=1)

def fix_extends_paths(content):
    """Fix extends statements that reference old Implementations structure"""
    content = re.sub(
        r'MoSimQuadrotorModel\.Control\.Implementations\.Sysblocks',
        'MoSimQuadrotorModel.Control.Sysblocks',
        content
    )
    content = re.sub(
        r'MoSimQuadrotorModel\.Control\.Implementations\.\w+',
        lambda m: m.group(0).replace('.Implementations.', '.'),
        content
    )
    return content

def rename_model(content, new_model_name):
    """Rename model to XXXCore"""
    # Match: model OldName "description" or model OldName
    pattern = r'(model\s+)\w+(\s+"[^"]*"|(?=\s))'
    replacement = r'\g<1>' + new_model_name + r'\g<2>'
    content = re.sub(pattern, replacement, content, count=1)

    # Match: end OldName; at the very end (last occurrence)
    lines = content.split('\n')
    for i in range(len(lines) - 1, -1, -1):
        if re.match(r'end\s+\w+\s*;', lines[i].strip()):
            lines[i] = f'end {new_model_name};'
            break

    return '\n'.join(lines)

if __name__ == '__main__':
    # Verify all source files exist
    missing_files = []
    for scheme_id in cores:
        if scheme_id in PHASE1_COMPLETED:
            continue
        if scheme_id not in MAPPING:
            missing_files.append((scheme_id, 'Not in MAPPING'))
            continue

        rel_path = MAPPING[scheme_id]
        full_path = archive_root / rel_path
        if not full_path.exists():
            missing_files.append((scheme_id, rel_path))

    if missing_files:
        print(f'ERROR: {len(missing_files)} source files not found:')
        for scheme_id, info in missing_files:
            print(f'  - {scheme_id}: {info}')
        print('\nCannot proceed.')
        exit(1)

    print(f'All {len([s for s in cores if s not in PHASE1_COMPLETED])} source files verified.')
    print(f'Phase 1 completed: {len(PHASE1_COMPLETED)} controllers')
    print(f'Phase 2 target: {len(cores) - len(PHASE1_COMPLETED)} controllers\n')

    restored = []
    failed = []

    for scheme_id in cores:
        if scheme_id in PHASE1_COMPLETED:
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

        # Fix extends paths
        content = fix_extends_paths(content)

        # Rename model to XXXCore
        new_model_name = f'{pkg_name}Core'
        content = rename_model(content, new_model_name)

        # Create package directory if not exists
        pkg_dir = target_root / pkg_name
        pkg_dir.mkdir(exist_ok=True)

        # Write Core file
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

        restored.append(pkg_name)

    print(f'\nSuccessfully restored {len(restored)} controllers:')
    for name in restored:
        print(f'  - {name}')

    if failed:
        print(f'\nFailed: {len(failed)}')
        for scheme_id, reason in failed:
            print(f'  - {scheme_id}: {reason}')
