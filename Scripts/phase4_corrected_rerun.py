#!/usr/bin/env python3
"""
Phase 4 Re-run with CORRECTED runner class names
Uses actual filesystem-discovered runner classes instead of scheme_to_pkg() guessing
"""
import json
from pathlib import Path

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
MAPPING_PATH = BASE_DIR / 'Results/control_platform/phase4_phase5_real_mcp/corrected_runner_mapping.json'
PHASE3_PATH = BASE_DIR / 'Results/control_platform/phase3_graphical_core_rebuild/phase3_final_restoration_summary.json'
RESULTS_DIR = BASE_DIR / 'Results/control_platform/phase4_phase5_real_mcp'

# Load corrected mapping
mapping_data = json.load(open(MAPPING_PATH, encoding='utf-8'))
runner_mapping = mapping_data['mapping']

# Load Phase 3 to get the exact 46 controller scope
phase3_data = json.load(open(PHASE3_PATH, encoding='utf-8'))
phase3_controllers = sorted(phase3_data['results'].keys())

# Build corrected test plan for the 46 controllers from Phase 1-3
corrected_plan = {
    'timestamp': '2026-08-19T02:15:00',
    'execution_type': 'PHASE4_CORRECTED_RERUN',
    'source': 'corrected_runner_mapping.json (filesystem discovery)',
    'total_controllers': 46,
    'controllers': []
}

for sid in phase3_controllers:
    if sid in runner_mapping:
        runner_class = runner_mapping[sid]
        parts = runner_class.split('.')
        family = parts[2]

        corrected_plan['controllers'].append({
            'scheme_id': sid,
            'runner_class': runner_class,
            'family': family
        })
    else:
        # Controller has no GraphicalRunner (should not happen for Phase 3 scope)
        corrected_plan['controllers'].append({
            'scheme_id': sid,
            'runner_class': None,
            'family': None,
            'note': 'NO_RUNNER_EXISTS'
        })

# Save corrected test plan
plan_path = RESULTS_DIR / 'phase4_corrected_test_plan.json'
with open(plan_path, 'w', encoding='utf-8') as f:
    json.dump(corrected_plan, f, indent=2, ensure_ascii=False)

print(f"Corrected Phase 4 test plan saved: {plan_path}")
print(f"Total controllers: {len(corrected_plan['controllers'])}")
print(f"Ready for Phase 4 re-run with mcp__sysplorer__check_model")
