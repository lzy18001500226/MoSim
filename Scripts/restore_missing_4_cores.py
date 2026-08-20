#!/usr/bin/env python3
"""
恢复4个缺失的Core文件（从归档转换）
"""
from pathlib import Path

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
ARCHIVE_DIR = Path('E:/刘致远18001500226/MoSim_Archive/20260818_codex_legacy_architecture')

# 定义4个控制器的转换规则
CONTROLLERS = [
    {
        'name': 'ndi',
        'archive_file': ARCHIVE_DIR / 'Control_Implementations_Graphical/ClassicRobust/MoSim_G5_NDI_DIRECT_GRAPHICAL_MIL.mo',
        'target_file': BASE_DIR / 'Models/MoSimQuadrotorModel/Control/ClassicRobust/Ndi/NdiCore.mo',
        'old_within': 'within MoSimQuadrotorModel.Control.Implementations.ClassicRobust;',
        'new_within': 'within MoSimQuadrotorModel.Control.ClassicRobust.Ndi;',
        'old_model': 'model MoSim_G5_NDI_DIRECT_GRAPHICAL_MIL',
        'new_model': 'model NdiCore',
        'old_end': 'end MoSim_G5_NDI_DIRECT_GRAPHICAL_MIL;',
        'new_end': 'end NdiCore;'
    },
    {
        'name': 'hinf_hover_wrench',
        'archive_file': ARCHIVE_DIR / 'Control_Implementations_Graphical/ClassicRobust/MoSim_G5_HINF_HOVER_WRENCH_DIRECT_GRAPHICAL_MIL.mo',
        'target_file': BASE_DIR / 'Models/MoSimQuadrotorModel/Control/ClassicRobust/HinfHoverWrench/HinfHoverWrenchCore.mo',
        'old_within': 'within MoSimQuadrotorModel.Control.Implementations.ClassicRobust;',
        'new_within': 'within MoSimQuadrotorModel.Control.ClassicRobust.HinfHoverWrench;',
        'old_model': 'model MoSim_G5_HINF_HOVER_WRENCH_DIRECT_GRAPHICAL_MIL',
        'new_model': 'model HinfHoverWrenchCore',
        'old_end': 'end MoSim_G5_HINF_HOVER_WRENCH_DIRECT_GRAPHICAL_MIL;',
        'new_end': 'end HinfHoverWrenchCore;'
    },
    {
        'name': 'dfbc_smooth_robust_bodyrate',
        'archive_file': ARCHIVE_DIR / 'Control_Implementations_Graphical/GeometricFlatness/MoSim_G5_DFBC_SMOOTH_ROBUST_BODYRATE_DIRECT_GRAPHICAL_MIL.mo',
        'target_file': BASE_DIR / 'Models/MoSimQuadrotorModel/Control/GeometricFlatness/DfbcSmoothRobustBodyrate/DfbcSmoothRobustBodyrateCore.mo',
        'old_within': 'within MoSimQuadrotorModel.Control.Implementations.GeometricFlatness;',
        'new_within': 'within MoSimQuadrotorModel.Control.GeometricFlatness.DfbcSmoothRobustBodyrate;',
        'old_model': 'model MoSim_G5_DFBC_SMOOTH_ROBUST_BODYRATE_DIRECT_GRAPHICAL_MIL',
        'new_model': 'model DfbcSmoothRobustBodyrateCore',
        'old_end': 'end MoSim_G5_DFBC_SMOOTH_ROBUST_BODYRATE_DIRECT_GRAPHICAL_MIL;',
        'new_end': 'end DfbcSmoothRobustBodyrateCore;'
    },
    {
        'name': 'official_pid',
        'archive_file': ARCHIVE_DIR / 'Control_Implementations_Graphical/Graphical/PID/OfficialPidSysblockCore.mo',
        'target_file': BASE_DIR / 'Models/MoSimQuadrotorModel/Control/PidFamily/OfficialPid/OfficialPidCore.mo',
        'old_within': 'within MoSimQuadrotorModel.Control.Implementations.Graphical.PID;',
        'new_within': 'within MoSimQuadrotorModel.Control.PidFamily.OfficialPid;',
        'old_model': 'model OfficialPidSysblockCore',
        'new_model': 'model OfficialPidCore',
        'old_end': 'end OfficialPidSysblockCore;',
        'new_end': 'end OfficialPidCore;'
    }
]

print("="*80)
print("Restore 4 missing Core files")
print("="*80)

for ctrl in CONTROLLERS:
    print(f"\nProcessing {ctrl['name']}...")
    print(f"  Source: {ctrl['archive_file']}")
    print(f"  Target: {ctrl['target_file']}")

    if not ctrl['archive_file'].exists():
        print(f"  [ERROR] Archive file not found!")
        continue

    # 读取归档文件
    content = ctrl['archive_file'].read_text(encoding='utf-8')

    # 执行替换
    content = content.replace(ctrl['old_within'], ctrl['new_within'])
    content = content.replace(ctrl['old_model'], ctrl['new_model'])
    content = content.replace(ctrl['old_end'], ctrl['new_end'])

    # 写入目标文件
    ctrl['target_file'].write_text(content, encoding='utf-8')
    print(f"  [OK] Created {ctrl['target_file'].name}")

print("\n" + "="*80)
print("Restoration complete!")
print("="*80)
