#!/usr/bin/env python3
"""
验证 IntegratedChains 控制器已转换为纯图形化架构
检查 Core 文件是否正确实例化了 Sysblock 模块
"""
import re
from pathlib import Path

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
CONTROL_DIR = BASE_DIR / 'Models/MoSimQuadrotorModel/Control/IntegratedChains'

print("="*80)
print("IntegratedChains 纯图形化架构验证")
print("="*80)

# 检查的控制器列表
controllers = [
    ('AwffL1Indi', 'AWFF_INDIControllerEquation_Sysblock'),
    ('AwffL1Residual', 'AWFF_L1ResidualControllerEquation_Sysblock'),
    ('LinearMpcL1Indi', 'AWFF_LinearMPCOuterLoopControllerEquation_Sysblock'),
    ('QpNmpcL1IndiCbf', 'AWFF_QPNMPCSafetyController_Sysblock'),
]

print("\n检查 Core 文件架构:")
print("-"*80)

all_passed = True

for ctrl_name, expected_sysblock in controllers:
    core_file = CONTROL_DIR / ctrl_name / f'{ctrl_name}Core.mo'

    if not core_file.exists():
        print(f"[ERROR] {ctrl_name:25s} Core 文件不存在")
        all_passed = False
        continue

    content = core_file.read_text(encoding='utf-8')

    # 检查1: 不应该有 extends 继承
    if re.search(r'^\s*extends\s+', content, re.MULTILINE):
        print(f"[FAIL] {ctrl_name:25s} 仍使用 extends 继承")
        all_passed = False
        continue

    # 检查2: 应该有独立的输入/输出端口声明
    if not re.search(r'input Real', content):
        print(f"[FAIL] {ctrl_name:25s} 缺少 input 端口声明")
        all_passed = False
        continue

    if not re.search(r'output Real', content):
        print(f"[FAIL] {ctrl_name:25s} 缺少 output 端口声明")
        all_passed = False
        continue

    # 检查3: 应该实例化对应的 Sysblock
    if expected_sysblock not in content:
        print(f"[FAIL] {ctrl_name:25s} 未实例化 {expected_sysblock}")
        all_passed = False
        continue

    # 检查4: 应该有 equation 连接
    if not re.search(r'equation', content):
        print(f"[FAIL] {ctrl_name:25s} 缺少 equation 连接")
        all_passed = False
        continue

    # 检查5: 应该有 controller 实例
    if 'controller' not in content:
        print(f"[FAIL] {ctrl_name:25s} 缺少 controller 实例")
        all_passed = False
        continue

    # 统计行数
    line_count = len(content.splitlines())
    print(f"[PASS] {ctrl_name:25s} {line_count:3d} 行，纯图形化架构")

# 检查 FixedAwffPid（特殊情况：Runner 本身包含完整逻辑）
print("\n检查 FixedAwffPid Runner:")
print("-"*80)
fixed_awff_pid = BASE_DIR / 'Models/MoSimQuadrotorModel/Experiment/Templates/IntegratedChains/FixedAwffPid.mo'

if fixed_awff_pid.exists():
    content = fixed_awff_pid.read_text(encoding='utf-8')
    line_count = len(content.splitlines())

    if 'AWFF_FullController_Sysblock' in content:
        print(f"[PASS] FixedAwffPid Runner     {line_count:3d} 行，完整闭环架构")
    else:
        print(f"[FAIL] FixedAwffPid Runner 缺少 AWFF_FullController_Sysblock")
        all_passed = False
else:
    print("[ERROR] FixedAwffPid.mo 不存在")
    all_passed = False

# 总结
print("\n" + "="*80)
if all_passed:
    print("[OK] 所有 IntegratedChains 控制器已成功转换为纯图形化架构！")
else:
    print("[ERROR] 部分控制器转换失败，请检查上述错误")

print("\n架构说明:")
print("-"*80)
print("纯图形化架构特征:")
print("  1. Core 文件包含显式的 input/output 端口声明")
print("  2. 实例化 Sysblock 模块（而非 extends 继承）")
print("  3. 在 equation 中连接端口和模块")
print("  4. 在 Sysplorer 中双击可看到完整的图形结构")
print("\nSysblock 作为原子模块:")
print("  - AWFF_INDIControllerEquation_Sysblock 等是封装好的控制器")
print("  - 内部用 equation 实现复杂的控制逻辑")
print("  - 对外暴露标准的 Sysblock 输入/输出端口")
print("  - 类似 Simulink 的 S-Function 或 Simscape 组件")

print("\n验证完成！")
