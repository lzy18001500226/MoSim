#!/usr/bin/env python3
"""
Archive mapping for 11 Phase 5 failed controllers using placeholder templates
"""

# Archive路径映射
ARCHIVE_MAPPING = {
    # PID Family
    'cascade_pid': 'PidFamily/MoSim_PID_CASCADE_PID_GRAPHICAL_MIL.mo',
    'fuzzy_pid': 'PidFamily/MoSim_PID_FUZZY_PID_GRAPHICAL_MIL.mo',
    'gain_scheduled_pid': 'PidFamily/MoSim_PID_GAIN_SCHEDULED_PID_GRAPHICAL_MIL.mo',
    'official_pid': 'Graphical/PID/OfficialPidSysblockCore.mo',  # 特殊路径

    # Classic Robust
    'ndi': 'ClassicRobust/MoSim_Classic_NDI_MIL.mo',
    'hinf_hover_wrench': 'ClassicRobust/MoSim_P10_HINF_HOVER_WRENCH_MIL.mo',

    # Geometric Flatness
    'dfbc_smooth_robust_bodyrate': 'GeometricFlatness/MoSim_P10_DFBC_SMOOTH_ROBUST_BODYRATE_MIL.mo',

    # Optimization
    'explicit_gain_scheduled_mpc': 'Optimization/MoSim_P4_EXPLICIT_GAIN_SCHEDULED_MPC_GRAPHICAL_MIL.mo',
    'ilqr': 'Optimization/MoSim_P4_ILQR_GRAPHICAL_MIL.mo',

    # Sliding Mode
    'super_twisting_smc': 'SlidingMode/MoSim_P3_SUPER_TWISTING_SMC_GRAPHICAL_MIL.mo',

    # Learning
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

if __name__ == '__main__':
    print("11个失败控制器的归档映射:")
    print("="*80)
    for sid, archive_rel in ARCHIVE_MAPPING.items():
        print(f"{sid:30s} -> {archive_rel}")
