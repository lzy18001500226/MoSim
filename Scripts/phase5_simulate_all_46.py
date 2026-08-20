#!/usr/bin/env python3
"""
Phase 5: 对所有46个控制器运行50s ClimbPath仿真
"""
import json
import sys
from pathlib import Path

# 添加MCP路径
sys.path.insert(0, str(Path(__file__).parent))

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
CONTROLLERS_FILE = BASE_DIR / 'Results/control_platform/phase4_phase5_real_46/controllers_to_verify.json'
OUTPUT_DIR = BASE_DIR / 'Results/control_platform/phase4_phase5_real_46'

def main():
    """生成Phase 5批量仿真脚本"""
    
    with open(CONTROLLERS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    controllers = data['controllers']
    
    print("="*80)
    print(f"Phase 5: 准备对 {len(controllers)} 个控制器运行50s ClimbPath仿真")
    print("="*80)
    
    # 输出Python列表供MCP调用
    runner_models = [c['runner_model'] for c in controllers]
    
    output_file = OUTPUT_DIR / 'phase5_runner_models.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(runner_models),
            'runner_models': runner_models
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n已生成 {output_file}")
    print(f"包含 {len(runner_models)} 个runner模型")
    print("\n前5个runner模型:")
    for i, model in enumerate(runner_models[:5], 1):
        print(f"  {i}. {model}")

if __name__ == '__main__':
    main()
