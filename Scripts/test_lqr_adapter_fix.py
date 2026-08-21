#!/usr/bin/env python3
"""
Test LqrBaselineGraphicalRunner after adapter architecture fix
"""
import sys
import json
from pathlib import Path

# Add MCP path
mcp_path = Path('D:/Program Files/MWORKS/Sysplorer 2026a/Tools/sysplorer_mcp')
sys.path.insert(0, str(mcp_path))

from sysplorer_mcp_client import SysplorerMCPClient

def main():
    client = SysplorerMCPClient()
    model_name = "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.LqrBaselineGraphicalRunner"

    print("="*80)
    print("Testing LqrBaselineGraphicalRunner with Adapter Architecture")
    print("="*80)

    # 1. CheckModel
    print("\n[1/3] CheckModel validation...")
    check_result = client.check_model(model_name)
    if not check_result['ok']:
        print(f"❌ CheckModel failed: {check_result.get('error')}")
        return
    print(f"✅ CheckModel passed ({check_result['elapsed_s']:.3f}s)")

    # 2. Simulate
    print("\n[2/3] Running 50s simulation...")
    sim_result = client.simulate_model(model_name, sim_mode=0)
    if not sim_result['ok']:
        print(f"❌ Simulation failed: {sim_result.get('error')}")
        return
    print("✅ Simulation completed")

    # 3. Extract key variables
    print("\n[3/3] Extracting result variables...")

    vars_to_check = [
        "position_error_norm",
        "core.enable",
        "core.position_x",
        "reference.position_command[1]",
        "reference.position_command[3]"
    ]

    results = {}
    for var in vars_to_check:
        var_result = client.get_var_values(var)
        if var_result['ok']:
            data = var_result['data']
            results[var] = {
                'first': data['first'],
                'last': data['last'],
                'min': data['min'],
                'max': data['max'],
                'mean': data.get('mean', 0)
            }
            print(f"  {var}:")
            print(f"    t=0s: {data['first']:.6f}")
            print(f"    t=50s: {data['last']:.6f}")
        else:
            print(f"  {var}: ❌ Not found")

    # 4. Verdict
    print("\n" + "="*80)
    print("VERDICT")
    print("="*80)

    error_norm = results.get('position_error_norm', {}).get('last', float('inf'))
    core_enable = results.get('core.enable', {}).get('last', 0)

    print(f"Final tracking error: {error_norm:.1f}m")
    print(f"Core enable signal: {core_enable:.1f}")

    if error_norm < 5:
        print("✅ PASS - Error < 5m threshold")
    else:
        print(f"❌ FAIL - Error {error_norm:.1f}m exceeds 5m threshold")

    if core_enable == 1.0:
        print("✅ Signal propagation: core.enable active")
    else:
        print("❌ Signal propagation: core.enable inactive")

    # Save results
    output_file = Path('Results/control_platform/phase6_fresh_test_46/lqr_adapter_test.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'model': model_name,
            'check_ok': check_result['ok'],
            'sim_ok': sim_result['ok'],
            'variables': results,
            'verdict': {
                'error_norm_m': error_norm,
                'core_enable': core_enable,
                'pass_threshold': error_norm < 5
            }
        }, f, indent=2)

    print(f"\nResults saved: {output_file}")

if __name__ == '__main__':
    main()
