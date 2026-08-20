#!/usr/bin/env python3
"""
Phase 5: 50s ClimbPath simulation for 38 PASS controllers
Uses corrected runner class names from Phase 4 corrected rerun
"""
import json
from pathlib import Path

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
PHASE4_CORRECTED = BASE_DIR / 'Results/control_platform/phase4_phase5_real_mcp/phase4_corrected_results.json'
RESULTS_DIR = BASE_DIR / 'Results/control_platform/phase4_phase5_real_mcp'

# Load Phase 4 corrected results
phase4_data = json.load(open(PHASE4_CORRECTED, encoding='utf-8'))

# Extract 38 PASS controllers
pass_controllers = []
for scheme_id, result in phase4_data['results'].items():
    if result['status'] == 'PASS':
        pass_controllers.append(scheme_id)

pass_controllers.sort()

print(f"Phase 5: 50s ClimbPath simulation")
print(f"Controllers: {len(pass_controllers)} PASS from Phase 4 corrected")
print()

# Generate Phase 5 test plan
phase5_plan = {
    'timestamp': '2026-08-19T02:45:00',
    'execution_type': 'PHASE5_CLIMBPATH_SIMULATION',
    'source': 'phase4_corrected_results.json (38 PASS controllers)',
    'simulation_scenario': 'ClimbPath',
    'simulation_duration_s': 50.0,
    'terminal_position_threshold_m': 5.0,
    'total_controllers': len(pass_controllers),
    'controllers': pass_controllers
}

plan_path = RESULTS_DIR / 'phase5_simulation_plan.json'
with open(plan_path, 'w', encoding='utf-8') as f:
    json.dump(phase5_plan, f, indent=2, ensure_ascii=False)

print(f"Phase 5 simulation plan saved: {plan_path}")
print(f"Ready for mcp__sysplorer__simulate_model execution")
print()
print("38 controllers to simulate:")
for i, sid in enumerate(pass_controllers, 1):
    print(f"  {i:2d}. {sid}")
