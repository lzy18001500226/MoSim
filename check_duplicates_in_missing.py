#!/usr/bin/env python3
"""检查8个missing runner是否与46个已有的重复"""
import json
from pathlib import Path

# 读取46个有runner的
mapping_path = Path('Results/control_platform/phase4_phase5_real_mcp/corrected_runner_mapping.json')
mapping_data = json.load(open(mapping_path, encoding='utf-8'))
controllers_with_runner = list(mapping_data['mapping'].keys())

# 8个missing
missing = [
    'geometric_tracking',
    'l1_adaptive', 
    'nmpc',
    'pid',
    'rl',
    'se3',
    'smc',
    'trained_neural_residual'
]

print("=== 检查8个missing是否与46个重复 ===\n")

duplicates = []
unique_missing = []

for m in missing:
    # 检查是否存在相似的名字
    base_name = m.replace('_', '')
    
    found_similar = []
    for existing in controllers_with_runner:
        existing_base = existing.replace('_', '')
        
        # 完全匹配
        if m == existing:
            found_similar.append((existing, 'EXACT'))
            continue
        
        # 包含关系
        if base_name in existing_base or existing_base in base_name:
            found_similar.append((existing, 'SIMILAR'))
            continue
        
        # 特殊检查：pid相关
        if 'pid' in m and 'pid' in existing:
            found_similar.append((existing, 'PID_FAMILY'))
            continue
        
        # 特殊检查：smc相关
        if m == 'smc' and 'smc' in existing:
            found_similar.append((existing, 'SMC_FAMILY'))
            continue
        
        # 特殊检查：nmpc相关
        if m == 'nmpc' and 'nmpc' in existing:
            found_similar.append((existing, 'NMPC_FAMILY'))
            continue
        
        # 特殊检查：rl相关
        if m == 'rl' and 'rl' in existing:
            found_similar.append((existing, 'RL_FAMILY'))
            continue
        
        # 特殊检查：se3相关
        if m == 'se3' and 'se3' in existing:
            found_similar.append((existing, 'SE3_FAMILY'))
    
    if found_similar:
        duplicates.append(m)
        print(f"{m}: 可能重复")
        for similar, match_type in found_similar:
            print(f"  - {similar} ({match_type})")
        print()
    else:
        unique_missing.append(m)
        print(f"{m}: 独立控制器，无重复")
        print()

print("=== 总结 ===")
print(f"可能重复的: {len(duplicates)}")
for d in duplicates:
    print(f"  - {d}")

print(f"\n独立的: {len(unique_missing)}")
for u in unique_missing:
    print(f"  - {u}")

print(f"\n最终结论:")
print(f"  46个有runner")
print(f"  + {len(unique_missing)}个独立missing")
print(f"  = {46 + len(unique_missing)}个真正独立的控制器")
print(f"\n  ({len(duplicates)}个missing可能是现有控制器的基础版本或变体)")
