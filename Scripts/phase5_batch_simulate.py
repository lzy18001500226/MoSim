#!/usr/bin/env python3
"""
Phase 5批量仿真：通过MCP依次对46个控制器运行50s ClimbPath
"""
import json
from pathlib import Path

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
INPUT_FILE = BASE_DIR / 'Results/control_platform/phase4_phase5_real_46/phase5_runner_models.json'
OUTPUT_FILE = BASE_DIR / 'Results/control_platform/phase4_phase5_real_46/phase5_simulation_results.json'

def generate_batch_plan():
    """生成分批仿真计划"""
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    runner_models = data['runner_models']
    
    # 分成9批，每批5个（最后一批6个）
    batches = []
    batch_size = 5
    for i in range(0, len(runner_models), batch_size):
        batch = runner_models[i:i+batch_size]
        batches.append({
            'batch_id': len(batches) + 1,
            'models': batch
        })
    
    plan = {
        'total_controllers': len(runner_models),
        'total_batches': len(batches),
        'batch_size': batch_size,
        'batches': batches
    }
    
    plan_file = BASE_DIR / 'Results/control_platform/phase4_phase5_real_46/phase5_batch_plan.json'
    with open(plan_file, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    print(f"生成分批计划: {len(batches)} 批，每批最多 {batch_size} 个")
    print(f"保存到: {plan_file}")
    
    return batches

if __name__ == '__main__':
    generate_batch_plan()
