#!/usr/bin/env python3
"""
Build mapping between catalog scheme_id and archived Core files
"""
import json
import os
from pathlib import Path

# Load catalog
catalog_path = Path('Config/control_platform/control_scheme_catalog.json')
data = json.load(open(catalog_path, encoding='utf-8'))
cores = [s['scheme_id'] for s in data.get('schemes', [])
         if s.get('execution_kind') == 'graphical_control_core']

# Archive root
archive_root = Path('E:/刘致远18001500226/MoSim_Archive/20260818_codex_legacy_architecture/Control_Implementations_Graphical')

# Manual mapping table (based on file inspection)
MANUAL_MAPPING = {
    # PID family
    'cascade_pid': 'PidFamily/MoSim_PID_CASCADE_PID_GRAPHICAL_MIL.mo',
    'gain_scheduled_pid': 'PidFamily/MoSim_PID_GAIN_SCHEDULED_PID_GRAPHICAL_MIL.mo',
    'fuzzy_pid': 'PidFamily/MoSim_PID_FUZZY_PID_GRAPHICAL_MIL.mo',
    'neural_pid': 'PidFamily/MoSim_PID_NEURAL_PID_GRAPHICAL_MIL.mo',
    'official_pid': 'Graphical/PID/OfficialPidCoreSysblock.mo',
    'fopid': 'ClassicRobust/MoSim_Classic_FOPID_MIL.mo',

    # AWFF family (3 variants using Sysblock cores)
    'fixed_awff_pid': 'Graphical/AWFF/AwffFullControllerCoreSysblock.mo',
    'fixed_awff_l1_residual': 'Graphical/AWFF/AwffL1ResidualControllerCoreSysblock.mo',
    'fixed_awff_l1_indi': 'Graphical/AWFF/AwffL1IndiControllerCoreSysblock.mo',

    # Linear robust state feedback
    'lqr_baseline': 'ClassicRobust/MoSim_WaveA_LQR_MIL.mo',
    'lqi_baseline': 'ClassicRobust/MoSim_WaveA_LQI_MIL.mo',
    'lqg': 'ClassicRobust/MoSim_P2_LQG_GRAPHICAL_MIL.mo',
    'h2_state_feedback': 'ClassicRobust/MoSim_Classic_H2_STATE_FEEDBACK_MIL.mo',
    'hinf_hover_wrench': 'ClassicRobust/MoSim_P10_HINF_HOVER_WRENCH_MIL.mo',
    'pole_placement_luenberger': 'ClassicRobust/MoSim_Classic_POLE_PLACEMENT_LUENBERGER_MIL.mo',

    # Nonlinear adaptive
    'backstepping_baseline': 'ClassicRobust/MoSim_WaveA_BACKSTEPPING_MIL.mo',
    'adaptive_backstepping': 'ClassicRobust/MoSim_P2_ADAPTIVE_BACKSTEPPING_GRAPHICAL_MIL.mo',
    'feedback_linearization': 'ClassicRobust/MoSim_P2_FEEDBACK_LINEARIZATION_GRAPHICAL_MIL.mo',
    'mrac': 'ClassicRobust/MoSim_Classic_MRAC_MIL.mo',
    'ndi': 'ClassicRobust/MoSim_Classic_NDI_MIL.mo',
    'passivity_based_control': 'ClassicRobust/MoSim_P2_PASSIVITY_BASED_CONTROL_GRAPHICAL_MIL.mo',

    # Sliding mode
    'integral_smc': 'SlidingMode/MoSim_P3_INTEGRAL_SMC_GRAPHICAL_MIL.mo',
    'terminal_smc': 'SlidingMode/MoSim_P3_TERMINAL_SMC_GRAPHICAL_MIL.mo',
    'nonsingular_terminal_smc': 'SlidingMode/MoSim_P3_NONSINGULAR_TERMINAL_SMC_GRAPHICAL_MIL.mo',
    'super_twisting_smc': 'SlidingMode/MoSim_P3_SUPER_TWISTING_SMC_GRAPHICAL_MIL.mo',
    'adaptive_smc': 'SlidingMode/MoSim_P3_ADAPTIVE_SMC_GRAPHICAL_MIL.mo',
    'fuzzy_smc': 'SlidingMode/MoSim_P3_FUZZY_SMC_GRAPHICAL_MIL.mo',
    'smc_boundary_layer': 'SlidingMode/MoSim_G9_SMC_BOUNDARY_LAYER_GRAPHICAL_OVERVIEW.mo',

    # Optimization predictive
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

    # Geometric flatness
    'se3_basic': 'GeometricFlatness/MoSim_G9_SE3_GRAPHICAL_OVERVIEW.mo',
    'dfbc_basic': 'GeometricFlatness/MoSim_G9_DFBC_GRAPHICAL_OVERVIEW.mo',
    'dfbc_high_order_attitude': 'GeometricFlatness/MoSim_P10_DFBC_HIGH_ORDER_ATTITUDE_MIL.mo',
    'dfbc_high_order_bodyrate': 'GeometricFlatness/MoSim_P10_DFBC_HIGH_ORDER_BODYRATE_MIL.mo',
    'dfbc_smooth_robust_attitude': 'GeometricFlatness/MoSim_P10_DFBC_SMOOTH_ROBUST_ATTITUDE_MIL.mo',
    'dfbc_smooth_robust_bodyrate': 'GeometricFlatness/MoSim_P10_DFBC_SMOOTH_ROBUST_BODYRATE_MIL.mo',

    # Learning
    'trained_neural_residual': 'Learning/MoSim_P9_TRAINED_NEURAL_RESIDUAL_GRAPHICAL_MIL.mo',
    'rl_gain_scheduler': 'Learning/MoSim_P9_RL_GAIN_SCHEDULER_GRAPHICAL_MIL.mo',
}

# Target package name conversion
def scheme_id_to_package_name(scheme_id):
    """Convert scheme_id to PascalCase package name"""
    parts = scheme_id.split('_')
    # Special cases
    special = {
        'pid': 'Pid',
        'lqr': 'Lqr',
        'lqi': 'Lqi',
        'lqg': 'Lqg',
        'h2': 'H2',
        'hinf': 'Hinf',
        'mrac': 'Mrac',
        'ndi': 'Ndi',
        'smc': 'Smc',
        'mpc': 'Mpc',
        'ilqr': 'Ilqr',
        'mppi': 'Mppi',
        'nmpc': 'Nmpc',
        'qp': 'Qp',
        'se3': 'Se3',
        'dfbc': 'Dfbc',
        'rl': 'Rl',
        'awff': 'Awff',
        'l1': 'L1',
        'indi': 'Indi',
        'cbf': 'Cbf',
        'fopid': 'Fopid',
    }

    result = []
    for part in parts:
        if part in special:
            result.append(special[part])
        else:
            result.append(part.capitalize())
    return ''.join(result)

# Generate mapping report
if __name__ == '__main__':
    print(f'Total graphical_control_core schemes: {len(cores)}')
    print(f'Manual mappings defined: {len(MANUAL_MAPPING)}')
    print()

    missing = [c for c in cores if c not in MANUAL_MAPPING]
    if missing:
        print(f'WARNING: {len(missing)} schemes not mapped:')
        for m in missing:
            print(f'  - {m}')
        print()

    print('Mapping table:')
    print('=' * 120)
    print(f'{"Scheme ID":<40} {"Package Name":<30} {"Archive Path":<50}')
    print('=' * 120)

    for scheme_id in cores:
        pkg_name = scheme_id_to_package_name(scheme_id)
        archive_rel = MANUAL_MAPPING.get(scheme_id, 'NOT MAPPED')
        archive_full = archive_root / archive_rel if archive_rel != 'NOT MAPPED' else None
        exists = 'OK' if archive_full and archive_full.exists() else 'MISSING'

        print(f'{scheme_id:<40} {pkg_name:<30} {exists:<8} {archive_rel}')
