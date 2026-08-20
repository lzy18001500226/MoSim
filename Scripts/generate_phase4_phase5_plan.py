#!/usr/bin/env python3
"""
Phase 4 + Phase 5: ALL 46 controllers - REAL Sysplorer MCP execution
Claude will execute MCP calls inline as this script outputs requests
"""
import json
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
PHASE3_PATH = BASE_DIR / 'Results/control_platform/phase3_graphical_core_rebuild/phase3_final_restoration_summary.json'
RESULTS_DIR = BASE_DIR / 'Results/control_platform/phase4_phase5_real_mcp'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def scheme_to_pkg(sid):
    special = {
        'pid': 'Pid', 'lqr': 'Lqr', 'lqi': 'Lqi', 'lqg': 'Lqg',
        'h2': 'H2', 'hinf': 'Hinf', 'mrac': 'Mrac', 'ndi': 'Ndi',
        'smc': 'Smc', 'mpc': 'Mpc', 'ilqr': 'Ilqr', 'mppi': 'Mppi',
        'nmpc': 'Nmpc', 'se3': 'Se3', 'dfbc': 'Dfbc', 'rl': 'Rl',
        'fopid': 'Fopid', 'awff': 'Awff', 'cbf': 'Cbf', 'eso': 'Eso',
        'l1': 'L1', 'indi': 'Indi', 'qp': 'Qp',
    }
    parts = sid.split('_')
    return ''.join([special.get(p, p.capitalize()) for p in parts])

# Load Phase 3 to get exact 46-controller scope
phase3_data = json.load(open(PHASE3_PATH, encoding='utf-8'))
phase3_controllers = set(phase3_data['results'].keys())

# Load catalog
catalog_path = BASE_DIR / 'Config/control_platform/control_scheme_catalog.json'
data = json.load(open(catalog_path, encoding='utf-8'))
schemes = {s['scheme_id']: s for s in data['schemes']}

# ALL 46 controllers from Phase 3
all_controllers = sorted(phase3_controllers)

# Generate the test plan for Claude to execute
test_plan = {
    'controllers': [],
    'phase4_runners': [],
    'phase5_runners': []
}

for sid in all_controllers:
    if sid not in schemes:
        continue

    scheme = schemes[sid]
    family = scheme['implementation_package']
    pkg_name = scheme_to_pkg(sid)
    runner_class = f'MoSimQuadrotorModel.Experiment.{family}.{pkg_name}GraphicalRunner'

    test_plan['controllers'].append({
        'scheme_id': sid,
        'runner_class': runner_class,
        'family': family,
        'pkg_name': pkg_name
    })
    test_plan['phase4_runners'].append(runner_class)

# Save test plan
plan_path = RESULTS_DIR / 'test_plan.json'
with open(plan_path, 'w', encoding='utf-8') as f:
    json.dump(test_plan, f, indent=2, ensure_ascii=False)

print(f"Test plan generated: {len(test_plan['controllers'])} controllers")
print(f"Plan saved to: {plan_path}")
print()
print("Next: Claude will execute Phase 4 CheckModel for all controllers using mcp__sysplorer__check_model")
