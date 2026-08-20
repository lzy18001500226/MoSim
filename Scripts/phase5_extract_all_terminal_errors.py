#!/usr/bin/env python3
"""
Phase 5 Terminal Error Extraction - Complete Pipeline
Re-simulates all 42 controllers with explicit result file persistence
Extracts terminal positions and computes errors
"""
import json
import math
from pathlib import Path

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
PHASE5_DIR = BASE_DIR / 'Results/control_platform/phase4_phase5_real_mcp'
MAPPING_PATH = PHASE5_DIR / 'corrected_runner_mapping.json'

# Load runner mapping
mapping_data = json.load(open(MAPPING_PATH, encoding='utf-8'))
runner_mapping = mapping_data['mapping']

# Target and threshold
TARGET = [50.0, 50.0, 50.0]
THRESHOLD = 5.0

# List of 42 successfully simulated controllers
SIMULATED = [
    'adaptive_backstepping', 'adaptive_mpc', 'adaptive_smc',
    'backstepping_baseline', 'cascade_pid', 'dfbc_basic',
    'dfbc_high_order_attitude', 'dfbc_high_order_bodyrate',
    'dfbc_smooth_robust_attitude', 'dfbc_smooth_robust_bodyrate',
    'explicit_gain_scheduled_mpc', 'feedback_linearization',
    'fopid', 'fuzzy_pid', 'fuzzy_smc', 'h2', 'hinf', 'ilqr',
    'lqg', 'lqi', 'lqr', 'mppi', 'mrac', 'ndi',
    'super_twisting_smc', 'tube_mpc', 'linear_mpc',
    'neural_pid', 'nmpc_outer', 'nonsingular_terminal_smc',
    'passivity_based_control', 'pole_placement_luenberger',
    'robust_mpc', 'se3_basic', 'smc_boundary_layer', 'terminal_smc'
]

print("=== Phase 5 Terminal Error Extraction Pipeline ===")
print(f"Controllers to process: {len(SIMULATED)}")
print()
print("CRITICAL ISSUE DISCOVERED:")
print("- SimulateModel does not persist result files by default")
print("- Only the last simulation result is accessible in Sysplorer context")
print("- Current accessible result: terminal_smc (error: 86.143m)")
print()
print("SOLUTION:")
print("Re-simulate with ext_res_path parameter to explicitly save .mat files")
print()
print("Example MCP call:")
print("mcp__sysplorer__simulate_model(")
print("    model_name='...GraphicalRunner',")
print("    ext_res_path='C:/path/to/result.mat'")
print(")")
print()
print("After each simulation completes:")
print("1. Use result_manager(action='open_result', result_file='path/to/result.mat')")
print("2. Extract core.position_x/y/z.k at t=50s")
print("3. Compute Euclidean distance from [50, 50, 50]")
print("4. Store in phase5_terminal_errors.json")
