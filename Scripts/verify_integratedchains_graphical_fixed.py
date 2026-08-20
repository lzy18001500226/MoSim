#!/usr/bin/env python3
"""
验证 IntegratedChains 控制器已正确使用图形化 Sysblock
检查 Core 文件是否实例化了图形化版本（而非 equation-based 版本）
"""
import re
from pathlib import Path

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
CONTROL_DIR = BASE_DIR / 'Models/MoSimQuadrotorModel/Control/IntegratedChains'

print("="*80)
print("IntegratedChains 图形化 Sysblock 验证")
print("="*80)

# 检查的控制器列表（预期使用图形化 Sysblock）
graphical_controllers = [
    ('AwffL1Indi', 'AWFF_INDIControllerGraphical_Sysblock'),
    ('AwffL1Residual', 'AWFF_L1ResidualControllerGraphical_Sysblock'),
    ('LinearMpcL1Indi', 'AWFF_LinearMPCControllerGraphical_Sysblock'),
]

# 检查预期保持 equation-based 的控制器
equation_controllers = [
    ('QpNmpcL1IndiCbf', 'AWFF_QPNMPCSafetyController_Sysblock'),
]

print("\n检查图形化 Sysblock Core 文件:")
print("-"*80)

all_passed = True

for ctrl_name, expected_graphical_sysblock in graphical_controllers:
    core_file = CONTROL_DIR / ctrl_name / f'{ctrl_name}Core.mo'

    if not core_file.exists():
        print(f"[ERROR] {ctrl_name:25s} Core 文件不存在")
        all_passed = False
        continue

    content = core_file.read_text(encoding='utf-8')

    # 检查1: 应该使用图形化 Sysblock
    if expected_graphical_sysblock not in content:
        print(f"[FAIL] {ctrl_name:25s} 未使用图形化 Sysblock")
        all_passed = False
        continue

    # 检查2: 不应该使用 equation-based Sysblock
    if 'ControllerEquation_Sysblock' in content:
        print(f"[FAIL] {ctrl_name:25s} 仍使用 equation-based Sysblock")
        all_passed = False
        continue

    # 检查3: 应该引用 AWFF_InnovationGraphicalControllers
    if 'AWFF_InnovationGraphicalControllers' not in content:
        print(f"[FAIL] {ctrl_name:25s} 未引用 InnovationGraphicalControllers")
        all_passed = False
        continue

    # 统计行数
    line_count = len(content.splitlines())
    print(f"[PASS] {ctrl_name:25s} {line_count:3d} 行，使用图形化 Sysblock [OK]")

print("\n检查 Equation-based Sysblock Core 文件 (合理保留):")
print("-"*80)

for ctrl_name, expected_equation_sysblock in equation_controllers:
    core_file = CONTROL_DIR / ctrl_name / f'{ctrl_name}Core.mo'

    if not core_file.exists():
        print(f"[ERROR] {ctrl_name:25s} Core 文件不存在")
        all_passed = False
        continue

    content = core_file.read_text(encoding='utf-8')

    # 检查: 应该使用 equation-based Sysblock
    if expected_equation_sysblock not in content:
        print(f"[FAIL] {ctrl_name:25s} 未使用预期的 Safety Sysblock")
        all_passed = False
        continue

    # 统计行数
    line_count = len(content.splitlines())
    print(f"[PASS] {ctrl_name:25s} {line_count:3d} 行，使用 equation-based (技术限制) [WARNING]")

# 检查 FixedAwffPid（特殊情况：Runner 本身包含完整逻辑）
print("\n检查 FixedAwffPid Runner:")
print("-"*80)
fixed_awff_pid = BASE_DIR / 'Models/MoSimQuadrotorModel/Experiment/Templates/IntegratedChains/FixedAwffPid.mo'

if fixed_awff_pid.exists():
    content = fixed_awff_pid.read_text(encoding='utf-8')
    line_count = len(content.splitlines())

    if 'AWFF_FullController_Sysblock' in content:
        print(f"[PASS] FixedAwffPid Runner     {line_count:3d} 行，完整闭环架构 [OK]")
    else:
        print(f"[FAIL] FixedAwffPid Runner 缺少 AWFF_FullController_Sysblock")
        all_passed = False
else:
    print("[ERROR] FixedAwffPid.mo 不存在")
    all_passed = False

# 总结
print("\n" + "="*80)
if all_passed:
    print("[OK] 所有 IntegratedChains 控制器已正确使用图形化 Sysblock！")
else:
    print("[ERROR] 部分控制器验证失败，请检查上述错误")

print("\n修复说明:")
print("-"*80)
print("图形化 Sysblock 特征:")
print("  1. Core 文件引用 AWFF_InnovationGraphicalControllers 模块")
print("  2. 实例化 *Graphical_Sysblock（而非 *Equation_Sysblock）")
print("  3. 在 Sysplorer 中双击可看到三层结构：外环 + 内环 + 混合器")
print("  4. 可继续双击子模块，查看内部 80+ 个图形块")
print("\nEquation-based 保留的合理性:")
print("  - QpNmpcL1IndiCbf: 包含 QP/NMPC/CBF 优化逻辑，必须用 equation")
print("  - 技术类比: Simulink 中的 MATLAB Function Block")

print("\n验证完成！")
