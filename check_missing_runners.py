#!/usr/bin/env python3
"""检查8个missing runner的控制器是否有Core"""
from pathlib import Path
import json

MODELS_DIR = Path('Models/MoSimQuadrotorModel')

MISSING_RUNNERS = [
    'geometric_tracking',
    'l1_adaptive',
    'nmpc',
    'pid',
    'rl',
    'se3',
    'smc',
    'trained_neural_residual'
]

# 可能的Core命名模式
CORE_PATTERNS = [
    '{name}Core',
    '{Name}Core',
    '{NAME}Core',
]

# 可能的Core位置
CONTROL_DIRS = [
    MODELS_DIR / 'Control',
    MODELS_DIR / 'Control' / 'PID',
    MODELS_DIR / 'Control' / 'SlidingMode',
    MODELS_DIR / 'Control' / 'GeometricFlatness',
    MODELS_DIR / 'Control' / 'Learning',
    MODELS_DIR / 'Control' / 'OptimizationPredictive',
]

def to_pascal_case(name):
    """Convert snake_case to PascalCase"""
    return ''.join(word.capitalize() for word in name.split('_'))

def search_core(controller_name):
    """搜索控制器的Core文件"""
    pascal_name = to_pascal_case(controller_name)
    
    # 生成所有可能的Core文件名
    possible_names = [
        f'{controller_name}Core',
        f'{pascal_name}Core',
        f'{controller_name.upper()}Core',
    ]
    
    # 在整个Control目录下递归搜索
    control_dir = MODELS_DIR / 'Control'
    if control_dir.exists():
        for mo_file in control_dir.rglob('*.mo'):
            file_stem = mo_file.stem
            if any(name.lower() == file_stem.lower() for name in possible_names):
                return mo_file
    
    return None

print("=== Checking 8 Missing Runner Controllers ===\n")

results = {}

for controller in MISSING_RUNNERS:
    print(f"Checking: {controller}")
    
    core_file = search_core(controller)
    
    if core_file:
        print(f"  FOUND Core: {core_file}")
        results[controller] = {
            'has_core': True,
            'core_path': str(core_file),
            'action': 'CREATE_RUNNER'
        }
    else:
        print(f"  NO Core found")
        results[controller] = {
            'has_core': False,
            'core_path': None,
            'action': 'DEPRECATED'
        }
    print()

# 统计
has_core = sum(1 for r in results.values() if r['has_core'])
no_core = len(results) - has_core

print("=== Summary ===")
print(f"Controllers with Core: {has_core}")
print(f"Controllers without Core: {no_core}")

if has_core > 0:
    print("\nNeed to create Runner for:")
    for name, data in results.items():
        if data['has_core']:
            print(f"  - {name} ({data['core_path']})")

if no_core > 0:
    print("\nShould be deprecated:")
    for name, data in results.items():
        if not data['has_core']:
            print(f"  - {name}")

# 保存结果
output = {
    'timestamp': '2026-08-19',
    'missing_runners': results,
    'summary': {
        'has_core': has_core,
        'no_core': no_core
    }
}

output_path = Path('Results/control_platform/phase4_phase5_real_mcp/missing_runners_analysis.json')
output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
print(f"\nSaved to: {output_path}")
