#!/usr/bin/env python3
"""
真实Sysplorer批量验证46个控制器
Phase 4: CheckModel
Phase 5: 50s ClimbPath simulation
"""
import json
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
RESULTS_DIR = BASE_DIR / 'Results/control_platform/phase4_phase5_real_46'
CONTROLLERS_FILE = RESULTS_DIR / 'controllers_to_verify.json'

# Load controller list
controllers_data = json.load(open(CONTROLLERS_FILE, encoding='utf-8'))
all_controllers = controllers_data['controllers']

print("="*80)
print(f"真实Sysplorer验证 - {len(all_controllers)}个MWORKS控制器")
print("="*80)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Phase 4/5结果将由外层MCP工具调用填充
phase4_results = {}
phase5_results = {}

# 保存待验证列表供外层MCP循环使用
output = {
    'metadata': {
        'total_controllers': len(all_controllers),
        'start_time': datetime.now().isoformat(),
    },
    'controllers': all_controllers,
    'phase4_results': {},
    'phase5_results': {}
}

output_path = RESULTS_DIR / 'verification_progress.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"验证进度文件已初始化: {output_path}")
print()
print("请通过外层调用mcp__sysplorer__check_model和mcp__sysplorer__simulate_model")
print()
print("控制器清单:")
for idx, ctrl in enumerate(all_controllers, 1):
    print(f"  [{idx:2d}/46] {ctrl['scheme_id']:40s}")
