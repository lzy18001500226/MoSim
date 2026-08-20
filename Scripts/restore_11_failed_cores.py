#!/usr/bin/env python3
"""
Restore 11 Phase 5 failed controllers from archive to working Core files
Transform: MIL model name -> Core, update within path, preserve Sysblock structure
"""
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
ARCHIVE_BASE = Path('E:/刘致远18001500226/MoSim_Archive/20260818_codex_legacy_architecture/Control_Implementations_Graphical')

# Archive路径映射
ARCHIVE_MAPPING = {
    'cascade_pid': 'PidFamily/MoSim_PID_CASCADE_PID_GRAPHICAL_MIL.mo',
    'fuzzy_pid': 'PidFamily/MoSim_PID_FUZZY_PID_GRAPHICAL_MIL.mo',
    'gain_scheduled_pid': 'PidFamily/MoSim_PID_GAIN_SCHEDULED_PID_GRAPHICAL_MIL.mo',
    'official_pid': 'Graphical/PID/OfficialPidSysblockCore.mo',
    'ndi': 'ClassicRobust/MoSim_Classic_NDI_MIL.mo',
    'hinf_hover_wrench': 'ClassicRobust/MoSim_P10_HINF_HOVER_WRENCH_MIL.mo',
    'dfbc_smooth_robust_bodyrate': 'GeometricFlatness/MoSim_P10_DFBC_SMOOTH_ROBUST_BODYRATE_MIL.mo',
    'explicit_gain_scheduled_mpc': 'Optimization/MoSim_P4_EXPLICIT_GAIN_SCHEDULED_MPC_GRAPHICAL_MIL.mo',
    'ilqr': 'Optimization/MoSim_P4_ILQR_GRAPHICAL_MIL.mo',
    'super_twisting_smc': 'SlidingMode/MoSim_P3_SUPER_TWISTING_SMC_GRAPHICAL_MIL.mo',
    'rl_gain_scheduler': 'Learning/MoSim_P9_RL_GAIN_SCHEDULER_GRAPHICAL_MIL.mo',
}

# 目标Core文件路径
CORE_PATH_MAP = {
    'cascade_pid': 'Models/MoSimQuadrotorModel/Control/PidFamily/CascadePid/CascadePidCore.mo',
    'fuzzy_pid': 'Models/MoSimQuadrotorModel/Control/PidFamily/FuzzyPid/FuzzyPidCore.mo',
    'gain_scheduled_pid': 'Models/MoSimQuadrotorModel/Control/PidFamily/GainScheduledPid/GainScheduledPidCore.mo',
    'official_pid': 'Models/MoSimQuadrotorModel/Control/PidFamily/OfficialPid/OfficialPidCore.mo',
    'ndi': 'Models/MoSimQuadrotorModel/Control/ClassicRobust/Ndi/NdiCore.mo',
    'hinf_hover_wrench': 'Models/MoSimQuadrotorModel/Control/ClassicRobust/HinfHoverWrench/HinfHoverWrenchCore.mo',
    'dfbc_smooth_robust_bodyrate': 'Models/MoSimQuadrotorModel/Control/GeometricFlatness/DfbcSmoothRobustBodyrate/DfbcSmoothRobustBodyrateCore.mo',
    'explicit_gain_scheduled_mpc': 'Models/MoSimQuadrotorModel/Control/Optimization/ExplicitGainScheduledMpc/ExplicitGainScheduledMpcCore.mo',
    'ilqr': 'Models/MoSimQuadrotorModel/Control/Optimization/Ilqr/IlqrCore.mo',
    'super_twisting_smc': 'Models/MoSimQuadrotorModel/Control/SlidingMode/SuperTwistingSmc/SuperTwistingSmcCore.mo',
    'rl_gain_scheduler': 'Models/MoSimQuadrotorModel/Control/Learning/RlGainScheduler/RlGainSchedulerCore.mo',
}

# 家族映射
FAMILY_MAP = {
    'cascade_pid': 'PidFamily',
    'fuzzy_pid': 'PidFamily',
    'gain_scheduled_pid': 'PidFamily',
    'official_pid': 'PidFamily',
    'ndi': 'ClassicRobust',
    'hinf_hover_wrench': 'ClassicRobust',
    'dfbc_smooth_robust_bodyrate': 'GeometricFlatness',
    'explicit_gain_scheduled_mpc': 'Optimization',
    'ilqr': 'Optimization',
    'super_twisting_smc': 'SlidingMode',
    'rl_gain_scheduler': 'Learning',
}

def scheme_to_pkg(sid):
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
    }
    parts = sid.split('_')
    return ''.join([special.get(p, p.capitalize()) for p in parts])

def transform_archive_to_core(archive_path, scheme_id):
    """
    Transform archived MIL model to Core:
    1. Read archive content
    2. Rename model: MoSim_XXX_GRAPHICAL_MIL -> XXXCore
    3. Update within path: Control.Implementations.{family} -> Control.{family}.{PkgName}
    4. Preserve all Sysblock components and connections
    """
    content = archive_path.read_text(encoding='utf-8')

    pkg = scheme_to_pkg(scheme_id)
    family = FAMILY_MAP[scheme_id]

    # Special case: official_pid archive already has correct name
    if scheme_id == 'official_pid':
        # Just update within path if needed
        content = re.sub(
            r'within\s+MoSimQuadrotorModel\.Control\.Implementations\.PidFamily\.OfficialPid\s*;',
            f'within MoSimQuadrotorModel.Control.{family}.{pkg};',
            content
        )
        # Model name should already be OfficialPidCore
        return content

    # Step 1: Extract old model name from archive
    # Pattern: model MoSim_PID_CASCADE_PID_GRAPHICAL_MIL "..."
    # Pattern: model MoSim_Classic_NDI_MIL "..."
    # Pattern: model MoSim_P10_HINF_HOVER_WRENCH_MIL "..."
    # Some models don't have description string, match without requiring "
    old_model_match = re.search(r'model\s+(MoSim_\S+?)(?:\s+"|$|\s*\n)', content)
    if not old_model_match:
        raise ValueError(f"Cannot find model declaration in {archive_path}")

    old_model_name = old_model_match.group(1)
    new_model_name = f"{pkg}Core"

    # Step 2: Update within path
    # From: within MoSimQuadrotorModel.Control.Implementations.{family};
    # To: within MoSimQuadrotorModel.Control.{family}.{PkgName};
    content = re.sub(
        r'within\s+MoSimQuadrotorModel\.Control\.Implementations\.\w+\s*;',
        f'within MoSimQuadrotorModel.Control.{family}.{pkg};',
        content
    )

    # Step 3: Rename model declaration
    # From: model MoSim_PID_CASCADE_PID_GRAPHICAL_MIL "cascade_pid graphical control core (MIL)"
    # To: model CascadePidCore "cascade_pid graphical control core"
    content = re.sub(
        rf'model\s+{re.escape(old_model_name)}\s+"([^"]*?)\s*(?:\(MIL\))?\s*"',
        f'model {new_model_name} "\\1"',
        content
    )

    # Step 4: Rename end statement
    # From: end MoSim_PID_CASCADE_PID_GRAPHICAL_MIL;
    # To: end CascadePidCore;
    content = re.sub(
        rf'end\s+{re.escape(old_model_name)}\s*;',
        f'end {new_model_name};',
        content
    )

    return content

print("="*80)
print("11个Phase 5失败控制器恢复流程")
print("="*80)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

success_count = 0
fail_count = 0
results = {}

for idx, sid in enumerate(ARCHIVE_MAPPING.keys(), 1):
    archive_rel = ARCHIVE_MAPPING[sid]
    archive_path = ARCHIVE_BASE / archive_rel
    core_rel = CORE_PATH_MAP[sid]
    core_path = BASE_DIR / core_rel

    print(f"[{idx}/11] {sid:30s}")
    print(f"        归档: {archive_rel}")
    print(f"        目标: {core_rel}")

    if not archive_path.exists():
        print(f"        [FAIL] 归档文件不存在")
        fail_count += 1
        results[sid] = {'status': 'fail', 'reason': 'archive_not_found'}
        print()
        continue

    try:
        # Transform archive content to Core format
        transformed = transform_archive_to_core(archive_path, sid)

        # Write to Core file
        core_path.parent.mkdir(parents=True, exist_ok=True)
        core_path.write_text(transformed, encoding='utf-8')

        size_kb = len(transformed) / 1024
        print(f"        [OK] 已写入 {size_kb:.1f}KB")
        success_count += 1
        results[sid] = {'status': 'success', 'size_kb': size_kb}

    except Exception as e:
        print(f"        [FAIL] {e}")
        fail_count += 1
        results[sid] = {'status': 'fail', 'reason': str(e)}

    print()

print("="*80)
print("恢复总结")
print("="*80)
print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()
print(f"成功: {success_count}/11")
print(f"失败: {fail_count}/11")
print()

if success_count == 11:
    print("[OK] 所有11个控制器Core文件已从归档恢复")
    print("下一步: 运行CheckModel验证所有Core文件")
else:
    print(f"[WARNING] {fail_count}个控制器恢复失败")

print("="*80)
