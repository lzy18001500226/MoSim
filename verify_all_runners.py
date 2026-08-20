#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证46个控制器的Runner模板是否一致"""
from pathlib import Path
import re
import json
import sys

# 强制UTF-8输出
sys.stdout.reconfigure(encoding='utf-8')

MODELS_DIR = Path('Models/MoSimQuadrotorModel')

# 读取46个有runner的
mapping_path = Path('Results/control_platform/phase4_phase5_real_mcp/corrected_runner_mapping.json')
mapping_data = json.load(open(mapping_path, encoding='utf-8'))

# 关键组件的正则模式
PATTERNS = {
    'trajectory': r'MoSimQuadrotorModel\.Guidance\.Trajectories\.MultiModeTrajectory',
    'core': r'MoSimQuadrotorModel\.Control\.\w+\.\w+\.\w+Core',
    'adapter': r'MoSimQuadrotorModel\.Experiment\.Adapters\.GraphicalScalarRotorPreview',
    'fault_compensator': r'MoSimQuadrotorModel\.Experiment\.Baselines\.ScheduledRotorEfficiencyCompensator',
    'esc': r'MoSimQuadrotorModel\.Vehicle\.BaseModules\.ESCDrive',
    'battery': r'MoSimQuadrotorModel\.Vehicle\.BaseModules\.BatteryPower',
    'plant': r'MoSimQuadrotorModel\.Vehicle\.Sunray150Assembly',
}

def check_runner_structure(runner_path):
    """检查Runner文件的组件结构"""
    if not runner_path.exists():
        return None
    
    content = runner_path.read_text(encoding='utf-8')
    
    result = {}
    for key, pattern in PATTERNS.items():
        if re.search(pattern, content):
            result[key] = True
        else:
            result[key] = False
    
    return result

print("=== 46 Runner Template Verification ===\n")

# 转换fully-qualified name到文件路径
def fqn_to_path(fqn):
    parts = fqn.split('.')
    relative_path = '/'.join(parts[1:])
    return MODELS_DIR / (relative_path + '.mo')

inconsistent = []
missing_files = []
all_structures = []

for ctrl_name, fqn in mapping_data['mapping'].items():
    runner_path = fqn_to_path(fqn)
    
    if not runner_path.exists():
        missing_files.append((ctrl_name, runner_path))
        continue
    
    structure = check_runner_structure(runner_path)
    if structure:
        all_structures.append((ctrl_name, structure))
        
        # 检查是否缺少关键组件
        missing_components = [k for k, v in structure.items() if not v]
        if missing_components:
            inconsistent.append((ctrl_name, missing_components))

print(f"Checked: {len(all_structures)} Runner files")
print()

if missing_files:
    print(f"WARNING: {len(missing_files)} files not found:")
    for name, path in missing_files[:5]:
        print(f"  - {name}")
    if len(missing_files) > 5:
        print(f"  ... and {len(missing_files)-5} more")
    print()

if inconsistent:
    print(f"WARNING: {len(inconsistent)} Runners missing components:")
    for name, missing in inconsistent[:10]:
        print(f"  - {name}: missing {', '.join(missing)}")
    if len(inconsistent) > 10:
        print(f"  ... and {len(inconsistent)-10} more")
    print()
else:
    print(f"OK: All {len(all_structures)} Runners have complete components:")
    print("  - MultiModeTrajectory")
    print("  - Core")
    print("  - GraphicalScalarRotorPreview")
    print("  - ScheduledRotorEfficiencyCompensator")
    print("  - ESCDrive")
    print("  - BatteryPower")
    print("  - Sunray150Assembly")
    print()

if all_structures:
    complete = sum(1 for _, s in all_structures if all(s.values()))
    print(f"Complete structure: {complete}/{len(all_structures)} ({100*complete/len(all_structures):.1f}%)")

print("\n=== Conclusion ===")
if not inconsistent and not missing_files:
    print("OK: 46 Runners use consistent template")
    print("OK: Can use same template for 7 missing runners")
else:
    print("WARNING: Inconsistencies found, need to fix first")

# 保存结果
output = {
    'timestamp': '2026-08-19',
    'total_checked': len(all_structures),
    'missing_files': len(missing_files),
    'missing_file_list': [name for name, _ in missing_files],
    'inconsistent': len(inconsistent),
    'inconsistent_list': [{name: missing} for name, missing in inconsistent],
    'complete': sum(1 for _, s in all_structures if all(s.values())) if all_structures else 0,
    'template_valid': not inconsistent and not missing_files
}

output_path = Path('Results/control_platform/phase4_phase5_real_mcp/runner_template_verification.json')
output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
print(f"\nSaved to: {output_path}")
