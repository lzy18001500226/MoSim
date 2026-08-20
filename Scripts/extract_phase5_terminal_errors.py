#!/usr/bin/env python3
"""
Extract terminal position errors from Phase 5 simulation results
Reads Sysplorer result files and computes Euclidean distance from target
"""
import json
import math
from pathlib import Path

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
RESULTS_DIR = BASE_DIR / 'Results/control_platform/phase4_phase5_real_mcp'
PRELIM_PATH = RESULTS_DIR / 'phase5_preliminary_results.json'

# ClimbPath terminal target
TARGET = [50.0, 50.0, 50.0]
THRESHOLD = 5.0

# Load preliminary results
prelim = json.load(open(PRELIM_PATH, encoding='utf-8'))

# Controllers that were simulated
simulated = [k for k, v in prelim['phase5_simulation_results'].items()
             if v['status'] == 'SIMULATED']

print(f"Found {len(simulated)} simulated controllers")
print("Controllers need Sysplorer result_manager calls to extract terminal positions")
print()
print("Use result_manager(action='get_vars_value_at', time_point='end', var_names=[...])")
print("to extract plant.pos_world_drone[1], [2], [3] for each controller")
