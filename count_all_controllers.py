#!/usr/bin/env python3
"""统计所有不重复的控制器"""
import json
from pathlib import Path

# 读取Phase 4-5的mapping
mapping_path = Path('Results/control_platform/phase4_phase5_real_mcp/corrected_runner_mapping.json')
mapping_data = json.load(open(mapping_path, encoding='utf-8'))

# 46个有runner的
controllers_with_runner = list(mapping_data['mapping'].keys())

# 8个missing runner的
missing_runners = [
    'geometric_tracking',
    'l1_adaptive',
    'nmpc',
    'pid',
    'rl',
    'se3',
    'smc',
    'trained_neural_residual'
]

print("=== 46个有Runner的控制器 ===")
print(f"总数: {len(controllers_with_runner)}")
print()

# 检查是否有重复（同一个控制器的不同变体）
# 按前缀分组
from collections import defaultdict
groups = defaultdict(list)

for ctrl in controllers_with_runner:
    # 提取基础名称（去掉_baseline, _basic, _high_order等后缀）
    base_name = ctrl
    
    # 常见的变体后缀
    suffixes = ['_baseline', '_basic', '_outer', '_state_feedback', '_hover_wrench',
                '_high_order_attitude', '_high_order_bodyrate', 
                '_smooth_robust_attitude', '_smooth_robust_bodyrate',
                '_boundary_layer', '_gain_scheduler']
    
    for suffix in suffixes:
        if base_name.endswith(suffix):
            base_name = base_name[:-len(suffix)]
            break
    
    groups[base_name].append(ctrl)

print("=== 可能的重复/变体 ===")
duplicates = {k: v for k, v in groups.items() if len(v) > 1}
print(f"有变体的控制器组数: {len(duplicates)}")
for base, variants in duplicates.items():
    print(f"\n{base}:")
    for v in variants:
        print(f"  - {v}")

print(f"\n=== 统计 ===")
print(f"46个有Runner的控制器")
print(f"其中有{len(duplicates)}组存在变体")
print(f"涉及{sum(len(v) for v in duplicates.values())}个变体实现")
print(f"\n8个missing runner的控制器:")
for m in missing_runners:
    print(f"  - {m}")

print(f"\n总计: {len(controllers_with_runner)} (有runner) + {len(missing_runners)} (missing) = {len(controllers_with_runner) + len(missing_runners)} 个")
print(f"\n如果每组变体只保留1个，预计剩余: 约 {len(groups)} (有runner) + {len(missing_runners)} (missing) = {len(groups) + len(missing_runners)} 个")
