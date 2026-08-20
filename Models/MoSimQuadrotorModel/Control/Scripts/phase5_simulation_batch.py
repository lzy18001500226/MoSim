#!/usr/bin/env python3
"""
Phase 5: Run 50s ClimbPath simulation on 15 passing controllers
Uses position_error_norm variable from Runner equation section
"""
from pathlib import Path
import json

BASE = Path('C:/Users/HP/Desktop/MoSim')
RESULTS_DIR = BASE / 'Results/control_platform/phase4_phase5_real'

# Load Phase 4 passing controllers
phase4_json = RESULTS_DIR / 'phase4_checkmodel_results.json'
with open(phase4_json, 'r', encoding='utf-8') as f:
    phase4_data = json.load(f)

passing_controllers = phase4_data['pass_controllers']

print(f"Phase 5: Simulating {len(passing_controllers)} controllers")
print("="*80)

phase5_results = []

for ctrl in passing_controllers:
    print(f"Simulating {ctrl}...", end=' ', flush=True)

    # Find family for this controller
    family_map = {
        'CascadePid': 'PidFamily', 'GainScheduledPid': 'PidFamily',
        'FuzzyPid': 'PidFamily', 'NeuralPid': 'PidFamily',
        'IntegralSmc': 'SlidingMode', 'TerminalSmc': 'SlidingMode',
        'NonsingularTerminalSmc': 'SlidingMode', 'SuperTwistingSmc': 'SlidingMode',
        'AdaptiveSmc': 'SlidingMode', 'FuzzySmc': 'SlidingMode',
        'DfbcHighOrderAttitude': 'GeometricFlatness', 'DfbcHighOrderBodyrate': 'GeometricFlatness',
        'DfbcSmoothRobustAttitude': 'GeometricFlatness', 'DfbcSmoothRobustBodyrate': 'GeometricFlatness',
        'TrainedNeuralResidual': 'Learning'
    }

    family = family_map.get(ctrl, 'Unknown')
    runner_class = f'MoSimQuadrotorModel.Experiment.{family}.{ctrl}GraphicalRunner'

    result = {
        'controller': ctrl,
        'family': family,
        'runner_class': runner_class,
        'note': 'Simulation via MCP - check phase5_simulation_results.json for outcomes'
    }

    phase5_results.append(result)
    print(f"Queued")

# Save preliminary results
phase5_json = RESULTS_DIR / 'phase5_simulation_queue.json'
with open(phase5_json, 'w', encoding='utf-8') as f:
    json.dump({
        'total': len(phase5_results),
        'controllers': phase5_results
    }, f, indent=2, ensure_ascii=False)

print(f"\n{'='*80}")
print(f"Phase 5 queue saved: {len(phase5_results)} controllers")
print("Run simulations via MCP simulate_model tool")
print(f"{'='*80}")
