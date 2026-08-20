#!/usr/bin/env python3
"""
恢复剩余28个placeholder控制器从E盘归档
将归档的GRAPHICAL_MIL模型转换为当前架构的Core文件
"""
import re
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
ARCHIVE_BASE = Path('E:/刘致远18001500226/MoSim_Archive/20260818_codex_legacy_architecture/Control_Implementations_Graphical')
CATALOG_PATH = BASE_DIR / 'Config/control_platform/control_scheme_catalog.json'

# 28个placeholder需要恢复的归档映射
ARCHIVE_MAPPING = {
    # PidFamily (1)
    'neural_pid': 'PidFamily/MoSim_PID_NEURAL_PID_GRAPHICAL_MIL.mo',

    # ClassicRobust (9)
    'fopid': 'ClassicRobust/MoSim_G5_FOPID_DIRECT_GRAPHICAL_MIL.mo',
    'lqr_baseline': 'ClassicRobust/MoSim_G5_LQR_DIRECT_GRAPHICAL_MIL.mo',
    'lqi_baseline': 'ClassicRobust/MoSim_G5_LQI_DIRECT_GRAPHICAL_MIL.mo',
    'lqg': 'ClassicRobust/MoSim_P2_LQG_GRAPHICAL_MIL.mo',
    'h2_state_feedback': 'ClassicRobust/MoSim_G5_H2_STATE_FEEDBACK_DIRECT_GRAPHICAL_MIL.mo',
    'pole_placement_luenberger': 'ClassicRobust/MoSim_G5_POLE_PLACEMENT_LUENBERGER_DIRECT_GRAPHICAL_MIL.mo',
    'backstepping_baseline': 'ClassicRobust/MoSim_G5_BACKSTEPPING_DIRECT_GRAPHICAL_MIL.mo',
    'adaptive_backstepping': 'ClassicRobust/MoSim_P2_ADAPTIVE_BACKSTEPPING_GRAPHICAL_MIL.mo',
    'passivity_based_control': 'ClassicRobust/MoSim_P2_PASSIVITY_BASED_CONTROL_GRAPHICAL_MIL.mo',

    # SlidingMode (5)
    'integral_smc': 'SlidingMode/MoSim_P3_INTEGRAL_SMC_GRAPHICAL_MIL.mo',
    'terminal_smc': 'SlidingMode/MoSim_P3_TERMINAL_SMC_GRAPHICAL_MIL.mo',
    'nonsingular_terminal_smc': 'SlidingMode/MoSim_P3_NONSINGULAR_TERMINAL_SMC_GRAPHICAL_MIL.mo',
    'adaptive_smc': 'SlidingMode/MoSim_P3_ADAPTIVE_SMC_GRAPHICAL_MIL.mo',
    'fuzzy_smc': 'SlidingMode/MoSim_P3_FUZZY_SMC_GRAPHICAL_MIL.mo',

    # Optimization (5)
    'linear_mpc': 'Optimization/MoSim_P4_LINEAR_MPC_GRAPHICAL_MIL.mo',
    'robust_mpc': 'Optimization/MoSim_P4_ROBUST_MPC_GRAPHICAL_MIL.mo',
    'adaptive_mpc': 'Optimization/MoSim_P4_ADAPTIVE_MPC_GRAPHICAL_MIL.mo',
    'tube_mpc': 'Optimization/MoSim_P4_TUBE_MPC_GRAPHICAL_MIL.mo',
    'mppi': 'Optimization/MoSim_P4_MPPI_GRAPHICAL_MIL.mo',

    # GeometricFlatness (2)
    'dfbc_high_order_attitude': 'GeometricFlatness/MoSim_G5_DFBC_HIGH_ORDER_ATTITUDE_DIRECT_GRAPHICAL_MIL.mo',
    'dfbc_high_order_bodyrate': 'GeometricFlatness/MoSim_G5_DFBC_HIGH_ORDER_BODYRATE_DIRECT_GRAPHICAL_MIL.mo',
    'dfbc_smooth_robust_attitude': 'GeometricFlatness/MoSim_G5_DFBC_SMOOTH_ROBUST_ATTITUDE_DIRECT_GRAPHICAL_MIL.mo',

    # IntegratedChains (5) - Need to check archive for these
    'fixed_awff_pid': 'Sysblocks/MoSim_PID_AWFF_LINEAR_ESO_GRAPHICAL_MIL.mo',  # pid_awff_linear_eso
    'fixed_awff_l1_residual': None,  # Need to find
    'fixed_awff_l1_indi': None,  # Need to find
    'fixed_linear_mpc_l1_indi': None,  # Need to find
    'fixed_qp_nmpc_l1_indi_cbf': 'Optimization/MoSim_G5_QPNMPC_SAFETY_DIRECT_GRAPHICAL_MIL.mo',
}

def to_pkg(sid):
    special = {
        'pid': 'Pid', 'lqr': 'Lqr', 'lqi': 'Lqi', 'lqg': 'Lqg',
        'h2': 'H2', 'hinf': 'Hinf', 'mrac': 'Mrac', 'ndi': 'Ndi',
        'smc': 'Smc', 'mpc': 'Mpc', 'ilqr': 'Ilqr', 'mppi': 'Mppi',
        'nmpc': 'Nmpc', 'se3': 'Se3', 'dfbc': 'Dfbc', 'rl': 'Rl',
        'fopid': 'Fopid', 'awff': 'Awff', 'cbf': 'Cbf', 'eso': 'Eso',
        'fuzzy': 'Fuzzy', 'neural': 'Neural', 'explicit': 'Explicit',
        'feedback': 'Feedback', 'linearization': 'Linearization',
        'gain': 'Gain', 'scheduled': 'Scheduled', 'super': 'Super',
        'twisting': 'Twisting', 'robust': 'Robust', 'smooth': 'Smooth',
        'bodyrate': 'Bodyrate', 'scheduler': 'Scheduler', 'official': 'Official',
        'hover': 'Hover', 'wrench': 'Wrench', 'cascade': 'Cascade',
        'adaptive': 'Adaptive', 'backstepping': 'Backstepping', 'baseline': 'Baseline',
        'high': 'High', 'order': 'Order', 'attitude': 'Attitude',
        'state': 'State', 'output': 'Output', 'rate': 'Rate',
        'integral': 'Integral', 'boundary': 'Boundary', 'layer': 'Layer',
        'linear': 'Linear', 'trained': 'Trained', 'residual': 'Residual',
        'fixed': 'Fixed', 'basic': 'Basic', 'outer': 'Outer',
        'terminal': 'Terminal', 'nonsingular': 'Nonsingular', 'passivity': 'Passivity',
        'based': 'Based', 'control': 'Control', 'placement': 'Placement',
        'luenberger': 'Luenberger', 'pole': 'Pole', 'tube': 'Tube',
        'qp': 'Qp', 'l1': 'L1', 'indi': 'Indi',
    }
    parts = sid.split('_')
    return ''.join([special.get(p, p.capitalize()) for p in parts])

# Load catalog
data = json.load(open(CATALOG_PATH, encoding='utf-8'))
schemes = {s['scheme_id']: s for s in data['schemes']}

print("="*80)
print("恢复28个Placeholder控制器从归档")
print("="*80)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

restored_count = 0
skipped_count = 0
failed_count = 0

for sid, archive_rel_path in ARCHIVE_MAPPING.items():
    if archive_rel_path is None:
        print(f"[SKIP] {sid:35s} - 归档文件待定位")
        skipped_count += 1
        continue

    archive_path = ARCHIVE_BASE / archive_rel_path
    if not archive_path.exists():
        print(f"[FAIL] {sid:35s} - 归档不存在: {archive_rel_path}")
        failed_count += 1
        continue

    # Read archive
    content = archive_path.read_text(encoding='utf-8')

    # Extract old model name
    old_model_match = re.search(r'model\s+(MoSim_\S+?)(?:\s+"|$|\s*\n)', content)
    if not old_model_match:
        print(f"[FAIL] {sid:35s} - 无法提取模型名")
        failed_count += 1
        continue

    old_model_name = old_model_match.group(1)

    # Target info
    family = schemes[sid]['implementation_package']
    pkg = to_pkg(sid)
    new_model_name = f'{pkg}Core'
    target_path = BASE_DIR / f'Models/MoSimQuadrotorModel/Control/{family}/{pkg}/{pkg}Core.mo'

    # Transform content
    # 1. Update within
    content = re.sub(
        r'within\s+MoSimQuadrotorModel\.Control\.Implementations\.\w+\s*;',
        f'within MoSimQuadrotorModel.Control.{family}.{pkg};',
        content
    )

    # 2. Rename model declaration (handle both with and without description)
    content = re.sub(
        rf'model\s+{re.escape(old_model_name)}\s+"([^"]*?)\s*(?:\(MIL\))?\s*"',
        f'model {new_model_name} "\\1"',
        content
    )
    content = re.sub(
        rf'model\s+{re.escape(old_model_name)}(?:\s+"|$|\s*\n)',
        f'model {new_model_name} ',
        content
    )

    # 3. Rename end statement
    content = re.sub(
        rf'end\s+{re.escape(old_model_name)}\s*;',
        f'end {new_model_name};',
        content
    )

    # Write to target
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(content, encoding='utf-8')

    size_kb = len(content) / 1024
    print(f"[OK]   {sid:35s} {size_kb:6.1f}KB -> {family}/{pkg}")
    restored_count += 1

print()
print("="*80)
print("恢复总结")
print("="*80)
print(f"成功恢复: {restored_count}/28")
print(f"待定位: {skipped_count}/28")
print(f"失败: {failed_count}/28")
print()
print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
