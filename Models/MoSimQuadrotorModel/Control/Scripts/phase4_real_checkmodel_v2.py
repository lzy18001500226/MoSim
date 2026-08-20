#!/usr/bin/env python3
"""
Phase 4: Real Sysplorer CheckModel verification using MCP tools directly
"""
import json
import subprocess
from pathlib import Path

PRODUCTION_CONTROLLERS = [
    # PidFamily (5)
    'cascade_pid', 'gain_scheduled_pid', 'fuzzy_pid', 'neural_pid', 'official_pid',
    # ClassicRobust (13)
    'lqr_baseline', 'lqi_baseline', 'lqg', 'h2_state_feedback', 'hinf_hover_wrench',
    'pole_placement_luenberger', 'backstepping_baseline', 'adaptive_backstepping',
    'feedback_linearization', 'mrac', 'ndi', 'passivity_based_control', 'fopid',
    # SlidingMode (6)
    'integral_smc', 'terminal_smc', 'nonsingular_terminal_smc', 'super_twisting_smc',
    'adaptive_smc', 'fuzzy_smc',
    # Optimization (7)
    'linear_mpc', 'robust_mpc', 'adaptive_mpc', 'tube_mpc',
    'explicit_gain_scheduled_mpc', 'ilqr', 'mppi',
    # GeometricFlatness (4)
    'dfbc_high_order_attitude', 'dfbc_high_order_bodyrate',
    'dfbc_smooth_robust_attitude', 'dfbc_smooth_robust_bodyrate',
    # Learning (2)
    'trained_neural_residual', 'rl_gain_scheduler',
    # IntegratedChains (1)
    'fixed_awff_pid'
]

def snake_to_pascal(name):
    return ''.join(word.capitalize() for word in name.split('_'))

def call_mcp_tool(tool_name, params):
    """Call Sysplorer MCP tool via subprocess"""
    cmd = [
        'D:/Dev/Anaconda3/python.exe',
        'D:/Program Files/MWORKS/Sysplorer 2026a/Tools/sysplorer_mcp/main.py',
        tool_name,
        json.dumps(params)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        return {'ok': False, 'error': result.stderr}
    return json.loads(result.stdout)

def main():
    print("Phase 4: CheckModel Verification (Real Sysplorer)")
    print(f"{'='*80}\n")

    # Ensure session
    print("Starting Sysplorer session...")
    health = call_mcp_tool('session_manager', {'action': 'ensure'})
    if not health.get('ok'):
        print(f"ERROR: {health.get('error')}")
        return

    print("Session ready\n")

    results = []
    passed = 0
    failed = 0

    for controller in PRODUCTION_CONTROLLERS:
        pascal_name = snake_to_pascal(controller)
        runner_model = f"MoSimQuadrotorModel.Experiment.G6Champion.{pascal_name}GraphicalRunner"

        print(f"[CHECK] {controller:40s} ", end='', flush=True)

        check_result = call_mcp_tool('check_model', {
            'model_name': runner_model,
            'model_type': 'Sysblock'
        })

        if check_result.get('ok') and check_result.get('check_ok'):
            print("PASS")
            results.append({'controller': controller, 'status': 'PASS'})
            passed += 1
        else:
            error_msg = check_result.get('error', 'Unknown')
            print(f"FAIL: {error_msg}")
            results.append({'controller': controller, 'status': 'FAIL', 'error': error_msg})
            failed += 1

    # Save
    output_dir = Path('Results/control_platform/phase4_real_checkmodel')
    output_dir.mkdir(parents=True, exist_ok=True)

    report = {
        'phase': 'Phase 4 - Real CheckModel',
        'total': len(PRODUCTION_CONTROLLERS),
        'passed': passed,
        'failed': failed,
        'success_rate': f"{passed}/{len(PRODUCTION_CONTROLLERS)} ({100*passed/len(PRODUCTION_CONTROLLERS):.1f}%)",
        'results': results
    }

    (output_dir / 'phase4_checkmodel_report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8'
    )

    print(f"\n{'='*80}")
    print(f"CheckModel: {passed}/{len(PRODUCTION_CONTROLLERS)} PASS")
    print(f"Report: Results/control_platform/phase4_real_checkmodel/")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()
