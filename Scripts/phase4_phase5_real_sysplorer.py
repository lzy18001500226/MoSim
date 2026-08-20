#!/usr/bin/env python3
"""
Phase 4 + Phase 5: 真实Sysplorer验证 - 46个MWORKS控制器
- Phase 4: 真实Sysplorer CheckModel
- Phase 5: 真实50s ClimbPath仿真
"""
import json
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
CATALOG_PATH = BASE_DIR / 'Config/control_platform/control_scheme_catalog.json'
RESULTS_DIR = BASE_DIR / 'Results/control_platform/phase4_phase5_real_46'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def to_pkg(sid):
    special = {
        'pid': 'Pid', 'lqr': 'Lqr', 'lqi': 'Lqi', 'lqg': 'Lqg',
        'h2': 'H2', 'hinf': 'Hinf', 'mrac': 'Mrac', 'ndi': 'Ndi',
        'smc': 'Smc', 'mpc': 'Mpc', 'ilqr': 'Ilqr', 'mppi': 'Mppi',
        'nmpc': 'Nmpc', 'se3': 'Se3', 'dfbc': 'Dfbc', 'rl': 'Rl',
        'fopid': 'Fopid', 'awff': 'Awff', 'cbf': 'Cbf', 'eso': 'Eso',
        'fuzzy': 'Fuzzy', 'neural': 'Neural', 'explicit': 'Explicit',
        'feedback': 'Feedback', 'linearization': 'Linearization',
        'gain': 'Gain', 'scheduled': 'Scheduled', 'super': 'Super',
        'twisting': 'Twisting', 'robust': 'Robust', 'smooth': 'Smooth',
        'bodyrate': 'Bodyrate', 'scheduler': 'Scheduler', 'official': 'Official',
        'hover': 'Hover', 'wrench': 'Wrench', 'cascade': 'Cascade',
        'adaptive': 'Adaptive', 'backstepping': 'Backstepping', 'baseline': 'Baseline',
        'high': 'High', 'order': 'Order', 'attitude': 'Attitude',
        'state': 'State', 'output': 'Output', 'rate': 'Rate',
        'integral': 'Integral', 'boundary': 'Boundary', 'layer': 'Layer',
        'linear': 'Linear', 'trained': 'Trained', 'residual': 'Residual',
        'fixed': 'Fixed', 'basic': 'Basic', 'outer': 'Outer',
        'terminal': 'Terminal', 'nonsingular': 'Nonsingular', 'passivity': 'Passivity',
        'based': 'Based', 'control': 'Control', 'placement': 'Placement',
        'luenberger': 'Luenberger', 'pole': 'Pole', 'tube': 'Tube',
        'qp': 'Qp', 'l1': 'L1', 'indi': 'Indi',
    }
    parts = sid.split('_')
    return ''.join([special.get(p, p.capitalize()) for p in parts])

# Load catalog
data = json.load(open(CATALOG_PATH, encoding='utf-8'))
schemes = {s['scheme_id']: s for s in data['schemes']}

# Find all 46 MWORKS controllers
all_controllers = []
for sid, scheme in schemes.items():
    if 'implementation_package' in scheme and scheme.get('execution_kind') == 'graphical_control_core':
        all_controllers.append(sid)

all_controllers.sort()

print("="*80)
print("PHASE 4 + PHASE 5: 真实Sysplorer验证 - 46个MWORKS控制器")
print("="*80)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"控制器总数: {len(all_controllers)}")
print()

# ============================================================================
# PHASE 4: 真实Sysplorer CheckModel
# ============================================================================
print("="*80)
print("PHASE 4: 真实Sysplorer CheckModel验证")
print("="*80)
print(f"预计时间: {len(all_controllers)} controllers x ~30s = ~{len(all_controllers)*30/60:.0f} minutes\n")

phase4_results = {}
phase4_pass = 0
phase4_fail = 0
phase4_start = time.time()

# 这里会调用真实的Sysplorer MCP check_model
# 由调用者通过MCP工具执行

print("Phase 4需要通过MCP工具逐个调用check_model")
print("请在外层脚本中调用mcp__sysplorer__check_model")
print()
print("控制器列表:")
for idx, sid in enumerate(all_controllers, 1):
    scheme = schemes[sid]
    family = scheme['implementation_package']
    pkg = to_pkg(sid)
    model_name = f"MoSimQuadrotorModel.Control.{family}.{pkg}.{pkg}Core"
    print(f"  [{idx:2d}/46] {sid:40s} -> {model_name}")

# 保存控制器列表供MCP调用
controllers_info = []
for sid in all_controllers:
    scheme = schemes[sid]
    family = scheme['implementation_package']
    pkg = to_pkg(sid)
    controllers_info.append({
        'scheme_id': sid,
        'family': family,
        'pkg': pkg,
        'core_model': f"MoSimQuadrotorModel.Control.{family}.{pkg}.{pkg}Core",
        'runner_model': f"MoSimQuadrotorModel.Experiment.{family}.{pkg}GraphicalRunner"
    })

info_path = RESULTS_DIR / 'controllers_to_verify.json'
with open(info_path, 'w', encoding='utf-8') as f:
    json.dump({
        'total': len(all_controllers),
        'controllers': controllers_info
    }, f, indent=2, ensure_ascii=False)

print()
print(f"控制器信息已保存: {info_path}")
print()
print("=" * 80)
print("下一步: 请通过MCP工具调用真实的Sysplorer验证")
print("=" * 80)
