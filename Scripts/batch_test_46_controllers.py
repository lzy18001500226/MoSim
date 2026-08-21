#!/usr/bin/env python3
"""
Batch test 46 controllers (excluding official_pid and px4ctrl)
Run CheckModel validation on each controller
"""
import json
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
HARNESS_PATH = BASE_DIR / 'Config/control_platform/formal_closed_loop_harness_map.json'
RESULTS_DIR = BASE_DIR / 'Results/control_platform/phase6_fresh_test_46'

# All 48 controllers from harness map
ALL_CONTROLLERS = [
    'cascade_pid', 'gain_scheduled_pid', 'fuzzy_pid', 'neural_pid',
    'fopid', 'awff_pid', 'awff_l1_residual', 'awff_l1_indi',
    'lqr_baseline', 'lqi_baseline', 'lqg', 'h2_state_feedback',
    'hinf_hover_wrench', 'pole_placement_luenberger', 'backstepping_baseline',
    'adaptive_backstepping', 'feedback_linearization', 'mrac', 'ndi',
    'passivity_based_control', 'integral_smc', 'terminal_smc',
    'nonsingular_terminal_smc', 'super_twisting_smc', 'adaptive_smc',
    'fuzzy_smc', 'smc_boundary_layer', 'linear_mpc', 'robust_mpc',
    'adaptive_mpc', 'tube_mpc', 'explicit_gain_scheduled_mpc',
    'ilqr', 'mppi', 'nmpc_outer', 'linear_mpc_l1_indi',
    'qp_nmpc_l1_indi_cbf', 'se3_basic', 'dfbc_basic',
    'dfbc_high_order_attitude', 'dfbc_high_order_bodyrate',
    'dfbc_smooth_robust_attitude', 'dfbc_smooth_robust_bodyrate',
    'trained_neural_residual', 'rl_gain_scheduler', 'pid_awff_linear_eso'
]

# Exclude official_pid and px4ctrl
TEST_CONTROLLERS = [c for c in ALL_CONTROLLERS if c not in ['official_pid', 'px4ctrl']]

print("="*80)
print("PHASE 6: Fresh Test of 46 Controllers")
print("="*80)
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Total controllers to test: {len(TEST_CONTROLLERS)}")
print(f"Excluded: official_pid, px4ctrl (baseline references)")
print("="*80)

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Save controller list
with open(RESULTS_DIR / 'test_controller_list.txt', 'w', encoding='utf-8') as f:
    f.write(f"Test date: {datetime.now().isoformat()}\n")
    f.write(f"Total controllers: {len(TEST_CONTROLLERS)}\n\n")
    for i, sid in enumerate(TEST_CONTROLLERS, 1):
        f.write(f"{i:2d}. {sid}\n")

print(f"\nController list saved: {RESULTS_DIR / 'test_controller_list.txt'}")
print("\nReady to run CheckModel tests via MCP.")
print("="*80)
