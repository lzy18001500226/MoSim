#!/usr/bin/env python3
"""
Intelligent restoration of 46 controller cores from archive to new flat structure
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

# Mapping from core_archive_mapping.py
MAPPING = {
    'cascade_pid': 'PidFamily/MoSim_PID_CASCADE_PID_GRAPHICAL_MIL.mo',
    'gain_scheduled_pid': 'PidFamily/MoSim_PID_GAIN_SCHEDULED_PID_GRAPHICAL_MIL.mo',
    'fuzzy_pid': 'PidFamily/MoSim_PID_FUZZY_PID_GRAPHICAL_MIL.mo',
    'neural_pid': 'PidFamily/MoSim_PID_NEURAL_PID_GRAPHICAL_MIL.mo',
    'official_pid': 'Graphical/PID/OfficialPidCoreSysblock.mo',
    'fopid': 'ClassicRobust/MoSim_Classic_FOPID_MIL.mo',
    'fixed_awff_pid': 'Graphical/AWFF/AwffFullControllerCoreSysblock.mo',
    'fixed_awff_l1_residual': 'Graphical/AWFF/AwffL1ResidualControllerCoreSysblock.mo',
    'fixed_awff_l1_indi': 'Graphical/AWFF/AwffL1IndiControllerCoreSysblock.mo',
    'lqr_baseline': 'ClassicRobust/MoSim_WaveA_LQR_MIL.mo',
    'lqi_baseline': 'ClassicRobust/MoSim_WaveA_LQI_MIL.mo',
    'lqg': 'ClassicRobust/MoSim_P2_LQG_GRAPHICAL_MIL.mo',
    'h2_state_feedback': 'ClassicRobust/MoSim_Classic_H2_STATE_FEEDBACK_MIL.mo',
    'hinf_hover_wrench': 'ClassicRobust/MoSim_P10_HINF_HOVER_WRENCH_MIL.mo',
    'pole_placement_luenberger': 'ClassicRobust/MoSim_Classic_POLE_PLACEMENT_LUENBERGER_MIL.mo',
    'backstepping_baseline': 'ClassicRobust/MoSim_WaveA_BACKSTEPPING_MIL.mo',
    'adaptive_backstepping': 'ClassicRobust/MoSim_P2_ADAPTIVE_BACKSTEPPING_GRAPHICAL_MIL.mo',
    'feedback_linearization': 'ClassicRobust/MoSim_P2_FEEDBACK_LINEARIZATION_GRAPHICAL_MIL.mo',
    'mrac': 'ClassicRobust/MoSim_Classic_MRAC_MIL.mo',
    'ndi': 'ClassicRobust/MoSim_Classic_NDI_MIL.mo',
    'passivity_based_control': 'ClassicRobust/MoSim_P2_PASSIVITY_BASED_CONTROL_GRAPHICAL_MIL.mo',
    'integral_smc': 'SlidingMode/MoSim_P3_INTEGRAL_SMC_GRAPHICAL_MIL.mo',
    'terminal_smc': 'SlidingMode/MoSim_P3_TERMINAL_SMC_GRAPHICAL_MIL.mo',
    'nonsingular_terminal_smc': 'SlidingMode/MoSim_P3_NONSINGULAR_TERMINAL_SMC_GRAPHICAL_MIL.mo',
    'super_twisting_smc': 'SlidingMode/MoSim_P3_SUPER_TWISTING_SMC_GRAPHICAL_MIL.mo',
    'adaptive_smc': 'SlidingMode/MoSim_P3_ADAPTIVE_SMC_GRAPHICAL_MIL.mo',
    'fuzzy_smc': 'SlidingMode/MoSim_P3_FUZZY_SMC_GRAPHICAL_MIL.mo',
    'smc_boundary_layer': 'SlidingMode/MoSim_G9_SMC_BOUNDARY_LAYER_GRAPHICAL_OVERVIEW.mo',
    'linear_mpc': 'Optimization/MoSim_P4_LINEAR_MPC_GRAPHICAL_MIL.mo',
    'robust_mpc': 'Optimization/MoSim_P4_ROBUST_MPC_GRAPHICAL_MIL.mo',
    'adaptive_mpc': 'Optimization/MoSim_P4_ADAPTIVE_MPC_GRAPHICAL_MIL.mo',
    'tube_mpc': 'Optimization/MoSim_P4_TUBE_MPC_GRAPHICAL_MIL.mo',
    'explicit_gain_scheduled_mpc': 'Optimization/MoSim_P4_EXPLICIT_GAIN_SCHEDULED_MPC_GRAPHICAL_MIL.mo',
    'ilqr': 'Optimization/MoSim_P4_ILQR_GRAPHICAL_MIL.mo',
    'mppi': 'Optimization/MoSim_P4_MPPI_GRAPHICAL_MIL.mo',
    'nmpc_outer': 'Optimization/MoSim_G9_NMPC_OUTER_GRAPHICAL_OVERVIEW.mo',
    'fixed_linear_mpc_l1_indi': 'Graphical/LinearMPC/LinearMpcL1IndiControllerCoreSysblock.mo',
    'fixed_qp_nmpc_l1_indi_cbf': 'Graphical/QPNMPC/QpNmpcL1IndiCbfControllerCoreSysblock.mo',
    'se3_basic': 'GeometricFlatness/MoSim_G9_SE3_GRAPHICAL_OVERVIEW.mo',
    'dfbc_basic': 'GeometricFlatness/MoSim_G9_DFBC_GRAPHICAL_OVERVIEW.mo',
    'dfbc_high_order_attitude': 'GeometricFlatness/MoSim_P10_DFBC_HIGH_ORDER_ATTITUDE_MIL.mo',
    'dfbc_high_order_bodyrate': 'GeometricFlatness/MoSim_P10_DFBC_HIGH_ORDER_BODYRATE_MIL.mo',
    'dfbc_smooth_robust_attitude': 'GeometricFlatness/MoSim_P10_DFBC_SMOOTH_ROBUST_ATTITUDE_MIL.mo',
    'dfbc_smooth_robust_bodyrate': 'GeometricFlatness/MoSim_P10_DFBC_SMOOTH_ROBUST_BODYRATE_MIL.mo',
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
    created_packages = []
    failed = []

    for scheme_id in cores:
        pkg_name = scheme_id_to_package_name(scheme_id)
        archive_rel = MAPPING[scheme_id]
        archive_path = archive_root / archive_rel

        if not archive_path.exists():
            failed.append((scheme_id, 'Archive file not found'))
            continue

        # Create target package directory
        pkg_dir = target_root / pkg_name
        pkg_dir.mkdir(exist_ok=True)

        # Read source file
        content = archive_path.read_text(encoding='utf-8')

        # Fix within statement
        # Detect old within path
        within_match = re.search(r'within\s+([\w\.]+)\s*;', content)
        if within_match:
            old_within = within_match.group(1)
            new_within = f'MoSimQuadrotorModel.Control.{pkg_name}'
            content = fix_within_path(content, old_within, new_within)

        # Determine target filename (Core.mo)
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
